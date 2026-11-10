package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.springframework.jdbc.core.JdbcTemplate
import java.util.UUID

internal fun interface PushProviderClient {
    fun send(app: String, provider: String, token: String, content: PushContent): PushAttempt
}
internal data class PushDispatchTarget(val principal: SessionPrincipal, val app: String, val environment: String, val installation: UUID)
internal data class PushDispatchOutcome(val provider: PushProvider?, val attempt: PushAttempt)
private data class ActiveDevice(val platform: String, val provider: String, val encrypted: ByteArray, val hash: ByteArray)

/** No token is cached between attempts; ownership and active session are rechecked each time. */
internal class PushDispatcher(private val db: JdbcTemplate, private val cipher: TokenCipher, private val invalidator: PushTokenInvalidator,
                              private val provider: PushProviderClient) {
    private fun device(target: PushDispatchTarget): ActiveDevice? {
        val devices = db.query("""SELECT d.platform,d.provider,d.token_encrypted,d.token_hash FROM device_tokens d
            JOIN sessions s ON s.id=d.session_id AND s.user_id=d.user_id
            WHERE d.app_id=? AND d.environment=? AND d.installation_id=? AND d.user_id=? AND d.invalidated_at IS NULL
              AND s.revoked_at IS NULL AND s.refresh_expires_at>now()
              AND EXISTS(SELECT 1 FROM sessions requester WHERE requester.id=? AND requester.user_id=?
                         AND requester.revoked_at IS NULL AND requester.refresh_expires_at>now())""", { rs, _ ->
            ActiveDevice(rs.getString(1), rs.getString(2), rs.getBytes(3), rs.getBytes(4))
        }, target.app, target.environment, target.installation, target.principal.userId, target.principal.sessionId, target.principal.userId)
        return devices.singleOrNull()?.takeIf { (it.platform == "ANDROID" && it.provider == "FCM") || (it.platform == "IOS" && it.provider == "APNS") }
    }
    fun providerFor(target: PushDispatchTarget): PushProvider? = device(target)?.let { if (it.provider == "FCM") PushProvider.FCM else PushProvider.APNS }
    fun send(target: PushDispatchTarget, content: PushContent): PushDispatchOutcome {
        val device = device(target) ?: return PushDispatchOutcome(null, PushAttempt(PushSendResult.FAILED, PushFailure.PERMANENT))
        val token = cipher.decrypt(device.encrypted, "${target.app}:${target.environment}:${device.platform}:${target.installation}")
        val result = provider.send(target.app, device.provider, token, content)
        if (result.result == PushSendResult.INVALID_TOKEN)
            invalidator.invalidate(target.app, target.environment, device.platform, target.installation, target.principal.userId, device.hash)
        return PushDispatchOutcome(if (device.provider == "FCM") PushProvider.FCM else PushProvider.APNS, result)
    }
}
