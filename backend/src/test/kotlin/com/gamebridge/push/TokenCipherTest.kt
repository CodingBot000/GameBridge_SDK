package com.gamebridge.push

import org.junit.jupiter.api.Test
import org.springframework.web.server.ResponseStatusException
import java.util.Base64
import kotlin.test.assertContentEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNotEquals
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

class TokenCipherTest {
    @Test fun `ciphertext hides token and binds associated data`() {
        val key = ByteArray(32) { it.toByte() }; val token = "mock-token-sensitive"
        val cipher = TokenCipher(Base64.getEncoder().encodeToString(key))
        val first = cipher.encrypt(token, "installation-a"); val second = cipher.encrypt(token, "installation-a")
        assertFalse(first.toString(Charsets.UTF_8).contains(token))
        assertNotEquals(first.toList(), second.toList())
        val decoder = Cipher.getInstance("AES/GCM/NoPadding")
        decoder.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), GCMParameterSpec(128, first.copyOfRange(0, 12)))
        decoder.updateAAD("installation-a".toByteArray())
        assertContentEquals(token.toByteArray(), decoder.doFinal(first.copyOfRange(12, first.size)))
        val wrong = Cipher.getInstance("AES/GCM/NoPadding")
        wrong.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), GCMParameterSpec(128, first.copyOfRange(0, 12)))
        wrong.updateAAD("installation-b".toByteArray())
        assertFailsWith<javax.crypto.AEADBadTagException> { wrong.doFinal(first.copyOfRange(12, first.size)) }
    }
    @Test fun `missing encryption key fails closed`() {
        assertFailsWith<ResponseStatusException> { TokenCipher("").encrypt("token", "context") }
    }
}
