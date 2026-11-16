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
final class CBridgeTests: MeasuredTestCase {
    func testCopiedUTF8AndCorrelatedResponse() throws {
        GBAssertEqual(GB_ProtocolVersion(), 1)
        GB_SetCallback(bridgeCallback)
        let request = """
        {"protocolVersion":1,"sdkSessionId":"dc9a46f4-8e20-4880-bcbb-ac45033157ca","kind":"request","requestId":"2efc133b-3138-4c3e-aa72-0532cd19056e","operation":"sdk.status","payload":{"text":"한글 🎮"}}
        """
        var bytes = Array(request.utf8)
        bytes.withUnsafeBufferPointer { buffer in GB_Dispatch(buffer.baseAddress, Int32(buffer.count)) }
        bytes = Array(repeating: 0, count: bytes.count)
        GBAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
        callbackLock.lock(); let result = callbackData; callbackLock.unlock()
        let response = try GBUnwrap(try JSONSerialization.jsonObject(with: GBUnwrap(result)) as? [String: Any])
        GBAssertEqual(response["requestId"] as? String, "2efc133b-3138-4c3e-aa72-0532cd19056e")
        GBAssertEqual(response["ok"] as? Bool, true)
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
        GBAssertEqual(callbackSignal.wait(timeout: .now() + 0.1), .timedOut)
        let request = """
        {"protocolVersion":1,"sdkSessionId":"dc9a46f4-8e20-4880-bcbb-ac45033157ca","kind":"request","requestId":"2efc133b-3138-4c3e-aa72-0532cd19056e","operation":"sdk.status","payload":{}}
        """
        let bytes = Array(request.utf8)
        bytes.withUnsafeBufferPointer { GB_Dispatch($0.baseAddress, Int32($0.count)) }
        GBAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
        callbackLock.lock(); let data = callbackData; callbackLock.unlock()
        let response = try GBUnwrap(JSONSerialization.jsonObject(with: GBUnwrap(data)) as? [String: Any])
        GBAssertEqual(response["ok"] as? Bool, true)
        GB_Shutdown()
    }
    func testMockInitializationAndSessionIsolation() throws {
        GB_SetCallback(bridgeCallback)
        let session = UUID().uuidString.lowercased()
        let key = "development-test-key-0123456789abcdef"
        let syntheticEmail = "synthetic-person@example.invalid", syntheticPhone = "+1-202-555-0107"
        func call(_ operation: String, _ payload: [String: Any], _ sessionId: String) throws -> [String: Any] {
            let request: [String: Any] = ["protocolVersion": 1, "sdkSessionId": sessionId, "kind": "request",
                "requestId": UUID().uuidString.lowercased(), "operation": operation, "payload": payload]
            let data = try JSONSerialization.data(withJSONObject: request)
            data.withUnsafeBytes { bytes in GB_Dispatch(bytes.bindMemory(to: UInt8.self).baseAddress, Int32(bytes.count)) }
            GBAssertEqual(callbackSignal.wait(timeout: .now() + 3), .success)
            callbackLock.lock(); let response = callbackData; callbackLock.unlock()
            let raw = try GBUnwrap(response)
            for sensitive in [key, syntheticEmail, syntheticPhone] { GBAssertFalse(String(decoding: raw, as: UTF8.self).contains(sensitive)) }
            return try GBUnwrap(JSONSerialization.jsonObject(with: raw) as? [String: Any])
        }
        let payload: [String: Any] = ["providerMode": "LOCAL_MOCK", "appId": "gamebridge-sample",
            "backendBaseUrl": "http://127.0.0.1:18080", "requestTimeoutMs": 30000, "developmentKey": key, "mockSubject": "A"]
        let initialized = try call("sdk.initialize", payload, session)
        GBAssertEqual(initialized["ok"] as? Bool, true)
        let result = try GBUnwrap(initialized["result"] as? [String: Any])
        GBAssertEqual(result["mode"] as? String, "LOCAL_MOCK")
        let diagnostics = try call("diagnostics.get", ["secret": key, "email": syntheticEmail, "phone": syntheticPhone], session)
        let events = try GBUnwrap((diagnostics["result"] as? [String: Any])?["events"] as? [[String: Any]])
        GBAssertTrue(events.contains { $0["kind"] as? String == "INITIALIZE" && $0["outcome"] as? String == "SUCCEEDED" })
        let other = try call("auth.restore", [:], UUID().uuidString.lowercased())
        GBAssertEqual((other["error"] as? [String: Any])?["code"] as? String, "NOT_INITIALIZED")
        GBAssertEqual(try call("sdk.shutdown", [:], session)["ok"] as? Bool, true)
        GBAssertEqual((try call("diagnostics.get", [:], session)["error"] as? [String: Any])?["code"] as? String, "NOT_INITIALIZED")
        let newSession = UUID().uuidString.lowercased()
        GBAssertEqual(try call("sdk.initialize", payload, newSession)["ok"] as? Bool, true)
        let fresh = try call("diagnostics.get", [:], newSession)
        let freshEvents = try GBUnwrap((fresh["result"] as? [String: Any])?["events"] as? [[String: Any]])
        GBAssertEqual(freshEvents.count, 2)
        GBAssertTrue(freshEvents.allSatisfy { $0["kind"] as? String == "INITIALIZE" })
        GBAssertEqual(try call("sdk.shutdown", [:], newSession)["ok"] as? Bool, true)
        GB_Shutdown()
    }

    func testHostPushEventRoutingAndDedup() throws {
        pushCallbackLock.lock(); pushCallbackMessages = []; pushCallbackLock.unlock()
        GB_SetCallback(pushBridgeCallback)
        let session = UUID().uuidString.lowercased()
        func send(_ operation: String, _ payload: [String: Any]) throws {
            let request: [String: Any] = ["protocolVersion": 1, "sdkSessionId": session, "kind": "request",
                "requestId": UUID().uuidString.lowercased(), "operation": operation, "payload": payload]
            var data = try JSONSerialization.data(withJSONObject: request)
            if operation == "host.pushOpened" { GBAssertNotNil(data.range(of: Data("한글 🎮🚀".utf8)), "test must send UTF-8 bytes, not escaped text") }
            data.withUnsafeBytes { bytes in GB_Dispatch(bytes.bindMemory(to: UInt8.self).baseAddress, Int32(bytes.count)) }
            data.resetBytes(in: 0..<data.count)
        }
        func receive() throws -> [String: Any] {
            GBAssertEqual(pushCallbackSignal.wait(timeout: .now() + 3), .success)
            pushCallbackLock.lock(); let data = pushCallbackMessages.removeFirst(); pushCallbackLock.unlock()
            return try GBUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        }
        try send("sdk.initialize", ["providerMode": "LOCAL_MOCK", "appId": "demo", "backendBaseUrl": "http://127.0.0.1:18080",
            "requestTimeoutMs": 30000, "developmentKey": String(repeating: "x", count: 32), "mockSubject": "A"])
        GBAssertEqual(try receive()["ok"] as? Bool, true)
        let payload: [String: Any] = ["messageId": "한글 🎮🚀", "route": "store", "campaignId": NSNull(), "url": "https://ignored.invalid"]
        try send("host.pushOpened", payload)
        let event = try receive(), response = try receive()
        GBAssertEqual(event["type"] as? String, "PushOpened")
        GBAssertEqual((event["payload"] as? [String: Any])?["route"] as? String, "store")
        GBAssertEqual((event["payload"] as? [String: Any])?["messageId"] as? String, "한글 🎮🚀")
        GBAssertNil((event["payload"] as? [String: Any])?["url"])
        GBAssertEqual(response["ok"] as? Bool, true)
        try send("host.pushOpened", payload); GBAssertEqual(try receive()["ok"] as? Bool, true)
        GBAssertEqual(pushCallbackSignal.wait(timeout: .now() + 0.1), .timedOut)
        try send("host.pushReceived", ["messageId": "bad", "route": "https://ignored.invalid"])
        GBAssertEqual((try receive()["error"] as? [String: Any])?["code"] as? String, "INVALID_ARGUMENT")
        GB_Shutdown()
    }

}
