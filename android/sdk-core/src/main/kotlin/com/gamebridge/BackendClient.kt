package com.gamebridge

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonArray
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URI

interface TokenStore {
    fun load(): String?
    fun save(value: String)
    fun clear()
}
class BackendResponse(val requestId: String?, val json: String) {
    override fun toString() = "BackendResponse([redacted])"
}

/** Never follows redirects with credentials and never exposes raw response bodies on failure. */
class BackendClient(private val config: GameBridgeConfig) {
    init { config.validate(); require(config.mode != ProviderMode.EDITOR_OFFLINE) }
    suspend fun request(path: String, method: String, body: String? = null, accessToken: String? = null,
                        developmentKey: String? = null, idempotencyKey: String? = null): BackendResponse = withContext(Dispatchers.IO) {
        if (!path.startsWith("/v1/") || path.contains('?') || path.contains('#') || path.contains('\\') || path.contains("..") || path.contains("%")) throw SdkFailure("INVALID_ARGUMENT")
        if (method !in setOf("GET", "POST", "PUT", "DELETE")) throw SdkFailure("INVALID_ARGUMENT")
        if (developmentKey != null && (config.mode != ProviderMode.LOCAL_MOCK || path != "/v1/dev/auth")) throw SdkFailure("UNSUPPORTED_OPERATION")
        if (idempotencyKey != null && (path != "/v1/purchases/verify" || runCatching { java.util.UUID.fromString(idempotencyKey).toString() == idempotencyKey }.getOrDefault(false).not())) throw SdkFailure("INVALID_ARGUMENT")
        val base = URI(config.backendBaseUrl!!)
        val endpoint = base.resolve(path)
        if (endpoint.scheme != base.scheme || endpoint.authority != base.authority) throw SdkFailure("INVALID_ARGUMENT")
        var connection: HttpURLConnection? = null
        try {
            connection = endpoint.toURL().openConnection() as HttpURLConnection
            connection.instanceFollowRedirects = false
            connection.requestMethod = method
            val timeout = config.requestTimeoutMs.coerceAtMost(Int.MAX_VALUE.toLong()).toInt()
            connection.connectTimeout = timeout; connection.readTimeout = timeout
            connection.setRequestProperty("Accept", "application/json")
            if (accessToken != null) connection.setRequestProperty("Authorization", "Bearer $accessToken")
            if (developmentKey != null) connection.setRequestProperty("X-Development-Key", developmentKey)
            if (idempotencyKey != null) connection.setRequestProperty("Idempotency-Key", idempotencyKey)
            if (body != null) {
                connection.doOutput = true; connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            }
            val code = connection.responseCode
            if (code == 401) throw SdkFailure("SESSION_EXPIRED")
            if (code !in 200..299) throw SdkFailure(if (code in 500..599) "NETWORK_UNAVAILABLE" else "INTERNAL_ERROR")
            val data = connection.inputStream.use { input ->
                val output = ByteArrayOutputStream(); val buffer = ByteArray(8192)
                while (true) {
                    val count = input.read(buffer); if (count < 0) break
                    if (output.size() + count > 256 * 1024) throw SdkFailure("PAYLOAD_TOO_LARGE")
                    output.write(buffer, 0, count)
                }
                output.toByteArray()
            }
            val content = try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(data)).toString() }
                catch (_: java.nio.charset.CharacterCodingException) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            try { val parsed = Json.parseToJsonElement(content); if (parsed !is JsonObject && parsed !is JsonArray) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            BackendResponse(connection.getHeaderField("X-Request-Id"), content)
        } catch (_: SocketTimeoutException) { throw SdkFailure("TIMEOUT") }
        catch (_: IOException) { throw SdkFailure("NETWORK_UNAVAILABLE") }
        finally { connection?.disconnect() }
    }
}
