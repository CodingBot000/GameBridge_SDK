package com.gamebridge

import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import java.net.InetSocketAddress
import java.util.concurrent.atomic.AtomicInteger
import kotlin.test.*

private class RefreshMemoryStore : TokenStore {
    var stored: String? = null
    override fun load(): String? = stored
    override fun save(value: String) { stored = value }
    override fun clear() { stored = null }
}
class LocalMockRefreshTest {
    @Test fun `logout from persisted session falls back to refresh after access expires`() = runBlocking {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val refreshRevokes = AtomicInteger()
        server.createContext("/v1/dev/auth") { exchange ->
            val body = """{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}""".toByteArray()
            exchange.sendResponseHeaders(200, body.size.toLong()); exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/v1/auth/logout") { exchange ->
            if (exchange.requestHeaders.getFirst("Authorization") != null) { exchange.sendResponseHeaders(401, -1); exchange.close() }
            else {
                val payload = exchange.requestBody.bufferedReader().readText()
                if (payload.contains("test-refresh")) refreshRevokes.incrementAndGet()
                val body = "{\"signedOut\":true}".toByteArray()
                exchange.sendResponseHeaders(200, body.size.toLong()); exchange.responseBody.use { it.write(body) }
            }
        }
        server.start()
        try {
            val config = GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:${server.address.port}")
            val store = RefreshMemoryStore(); LocalMockClient(config, store, "x".repeat(32)).signIn("A")
            LocalMockClient(config, store, "x".repeat(32)).signOut()
            assertEquals(1, refreshRevokes.get()); assertNull(store.stored)
        } finally { server.stop(0) }
    }
    @Test fun `lost refresh response leaves tombstone and cannot replay old token`() = runBlocking {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val refreshes = AtomicInteger()
        server.createContext("/v1/dev/auth") { exchange ->
            val body = """{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}""".toByteArray()
            exchange.sendResponseHeaders(200, body.size.toLong()); exchange.responseBody.use { it.write(body) }
        }
        server.createContext("/v1/entitlements") { exchange -> exchange.sendResponseHeaders(401, -1); exchange.close() }
        server.createContext("/v1/auth/refresh") { exchange -> refreshes.incrementAndGet(); Thread.sleep(500); exchange.close() }
        server.start()
        try {
            val url = "http://127.0.0.1:${server.address.port}"
            val config = GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, url, requestTimeoutMs = 100)
            val storage = RefreshMemoryStore(); val client = LocalMockClient(config, storage, "x".repeat(32))
            client.signIn("A")
            val original = storage.stored
            val wrongApp = LocalMockClient(config.copy(appId = "other"), storage, "x".repeat(32))
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { wrongApp.restore() }.code)
            assertEquals(original, storage.stored)
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { wrongApp.signOut() }.code)
            assertEquals(original, storage.stored)
            val wrongServer = LocalMockClient(config.copy(backendBaseUrl = "http://127.0.0.1:1"), storage, "x".repeat(32))
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { wrongServer.restore() }.code)
            assertEquals(original, storage.stored)
            assertEquals("TIMEOUT", assertFailsWith<SdkFailure> { client.wallet() }.code)
            assertEquals("{\"state\":\"refresh_pending\"}", storage.stored)
            assertFalse(storage.stored.orEmpty().contains("test-refresh"))
            val restarted = LocalMockClient(config, storage, "x".repeat(32))
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { restarted.restore() }.code)
            assertEquals(1, refreshes.get())
            val logout = assertFailsWith<SdkFailure> { restarted.signOut() }
            assertEquals("REVOCATION_UNCONFIRMED", logout.nativeCode); assertNull(storage.stored)
        } finally { server.stop(0) }
    }
}
