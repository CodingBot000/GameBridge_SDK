package com.gamebridge.purchase

import com.google.api.client.googleapis.json.GoogleJsonResponseException
import com.google.api.services.androidpublisher.AndroidPublisher
import com.google.api.services.androidpublisher.model.ProductPurchaseV2
import java.io.IOException
import java.security.MessageDigest

internal class GoogleProofRejected : RuntimeException("VERIFICATION_FAILED")
internal class GoogleVerifierUnavailable : RuntimeException("STORE_UNAVAILABLE")
internal data class VerifiedGooglePurchase(val proofHash: ByteArray, val productId: String, val account: String) {
    override fun toString() = "VerifiedGooglePurchase([redacted])"
}
internal fun interface GooglePurchaseLookup { fun get(packageName: String, token: String): ProductPurchaseV2 }

/** Publisher client credentials are injected by the host and are never loaded on the mock path. */
internal class GooglePurchaseVerifier(
    private val packageName: String,
    private val allowedProducts: Set<String>,
    private val sandbox: Boolean,
    private val lookup: GooglePurchaseLookup,
) {
    init { require(packageName.isNotBlank() && allowedProducts.isNotEmpty()) }
    fun verify(token: String, expectedProduct: String, expectedAccount: String): VerifiedGooglePurchase {
        if (token.isBlank() || expectedProduct !in allowedProducts || expectedAccount.isBlank()) throw GoogleProofRejected()
        val purchase = try { lookup.get(packageName, token) } catch (e: GoogleJsonResponseException) {
            if (e.statusCode == 400 || e.statusCode == 404 || e.statusCode == 410) throw GoogleProofRejected()
            throw GoogleVerifierUnavailable()
        } catch (_: IOException) { throw GoogleVerifierUnavailable() }
        val lines = purchase.productLineItem
        val item = lines?.singleOrNull()
        if (purchase.purchaseStateContext?.purchaseState != "PURCHASED" ||
            purchase.obfuscatedExternalAccountId != expectedAccount ||
            (purchase.testPurchaseContext != null) != sandbox ||
            item?.productId != expectedProduct || item.productOfferDetails?.quantity != 1) throw GoogleProofRejected()
        return VerifiedGooglePurchase(MessageDigest.getInstance("SHA-256").digest(token.toByteArray(Charsets.UTF_8)), expectedProduct, expectedAccount)
    }
    companion object {
        fun configured(packageName: String, products: Set<String>, sandbox: Boolean, publisher: AndroidPublisher) =
            GooglePurchaseVerifier(packageName, products, sandbox, GooglePurchaseLookup { app, token ->
                publisher.purchases().productsv2().getproductpurchasev2(app, token).execute()
            })
    }
}
