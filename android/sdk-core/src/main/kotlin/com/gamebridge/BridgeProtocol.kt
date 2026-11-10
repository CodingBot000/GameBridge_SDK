package com.gamebridge

import java.util.UUID
import kotlinx.serialization.json.*

/** Validation only; does not invoke methods named by untrusted input. */
object BridgeProtocol {
    const val MAX_BYTES = 256 * 1024
    private val operations = setOf(
        "sdk.initialize", "sdk.status", "sdk.capabilities", "auth.signIn", "auth.signOut", "auth.restore",
        "store.products", "store.purchase", "store.entitlements", "store.sync", "push.permission", "push.register",
        "push.unregister", "config.get", "diagnostics.get", "sdk.shutdown", "host.pushToken", "host.pushReceived",
        "host.pushOpened", "host.lifecycle",
    )
    class ProtocolException(val code: String) : IllegalArgumentException(code)
    private fun fail(): Nothing = throw ProtocolException("BRIDGE_PROTOCOL_MISMATCH")
    private fun JsonObject.requiredString(key: String): String =
        (this[key] as? JsonPrimitive)?.takeIf { it.isString }?.content ?: fail()
    private fun uuid(s: String) { if (runCatching { UUID.fromString(s).toString() == s.lowercase() }.getOrDefault(false).not()) fail() }

    fun parse(bytes: ByteArray, expectedSession: String? = null, expectedRequest: String? = null): JsonObject {
        if (bytes.size > MAX_BYTES) throw ProtocolException("PAYLOAD_TOO_LARGE")
        val text = try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(bytes)).toString() } catch (_: Exception) { fail() }
        val obj = try { Json.parseToJsonElement(text) as? JsonObject ?: fail() } catch (_: Exception) { fail() }
        if (obj["protocolVersion"] != JsonPrimitive(1)) fail()
        val session = obj.requiredString("sdkSessionId"); uuid(session)
        if (expectedSession != null && session != expectedSession) fail()
        when (obj.requiredString("kind")) {
            "request", "response" -> {
                val request = obj.requiredString("requestId"); uuid(request)
                if (expectedRequest != null && request != expectedRequest) fail()
                if (obj.requiredString("operation") !in operations) fail()
                if (obj["kind"] == JsonPrimitive("request")) {
                    if (obj["payload"] !is JsonObject) fail()
                } else {
                    val ok = (obj["ok"] as? JsonPrimitive)?.booleanOrNull ?: fail()
                    if (!obj.containsKey("result") || !obj.containsKey("error")) fail()
                    if (ok && obj["error"] != JsonNull) fail()
                    if (!ok && (obj["result"] != JsonNull || obj["error"] !is JsonObject)) fail()
                }
            }
            "event" -> { uuid(obj.requiredString("eventId")); if (obj["payload"] !is JsonObject) fail() }
            else -> fail()
        }
        return obj
    }
}
