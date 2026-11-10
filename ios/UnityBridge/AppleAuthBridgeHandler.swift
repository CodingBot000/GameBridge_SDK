import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
import GameBridgeApple
#endif
#if canImport(UIKit) && canImport(AuthenticationServices)
import UIKit
import AuthenticationServices
#endif

@MainActor protocol AppleAuthBridgeApi {
    func signIn() async throws -> UserProfile
    func restore() async throws -> UserProfile?
    func signOut() async throws
    func products() async throws -> [StoreProduct]
    func purchase(_ productId: String) async throws -> AppleBridgePurchase
    func entitlements() async throws -> EntitlementSnapshot
    func recover(userInitiated: Bool) async throws -> AppleBridgeRecoveryCounts
    func close()
}
struct AppleBridgeRecoveryCounts {
    let examined: Int, recovered: Int, deferred: Int, failed: Int
}
struct AppleBridgePurchase {
    let status: PurchaseStatus
    let serverPurchaseId: UUID?
    let fulfillmentStatus: FulfillmentStatus
    let finalizationStatus: FinalizationStatus
}
extension AppleAuthBridgeApi {
    func products() async throws -> [StoreProduct] { throw SdkFailure("CONFIG_REQUIRED") }
    func purchase(_ productId: String) async throws -> AppleBridgePurchase { throw SdkFailure("CONFIG_REQUIRED") }
    func entitlements() async throws -> EntitlementSnapshot { throw SdkFailure("CONFIG_REQUIRED") }
    func recover(userInitiated: Bool) async throws -> AppleBridgeRecoveryCounts { throw SdkFailure("CONFIG_REQUIRED") }
}

@MainActor final class AppleAuthBridgeHandler {
    private let factory: (GameBridgeConfig, [String: String]?) throws -> AppleAuthBridgeApi
    private var provider: AppleAuthBridgeApi?
    private var config: GameBridgeConfig?
    private var productIds: [String: String]?
    init(factory: @escaping (GameBridgeConfig, [String: String]?) throws -> AppleAuthBridgeApi) { self.factory = factory }
    func invoke(_ operation: String, payload: [String: Any]) async throws -> Any {
        if operation == "sdk.initialize" { return try initialize(payload) }
        if operation == "sdk.shutdown" { provider?.close(); provider = nil; config = nil; productIds = nil; return [String: Any]() }
        guard let provider else { throw SdkFailure("NOT_INITIALIZED") }
        switch operation {
        case "auth.signIn":
            guard payload["provider"] as? String == "APPLE" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
            return try object(try await provider.signIn())
        case "auth.restore":
            let user = try await provider.restore()
            return ["signedIn": user != nil, "user": try user.map { try object($0) } ?? NSNull(),
                    "expiresAt": NSNull(), "sessionRestored": user != nil] as [String: Any]
        case "auth.signOut": try await provider.signOut(); return [String: Any]()
        case "store.products":
            guard productIds != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            return try object(try await provider.products())
        case "store.entitlements":
            guard productIds != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            return try object(try await provider.entitlements())
        case "store.sync":
            guard productIds != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            guard let reason = payload["reason"] as? String, ["APP_RESUME", "USER_RESTORE"].contains(reason) else { throw SdkFailure("INVALID_ARGUMENT") }
            let counts = try await provider.recover(userInitiated: reason == "USER_RESTORE")
            let wallet = try await provider.entitlements()
            return ["examinedCount": counts.examined, "recoveredCount": counts.recovered, "deferredCount": counts.deferred,
                    "failureCount": counts.failed, "entitlements": try object(wallet)] as [String: Any]
        case "store.purchase":
            guard productIds != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            guard let productId = payload["productId"] as? String, !productId.isEmpty else { throw SdkFailure("INVALID_ARGUMENT") }
            let result = try await provider.purchase(productId)
            if result.status == .purchased && (result.serverPurchaseId == nil || ![FulfillmentStatus.granted, .alreadyGranted].contains(result.fulfillmentStatus)) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            if result.status != .purchased && (result.serverPurchaseId != nil || result.fulfillmentStatus != .notGranted) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return ["attemptId": UUID().uuidString.lowercased(), "productId": productId, "status": result.status.rawValue,
                    "serverPurchaseId": result.serverPurchaseId?.uuidString.lowercased() as Any? ?? NSNull(),
                    "fulfillmentStatus": result.fulfillmentStatus.rawValue, "finalizationStatus": result.finalizationStatus.rawValue,
                    "error": NSNull()] as [String: Any]
        default: throw SdkFailure("UNSUPPORTED_OPERATION")
        }
    }
    private func initialize(_ payload: [String: Any]) throws -> [String: Any] {
        guard payload["providerMode"] as? String == "PLATFORM_SANDBOX", payload["developmentKey"] == nil else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard let appId = payload["appId"] as? String, let base = payload["backendBaseUrl"] as? String,
              let timeout = payload["requestTimeoutMs"] as? Int else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = GameBridgeConfig(appId: appId, mode: .platformSandbox, backendBaseURL: base, requestTimeoutMs: timeout)
        do { try next.validate() } catch { throw SdkFailure("CONFIG_REQUIRED") }
        let mapping: [String: String]?
        if let raw = payload["storeProductIds"] {
            guard let value = raw as? [String: String], Set(value.keys) == Set(["coins_100", "premium_unlock"]),
                  let coins = value["coins_100"], let premium = value["premium_unlock"],
                  !coins.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  !premium.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, coins != premium else { throw SdkFailure("CONFIG_REQUIRED") }
            mapping = value
        } else { mapping = nil }
        if provider != nil && (config != next || productIds != mapping) { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        if provider == nil { provider = try factory(next, mapping); config = next; productIds = mapping }
        var capabilities: [String: Any] = [:]
        for name in ["auth", "store", "push", "config"] {
            let supported = name == "auth" || name == "store"
            let configured = name == "auth" || (name == "store" && mapping != nil)
            capabilities[name] = ["supported": supported, "configured": configured, "mode": "PLATFORM_SANDBOX",
                                  "reason": configured ? NSNull() as Any : (supported ? "Store product IDs required" : "Bridge operation is not connected")]
        }
        return ["state": "READY", "mode": "PLATFORM_SANDBOX", "provider": "APPLE", "capabilities": capabilities]
    }
    private func object<T: Encodable>(_ value: T) throws -> Any { try JSONSerialization.jsonObject(with: JSONEncoder().encode(value)) }
}

#if canImport(UIKit) && canImport(AuthenticationServices)
@MainActor private final class AppleSystemAuthBridgeApi: AppleAuthBridgeApi {
    let provider: AppleAuthProvider
    private let config: GameBridgeConfig
    private let productIds: [String: String]?
    private var store: AppleStore?
    private let makeEmitter: () -> (AppleStorePurchaseResult) -> Void
    init(config: GameBridgeConfig, productIds: [String: String]?, makeEmitter: @escaping () -> (AppleStorePurchaseResult) -> Void) throws {
        self.config = config; self.productIds = productIds; self.makeEmitter = makeEmitter
        guard let window = Self.window() else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "HOST_WINDOW") }
        provider = try AppleAuthProvider.create(config: config, store: KeychainTokenStore(service: "com.gamebridge.sdk.unity.apple"), window: window)
    }
    private static func window() -> UIWindow? {
        UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
            .filter { $0.activationState == .foregroundActive }.flatMap(\.windows).first(where: \.isKeyWindow)
    }
    private func activeStore() async throws -> AppleStore {
        if let store { return store }
        guard let productIds else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = try AppleStore(auth: provider, config: config, productIds: productIds)
        next.setPurchaseUpdatedHandler(makeEmitter())
        try await next.start(); store = next
        return next
    }
    private func dropStore() { store?.stop(); store = nil }
    func signIn() async throws -> UserProfile {
        dropStore()
        guard let window = Self.window() else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "HOST_WINDOW") }
        provider.attachHost(window); return try await provider.signIn()
    }
    func restore() async throws -> UserProfile? { try await provider.restore() }
    func signOut() async throws { dropStore(); try await provider.signOut() }
    func products() async throws -> [StoreProduct] { try await activeStore().products() }
    func entitlements() async throws -> EntitlementSnapshot { try await activeStore().entitlements() }
    func recover(userInitiated: Bool) async throws -> AppleBridgeRecoveryCounts {
        let counts = try await activeStore().recoverDetailed(userInitiated: userInitiated)
        return AppleBridgeRecoveryCounts(examined: counts.examinedCount, recovered: counts.recoveredCount,
                                         deferred: counts.deferredCount, failed: counts.failureCount)
    }
    func purchase(_ productId: String) async throws -> AppleBridgePurchase {
        let result = try await activeStore().purchase(productId: productId)
        switch result.status {
        case .purchased:
            guard let id = result.serverPurchaseId, let fulfillment = result.fulfillmentStatus.flatMap(FulfillmentStatus.init(rawValue:)),
                  [.granted, .alreadyGranted].contains(fulfillment) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return AppleBridgePurchase(status: .purchased, serverPurchaseId: id, fulfillmentStatus: fulfillment, finalizationStatus: .finalized)
        case .pending: return AppleBridgePurchase(status: .pending, serverPurchaseId: nil, fulfillmentStatus: .notGranted, finalizationStatus: .pending)
        case .verificationPending: return AppleBridgePurchase(status: .verificationPending, serverPurchaseId: nil, fulfillmentStatus: .notGranted, finalizationStatus: .pending)
        case .cancelled: return AppleBridgePurchase(status: .canceled, serverPurchaseId: nil, fulfillmentStatus: .notGranted, finalizationStatus: .notRequired)
        }
    }
    func close() { dropStore(); provider.detachHost() }
}
@MainActor func makeAppleAuthBridgeHandler(makeEmitter: @escaping () -> (AppleStorePurchaseResult) -> Void) -> AppleAuthBridgeHandler {
    AppleAuthBridgeHandler { try AppleSystemAuthBridgeApi(config: $0, productIds: $1, makeEmitter: makeEmitter) }
}
#endif
