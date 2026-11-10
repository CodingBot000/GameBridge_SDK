package com.gamebridge

import kotlinx.serialization.json.*
import java.util.UUID

sealed interface BridgeDispatchResult {
    data class Message(val json: String) : BridgeDispatchResult
    data class Rejected(val code: String) : BridgeDispatchResult
}

/** Provider operations receive only a validated request and return a JSON result. */
fun interface BridgeOperationHandler {
    fun invoke(operation: String, payload: JsonObject): JsonElement
}

/** A narrow operation allowlist; unsupported functions never return fake success. */
class BridgeDispatcher(private val handler: BridgeOperationHandler? = null) {
    private val diagnostics = Diagnostics()
    private var state = "UNINITIALIZED"
    private var ownerSession: String? = null
    @Synchronized
    fun dispatch(bytes: ByteArray): BridgeDispatchResult {
        val request = parseRequest(bytes) ?: return rejection(bytes)
        val operation = request.getValue("operation").jsonPrimitive.content
        val session = request.getValue("sdkSessionId").jsonPrimitive.content
        if (ownerSession != null && ownerSession != session) return response(request, null, "NOT_INITIALIZED")
        val category = when {
            operation == "sdk.initialize" -> DiagnosticKind.INITIALIZE
            operation == "sdk.shutdown" -> DiagnosticKind.SHUTDOWN
            operation.startsWith("auth.") -> DiagnosticKind.AUTH
            operation.startsWith("store.") -> DiagnosticKind.PURCHASE
            operation.startsWith("push.") -> DiagnosticKind.PUSH
            else -> null
        }
        val id = runCatching { UUID.fromString(request.getValue("requestId").jsonPrimitive.content) }.getOrNull()
        if (operation == "sdk.initialize" && ownerSession == null) diagnostics.clear()
        category?.let { diagnostics.record(it, DiagnosticOutcome.STARTED, id) }
        return try {
            val result = when (operation) {
                "diagnostics.get" -> {
                    if (state != "READY") throw SdkFailure("NOT_INITIALIZED")
                    buildJsonObject {
                    put("events", buildJsonArray {
                        diagnostics.snapshot().forEach { event -> add(buildJsonObject {
                            put("kind", event.kind.name); put("outcome", event.outcome.name)
                            put("timestamp", event.timestamp.toString())
                            put("requestId", event.requestId?.toString()?.let(::JsonPrimitive) ?: JsonNull)
                        }) }
                    })
                }
                }
                "sdk.status" -> buildJsonObject { put("state", state); put("sdkVersion", GameBridgeVersion.CURRENT) }
                "sdk.shutdown" -> {
                    handler?.invoke(operation, request.getValue("payload").jsonObject)
                    state = "SHUTDOWN"; ownerSession = null
                    buildJsonObject { put("state", state) }
                }
                "sdk.initialize" -> {
                    val initialized = handler?.invoke(operation, request.getValue("payload").jsonObject)
                        ?: throw SdkFailure("UNSUPPORTED_OPERATION")
                    state = "READY"; ownerSession = session
                    initialized
                }
                else -> handler?.invoke(operation, request.getValue("payload").jsonObject)
                    ?: throw SdkFailure("UNSUPPORTED_OPERATION")
            }
            category?.let { diagnostics.record(it, DiagnosticOutcome.SUCCEEDED, id) }
            response(request, result, null)
        } catch (failure: SdkFailure) {
            category?.let { diagnostics.record(it, DiagnosticOutcome.FAILED, id) }
            response(request, null, failure.code, failure.retryable, failure.nativeCode)
        } catch (_: Exception) {
            category?.let { diagnostics.record(it, DiagnosticOutcome.FAILED, id) }
            response(request, null, "INTERNAL_ERROR")
        }
    }
    /** Drop in-memory provider state after host disposal; persistent sessions remain restorable. */
    @Synchronized
    fun reset() {
        try { handler?.invoke("sdk.shutdown", buildJsonObject {}) }
        finally { ownerSession = null; state = "SHUTDOWN" }
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
    private fun response(request: JsonObject, result: JsonElement?, errorCode: String?, retryable: Boolean = false, nativeCode: String? = null): BridgeDispatchResult.Message {
        val operation = request.getValue("operation").jsonPrimitive.content
        return BridgeDispatchResult.Message(buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", request.getValue("sdkSessionId")); put("kind", "response")
            put("requestId", request.getValue("requestId")); put("operation", operation); put("ok", errorCode == null)
            put("result", result ?: JsonNull)
            put("error", if (errorCode == null) JsonNull else buildJsonObject {
                put("code", errorCode); put("message", "Operation is not available")
                put("retryable", retryable || errorCode == "BUSY"); put("requestId", request.getValue("requestId"))
                put("nativeCode", nativeCode?.let(::JsonPrimitive) ?: JsonNull); put("details", buildJsonObject {})
            })
        }.toString())
    }
}
