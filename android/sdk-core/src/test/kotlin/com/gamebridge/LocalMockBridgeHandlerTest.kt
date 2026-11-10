package com.gamebridge

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import kotlinx.serialization.json.*
import java.net.InetSocketAddress
import java.util.UUID
import kotlin.test.*

class LocalMockBridgeHandlerTest {
    @Test fun `bridge performs authenticated mock purchase without exposing credentials`() {
        val user = "d2719c4e-d533-47ee-9efd-838791ea79c8"
        val key = "test-only-development-key-0123456789"
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        var purchases = 0
        val configured = java.util.concurrent.atomic.AtomicBoolean(false)
        val wallet = """{"userId":"$user","premiumEnabled":false,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}"""
        fun reply(exchange: HttpExchange, body: String) {
            val bytes = body.toByteArray(); exchange.sendResponseHeaders(200, bytes.size.toLong())
            exchange.responseBody.use { it.write(bytes) }
        }
        server.createContext("/v1/dev/auth") { e ->
            assertEquals(key, e.requestHeaders.getFirst("X-Development-Key"))
            reply(e, """{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2099-01-01T00:00:00Z","userId":"$user"}""")
        }
        server.createContext("/v1/config") { e ->
            if (configured.get()) reply(e, """{"revision":"1","maintenanceEnabled":false,"message":null,"expiresAt":"2099-01-01T00:00:00Z"}""")
            else { val bytes = """{"code":"CONFIG_REQUIRED"}""".toByteArray(); e.sendResponseHeaders(503, bytes.size.toLong()); e.responseBody.use { it.write(bytes) } }
        }
        server.createContext("/v1/purchases/verify") { e ->
            assertEquals("Bearer test-access", e.requestHeaders.getFirst("Authorization"))
            assertNotNull(e.requestHeaders.getFirst("Idempotency-Key")); purchases++
            reply(e, """{"serverPurchaseId":"d2719c4e-d533-47ee-9efd-838791ea79c8","fulfillmentStatus":"GRANTED","finalizationStatus":"NOT_REQUIRED","entitlements":$wallet}""")
        }
        server.createContext("/v1/entitlements") { e -> reply(e, wallet) }
        server.createContext("/v1/auth/logout") { e -> reply(e, "{}") }
        server.start()
        try {
            var saved: String? = null
            val store = object : TokenStore {
                override fun load() = saved
                override fun save(value: String) { saved = value }
                override fun clear() { saved = null }
            }
            var pendingValue: String? = null
            val pending = object : TokenStore {
                override fun load() = pendingValue
                override fun save(value: String) { pendingValue = value }
                override fun clear() { pendingValue = null }
            }
            val dispatcher = BridgeDispatcher(LocalMockBridgeHandler({ store }, { pending }))
            val session = UUID.randomUUID().toString()
            fun request(operation: String, payload: JsonObject = buildJsonObject {}, id: String = session): JsonObject {
                val envelope = buildJsonObject {
                    put("protocolVersion", 1); put("sdkSessionId", id); put("kind", "request")
                    put("requestId", UUID.randomUUID().toString()); put("operation", operation); put("payload", payload)
                }
                val response = dispatcher.dispatch(envelope.toString().toByteArray()) as BridgeDispatchResult.Message
                assertFalse(response.json.contains(key)); assertFalse(response.json.contains("test-access")); assertFalse(response.json.contains("test-refresh"))
                return BridgeProtocol.parse(response.json.toByteArray())
            }
            val init = request("sdk.initialize", buildJsonObject {
                put("appId", "gamebridge-sample"); put("providerMode", "LOCAL_MOCK"); put("backendBaseUrl", "http://127.0.0.1:${server.address.port}")
                put("requestTimeoutMs", 30000); put("developmentKey", key); put("mockSubject", "A")
            })
            assertTrue(init.getValue("ok").jsonPrimitive.boolean)
            assertEquals("CONFIG_REQUIRED", request("config.get").getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
            configured.set(true)
            assertEquals("NETWORK", request("config.get").getValue("result").jsonObject.getValue("source").jsonPrimitive.content)
            configured.set(false)
            assertEquals("CACHE", request("config.get").getValue("result").jsonObject.getValue("source").jsonPrimitive.content)
            configured.set(true)
            assertTrue(request("auth.signIn", buildJsonObject { put("provider", "MOCK") }).getValue("ok").jsonPrimitive.boolean)
            val result = request("store.purchase", buildJsonObject { put("productId", "coins_100") })
            assertEquals("GRANTED", result.getValue("result").jsonObject.getValue("fulfillmentStatus").jsonPrimitive.content)
            assertEquals(1, purchases)
            assertEquals("100", request("store.entitlements").getValue("result").jsonObject.getValue("coinBalance").jsonPrimitive.content)
            val sync = request("store.sync", buildJsonObject { put("reason", "APP_RESUME") }).getValue("result").jsonObject
            assertEquals(0, sync.getValue("examinedCount").jsonPrimitive.int)
            assertEquals("100", sync.getValue("entitlements").jsonObject.getValue("coinBalance").jsonPrimitive.content)
            assertEquals("NOT_INITIALIZED", request("store.entitlements", id = UUID.randomUUID().toString()).getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
            request("auth.signOut"); assertNull(saved)
            dispatcher.reset()
            assertEquals("NOT_INITIALIZED", request("store.entitlements").getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
            val fresh = request("sdk.initialize", buildJsonObject {
                put("appId", "gamebridge-sample"); put("providerMode", "LOCAL_MOCK"); put("backendBaseUrl", "http://127.0.0.1:${server.address.port}")
                put("requestTimeoutMs", 30000); put("developmentKey", key); put("mockSubject", "A")
            }, UUID.randomUUID().toString())
            assertTrue(fresh.getValue("ok").jsonPrimitive.boolean)
        } finally { server.stop(0) }
    }
    @Test fun `registered local push starts native stream and shuts down on logout`() {
        val user = UUID.randomUUID().toString(); val id = UUID.randomUUID(); val seen = java.util.concurrent.CountDownLatch(1)
        val messages = java.util.concurrent.CopyOnWriteArrayList<PushPayload>()
        val releaseStream = java.util.concurrent.CountDownLatch(1)
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.executor = java.util.concurrent.Executors.newCachedThreadPool { r -> Thread(r).apply { isDaemon = true } }
        fun reply(e: HttpExchange, body: String) { val bytes = body.toByteArray(); e.sendResponseHeaders(200, bytes.size.toLong()); e.responseBody.use { it.write(bytes) } }
        server.createContext("/v1/dev/auth") { e -> reply(e, """{"accessToken":"test-access","refreshToken":"test-refresh","expiresAt":"2099-01-01T00:00:00Z","userId":"$user"}""") }
        server.createContext("/v1/me") { e -> reply(e, """{"userId":"$user"}""") }
        server.createContext("/v1/devices/") { e -> reply(e, """{"provider":"MOCK","registered":true,"tokenFingerprint":"abcdef123456"}""") }
        server.createContext("/v1/auth/logout") { e -> reply(e, "{}") }
        server.createContext("/v1/dev/push/stream") { e ->
            assertEquals("Bearer test-access", e.requestHeaders.getFirst("Authorization"))
            e.sendResponseHeaders(200, 0)
            e.responseBody.use { output ->
                output.write("event:push\ndata:{\"messageId\":\"stream-one\",\"route\":\"home\"}\n\n".toByteArray()); output.flush()
                releaseStream.await(5, java.util.concurrent.TimeUnit.SECONDS)
            }
        }
        server.start()
        try {
            var saved: String? = null
            val store = object : TokenStore { override fun load() = saved; override fun save(value: String) { saved = value }; override fun clear() { saved = null } }
            val handler = LocalMockBridgeHandler { store }
            handler.setMockPushSinkFactory { { payload -> messages.add(payload); seen.countDown() } }
            handler.invoke("sdk.initialize", buildJsonObject { put("appId", "gamebridge-sample"); put("providerMode", "LOCAL_MOCK");
                put("backendBaseUrl", "http://127.0.0.1:${server.address.port}"); put("requestTimeoutMs", 30000); put("developmentKey", "test-only-development-key-0123456789"); put("mockSubject", "A"); put("installationId", id.toString()) })
            handler.invoke("auth.signIn", buildJsonObject { put("provider", "MOCK") })
            handler.invoke("push.register", buildJsonObject {})
            assertTrue(seen.await(5, java.util.concurrent.TimeUnit.SECONDS))
            assertEquals(PushPayload("stream-one", "home", null), messages.single())
            val logout = java.util.concurrent.CompletableFuture.runAsync { handler.invoke("auth.signOut", buildJsonObject {}) }
            try { logout.get(2, java.util.concurrent.TimeUnit.SECONDS) } finally { releaseStream.countDown() }
            assertNull(saved)
            handler.invoke("sdk.shutdown", buildJsonObject {})
        } finally { releaseStream.countDown(); server.stop(0) }
    }

}
