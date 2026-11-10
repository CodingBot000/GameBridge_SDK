package com.gamebridge.purchase

import org.springframework.jdbc.core.JdbcTemplate
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
