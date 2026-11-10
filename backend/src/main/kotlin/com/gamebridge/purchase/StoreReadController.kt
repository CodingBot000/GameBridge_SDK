package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import java.util.UUID

/** Store prices are intentionally absent; only the platform store supplies localized prices. */
@RestController
@Profile("sandbox", "production")
internal class StoreReadController(private val db: JdbcTemplate, private val environment: Environment) {
    private fun scope(principal: SessionPrincipal): String = db.query(
        "SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
        { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
        ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
    private fun mode() = if (environment.activeProfiles.contains("sandbox")) "SANDBOX" else "PRODUCTION"

    @GetMapping("/v1/catalog")
    fun catalog(auth: Authentication): List<Map<String, Any>> {
        val principal = auth.principal as SessionPrincipal
        return db.queryForList("SELECT logical_id AS \"productId\", store_id AS \"storeProductId\", platform, type FROM products WHERE app_id=? AND platform IN ('GOOGLE','APPLE') ORDER BY logical_id,platform", scope(principal))
    }
    @GetMapping("/v1/entitlements")
    fun entitlements(auth: Authentication): WalletSnapshot {
        val principal = auth.principal as SessionPrincipal; val app = scope(principal); val env = mode()
        val balance = db.queryForObject("SELECT COALESCE(SUM(l.delta),0)::text FROM wallet_ledger l JOIN purchases p ON p.id=l.purchase_id WHERE p.user_id=? AND p.app_id=? AND p.environment=? AND p.fulfillment_state='GRANTED'", String::class.java, principal.userId, app, env)!!
        val premium = db.queryForObject("SELECT EXISTS(SELECT 1 FROM entitlements e JOIN purchases p ON p.id=e.source_purchase_id WHERE e.user_id=? AND p.app_id=? AND p.environment=? AND e.product_id='premium_unlock' AND e.active)", Boolean::class.java, principal.userId, app, env)!!
        val revision = db.queryForObject("SELECT COUNT(*)::text FROM purchases WHERE user_id=? AND app_id=? AND environment=? AND fulfillment_state='GRANTED'", String::class.java, principal.userId, app, env)!!
        val updated = db.queryForObject("SELECT COALESCE(MAX(created_at),'1970-01-01 00:00:00+00'::timestamptz) FROM purchases WHERE user_id=? AND app_id=? AND environment=? AND fulfillment_state='GRANTED'", java.sql.Timestamp::class.java, principal.userId, app, env)!!.toInstant().toString()
        return WalletSnapshot(principal.userId.toString(), premium, balance, revision, updated)
    }
    @GetMapping("/v1/purchases/{purchaseId}")
    fun purchase(auth: Authentication, @PathVariable purchaseId: UUID): Map<String, Any> {
        val principal = auth.principal as SessionPrincipal
        return db.query("SELECT id,product_id,store_state,fulfillment_state,finalization_state FROM purchases WHERE id=? AND user_id=? AND app_id=? AND environment=?",
            { rs, _ -> mapOf("serverPurchaseId" to rs.getObject(1, UUID::class.java).toString(), "productId" to rs.getString(2),
                "storeStatus" to rs.getString(3), "fulfillmentStatus" to rs.getString(4), "finalizationStatus" to (if (rs.getString(5) == "CLIENT_PENDING") "PENDING" else rs.getString(5))) },
            purchaseId, principal.userId, scope(principal), mode()).firstOrNull() ?: throw ResponseStatusException(HttpStatus.NOT_FOUND)
    }
}
