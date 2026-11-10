package com.gamebridge.push

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import java.util.UUID
import kotlin.test.*

/** Dedicated local DB and test-only keys; sends no remote messages. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("local-mock")
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class DevPushHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    @org.springframework.boot.test.web.server.LocalServerPort var port: Int = 0
    companion object {
        private val installation = UUID.randomUUID()
        private const val authKey = "test-only-development-key-0123456789"
        private const val adminKey = "test-only-push-admin-key-0123456789"
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
            registry.add("GAMEBRIDGE_DEV_AUTH_KEY") { authKey }
            registry.add("GAMEBRIDGE_DEV_PUSH_ADMIN_KEY") { adminKey }
            registry.add("GAMEBRIDGE_DEV_PUSH_ALLOWLIST") { installation.toString() }
            registry.add("SERVER_TOKEN_ENCRYPTION_KEY") { java.util.Base64.getEncoder().encodeToString(ByteArray(32) { it.toByte() }) }
        }
    }
    @Test fun `dev push requires auth admin allowlist ownership and enforces rolling limit`() {
        fun login(subject: String): String {
            val headers = HttpHeaders().apply { set("X-Development-Key", authKey) }
            val response = rest.exchange("/v1/dev/auth", HttpMethod.POST, HttpEntity(mapOf("subject" to subject), headers), Map::class.java)
            assertEquals(200, response.statusCode.value()); return response.body!!["accessToken"] as String
        }
        val a = login("A"); val b = login("B")
        val owner = HttpHeaders().apply { setBearerAuth(a) }
        val register = mapOf("token" to "synthetic-token", "provider" to "MOCK", "platform" to "MOCK", "appId" to "gamebridge-sample")
        assertEquals(200, rest.exchange("/v1/devices/$installation/push-token", HttpMethod.PUT, HttpEntity(register, owner), Map::class.java).statusCode.value())
        val payload = mapOf("installationId" to installation.toString(), "messageId" to "test-message", "route" to "home", "title" to "test", "body" to "test")
        fun send(token: String?, key: String?, value: Map<String, String> = payload) = rest.exchange("/v1/dev/push/send", HttpMethod.POST,
            HttpEntity(value, HttpHeaders().apply { if (token != null) setBearerAuth(token); if (key != null) set("X-Admin-Key", key) }), Map::class.java)
        assertEquals(401, send(null, adminKey).statusCode.value())
        assertEquals(403, send(a, "wrong-key").statusCode.value())
        assertEquals(403, send(a, adminKey, payload + ("installationId" to UUID.randomUUID().toString())).statusCode.value())
        assertEquals(400, send(a, adminKey, payload + ("route" to "https://invalid.example")).statusCode.value())
        assertEquals(403, send(b, adminKey).statusCode.value()) // Authenticated but not the installation owner; consumes one slot.
        val accepted = send(a, adminKey); assertEquals(200, accepted.statusCode.value()); assertEquals("SIMULATED", accepted.body!!["delivery"])
        repeat(8) { assertEquals(200, send(a, adminKey).statusCode.value()) }
        val limited = send(a, adminKey); assertEquals(429, limited.statusCode.value()); assertEquals("BUSY", limited.body!!["code"]); assertEquals(true, limited.body!!["retryable"])
    }
    @Test fun `local push stream delivers only while registered session is connected`() {
        fun login(subject: String): String {
            val headers = HttpHeaders().apply { set("X-Development-Key", authKey) }
            return rest.exchange("/v1/dev/auth", HttpMethod.POST, HttpEntity(mapOf("subject" to subject), headers), Map::class.java).body!!["accessToken"] as String
        }
        val a = login("A"); val b = login("B")
        val owner = HttpHeaders().apply { setBearerAuth(a) }
        val register = mapOf("token" to "synthetic-stream-token", "provider" to "MOCK", "platform" to "MOCK", "appId" to "gamebridge-sample")
        assertEquals(200, rest.exchange("/v1/devices/$installation/push-token", HttpMethod.PUT, HttpEntity(register, owner), Map::class.java).statusCode.value())
        val http = java.net.http.HttpClient.newHttpClient()
        fun request(token: String) = java.net.http.HttpRequest.newBuilder(java.net.URI("http://127.0.0.1:$port/v1/dev/push/stream?installationId=$installation"))
            .header("Authorization", "Bearer $token").GET().build()
        val forbidden = http.send(request(b), java.net.http.HttpResponse.BodyHandlers.discarding())
        assertEquals(403, forbidden.statusCode())
        val connected = http.send(request(a), java.net.http.HttpResponse.BodyHandlers.ofInputStream())
        assertEquals(200, connected.statusCode())
        val reader = connected.body().bufferedReader()
        assertEquals("event:ready", reader.readLine()); assertEquals("data:connected", reader.readLine()); assertEquals("", reader.readLine())
        val payload = mapOf("installationId" to installation.toString(), "messageId" to "stream-test", "route" to "home", "title" to "secret-title", "body" to "secret-body")
        val headers = HttpHeaders().apply { setBearerAuth(a); set("X-Admin-Key", adminKey) }
        val sent = rest.exchange("/v1/dev/push/send", HttpMethod.POST, HttpEntity(payload, headers), Map::class.java)
        assertEquals(200, sent.statusCode.value())
        assertEquals("event:push", reader.readLine())
        val data = reader.readLine(); assertTrue(data.contains("stream-test")); assertFalse(data.contains("secret-title")); assertFalse(data.contains("secret-body"))
        reader.close()
    }

}
