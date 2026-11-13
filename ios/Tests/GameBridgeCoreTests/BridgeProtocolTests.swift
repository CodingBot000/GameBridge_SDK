import Foundation
import XCTest
@testable import GameBridgeCore

final class BridgeProtocolTests: XCTestCase {
    func fixture(_ name: String) throws -> Data {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let contracts = ProcessInfo.processInfo.environment["GAMEBRIDGE_CONTRACT_ROOT"].map { URL(fileURLWithPath: $0) } ?? root.appendingPathComponent("contracts")
        return try Data(contentsOf: contracts.appendingPathComponent("fixtures/bridge/\(name).json"))
    }
    func testValidEnvelopes() throws {
        for name in ["request", "success", "failure", "event", "unsupported"] { _ = try BridgeProtocol.parse(fixture(name)) }
        _ = try BridgeProtocol.parse(fixture("pending"), expectedSession: "dc9a46f4-8e20-4880-bcbb-ac45033157ca", expectedRequest: "2efc133b-3138-4c3e-aa72-0532cd19056e")
    }
    func testRejectsMalformedInputs() throws {
        for name in ["invalid-failure", "invalid-version", "invalid-operation"] {
            XCTAssertThrowsError(try BridgeProtocol.parse(fixture(name)))
        }
        XCTAssertThrowsError(try BridgeProtocol.parse(fixture("pending"), expectedRequest: "other"))
        XCTAssertThrowsError(try BridgeProtocol.parse(Data([0xc3])))
        XCTAssertThrowsError(try BridgeProtocol.parse(Data("{".utf8)))
        var request = try XCTUnwrap(JSONSerialization.jsonObject(with: fixture("request")) as? [String: Any])
        request.removeValue(forKey: "requestId")
        XCTAssertThrowsError(try BridgeProtocol.parse(JSONSerialization.data(withJSONObject: request)))
        let root = ProcessInfo.processInfo.environment["GAMEBRIDGE_CONTRACT_ROOT"].map { URL(fileURLWithPath: $0) } ?? URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("contracts")
        let length = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: root.appendingPathComponent("fixtures/bridge-length.json"))) as? [String: Any])
        let maxBytes = try XCTUnwrap(length["maxBytes"] as? Int)
        let invalidBytes = try XCTUnwrap(length["invalidBytes"] as? Int)
        XCTAssertEqual(maxBytes, BridgeProtocol.maxBytes)
        XCTAssertEqual(invalidBytes, maxBytes + 1)
        XCTAssertEqual(length["expectedError"] as? String, "PAYLOAD_TOO_LARGE")
        XCTAssertThrowsError(try BridgeProtocol.parse(Data(count: invalidBytes)))
    }
}
