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
    func registerPush(tokenHex: String) async throws -> String
    func unregisterPush() async throws
    func serviceSettings() async throws -> (ServiceSettings, ConfigurationSource)
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
    func registerPush(tokenHex: String) async throws -> String { throw SdkFailure("CONFIG_REQUIRED") }
    func unregisterPush() async throws { throw SdkFailure("CONFIG_REQUIRED") }
    func serviceSettings() async throws -> (ServiceSettings, ConfigurationSource) { throw SdkFailure("CONFIG_REQUIRED") }
}

@MainActor final class AppleAuthBridgeHandler {
    private let factory: (GameBridgeConfig, [String: String]?, UUID?) throws -> AppleAuthBridgeApi
    private var provider: AppleAuthBridgeApi?
    private var config: GameBridgeConfig?
    private var productIds: [String: String]?
    private var installationId: UUID?
    init(factory: @escaping (GameBridgeConfig, [String: String]?, UUID?) throws -> AppleAuthBridgeApi) { self.factory = factory }
    func invoke(_ operation: String, payload: [String: Any]) async throws -> Any {
        if operation == "sdk.initialize" { return try initialize(payload) }
        if operation == "sdk.shutdown" { provider?.close(); provider = nil; config = nil; productIds = nil; installationId = nil; return [String: Any]() }
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
        case "config.get":
            let (settings, source) = try await provider.serviceSettings()
            let formatter = ISO8601DateFormatter(); formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            return ["revision": settings.revision, "maintenanceEnabled": settings.maintenanceEnabled,
                    "message": settings.message as Any? ?? NSNull(), "expiresAt": formatter.string(from: settings.expiresAt),
                    "source": source == .remote ? "NETWORK" : "CACHE"] as [String: Any]
        case "host.pushToken":
            guard installationId != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            guard payload["provider"] as? String == "APNS", let token = payload["token"] as? String, !token.isEmpty,
                  token.count.isMultiple(of: 2), token.range(of: "^[0-9a-fA-F]+$", options: .regularExpression) != nil else { throw SdkFailure("INVALID_ARGUMENT") }
            let fingerprint = try await provider.registerPush(tokenHex: token)
            guard fingerprint.range(of: "^[0-9a-f]{12}$", options: .regularExpression) != nil else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return ["registered": true, "tokenFingerprint": fingerprint] as [String: Any]
        case "push.unregister":
            guard installationId != nil else { throw SdkFailure("CONFIG_REQUIRED") }
            try await provider.unregisterPush(); return ["registered": false]
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
        let installation: UUID?
        if let raw = payload["installationId"] {
            guard let text = raw as? String, let parsed = UUID(uuidString: text), parsed.uuidString.lowercased() == text.lowercased() else { throw SdkFailure("CONFIG_REQUIRED") }
            installation = parsed
        } else { installation = nil }
        if provider != nil && (config != next || productIds != mapping || installationId != installation) { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        if provider == nil { provider = try factory(next, mapping, installation); config = next; productIds = mapping; installationId = installation }
        var capabilities: [String: Any] = [:]
        for name in ["auth", "store", "push", "config"] {
            let supported = name == "auth" || name == "store" || name == "push" || name == "config"
            let configured = name == "auth" || name == "config" || (name == "store" && mapping != nil) || (name == "push" && installation != nil)
            capabilities[name] = ["supported": supported, "configured": configured, "mode": "PLATFORM_SANDBOX",
                                  "reason": configured ? NSNull() as Any : (name == "store" ? "coinsStoreProductId, premiumStoreProductId required" : name == "push" ? "installationId required" : "Bridge operation is not connected")]
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
    private let push: ApplePushClient?
    private let serviceSession: AppleStoreSession
    private let makeEmitter: () -> (AppleStorePurchaseResult) -> Void
    init(config: GameBridgeConfig, productIds: [String: String]?, installationId: UUID?, makeEmitter: @escaping () -> (AppleStorePurchaseResult) -> Void) throws {
        self.config = config; self.productIds = productIds; self.makeEmitter = makeEmitter
        guard let window = Self.window() else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "HOST_WINDOW") }
        let provider = try AppleAuthProvider.create(config: config, store: KeychainTokenStore(service: "com.gamebridge.sdk.unity.apple"), window: window)
        self.provider = provider
        self.serviceSession = try AppleStoreSession(auth: provider, config: config)
        self.push = try installationId.map { try ApplePushClient(auth: provider, config: config, installationId: $0) }
    }
    private static func window() -> UIWindow? {
        UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
            .filter { $0.activationState == .foregroundActive }.flatMap(\.windows).first(where: \.isKeyWindow)
    }
    private func activeStore() async throws -> AppleStore {
        if let store { return store }
        guard let productIds else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = try serviceSession.createStore(productIds: productIds)
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
    func registerPush(tokenHex: String) async throws -> String {
        guard let push else { throw SdkFailure("CONFIG_REQUIRED") }
        var bytes = Data(); var index = tokenHex.startIndex
        while index < tokenHex.endIndex {
            let end = tokenHex.index(index, offsetBy: 2)
            guard let byte = UInt8(tokenHex[index..<end], radix: 16) else { throw SdkFailure("INVALID_ARGUMENT") }
            bytes.append(byte); index = end
        }
        return try await push.register(deviceToken: bytes)
    }
    func unregisterPush() async throws { guard let push else { throw SdkFailure("CONFIG_REQUIRED") }; try await push.unregister() }
    func serviceSettings() async throws -> (ServiceSettings, ConfigurationSource) {
        let value = try await serviceSession.serviceSettings(); return (value.settings, value.source)
    }
    func close() { dropStore(); provider.detachHost() }
}
@MainActor func makeAppleAuthBridgeHandler(makeEmitter: @escaping () -> (AppleStorePurchaseResult) -> Void) -> AppleAuthBridgeHandler {
    AppleAuthBridgeHandler { try AppleSystemAuthBridgeApi(config: $0, productIds: $1, installationId: $2, makeEmitter: makeEmitter) }
}
#endif
