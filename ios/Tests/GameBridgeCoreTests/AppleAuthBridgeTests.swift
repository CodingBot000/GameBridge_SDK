import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeUnityBridge

@MainActor private final class FakeAppleBridgeApi: AppleAuthBridgeApi {
    var signIns = 0
    var closed = false
    var purchaseResult = AppleBridgePurchase(status: .verificationPending, serverPurchaseId: nil, fulfillmentStatus: .notGranted, finalizationStatus: .pending)
    func signIn() async throws -> UserProfile { signIns += 1; return UserProfile(userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", displayName: nil, provider: "APPLE") }
    func restore() async throws -> UserProfile? { nil }
    func signOut() async throws {}
    func purchase(_ productId: String) async throws -> AppleBridgePurchase { purchaseResult }
    func close() { closed = true }
}
final class AppleAuthBridgeTests: XCTestCase {
    @MainActor func testSandboxUsesAppleAndRejectsMock() async throws {
        let fake = FakeAppleBridgeApi()
        let handler = AppleAuthBridgeHandler { _, _ in fake }
        let initResult = try await handler.invoke("sdk.initialize", payload: ["providerMode": "PLATFORM_SANDBOX", "appId": "demo",
            "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000]) as? [String: Any]
        XCTAssertEqual(initResult?["mode"] as? String, "PLATFORM_SANDBOX")
        do { _ = try await handler.invoke("auth.signIn", payload: ["provider": "MOCK"]); XCTFail("must reject") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "UNSUPPORTED_PROVIDER") }
        let profile = try await handler.invoke("auth.signIn", payload: ["provider": "APPLE"]) as? [String: Any]
        XCTAssertEqual(profile?["provider"] as? String, "APPLE"); XCTAssertEqual(fake.signIns, 1)
        do { _ = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]); XCTFail("missing store config") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "CONFIG_REQUIRED") }
        _ = try await handler.invoke("sdk.shutdown", payload: [:]); XCTAssertTrue(fake.closed)
    }
    @MainActor func testPurchaseStatesDoNotGrantBeforeVerification() async throws {
        let fake = FakeAppleBridgeApi(); let handler = AppleAuthBridgeHandler { _, _ in fake }
        let initialized = try await handler.invoke("sdk.initialize", payload: ["providerMode": "PLATFORM_SANDBOX", "appId": "demo",
            "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000,
            "storeProductIds": ["coins_100": "test_coins", "premium_unlock": "test_premium"]]) as? [String: Any]
        let caps = initialized?["capabilities"] as? [String: [String: Any]]
        XCTAssertEqual(caps?["store"]?["configured"] as? Bool, true)
        let pending = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]) as? [String: Any]
        XCTAssertEqual(pending?["status"] as? String, "VERIFICATION_PENDING")
        XCTAssertEqual(pending?["fulfillmentStatus"] as? String, "NOT_GRANTED")
        XCTAssertTrue(pending?["serverPurchaseId"] is NSNull)
        let id = UUID()
        fake.purchaseResult = AppleBridgePurchase(status: .purchased, serverPurchaseId: id, fulfillmentStatus: .alreadyGranted, finalizationStatus: .finalized)
        let verified = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]) as? [String: Any]
        XCTAssertEqual(verified?["serverPurchaseId"] as? String, id.uuidString.lowercased())
        XCTAssertEqual(verified?["fulfillmentStatus"] as? String, "ALREADY_GRANTED")
        fake.purchaseResult = AppleBridgePurchase(status: .purchased, serverPurchaseId: nil, fulfillmentStatus: .granted, finalizationStatus: .finalized)
        do { _ = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]); XCTFail("missing grant ID") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "BRIDGE_PROTOCOL_MISMATCH") }
    }

}
