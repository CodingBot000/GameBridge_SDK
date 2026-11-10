package com.gamebridge.purchase

import org.springframework.context.annotation.Profile
import org.springframework.stereotype.Component
import java.util.UUID

/** Accepts synthetic proofs only in the explicitly selected local-mock profile. */
@Component
@Profile("local-mock")
class MockPurchaseVerifier {
    data class Verified(val transactionId: UUID, val productId: String, val owner: UUID)
    fun verify(proof: String, expectedProduct: String, expectedUser: UUID): Verified? {
        if (proof.length > 160) return null
        val fields = proof.split(':')
        if (fields.size != 4 || fields[0] != "mock" || fields[2] != expectedProduct ||
            expectedProduct !in setOf("coins_100", "premium_unlock")) return null
        val owner = runCatching { UUID.fromString(fields[1]) }.getOrNull() ?: return null
        val transaction = runCatching { UUID.fromString(fields[3]) }.getOrNull() ?: return null
        if (owner != expectedUser || owner.toString() != fields[1] || transaction.toString() != fields[3]) return null
        return Verified(transaction, expectedProduct, owner)
    }
}
