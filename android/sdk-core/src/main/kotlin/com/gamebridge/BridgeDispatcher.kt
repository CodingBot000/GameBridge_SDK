package com.gamebridge

import kotlinx.serialization.json.*

sealed interface BridgeDispatchResult {
    data class Message(val json: String) : BridgeDispatchResult
    data class Rejected(val code: String) : BridgeDispatchResult
}

/** A narrow operation allowlist; unsupported functions never return fake success. */
class BridgeDispatcher {
    private var state = "UNINITIALIZED"
    @Synchronized
    fun dispatch(bytes: ByteArray): BridgeDispatchResult {
        val request = parseRequest(bytes) ?: return rejection(bytes)
        val operation = request.getValue("operation").jsonPrimitive.content
        val result = if (operation == "sdk.status") buildJsonObject {
            put("state", state); put("sdkVersion", GameBridgeVersion.CURRENT)
        } else if (operation == "sdk.shutdown") {
            state = "SHUTDOWN"; buildJsonObject { put("state", state) }
        } else null
        return response(request, result, if (result == null) "UNSUPPORTED_OPERATION" else null)
    }
    fun busy(bytes: ByteArray): BridgeDispatchResult {
        val request = parseRequest(bytes) ?: return rejection(bytes)
        return response(request, null, "BUSY")
    }
    private fun parseRequest(bytes: ByteArray): JsonObject? = try {
        BridgeProtocol.parse(bytes).takeIf { it["kind"] == JsonPrimitive("request") }
    } catch (_: BridgeProtocol.ProtocolException) { null }
    private fun rejection(bytes: ByteArray): BridgeDispatchResult = try {
        BridgeProtocol.parse(bytes); BridgeDispatchResult.Rejected("BRIDGE_PROTOCOL_MISMATCH")
    } catch (error: BridgeProtocol.ProtocolException) { BridgeDispatchResult.Rejected(error.code) }
    private fun response(request: JsonObject, result: JsonObject?, errorCode: String?): BridgeDispatchResult.Message {
        val operation = request.getValue("operation").jsonPrimitive.content
        return BridgeDispatchResult.Message(buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", request.getValue("sdkSessionId")); put("kind", "response")
            put("requestId", request.getValue("requestId")); put("operation", operation); put("ok", errorCode == null)
            put("result", result ?: JsonNull)
            put("error", if (errorCode == null) JsonNull else buildJsonObject {
                put("code", errorCode); put("message", "Operation is not available")
                put("retryable", errorCode == "BUSY"); put("requestId", request.getValue("requestId"))
                put("nativeCode", JsonNull); put("details", buildJsonObject {})
            })
        }.toString())
    }
}
