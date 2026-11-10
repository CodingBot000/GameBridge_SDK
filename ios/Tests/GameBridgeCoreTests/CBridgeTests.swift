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
}
