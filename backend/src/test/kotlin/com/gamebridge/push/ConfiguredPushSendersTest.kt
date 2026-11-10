package com.gamebridge.push

import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import org.springframework.web.server.ResponseStatusException
import java.nio.file.Files
import java.nio.file.Path
import java.security.KeyPairGenerator
import java.security.spec.ECGenParameterSpec
import java.util.Base64
import kotlin.test.*

class ConfiguredPushSendersTest {
    @TempDir lateinit var temp: Path
    @Test fun `credentials are lazy app scoped and missing config fails closed`() {
        val mapper = ObjectMapper()
        val missing = ConfiguredPushSenders("", "", mapper)
        assertEquals(503, assertFailsWith<ResponseStatusException> { missing.fcm("app") }.statusCode.value())
        assertEquals(503, assertFailsWith<ResponseStatusException> { missing.apns("app", ApnsEnvironment.SANDBOX) }.statusCode.value())
        val generator = KeyPairGenerator.getInstance("EC"); generator.initialize(ECGenParameterSpec("secp256r1"))
        val key = generator.generateKeyPair().private.encoded // Test-only synthetic key.
        val path = temp.resolve("test-only.p8")
        Files.writeString(path, "-----BEGIN PRIVATE KEY-----\n" + Base64.getMimeEncoder(64, "\n".toByteArray()).encodeToString(key) + "\n-----END PRIVATE KEY-----\n")
        val config = mapper.writeValueAsString(mapOf("app" to mapOf("privateKeyPath" to path.toString(), "topic" to "test.bundle", "teamId" to "test-team", "keyId" to "test-key")))
        val registry = ConfiguredPushSenders("", config, mapper)
        val sandbox = registry.apns("app", ApnsEnvironment.SANDBOX)
        assertSame(sandbox, registry.apns("app", ApnsEnvironment.SANDBOX))
        assertNotSame(sandbox, registry.apns("app", ApnsEnvironment.PRODUCTION))
        assertEquals(503, assertFailsWith<ResponseStatusException> { registry.apns("other", ApnsEnvironment.SANDBOX) }.statusCode.value())
        registry.close()
    }
}
