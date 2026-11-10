import Foundation
import XCTest
import GameBridgeCore
import GameBridgeTesting

final class OfflineFakeTests: XCTestCase {
    func testExplicitFakeAndDuplicatePurchase() async throws {
        let fake = OfflineFake()
        do { _ = try await fake.initialize(GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com")); XCTFail("real mode must reject fake") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "UNSUPPORTED_PROVIDER") }
        _ = try await fake.initialize(GameBridgeConfig(appId: "demo", mode: .editorOffline, backendBaseURL: nil))
        _ = try await fake.signIn(); let products = try await fake.products(); XCTAssertEqual(products.count, 2)
        let id = UUID(uuidString: "e576c264-01d7-44a5-a264-856e7c0d91c0")!
        let pending = try await fake.purchase(productId: "coins_100", transactionId: id, scenario: .pending)
        XCTAssertEqual(pending.wallet.coinBalance, 0)
        let first = try await fake.purchase(productId: "coins_100", transactionId: id, scenario: .success)
        let duplicate = try await fake.purchase(productId: "coins_100", transactionId: id, scenario: .success)
        XCTAssertTrue(first.granted); XCTAssertFalse(duplicate.granted); XCTAssertEqual(duplicate.wallet.coinBalance, 100)
        let permission = try await fake.requestPushPermission(); XCTAssertTrue(permission)
        let fingerprint = try await fake.registerPush(); XCTAssertEqual(fingerprint, "mock-fingerprint")
        try await fake.receivePush(messageId: "message-1", route: "store")
        try await fake.receivePush(messageId: "message-1", route: "store")
        let events = try await fake.drainPushEvents(); XCTAssertEqual(events.count, 1); XCTAssertEqual(events.first?.route, "store")
        do { try await fake.receivePush(messageId: "message-2", route: "https://example.com"); XCTFail("route must be rejected") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "INVALID_ARGUMENT") }
        try await fake.shutdown()
    }
}
