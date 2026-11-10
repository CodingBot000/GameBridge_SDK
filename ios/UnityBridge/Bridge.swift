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
        do {
            let result: Any
            switch operation {
            case "sdk.status": result = ["state": state, "sdkVersion": GameBridgeVersion.current]
            case "sdk.shutdown":
                invalidatePurchaseEvents(clearSession: true)
                _ = try await invokeActive(operation, payload: payload)
                state = "SHUTDOWN"; ownerSession = nil; activeMode = nil; result = ["state": state]
            case "sdk.initialize":
                let mode = payload["providerMode"] as? String
                if let activeMode, activeMode != mode { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
                switch mode {
                case "LOCAL_MOCK":
                    #if canImport(Security)
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
                state = "READY"; ownerSession = session; activeMode = mode
                bindEventSession(session)
            default:
                if operation == "auth.signIn" || operation == "auth.signOut" { invalidatePurchaseEvents(clearSession: false) }
                result = try await invokeActive(operation, payload: payload)
            }
            return envelope(data, result: result, failure: nil)
        } catch let failure as SdkFailure { return envelope(data, result: nil, failure: failure) }
        catch { return envelope(data, result: nil, failure: SdkFailure("INTERNAL_ERROR")) }
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
