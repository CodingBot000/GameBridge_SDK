package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import java.security.MessageDigest
import java.util.UUID

internal data class GoogleGrantResult(val userId: UUID, val accountId: String, val productId: String,
                                      val serverPurchaseId: UUID, val fulfillmentStatus: String, val proofFingerprint: String) {
    override fun toString() = "GoogleGrantResult([redacted])"
}
private data class GoogleExistingPurchase(val id: UUID, val userId: UUID, val productId: String)

/** Requires store-verified facts; encrypted evidence remains pending until an authorized retention policy is applied. */
@Service
internal class GoogleGrantService(private val db: JdbcTemplate, private val tx: TransactionTemplate, private val cipher: GoogleEvidenceCipher) {
    fun grant(principal: SessionPrincipal, environment: StoreEnvironment, verified: VerifiedGooglePurchase, token: String, attemptId: UUID): GoogleGrantResult = tx.execute {
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now() FOR UPDATE",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull() ?: throw PurchaseConflict("SESSION_EXPIRED")
        val binding = db.query("SELECT google_obfuscated_id FROM purchase_account_bindings WHERE user_id=? AND app_id=?",
            { rs, _ -> rs.getObject(1, UUID::class.java).toString() }, principal.userId, app).firstOrNull()
        if (binding == null || binding != verified.account) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        val product = db.query("SELECT logical_id,type,grant_amount FROM products WHERE app_id=? AND platform='GOOGLE' AND store_id=?",
            { rs, _ -> Triple(rs.getString(1), rs.getString(2), rs.getLong(3)) }, app, verified.productId).firstOrNull()
            ?: throw PurchaseConflict("PRODUCT_NOT_FOUND")
        val hash = MessageDigest.getInstance("SHA-256").digest(token.toByteArray(Charsets.UTF_8))
        if (token.isBlank() || !MessageDigest.isEqual(hash, verified.proofHash)) throw PurchaseConflict("VERIFICATION_FAILED")
        val bodyHash = MessageDigest.getInstance("SHA-256").digest((verified.productId + "\u0000" + environment.name).toByteArray(Charsets.UTF_8) + hash)
        db.update("INSERT INTO idempotency_records(user_id,operation,key,body_hash,state) VALUES (?, 'purchase.verify', ?, ?, 'STARTED') ON CONFLICT DO NOTHING", principal.userId, attemptId.toString(), bodyHash)
        val existingHash = db.queryForObject("SELECT body_hash FROM idempotency_records WHERE user_id=? AND operation='purchase.verify' AND key=? FOR UPDATE", ByteArray::class.java, principal.userId, attemptId.toString())!!
        if (!MessageDigest.isEqual(bodyHash, existingHash)) throw PurchaseConflict("IDEMPOTENCY_CONFLICT")
        val newId = UUID.randomUUID()
        val encrypted = cipher.encrypt(token, "$app:${environment.name}:GOOGLE:$newId")
        val inserted = db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state,evidence_encrypted)
            VALUES (?,?,?,'GOOGLE',?,?,?,'PURCHASED','GRANTED','PENDING',?) ON CONFLICT (app_id,environment,platform,proof_key_hash) DO NOTHING""",
            newId, app, environment.name, hash, principal.userId, product.first, encrypted)
        val stored = db.queryForObject("SELECT id,user_id,product_id FROM purchases WHERE app_id=? AND environment=? AND platform='GOOGLE' AND proof_key_hash=? FOR UPDATE",
            { rs, _ -> GoogleExistingPurchase(rs.getObject(1, UUID::class.java), rs.getObject(2, UUID::class.java), rs.getString(3)) }, app, environment.name, hash)!!
        if (stored.userId != principal.userId || stored.productId != product.first) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        if (inserted == 1) {
            val action = when (product.second) {
                "CONSUMABLE" -> {
                    check(db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) VALUES (?,?,?,?, 'GOOGLE_PURCHASE')", UUID.randomUUID(), stored.id, principal.userId, product.third) == 1)
                    "GOOGLE_CONSUME"
                }
                "NON_CONSUMABLE" -> {
                    db.update("INSERT INTO entitlements(user_id,product_id,active,source_purchase_id) VALUES (?,?,true,?) ON CONFLICT (user_id,product_id) DO UPDATE SET active=true", principal.userId, product.first, stored.id)
                    "GOOGLE_ACKNOWLEDGE"
                }
                else -> error("Invalid catalog type")
            }
            db.update("INSERT INTO store_finalization_jobs(purchase_id,action,next_attempt_at,status) VALUES (?,?,now(),'PENDING')", stored.id, action)
        }
        db.update("UPDATE idempotency_records SET purchase_id=?,state='COMPLETE' WHERE user_id=? AND operation='purchase.verify' AND key=?", stored.id, principal.userId, attemptId.toString())
        GoogleGrantResult(principal.userId, verified.account, product.first, stored.id, if (inserted == 1) "GRANTED" else "ALREADY_GRANTED", hash.joinToString("") { "%02x".format(it) })
    }!!
}
