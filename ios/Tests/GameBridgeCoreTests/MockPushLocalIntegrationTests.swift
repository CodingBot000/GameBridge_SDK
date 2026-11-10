import Foundation
import XCTest
@testable import GameBridgeCore

#if canImport(Darwin)
private final class MockPushE2EStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
final class MockPushLocalIntegrationTests: XCTestCase {
    func testLocalBackendDeliversPushToSwiftHandler() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["GAMEBRIDGE_RUN_MOCK_PUSH_E2E"] == "true" else { throw XCTSkip("explicit local mock E2E opt-in required") }
        let base = try XCTUnwrap(env["GAMEBRIDGE_PUSH_E2E_BASE_URL"]); guard base.hasPrefix("http://127.0.0.1:") else { throw SdkFailure("CONFIG_REQUIRED") }
        let key = try XCTUnwrap(env["GAMEBRIDGE_PUSH_E2E_AUTH_KEY"]), admin = try XCTUnwrap(env["GAMEBRIDGE_PUSH_E2E_ADMIN_KEY"])
        let installation = try XCTUnwrap(env["GAMEBRIDGE_PUSH_E2E_INSTALLATION"]); XCTAssertNotNil(UUID(uuidString: installation))
        func post(_ path: String, _ body: [String: Any], _ headers: [String: String]) async throws -> [String: Any] {
            var request = URLRequest(url: URL(string: base + path)!); request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type"); headers.forEach { request.setValue($0.value, forHTTPHeaderField: $0.key) }
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            let (data, response) = try await URLSession.shared.data(for: request)
            XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 200)
            return try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        }
        let senderResponse = try await post("/v1/dev/auth", ["subject":"A"], ["X-Development-Key":key])
        let sender = try XCTUnwrap(senderResponse["accessToken"] as? String)
        let store = MockPushE2EStore(); let handler = LocalMockBridgeHandler(tokenStore: { store })
        let delivered = expectation(description: "local backend delivered push"); delivered.assertForOverFulfill = false
        await handler.setMockPushSinkFactory { { payload in if payload.route == "store" { delivered.fulfill() } } }
        _ = try await handler.invoke("sdk.initialize", payload: ["appId":"gamebridge-sample", "providerMode":"LOCAL_MOCK", "backendBaseUrl":base,
            "requestTimeoutMs":5000, "developmentKey":key, "mockSubject":"A", "installationId":installation])
        _ = try await handler.invoke("auth.signIn", payload: ["provider":"MOCK"]); _ = try await handler.invoke("push.register", payload: [:])
        let senderTask = Task {
            for attempt in 1...4 {
                try await Task.sleep(nanoseconds: 500_000_000)
                _ = try await post("/v1/dev/push/send", ["installationId":installation, "messageId":"swift-e2e-\(attempt)", "route":"store", "title":"test", "body":"test"],
                                   ["Authorization":"Bearer \(sender)", "X-Admin-Key":admin])
            }
        }
        await fulfillment(of: [delivered], timeout: 6); senderTask.cancel(); _ = try? await senderTask.value
        _ = try await handler.invoke("auth.signOut", payload: [:]); XCTAssertNil(store.value)
        _ = try await handler.invoke("sdk.shutdown", payload: [:])
    }
}
#endif
