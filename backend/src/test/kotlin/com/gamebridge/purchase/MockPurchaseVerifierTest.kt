package com.gamebridge.purchase

import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull

class MockPurchaseVerifierTest {
    private val verifier = MockPurchaseVerifier()
    @Test fun `mock proof is bound to user product and transaction`() {
        val user = UUID.randomUUID(); val transaction = UUID.randomUUID()
        val proof = "mock:$user:coins_100:$transaction"
        assertEquals(transaction, assertNotNull(verifier.verify(proof, "coins_100", user)).transactionId)
        assertNull(verifier.verify(proof, "premium_unlock", user))
        assertNull(verifier.verify(proof, "coins_100", UUID.randomUUID()))
        assertNull(verifier.verify(proof.replace("mock:", "real:"), "coins_100", user))
        assertNull(verifier.verify("mock:$user:coins_100:not-a-uuid", "coins_100", user))
    }
}
