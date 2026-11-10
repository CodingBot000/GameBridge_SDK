#if canImport(StoreKit)
import Foundation
import StoreKit
import CryptoKit
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@available(iOS 16.0, macOS 13.0, *)
func isXcodeStoreEnvironment(_ environment: AppStore.Environment) -> Bool { environment == .xcode }

@MainActor private final class XcodeAccountReference { var value: ApplePurchaseAccount? }
private final class XcodeFakeProofSink: ApplePurchaseProofSink {
    let client: LocalMockClient
    let account: XcodeMockAccount
    init(client: LocalMockClient, account: XcodeMockAccount) { self.client = client; self.account = account }
    func verify(_ proof: ApplePurchaseProof, userId: UUID) async throws -> ServerGrant {
        guard userId == account.userId, proof.binding == account.bindingId else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
        // Fail closed until Xcode transaction identity remains stable across unfinished recovery.
        throw SdkFailure("CONFIG_REQUIRED", nativeCode: "XCODE_TRANSACTION_IDENTITY_UNSTABLE")
    }
}
/// Xcode-local StoreKit client verification with an isolated fake server grant; never Apple server validation.
@MainActor public final class XcodeStoreKitSession {
    private let client: LocalMockClient
    private let account: XcodeMockAccount
    private let accountRef: XcodeAccountReference
    private let provider: StoreKitBillingProvider
    private let onVerified: (AppleStorePurchaseResult) -> Void
    public init(client: LocalMockClient, onVerified: @escaping (AppleStorePurchaseResult) -> Void = { _ in }) async throws {
        self.client = client; self.onVerified = onVerified
        let account = try await client.xcodeAccount(); self.account = account
        let ref = XcodeAccountReference(); ref.value = ApplePurchaseAccount(userId: account.userId, binding: account.bindingId); self.accountRef = ref
        let sink = XcodeFakeProofSink(client: client, account: account)
        provider = StoreKitBillingProvider(sink: sink, onVerified: { grant in
            onVerified(AppleStorePurchaseResult(productId: grant.productId, status: .purchased, serverPurchaseId: grant.serverPurchaseId, fulfillmentStatus: grant.fulfillmentStatus))
        }, acceptsTransaction: { transaction in
            if #available(iOS 16.0, macOS 13.0, *) { return isXcodeStoreEnvironment(transaction.environment) }
            return false
        }, transactionIdentity: { _, jws in
            SHA256.hash(data: Data(jws.utf8)).map { String(format: "%02x", $0) }.joined()
        }) { [weak ref] in ref?.value }
    }
    public var userId: UUID { account.userId }
    public func start() async throws { provider.start(); _ = try await provider.recoverUnfinished() }
    public func products() async throws -> [StoreProduct] {
        let ids: Set<String> = ["coins_100", "premium_unlock"]
        let items = try await provider.products(ids: ids); let mapping = Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
        return try ["coins_100", "premium_unlock"].map { id in
            guard let value = mapping[id], value.type == (id == "coins_100" ? .consumable : .nonConsumable) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
            return StoreProduct(productId: id, storeProductId: id, type: id == "coins_100" ? .consumable : .nonConsumable,
                title: value.displayName, localizedPrice: value.displayPrice, currencyCode: value.priceFormatStyle.currencyCode, priceMicros: nil)
        }
    }
    private var transactionIdentityReady: Bool { false }
    public func purchase(_ id: String) async throws -> AppleStorePurchaseResult {
        guard ["coins_100", "premium_unlock"].contains(id) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        // Xcode's local transaction identity was observed to collide across separate purchases.
        guard transactionIdentityReady else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "XCODE_TRANSACTION_IDENTITY_UNSTABLE") }
        let settings = try await client.serviceSettings()
        guard MaintenanceGate.permits(maintenanceEnabled: settings.settings.maintenanceEnabled, operation: .startPurchase) else { throw SdkFailure("MAINTENANCE") }
        guard let product = try await provider.products(ids: [id]).first, product.id == id,
              product.type == (id == "coins_100" ? .consumable : .nonConsumable) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        switch try await provider.purchase(product) {
        case .pending: return AppleStorePurchaseResult(productId: id, status: .pending, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .verificationPending: return AppleStorePurchaseResult(productId: id, status: .verificationPending, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .cancelled: return AppleStorePurchaseResult(productId: id, status: .cancelled, serverPurchaseId: nil, fulfillmentStatus: nil)
        case .verified(let grant): return AppleStorePurchaseResult(productId: id, status: .purchased, serverPurchaseId: grant.serverPurchaseId, fulfillmentStatus: grant.fulfillmentStatus)
        }
    }
    public func recover(userInitiated: Bool) async throws -> AppleRecoveryCounts { try await userInitiated ? provider.userRestore() : provider.recoverUnfinished() }
    public func wallet() async throws -> LocalWallet { try await client.xcodeWallet(account: account) }
    public func stop() { accountRef.value = nil; provider.stop() }
}
#endif
