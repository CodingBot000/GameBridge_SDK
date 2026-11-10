#if canImport(StoreKit)
import Foundation
import StoreKit
import CryptoKit
import CoreFoundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// This only normalizes data already verified by StoreKit; it does not verify a JWS.
func xcodeStableIdentity(_ signedTransaction: String) -> String? {
    guard signedTransaction.utf8.count <= BridgeProtocol.maxBytes else { return nil }
    let parts = signedTransaction.split(separator: ".", omittingEmptySubsequences: false)
    guard parts.count == 3, !parts[1].isEmpty else { return nil }
    let raw = String(parts[1]).replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
    let padded = raw + String(repeating: "=", count: (4 - raw.count % 4) % 4)
    guard let data = Data(base64Encoded: padded), let payload = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] else { return nil }
    let keys = ["transactionId", "originalTransactionId", "productId", "purchaseDate", "originalPurchaseDate", "appAccountToken", "bundleId", "appTransactionId"]
    var selected: [String: Any] = [:]
    for key in keys {
        guard let value = payload[key] else { return nil }
        if let text = value as? String { guard !text.isEmpty else { return nil }; selected[key] = text }
        else if let number = value as? NSNumber, CFGetTypeID(number) != CFBooleanGetTypeID(), number.doubleValue.isFinite { selected[key] = number }
        else { return nil }
    }
    guard let canonical = try? JSONSerialization.data(withJSONObject: selected, options: [.sortedKeys]) else { return nil }
    return SHA256.hash(data: canonical).map { String(format: "%02x", $0) }.joined()
}

@available(iOS 16.0, macOS 13.0, *)
func isXcodeStoreEnvironment(_ environment: AppStore.Environment) -> Bool { environment == .xcode }

func validateXcodeIdentityMatches(_ count: Int) throws {
    if count == 0 { throw SdkFailure("NETWORK_UNAVAILABLE", retryable: true) }
    if count != 1 { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
}

@MainActor private final class XcodeAccountReference { var value: ApplePurchaseAccount? }
private final class XcodeFakeProofSink: ApplePurchaseProofSink {
    let client: LocalMockClient
    let account: XcodeMockAccount
    let journal: XcodeAttemptJournal
    init(client: LocalMockClient, account: XcodeMockAccount, journal: XcodeAttemptJournal) {
        self.client = client; self.account = account; self.journal = journal
    }
    func verify(_ proof: ApplePurchaseProof, userId: UUID) async throws -> ServerGrant {
        guard userId == account.userId, proof.binding == account.bindingId else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
        var matches = 0
        for await result in Transaction.all {
            let transaction: Transaction
            switch result {
            case .verified(let value): transaction = value
            case .unverified(let value, _):
                if value.appAccountToken == account.bindingId { throw SdkFailure("VERIFICATION_FAILED") }
                continue
            }
            guard transaction.appAccountToken == account.bindingId else { continue }
            if #available(iOS 18.0, macOS 15.0, *), transaction.environment == .xcode {
                guard let key = xcodeStableIdentity(result.jwsRepresentation) else { throw SdkFailure("VERIFICATION_FAILED") }
                if key == proof.transactionKey { matches += 1 }
            }
        }
        try validateXcodeIdentityMatches(matches)
        let attempt = try await journal.begin(account: account.userId, key: proof.transactionKey)
        let result = try await client.xcodeGrant(productId: proof.productId, transactionKey: proof.transactionKey, attemptId: attempt, account: account)
        return ServerGrant(userId: result.userId, bindingId: result.bindingId, productId: result.productId,
            transactionKey: result.transactionKey, serverPurchaseId: result.serverPurchaseId, fulfillmentStatus: result.fulfillmentStatus)
    }
    func didFinish(_ proof: ApplePurchaseProof, userId: UUID) async throws {
        guard userId == account.userId else { throw SdkFailure("INTERNAL_ERROR") }
        try await journal.finish(account: userId, key: proof.transactionKey)
    }
}
/// Xcode-local StoreKit client verification with an isolated fake server grant; never Apple server validation.
@MainActor public final class XcodeStoreKitSession {
    private let client: LocalMockClient
    private let account: XcodeMockAccount
    private let accountRef: XcodeAccountReference
    private let provider: StoreKitBillingProvider
    private let journal: XcodeAttemptJournal
    public init(client: LocalMockClient, pendingStore: TokenStore, onVerified: @escaping (AppleStorePurchaseResult) -> Void = { _ in }) async throws {
        guard !(await client.sharesTokenStore(pendingStore)) else { throw SdkFailure("CONFIG_REQUIRED") }
        guard #available(iOS 18.0, macOS 15.0, *) else { throw SdkFailure("UNSUPPORTED_PLATFORM", nativeCode: "XCODE_CONSUMABLE_HISTORY_REQUIRED") }
        guard Bundle.main.object(forInfoDictionaryKey: "SKIncludeConsumableInAppPurchaseHistory") as? Bool == true else {
            throw SdkFailure("CONFIG_REQUIRED", nativeCode: "XCODE_CONSUMABLE_HISTORY_REQUIRED")
        }
        self.client = client
        let journal = XcodeAttemptJournal(store: pendingStore); self.journal = journal
        let account = try await client.xcodeAccount(); self.account = account
        let ref = XcodeAccountReference(); ref.value = ApplePurchaseAccount(userId: account.userId, binding: account.bindingId); self.accountRef = ref
        let sink = XcodeFakeProofSink(client: client, account: account, journal: journal)
        provider = StoreKitBillingProvider(sink: sink, onVerified: { grant in
            onVerified(AppleStorePurchaseResult(productId: grant.productId, status: .purchased, serverPurchaseId: grant.serverPurchaseId, fulfillmentStatus: grant.fulfillmentStatus))
        }, acceptsTransaction: { transaction in
            if #available(iOS 16.0, macOS 13.0, *) { return isXcodeStoreEnvironment(transaction.environment) }
            return false
        }, transactionIdentity: { _, jws in
            xcodeStableIdentity(jws) ?? ""
        }) { [weak ref] in ref?.value }
    }
    public var userId: UUID { account.userId }
    public func start() async throws {
        var unfinished = Set<String>(); var history: [String: Int] = [:]
        for await result in Transaction.unfinished {
            guard case .verified(let value) = result, value.appAccountToken == account.bindingId else { continue }
            if #available(iOS 16.0, macOS 13.0, *), value.environment == .xcode {
                guard let key = xcodeStableIdentity(result.jwsRepresentation), unfinished.insert(key).inserted else { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
            }
        }
        for await result in Transaction.all {
            guard case .verified(let value) = result, value.appAccountToken == account.bindingId else { continue }
            if #available(iOS 16.0, macOS 13.0, *), value.environment == .xcode {
                guard let key = xcodeStableIdentity(result.jwsRepresentation) else { throw SdkFailure("VERIFICATION_FAILED") }
                history[key, default: 0] += 1
                guard history[key] == 1 else { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
            }
        }
        try await journal.reconcile(account: account.userId, unfinished: unfinished, completed: Set(history.keys).subtracting(unfinished))
        provider.start(); _ = try await provider.recoverUnfinished()
    }
    public func products() async throws -> [StoreProduct] {
        let ids: Set<String> = ["coins_100", "premium_unlock"]
        let items = try await provider.products(ids: ids); let mapping = Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
        return try ["coins_100", "premium_unlock"].map { id in
            guard let value = mapping[id], value.type == (id == "coins_100" ? .consumable : .nonConsumable) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
            return StoreProduct(productId: id, storeProductId: id, type: id == "coins_100" ? .consumable : .nonConsumable,
                title: value.displayName, localizedPrice: value.displayPrice, currencyCode: value.priceFormatStyle.currencyCode, priceMicros: nil)
        }
    }
    public func purchase(_ id: String) async throws -> AppleStorePurchaseResult {
        guard ["coins_100", "premium_unlock"].contains(id) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        try await journal.ensureEmpty(account: account.userId)
        for await result in Transaction.unfinished {
            if case .verified(let value) = result, value.appAccountToken == account.bindingId {
                if #available(iOS 16.0, macOS 13.0, *), value.environment == .xcode { throw SdkFailure("BUSY", retryable: true) }
            }
        }
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
