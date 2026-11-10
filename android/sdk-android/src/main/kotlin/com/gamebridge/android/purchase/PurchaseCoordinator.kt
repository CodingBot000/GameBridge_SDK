package com.gamebridge.android.purchase

import com.gamebridge.SdkFailure
import java.util.UUID

internal enum class StoreTransactionState { INITIATED, PENDING, PURCHASED, CANCELED, FAILED }
internal enum class GrantState { NOT_GRANTED, GRANTED }
internal enum class FinalizationPhase { NOT_REQUIRED, PENDING, FINALIZED }
internal data class PurchaseSnapshot(val store: StoreTransactionState, val grant: GrantState, val finalization: FinalizationPhase, val serverPurchaseId: UUID?)
/** Only a validated Backend response may be converted to this internal value. */
internal data class ServerGrant(val userId: UUID, val bindingId: UUID, val productId: String, val transactionKey: String, val serverPurchaseId: UUID) {
    override fun toString() = "ServerGrant([redacted])"
}

/** Tracks state only: wallet and entitlement authority remains the Backend. */
internal class PurchaseCoordinator(private val userId: UUID, private val bindingId: UUID, private val productId: String) {
    private var store = StoreTransactionState.INITIATED
    private var grant = GrantState.NOT_GRANTED
    private var finalization = FinalizationPhase.NOT_REQUIRED
    private var transactionKey: String? = null
    private var purchaseId: UUID? = null
    @Synchronized fun snapshot() = PurchaseSnapshot(store, grant, finalization, purchaseId)
    @Synchronized fun observe(next: StoreTransactionState, key: String? = null) {
        val allowed = when (store) {
            StoreTransactionState.INITIATED -> setOf(StoreTransactionState.PENDING, StoreTransactionState.PURCHASED, StoreTransactionState.CANCELED, StoreTransactionState.FAILED)
            StoreTransactionState.PENDING -> setOf(StoreTransactionState.PENDING, StoreTransactionState.PURCHASED, StoreTransactionState.CANCELED, StoreTransactionState.FAILED)
            else -> setOf(store)
        }
        if (next !in allowed || (next == StoreTransactionState.PURCHASED && key.isNullOrBlank())) throw SdkFailure("INVALID_ARGUMENT")
        if (transactionKey != null && key != null && transactionKey != key) throw SdkFailure("IDEMPOTENCY_CONFLICT")
        if (key != null) transactionKey = key
        store = next
    }
    @Synchronized fun acceptServerGrant(value: ServerGrant): Boolean {
        if (value.userId != userId || value.bindingId != bindingId) throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH")
        if (value.productId != productId || transactionKey == null || value.transactionKey != transactionKey) throw SdkFailure("VERIFICATION_FAILED")
        if (store != StoreTransactionState.PURCHASED) throw SdkFailure("VERIFICATION_FAILED")
        if (grant == GrantState.GRANTED) {
            if (purchaseId != value.serverPurchaseId) throw SdkFailure("IDEMPOTENCY_CONFLICT")
            return false
        }
        grant = GrantState.GRANTED; purchaseId = value.serverPurchaseId; finalization = FinalizationPhase.PENDING
        return true
    }
    @Synchronized fun finalized() {
        if (grant != GrantState.GRANTED || finalization == FinalizationPhase.NOT_REQUIRED) throw SdkFailure("INVALID_ARGUMENT")
        finalization = FinalizationPhase.FINALIZED
    }
}
