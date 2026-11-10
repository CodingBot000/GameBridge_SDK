package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.stereotype.Component
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64
import java.util.UUID
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

@Component
class TokenCipher(@Value("\${SERVER_TOKEN_ENCRYPTION_KEY:}") private val configuredKey: String) {
    private fun key(): SecretKeySpec {
        val bytes = runCatching { Base64.getDecoder().decode(configuredKey) }.getOrNull()
        if (bytes == null || bytes.size != 32) throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED")
        return SecretKeySpec(bytes, "AES")
    }
    fun encrypt(value: String, associatedData: String): ByteArray {
        val nonce = ByteArray(12).also { SecureRandom().nextBytes(it) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key(), GCMParameterSpec(128, nonce))
        cipher.updateAAD(associatedData.toByteArray(StandardCharsets.UTF_8))
        return nonce + cipher.doFinal(value.toByteArray(StandardCharsets.UTF_8))
    }
}
data class MockDeviceInput(@field:NotBlank val token: String, val provider: String, val platform: String, val appId: String)
@RestController
@Profile("local-mock")
class MockDevicesController(private val db: JdbcTemplate, private val cipher: TokenCipher) {
    @PutMapping("/v1/devices/{installationId}/push-token")
    fun register(auth: Authentication, @PathVariable installationId: UUID, @Valid @RequestBody input: MockDeviceInput): Map<String, Any> {
        if (input.provider != "MOCK" || input.platform != "MOCK" || input.appId != "gamebridge-sample") throw ResponseStatusException(HttpStatus.BAD_REQUEST)
        val user = (auth.principal as SessionPrincipal).userId
        val encrypted = cipher.encrypt(input.token, "${input.appId}:local-mock:MOCK:$installationId")
        val hash = MessageDigest.getInstance("SHA-256").digest(input.token.toByteArray(StandardCharsets.UTF_8))
        val count = db.update("""INSERT INTO device_tokens(app_id,environment,platform,installation_id,user_id,provider,token_encrypted,token_hash,updated_at)
            VALUES (?, 'local-mock', 'MOCK', ?, ?, 'MOCK', ?, ?, now())
            ON CONFLICT (app_id,environment,platform,installation_id) DO UPDATE SET user_id=excluded.user_id,
              token_encrypted=excluded.token_encrypted,token_hash=excluded.token_hash,updated_at=now()
            WHERE device_tokens.user_id IS NULL OR device_tokens.user_id=excluded.user_id""", input.appId, installationId, user, encrypted, hash)
        if (count != 1) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        val fingerprint = hash.take(6).joinToString("") { "%02x".format(it) }
        return mapOf("provider" to "MOCK", "registered" to true, "tokenFingerprint" to fingerprint)
    }

}
@RestController
class PublicServiceConfigController {
    @GetMapping("/v1/config") fun config(): Map<String, Any?> = mapOf("revision" to "0", "maintenanceEnabled" to false, "message" to null, "expiresAt" to null, "source" to "DEFAULT")
}
