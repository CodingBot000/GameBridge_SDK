package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import java.security.MessageDigest
import java.util.UUID

private fun digest(value: String): ByteArray = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
private fun reject(status: HttpStatus): Nothing = throw ResponseStatusException(status, "Request rejected")
class PurchaseConflict(val errorCode: String) : RuntimeException()
data class MockPurchaseInput(@field:NotBlank val productId: String, @field:NotBlank val proof: String, val quantity: Int) {
    override fun toString() = "MockPurchaseInput([redacted])"
}
data class WalletSnapshot(val userId: String, val premiumEnabled: Boolean, val coinBalance: String, val revision: String, val updatedAt: String)
data class MockPurchaseOutput(val serverPurchaseId: String, val fulfillmentStatus: String, val finalizationStatus: String, val entitlements: WalletSnapshot)
private data class ExistingPurchase(val id: UUID, val owner: UUID, val product: String)

@RestController
@Profile("local-mock")
class MockPurchaseController(private val verifier: MockPurchaseVerifier, private val db: JdbcTemplate, private val tx: TransactionTemplate) {
    @GetMapping("/v1/catalog")
    fun catalog(): List<Map<String, Any>> = db.queryForList("SELECT logical_id AS \"productId\", store_id AS \"storeProductId\", type FROM products WHERE app_id='gamebridge-sample' AND platform='MOCK' ORDER BY logical_id")

    @GetMapping("/v1/entitlements")
    fun entitlements(auth: Authentication): WalletSnapshot = wallet((auth.principal as SessionPrincipal).userId)

    @PostMapping("/v1/purchases/verify")
    fun verify(auth: Authentication, @RequestHeader("Idempotency-Key") key: String, @Valid @RequestBody input: MockPurchaseInput): MockPurchaseOutput {
        if (key.isBlank() || key.length > 128 || input.quantity != 1) reject(HttpStatus.BAD_REQUEST)
        val user = (auth.principal as SessionPrincipal).userId
        val parts = input.proof.split(':')
        if (parts.size == 4 && parts[0] == "mock" && parts[1] != user.toString()) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        val verified = verifier.verify(input.proof, input.productId, user) ?: reject(HttpStatus.BAD_REQUEST)
        val bodyHash = digest("${input.productId}\u0000${input.proof}\u0000${input.quantity}")
        val proofHash = digest(verified.transactionId.toString())
        return tx.execute {
            db.update("INSERT INTO idempotency_records(user_id,operation,key,body_hash,state) VALUES (?, 'purchase.verify', ?, ?, 'STARTED') ON CONFLICT DO NOTHING", user, key, bodyHash)
            val existingHash = db.queryForObject("SELECT body_hash FROM idempotency_records WHERE user_id=? AND operation='purchase.verify' AND key=? FOR UPDATE", ByteArray::class.java, user, key)!!
            if (!MessageDigest.isEqual(existingHash, bodyHash)) throw PurchaseConflict("IDEMPOTENCY_CONFLICT")
            val newId = UUID.randomUUID()
            val inserted = db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state)
                VALUES (?, 'gamebridge-sample', 'local-mock', 'MOCK', ?, ?, ?, 'PURCHASED', 'GRANTED', 'PENDING') ON CONFLICT (app_id,environment,platform,proof_key_hash) DO NOTHING""", newId, proofHash, user, input.productId)
            val purchase = db.queryForObject("SELECT id,user_id,product_id FROM purchases WHERE app_id='gamebridge-sample' AND environment='local-mock' AND platform='MOCK' AND proof_key_hash=? FOR UPDATE", { rs, _ -> ExistingPurchase(rs.getObject("id", UUID::class.java), rs.getObject("user_id", UUID::class.java), rs.getString("product_id")) }, proofHash)!!
            if (purchase.owner != user || purchase.product != input.productId) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
            if (inserted == 1) {
                val catalogCount = db.queryForObject("SELECT COUNT(*) FROM products WHERE app_id='gamebridge-sample' AND platform='MOCK' AND logical_id=?", Int::class.java, input.productId) ?: 0
                check(catalogCount == 1) { "Mock catalog is incomplete" }
                if (input.productId == "coins_100") {
                    val count = db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) SELECT ?,?,?,grant_amount,'MOCK_PURCHASE' FROM products WHERE app_id='gamebridge-sample' AND platform='MOCK' AND logical_id=?", UUID.randomUUID(), purchase.id, user, input.productId)
                    check(count == 1) { "Mock ledger grant failed" }
                } else {
                    db.update("INSERT INTO entitlements(user_id,product_id,active,source_purchase_id) VALUES (?, ?, true, ?) ON CONFLICT (user_id,product_id) DO UPDATE SET active=true", user, input.productId, purchase.id)
                }
            }
            if (inserted == 1) {
                db.update("INSERT INTO store_finalization_jobs(purchase_id,action,next_attempt_at,status) VALUES (?, 'MOCK', now(), 'PENDING')", purchase.id)
            }
            db.update("UPDATE idempotency_records SET purchase_id=?,state='COMPLETE' WHERE user_id=? AND operation='purchase.verify' AND key=?", purchase.id, user, key)
            val finalization = db.queryForObject("SELECT finalization_state FROM purchases WHERE id=?", String::class.java, purchase.id)!!
            MockPurchaseOutput(purchase.id.toString(), if (inserted == 1) "GRANTED" else "ALREADY_GRANTED", finalization, wallet(user))
        }!!
    }
    private fun wallet(user: UUID): WalletSnapshot {
        val balance = db.queryForObject("SELECT COALESCE(SUM(delta),0)::text FROM wallet_ledger WHERE user_id=?", String::class.java, user)!!
        val premium = db.queryForObject("SELECT EXISTS(SELECT 1 FROM entitlements WHERE user_id=? AND product_id='premium_unlock' AND active)", Boolean::class.java, user)!!
        val revision = db.queryForObject("SELECT COUNT(*)::text FROM purchases WHERE user_id=? AND fulfillment_state='GRANTED'", String::class.java, user)!!
        val updated = db.queryForObject("SELECT COALESCE(MAX(created_at),'1970-01-01 00:00:00+00'::timestamptz) FROM purchases WHERE user_id=? AND fulfillment_state='GRANTED'", java.sql.Timestamp::class.java, user)!!.toInstant().toString()
        return WalletSnapshot(user.toString(), premium, balance, revision, updated)
    }
}
