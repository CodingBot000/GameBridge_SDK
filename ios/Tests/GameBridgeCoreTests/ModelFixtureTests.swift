import Foundation
import XCTest
@testable import GameBridgeCore

private struct Fixture: Codable, Equatable {
    let profile: UserProfile
    let product: StoreProduct
    let purchase: PurchaseResult
    let error: SdkError
}
final class ModelFixtureTests: XCTestCase {
    private func source() throws -> Data {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let contracts = ProcessInfo.processInfo.environment["GAMEBRIDGE_CONTRACT_ROOT"].map { URL(fileURLWithPath: $0) } ?? root.appendingPathComponent("contracts")
        return try Data(contentsOf: contracts.appendingPathComponent("fixtures/models/roundtrip.json"))
    }
    func testSharedFixtureRoundTrip() throws {
        let value = try JSONDecoder().decode(Fixture.self, from: source())
        let restored = try JSONDecoder().decode(Fixture.self, from: JSONEncoder().encode(value))
        XCTAssertEqual(value, restored)
        XCTAssertEqual(restored.profile.displayName, "별빛 🎮")
        XCTAssertEqual(restored.product.priceMicros, "9223372036854775807")
    }
    func testMissingNullableAndUnknownEnumAreRejected() throws {
        let text = String(decoding: try source(), as: UTF8.self)
        XCTAssertThrowsError(try JSONDecoder().decode(Fixture.self, from: Data(text.replacingOccurrences(of: "\"displayName\":\"별빛 🎮\",", with: "").utf8)))
        XCTAssertThrowsError(try JSONDecoder().decode(Fixture.self, from: Data(text.replacingOccurrences(of: "\"CONSUMABLE\"", with: "\"UNKNOWN\"").utf8)))
    }
}
