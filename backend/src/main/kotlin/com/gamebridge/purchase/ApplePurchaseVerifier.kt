package com.gamebridge.purchase

import com.apple.itunes.storekit.model.Environment
import com.apple.itunes.storekit.model.JWSTransactionDecodedPayload
import com.apple.itunes.storekit.model.Type
import com.apple.itunes.storekit.verification.SignedDataVerifier
import com.apple.itunes.storekit.verification.VerificationException
import com.apple.itunes.storekit.verification.VerificationStatus
import java.io.InputStream
import java.util.UUID

/** A successful result is only a verified store fact, never a grant by itself. */
internal data class VerifiedApplePurchase(val transactionId: String, val productId: String, val account: UUID)
internal class AppleProofRejected : RuntimeException("VERIFICATION_FAILED")
internal class AppleVerifierUnavailable : RuntimeException("STORE_UNAVAILABLE")

internal fun interface AppleSignedTransactionDecoder {
    fun decode(jws: String): JWSTransactionDecodedPayload
}

/** Only sandbox and production are accepted; Xcode testing needs a separate development path. */
internal class ApplePurchaseVerifier(
    private val bundleId: String,
    private val environment: Environment,
    private val products: Set<String>,
    private val decoder: AppleSignedTransactionDecoder,
) {
    init {
        require(bundleId.isNotBlank() && products.isNotEmpty())
        require(environment == Environment.SANDBOX || environment == Environment.PRODUCTION)
    }

    fun supports(productId: String): Boolean = productId in products
    fun verify(jws: String, expectedProduct: String, expectedAccount: UUID): VerifiedApplePurchase {
        if (jws.isBlank() || expectedProduct !in products) throw AppleProofRejected()
        val payload = try { decoder.decode(jws) } catch (e: VerificationException) {
            if (e.status == VerificationStatus.RETRYABLE_VERIFICATION_FAILURE) throw AppleVerifierUnavailable()
            throw AppleProofRejected()
        }
        if (payload.bundleId != bundleId || payload.environment != environment ||
            payload.productId != expectedProduct || payload.appAccountToken != expectedAccount ||
            payload.revocationDate != null || payload.quantity != 1 ||
            payload.type !in setOf(Type.CONSUMABLE, Type.NON_CONSUMABLE) || payload.transactionId.isNullOrBlank()) {
            throw AppleProofRejected()
        }
        return VerifiedApplePurchase(payload.transactionId, expectedProduct, expectedAccount)
    }

    companion object {
        /** Certificates and identifiers must be explicitly configured; no test roots or fallback. */
        fun configured(bundleId: String, appAppleId: Long?, environment: Environment, products: Set<String>, roots: Set<InputStream>): ApplePurchaseVerifier {
            require(roots.isNotEmpty())
            require(environment != Environment.PRODUCTION || appAppleId != null)
            val verifier = SignedDataVerifier(roots, bundleId, appAppleId, environment, true)
            return ApplePurchaseVerifier(bundleId, environment, products, AppleSignedTransactionDecoder { verifier.verifyAndDecodeTransaction(it) })
        }
    }
}
