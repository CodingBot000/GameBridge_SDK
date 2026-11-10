package com.gamebridge.bridge

import com.gamebridge.*
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*
import java.util.UUID

internal interface GoogleAuthBridgeApi {
    suspend fun signIn(): UserProfile
    suspend fun restore(): UserProfile?
    suspend fun signOut()
    suspend fun products(): List<StoreProduct> = throw SdkFailure("CONFIG_REQUIRED")
    suspend fun purchase(productId: String): PurchaseStatus = throw SdkFailure("CONFIG_REQUIRED")
    suspend fun entitlements(): EntitlementSnapshot = throw SdkFailure("CONFIG_REQUIRED")
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

internal class GoogleAuthBridgeHandler(private val factory: (GameBridgeConfig, Map<String, String>?) -> GoogleAuthBridgeApi) : BridgeOperationHandler {
    private var provider: GoogleAuthBridgeApi? = null
    private var config: GameBridgeConfig? = null
    private var productIds: Map<String, String>? = null
    override fun invoke(operation: String, payload: JsonObject): JsonElement = runBlocking {
        when (operation) {
            "sdk.initialize" -> initialize(payload)
            "sdk.shutdown" -> { provider?.close(); provider = null; config = null; productIds = null; buildJsonObject {} }
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
                    "store.products" -> JsonArray(auth.products().map { Json.encodeToJsonElement(StoreProduct.serializer(), it) })
                    "store.entitlements" -> Json.encodeToJsonElement(EntitlementSnapshot.serializer(), auth.entitlements())
                    "store.purchase" -> {
                        val product = payload.string("productId") ?: throw SdkFailure("INVALID_ARGUMENT")
                        val status = auth.purchase(product)
                        if (status !in setOf(PurchaseStatus.PENDING, PurchaseStatus.VERIFICATION_PENDING)) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
                        buildJsonObject {
                            put("attemptId", UUID.randomUUID().toString()); put("productId", product); put("status", status.name)
                            put("serverPurchaseId", JsonNull); put("fulfillmentStatus", "NOT_GRANTED")
                            put("finalizationStatus", "PENDING"); put("error", JsonNull)
                        }
                    }
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
        val mapping = payload["storeProductIds"]?.let { value ->
            val obj = value as? JsonObject ?: throw SdkFailure("CONFIG_REQUIRED")
            if (obj.keys != setOf("coins_100", "premium_unlock")) throw SdkFailure("CONFIG_REQUIRED")
            val coins = obj.string("coins_100")?.takeIf { it.isNotBlank() } ?: throw SdkFailure("CONFIG_REQUIRED")
            val premium = obj.string("premium_unlock")?.takeIf { it.isNotBlank() } ?: throw SdkFailure("CONFIG_REQUIRED")
            if (coins == premium) throw SdkFailure("CONFIG_REQUIRED")
            mapOf("coins_100" to coins, "premium_unlock" to premium)
        }
        if (provider != null && (config != next || productIds != mapping)) throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
        if (provider == null) { provider = factory(next, mapping); config = next; productIds = mapping }
        return buildJsonObject {
            put("state", "READY"); put("mode", "PLATFORM_SANDBOX"); put("provider", "GOOGLE")
            put("capabilities", buildJsonObject {
                for (name in listOf("auth", "store", "push", "config")) {
                    val supported = name == "auth" || name == "store"
                    val configured = when (name) { "auth" -> clientId != null; "store" -> clientId != null && mapping != null; else -> false }
                    put(name, buildJsonObject {
                        put("supported", supported); put("configured", configured); put("mode", "PLATFORM_SANDBOX")
                        put("reason", if (configured) JsonNull else JsonPrimitive(if (supported) "Google client ID and store product IDs required" else "Bridge operation is not connected"))
                    })
                }
            })
        }
    }
}
private fun JsonObject.string(name: String): String? = (this[name] as? JsonPrimitive)?.takeIf { it.isString }?.content
