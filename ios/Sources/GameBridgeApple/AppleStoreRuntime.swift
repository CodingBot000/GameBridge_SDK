import Foundation
import StoreKit
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// Native-only composition. The host supplies configured store IDs and an authenticated session.
@MainActor
final class AppleStoreRuntime {
    private let ids: [String: String]
    private let account: ApplePurchaseAccountSource
    private let provider: StoreKitBillingProvider

    init(auth: AppleAuthProvider, client: BackendClient, productIds: [String: String], verificationConcurrency: Int = 1) throws {
        guard Set(productIds.keys) == Set(["coins_100", "premium_unlock"]),
              productIds.values.allSatisfy({ !$0.isEmpty }), Set(productIds.values).count == 2,
              verificationConcurrency > 0 else { throw SdkFailure("CONFIG_REQUIRED") }
        ids = productIds
        let account = ApplePurchaseAccountSource(auth: auth, client: client)
        self.account = account
        let sink = AppleHttpProofSink(auth: auth, client: client)
        provider = StoreKitBillingProvider(sink: sink, verificationConcurrency: verificationConcurrency, uiGate: auth.uiGate) { [weak account] in account?.current() }
    }
    func start() async throws {
        guard try await account.refresh() != nil else { throw SdkFailure("SESSION_EXPIRED") }
        provider.start()
        await provider.recoverUnfinished()
    }
    func products() async throws -> [StoreProduct] {
        let products = try await provider.products(ids: Set(ids.values))
        let byId = Dictionary(uniqueKeysWithValues: products.map { ($0.id, $0) })
        return try ["coins_100", "premium_unlock"].map { logical in
            guard let storeId = ids[logical], let product = byId[storeId] else { throw SdkFailure("PRODUCT_NOT_FOUND") }
            try validateType(product, logical: logical)
            return StoreProduct(productId: logical, storeProductId: storeId, type: logical == "coins_100" ? .consumable : .nonConsumable,
                                title: product.displayName, localizedPrice: product.displayPrice, currencyCode: product.priceFormatStyle.currencyCode, priceMicros: nil)
        }
    }
    func purchase(_ logicalProductId: String) async throws -> ApplePurchaseOutcome {
        guard let storeId = ids[logicalProductId] else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        guard try await account.refresh() != nil else { throw SdkFailure("SESSION_EXPIRED") }
        guard let product = try await provider.products(ids: [storeId]).first, product.id == storeId else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        try validateType(product, logical: logicalProductId)
        return try await provider.purchase(product)
    }
    /// Must be called only in response to a user restore action.
    func userRestore() async throws {
        guard try await account.refresh() != nil else { throw SdkFailure("SESSION_EXPIRED") }
        try await provider.userRestore()
    }
    func stop() { provider.stop() }
    private func validateType(_ product: Product, logical: String) throws {
        let expected: Product.ProductType = logical == "coins_100" ? .consumable : .nonConsumable
        guard product.type == expected else { throw SdkFailure("PRODUCT_NOT_FOUND") }
    }
}
