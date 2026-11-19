import Foundation
import GameBridgeCore

public enum FakeScenario { case success, canceled, pending, networkFailure }
public struct FakeWallet: Equatable {
    public let coinBalance: Int64
    public let premiumEnabled: Bool
}
public struct FakePushEvent: Equatable { public let messageId: String; public let route: String }
public struct FakePurchase {
    public let status: String
    public let transactionId: String
    public let granted: Bool
    public let wallet: FakeWallet
}
/// In-memory test double, never a server or a real-store fulfillment provider.
public actor OfflineFake: SdkProvider {
    private var ready = false
    private var signedIn = false
    private var coins: Int64 = 0
    private var premium = false
    private var granted: [String: String] = [:]
    private var pushPermission = false
    private var pushRegistered = false
    private var seenMessages: Set<String> = []
    private var messageOrder: [String] = []
    private var events: [FakePushEvent] = []
    public init() {}
    public func initialize(_ config: GameBridgeConfig) async throws -> InitSnapshot {
        guard config.mode == .editorOffline else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        ready = true
        return InitSnapshot(capabilities: ["fake": Capability(supported: true, configured: true, mode: config.mode, reason: "Offline fake only")])
    }
    public func shutdown() async throws { ready = false; signedIn = false; pushRegistered = false; events.removeAll(); seenMessages.removeAll(); messageOrder.removeAll() }
    public func signIn() throws -> UserProfile {
        try requireReady(); signedIn = true
        return UserProfile(userId: "d2719c4e-d533-47ee-9efd-838791ea79c8", displayName: "Mock User", provider: "MOCK")
    }
    public func products() throws -> [StoreProduct] {
        try requireReady()
        return [StoreProduct(productId: "coins_100", storeProductId: "coins_100", type: .consumable, title: "Mock coins", localizedPrice: "Mock price", currencyCode: "XXX", priceMicros: nil),
                StoreProduct(productId: "premium_unlock", storeProductId: "premium_unlock", type: .nonConsumable, title: "Mock premium", localizedPrice: "Mock price", currencyCode: "XXX", priceMicros: nil)]
    }
    public func purchase(productId: String, transactionId: UUID, scenario: FakeScenario) throws -> FakePurchase {
        try requireReady(); guard signedIn else { throw SdkFailure("SESSION_EXPIRED") }
        guard ["coins_100", "premium_unlock"].contains(productId) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        if scenario == .networkFailure { throw SdkFailure("NETWORK_UNAVAILABLE") }
        let id = "mock:\(transactionId.uuidString.lowercased())"
        if let previous = granted[id], previous != productId { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
        let shouldGrant = scenario == .success && granted[id] == nil
        if shouldGrant {
            if productId == "coins_100" {
                let (next, overflow) = coins.addingReportingOverflow(100)
                if overflow { throw SdkFailure("INTERNAL_ERROR") }; coins = next
            } else { premium = true }
            granted[id] = productId
        }
        let status: String
        switch scenario { case .success: status = "PURCHASED"; case .canceled: status = "CANCELED"; case .pending: status = "PENDING"; case .networkFailure: throw SdkFailure("NETWORK_UNAVAILABLE") }
        return FakePurchase(status: status, transactionId: id, granted: shouldGrant, wallet: FakeWallet(coinBalance: coins, premiumEnabled: premium))
    }
    public func requestPushPermission() throws -> Bool { try requireReady(); pushPermission = true; return true }
    public func registerPush() throws -> String {
        try requireReady(); guard signedIn else { throw SdkFailure("SESSION_EXPIRED") }
        guard pushPermission else { throw SdkFailure("PERMISSION_DENIED") }
        pushRegistered = true; return "mock-fingerprint"
    }
    public func receivePush(messageId: String, route: String) throws {
        try requireReady(); guard pushRegistered else { throw SdkFailure("PERMISSION_DENIED") }
        guard !messageId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, ["home", "store"].contains(route) else { throw SdkFailure("INVALID_ARGUMENT") }
        if seenMessages.insert(messageId).inserted {
            messageOrder.append(messageId)
            if messageOrder.count > 200 { seenMessages.remove(messageOrder.removeFirst()) }
            events.append(FakePushEvent(messageId: messageId, route: route))
        }
    }
    public func drainPushEvents() throws -> [FakePushEvent] {
        try requireReady(); let result = events; events.removeAll(); return result
    }
    public func wallet() throws -> FakeWallet { try requireReady(); return FakeWallet(coinBalance: coins, premiumEnabled: premium) }
    private func requireReady() throws { if !ready { throw SdkFailure("NOT_INITIALIZED") } }
}
