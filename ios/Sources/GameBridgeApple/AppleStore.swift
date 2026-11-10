import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

public enum AppleStorePurchaseStatus { case purchased, pending, verificationPending, cancelled }
public struct AppleStorePurchaseResult {
    public let productId: String
    public let status: AppleStorePurchaseStatus
    public let serverPurchaseId: UUID?
    public let fulfillmentStatus: String?
}
@MainActor private final class AppleStoreUpdates {
    var handler: ((AppleStorePurchaseResult) -> Void)?
}
/// Native facade. Product IDs are supplied by the host and prices come from StoreKit.
@MainActor
public final class AppleStore {
    private let auth: AppleAuthProvider
    private let client: BackendClient
    private let runtime: AppleStoreRuntime
    private let updates: AppleStoreUpdates
    public convenience init(auth: AppleAuthProvider, config: GameBridgeConfig, productIds: [String: String]) throws {
        guard config.mode == .platformSandbox else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard auth.usesConfiguration(config) else { throw SdkFailure("CONFIG_REQUIRED") }
        try self.init(auth: auth, client: BackendClient(config: config), productIds: productIds)
    }
    internal init(auth: AppleAuthProvider, client: BackendClient, productIds: [String: String]) throws {
        self.auth = auth; self.client = client
        let updates = AppleStoreUpdates(); self.updates = updates
        runtime = try AppleStoreRuntime(auth: auth, client: client, productIds: productIds) { productId, grant in
            updates.handler?(AppleStorePurchaseResult(productId: productId, status: .purchased,
                serverPurchaseId: grant.serverPurchaseId, fulfillmentStatus: grant.fulfillmentStatus))
        }
    }
    public func setPurchaseUpdatedHandler(_ handler: ((AppleStorePurchaseResult) -> Void)?) { updates.handler = handler }
    public func start() async throws { try await runtime.start() }
    public func products() async throws -> [StoreProduct] { try await runtime.products() }
    public func purchase(productId: String) async throws -> AppleStorePurchaseResult {
        switch try await runtime.purchase(productId) {
        case .pending: return AppleStorePurchaseResult(productId: productId, status: .pending, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .verificationPending: return AppleStorePurchaseResult(productId: productId, status: .verificationPending, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .cancelled: return AppleStorePurchaseResult(productId: productId, status: .cancelled, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .verified(let grant): return AppleStorePurchaseResult(productId: productId, status: .purchased, serverPurchaseId: grant.serverPurchaseId, fulfillmentStatus: grant.fulfillmentStatus)
        }
    }
    public func entitlements() async throws -> EntitlementSnapshot {
        let value: EntitlementSnapshot? = try await auth.withAuthenticatedSession { session in
            let response = try await client.request(path: "/v1/entitlements", method: "GET", accessToken: session.accessToken)
            guard let snapshot = try? JSONDecoder().decode(EntitlementSnapshot.self, from: response.json), snapshot.userId == session.userId else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return snapshot
        }
        guard let value else { throw SdkFailure("SESSION_EXPIRED") }
        return value
    }
    /// Only call after an explicit user restore action.
    public func restore() async throws { try await runtime.userRestore() }
    public func stop() { updates.handler = nil; runtime.stop() }
}
