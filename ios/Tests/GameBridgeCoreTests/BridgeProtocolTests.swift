import Foundation
import XCTest
@testable import GameBridgeCore

final class BridgeProtocolTests: XCTestCase {
    func fixture(_ name: String) throws -> Data {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        return try Data(contentsOf: root.appendingPathComponent("contracts/fixtures/bridge/\(name).json"))
    }
    func testValidEnvelopes() throws {
        _ = try BridgeProtocol.parse(fixture("request"))
        _ = try BridgeProtocol.parse(fixture("pending"), expectedSession: "dc9a46f4-8e20-4880-bcbb-ac45033157ca", expectedRequest: "2efc133b-3138-4c3e-aa72-0532cd19056e")
    }
    func testRejectsMalformedInputs() throws {
        for name in ["invalid-failure", "invalid-version", "invalid-operation"] {
            XCTAssertThrowsError(try BridgeProtocol.parse(fixture(name)))
        }
        XCTAssertThrowsError(try BridgeProtocol.parse(fixture("pending"), expectedRequest: "other"))
        XCTAssertThrowsError(try BridgeProtocol.parse(Data([0xc3])))
        XCTAssertThrowsError(try BridgeProtocol.parse(Data(count: BridgeProtocol.maxBytes + 1)))
    }
}
