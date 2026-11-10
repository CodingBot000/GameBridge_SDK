import Foundation
import XCTest
import GameBridgeUnityBridge

private let callbackLock = NSLock()
private var callbackData: Data?
private let callbackSignal = DispatchSemaphore(value: 0)
private let bridgeCallback: GBCallback = { pointer, length in
    guard let pointer, length > 0 else { return }
    let copied = Data(bytes: pointer, count: Int(length))
    callbackLock.lock(); callbackData = copied; callbackLock.unlock()
    callbackSignal.signal()
}
final class CBridgeTests: XCTestCase {
    func testCopiedUTF8AndCorrelatedResponse() throws {
        XCTAssertEqual(GB_ProtocolVersion(), 1)
        GB_SetCallback(bridgeCallback)
        let request = """
        {"protocolVersion":1,"sdkSessionId":"dc9a46f4-8e20-4880-bcbb-ac45033157ca","kind":"request","requestId":"2efc133b-3138-4c3e-aa72-0532cd19056e","operation":"sdk.status","payload":{"text":"한글 🎮"}}
        """
        var bytes = Array(request.utf8)
        bytes.withUnsafeBufferPointer { buffer in GB_Dispatch(buffer.baseAddress, Int32(buffer.count)) }
        bytes = Array(repeating: 0, count: bytes.count)
        XCTAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
        callbackLock.lock(); let result = callbackData; callbackLock.unlock()
        let response = try XCTUnwrap(try JSONSerialization.jsonObject(with: XCTUnwrap(result)) as? [String: Any])
        XCTAssertEqual(response["requestId"] as? String, "2efc133b-3138-4c3e-aa72-0532cd19056e")
        XCTAssertEqual(response["ok"] as? Bool, true)
        GB_Shutdown()
    }
    func testMockInitializationAndSessionIsolation() throws {
        GB_SetCallback(bridgeCallback)
        let session = UUID().uuidString.lowercased()
        let key = "development-test-key-0123456789abcdef"
        func call(_ operation: String, _ payload: [String: Any], _ sessionId: String) throws -> [String: Any] {
            let request: [String: Any] = ["protocolVersion": 1, "sdkSessionId": sessionId, "kind": "request",
                "requestId": UUID().uuidString.lowercased(), "operation": operation, "payload": payload]
            let data = try JSONSerialization.data(withJSONObject: request)
            data.withUnsafeBytes { bytes in GB_Dispatch(bytes.bindMemory(to: UInt8.self).baseAddress, Int32(bytes.count)) }
            XCTAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
            callbackLock.lock(); let response = callbackData; callbackLock.unlock()
            let raw = try XCTUnwrap(response)
            XCTAssertFalse(String(decoding: raw, as: UTF8.self).contains(key))
            return try XCTUnwrap(JSONSerialization.jsonObject(with: raw) as? [String: Any])
        }
        let payload: [String: Any] = ["providerMode": "LOCAL_MOCK", "appId": "gamebridge-sample",
            "backendBaseUrl": "http://127.0.0.1:18080", "requestTimeoutMs": 30000, "developmentKey": key, "mockSubject": "A"]
        let initialized = try call("sdk.initialize", payload, session)
        XCTAssertEqual(initialized["ok"] as? Bool, true)
        let result = try XCTUnwrap(initialized["result"] as? [String: Any])
        XCTAssertEqual(result["mode"] as? String, "LOCAL_MOCK")
        let other = try call("auth.restore", [:], UUID().uuidString.lowercased())
        XCTAssertEqual((other["error"] as? [String: Any])?["code"] as? String, "NOT_INITIALIZED")
        XCTAssertEqual(try call("sdk.shutdown", [:], session)["ok"] as? Bool, true)
        GB_Shutdown()
    }

}
