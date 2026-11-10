package com.gamebridge.purchase

import com.apple.itunes.storekit.model.Environment
import com.apple.itunes.storekit.model.JWSTransactionDecodedPayload
import com.apple.itunes.storekit.model.Type
import com.apple.itunes.storekit.verification.VerificationException
import com.apple.itunes.storekit.verification.VerificationStatus
import java.util.UUID
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class ApplePurchaseVerifierTest {
    private val account = UUID.randomUUID()
    private fun payload() = JWSTransactionDecodedPayload().bundleId("test.bundle").environment(Environment.SANDBOX)
        .productId("coins").appAccountToken(account).transactionId("123").quantity(1).type(Type.CONSUMABLE)
    private fun verifier(payload: JWSTransactionDecodedPayload) = ApplePurchaseVerifier("test.bundle", Environment.SANDBOX, setOf("coins"), AppleSignedTransactionDecoder { payload })
    @Test fun `verified facts must match configured app product account and state`() {
        assertEquals("123", verifier(payload()).verify("synthetic", "coins", account).transactionId)
        listOf(payload().bundleId("wrong"), payload().environment(Environment.PRODUCTION), payload().productId("other"),
            payload().appAccountToken(UUID.randomUUID()), payload().revocationDate(1L), payload().quantity(2),
            payload().type(Type.AUTO_RENEWABLE_SUBSCRIPTION), payload().transactionId("")).forEach {
            assertFailsWith<AppleProofRejected> { verifier(it).verify("synthetic", "coins", account) }
        }
        assertFailsWith<AppleProofRejected> { verifier(payload()).verify("synthetic", "unknown", account) }
        assertFailsWith<IllegalArgumentException> { ApplePurchaseVerifier("test.bundle", Environment.XCODE, setOf("coins"), AppleSignedTransactionDecoder { payload() }) }
    }
    @Test fun `signature failure and retryable certificate failure stay distinct`() {
        fun failing(status: VerificationStatus) = ApplePurchaseVerifier("test.bundle", Environment.SANDBOX, setOf("coins"), AppleSignedTransactionDecoder { throw VerificationException(status) })
        assertFailsWith<AppleProofRejected> { failing(VerificationStatus.INVALID_CHAIN).verify("forged", "coins", account) }
        assertFailsWith<AppleVerifierUnavailable> { failing(VerificationStatus.RETRYABLE_VERIFICATION_FAILURE).verify("synthetic", "coins", account) }
    }
}
