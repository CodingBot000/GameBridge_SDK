import Foundation
import XCTest
import StoreKitTest
import GameBridgeCore
@testable import GameBridgeApple

private final class DropCommittedGrantProtocol: URLProtocol {
    static let lock = NSLock()
    static var dropGrants = true
    static var droppedCommittedCount = 0
    static func droppedCount() -> Int { lock.lock(); defer { lock.unlock() }; return droppedCommittedCount }
    static func setDrop(_ value: Bool) { lock.lock(); dropGrants = value; lock.unlock() }
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let config = URLSessionConfiguration.ephemeral; config.protocolClasses = []
        let session = URLSession(configuration: config)
        session.dataTask(with: request) { data, response, error in
            defer { session.finishTasksAndInvalidate() }
            if let error { self.client?.urlProtocol(self, didFailWithError: error); return }
            guard let response = response as? HTTPURLResponse, let data else { self.client?.urlProtocol(self, didFailWithError: URLError(.badServerResponse)); return }
            Self.lock.lock(); let drop = Self.dropGrants; Self.lock.unlock()
            if self.request.url?.path == "/v1/dev/xcode-storekit/grant", response.statusCode == 200, drop {
                Self.lock.lock(); Self.droppedCommittedCount += 1; Self.lock.unlock()
                let failure = HTTPURLResponse(url:self.request.url!, statusCode:503, httpVersion:nil, headerFields:["Content-Type":"application/json"])!
                self.client?.urlProtocol(self, didReceive:failure, cacheStoragePolicy:.notAllowed)
                self.client?.urlProtocol(self, didLoad:Data(#"{"code":"NETWORK_UNAVAILABLE"}"#.utf8))
            } else {
                self.client?.urlProtocol(self, didReceive:response, cacheStoragePolicy:.notAllowed)
                self.client?.urlProtocol(self, didLoad:data)
            }
            self.client?.urlProtocolDidFinishLoading(self)
        }.resume()
    }
    override func stopLoading() {}
}
private final class FailOnceClearStore: TokenStore {
    let backing: TokenStore
    var shouldFail = true
    init(_ backing: TokenStore) { self.backing = backing }
    func load() throws -> String? { try backing.load() }
    func save(_ value: String) throws { try backing.save(value) }
    func clear() throws {
        if shouldFail { shouldFail = false; throw SdkFailure("INTERNAL_ERROR") }
        try backing.clear()
    }
}
final class XcodeStoreKitLocalDatabaseTests: XCTestCase {
    @MainActor func testCommittedGrantResponseLossRecoversAfterJournalRecreation() async throws {
        let environment = ProcessInfo.processInfo.environment
        guard environment["GAMEBRIDGE_RUN_XCODE_DB_E2E"] == "true" else { throw XCTSkip("explicit local database E2E opt-in required") }
        let base = try XCTUnwrap(environment["GAMEBRIDGE_XCODE_E2E_BASE_URL"]), key = try XCTUnwrap(environment["GAMEBRIDGE_XCODE_E2E_AUTH_KEY"])
        guard base.hasPrefix("http://127.0.0.1:") else { throw SdkFailure("CONFIG_REQUIRED") }
        let session = try SKTestSession(configurationFileNamed:"GameBridge"); session.disableDialogs = true
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [DropCommittedGrantProtocol.self]
        let identifier = UUID().uuidString.lowercased()
        let sessionService = "com.gamebridge.test.xcode.session." + identifier
        let pendingService = "com.gamebridge.test.xcode.pending." + identifier
        let authStore = KeychainTokenStore(service:sessionService), pendingStore = KeychainTokenStore(service:pendingService)
        let config = GameBridgeConfig(appId:"gamebridge-sample", mode:.localMock, backendBaseURL:base, requestTimeoutMs:5000)
        var stage = "client construction"
        do {
        let client = try LocalMockClient(config:config, store:authStore, developmentKey:key, sessionConfiguration:configuration)
        stage = "sign in and session Keychain save"
        _ = try await client.signIn(subject:"A")
        do {
            _ = try await XcodeStoreKitSession(client:client, pendingStore:KeychainTokenStore(service:sessionService), enableTestGrant:true)
            XCTFail("separate Keychain objects with same service must be rejected")
        } catch let error as SdkFailure { XCTAssertEqual(error.code, "CONFIG_REQUIRED") }
        DropCommittedGrantProtocol.setDrop(true)
        stage = "initial Xcode account"
        let first = try await XcodeStoreKitSession(client:client, pendingStore:pendingStore, enableTestGrant:true)
        stage = "first StoreKit start"
        try await first.start()
        stage = "purchase and dropped grant response"
        let result = try await first.purchase("coins_100")
        XCTAssertEqual(result.status, .verificationPending)
        XCTAssertGreaterThan(DropCommittedGrantProtocol.droppedCount(), 0, "server grant must commit before response is dropped")
        let accountBeforeRestart = try await client.xcodeAccount()
        let walletBeforeRestart = try await client.xcodeWallet(account: accountBeforeRestart)
        XCTAssertEqual(walletBeforeRestart.coinBalance, "100", "grant must already be committed before recovery")
        XCTAssertNotNil(try pendingStore.load(), "attempt must be durable before retry")
        first.stop()
        DropCommittedGrantProtocol.setDrop(false)
        stage = "recreate client and restore"
        let restored = try LocalMockClient(config:config, store:KeychainTokenStore(service:sessionService), developmentKey:key, sessionConfiguration:configuration)
        let restoredUser = try await restored.restore(); XCTAssertNotNil(restoredUser)
        let recreatedPending = KeychainTokenStore(service:pendingService)
        stage = "recreate StoreKit and journal"
        let recovered = try await XcodeStoreKitSession(client:restored, pendingStore:FailOnceClearStore(recreatedPending), enableTestGrant:true)
        stage = "recover and finish with injected journal clear failure"
        try await recovered.start()
        let wallet = try await recovered.wallet()
        XCTAssertEqual(wallet.coinBalance, "100", "response loss must not grant twice")
        XCTAssertNotNil(try recreatedPending.load(), "failed cleanup must retain journal")
        recovered.stop()
        stage = "reconcile finished consumable after second recreation"
        let finalStore = KeychainTokenStore(service:pendingService)
        let final = try await XcodeStoreKitSession(client:restored, pendingStore:finalStore, enableTestGrant:true)
        try await final.start()
        XCTAssertNil(try finalStore.load(), "verified completed transaction must clear stale journal")
        let finalWallet = try await final.wallet(); XCTAssertEqual(finalWallet.coinBalance, "100")
        let remaining = try await final.recover(userInitiated:false); XCTAssertEqual(remaining.examinedCount, 0)
        final.stop(); try await restored.signOut()
        } catch {
            XCTFail("local E2E failed at stage: \(stage), error type: \(type(of:error))")
            throw error
        }
    }
}
