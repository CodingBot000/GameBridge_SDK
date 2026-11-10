package com.gamebridge.bridge

import com.gamebridge.*
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*

internal interface GoogleAuthBridgeApi {
    suspend fun signIn(): UserProfile
    suspend fun restore(): UserProfile?
    suspend fun signOut()
    fun close()
}

/** Selects only the explicitly requested provider; there is no sandbox-to-mock fallback. */
internal class ModeBridgeHandler(private val local: BridgeOperationHandler, private val google: BridgeOperationHandler) : BridgeOperationHandler {
    private var active: BridgeOperationHandler? = null
    override fun invoke(operation: String, payload: JsonObject): JsonElement {
        if (operation == "sdk.shutdown") {
            try { return active?.invoke(operation, payload) ?: buildJsonObject {} } finally { active = null }
        }
        if (operation == "sdk.initialize") {
            val next = when (payload.string("providerMode")) {
                "LOCAL_MOCK" -> local
                "PLATFORM_SANDBOX" -> google
                else -> throw SdkFailure("UNSUPPORTED_PROVIDER")
            }
            if (active != null && active !== next) throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
            return next.invoke(operation, payload).also { active = next }
        }
        return (active ?: throw SdkFailure("NOT_INITIALIZED")).invoke(operation, payload)
    }
}

internal class GoogleAuthBridgeHandler(private val factory: (GameBridgeConfig) -> GoogleAuthBridgeApi) : BridgeOperationHandler {
    private var provider: GoogleAuthBridgeApi? = null
    private var config: GameBridgeConfig? = null
    override fun invoke(operation: String, payload: JsonObject): JsonElement = runBlocking {
        when (operation) {
            "sdk.initialize" -> initialize(payload)
            "sdk.shutdown" -> { provider?.close(); provider = null; config = null; buildJsonObject {} }
            else -> {
                val auth = provider ?: throw SdkFailure("NOT_INITIALIZED")
                when (operation) {
                    "auth.signIn" -> {
                        if (payload.string("provider") != "GOOGLE") throw SdkFailure("UNSUPPORTED_PROVIDER")
                        Json.encodeToJsonElement(UserProfile.serializer(), auth.signIn())
                    }
                    "auth.restore" -> {
                        val user = auth.restore()
                        buildJsonObject {
                            put("signedIn", user != null)
                            put("user", user?.let { Json.encodeToJsonElement(UserProfile.serializer(), it) } ?: JsonNull)
                            put("expiresAt", JsonNull); put("sessionRestored", user != null)
                        }
                    }
                    "auth.signOut" -> { auth.signOut(); buildJsonObject {} }
                    else -> throw SdkFailure("UNSUPPORTED_OPERATION")
                }
            }
        }
    }
    private fun initialize(payload: JsonObject): JsonObject {
        if (payload.string("providerMode") != "PLATFORM_SANDBOX" || payload.containsKey("developmentKey")) throw SdkFailure("UNSUPPORTED_PROVIDER")
        val appId = payload.string("appId") ?: throw SdkFailure("CONFIG_REQUIRED")
        val base = payload.string("backendBaseUrl") ?: throw SdkFailure("CONFIG_REQUIRED")
        val timeout = (payload["requestTimeoutMs"] as? JsonPrimitive)?.longOrNull ?: throw SdkFailure("CONFIG_REQUIRED")
        val clientId = payload.string("googleServerClientId")?.takeIf { it.isNotBlank() }
        val next = GameBridgeConfig(appId, ProviderMode.PLATFORM_SANDBOX, base, clientId, timeout)
        try { next.validate() } catch (_: ConfigurationException) { throw SdkFailure("CONFIG_REQUIRED") }
        if (provider != null && config != next) throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
        if (provider == null) { provider = factory(next); config = next }
        return buildJsonObject {
            put("state", "READY"); put("mode", "PLATFORM_SANDBOX"); put("provider", "GOOGLE")
            put("capabilities", buildJsonObject {
                for (name in listOf("auth", "store", "push", "config")) {
                    val supported = name == "auth"; val configured = supported && clientId != null
                    put(name, buildJsonObject {
                        put("supported", supported); put("configured", configured); put("mode", "PLATFORM_SANDBOX")
                        put("reason", if (configured) JsonNull else JsonPrimitive(if (supported) "googleServerClientId required" else "Bridge operation is not connected"))
                    })
                }
            })
        }
    }
}
private fun JsonObject.string(name: String): String? = (this[name] as? JsonPrimitive)?.takeIf { it.isString }?.content
