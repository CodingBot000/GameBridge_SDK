package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import java.util.UUID

internal fun interface PushProviderClient {
    fun send(app: String, provider: String, token: String, content: PushContent): PushAttempt
}
internal data class PushDispatchTarget(val principal: SessionPrincipal, val app: String, val environment: String, val installation: UUID)
private data class ActiveDevice(val platform: String, val provider: String, val encrypted: ByteArray, val hash: ByteArray)

/** No token is cached between attempts; ownership and active session are rechecked each time. */
internal class PushDispatcher(private val db: JdbcTemplate, private val cipher: TokenCipher, private val invalidator: PushTokenInvalidator,
                              private val provider: PushProviderClient) {
    fun send(target: PushDispatchTarget, content: PushContent): PushAttempt {
        val devices = db.query("""SELECT d.platform,d.provider,d.token_encrypted,d.token_hash FROM device_tokens d
            JOIN sessions s ON s.id=d.session_id AND s.user_id=d.user_id
            WHERE d.app_id=? AND d.environment=? AND d.installation_id=? AND d.user_id=? AND d.invalidated_at IS NULL
              AND s.revoked_at IS NULL AND s.refresh_expires_at>now()
              AND EXISTS(SELECT 1 FROM sessions requester WHERE requester.id=? AND requester.user_id=?
                         AND requester.revoked_at IS NULL AND requester.refresh_expires_at>now())""", { rs, _ ->
            ActiveDevice(rs.getString(1), rs.getString(2), rs.getBytes(3), rs.getBytes(4))
        }, target.app, target.environment, target.installation, target.principal.userId, target.principal.sessionId, target.principal.userId)
        val device = devices.singleOrNull() ?: return PushAttempt(PushSendResult.FAILED, PushFailure.PERMANENT)
        if (!((device.platform == "ANDROID" && device.provider == "FCM") || (device.platform == "IOS" && device.provider == "APNS")))
            return PushAttempt(PushSendResult.FAILED, PushFailure.PERMANENT)
        val token = cipher.decrypt(device.encrypted, "${target.app}:${target.environment}:${device.platform}:${target.installation}")
        val result = provider.send(target.app, device.provider, token, content)
        if (result.result == PushSendResult.INVALID_TOKEN)
            invalidator.invalidate(target.app, target.environment, device.platform, target.installation, target.principal.userId, device.hash)
        return result
    }
}
