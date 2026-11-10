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
#endif
