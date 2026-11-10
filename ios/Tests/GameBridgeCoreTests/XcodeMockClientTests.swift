import Foundation
import XCTest
@testable import GameBridgeCore

private final class XcodeStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
private final class XcodeProtocol: URLProtocol {
    private let xcode = "d2719c4e-d533-47ee-9efd-838791ea79c8"
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let path = request.url!.path
        let body: String
        if path == "/v1/dev/auth" { body = #"{"accessToken":"access","refreshToken":"refresh","expiresAt":"2099-01-01T00:00:00Z","userId":"98b56d7a-5669-4fb0-b70e-1c313f72fd99"}"# }
        else if path.hasPrefix("/v1/dev/xcode-storekit/") {
            guard request.value(forHTTPHeaderField: "X-Development-Key") == String(repeating:"x", count:32), request.value(forHTTPHeaderField: "Authorization") == "Bearer access" else { client?.urlProtocol(self, didFailWithError: URLError(.userAuthenticationRequired)); return }
            if path.hasSuffix("/account") { body = "{\"userId\":\"\(xcode)\",\"bindingId\":\"\(xcode)\"}" }
            else if path.hasSuffix("/grant") { body = "{\"userId\":\"\(xcode)\",\"bindingId\":\"\(xcode)\",\"productId\":\"coins_100\",\"transactionKey\":\"7\",\"serverPurchaseId\":\"\(xcode)\",\"fulfillmentStatus\":\"GRANTED\"}" }
            else { body = "{\"userId\":\"\(xcode)\",\"premiumEnabled\":false,\"coinBalance\":\"100\",\"revision\":\"1\",\"updatedAt\":\"2026-01-01T00:00:00Z\"}" }
        } else { body = "{}" }
        let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: ["Content-Type":"application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(body.utf8)); client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class XcodeMockClientTests: XCTestCase {
    func testLocalAccountGrantAndWalletUseExplicitDevelopmentKey() async throws {
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [XcodeProtocol.self]
        let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:18080")
        let client = try LocalMockClient(config: config, store: XcodeStore(), developmentKey: String(repeating:"x", count:32), sessionConfiguration: configuration)
        _ = try await client.signIn(subject: "A")
        let account = try await client.xcodeAccount()
        let grant = try await client.xcodeGrant(productId: "coins_100", transactionId: 7, account: account)
        XCTAssertEqual(grant.transactionKey, "7"); XCTAssertEqual(grant.fulfillmentStatus, "GRANTED")
        let wallet = try await client.xcodeWallet(account: account); XCTAssertEqual(wallet.coinBalance, "100")
    }
}
