import Foundation
import XCTest
import GameBridgeCore

final class MockRecoveryDeviceTests: XCTestCase {
    func testKeychainInstancesRecoverCommittedMockPurchaseOnce() async throws {
        let prefix = "com.gamebridge.sdk.test.recovery." + UUID().uuidString.lowercased()
        let sessions = KeychainTokenStore(service: prefix + ".session")
        let pending = KeychainTokenStore(service: prefix + ".pending")
        defer { try? sessions.clear(); try? pending.clear() }
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let key = "local-test-key-0123456789-abcdef0123456789"
        let client = try LocalMockClient(config: config, store: sessions, developmentKey: key, pendingStore: pending)
        let user = try await client.signIn(subject: "B"); let before = try await client.wallet()
        let transaction = UUID().uuidString.lowercased(), attempt = UUID().uuidString.lowercased()
        let raw = try XCTUnwrap(sessions.load())
        let secret = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(raw.utf8)) as? [String: Any])
        let token = try XCTUnwrap(secret["accessToken"] as? String)
        let item: [[String: Any]] = [["appId": config.appId, "backendBaseURL": config.backendBaseURL!, "userId": user.userId,
            "productId": "coins_100", "transactionId": transaction, "attemptId": attempt]]
        try pending.save(String(decoding: JSONSerialization.data(withJSONObject: item), as: UTF8.self))
        let body = try JSONSerialization.data(withJSONObject: ["productId": "coins_100", "quantity": 1, "proof": "mock:\(user.userId):coins_100:\(transaction)"])
        _ = try await BackendClient(config: config).request(path: "/v1/purchases/verify", method: "POST", body: body, accessToken: token, idempotencyKey: attempt)
        let restarted = try LocalMockClient(config: config, store: KeychainTokenStore(service: prefix + ".session"), developmentKey: key,
                                            pendingStore: KeychainTokenStore(service: prefix + ".pending"))
        let restored = try await restarted.restore(); XCTAssertNotNil(restored)
        let counts = try await restarted.recoverPending(); XCTAssertEqual(counts.examinedCount, 1); XCTAssertEqual(counts.recoveredCount, 1)
        XCTAssertNil(try pending.load())
        let wallet = try await restarted.wallet(); XCTAssertEqual(Int64(wallet.coinBalance), try XCTUnwrap(Int64(before.coinBalance)) + 100)
        try await restarted.signOut()
    }
}
