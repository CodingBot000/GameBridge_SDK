import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

enum StoreTransactionState { case initiated, pending, purchased, canceled, failed }
enum GrantState { case notGranted, granted }
enum FinalizationPhase { case notRequired, pending, finalized }
struct PurchaseSnapshot {
    let store: StoreTransactionState
    let grant: GrantState
    let finalization: FinalizationPhase
    let serverPurchaseId: UUID?
}
/// Only a verified Backend response can be converted into this internal value.
struct ServerGrant: CustomStringConvertible {
    let userId, bindingId: UUID
    let productId, transactionKey: String
    let serverPurchaseId: UUID
    let fulfillmentStatus: String
    init(userId: UUID, bindingId: UUID, productId: String, transactionKey: String, serverPurchaseId: UUID, fulfillmentStatus: String = "GRANTED") {
        self.userId = userId; self.bindingId = bindingId; self.productId = productId; self.transactionKey = transactionKey
        self.serverPurchaseId = serverPurchaseId; self.fulfillmentStatus = fulfillmentStatus
    }
    var description: String { "ServerGrant([redacted])" }
}
/// Native state only; the Backend remains authoritative for balances and entitlements.
actor PurchaseCoordinator {
    private let userId, bindingId: UUID
    private let productId: String
    private var store: StoreTransactionState = .initiated
    private var grant: GrantState = .notGranted
    private var finalization: FinalizationPhase = .notRequired
    private var transactionKey: String?
    private var purchaseId: UUID?
    init(userId: UUID, bindingId: UUID, productId: String) { self.userId = userId; self.bindingId = bindingId; self.productId = productId }
    func snapshot() -> PurchaseSnapshot { PurchaseSnapshot(store: store, grant: grant, finalization: finalization, serverPurchaseId: purchaseId) }
    func observe(_ next: StoreTransactionState, key: String? = nil) throws {
        let allowed: [StoreTransactionState]
        switch store {
        case .initiated: allowed = [.pending, .purchased, .canceled, .failed]
        case .pending: allowed = [.pending, .purchased, .canceled, .failed]
        default: allowed = [store]
        }
        guard allowed.contains(next), next != .purchased || (key?.isEmpty == false) else { throw SdkFailure("INVALID_ARGUMENT") }
        if let transactionKey, let key, transactionKey != key { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
        if let key { transactionKey = key }; store = next
    }
    func acceptServerGrant(_ value: ServerGrant) throws -> Bool {
        guard value.userId == userId, value.bindingId == bindingId else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
        guard value.productId == productId, let transactionKey, value.transactionKey == transactionKey, store == .purchased else { throw SdkFailure("VERIFICATION_FAILED") }
        if grant == .granted {
            guard purchaseId == value.serverPurchaseId else { throw SdkFailure("IDEMPOTENCY_CONFLICT") }
            return false
        }
        grant = .granted; purchaseId = value.serverPurchaseId; finalization = .pending
        return true
    }
    func markFinalized() throws {
        guard grant == .granted && finalization != .notRequired else { throw SdkFailure("INVALID_ARGUMENT") }
        finalization = .finalized
    }
}
