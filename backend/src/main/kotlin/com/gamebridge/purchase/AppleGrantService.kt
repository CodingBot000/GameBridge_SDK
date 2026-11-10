package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import java.security.MessageDigest
import java.util.UUID

internal enum class StoreEnvironment { SANDBOX, PRODUCTION }
internal data class AppleGrantResult(val userId: UUID, val bindingId: UUID, val productId: String,
                                     val transactionKey: String, val serverPurchaseId: UUID, val fulfillmentStatus: String) {
    override fun toString() = "AppleGrantResult([redacted])"
}
private data class AppleExistingPurchase(val id: UUID, val userId: UUID, val productId: String)

/** Caller must supply facts already verified by ApplePurchaseVerifier, never raw client claims. */
@Service
internal class AppleGrantService(private val db: JdbcTemplate, private val tx: TransactionTemplate) {
    fun grant(principal: SessionPrincipal, environment: StoreEnvironment, verified: VerifiedApplePurchase, attemptId: UUID? = null): AppleGrantResult = tx.execute {
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now() FOR UPDATE",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
            ?: throw PurchaseConflict("SESSION_EXPIRED")
        val binding = db.query("SELECT apple_account_token FROM purchase_account_bindings WHERE user_id=? AND app_id=?",
            { rs, _ -> rs.getObject(1, UUID::class.java) }, principal.userId, app).firstOrNull()
        if (binding != verified.account) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        val product = db.query("SELECT logical_id,type,grant_amount FROM products WHERE app_id=? AND platform='APPLE' AND store_id=?",
            { rs, _ -> Triple(rs.getString(1), rs.getString(2), rs.getLong(3)) }, app, verified.productId).firstOrNull()
            ?: throw PurchaseConflict("PRODUCT_NOT_FOUND")
        val hash = MessageDigest.getInstance("SHA-256").digest(verified.transactionId.toByteArray(Charsets.UTF_8))
        if (attemptId != null) {
            val requestHash = MessageDigest.getInstance("SHA-256").digest((verified.productId + "\u0000" + verified.transactionId + "\u0000" + environment.name).toByteArray(Charsets.UTF_8))
            db.update("INSERT INTO idempotency_records(user_id,operation,key,body_hash,state) VALUES (?, 'purchase.verify', ?, ?, 'STARTED') ON CONFLICT DO NOTHING", principal.userId, attemptId.toString(), requestHash)
            val existing = db.queryForObject("SELECT body_hash FROM idempotency_records WHERE user_id=? AND operation='purchase.verify' AND key=? FOR UPDATE", ByteArray::class.java, principal.userId, attemptId.toString())!!
            if (!MessageDigest.isEqual(existing, requestHash)) throw PurchaseConflict("IDEMPOTENCY_CONFLICT")
        }
        val newId = UUID.randomUUID()
        val inserted = db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state)
            VALUES (?,?,?,'APPLE',?,?,?,'PURCHASED','GRANTED','CLIENT_PENDING') ON CONFLICT (app_id,environment,platform,proof_key_hash) DO NOTHING""",
            newId, app, environment.name, hash, principal.userId, product.first)
        val stored = db.queryForObject("SELECT id,user_id,product_id FROM purchases WHERE app_id=? AND environment=? AND platform='APPLE' AND proof_key_hash=? FOR UPDATE",
            { rs, _ -> AppleExistingPurchase(rs.getObject(1, UUID::class.java), rs.getObject(2, UUID::class.java), rs.getString(3)) }, app, environment.name, hash)!!
        if (stored.userId != principal.userId || stored.productId != product.first) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        if (inserted == 1) when (product.second) {
            "CONSUMABLE" -> check(db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) VALUES (?,?,?,?, 'APPLE_PURCHASE')", UUID.randomUUID(), stored.id, principal.userId, product.third) == 1)
            "NON_CONSUMABLE" -> db.update("INSERT INTO entitlements(user_id,product_id,active,source_purchase_id) VALUES (?,?,true,?) ON CONFLICT (user_id,product_id) DO UPDATE SET active=true", principal.userId, product.first, stored.id)
            else -> error("Invalid catalog type")
        }
        if (attemptId != null) db.update("UPDATE idempotency_records SET purchase_id=?,state='COMPLETE' WHERE user_id=? AND operation='purchase.verify' AND key=?", stored.id, principal.userId, attemptId.toString())
        AppleGrantResult(principal.userId, verified.account, verified.productId, verified.transactionId, stored.id, if (inserted == 1) "GRANTED" else "ALREADY_GRANTED")
    }!!
}
