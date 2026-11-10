import Foundation
import XCTest
@testable import GameBridgeCore

private final class RecoveryMemoryStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
private final class RecoveryProtocol: URLProtocol {
    static let lock = NSLock()
    static var attempts: [(String, String)] = []
    static var subject = "A"
    static let userA = "d2719c4e-d533-47ee-9efd-838791ea79c8"
    static let userB = "a2719c4e-d533-47ee-9efd-838791ea79c8"
    static func reset() { lock.lock(); attempts = []; subject = "A"; lock.unlock() }
    static func setSubject(_ value: String) { lock.lock(); subject = value; lock.unlock() }
    static func snapshot() -> [(String, String)] { lock.lock(); defer { lock.unlock() }; return attempts }
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    private func bodyData() -> Data {
        if let body = request.httpBody { return body }
        guard let stream = request.httpBodyStream else { return Data() }
        stream.open(); defer { stream.close() }
        var data = Data(); var buffer = [UInt8](repeating: 0, count: 4096)
        while stream.hasBytesAvailable { let count = stream.read(&buffer, maxLength: buffer.count); if count <= 0 { break }; data.append(contentsOf: buffer.prefix(count)) }
        return data
    }
    override func startLoading() {
        var status = 200, body = "{}"
        switch request.url!.path {
        case "/v1/dev/auth":
            Self.lock.lock(); let subject = Self.subject; Self.lock.unlock()
            let user = subject == "A" ? Self.userA : Self.userB
            body = """
            {"accessToken":"access-\(subject)","refreshToken":"refresh-\(subject)","expiresAt":"2099-01-01T00:00:00Z","userId":"\(user)"}
            """
        case "/v1/config": body = #"{"revision":"1","maintenanceEnabled":false,"message":null,"expiresAt":"2099-01-01T00:00:00Z"}"#
        case "/v1/purchases/verify":
            let object = (try? JSONSerialization.jsonObject(with: bodyData())) as? [String: Any]
            Self.lock.lock(); Self.attempts.append((request.value(forHTTPHeaderField: "Idempotency-Key") ?? "", object?["proof"] as? String ?? "")); let number = Self.attempts.count; Self.lock.unlock()
            if number == 1 { status = 503; body = #"{"code":"NETWORK_UNAVAILABLE"}"# }
            else { body = """
            {"serverPurchaseId":"b2719c4e-d533-47ee-9efd-838791ea79c8","fulfillmentStatus":"ALREADY_GRANTED","finalizationStatus":"PENDING","entitlements":{"userId":"\(Self.userA)","premiumEnabled":false,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}}
            """ }
        case "/v1/auth/logout": break
        default: status = 404
        }
        let response = HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: nil)!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(body.utf8)); client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
final class LocalMockRecoveryTests: XCTestCase {
    func testLostResponseRecoversOnlyForOriginalUser() async throws {
        RecoveryProtocol.reset()
        let network = URLSessionConfiguration.ephemeral; network.protocolClasses = [RecoveryProtocol.self]
        let config = GameBridgeConfig(appId: "demo", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080")
        let sessions = RecoveryMemoryStore(), pending = RecoveryMemoryStore(), key = String(repeating: "x", count: 32)
        XCTAssertThrowsError(try LocalMockClient(config: config, store: sessions, developmentKey: key, sessionConfiguration: network, pendingStore: sessions))
        let original = try LocalMockClient(config: config, store: sessions, developmentKey: key, sessionConfiguration: network, pendingStore: pending)
        _ = try await original.signIn(subject: "A")
        do { _ = try await original.purchase(productId: "coins_100", transactionId: UUID(), attemptId: UUID()); XCTFail("lost response") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "NETWORK_UNAVAILABLE") }
        XCTAssertNotNil(pending.value); XCTAssertFalse(pending.value!.contains("access-A")); XCTAssertFalse(pending.value!.contains("mock:"))
        try await original.signOut()
        let other = try LocalMockClient(config: config, store: sessions, developmentKey: key, sessionConfiguration: network, pendingStore: pending)
        RecoveryProtocol.setSubject("B")
        let otherUser = try await other.signIn(subject: "B"); XCTAssertEqual(otherUser.userId, RecoveryProtocol.userB)
        let otherResult = try await other.recoverPending(); XCTAssertEqual(otherResult.examinedCount, 0); XCTAssertNotNil(pending.value)
        try await other.signOut()
        let restarted = try LocalMockClient(config: config, store: sessions, developmentKey: key, sessionConfiguration: network, pendingStore: pending)
        RecoveryProtocol.setSubject("A")
        let originalUser = try await restarted.signIn(subject: "A"); XCTAssertEqual(originalUser.userId, RecoveryProtocol.userA)
        let result = try await restarted.recoverPending(); XCTAssertEqual(result.examinedCount, 1); XCTAssertEqual(result.recoveredCount, 1)
        XCTAssertNil(pending.value)
        let attempts = RecoveryProtocol.snapshot(); XCTAssertEqual(attempts.count, 2)
        XCTAssertFalse(attempts[0].0.isEmpty); XCTAssertFalse(attempts[0].1.isEmpty)
        XCTAssertEqual(attempts[0].0, attempts[1].0); XCTAssertEqual(attempts[0].1, attempts[1].1)
        try await restarted.signOut()
    }
}
