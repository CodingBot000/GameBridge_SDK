import Foundation
import XCTest
@testable import GameBridgeCore

private final class TestTokenStore: TokenStore {
    private var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
final class LocalMockIntegrationTests: XCTestCase {
    func testLocalServerWalletAndRestore() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let storage = TestTokenStore(); let client = try LocalMockClient(config: config, store: storage, developmentKey: key)
        let user = try await client.signIn(subject: "A")
        let products = try await client.products(); XCTAssertEqual(products.count, 2)
        let before = try await client.wallet(); let original = try XCTUnwrap(Int64(before.coinBalance))
        let transaction = UUID(); let attempt = UUID()
        let first = try await client.purchase(productId: "coins_100", transactionId: transaction, attemptId: attempt)
        let duplicate = try await client.purchase(productId: "coins_100", transactionId: transaction, attemptId: attempt)
        XCTAssertEqual(Int64(first.entitlements.coinBalance), original + 100)
        XCTAssertEqual(Int64(duplicate.entitlements.coinBalance), original + 100)
        let restored = try LocalMockClient(config: config, store: storage, developmentKey: key)
        let restoredUser = try await restored.restore(); XCTAssertEqual(restoredUser?.userId, user.userId)
        let wallet = try await restored.wallet(); XCTAssertEqual(Int64(wallet.coinBalance), original + 100)
        try await restored.signOut(); XCTAssertNil(try storage.load())
    }
}
