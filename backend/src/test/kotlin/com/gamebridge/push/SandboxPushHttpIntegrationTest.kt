package com.gamebridge.push

import com.gamebridge.auth.IdentityProvider
import com.gamebridge.auth.VerifiedIdentity
import com.gamebridge.session.SessionService
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.mockito.Mockito
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import org.springframework.test.context.bean.override.mockito.MockitoBean
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlin.test.*

/** Synthetic sender/credentials with real HTTP auth and sandbox test DB; no external push. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_AUTH_DB_TESTS", matches = "true")
class SandboxPushHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    @Autowired lateinit var sessions: SessionService
    @MockitoBean internal lateinit var providers: ConfiguredPushSenders
    companion object {
        private val installation = UUID.randomUUID()
        private const val adminKey = "test-only-push-admin-key-0123456789"
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
            registry.add("GAMEBRIDGE_DEV_PUSH_ADMIN_KEY") { adminKey }
            registry.add("GAMEBRIDGE_DEV_PUSH_ALLOWLIST") { installation.toString() }
            registry.add("SERVER_TOKEN_ENCRYPTION_KEY") { java.util.Base64.getEncoder().encodeToString(ByteArray(32) { it.toByte() }) }
            registry.add("gamebridge.push.initial-backoff-seconds") { 1L } // Test-only accelerated retry.
        }
    }
    @Test fun `manual sandbox send queues and retries fake transient response`() {
        val app = "test-" + UUID.randomUUID()
        val session = sessions.createVerified(VerifiedIdentity(IdentityProvider.GOOGLE, "https://accounts.google.com", UUID.randomUUID().toString(), "test"), app, null)
        val auth = HttpHeaders().apply { setBearerAuth(session.accessToken) }
        val registration = mapOf("token" to "synthetic-fcm-token", "provider" to "FCM", "platform" to "ANDROID")
        assertEquals(200, rest.exchange("/v1/devices/$installation/push-token", HttpMethod.PUT, HttpEntity(registration, auth), Map::class.java).statusCode.value())
        val fakeSender = Mockito.mock(FcmPushSender::class.java)
        Mockito.`when`(providers.fcm(app)).thenReturn(fakeSender)
        val calls = AtomicInteger(); val finished = CountDownLatch(2)
        val content = PushContent("message-test", "home", "title", "body")
        Mockito.`when`(fakeSender.send("synthetic-fcm-token", content)).thenAnswer {
            finished.countDown()
            if (calls.incrementAndGet() == 1) PushAttempt(PushSendResult.RETRYABLE, PushFailure.RATE_LIMIT) else PushAttempt(PushSendResult.SENT)
        }
        val headers = HttpHeaders().apply { setBearerAuth(session.accessToken); set("X-Admin-Key", adminKey) }
        val body = mapOf("installationId" to installation.toString(), "messageId" to "message-test", "route" to "home", "title" to "title", "body" to "body")
        val result = rest.exchange("/v1/dev/push/send", HttpMethod.POST, HttpEntity(body, headers), Map::class.java)
        assertEquals(200, result.statusCode.value()); assertEquals("QUEUED", result.body!!["delivery"])
        assertFalse(result.body?.toString().orEmpty().contains("synthetic-fcm-token"))
        assertTrue(finished.await(8, TimeUnit.SECONDS)); assertEquals(2, calls.get())
    }
}
