package com.gamebridge

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*
import java.net.InetSocketAddress
import java.util.UUID
import kotlin.test.*

class LocalMockRecoveryTest {
    @Test fun `lost response recovers same transaction only for original user`() = runBlocking {
        val userA = "d2719c4e-d533-47ee-9efd-838791ea79c8"
        val userB = "a2719c4e-d533-47ee-9efd-838791ea79c8"
        val purchaseId = "b2719c4e-d533-47ee-9efd-838791ea79c8"
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val attempts = mutableListOf<Pair<String, String>>()
        val maintenance = java.util.concurrent.atomic.AtomicBoolean(false)
        fun reply(e: HttpExchange, status: Int, text: String) { val bytes = text.toByteArray(); e.sendResponseHeaders(status, bytes.size.toLong()); e.responseBody.use { it.write(bytes) } }
        server.createContext("/v1/dev/auth") { e ->
            val subject = Json.parseToJsonElement(e.requestBody.bufferedReader().readText()).jsonObject.getValue("subject").jsonPrimitive.content
            val user = if (subject == "A") userA else userB
            reply(e, 200, """{"accessToken":"access-$subject","refreshToken":"refresh-$subject","expiresAt":"2099-01-01T00:00:00Z","userId":"$user"}""")
        }
        server.createContext("/v1/me") { e ->
            val user = if (e.requestHeaders.getFirst("Authorization") == "Bearer access-A") userA else userB
            reply(e, 200, """{"userId":"$user"}""")
        }
        server.createContext("/v1/config") { e -> reply(e, 200, """{"revision":"1","maintenanceEnabled":${maintenance.get()},"message":null,"expiresAt":"2099-01-01T00:00:00Z"}""") }
        server.createContext("/v1/auth/logout") { e -> reply(e, 200, "{}") }
        server.createContext("/v1/purchases/verify") { e ->
            val key = e.requestHeaders.getFirst("Idempotency-Key")
            val proof = Json.parseToJsonElement(e.requestBody.bufferedReader().readText()).jsonObject.getValue("proof").jsonPrimitive.content
            attempts.add(key to proof)
            if (attempts.size == 1) reply(e, 503, """{"code":"NETWORK_UNAVAILABLE"}""")
            else reply(e, 200, """{"serverPurchaseId":"$purchaseId","fulfillmentStatus":"ALREADY_GRANTED","finalizationStatus":"PENDING","entitlements":{"userId":"$userA","premiumEnabled":false,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}}""")
        }
        server.start()
        try {
            class Memory : TokenStore { var value: String? = null; override fun load() = value; override fun save(value: String) { this.value = value }; override fun clear() { value = null } }
            val sessions = Memory(); val pending = Memory()
            val config = GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:${server.address.port}")
            assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { LocalMockClient(config, sessions, "x".repeat(32), sessions) }.code)
            val original = LocalMockClient(config, sessions, "x".repeat(32), pending)
            original.signIn("A")
            assertEquals("NETWORK_UNAVAILABLE", assertFailsWith<SdkFailure> { original.purchase("coins_100", UUID.randomUUID(), UUID.randomUUID()) }.code)
            assertNotNull(pending.value); assertFalse(pending.value!!.contains("access-A")); assertFalse(pending.value!!.contains("mock:"))
            original.signOut()
            val other = LocalMockClient(config, sessions, "x".repeat(32), pending); other.signIn("B")
            assertEquals(LocalRecoveryCounts(0, 0, 0, 0), other.recoverPending()); assertNotNull(pending.value); other.signOut()
            val restarted = LocalMockClient(config, sessions, "x".repeat(32), pending); restarted.signIn("A")
            maintenance.set(true)
            assertEquals("MAINTENANCE", assertFailsWith<SdkFailure> { restarted.purchase("coins_100", UUID.randomUUID(), UUID.randomUUID()) }.code)
            assertEquals(1, attempts.size)
            assertEquals(LocalRecoveryCounts(1, 1, 0, 0), restarted.recoverPending()); assertNull(pending.value)
            assertEquals(2, attempts.size); assertEquals(attempts[0], attempts[1]); restarted.signOut()
        } finally { server.stop(0) }
    }
}
