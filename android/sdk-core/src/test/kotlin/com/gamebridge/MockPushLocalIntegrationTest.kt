package com.gamebridge

import kotlinx.serialization.json.*
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.test.*

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_MOCK_PUSH_E2E", matches = "true")
class MockPushLocalIntegrationTest {
    @Test fun `local backend delivers push to registered Android native handler`() {
        val base = requireNotNull(System.getenv("GAMEBRIDGE_PUSH_E2E_BASE_URL"))
        require(base.startsWith("http://127.0.0.1:"))
        val key = requireNotNull(System.getenv("GAMEBRIDGE_PUSH_E2E_AUTH_KEY")); val admin = requireNotNull(System.getenv("GAMEBRIDGE_PUSH_E2E_ADMIN_KEY"))
        val installation = requireNotNull(System.getenv("GAMEBRIDGE_PUSH_E2E_INSTALLATION")); UUID.fromString(installation)
        fun post(path: String, body: String, headers: Map<String,String>): JsonObject {
            val c = URL(base + path).openConnection() as HttpURLConnection
            try { c.requestMethod = "POST"; c.connectTimeout = 5000; c.readTimeout = 5000; c.doOutput = true
                c.setRequestProperty("Content-Type", "application/json"); headers.forEach(c::setRequestProperty)
                c.outputStream.use { it.write(body.toByteArray()) }; assertEquals(200, c.responseCode)
                return Json.parseToJsonElement(c.inputStream.bufferedReader().use { it.readText() }).jsonObject
            } finally { c.disconnect() }
        }
        val sender = post("/v1/dev/auth", """{"subject":"A"}""", mapOf("X-Development-Key" to key))["accessToken"]!!.jsonPrimitive.content
        var saved: String? = null
        val store = object : TokenStore { override fun load() = saved; override fun save(value: String) { saved = value }; override fun clear() { saved = null } }
        val handler = LocalMockBridgeHandler { store }; val seen = CountDownLatch(1); val received = java.util.concurrent.CopyOnWriteArrayList<PushPayload>()
        handler.setMockPushSinkFactory { { payload -> received.add(payload); seen.countDown() } }
        try {
            handler.invoke("sdk.initialize", buildJsonObject { put("appId", "gamebridge-sample"); put("providerMode", "LOCAL_MOCK"); put("backendBaseUrl", base)
                put("requestTimeoutMs", 5000); put("developmentKey", key); put("mockSubject", "A"); put("installationId", installation) })
            handler.invoke("auth.signIn", buildJsonObject { put("provider", "MOCK") }); handler.invoke("push.register", buildJsonObject {})
            for (attempt in 1..4) {
                Thread.sleep(500)
                val payload = buildJsonObject { put("installationId", installation); put("messageId", "android-e2e-$attempt"); put("route", "home"); put("title", "test"); put("body", "test") }
                post("/v1/dev/push/send", payload.toString(), mapOf("Authorization" to "Bearer $sender", "X-Admin-Key" to admin))
                if (seen.await(500, TimeUnit.MILLISECONDS)) break
            }
            assertEquals(0, seen.count); assertEquals("home", received.first().route)
            handler.invoke("auth.signOut", buildJsonObject {}); assertNull(saved)
        } finally { handler.invoke("sdk.shutdown", buildJsonObject {}) }
    }
}
