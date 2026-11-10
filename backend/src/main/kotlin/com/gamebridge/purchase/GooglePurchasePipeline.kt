package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import java.util.UUID

internal fun interface GoogleVerifierRegistry {
    fun verifier(appId: String, environment: StoreEnvironment): GooglePurchaseVerifier
}
internal class GooglePurchasePipeline(private val db: JdbcTemplate, private val registry: GoogleVerifierRegistry, private val grants: GoogleGrantService) {
    fun verifyAndGrant(principal: SessionPrincipal, environment: StoreEnvironment, productId: String, token: String, attemptId: UUID): GoogleGrantResult {
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull() ?: throw PurchaseConflict("SESSION_EXPIRED")
        val account = db.query("SELECT google_obfuscated_id FROM purchase_account_bindings WHERE app_id=? AND user_id=?",
            { rs, _ -> rs.getObject(1, UUID::class.java).toString() }, app, principal.userId).firstOrNull() ?: throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        val verified = registry.verifier(app, environment).verify(token, productId, account)
        return grants.grant(principal, environment, verified, token, attemptId)
    }
}
