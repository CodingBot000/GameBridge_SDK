package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import java.util.UUID

/** The registry must bind a configured app and environment to its official Apple verifier. */
internal fun interface AppleVerifierRegistry {
    fun verifier(appId: String, environment: StoreEnvironment): ApplePurchaseVerifier
}
internal class ApplePurchasePipeline(private val db: JdbcTemplate, private val registry: AppleVerifierRegistry, private val grants: AppleGrantService) {
    fun verifyAndGrant(principal: SessionPrincipal, environment: StoreEnvironment, productId: String, signedTransaction: String, attemptId: UUID? = null): AppleGrantResult {
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
            ?: throw PurchaseConflict("SESSION_EXPIRED")
        val account = db.query("SELECT apple_account_token FROM purchase_account_bindings WHERE app_id=? AND user_id=?",
            { rs, _ -> rs.getObject(1, UUID::class.java) }, app, principal.userId).firstOrNull()
            ?: throw PurchaseConflict("PURCHASE_ACCOUNT_MISMATCH")
        val verified = registry.verifier(app, environment).verify(signedTransaction, productId, account)
        // Grant locks and revalidates the session/binding after potentially slow signature checks.
        return grants.grant(principal, environment, verified, attemptId)
    }
}
