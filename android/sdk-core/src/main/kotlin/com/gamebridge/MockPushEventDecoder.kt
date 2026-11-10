package com.gamebridge

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive

/** Decode only the public local-mock push fields; never forward arbitrary server data. */
internal object MockPushEventDecoder {
    fun decode(bytes: ByteArray): PushPayload? {
        if (bytes.size > BridgeProtocol.MAX_BYTES) return null
        val text = try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(bytes)).toString() } catch (_: Exception) { return null }
        val json = try { Json.parseToJsonElement(text) as? JsonObject } catch (_: Exception) { null } ?: return null
        fun string(name: String): String? = (json[name] as? JsonPrimitive)?.takeIf { it.isString }?.content
        val messageId = string("messageId")?.takeIf { it.isNotEmpty() } ?: return null
        val route = string("route")?.takeIf { it == "home" || it == "store" } ?: return null
        val campaign = json["campaignId"]
        if (campaign != null && campaign !is JsonNull && (campaign !is JsonPrimitive || !campaign.isString)) return null
        return PushPayload(messageId, route, string("campaignId"))
    }
}
