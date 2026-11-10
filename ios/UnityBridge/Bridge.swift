import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

public typealias GBCallback = @convention(c) (UnsafePointer<UInt8>?, Int32) -> Void

private final class BridgeState {
    static let shared = BridgeState()
    private let lock = NSRecursiveLock()
    private let queue = DispatchQueue(label: "com.gamebridge.bridge")
    private var callback: GBCallback?
    private var generation: UInt64 = 0
    private var pending = 0
    private var state = "UNINITIALIZED"
    func setCallback(_ value: GBCallback?) {
        lock.lock(); defer { lock.unlock() }
        generation &+= 1; callback = value
    }
    func dispatch(_ data: Data) {
        lock.lock()
        let current = generation
        if pending >= 100 {
            lock.unlock()
            if let response = makeResponse(data, forcedError: "BUSY") { deliver(response, generation: current) }
            return
        }
        pending += 1; lock.unlock()
        queue.async {
            defer { self.lock.lock(); self.pending -= 1; self.lock.unlock() }
            if let response = self.makeResponse(data, forcedError: nil) { self.deliver(response, generation: current) }
        }
    }
    private func makeResponse(_ data: Data, forcedError: String?) -> Data? {
        guard let request = try? BridgeProtocol.parse(data), request["kind"] as? String == "request",
              let operation = request["operation"] as? String, let session = request["sdkSessionId"] as? String,
              let requestId = request["requestId"] as? String else { return nil }
        var result: [String: Any]?
        if forcedError == nil {
            switch operation {
            case "sdk.status": result = ["state": state, "sdkVersion": GameBridgeVersion.current]
            case "sdk.shutdown": state = "SHUTDOWN"; result = ["state": state]
            default: break
            }
        }
        let errorCode = forcedError ?? (result == nil ? "UNSUPPORTED_OPERATION" : nil)
        let error: Any = errorCode.map { ["code": $0, "message": "Operation is not available", "retryable": $0 == "BUSY", "requestId": requestId, "nativeCode": NSNull(), "details": [:]] as [String: Any] } ?? NSNull()
        let envelope: [String: Any] = ["protocolVersion": 1, "sdkSessionId": session, "kind": "response", "requestId": requestId, "operation": operation, "ok": errorCode == nil, "result": result ?? NSNull(), "error": error]
        return try? JSONSerialization.data(withJSONObject: envelope)
    }
    private func deliver(_ encoded: Data, generation expected: UInt64) {
        guard encoded.count <= Int(Int32.max) else { return }
        lock.lock(); defer { lock.unlock() }
        guard expected == generation, let send = callback else { return }
        encoded.withUnsafeBytes { raw in send(raw.bindMemory(to: UInt8.self).baseAddress, Int32(raw.count)) }
    }
    func shutdown() {
        setCallback(nil)
        queue.async { self.state = "SHUTDOWN" }
    }
}

@_cdecl("GB_ProtocolVersion")
public func GB_ProtocolVersion() -> Int32 { 1 }
@_cdecl("GB_SetCallback")
public func GB_SetCallback(_ callback: GBCallback?) { BridgeState.shared.setCallback(callback) }
@_cdecl("GB_Dispatch")
public func GB_Dispatch(_ pointer: UnsafePointer<UInt8>?, _ length: Int32) {
    guard length > 0, length <= BridgeProtocol.maxBytes, let pointer else { return }
    // Copy before returning: the caller retains ownership of the input pointer.
    BridgeState.shared.dispatch(Data(bytes: pointer, count: Int(length)))
}
@_cdecl("GB_Shutdown")
public func GB_Shutdown() { BridgeState.shared.shutdown() }
