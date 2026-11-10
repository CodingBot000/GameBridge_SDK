import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeUnityBridge

@MainActor private final class FakeAppleBridgeApi: AppleAuthBridgeApi {
    var signIns = 0
    var closed = false
    func signIn() async throws -> UserProfile { signIns += 1; return UserProfile(userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", displayName: nil, provider: "APPLE") }
    func restore() async throws -> UserProfile? { nil }
    func signOut() async throws {}
    func close() { closed = true }
}
final class AppleAuthBridgeTests: XCTestCase {
    @MainActor func testSandboxUsesAppleAndRejectsMock() async throws {
        let fake = FakeAppleBridgeApi()
        let handler = AppleAuthBridgeHandler { _ in fake }
        let initResult = try await handler.invoke("sdk.initialize", payload: ["providerMode": "PLATFORM_SANDBOX", "appId": "demo",
            "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000]) as? [String: Any]
        XCTAssertEqual(initResult?["mode"] as? String, "PLATFORM_SANDBOX")
        do { _ = try await handler.invoke("auth.signIn", payload: ["provider": "MOCK"]); XCTFail("must reject") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "UNSUPPORTED_PROVIDER") }
        let profile = try await handler.invoke("auth.signIn", payload: ["provider": "APPLE"]) as? [String: Any]
        XCTAssertEqual(profile?["provider"] as? String, "APPLE"); XCTAssertEqual(fake.signIns, 1)
        do { _ = try await handler.invoke("store.purchase", payload: [:]); XCTFail("unconnected store") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "UNSUPPORTED_OPERATION") }
        _ = try await handler.invoke("sdk.shutdown", payload: [:]); XCTAssertTrue(fake.closed)
    }
}
