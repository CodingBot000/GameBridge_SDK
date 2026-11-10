package com.gamebridge

import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import java.net.InetSocketAddress
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.*

class LocalMockMaintenanceTest {
    @Test fun `missing or maintenance config blocks new purchase while wallet and logout continue`() = runBlocking {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val configured = AtomicBoolean(false); val verificationCalls = AtomicInteger()
        fun reply(exchange: com.sun.net.httpserver.HttpExchange, status: Int, body: String) { val data = body.toByteArray(); exchange.sendResponseHeaders(status, data.size.toLong()); exchange.responseBody.use { it.write(data) } }
        server.createContext("/v1/dev/auth") { reply(it, 200, """{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}""") }
        server.createContext("/v1/config") { if (!configured.get()) reply(it, 503, """{"code":"CONFIG_REQUIRED"}""") else reply(it, 200, """{"revision":"r","maintenanceEnabled":true,"message":null,"expiresAt":"2099-01-01T00:00:00Z"}""") }
        server.createContext("/v1/purchases/verify") { verificationCalls.incrementAndGet(); reply(it, 500, "{}") }
        server.createContext("/v1/entitlements") { reply(it, 200, """{"userId":"d2719c4e-d533-47ee-9efd-838791ea79c8","premiumEnabled":false,"coinBalance":"0","revision":"0","updatedAt":"2026-01-01T00:00:00Z"}""") }
        server.createContext("/v1/auth/logout") { reply(it, 200, """{"signedOut":true}""") }
        server.start()
        try {
            val store = object : TokenStore { var value: String? = null; override fun load() = value; override fun save(value: String) { this.value = value }; override fun clear() { value = null } }
            val client = LocalMockClient(GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:${server.address.port}"), store, "x".repeat(32))
            client.signIn("A")
            assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { client.purchase("coins_100", UUID.randomUUID(), UUID.randomUUID()) }.code)
            configured.set(true)
            assertEquals("MAINTENANCE", assertFailsWith<SdkFailure> { client.purchase("coins_100", UUID.randomUUID(), UUID.randomUUID()) }.code)
            assertEquals("0", client.wallet().coinBalance); client.signOut()
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { client.purchase("coins_100", UUID.randomUUID(), UUID.randomUUID()) }.code)
            assertEquals(0, verificationCalls.get())
        } finally { server.stop(0) }
    }
}
