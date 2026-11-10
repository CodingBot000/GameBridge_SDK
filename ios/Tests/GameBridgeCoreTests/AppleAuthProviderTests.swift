import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeApple

private final class AppleProofProtocol: URLProtocol {
    static var responseBody = Data()
    static var capturedPath: String?
    static var capturedAuth: String?
    static var capturedIdempotency: String?
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        Self.capturedPath = request.url?.path
        Self.capturedAuth = request.value(forHTTPHeaderField: "Authorization")
        Self.capturedIdempotency = request.value(forHTTPHeaderField: "Idempotency-Key")
        let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Self.responseBody)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
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
    var expired = false
    var refreshes = 0
    var refreshFails = false
    func challenge(appId: String) async throws -> AppleChallenge { AppleChallenge(challengeId: "dc9a46f4-8e20-4880-bcbb-ac45033157ca", nonce: "server-nonce", expiresAt: "2030-01-01T00:00:00Z") }
    func exchange(challengeId: String, credential: AppleCredential) async throws -> AppleSession {
        AppleSession(accessToken: "test-access", refreshToken: "test-refresh", expiresAt: "2030-01-01T00:00:00.123Z", userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", appleUserIdentifier: credential.userIdentifier, appId: "demo", providerMode: "PLATFORM_SANDBOX", backendBaseURL: "https://example.com")
    }
    func profile(session: AppleSession) async throws -> UserProfile {
        if expired && session.accessToken == "test-access" { throw SdkFailure("SESSION_EXPIRED") }
        return UserProfile(userId: profileUser, displayName: nil, provider: "APPLE")
    }
    func refresh(session: AppleSession) async throws -> AppleSession {
        refreshes += 1
        try await Task.sleep(nanoseconds: 30_000_000)
        if refreshFails { throw SdkFailure("TIMEOUT") }
        return AppleSession(accessToken: "test-access-new", refreshToken: "test-refresh-new", expiresAt: session.expiresAt, userId: session.userId,
                            appleUserIdentifier: session.appleUserIdentifier, appId: session.appId, providerMode: session.providerMode, backendBaseURL: session.backendBaseURL)
    }
    func revoke(session: AppleSession) async throws { revoked = true; if revokeFails { throw SdkFailure("NETWORK_UNAVAILABLE") } }
}
final class AppleAuthProviderTests: XCTestCase {
    func testAppleHttpRevokeFallsBackToRefresh() async throws {
        SessionProtocol.reset(.timeout)
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [SessionProtocol.self]
        let config = GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com")
        let backend = try HttpAppleBackend(config: config, sessionConfiguration: configuration)
        let session = AppleSession(accessToken: "test-access", refreshToken: "test-refresh", expiresAt: "2030-01-01T00:00:00Z", userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", appleUserIdentifier: "test-user", appId: "demo", providerMode: "PLATFORM_SANDBOX", backendBaseURL: "https://example.com")
        try await backend.revoke(session: session)
        XCTAssertEqual(SessionProtocol.logoutCount(), 1)
    }
    @MainActor func testNonceProfileAndRevokedLocalLogout() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); let backend = AppleFakeBackend()
        let provider = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: store, gateway: gateway, backend: backend)
        let user = try await provider.signIn()
        XCTAssertEqual(gateway.nonce, "server-nonce"); XCTAssertEqual(user.provider, "APPLE"); XCTAssertNotNil(store.value)
        XCTAssertFalse(String(describing: user).contains("test-apple-token"))
        let saved = store.value
        let mock = try LocalMockClient(config: GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:1"), store: store, developmentKey: String(repeating: "x", count: 32))
        do { _ = try await mock.restore(); XCTFail("Apple session must not reach mock backend") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        XCTAssertFalse(String(describing: AppleCredential(identityToken: "test-apple-token", userIdentifier: "user", displayName: nil)).contains("test-apple-token"))
        XCTAssertFalse(String(describing: AppleChallenge(challengeId: "id", nonce: "server-nonce", expiresAt: "time")).contains("server-nonce"))
        gateway.state = .revoked; backend.revokeFails = true
        do { _ = try await provider.checkCredentialState(); XCTFail("revoke error") } catch let error as SdkFailure { XCTAssertEqual(error.code, "NETWORK_UNAVAILABLE"); XCTAssertEqual(error.nativeCode, "REVOCATION_UNCONFIRMED") }
        XCTAssertNil(store.value); XCTAssertTrue(backend.revoked)
    }
    @MainActor func testAppleProofSinkRequiresDurableServerGrant() async throws {
        let config = GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com")
        let auth = AppleAuthProvider(config: config, store: AppleMemoryStore(), gateway: AppleFakeGateway(), backend: AppleFakeBackend())
        let user = try await auth.signIn()
        let binding = UUID(), purchase = UUID()
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [AppleProofProtocol.self]
        let client = try BackendClient(config: config, sessionConfiguration: configuration)
        let sink = AppleHttpProofSink(auth: auth, client: client)
        let proof = ApplePurchaseProof(transactionId: 42, productId: "coins", binding: binding, signedTransaction: "test-secret-jws")
        func response(_ status: String) -> Data {
            Data("{\"userId\":\"\(user.userId)\",\"bindingId\":\"\(binding.uuidString)\",\"productId\":\"coins\",\"transactionKey\":\"42\",\"serverPurchaseId\":\"\(purchase.uuidString)\",\"fulfillmentStatus\":\"\(status)\"}".utf8)
        }
        AppleProofProtocol.responseBody = response("GRANTED")
        let grant = try await sink.verify(proof, userId: UUID(uuidString: user.userId)!)
        XCTAssertEqual(grant.serverPurchaseId, purchase)
        XCTAssertEqual(AppleProofProtocol.capturedPath, "/v1/purchases/apple/verify")
        XCTAssertEqual(AppleProofProtocol.capturedAuth, "Bearer test-access")
        XCTAssertNotNil(AppleProofProtocol.capturedIdempotency.flatMap(UUID.init(uuidString:)))
        XCTAssertFalse(String(describing: grant).contains("test-secret-jws"))
        AppleProofProtocol.responseBody = response("PENDING")
        do { _ = try await sink.verify(proof, userId: UUID(uuidString: user.userId)!); XCTFail("pending is not a grant") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "BRIDGE_PROTOCOL_MISMATCH") }
    }
    @MainActor func testPurchaseBindingCacheInvalidatesOnLogout() async throws {
        let auth = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: AppleMemoryStore(), gateway: AppleFakeGateway(), backend: AppleFakeBackend())
        _ = try await auth.signIn()
        let binding = UUID()
        let source = ApplePurchaseAccountSource(auth: auth) { token in
            XCTAssertEqual(token, "test-access")
            return Data("{\"appleAccountToken\":\"\(binding.uuidString)\"}".utf8)
        }
        let account = try await source.refresh()
        XCTAssertEqual(account?.binding, binding)
        XCTAssertNotNil(source.current())
        try await auth.signOut()
        XCTAssertNil(source.current())
        do { _ = try parseAppleBinding(userId: UUID().uuidString, data: Data("{}".utf8)); XCTFail("invalid binding") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "BRIDGE_PROTOCOL_MISMATCH") }
    }
    @MainActor func testLatePurchaseBindingAfterLogoutIsDiscarded() async throws {
        let auth = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: AppleMemoryStore(), gateway: AppleFakeGateway(), backend: AppleFakeBackend())
        _ = try await auth.signIn()
        var continuation: CheckedContinuation<Void, Never>?
        var entered = false
        let source = ApplePurchaseAccountSource(auth: auth) { _ in
            entered = true
            await withCheckedContinuation { continuation = $0 }
            return Data("{\"appleAccountToken\":\"\(UUID().uuidString)\"}".utf8)
        }
        let pending = Task { try await source.refresh() }
        while !entered { await Task.yield() }
        try await auth.signOut()
        continuation?.resume()
        do { _ = try await pending.value; XCTFail("late binding") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "CANCELED") }
        XCTAssertNil(source.current())
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
    @MainActor func testConcurrentRestoreSharesRefreshAndOfflineLogoutClearsLocally() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); let backend = AppleFakeBackend()
        let config = GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com")
        let provider = AppleAuthProvider(config: config, store: store, gateway: gateway, backend: backend)
        _ = try await provider.signIn(); backend.expired = true
        let wrong = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://other.example"), store: store, gateway: gateway, backend: backend)
        let saved = store.value
        do { _ = try await wrong.restore(); XCTFail("different server") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        do { try await wrong.signOut(); XCTFail("foreign session must not be deleted") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        let tasks = (0..<8).map { _ in Task { @MainActor in try await provider.restore() } }
        for task in tasks { let result = try await task.value; XCTAssertNotNil(result) }
        XCTAssertEqual(backend.refreshes, 1)
        backend.revokeFails = true
        do { try await provider.signOut(); XCTFail("revoke failure") } catch let error as SdkFailure { XCTAssertEqual(error.code, "NETWORK_UNAVAILABLE"); XCTAssertEqual(error.nativeCode, "REVOCATION_UNCONFIRMED") }
        XCTAssertNil(store.value)
    }
    @MainActor func testLostRefreshLeavesTombstone() async throws {
        let store = AppleMemoryStore(); let gateway = AppleFakeGateway(); let backend = AppleFakeBackend()
        let provider = AppleAuthProvider(config: GameBridgeConfig(appId: "demo", mode: .platformSandbox, backendBaseURL: "https://example.com"), store: store, gateway: gateway, backend: backend)
        _ = try await provider.signIn(); backend.expired = true; backend.refreshFails = true
        do { _ = try await provider.restore(); XCTFail("refresh timeout") } catch let error as SdkFailure { XCTAssertEqual(error.code, "TIMEOUT") }
        XCTAssertEqual(store.value, "{\"state\":\"refresh_pending\"}")
        do { _ = try await provider.restore(); XCTFail("old refresh replay") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(backend.refreshes, 1)
        do { try await provider.signOut(); XCTFail("unconfirmed remote revoke") }
        catch let error as SdkFailure { XCTAssertEqual(error.nativeCode, "REVOCATION_UNCONFIRMED") }
        XCTAssertNil(store.value)
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
