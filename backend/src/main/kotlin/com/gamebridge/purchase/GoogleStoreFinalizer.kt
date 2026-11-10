package com.gamebridge.purchase

import com.google.api.services.androidpublisher.AndroidPublisher
import com.google.api.services.androidpublisher.model.ProductPurchase
import com.google.api.services.androidpublisher.model.ProductPurchasesAcknowledgeRequest
import java.security.MessageDigest
import java.util.UUID

enum class GoogleFinalizationAction { CONSUME, ACKNOWLEDGE }
internal class GoogleFinalizationInput(val purchaseId: UUID, val packageName: String, val productId: String,
                                       val accountId: String, val token: String, val action: GoogleFinalizationAction) {
    override fun toString() = "GoogleFinalizationInput([redacted])"
}
internal fun interface DurableGoogleGrantCheck { fun isGranted(input: GoogleFinalizationInput, tokenHash: ByteArray): Boolean }
internal interface GoogleFinalizationGateway {
    fun lookup(input: GoogleFinalizationInput): ProductPurchase
    fun consume(input: GoogleFinalizationInput)
    fun acknowledge(input: GoogleFinalizationInput)
}
/** Only invokes the store after a durable grant and a fresh matching store lookup. */
internal class GoogleStoreFinalizer(private val grantCheck: DurableGoogleGrantCheck, private val gateway: GoogleFinalizationGateway) {
    fun finalize(input: GoogleFinalizationInput) {
        require(input.packageName.isNotBlank() && input.productId.isNotBlank() && input.token.isNotBlank() && input.accountId.isNotBlank())
        val hash = MessageDigest.getInstance("SHA-256").digest(input.token.toByteArray(Charsets.UTF_8))
        if (!grantCheck.isGranted(input, hash)) throw PurchaseConflict("VERIFICATION_FAILED")
        val purchase = gateway.lookup(input)
        if (purchase.purchaseState != 0 || purchase.obfuscatedExternalAccountId != input.accountId ||
            (purchase.productId != null && purchase.productId != input.productId) || (purchase.quantity ?: 1) != 1) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        when (input.action) {
            GoogleFinalizationAction.CONSUME -> when (purchase.consumptionState) {
                1 -> return
                0 -> gateway.consume(input)
                else -> throw PurchaseConflict("VERIFICATION_FAILED")
            }
            GoogleFinalizationAction.ACKNOWLEDGE -> when (purchase.acknowledgementState) {
                1 -> return
                0 -> gateway.acknowledge(input)
                else -> throw PurchaseConflict("VERIFICATION_FAILED")
            }
        }
    }
    companion object {
        fun configured(grantCheck: DurableGoogleGrantCheck, publisher: AndroidPublisher) = GoogleStoreFinalizer(grantCheck, object : GoogleFinalizationGateway {
            override fun lookup(input: GoogleFinalizationInput): ProductPurchase = publisher.purchases().products().get(input.packageName, input.productId, input.token).execute()
            override fun consume(input: GoogleFinalizationInput) { publisher.purchases().products().consume(input.packageName, input.productId, input.token).execute() }
            override fun acknowledge(input: GoogleFinalizationInput) { publisher.purchases().products().acknowledge(input.packageName, input.productId, input.token, ProductPurchasesAcknowledgeRequest()).execute() }
        })
    }
}
