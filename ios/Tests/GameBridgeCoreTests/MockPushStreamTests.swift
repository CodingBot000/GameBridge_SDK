import Foundation
import XCTest
@testable import GameBridgeCore

#if canImport(Darwin)
private final class MockStreamProtocol: URLProtocol {
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        guard request.value(forHTTPHeaderField: "Authorization") == "Bearer synthetic-token", let url = request.url else { client?.urlProtocol(self, didFailWithError: URLError(.userAuthenticationRequired)); return }
        let response = HTTPURLResponse(url: url, statusCode: 200, httpVersion: "HTTP/1.1", headerFields: ["Content-Type":"text/event-stream"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data("event:push\ndata:{\"messageId\":\"one\",\"route\":\"home\"}\n\n".utf8))
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class MockPushStreamTests: XCTestCase {
    func testAuthenticatedMockStreamDecodesEvent() async {
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [MockStreamProtocol.self]
        let delivered = expectation(description: "push delivered")
        let stream = MockPushStream(baseURL: URL(string: "http://127.0.0.1:18080")!, installationId: UUID(), configuration: configuration,
                                    token: { "synthetic-token" }) { value in
            XCTAssertEqual(value.messageId, "one"); XCTAssertEqual(value.route, "home"); delivered.fulfill()
        }
        stream.start(); await fulfillment(of: [delivered], timeout: 5); stream.stop()
    }
}

private final class MockLifecycleStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
private final class MockLifecycleProtocol: URLProtocol {
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let user = "d2719c4e-d533-47ee-9efd-838791ea79c8"
        let path = request.url!.path
        let body: String
        if path == "/v1/dev/auth" { body = "{\"accessToken\":\"synthetic-access\",\"refreshToken\":\"synthetic-refresh\",\"expiresAt\":\"2099-01-01T00:00:00Z\",\"userId\":\"\(user)\"}" }
        else if path == "/v1/me" { body = "{\"userId\":\"\(user)\"}" }
        else if path.hasPrefix("/v1/devices/") { body = #"{"provider":"MOCK","registered":true,"tokenFingerprint":"abcdef123456"}"# }
        else if path == "/v1/dev/push/stream" {
            guard request.value(forHTTPHeaderField: "Authorization") == "Bearer synthetic-access" else { client?.urlProtocol(self, didFailWithError: URLError(.userAuthenticationRequired)); return }
            body = "event:push\ndata:{\"messageId\":\"one\",\"route\":\"home\"}\n\n"
        } else { body = "{}" }
        let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: "HTTP/1.1", headerFields: ["Content-Type": path.hasSuffix("/stream") ? "text/event-stream" : "application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(body.utf8)); client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class MockPushLifecycleTests: XCTestCase {
    func testRegisterStartsStreamAndLogoutClearsSession() async throws {
        let config = URLSessionConfiguration.ephemeral; config.protocolClasses = [MockLifecycleProtocol.self]
        let store = MockLifecycleStore()
        let handler = LocalMockBridgeHandler(tokenStore: { store }, sessionConfiguration: config)
        let delivered = expectation(description: "mock push delivered")
        await handler.setMockPushSinkFactory { { payload in XCTAssertEqual(payload.messageId, "one"); delivered.fulfill() } }
        _ = try await handler.invoke("sdk.initialize", payload: ["appId":"gamebridge-sample", "providerMode":"LOCAL_MOCK",
            "backendBaseUrl":"http://127.0.0.1:18080", "requestTimeoutMs":30000, "developmentKey":String(repeating:"x",count:32),
            "mockSubject":"A", "installationId": UUID().uuidString.lowercased()])
        _ = try await handler.invoke("auth.signIn", payload: ["provider":"MOCK"])
        _ = try await handler.invoke("push.register", payload: [:])
        await fulfillment(of: [delivered], timeout: 5)
        _ = try await handler.invoke("auth.signOut", payload: [:]); XCTAssertNil(store.value)
        _ = try await handler.invoke("sdk.shutdown", payload: [:])
    }
}
#endif
