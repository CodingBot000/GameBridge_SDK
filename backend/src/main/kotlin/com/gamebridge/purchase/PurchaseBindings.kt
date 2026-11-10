package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import org.springframework.stereotype.Service
import java.util.UUID

/** Random per-user/app/store bindings, never derived from email or raw account details. */
data class PurchaseBinding(val appleAccountToken: UUID, val googleObfuscatedAccountId: UUID) {
    override fun toString() = "PurchaseBinding([redacted])"
}
@Service
class PurchaseBindings(private val db: JdbcTemplate) {
    fun forUser(userId: UUID, appId: String): PurchaseBinding {
        require(appId.isNotBlank())
        db.update("INSERT INTO purchase_account_bindings(user_id,app_id,apple_account_token,google_obfuscated_id) VALUES (?,?,?,?) ON CONFLICT (user_id,app_id) DO NOTHING", userId, appId, UUID.randomUUID(), UUID.randomUUID())
        return requireNotNull(db.queryForObject("SELECT apple_account_token,google_obfuscated_id FROM purchase_account_bindings WHERE user_id=? AND app_id=?", { rs, _ ->
            PurchaseBinding(rs.getObject(1, UUID::class.java), rs.getObject(2, UUID::class.java))
        }, userId, appId))
    }
}

/** Scope is read from the authenticated session, never supplied by the client. */
@RestController
class PurchaseBindingController(private val db: JdbcTemplate, private val bindings: PurchaseBindings) {
    @GetMapping("/v1/purchases/bindings")
    fun binding(authentication: Authentication): PurchaseBinding {
        val principal = authentication.principal as SessionPrincipal
        val scope = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
        if (scope.isNullOrBlank()) throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
        return bindings.forUser(principal.userId, scope)
    }
}
