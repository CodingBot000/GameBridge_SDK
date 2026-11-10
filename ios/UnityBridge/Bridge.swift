import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
import GameBridgeApple
#endif

public typealias GBCallback = @convention(c) (UnsafePointer<UInt8>?, Int32) -> Void

private final class BridgeState {
    static let shared = BridgeState()
    private let lock = NSRecursiveLock()
    private let queue = DispatchQueue(label: "com.gamebridge.bridge")
    #if canImport(Security)
    private let handler = LocalMockBridgeHandler(tokenStore: { KeychainTokenStore(service: "com.gamebridge.sdk.unity.local-mock") },
        pendingStore: { KeychainTokenStore(service: "com.gamebridge.sdk.unity.mock-purchases") })
    #endif
    private var callback: GBCallback?
    private var generation: UInt64 = 0
    private var pending = 0
    private var eventSession: String?
    private var accountEpoch: UInt64 = 0
    private let pushRouter = PushRouter()
    private let diagnostics = Diagnostics()
    // Accessed only by the serial bridge queue and the one task it waits for.
    private var state = "UNINITIALIZED"
    private var ownerSession: String?
    private var activeMode: String?
    #if canImport(UIKit) && canImport(AuthenticationServices)
    private var appleHandler: AppleAuthBridgeHandler?
    #endif
    func setCallback(_ value: GBCallback?) {
        lock.lock(); defer { lock.unlock() }
        generation &+= 1; callback = value
        if value == nil { eventSession = nil; accountEpoch &+= 1 }
    }
    func dispatch(_ data: Data) {
        lock.lock()
        let current = generation
        if pending >= 100 {
            lock.unlock()
            if let response = envelope(data, result: nil, failure: SdkFailure("BUSY", retryable: true)) { deliver(response, generation: current) }
            return
        }
        pending += 1; lock.unlock()
        queue.async {
            defer { self.lock.lock(); self.pending -= 1; self.lock.unlock() }
            self.lock.lock(); let valid = self.generation == current; self.lock.unlock()
            guard valid else { return }
            // The queue serializes actor calls without blocking Unity's main thread.
            let done = DispatchSemaphore(value: 0)
            Task {
                defer { done.signal() }
                if let response = await self.makeResponse(data) { self.deliver(response, generation: current) }
            }
            done.wait()
        }
    }
    private func makeResponse(_ data: Data) async -> Data? {
        guard let request = try? BridgeProtocol.parse(data), request["kind"] as? String == "request",
              let operation = request["operation"] as? String, let session = request["sdkSessionId"] as? String,
              let payload = request["payload"] as? [String: Any] else { return nil }
        if let ownerSession, ownerSession != session { return envelope(data, result: nil, failure: SdkFailure("NOT_INITIALIZED")) }
        let category: DiagnosticKind?
        if operation == "sdk.initialize" { category = .initialize }
        else if operation == "sdk.shutdown" { category = .shutdown }
        else if operation.hasPrefix("auth.") { category = .auth }
        else if operation.hasPrefix("store.") { category = .purchase }
        else if operation.hasPrefix("push.") { category = .push }
        else { category = nil }
        let requestId = (request["requestId"] as? String).flatMap(UUID.init(uuidString:))
        if operation == "sdk.initialize" && ownerSession == nil { await diagnostics.clear() }
        if let category { await diagnostics.record(category, .started, requestId: requestId) }
        do {
            let result: Any
            switch operation {
            case "diagnostics.get":
                guard state == "READY" else { throw SdkFailure("NOT_INITIALIZED") }
                let events = await diagnostics.snapshot()
                result = ["events": events.map { event in
                    ["kind": event.kind.rawValue.uppercased(), "outcome": event.outcome.rawValue.uppercased(),
                     "timestamp": ISO8601DateFormatter().string(from: event.timestamp),
                     "requestId": event.requestId?.uuidString.lowercased() as Any? ?? NSNull()] as [String: Any]
                }]
            case "sdk.status": result = ["state": state, "sdkVersion": GameBridgeVersion.current]
            case "sdk.shutdown":
                await pushRouter.reset()
                invalidatePurchaseEvents(clearSession: true)
                _ = try await invokeActive(operation, payload: payload)
                state = "SHUTDOWN"; ownerSession = nil; activeMode = nil; result = ["state": state]
            case "sdk.initialize":
                let mode = payload["providerMode"] as? String
                if let activeMode, activeMode != mode { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
                switch mode {
                case "LOCAL_MOCK":
                    #if canImport(Security)
                    await handler.setMockPushSinkFactory { [weak self] in self?.mockPushEmitter() ?? { _ in } }
                    result = try await handler.invoke(operation, payload: payload)
                    #else
                    throw SdkFailure("UNSUPPORTED_OPERATION")
                    #endif
                case "PLATFORM_SANDBOX":
                    #if canImport(UIKit) && canImport(AuthenticationServices)
                    if appleHandler == nil { appleHandler = await makeAppleAuthBridgeHandler { self.purchaseEmitter() } }
                    result = try await appleHandler!.invoke(operation, payload: payload)
                    #else
                    throw SdkFailure("UNSUPPORTED_PLATFORM")
                    #endif
                default: throw SdkFailure("UNSUPPORTED_PROVIDER")
                }
                let newlyInitialized = ownerSession == nil
                state = "READY"; ownerSession = session; activeMode = mode
                bindEventSession(session)
                if newlyInitialized { _ = await pushRouter.setReady() }
            case "host.pushReceived", "host.pushOpened":
                guard state == "READY" else { throw SdkFailure("NOT_INITIALIZED") }
                var fields: [AnyHashable: Any] = ["messageId": payload["messageId"] as Any, "route": payload["route"] as Any]
                if let campaign = payload["campaignId"], !(campaign is NSNull) { fields["campaignId"] = campaign }
                guard let push = PushPayload(data: fields) else { throw SdkFailure("INVALID_ARGUMENT") }
                let opened = operation == "host.pushOpened"
                let decision = await pushRouter.submit(PushRouteEvent(payload: push, kind: opened ? .opened : .received))
                switch decision {
                case .deliver: emitPush(push, opened: opened, session: session)
                case .duplicate: break
                case .queued: throw SdkFailure("NOT_INITIALIZED")
                case .busy: throw SdkFailure("BUSY", retryable: true)
                }
                result = ["accepted": true]
            default:
                if operation == "auth.signIn" || operation == "auth.signOut" {
                    invalidatePurchaseEvents(clearSession: false)
                    await pushRouter.reset(); _ = await pushRouter.setReady()
                }
                result = try await invokeActive(operation, payload: payload)
            }
            if let category { await diagnostics.record(category, .succeeded, requestId: requestId) }
            return envelope(data, result: result, failure: nil)
        } catch let failure as SdkFailure {
            if let category { await diagnostics.record(category, .failed, requestId: requestId) }
            return envelope(data, result: nil, failure: failure)
        } catch {
            if let category { await diagnostics.record(category, .failed, requestId: requestId) }
            return envelope(data, result: nil, failure: SdkFailure("INTERNAL_ERROR"))
        }
    }
    private func invokeActive(_ operation: String, payload: [String: Any]) async throws -> Any {
        switch activeMode {
        case "LOCAL_MOCK":
            #if canImport(Security)
            return try await handler.invoke(operation, payload: payload)
            #else
            throw SdkFailure("UNSUPPORTED_OPERATION")
            #endif
        case "PLATFORM_SANDBOX":
            #if canImport(UIKit) && canImport(AuthenticationServices)
            guard let appleHandler else { throw SdkFailure("NOT_INITIALIZED") }
            return try await appleHandler.invoke(operation, payload: payload)
            #else
            throw SdkFailure("UNSUPPORTED_PLATFORM")
            #endif
        default:
            if operation == "sdk.shutdown" { return [String: Any]() }
            throw SdkFailure("NOT_INITIALIZED")
        }
    }
    private func mockPushEmitter() -> (PushPayload) -> Void {
        lock.lock(); let expectedGeneration = generation; let expectedEpoch = accountEpoch; let session = eventSession; lock.unlock()
        return { [weak self] value in
            guard let self, let session else { return }
            Task {
                guard self.isCurrentMockSession(expectedGeneration, expectedEpoch, session) else { return }
                let decision = await self.pushRouter.submit(PushRouteEvent(payload: value, kind: .received))
                if decision == .deliver && self.isCurrentMockSession(expectedGeneration, expectedEpoch, session) {
                    self.emitPush(value, opened: false, session: session)
                }
            }
        }
    }
    private func isCurrentMockSession(_ expectedGeneration: UInt64, _ expectedEpoch: UInt64, _ session: String) -> Bool {
        lock.lock(); defer { lock.unlock() }
        return generation == expectedGeneration && accountEpoch == expectedEpoch && eventSession == session && callback != nil
    }
    private func emitPush(_ push: PushPayload, opened: Bool, session: String) {
        lock.lock(); defer { lock.unlock() }
        guard session == eventSession, let send = callback else { return }
        let payload: [String: Any] = ["messageId": push.messageId, "route": push.route, "campaignId": push.campaignId as Any? ?? NSNull()]
        let envelope: [String: Any] = ["protocolVersion": 1, "sdkSessionId": session, "kind": "event", "eventId": UUID().uuidString.lowercased(),
            "type": opened ? "PushOpened" : "PushReceived", "occurredAt": ISO8601DateFormatter().string(from: Date()), "payload": payload]
        guard let encoded = try? JSONSerialization.data(withJSONObject: envelope), encoded.count <= Int(Int32.max) else { return }
        encoded.withUnsafeBytes { raw in send(raw.bindMemory(to: UInt8.self).baseAddress, Int32(raw.count)) }
    }
    private func bindEventSession(_ session: String) {
        lock.lock(); defer { lock.unlock() }; eventSession = session
    }
    private func invalidatePurchaseEvents(clearSession: Bool) {
        lock.lock(); defer { lock.unlock() }; accountEpoch &+= 1
        if clearSession { eventSession = nil }
    }
    #if canImport(UIKit) && canImport(AuthenticationServices)
    private func purchaseEmitter() -> (AppleStorePurchaseResult) -> Void {
        lock.lock(); let expectedGeneration = generation; let expectedEpoch = accountEpoch; let session = eventSession; lock.unlock()
        return { [weak self] event in self?.emitPurchase(event, generation: expectedGeneration, epoch: expectedEpoch, session: session) }
    }
    private func emitPurchase(_ event: AppleStorePurchaseResult, generation expectedGeneration: UInt64, epoch expectedEpoch: UInt64, session: String?) {
        lock.lock(); defer { lock.unlock() }
        guard let session, session == eventSession, expectedGeneration == generation, expectedEpoch == accountEpoch,
              event.status == .purchased, let purchaseId = event.serverPurchaseId,
              ["coins_100", "premium_unlock"].contains(event.productId), let send = callback else { return }
        let envelope: [String: Any] = ["protocolVersion": 1, "sdkSessionId": session, "kind": "event", "eventId": UUID().uuidString.lowercased(),
            "type": "PurchaseUpdated", "occurredAt": ISO8601DateFormatter().string(from: Date()),
            "payload": ["productId": event.productId, "status": "PURCHASED", "serverPurchaseId": purchaseId.uuidString.lowercased(), "errorCode": NSNull()]]
        guard let encoded = try? JSONSerialization.data(withJSONObject: envelope), encoded.count <= Int(Int32.max) else { return }
        encoded.withUnsafeBytes { raw in send(raw.bindMemory(to: UInt8.self).baseAddress, Int32(raw.count)) }
    }
    #endif
    private func envelope(_ data: Data, result: Any?, failure: SdkFailure?) -> Data? {
        guard let request = try? BridgeProtocol.parse(data), request["kind"] as? String == "request",
              let operation = request["operation"] as? String, let session = request["sdkSessionId"] as? String,
              let requestId = request["requestId"] as? String else { return nil }
        let error: Any = failure.map { ["code": $0.code, "message": "Operation is not available", "retryable": $0.retryable,
            "requestId": requestId, "nativeCode": $0.nativeCode as Any? ?? NSNull(), "details": [:]] as [String: Any] } ?? NSNull()
        return try? JSONSerialization.data(withJSONObject: ["protocolVersion": 1, "sdkSessionId": session, "kind": "response",
            "requestId": requestId, "operation": operation, "ok": failure == nil, "result": result ?? NSNull(), "error": error])
    }
    private func deliver(_ encoded: Data, generation expected: UInt64) {
        guard encoded.count <= Int(Int32.max) else { return }
        lock.lock(); defer { lock.unlock() }
        guard expected == generation, let send = callback else { return }
        encoded.withUnsafeBytes { raw in send(raw.bindMemory(to: UInt8.self).baseAddress, Int32(raw.count)) }
    }
    func shutdown() {
        setCallback(nil)
        queue.async {
            let done = DispatchSemaphore(value: 0)
            Task {
                _ = try? await self.invokeActive("sdk.shutdown", payload: [:])
                await self.pushRouter.reset()
                self.state = "SHUTDOWN"; self.ownerSession = nil; self.activeMode = nil; done.signal()
            }
            done.wait()
        }
    }
}

@_cdecl("GB_ProtocolVersion")
public func GB_ProtocolVersion() -> Int32 { 1 }
@_cdecl("GB_SetCallback")
public func GB_SetCallback(_ callback: GBCallback?) { BridgeState.shared.setCallback(callback) }
@_cdecl("GB_Dispatch")
public func GB_Dispatch(_ pointer: UnsafePointer<UInt8>?, _ length: Int32) {
    guard length > 0, length <= BridgeProtocol.maxBytes, let pointer else { return }
    BridgeState.shared.dispatch(Data(bytes: pointer, count: Int(length)))
}
@_cdecl("GB_Shutdown")
public func GB_Shutdown() { BridgeState.shared.shutdown() }
