import Foundation
import XCTest
import GameBridgeUnityBridge
import GameBridgeCore

private let callbackLock = NSLock()
private var callbackData: Data?
private let callbackSignal = DispatchSemaphore(value: 0)
private let bridgeCallback: GBCallback = { pointer, length in
    guard let pointer, length > 0 else { return }
    let copied = Data(bytes: pointer, count: Int(length))
    callbackLock.lock(); callbackData = copied; callbackLock.unlock()
    callbackSignal.signal()
}
private let pushCallbackLock = NSLock()
private var pushCallbackMessages: [Data] = []
private let pushCallbackSignal = DispatchSemaphore(value: 0)
private let pushBridgeCallback: GBCallback = { pointer, length in
    guard let pointer, length > 0 else { return }
    pushCallbackLock.lock(); pushCallbackMessages.append(Data(bytes: pointer, count: Int(length))); pushCallbackLock.unlock()
    pushCallbackSignal.signal()
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
    func testInvalidLengthsAreRejectedWithoutReadingAndBridgeSurvives() throws {
        GB_SetCallback(bridgeCallback)
        var byte: UInt8 = 0
        withUnsafePointer(to: &byte) { pointer in
            GB_Dispatch(pointer, -1)
            GB_Dispatch(pointer, Int32(BridgeProtocol.maxBytes + 1))
            GB_Dispatch(nil, 1)
        }
        XCTAssertEqual(callbackSignal.wait(timeout: .now() + 0.1), .timedOut)
        let request = """
        {"protocolVersion":1,"sdkSessionId":"dc9a46f4-8e20-4880-bcbb-ac45033157ca","kind":"request","requestId":"2efc133b-3138-4c3e-aa72-0532cd19056e","operation":"sdk.status","payload":{}}
        """
        let bytes = Array(request.utf8)
        bytes.withUnsafeBufferPointer { GB_Dispatch($0.baseAddress, Int32($0.count)) }
        XCTAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
        callbackLock.lock(); let data = callbackData; callbackLock.unlock()
        let response = try XCTUnwrap(JSONSerialization.jsonObject(with: XCTUnwrap(data)) as? [String: Any])
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
        let diagnostics = try call("diagnostics.get", ["secret": key], session)
        let events = try XCTUnwrap((diagnostics["result"] as? [String: Any])?["events"] as? [[String: Any]])
        XCTAssertTrue(events.contains { $0["kind"] as? String == "INITIALIZE" && $0["outcome"] as? String == "SUCCEEDED" })
        let other = try call("auth.restore", [:], UUID().uuidString.lowercased())
        XCTAssertEqual((other["error"] as? [String: Any])?["code"] as? String, "NOT_INITIALIZED")
        XCTAssertEqual(try call("sdk.shutdown", [:], session)["ok"] as? Bool, true)
        XCTAssertEqual((try call("diagnostics.get", [:], session)["error"] as? [String: Any])?["code"] as? String, "NOT_INITIALIZED")
        let newSession = UUID().uuidString.lowercased()
        XCTAssertEqual(try call("sdk.initialize", payload, newSession)["ok"] as? Bool, true)
        let fresh = try call("diagnostics.get", [:], newSession)
        let freshEvents = try XCTUnwrap((fresh["result"] as? [String: Any])?["events"] as? [[String: Any]])
        XCTAssertEqual(freshEvents.count, 2)
        XCTAssertTrue(freshEvents.allSatisfy { $0["kind"] as? String == "INITIALIZE" })
        XCTAssertEqual(try call("sdk.shutdown", [:], newSession)["ok"] as? Bool, true)
        GB_Shutdown()
    }

    func testHostPushEventRoutingAndDedup() throws {
        pushCallbackLock.lock(); pushCallbackMessages = []; pushCallbackLock.unlock()
        GB_SetCallback(pushBridgeCallback)
        let session = UUID().uuidString.lowercased()
        func send(_ operation: String, _ payload: [String: Any]) throws {
            let request: [String: Any] = ["protocolVersion": 1, "sdkSessionId": session, "kind": "request",
                "requestId": UUID().uuidString.lowercased(), "operation": operation, "payload": payload]
            let data = try JSONSerialization.data(withJSONObject: request)
            data.withUnsafeBytes { bytes in GB_Dispatch(bytes.bindMemory(to: UInt8.self).baseAddress, Int32(bytes.count)) }
        }
        func receive() throws -> [String: Any] {
            XCTAssertEqual(pushCallbackSignal.wait(timeout: .now() + 3), .success)
            pushCallbackLock.lock(); let data = pushCallbackMessages.removeFirst(); pushCallbackLock.unlock()
            return try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        }
        try send("sdk.initialize", ["providerMode": "LOCAL_MOCK", "appId": "demo", "backendBaseUrl": "http://127.0.0.1:18080",
            "requestTimeoutMs": 30000, "developmentKey": String(repeating: "x", count: 32), "mockSubject": "A"])
        XCTAssertEqual(try receive()["ok"] as? Bool, true)
        let payload: [String: Any] = ["messageId": "test-id", "route": "store", "campaignId": NSNull(), "url": "https://ignored.invalid"]
        try send("host.pushOpened", payload)
        let event = try receive(), response = try receive()
        XCTAssertEqual(event["type"] as? String, "PushOpened")
        XCTAssertEqual((event["payload"] as? [String: Any])?["route"] as? String, "store")
        XCTAssertNil((event["payload"] as? [String: Any])?["url"])
        XCTAssertEqual(response["ok"] as? Bool, true)
        try send("host.pushOpened", payload); XCTAssertEqual(try receive()["ok"] as? Bool, true)
        XCTAssertEqual(pushCallbackSignal.wait(timeout: .now() + 0.1), .timedOut)
        try send("host.pushReceived", ["messageId": "bad", "route": "https://ignored.invalid"])
        XCTAssertEqual((try receive()["error"] as? [String: Any])?["code"] as? String, "INVALID_ARGUMENT")
        GB_Shutdown()
    }

}
