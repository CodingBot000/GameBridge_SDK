package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.DeleteMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PutMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import java.security.MessageDigest
import java.util.UUID

internal data class DeviceRegistrationInput(@field:NotBlank @field:Size(max = 262144) val token: String,
                                            val provider: String, val platform: String) {
    override fun toString() = "DeviceRegistrationInput([redacted])"
}
@RestController
@Profile("sandbox", "production")
internal class DeviceRegistrationController(private val db: JdbcTemplate, private val cipher: TokenCipher,
                                             private val tx: TransactionTemplate, private val environment: Environment) {
    private fun mode() = if (environment.activeProfiles.contains("sandbox")) "sandbox" else "production"
    @PutMapping("/v1/devices/{installationId}/push-token")
    fun register(auth: Authentication, @PathVariable installationId: UUID, @Valid @RequestBody input: DeviceRegistrationInput): Map<String, Any> {
        if (!((input.platform == "ANDROID" && input.provider == "FCM") || (input.platform == "IOS" && input.provider == "APNS")))
            throw ResponseStatusException(HttpStatus.BAD_REQUEST)
        val principal = auth.principal as SessionPrincipal; val mode = mode()
        val hash = MessageDigest.getInstance("SHA-256").digest(input.token.toByteArray(Charsets.UTF_8))
        val count = tx.execute {
            val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now() FOR UPDATE",
                { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull() ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
            val encrypted = cipher.encrypt(input.token, "$app:$mode:${input.platform}:$installationId")
            db.update("""INSERT INTO device_tokens(app_id,environment,platform,installation_id,user_id,provider,token_encrypted,token_hash,updated_at,session_id)
                VALUES (?,?,?,?,?,?,?,?,now(),?) ON CONFLICT (app_id,environment,platform,installation_id) DO UPDATE SET
                user_id=excluded.user_id,provider=excluded.provider,token_encrypted=excluded.token_encrypted,token_hash=excluded.token_hash,updated_at=now(),session_id=excluded.session_id
                WHERE device_tokens.user_id IS NULL OR device_tokens.user_id=excluded.user_id""",
                app, mode, input.platform, installationId, principal.userId, input.provider, encrypted, hash, principal.sessionId)
        } ?: 0
        if (count != 1) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        return mapOf("provider" to input.provider, "registered" to true, "tokenFingerprint" to hash.take(6).joinToString("") { "%02x".format(it) })
    }
    @DeleteMapping("/v1/devices/{installationId}/push-token")
    fun unregister(auth: Authentication, @PathVariable installationId: UUID): Map<String, Boolean> {
        val principal = auth.principal as SessionPrincipal
        val count = tx.execute {
            val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now() FOR UPDATE",
                { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull() ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
            db.update("DELETE FROM device_tokens WHERE app_id=? AND environment=? AND installation_id=? AND user_id=?", app, mode(), installationId, principal.userId)
        } ?: 0
        if (count != 1) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        return mapOf("registered" to false)
    }
}
