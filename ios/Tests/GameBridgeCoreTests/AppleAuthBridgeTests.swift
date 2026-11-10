import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeUnityBridge

@MainActor private final class FakeAppleBridgeApi: AppleAuthBridgeApi {
    var signIns = 0
    var closed = false
    var restoreRequests: [Bool] = []
    var receivedToken: String?
    var pushUnregistered = false
    var purchaseResult = AppleBridgePurchase(status: .verificationPending, serverPurchaseId: nil, fulfillmentStatus: .notGranted, finalizationStatus: .pending)
    func signIn() async throws -> UserProfile { signIns += 1; return UserProfile(userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", displayName: nil, provider: "APPLE") }
    func restore() async throws -> UserProfile? { nil }
    func signOut() async throws {}
    func purchase(_ productId: String) async throws -> AppleBridgePurchase { purchaseResult }
    func recover(userInitiated: Bool) async throws -> AppleBridgeRecoveryCounts {
        restoreRequests.append(userInitiated); return AppleBridgeRecoveryCounts(examined: 3, recovered: 1, deferred: 1, failed: 1)
    }
    func entitlements() async throws -> EntitlementSnapshot {
        try JSONDecoder().decode(EntitlementSnapshot.self, from: Data(#"{"userId":"d2719c4e-d533-47ee-9efd-838791ea79c8","premiumEnabled":false,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}"#.utf8))
    }
    func registerPush(tokenHex: String) async throws -> String { receivedToken = tokenHex; return "abcdef123456" }
    func unregisterPush() async throws { pushUnregistered = true }
    func close() { closed = true }
}
final class AppleAuthBridgeTests: XCTestCase {
    @MainActor func testSandboxUsesAppleAndRejectsMock() async throws {
        let fake = FakeAppleBridgeApi()
        let handler = AppleAuthBridgeHandler { _, _, _ in fake }
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
        let fake = FakeAppleBridgeApi(); let handler = AppleAuthBridgeHandler { _, _, _ in fake }
        let initialized = try await handler.invoke("sdk.initialize", payload: ["providerMode": "PLATFORM_SANDBOX", "appId": "demo",
            "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000,
            "storeProductIds": ["coins_100": "test_coins", "premium_unlock": "test_premium"]]) as? [String: Any]
        let caps = initialized?["capabilities"] as? [String: [String: Any]]
        XCTAssertEqual(caps?["store"]?["configured"] as? Bool, true)
        let pending = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]) as? [String: Any]
        XCTAssertEqual(pending?["status"] as? String, "VERIFICATION_PENDING")
        XCTAssertEqual(pending?["fulfillmentStatus"] as? String, "NOT_GRANTED")
        XCTAssertTrue(pending?["serverPurchaseId"] is NSNull)
        let resume = try await handler.invoke("store.sync", payload: ["reason": "APP_RESUME"]) as? [String: Any]
        XCTAssertEqual(resume?["examinedCount"] as? Int, 3)
        XCTAssertEqual((resume?["entitlements"] as? [String: Any])?["coinBalance"] as? String, "100")
        _ = try await handler.invoke("store.sync", payload: ["reason": "USER_RESTORE"])
        XCTAssertEqual(fake.restoreRequests, [false, true])
        do { _ = try await handler.invoke("store.sync", payload: ["reason": "OTHER"]); XCTFail("invalid reason") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "INVALID_ARGUMENT") }
        let id = UUID()
        fake.purchaseResult = AppleBridgePurchase(status: .purchased, serverPurchaseId: id, fulfillmentStatus: .alreadyGranted, finalizationStatus: .finalized)
        let verified = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]) as? [String: Any]
        XCTAssertEqual(verified?["serverPurchaseId"] as? String, id.uuidString.lowercased())
        XCTAssertEqual(verified?["fulfillmentStatus"] as? String, "ALREADY_GRANTED")
        fake.purchaseResult = AppleBridgePurchase(status: .purchased, serverPurchaseId: nil, fulfillmentStatus: .granted, finalizationStatus: .finalized)
        do { _ = try await handler.invoke("store.purchase", payload: ["productId": "coins_100"]); XCTFail("missing grant ID") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "BRIDGE_PROTOCOL_MISMATCH") }
    }

    @MainActor func testPushTokenRegistrationIsScopedAndRedacted() async throws {
        let fake = FakeAppleBridgeApi(); let id = UUID(); var factoryId: UUID?
        let handler = AppleAuthBridgeHandler { _, _, installation in factoryId = installation; return fake }
        _ = try await handler.invoke("sdk.initialize", payload: ["providerMode": "PLATFORM_SANDBOX", "appId": "demo",
            "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000, "installationId": id.uuidString.lowercased()])
        XCTAssertEqual(factoryId, id)
        do { _ = try await handler.invoke("host.pushToken", payload: ["provider": "APNS", "token": "not-hex"]); XCTFail("invalid token") }
        catch let failure as SdkFailure { XCTAssertEqual(failure.code, "INVALID_ARGUMENT") }
        let result = try await handler.invoke("host.pushToken", payload: ["provider": "APNS", "token": "010203"]) as? [String: Any]
        XCTAssertEqual(fake.receivedToken, "010203"); XCTAssertEqual(result?["tokenFingerprint"] as? String, "abcdef123456")
        XCTAssertFalse(String(describing: result).contains("010203"))
        _ = try await handler.invoke("push.unregister", payload: [:]); XCTAssertTrue(fake.pushUnregistered)
    }

}
