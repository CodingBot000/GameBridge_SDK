package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import java.math.BigInteger
import java.security.MessageDigest
import java.util.UUID

internal data class XcodeGrantInput(@field:NotBlank val productId: String, @field:NotBlank val transactionId: String, val bindingId: UUID)
internal data class XcodeGrantOutput(val userId: UUID, val bindingId: UUID, val productId: String, val transactionKey: String,
                                     val serverPurchaseId: UUID, val fulfillmentStatus: String)
private data class XcodePurchase(val id: UUID, val userId: UUID, val productId: String)

/** Development-only fake grant. Client claims are NOT Apple server signature verification. */
@RestController
@Profile("local-mock")
internal class MockXcodeStoreKitController(private val db: JdbcTemplate, private val tx: TransactionTemplate,
    @Value("\${GAMEBRIDGE_DEV_AUTH_KEY:}") private val developmentKey: String) {
    private fun principal(auth: Authentication, supplied: String?): SessionPrincipal {
        if (developmentKey.length < 32) throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE)
        if (supplied == null || !MessageDigest.isEqual(developmentKey.toByteArray(Charsets.UTF_8), supplied.toByteArray(Charsets.UTF_8)))
            throw ResponseStatusException(HttpStatus.FORBIDDEN)
        return auth.principal as SessionPrincipal
    }
    private fun scopedUser(principal: SessionPrincipal): UUID = UUID.nameUUIDFromBytes("gamebridge-xcode-storekit:${principal.userId}".toByteArray(Charsets.UTF_8))
    private fun ensureSession(principal: SessionPrincipal) {
        val valid = db.queryForObject("SELECT EXISTS(SELECT 1 FROM sessions WHERE id=? AND user_id=? AND app_scope='gamebridge-sample' AND revoked_at IS NULL AND expires_at>now())",
            Boolean::class.java, principal.sessionId, principal.userId) == true
        if (!valid) throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
    }
    private fun ensureXcodeUser(id: UUID) { db.update("INSERT INTO users(id,display_name) VALUES (?, 'Xcode StoreKit development') ON CONFLICT(id) DO NOTHING", id) }
    @PostMapping("/v1/dev/xcode-storekit/account")
    fun account(auth: Authentication, @RequestHeader("X-Development-Key", required = false) key: String?): Map<String, String> {
        val principal = principal(auth, key); ensureSession(principal); val user = scopedUser(principal); ensureXcodeUser(user)
        return mapOf("userId" to user.toString(), "bindingId" to user.toString())
    }
    @PostMapping("/v1/dev/xcode-storekit/grant")
    fun grant(auth: Authentication, @RequestHeader("X-Development-Key", required = false) key: String?, @Valid @RequestBody input: XcodeGrantInput): XcodeGrantOutput {
        val principal = principal(auth, key); val user = scopedUser(principal)
        if (input.bindingId != user) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        if (input.productId !in setOf("coins_100", "premium_unlock") || !input.transactionId.matches(Regex("[1-9][0-9]{0,19}")) ||
            runCatching { BigInteger(input.transactionId) > BigInteger("18446744073709551615") }.getOrDefault(true))
            throw ResponseStatusException(HttpStatus.BAD_REQUEST)
        val hash = MessageDigest.getInstance("SHA-256").digest(input.transactionId.toByteArray(Charsets.UTF_8))
        return tx.execute {
            val active = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND app_scope='gamebridge-sample' AND revoked_at IS NULL AND expires_at>now() FOR UPDATE",
                { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
            if (active == null) throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
            ensureXcodeUser(user)
            val proposed = UUID.randomUUID()
            val inserted = db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state)
                VALUES (?, 'gamebridge-sample', 'xcode-storekit', 'XCODE', ?, ?, ?, 'PURCHASED', 'GRANTED', 'CLIENT_PENDING')
                ON CONFLICT (app_id,environment,platform,proof_key_hash) DO NOTHING""", proposed, hash, user, input.productId)
            val purchase = db.queryForObject("SELECT id,user_id,product_id FROM purchases WHERE app_id='gamebridge-sample' AND environment='xcode-storekit' AND platform='XCODE' AND proof_key_hash=? FOR UPDATE",
                { rs, _ -> XcodePurchase(rs.getObject(1, UUID::class.java), rs.getObject(2, UUID::class.java), rs.getString(3)) }, hash)!!
            if (purchase.userId != user || purchase.productId != input.productId) throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
            if (inserted == 1) {
                if (input.productId == "coins_100") check(db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) SELECT ?,?,?,grant_amount,'XCODE_FAKE_PURCHASE' FROM products WHERE app_id='gamebridge-sample' AND platform='MOCK' AND logical_id=?", UUID.randomUUID(), purchase.id, user, input.productId) == 1)
                else db.update("INSERT INTO entitlements(user_id,product_id,active,source_purchase_id) VALUES (?, ?, true, ?) ON CONFLICT(user_id,product_id) DO UPDATE SET active=true,source_purchase_id=excluded.source_purchase_id", user, input.productId, purchase.id)
            }
            XcodeGrantOutput(user, user, input.productId, input.transactionId, purchase.id, if (inserted == 1) "GRANTED" else "ALREADY_GRANTED")
        }!!
    }
    @PostMapping("/v1/dev/xcode-storekit/wallet")
    fun wallet(auth: Authentication, @RequestHeader("X-Development-Key", required = false) key: String?): WalletSnapshot {
        val principal = principal(auth, key); ensureSession(principal); val user = scopedUser(principal); ensureXcodeUser(user)
        val coins = db.queryForObject("SELECT COALESCE(SUM(delta),0)::text FROM wallet_ledger WHERE user_id=?", String::class.java, user)!!
        val premium = db.queryForObject("SELECT EXISTS(SELECT 1 FROM entitlements WHERE user_id=? AND product_id='premium_unlock' AND active)", Boolean::class.java, user)!!
        val revision = db.queryForObject("SELECT COUNT(*)::text FROM purchases WHERE user_id=? AND fulfillment_state='GRANTED'", String::class.java, user)!!
        val updated = db.queryForObject("SELECT COALESCE(MAX(created_at),'1970-01-01 00:00:00+00'::timestamptz) FROM purchases WHERE user_id=?", java.sql.Timestamp::class.java, user)!!.toInstant().toString()
        return WalletSnapshot(user.toString(), premium, coins, revision, updated)
    }
}
