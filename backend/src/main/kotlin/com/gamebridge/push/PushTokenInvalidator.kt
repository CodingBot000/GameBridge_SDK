package com.gamebridge.push

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Component
import java.util.UUID

/** A stale provider response cannot invalidate a newer rotated token. */
@Component
internal class PushTokenInvalidator(private val db: JdbcTemplate) {
    fun invalidate(app: String, environment: String, platform: String, installation: UUID, user: UUID, tokenHash: ByteArray): Boolean =
        db.update("""UPDATE device_tokens SET invalidated_at=now() WHERE app_id=? AND environment=? AND platform=?
            AND installation_id=? AND user_id=? AND token_hash=? AND invalidated_at IS NULL""", app, environment, platform, installation, user, tokenHash) == 1
}
