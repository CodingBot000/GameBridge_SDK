package com.gamebridge

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.*
import java.util.UUID

/** Development-only bridge. Sessions and purchase proofs remain inside the Native client. */
class LocalMockBridgeHandler(private val tokenStore: () -> TokenStore, private val pendingStore: (() -> TokenStore)?) : BridgeOperationHandler {
    constructor(tokenStore: () -> TokenStore) : this(tokenStore, null)
    private var client: LocalMockClient? = null
    private var config: GameBridgeConfig? = null
    private var developmentKey: String? = null
    private var mockSubject: String? = null

    override fun invoke(operation: String, payload: JsonObject): JsonElement = runBlocking {
        when (operation) {
            "sdk.initialize" -> initialize(payload)
            "sdk.shutdown" -> {
                client = null; config = null; developmentKey = null; mockSubject = null
                buildJsonObject { put("state", "SHUTDOWN") }
            }
            else -> {
                val current = client ?: throw SdkFailure("NOT_INITIALIZED")
                when (operation) {
                    "auth.signIn" -> {
                        if (payload.string("provider") != "MOCK") throw SdkFailure("UNSUPPORTED_PROVIDER")
                        Json.encodeToJsonElement(UserProfile.serializer(), current.signIn(mockSubject!!))
                    }
                    "auth.restore" -> {
                        val user = current.restore()
                        buildJsonObject {
                            put("signedIn", user != null)
                            put("user", user?.let { Json.encodeToJsonElement(UserProfile.serializer(), it) } ?: JsonNull)
                            put("expiresAt", JsonNull); put("sessionRestored", user != null)
                        }
                    }
                    "auth.signOut" -> { current.signOut(); buildJsonObject {} }
                    "config.get" -> {
                        val effective = current.serviceSettings()
                        buildJsonObject {
                            put("revision", effective.settings.revision); put("maintenanceEnabled", effective.settings.maintenanceEnabled)
                            put("message", effective.settings.message?.let(::JsonPrimitive) ?: JsonNull)
                            put("expiresAt", effective.settings.expiresAt.toString())
                            put("source", if (effective.source == ConfigurationSource.REMOTE) "NETWORK" else "CACHE")
                        }
                    }
                    "store.products" -> JsonArray(current.products().map { product ->
                        buildJsonObject {
                            put("productId", product.productId); put("storeProductId", product.storeProductId)
                            put("type", product.type); put("title", "Mock ${product.productId}")
                            put("localizedPrice", "Mock price"); put("currencyCode", "XXX"); put("priceMicros", JsonNull)
                        }
                    })
                    "store.entitlements" -> Json.encodeToJsonElement(LocalWallet.serializer(), current.wallet())
                    "store.sync" -> {
                        if (payload.string("reason") !in setOf("APP_RESUME", "USER_RESTORE")) throw SdkFailure("INVALID_ARGUMENT")
                        val counts = current.recoverPending(); val wallet = current.wallet()
                        buildJsonObject {
                            put("examinedCount", counts.examinedCount); put("recoveredCount", counts.recoveredCount)
                            put("deferredCount", counts.deferredCount); put("failureCount", counts.failureCount)
                            put("entitlements", Json.encodeToJsonElement(LocalWallet.serializer(), wallet))
                        }
                    }
                    "store.purchase" -> {
                        val productId = payload.string("productId") ?: throw SdkFailure("INVALID_ARGUMENT")
                        val attempt = UUID.randomUUID()
                        val purchase = current.purchase(productId, UUID.randomUUID(), attempt)
                        buildJsonObject {
                            put("attemptId", attempt.toString()); put("productId", productId); put("status", "PURCHASED")
                            put("serverPurchaseId", purchase.serverPurchaseId); put("fulfillmentStatus", purchase.fulfillmentStatus)
                            put("finalizationStatus", purchase.finalizationStatus); put("error", JsonNull)
                        }
                    }
                    else -> throw SdkFailure("UNSUPPORTED_OPERATION")
                }
            }
        }
    }

    private fun initialize(payload: JsonObject): JsonObject {
        if (payload.string("providerMode") != "LOCAL_MOCK") throw SdkFailure("UNSUPPORTED_PROVIDER")
        val appId = payload.string("appId") ?: throw SdkFailure("CONFIG_REQUIRED")
        val baseUrl = payload.string("backendBaseUrl") ?: throw SdkFailure("CONFIG_REQUIRED")
        val key = payload.string("developmentKey") ?: throw SdkFailure("CONFIG_REQUIRED")
        val subject = payload.string("mockSubject") ?: throw SdkFailure("CONFIG_REQUIRED")
        val timeout = (payload["requestTimeoutMs"] as? JsonPrimitive)?.longOrNull ?: throw SdkFailure("CONFIG_REQUIRED")
        if (key.length < 32 || subject !in setOf("A", "B")) throw SdkFailure("CONFIG_REQUIRED")
        val next = GameBridgeConfig(appId, ProviderMode.LOCAL_MOCK, baseUrl, requestTimeoutMs = timeout)
        try { next.validate() } catch (_: ConfigurationException) { throw SdkFailure("CONFIG_REQUIRED") }
        if (client != null && (config != next || developmentKey != key || mockSubject != subject)) {
            throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
        }
        if (client == null) {
            client = LocalMockClient(next, tokenStore(), key, pendingStore?.invoke())
            config = next; developmentKey = key; mockSubject = subject
        }
        return buildJsonObject {
            put("state", "READY"); put("mode", "LOCAL_MOCK"); put("provider", "MOCK")
            put("capabilities", buildJsonObject {
                for (name in listOf("auth", "store", "push", "config")) {
                    val available = name == "auth" || name == "store" || name == "config"
                    put(name, buildJsonObject {
                        put("supported", available); put("configured", available); put("mode", "LOCAL_MOCK")
                        put("reason", when (name) {
                            "store" -> if (pendingStore == null) JsonPrimitive("Purchase recovery storage is not configured") else JsonNull
                            "push" -> JsonPrimitive("Bridge operation is not connected")
                            else -> JsonNull
                        })
                    })
                }
            })
        }
    }
    private fun JsonObject.string(name: String): String? = (this[name] as? JsonPrimitive)?.takeIf { it.isString }?.content
}
