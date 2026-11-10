package com.gamebridge

import kotlinx.coroutines.*
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URI
import java.util.UUID

/** LOCAL_MOCK only. One cancellable connection; never logs tokens or raw messages. */
internal class MockPushStream(private val baseUrl: String, private val installationId: UUID,
                              private val token: suspend () -> String?, private val onPush: (PushPayload) -> Unit) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @Volatile private var connection: HttpURLConnection? = null
    fun start() { scope.launch {
        var retry = 5_000L
        while (isActive) {
            try {
                val credential = token() ?: break
                ensureActive()
                val base = URI(baseUrl)
                val endpoint = base.resolve("/v1/dev/push/stream?installationId=$installationId")
                if (endpoint.scheme != base.scheme || endpoint.authority != base.authority) break
                val current = endpoint.toURL().openConnection() as HttpURLConnection
                connection = current
                try {
                    ensureActive()
                    current.instanceFollowRedirects = false; current.requestMethod = "GET"
                    current.connectTimeout = 30_000; current.readTimeout = 90_000
                    current.setRequestProperty("Authorization", "Bearer $credential")
                    current.setRequestProperty("Accept", "text/event-stream, application/json")
                    if (current.responseCode == 200) {
                        retry = 5_000L
                        current.inputStream.use { consume(it) }
                    }
                } finally { connection = null; current.disconnect() }
            } catch (cancel: CancellationException) { throw cancel }
            catch (_: Exception) { /* retry without exposing token or response */ }
            delay(retry); retry = (retry * 2).coerceAtMost(60_000L)
        }
    } }
    fun stop() {
        scope.cancel()
        val current = connection; connection = null
        if (current != null) Thread({ current.disconnect() }, "gamebridge-mock-push-disconnect").apply { isDaemon = true; start() }
    }
    private fun consume(input: InputStream) {
        var event: String? = null; var data: String? = null
        while (scope.isActive) {
            val line = boundedLine(input) ?: return
            if (line.isEmpty()) {
                if (event == "push" && data != null) MockPushEventDecoder.decode(data.toByteArray(Charsets.UTF_8))?.let(onPush)
                event = null; data = null
            } else if (line.startsWith("event:")) event = line.substring(6).trimStart()
            else if (line.startsWith("data:")) {
                if (data != null) return // no multi-line or oversized accumulation
                data = line.substring(5).trimStart()
            }
        }
    }
    private fun boundedLine(input: InputStream): String? {
        val out = ByteArrayOutputStream()
        while (true) {
            val next = input.read()
            if (next < 0) return null
            if (next == 10) break
            if (out.size() >= BridgeProtocol.MAX_BYTES) return null
            if (next != 13) out.write(next)
        }
        return try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(out.toByteArray())).toString() } catch (_: Exception) { null }
    }
}
