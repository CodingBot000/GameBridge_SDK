package com.gamebridge

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonPrimitive
import java.io.InputStream
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URI

/** Implementations must atomically replace the complete value and keep it encrypted at rest. */
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
        if (idempotencyKey != null && (path !in setOf("/v1/purchases/verify", "/v1/purchases/google/verify") || runCatching { java.util.UUID.fromString(idempotencyKey).toString() == idempotencyKey }.getOrDefault(false).not())) throw SdkFailure("INVALID_ARGUMENT")
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
            if (code !in 200..299) {
                val data = connection.errorStream?.use { readBounded(it) } ?: ByteArray(0)
                throw failure(code, data)
            }
            val data = connection.inputStream.use { readBounded(it) }
            val content = try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(data)).toString() }
                catch (_: java.nio.charset.CharacterCodingException) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            try { val parsed = Json.parseToJsonElement(content); if (parsed !is JsonObject && parsed !is JsonArray) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            BackendResponse(connection.getHeaderField("X-Request-Id"), content)
        } catch (_: SocketTimeoutException) { throw SdkFailure("TIMEOUT", retryable = true) }
        catch (_: IOException) { throw SdkFailure("NETWORK_UNAVAILABLE", retryable = true) }
        finally { connection?.disconnect() }
    }
    private fun readBounded(input: InputStream): ByteArray {
        val output = ByteArrayOutputStream(); val buffer = ByteArray(8192)
        while (true) {
            val count = input.read(buffer); if (count < 0) break
            if (output.size() + count > 256 * 1024) throw SdkFailure("PAYLOAD_TOO_LARGE")
            output.write(buffer, 0, count)
        }
        return output.toByteArray()
    }
    private fun failure(status: Int, data: ByteArray): SdkFailure {
        val serverCode = runCatching {
            val value = (Json.parseToJsonElement(data.toString(Charsets.UTF_8)) as? JsonObject)?.get("code") as? JsonPrimitive
            value?.takeIf { it.isString }?.content
        }.getOrNull()
        val allowed = when (status) {
            400 -> setOf("INVALID_ARGUMENT", "VERIFICATION_FAILED")
            401 -> setOf("AUTH_FAILED", "SESSION_EXPIRED")
            403 -> setOf("PERMISSION_DENIED")
            404 -> setOf("UNSUPPORTED_OPERATION", "PRODUCT_NOT_FOUND")
            409 -> setOf("AUTH_REPLAY_DETECTED", "PURCHASE_ACCOUNT_MISMATCH", "IDEMPOTENCY_CONFLICT")
            413 -> setOf("PAYLOAD_TOO_LARGE")
            429 -> setOf("BUSY")
            503 -> setOf("CONFIG_REQUIRED", "NETWORK_UNAVAILABLE")
            else -> emptySet()
        }
        val fallback = when (status) {
            400 -> "INVALID_ARGUMENT"; 401 -> "SESSION_EXPIRED"; 403 -> "PERMISSION_DENIED"; 404 -> "UNSUPPORTED_OPERATION"
            413 -> "PAYLOAD_TOO_LARGE"; 429 -> "BUSY"; in 500..599 -> "NETWORK_UNAVAILABLE"; else -> "INTERNAL_ERROR"
        }
        val code = serverCode?.takeIf { it in allowed } ?: fallback
        return SdkFailure(code, retryable = code == "BUSY" || code == "NETWORK_UNAVAILABLE")
    }
}
