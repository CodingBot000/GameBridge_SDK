import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeApple

private final class AppleMemoryStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
@MainActor private final class AppleFakeGateway: AppleCredentialGateway {
    var nonce: String?
    var state: AppleCredentialState = .authorized
    var failure: SdkFailure?
    var hold = false
    var entered = false
    var continuation: CheckedContinuation<Void, Never>?
    func authorize(nonce: String) async throws -> AppleCredential {
        self.nonce = nonce; entered = true
        if hold { await withCheckedContinuation { continuation = $0 } }
        if let failure { throw failure }
        return AppleCredential(identityToken: "test-apple-token", userIdentifier: "test-apple-user", displayName: nil)
    }
    func credentialState(userIdentifier: String) async throws -> AppleCredentialState { state }
    func waitForEntry() async { while !entered { await Task.yield() } }
    func release() { continuation?.resume(); continuation = nil }
}
private final class AppleFakeBackend: AppleAuthBackend {
    var profileUser = "d2719c4e-d533-47ee-9efd-838791ea79c8"
    var revoked = false
    var revokeFails = false
    func challenge(appId: String) async throws -> AppleChallenge { AppleChallenge(challengeId: "dc9a46f4-8e20-4880-bcbb-ac45033157ca", nonce: "server-nonce", expiresAt: "2030-01-01T00:00:00Z") }
    func exchange(challengeId: String, credential: AppleCredential) async throws -> AppleSession {
        AppleSession(accessToken: "test-access", refreshToken: "test-refresh", expiresAt: "2030-01-01T00:00:00.123Z", userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", appleUserIdentifier: credential.userIdentifier)
    }
    func profile(session: AppleSession) async throws -> UserProfile { UserProfile(userId: profileUser, displayName: nil, provider: "APPLE") }
    func revoke(session: AppleSession) async throws { revoked = true; if revokeFails { throw SdkFailure("NETWORK_UNAVAILABLE") } }
}
final class AppleAuthProviderTests: XCTestCase {
    @MainActor func testNonceProfileAndRevokedLocalLogout() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); let backend = AppleFakeBackend()
        let provider = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: store, gateway: gateway, backend: backend)
        let user = try await provider.signIn()
        XCTAssertEqual(gateway.nonce, "server-nonce"); XCTAssertEqual(user.provider, "APPLE"); XCTAssertNotNil(store.value)
        XCTAssertFalse(String(describing: user).contains("test-apple-token"))
        XCTAssertFalse(String(describing: AppleCredential(identityToken: "test-apple-token", userIdentifier: "user", displayName: nil)).contains("test-apple-token"))
        XCTAssertFalse(String(describing: AppleChallenge(challengeId: "id", nonce: "server-nonce", expiresAt: "time")).contains("server-nonce"))
        gateway.state = .revoked; backend.revokeFails = true
        do { _ = try await provider.checkCredentialState(); XCTFail("revoke error") } catch let error as SdkFailure { XCTAssertEqual(error.code, "NETWORK_UNAVAILABLE") }
        XCTAssertNil(store.value); XCTAssertTrue(backend.revoked)
    }
    @MainActor func testConcurrentAuthorizationIsBusy() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); gateway.hold = true
        let provider = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: store, gateway: gateway, backend: AppleFakeBackend())
        let first = Task { try await provider.signIn() }
        await gateway.waitForEntry()
        do { _ = try await provider.signIn(); XCTFail("concurrent authorization") } catch let error as SdkFailure { XCTAssertEqual(error.code, "BUSY") }
        do { _ = try await provider.checkCredentialState(); XCTFail("concurrent credential state") } catch let error as SdkFailure { XCTAssertEqual(error.code, "BUSY") }
        gateway.release(); _ = try await first.value
    }
    @MainActor func testCancellationAndMismatchedProfileDoNotSave() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); let backend = AppleFakeBackend()
        let provider = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: store, gateway: gateway, backend: backend)
        gateway.failure = SdkFailure("CANCELED")
        do { _ = try await provider.signIn(); XCTFail("cancellation") } catch let error as SdkFailure { XCTAssertEqual(error.code, "CANCELED") }
        XCTAssertNil(store.value); gateway.failure = nil; backend.profileUser = "8e37925d-a1a8-4118-84eb-b00668b9d469"
        do { _ = try await provider.signIn(); XCTFail("mismatch") } catch let error as SdkFailure { XCTAssertEqual(error.code, "AUTH_FAILED") }
        XCTAssertNil(store.value)
    }
}
