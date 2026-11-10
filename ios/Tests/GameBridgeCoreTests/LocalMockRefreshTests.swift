import Foundation
import XCTest
@testable import GameBridgeCore

private final class RefreshStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
final class SessionProtocol: URLProtocol {
    enum Mode { case timeout, concurrent }
    static let guardLock = NSLock()
    static var mode: Mode = .timeout
    static var refreshCount = 0
    static var oldCount = 0
    static var logoutRefreshCount = 0
    static func reset(_ value: Mode) { guardLock.lock(); mode = value; refreshCount = 0; oldCount = 0; logoutRefreshCount = 0; guardLock.unlock() }
    static func counts() -> (Int, Int) { guardLock.lock(); defer { guardLock.unlock() }; return (refreshCount, oldCount) }
    static func logoutCount() -> Int { guardLock.lock(); defer { guardLock.unlock() }; return logoutRefreshCount }
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let path = request.url!.path
        if path == "/v1/dev/auth" {
            respond(200, #"{"accessToken":"test-old","refreshToken":"test-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}"#, delay: 0)
        } else if path == "/v1/auth/refresh" {
            Self.guardLock.lock(); Self.refreshCount += 1; let mode = Self.mode; Self.guardLock.unlock()
            if mode == .timeout { client?.urlProtocol(self, didFailWithError: URLError(.timedOut)); return }
            respond(200, #"{"accessToken":"test-new","refreshToken":"test-refresh-new","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}"#, delay: 0.02)
        } else if path == "/v1/auth/logout" {
            if request.value(forHTTPHeaderField: "Authorization") != nil { respond(401, "{}", delay: 0) }
            else {
                var captured = request.httpBody
                if captured == nil, let stream = request.httpBodyStream {
                    stream.open(); defer { stream.close() }
                    var data = Data(); var buffer = [UInt8](repeating: 0, count: 1024)
                    while true { let count = stream.read(&buffer, maxLength: buffer.count); if count <= 0 { break }; data.append(contentsOf: buffer.prefix(count)) }
                    captured = data
                }
                if let body = captured, String(decoding: body, as: UTF8.self).contains("test-refresh") {
                    Self.guardLock.lock(); Self.logoutRefreshCount += 1; Self.guardLock.unlock()
                }
                respond(200, #"{"signedOut":true}"#, delay: 0)
            }
        } else if path == "/v1/entitlements" || path == "/v1/me" {
            if request.value(forHTTPHeaderField: "Authorization") == "Bearer test-old" {
                Self.guardLock.lock(); Self.oldCount += 1; let count = Self.oldCount; let mode = Self.mode; Self.guardLock.unlock()
                respond(401, "{}", delay: mode == .concurrent && count > 1 ? 0.2 : 0.02)
            } else {
                let body = path == "/v1/me" ? #"{"userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}"# : #"{"userId":"d2719c4e-d533-47ee-9efd-838791ea79c8","premiumEnabled":false,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}"#
                respond(200, body, delay: 0)
            }
        } else { respond(404, "{}", delay: 0) }
    }
    private func respond(_ status: Int, _ body: String, delay: Double) {
        DispatchQueue.global().asyncAfter(deadline: .now() + delay) {
            let response = HTTPURLResponse(url: self.request.url!, statusCode: status, httpVersion: nil, headerFields: nil)!
            self.client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            self.client?.urlProtocol(self, didLoad: Data(body.utf8)); self.client?.urlProtocolDidFinishLoading(self)
        }
    }
    override func stopLoading() {}
}
final class LocalMockRefreshTests: XCTestCase {
    private func configuration() -> URLSessionConfiguration { let value = URLSessionConfiguration.ephemeral; value.protocolClasses = [SessionProtocol.self]; return value }
    func testLostRefreshPreservesTombstoneAndRejectsOtherApp() async throws {
        SessionProtocol.reset(.timeout)
        let store = RefreshStore(); let config = GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080")
        let client = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        _ = try await client.signIn(subject: "A"); let saved = store.value
        let wrong = try LocalMockClient(config: GameBridgeConfig(appId: "other", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080"), store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        do { _ = try await wrong.restore(); XCTFail("different app") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        do { try await wrong.signOut(); XCTFail("foreign session must not be deleted") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        let wrongServer = try LocalMockClient(config: GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:1"), store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        do { _ = try await wrongServer.restore(); XCTFail("different server") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(store.value, saved)
        do { _ = try await client.wallet(); XCTFail("refresh timeout") } catch let error as SdkFailure { XCTAssertEqual(error.code, "TIMEOUT") }
        XCTAssertEqual(store.value, "{\"state\":\"refresh_pending\"}")
        let restarted = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        do { _ = try await restarted.restore(); XCTFail("old token must not be replayed") } catch let error as SdkFailure { XCTAssertEqual(error.code, "SESSION_EXPIRED") }
        XCTAssertEqual(SessionProtocol.counts().0, 1)
        do { try await restarted.signOut(); XCTFail("unconfirmed remote revoke") }
        catch let error as SdkFailure { XCTAssertEqual(error.nativeCode, "REVOCATION_UNCONFIRMED") }
        XCTAssertNil(store.value)
    }
    func testPersistedLogoutFallsBackToRefresh() async throws {
        SessionProtocol.reset(.timeout)
        let store = RefreshStore(); let config = GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080")
        let original = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        _ = try await original.signIn(subject: "A")
        let restarted = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        try await restarted.signOut(); XCTAssertNil(store.value); XCTAssertEqual(SessionProtocol.logoutCount(), 1)
    }
    func testConcurrentRestoresShareRefresh() async throws {
        SessionProtocol.reset(.concurrent)
        let store = RefreshStore(); let config = GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080")
        let original = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        _ = try await original.signIn(subject: "A")
        let restored = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        async let first = restored.restore(); async let second = restored.restore()
        let (a, b) = try await (first, second)
        XCTAssertEqual(a?.userId, b?.userId); XCTAssertEqual(SessionProtocol.counts().0, 1); XCTAssertEqual(SessionProtocol.counts().1, 2)
    }
    func testLateUnauthorizedDoesNotRepeatRefresh() async throws {
        SessionProtocol.reset(.concurrent)
        let store = RefreshStore(); let config = GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080")
        let client = try LocalMockClient(config: config, store: store, developmentKey: String(repeating: "x", count: 32), sessionConfiguration: configuration())
        _ = try await client.signIn(subject: "A")
        async let first = client.wallet(); async let second = client.wallet()
        let (a, b) = try await (first, second)
        XCTAssertEqual(a.coinBalance, "100"); XCTAssertEqual(b.coinBalance, "100")
        XCTAssertEqual(SessionProtocol.counts().0, 1); XCTAssertEqual(SessionProtocol.counts().1, 2)
    }
}
