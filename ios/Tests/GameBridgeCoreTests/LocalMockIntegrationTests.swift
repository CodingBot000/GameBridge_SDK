import Foundation
import CryptoKit
import XCTest
@testable import GameBridgeCore

private final class TestTokenStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
final class LocalMockIntegrationTests: XCTestCase {
    private func sql(_ statement: String) throws -> String {
        let process = Process(); process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["docker", "exec", "-i", "gamebridge-sdk-local-postgres-1", "psql", "-U", "gamebridge", "-d", "gamebridge_local", "-v", "ON_ERROR_STOP=1", "-tA"]
        let input = Pipe(); let output = Pipe(); process.standardInput = input; process.standardOutput = output; process.standardError = Pipe()
        try process.run(); input.fileHandleForWriting.write(Data(statement.utf8)); try input.fileHandleForWriting.close()
        let data = output.fileHandleForReading.readDataToEndOfFile(); process.waitUntilExit()
        guard process.terminationStatus == 0 else { throw SdkFailure("INTERNAL_ERROR") }
        return String(decoding: data, as: UTF8.self).trimmingCharacters(in: .whitespacesAndNewlines)
    }
    func testConcurrentExpiredRequestsRotateOnceAgainstLocalBackend() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let storage = TestTokenStore(); let client = try LocalMockClient(config: config, store: storage, developmentKey: key)
        _ = try await client.signIn(subject: "A")
        let raw = try XCTUnwrap(storage.value)
        let object = try XCTUnwrap(try JSONSerialization.jsonObject(with: Data(raw.utf8)) as? [String: Any])
        let token = try XCTUnwrap(object["refreshToken"] as? String)
        let digest = SHA256.hash(data: Data(token.utf8)).map { String(format: "%02x", $0) }.joined()
        XCTAssertEqual(try sql("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=decode('\(digest)','hex');"), "UPDATE 1")
        let tasks = (0..<8).map { _ in Task { try await client.wallet() } }
        for task in tasks { let wallet = try await task.value; XCTAssertFalse(wallet.userId.isEmpty) }
        XCTAssertEqual(try sql("SELECT count(*) FROM session_refresh_history WHERE consumed_refresh_hash=decode('\(digest)','hex');"), "1")
        XCTAssertFalse(storage.value?.contains(token) ?? true)
        try await client.signOut()
    }
    func testExpiredAccessLogoutUsesRefreshAgainstLocalBackend() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let storage = TestTokenStore(); let client = try LocalMockClient(config: config, store: storage, developmentKey: key)
        _ = try await client.signIn(subject: "A")
        let raw = try XCTUnwrap(storage.value)
        let object = try XCTUnwrap(try JSONSerialization.jsonObject(with: Data(raw.utf8)) as? [String: Any])
        let token = try XCTUnwrap(object["refreshToken"] as? String)
        let digest = SHA256.hash(data: Data(token.utf8)).map { String(format: "%02x", $0) }.joined()
        XCTAssertEqual(try sql("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=decode('\(digest)','hex');"), "UPDATE 1")
        try await client.signOut(); XCTAssertNil(storage.value)
        XCTAssertEqual(try sql("SELECT count(*) FROM sessions WHERE refresh_hash=decode('\(digest)','hex') AND revoked_at IS NOT NULL;"), "1")
    }
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
        let premiumTransaction = UUID(), premiumAttempt = UUID()
        let premium = try await client.purchase(productId:"premium_unlock", transactionId:premiumTransaction, attemptId:premiumAttempt)
        XCTAssertTrue(premium.entitlements.premiumEnabled)
        let premiumAgain = try await client.purchase(productId:"premium_unlock", transactionId:premiumTransaction, attemptId:premiumAttempt)
        XCTAssertEqual(premiumAgain.fulfillmentStatus, "ALREADY_GRANTED")
        let restored = try LocalMockClient(config: config, store: storage, developmentKey: key)
        let restoredUser = try await restored.restore(); XCTAssertEqual(restoredUser?.userId, user.userId)
        let wallet = try await restored.wallet(); XCTAssertEqual(Int64(wallet.coinBalance), original + 100); XCTAssertTrue(wallet.premiumEnabled)
        let oldCoins = try await restored.purchase(productId:"coins_100", transactionId:transaction, attemptId:attempt)
        let oldPremium = try await restored.purchase(productId:"premium_unlock", transactionId:premiumTransaction, attemptId:premiumAttempt)
        XCTAssertEqual(oldCoins.fulfillmentStatus, "ALREADY_GRANTED"); XCTAssertEqual(oldPremium.fulfillmentStatus, "ALREADY_GRANTED")
        let afterOldPurchases = try await restored.wallet(); XCTAssertEqual(Int64(afterOldPurchases.coinBalance), original + 100); XCTAssertTrue(afterOldPurchases.premiumEnabled)
        try await restored.signOut(); XCTAssertNil(try storage.load())
    }
    func testBridgeHandlerAgainstLocalBackend() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let storage = TestTokenStore(); let handler = LocalMockBridgeHandler { storage }
        let initialization = try await handler.invoke("sdk.initialize", payload: ["appId": "gamebridge-sample", "providerMode": "LOCAL_MOCK",
            "backendBaseUrl": "http://127.0.0.1:18080", "requestTimeoutMs": 30000, "developmentKey": key, "mockSubject": "B", "installationId": UUID().uuidString.lowercased()])
        XCTAssertEqual((initialization as? [String: Any])?["state"] as? String, "READY")
        let profile = try await handler.invoke("auth.signIn", payload: ["provider": "MOCK"])
        let stored = try XCTUnwrap(storage.value)
        let storedSession = try XCTUnwrap(try JSONSerialization.jsonObject(with: Data(stored.utf8)) as? [String: Any])
        let syntheticTokens = try ["accessToken", "refreshToken"].map { try XCTUnwrap(storedSession[$0] as? String) }
        func checkNoTokens(_ value: Any) throws {
            let serialized = String(decoding: try JSONSerialization.data(withJSONObject: value), as: UTF8.self)
            for token in syntheticTokens { XCTAssertFalse(serialized.contains(token), "session token leaked in bridge result") }
        }
        try checkNoTokens(profile)
        let push = try await handler.invoke("push.register", payload: [:]) as? [String: Any]
        XCTAssertEqual(push?["registered"] as? Bool, true)
        try checkNoTokens(try XCTUnwrap(push))
        _ = try await handler.invoke("push.unregister", payload: [:])
        let encodedProfile = try JSONSerialization.data(withJSONObject: profile)
        XCTAssertFalse(String(decoding: encodedProfile, as: UTF8.self).contains(key))
        let beforeValue = try await handler.invoke("store.entitlements", payload: [:])
        let before = try XCTUnwrap(beforeValue as? [String: Any])
        let coins = try XCTUnwrap(Int64(try XCTUnwrap(before["coinBalance"] as? String)))
        let purchaseValue = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"])
        try checkNoTokens(purchaseValue)
        let purchase = try XCTUnwrap(purchaseValue as? [String: Any])
        XCTAssertEqual(purchase["fulfillmentStatus"] as? String, "GRANTED")
        let walletValue = try await handler.invoke("store.entitlements", payload: [:])
        let wallet = try XCTUnwrap(walletValue as? [String: Any])
        XCTAssertEqual(Int64(try XCTUnwrap(wallet["coinBalance"] as? String)), coins + 100)
        let restoredValue = try await handler.invoke("auth.restore", payload: [:])
        try checkNoTokens(restoredValue)
        let restored = try XCTUnwrap(restoredValue as? [String: Any])
        XCTAssertEqual(restored["sessionRestored"] as? Bool, true)
        _ = try await handler.invoke("auth.signOut", payload: [:]); XCTAssertNil(storage.value)
        _ = try await handler.invoke("sdk.shutdown", payload: [:])
    }

    func testPersistedMockTransactionRecoversAfterCommittedResponseIsLost() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let sessions = TestTokenStore(), pending = TestTokenStore()
        let client = try LocalMockClient(config: config, store: sessions, developmentKey: key, pendingStore: pending)
        let user = try await client.signIn(subject: "B"); let before = try await client.wallet()
        let transaction = UUID().uuidString.lowercased(), attempt = UUID().uuidString.lowercased()
        let secret = try XCTUnwrap(sessions.value); let stored = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(secret.utf8)) as? [String: Any])
        let token = try XCTUnwrap(stored["accessToken"] as? String)
        let item: [[String: Any]] = [["appId": config.appId, "backendBaseURL": config.backendBaseURL!, "userId": user.userId,
            "productId": "coins_100", "transactionId": transaction, "attemptId": attempt]]
        try pending.save(String(decoding: JSONSerialization.data(withJSONObject: item), as: UTF8.self))
        let body = try JSONSerialization.data(withJSONObject: ["productId": "coins_100", "quantity": 1, "proof": "mock:\(user.userId):coins_100:\(transaction)"])
        let backend = try BackendClient(config: config)
        _ = try await backend.request(path: "/v1/purchases/verify", method: "POST", body: body, accessToken: token, idempotencyKey: attempt)
        let restarted = try LocalMockClient(config: config, store: sessions, developmentKey: key, pendingStore: pending)
        let restored = try await restarted.restore(); XCTAssertNotNil(restored)
        let counts = try await restarted.recoverPending(); XCTAssertEqual(counts.examinedCount, 1); XCTAssertEqual(counts.recoveredCount, 1)
        XCTAssertNil(pending.value)
        let wallet = try await restarted.wallet(); XCTAssertEqual(Int64(wallet.coinBalance), try XCTUnwrap(Int64(before.coinBalance)) + 100)
        try await restarted.signOut()
    }

    func testMockPushUnregisterAndLogoutRemoveToken() async throws {
        try XCTSkipUnless(ProcessInfo.processInfo.environment["GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST"] == "true", "Explicit local mock backend test only")
        let key = try XCTUnwrap(ProcessInfo.processInfo.environment["GAMEBRIDGE_DEV_AUTH_KEY"])
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let client = try LocalMockClient(config: config, store: TestTokenStore(), developmentKey: key)
        _ = try await client.signIn(subject: "B"); let id = UUID()
        let first = try await client.registerMockPush(installationId: id)
        XCTAssertNotNil(first.tokenFingerprint.range(of: "^[0-9a-f]{12}$", options: .regularExpression))
        XCTAssertEqual(try sql("SELECT count(*) FROM device_tokens WHERE installation_id='\(id.uuidString)' AND environment='local-mock';"), "1")
        try await client.unregisterMockPush(installationId: id)
        XCTAssertEqual(try sql("SELECT count(*) FROM device_tokens WHERE installation_id='\(id.uuidString)' AND environment='local-mock';"), "0")
        _ = try await client.registerMockPush(installationId: id); try await client.signOut()
        XCTAssertEqual(try sql("SELECT count(*) FROM device_tokens WHERE installation_id='\(id.uuidString)' AND environment='local-mock';"), "0")
    }

}
