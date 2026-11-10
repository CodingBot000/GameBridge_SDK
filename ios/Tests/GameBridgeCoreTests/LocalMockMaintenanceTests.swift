import Foundation
import XCTest
@testable import GameBridgeCore

private final class MaintenanceStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
private final class MaintenanceProtocol: URLProtocol {
    static let lock = NSLock()
    static var configured = false
    static var verifyCalls = 0
    static func reset() { lock.lock(); configured = false; verifyCalls = 0; lock.unlock() }
    static func setConfigured(_ value: Bool) { lock.lock(); configured = value; lock.unlock() }
    static func count() -> Int { lock.lock(); defer { lock.unlock() }; return verifyCalls }
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let path = request.url!.path
        var status = 200, body = "{}"
        switch path {
        case "/v1/dev/auth": body = #"{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}"#
        case "/v1/config":
            Self.lock.lock(); let configured = Self.configured; Self.lock.unlock()
            if configured { body = #"{"revision":"r","maintenanceEnabled":true,"message":null,"expiresAt":"2099-01-01T00:00:00Z"}"# }
            else { status = 503; body = #"{"code":"CONFIG_REQUIRED"}"# }
        case "/v1/purchases/verify": Self.lock.lock(); Self.verifyCalls += 1; Self.lock.unlock(); status = 500
        case "/v1/entitlements": body = #"{"userId":"d2719c4e-d533-47ee-9efd-838791ea79c8","premiumEnabled":false,"coinBalance":"0","revision":"0","updatedAt":"2026-01-01T00:00:00Z"}"#
        case "/v1/auth/logout": body = #"{"signedOut":true}"#
        default: status = 404
        }
        let response = HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: nil)!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(body.utf8)); client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class LocalMockMaintenanceTests: XCTestCase {
    func testMissingAndMaintenanceConfigBlockPurchaseButNotWalletOrLogout() async throws {
        MaintenanceProtocol.reset()
        let network = URLSessionConfiguration.ephemeral; network.protocolClasses = [MaintenanceProtocol.self]
        let client = try LocalMockClient(config: GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080"), store: MaintenanceStore(), developmentKey: String(repeating: "x", count: 32), sessionConfiguration: network)
        _ = try await client.signIn(subject: "A")
        do { _ = try await client.purchase(productId: "coins_100", transactionId: UUID(), attemptId: UUID()); XCTFail("missing config") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "CONFIG_REQUIRED") }
        MaintenanceProtocol.setConfigured(true)
        do { _ = try await client.purchase(productId: "coins_100", transactionId: UUID(), attemptId: UUID()); XCTFail("maintenance") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "MAINTENANCE") }
        let wallet = try await client.wallet(); XCTAssertEqual(wallet.coinBalance, "0")
        try await client.signOut(); XCTAssertEqual(MaintenanceProtocol.count(), 0)
    }
    func testBridgeConfigFailsClosedAndReportsCache() async throws {
        MaintenanceProtocol.reset()
        let network = URLSessionConfiguration.ephemeral; network.protocolClasses = [MaintenanceProtocol.self]
        let handler = LocalMockBridgeHandler(tokenStore: { MaintenanceStore() }, sessionConfiguration: network)
        _ = try await handler.invoke("sdk.initialize", payload: ["appId": "demo", "providerMode": "LOCAL_MOCK",
            "backendBaseUrl": "http://127.0.0.1:8080", "requestTimeoutMs": 30000,
            "developmentKey": String(repeating: "x", count: 32), "mockSubject": "A"])
        do { _ = try await handler.invoke("config.get", payload: [:]); XCTFail("missing config") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "CONFIG_REQUIRED") }
        MaintenanceProtocol.setConfigured(true)
        let remote = try await handler.invoke("config.get", payload: [:]) as? [String: Any]
        XCTAssertEqual(remote?["source"] as? String, "NETWORK")
        XCTAssertEqual(remote?["maintenanceEnabled"] as? Bool, true)
        MaintenanceProtocol.setConfigured(false)
        let cache = try await handler.invoke("config.get", payload: [:]) as? [String: Any]
        XCTAssertEqual(cache?["source"] as? String, "CACHE")
        XCTAssertEqual(cache?["maintenanceEnabled"] as? Bool, true)
    }

    func testBridgeSyncReportsActualEmptyPendingAndWallet() async throws {
        MaintenanceProtocol.reset()
        let network = URLSessionConfiguration.ephemeral; network.protocolClasses = [MaintenanceProtocol.self]
        let sessions = MaintenanceStore(), pending = MaintenanceStore()
        let handler = LocalMockBridgeHandler(tokenStore: { sessions }, sessionConfiguration: network, pendingStore: { pending })
        _ = try await handler.invoke("sdk.initialize", payload: ["appId": "demo", "providerMode": "LOCAL_MOCK",
            "backendBaseUrl": "http://127.0.0.1:8080", "requestTimeoutMs": 30000,
            "developmentKey": String(repeating: "x", count: 32), "mockSubject": "A"])
        _ = try await handler.invoke("auth.signIn", payload: ["provider": "MOCK"])
        let result = try await handler.invoke("store.sync", payload: ["reason": "APP_RESUME"]) as? [String: Any]
        XCTAssertEqual(result?["examinedCount"] as? Int, 0)
        XCTAssertEqual((result?["entitlements"] as? [String: Any])?["coinBalance"] as? String, "0")
        do { _ = try await handler.invoke("store.sync", payload: ["reason": "OTHER"]); XCTFail("invalid reason") }
        catch let failure as SdkFailure { XCTAssertEqual(failure.code, "INVALID_ARGUMENT") }
        _ = try await handler.invoke("auth.signOut", payload: [:])
    }

}
