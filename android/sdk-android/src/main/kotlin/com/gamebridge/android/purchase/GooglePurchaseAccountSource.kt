package com.gamebridge.android.purchase

import com.gamebridge.BackendClient
import com.gamebridge.SdkFailure
import com.gamebridge.android.auth.GoogleAuthProvider
import com.gamebridge.android.auth.BackendSessionAccess
import com.gamebridge.android.auth.GoogleSessionAccess
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.util.UUID

/** Internal Native-only source: neither credentials nor binding cross the Unity bridge. */
internal class GooglePurchaseAccountSource(private val auth: BackendSessionAccess, private val client: BackendClient) : PlayAccountSource {
    constructor(auth:GoogleAuthProvider,client:BackendClient):this(GoogleSessionAccess(auth),client)
    override suspend fun current(): BoundPlayAccount? = auth.withAuthenticatedSession { session ->
        val response = client.request("/v1/purchases/bindings", "GET", accessToken = session.accessToken)
        parseGoogleBinding(session.userId, response.json)
    }
}
internal fun parseGoogleBinding(userId: String, body: String): BoundPlayAccount {
    try {
        val id = UUID.fromString(userId)
        val value = Json.parseToJsonElement(body).jsonObject.getValue("googleObfuscatedAccountId").jsonPrimitive.content
        val binding = UUID.fromString(value)
        if (binding.toString() != value || id.toString() != userId) throw IllegalArgumentException()
        return BoundPlayAccount(id, binding.toString())
    } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
}
