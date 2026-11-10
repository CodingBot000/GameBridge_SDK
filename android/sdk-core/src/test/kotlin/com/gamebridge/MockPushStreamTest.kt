package com.gamebridge

import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.test.*

class MockPushStreamTest {
    @Test fun `local stream accepts authenticated push and ignores other data`() {
        val received = mutableListOf<PushPayload>(); val done = CountDownLatch(1); val install = UUID.randomUUID()
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/v1/dev/push/stream") { exchange ->
            assertEquals("Bearer synthetic-token", exchange.requestHeaders.getFirst("Authorization"))
            assertEquals("installationId=$install", exchange.requestURI.rawQuery)
            val bytes = (":heartbeat\n\nevent:push\ndata:{\"messageId\":\"one\",\"route\":\"home\",\"token\":\"ignored\"}\n\n").toByteArray()
            exchange.sendResponseHeaders(200, bytes.size.toLong()); exchange.responseBody.use { it.write(bytes) }
        }
        server.start()
        val stream = MockPushStream("http://127.0.0.1:${server.address.port}", install, { "synthetic-token" }) { synchronized(received) { received.add(it) }; done.countDown() }
        try { stream.start(); assertTrue(done.await(5, TimeUnit.SECONDS)); assertEquals(PushPayload("one", "home", null), synchronized(received) { received.single() }) }
        finally { stream.stop(); server.stop(0) }
    }
}
