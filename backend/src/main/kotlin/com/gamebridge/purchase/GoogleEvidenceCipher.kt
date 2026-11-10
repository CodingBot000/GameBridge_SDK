package com.gamebridge.purchase

import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component
import org.springframework.web.server.ResponseStatusException
import java.security.SecureRandom
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/** Dedicated key; ciphertext is bound to app/environment/purchase identity. */
@Component
internal class GoogleEvidenceCipher(@Value("\${SERVER_PURCHASE_ENCRYPTION_KEY:}") private val encodedKey: String) {
    private fun key(): SecretKeySpec {
        val value = runCatching { Base64.getDecoder().decode(encodedKey) }.getOrNull()
        if (value == null || value.size != 32) throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED")
        return SecretKeySpec(value, "AES")
    }
    fun requireConfigured() { key() }
    fun encrypt(token: String, context: String): ByteArray {
        val nonce = ByteArray(12).also { SecureRandom().nextBytes(it) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key(), GCMParameterSpec(128, nonce))
        cipher.updateAAD(context.toByteArray(Charsets.UTF_8))
        return nonce + cipher.doFinal(token.toByteArray(Charsets.UTF_8))
    }
    fun decrypt(value: ByteArray, context: String): String {
        require(value.size >= 28)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, value.copyOfRange(0, 12)))
        cipher.updateAAD(context.toByteArray(Charsets.UTF_8))
        return String(cipher.doFinal(value.copyOfRange(12, value.size)), Charsets.UTF_8)
    }
}
