package com.gamebridge

import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import java.net.InetSocketAddress
import kotlin.test.*

class BackendClientTest {
    @Test fun `http response authentication and invalid json are mapped`() = runBlocking {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/v1/ok") { e -> val body = "{\"ok\":true}".toByteArray(); e.responseHeaders.add("X-Request-Id", "request-test"); e.sendResponseHeaders(200, body.size.toLong()); e.responseBody.use { it.write(body) } }
        server.createContext("/v1/unauthorized") { e -> e.sendResponseHeaders(401, -1); e.close() }
        server.createContext("/v1/bad") { e -> val body = "bad".toByteArray(); e.sendResponseHeaders(200, body.size.toLong()); e.responseBody.use { it.write(body) } }
        server.createContext("/v1/conflict") { e -> val body = "{\"code\":\"PURCHASE_ACCOUNT_MISMATCH\",\"message\":\"secret-token\"}".toByteArray(); e.sendResponseHeaders(409, body.size.toLong()); e.responseBody.use { it.write(body) } }
        server.createContext("/v1/limited") { e -> val body = "{\"code\":\"secret-token\"}".toByteArray(); e.sendResponseHeaders(429, body.size.toLong()); e.responseBody.use { it.write(body) } }
        server.createContext("/v1/auth-failure") { e -> val body = "{\"code\":\"AUTH_FAILED\"}".toByteArray(); e.sendResponseHeaders(401, body.size.toLong()); e.responseBody.use { it.write(body) } }
        server.createContext("/v1/slow") { e -> Thread.sleep(200); e.close() }
        server.start()
        try {
            val client = BackendClient(GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:${server.address.port}"))
            val response = client.request("/v1/ok", "GET")
            assertEquals("request-test", response.requestId)
            assertFalse(response.toString().contains("ok"))
            assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { client.request("/v1/unauthorized", "GET") }.code)
            assertEquals("BRIDGE_PROTOCOL_MISMATCH", assertFailsWith<SdkFailure> { client.request("/v1/bad", "GET") }.code)
            assertEquals("INVALID_ARGUMENT", assertFailsWith<SdkFailure> { client.request("/v1/../evil", "GET") }.code)
            val conflict = assertFailsWith<SdkFailure> { client.request("/v1/conflict", "GET") }
            assertEquals("PURCHASE_ACCOUNT_MISMATCH", conflict.code); assertFalse(conflict.toString().contains("secret-token"))
            val limited = assertFailsWith<SdkFailure> { client.request("/v1/limited", "GET") }
            assertEquals("BUSY", limited.code); assertTrue(limited.retryable)
            assertEquals("AUTH_FAILED", assertFailsWith<SdkFailure> { client.request("/v1/auth-failure", "GET") }.code)
            val shortTimeout = BackendClient(GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:${server.address.port}", requestTimeoutMs = 20))
            assertEquals("TIMEOUT", assertFailsWith<SdkFailure> { shortTimeout.request("/v1/slow", "GET") }.code)
        } finally { server.stop(0) }
    }
}
