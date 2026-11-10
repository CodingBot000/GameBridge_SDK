import XCTest
import Foundation
import StoreKit
import StoreKitTest
import GameBridgeCore
import GameBridgeApple

private final class StoreKitTestMemoryStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
private final class StoreKitFakeBackend: URLProtocol {
    static let lock = NSLock()
    static var paths: [String] = []
    static var grantBodyValid = false
    static var grants: [String: String] = [:]
    static func snapshot() -> String { lock.lock(); defer { lock.unlock() }; return "paths=\(paths), bodyValid=\(grantBodyValid)" }
    private let account = "d2719c4e-d533-47ee-9efd-838791ea79c8"
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let path = request.url!.path; let body: String
        Self.lock.lock(); Self.paths.append(path); Self.lock.unlock()
        switch path {
        case "/v1/dev/auth": body = #"{"accessToken":"fake-access","refreshToken":"fake-refresh","expiresAt":"2099-01-01T00:00:00Z","userId":"98b56d7a-5669-4fb0-b70e-1c313f72fd99"}"#
        case "/v1/config": body = #"{"revision":"1","maintenanceEnabled":false,"message":null,"expiresAt":"2099-01-01T00:00:00Z"}"#
        case "/v1/dev/xcode-storekit/account": body = "{\"userId\":\"\(account)\",\"bindingId\":\"\(account)\"}"
        case "/v1/dev/xcode-storekit/grant":
            var raw = request.httpBody
            if raw == nil, let stream = request.httpBodyStream {
                stream.open(); defer { stream.close() }; var data = Data(); var buffer = [UInt8](repeating: 0, count: 1024)
                while true { let count = stream.read(&buffer, maxLength: buffer.count); if count <= 0 { break }; data.append(contentsOf: buffer.prefix(count)) }
                raw = data
            }
            guard let raw, let values = (try? JSONSerialization.jsonObject(with: raw)) as? [String: Any],
                  let transaction = values["transactionId"] as? String, let product = values["productId"] as? String,
                  values["bindingId"] as? String == account else { client?.urlProtocol(self, didFailWithError: URLError(.cannotParseResponse)); return }
            guard transaction.range(of: "^[0-9a-f]{64}$", options: .regularExpression) != nil else { client?.urlProtocol(self, didFailWithError: URLError(.cannotParseResponse)); return }
            Self.lock.lock(); Self.grantBodyValid = true
            let existing = Self.grants[transaction]; let purchaseId = existing ?? UUID().uuidString.lowercased()
            Self.grants[transaction] = purchaseId; Self.lock.unlock()
            body = "{\"userId\":\"\(account)\",\"bindingId\":\"\(account)\",\"productId\":\"\(product)\",\"transactionKey\":\"\(transaction)\",\"serverPurchaseId\":\"\(purchaseId)\",\"fulfillmentStatus\":\"\(existing == nil ? "GRANTED" : "ALREADY_GRANTED")\"}"
        default: body = "{}"
        }
        let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: ["Content-Type":"application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(body.utf8)); client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class XcodeStoreKitPurchaseTests: XCTestCase {
    @MainActor func testLocalVerifiedPurchaseReceivesFakeGrantAndFinishes() async throws {
        let testSession = try SKTestSession(configurationFileNamed: "GameBridge"); testSession.disableDialogs = true
        let config = URLSessionConfiguration.ephemeral; config.protocolClasses = [StoreKitFakeBackend.self]
        let client = try LocalMockClient(config: GameBridgeConfig(appId:"gamebridge-sample", mode:.localMock, backendBaseURL:"http://127.0.0.1:18080"),
                                         store: StoreKitTestMemoryStore(), developmentKey:String(repeating:"x", count:32), sessionConfiguration:config)
        _ = try await client.signIn(subject:"A")
        let store = try await XcodeStoreKitSession(client:client); defer { store.stop() }
        try await store.start()
        let purchase = try await store.purchase("coins_100")
        var unfinished: [String] = []
        for await result in Transaction.unfinished {
            if case .verified(let value) = result { unfinished.append("id=\(value.id), env=\(value.environment), token=\(value.appAccountToken != nil)") }
        }
        XCTAssertEqual(purchase.status, .purchased, StoreKitFakeBackend.snapshot() + " unfinished=\(unfinished)"); XCTAssertEqual(purchase.fulfillmentStatus, "GRANTED"); XCTAssertNotNil(purchase.serverPurchaseId)
        let second = try await store.purchase("coins_100")
        XCTAssertEqual(second.status, .purchased); XCTAssertNotNil(second.serverPurchaseId)
        XCTAssertNotEqual(purchase.serverPurchaseId, second.serverPurchaseId, "two local purchases must have distinct stable keys")
        let recovery = try await store.recover(userInitiated:false)
        XCTAssertEqual(recovery.examinedCount, 0)
    }
}
