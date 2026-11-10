import Foundation
import XCTest
@testable import GameBridgeCore

private final class StubProtocol: URLProtocol {
    static var responseCode = 200
    static var data = Data("{\"ok\":true}".utf8)
    static var failWithTimeout = false
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        if Self.failWithTimeout { client?.urlProtocol(self, didFailWithError: URLError(.timedOut)); return }
        let response = HTTPURLResponse(url: request.url!, statusCode: Self.responseCode, httpVersion: nil, headerFields: ["X-Request-Id": "request-test"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Self.data)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class BackendClientTests: XCTestCase {
    func testResponseErrorAndTimeoutMapping() async throws {
        let configuration = URLSessionConfiguration.ephemeral; configuration.protocolClasses = [StubProtocol.self]
        let client = try BackendClient(config: GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080"), sessionConfiguration: configuration)
        StubProtocol.responseCode = 200; StubProtocol.data = Data("{\"ok\":true}".utf8); StubProtocol.failWithTimeout = false
        let value = try await client.request(path: "/v1/ok", method: "GET"); XCTAssertEqual(value.requestId, "request-test"); XCTAssertFalse(String(describing: value).contains("ok"))
        StubProtocol.responseCode = 401
        do { _ = try await client.request(path: "/v1/me", method: "GET"); XCTFail("401") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        StubProtocol.responseCode = 200; StubProtocol.data = Data("bad".utf8)
        do { _ = try await client.request(path: "/v1/bad", method: "GET"); XCTFail("invalid JSON") } catch let error as SdkFailure { XCTAssertEqual(error.code, "BRIDGE_PROTOCOL_MISMATCH") }
        StubProtocol.failWithTimeout = true
        do { _ = try await client.request(path: "/v1/slow", method: "GET"); XCTFail("timeout") } catch let error as SdkFailure { XCTAssertEqual(error.code, "TIMEOUT") }
        StubProtocol.failWithTimeout = false
        do { _ = try await client.request(path: "/v1/../bad", method: "GET"); XCTFail("path") } catch let error as SdkFailure { XCTAssertEqual(error.code, "INVALID_ARGUMENT") }
    }
}
