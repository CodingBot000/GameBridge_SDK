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
        let restored = try LocalMockClient(config: config, store: storage, developmentKey: key)
        let restoredUser = try await restored.restore(); XCTAssertEqual(restoredUser?.userId, user.userId)
        let wallet = try await restored.wallet(); XCTAssertEqual(Int64(wallet.coinBalance), original + 100)
        try await restored.signOut(); XCTAssertNil(try storage.load())
    }
}
