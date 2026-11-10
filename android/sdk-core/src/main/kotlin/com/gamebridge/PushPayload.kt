package com.gamebridge

data class PushPayload(val messageId: String, val route: String, val campaignId: String?) {
    companion object {
        fun parse(data: Map<String, String>): PushPayload? {
            val id = data["messageId"]?.takeIf { it.isNotEmpty() } ?: return null
            val route = data["route"]?.takeIf { it == "home" || it == "store" } ?: return null
            return PushPayload(id, route, data["campaignId"])
        }
    }
}
