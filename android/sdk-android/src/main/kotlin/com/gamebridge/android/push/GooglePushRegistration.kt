package com.gamebridge.android.push

import com.gamebridge.BackendClient
import com.gamebridge.SdkFailure
import com.gamebridge.android.auth.GoogleAuthProvider
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.boolean
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import java.util.UUID

/** Installation identity is supplied by the host; neither token nor credentials are exposed to Unity. */
internal class GooglePushRegistration(
    private val auth: GoogleAuthProvider,
    private val installationId: UUID,
    private val request: suspend (path: String, method: String, body: String?, accessToken: String) -> String,
) {
    constructor(auth: GoogleAuthProvider, installationId: UUID, client: BackendClient) : this(auth, installationId, { path, method, body, token ->
        client.request(path, method, body, accessToken = token).json
    })
    private val path get() = "/v1/devices/$installationId/push-token"
    suspend fun register(token: String): String {
        if (token.isBlank()) throw SdkFailure("INVALID_ARGUMENT")
        return auth.withAuthenticatedSession { session ->
            val body = buildJsonObject { put("token", token); put("provider", "FCM"); put("platform", "ANDROID") }.toString()
            val result = request(path, "PUT", body, session.accessToken)
            try {
                val json = Json.parseToJsonElement(result).jsonObject
                val fingerprint = json.getValue("tokenFingerprint").jsonPrimitive.content
                require(json.getValue("provider").jsonPrimitive.content == "FCM" && json.getValue("registered").jsonPrimitive.boolean && fingerprint.matches(Regex("[0-9a-f]{12}")))
                fingerprint
            } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        } ?: throw SdkFailure("SESSION_EXPIRED")
    }
    suspend fun unregister() {
        auth.withAuthenticatedSession { session ->
            val result = request(path, "DELETE", null, session.accessToken)
            try { require(!Json.parseToJsonElement(result).jsonObject.getValue("registered").jsonPrimitive.boolean) }
            catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        } ?: throw SdkFailure("SESSION_EXPIRED")
    }
}

/** Host-managed FCM registration; raw tokens remain within the Native SDK. */
class GooglePushClient internal constructor(private val registration: GooglePushRegistration) {
    companion object {
        @JvmStatic fun create(auth: GoogleAuthProvider, config: com.gamebridge.GameBridgeConfig, installationId: UUID): GooglePushClient {
            if (config.mode != com.gamebridge.ProviderMode.PLATFORM_SANDBOX || !auth.usesConfiguration(config)) throw SdkFailure("CONFIG_REQUIRED")
            return GooglePushClient(GooglePushRegistration(auth, installationId, BackendClient(config)))
        }
    }
    suspend fun register(token: String): String = registration.register(token)
    suspend fun unregister() = registration.unregister()
}
