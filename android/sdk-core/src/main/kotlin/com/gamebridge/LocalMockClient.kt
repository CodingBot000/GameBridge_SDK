package com.gamebridge

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import java.util.UUID

private val wireJson = Json { ignoreUnknownKeys = true }
@Serializable private class WireSession(val accessToken: String, val refreshToken: String, val expiresAt: String, val userId: String) {
    override fun toString() = "WireSession([redacted])"
}
@Serializable private class SecretSession(val accessToken: String, val refreshToken: String, val expiresAt: String, val userId: String,
                                          val appId: String, val providerMode: String, val backendBaseUrl: String) {
    override fun toString() = "SecretSession([redacted])"
}
@Serializable private data class Me(val userId: String)
@Serializable data class LocalWallet(val userId: String, val premiumEnabled: Boolean, val coinBalance: String, val revision: String, val updatedAt: String)
@Serializable data class LocalProduct(val productId: String, val storeProductId: String, val type: String)
@Serializable data class LocalPurchase(val serverPurchaseId: String, val fulfillmentStatus: String, val finalizationStatus: String, val entitlements: LocalWallet)

/** Native-only local development path. Tokens remain in Native memory/storage. */
class LocalMockClient(private val config: GameBridgeConfig, private val store: TokenStore, private val developmentKey: String) {
    private val backend = BackendClient(config)
    private val serviceConfig = backendServiceConfiguration(backend)
    private val lock = Mutex()
    private var session: SecretSession? = null
    init {
        if (config.mode != ProviderMode.LOCAL_MOCK) throw SdkFailure("UNSUPPORTED_PROVIDER")
        if (developmentKey.length < 32) throw SdkFailure("CONFIG_REQUIRED")
    }
    suspend fun signIn(subject: String): UserProfile = lock.withLock {
        if (subject !in setOf("A", "B")) throw SdkFailure("INVALID_ARGUMENT")
        val body = buildJsonObject { put("subject", subject) }.toString()
        val result = backend.request("/v1/dev/auth", "POST", body, developmentKey = developmentKey)
        val next = wrap(decode<WireSession>(result.json))
        store.save(wireJson.encodeToString(next)); session = next
        UserProfile(next.userId, null, "MOCK")
    }
    suspend fun restore(): UserProfile? = lock.withLock {
        val loaded = loadBound() ?: return@withLock null
        session = loaded
        val me = decode<Me>(authenticated("/v1/me", "GET").json)
        if (me.userId != session?.userId) { store.clear(); session = null; throw SdkFailure("AUTH_FAILED") }
        UserProfile(me.userId, null, "MOCK")
    }
    suspend fun serviceSettings(): EffectiveServiceSettings = serviceConfig.current() ?: throw SdkFailure("CONFIG_REQUIRED")
    suspend fun products(): List<LocalProduct> = lock.withLock { decode(authenticated("/v1/catalog", "GET").json) }
    suspend fun wallet(): LocalWallet = lock.withLock { decode(authenticated("/v1/entitlements", "GET").json) }
    suspend fun purchase(productId: String, transactionId: UUID, attemptId: UUID): LocalPurchase = lock.withLock {
        if (productId !in setOf("coins_100", "premium_unlock")) throw SdkFailure("PRODUCT_NOT_FOUND")
        val userId = session?.userId ?: throw SdkFailure("SESSION_EXPIRED")
        val maintenance = serviceConfig.current()?.settings?.maintenanceEnabled
        if (!MaintenanceGate.permits(maintenance, ProtectedOperation.START_PURCHASE)) throw SdkFailure(if (maintenance == true) "MAINTENANCE" else "CONFIG_REQUIRED")
        val proof = "mock:$userId:$productId:$transactionId"
        val body = buildJsonObject { put("productId", productId); put("proof", proof); put("quantity", 1) }.toString()
        decode(authenticated("/v1/purchases/verify", "POST", body, attemptId.toString()).json)
    }
    suspend fun signOut() = lock.withLock {
        if (store.load() == "{\"state\":\"refresh_pending\"}") {
            session = null; store.clear(); throw SdkFailure("SESSION_EXPIRED", "REVOCATION_UNCONFIRMED")
        }
        val saved = loadBound()
        val current = session ?: saved
        session = null
        store.clear()
        if (current != null) try {
            try { backend.request("/v1/auth/logout", "POST", accessToken = current.accessToken) }
            catch (failure: SdkFailure) {
                if (failure.code != "SESSION_EXPIRED") throw failure
                backend.request("/v1/auth/logout", "POST", buildJsonObject { put("refreshToken", current.refreshToken) }.toString())
            }
        } catch (failure: SdkFailure) { throw SdkFailure(failure.code, "REVOCATION_UNCONFIRMED", failure.retryable) }
        catch (_: kotlinx.coroutines.CancellationException) { throw SdkFailure("CANCELED", "REVOCATION_UNCONFIRMED") }
        catch (_: Exception) { throw SdkFailure("INTERNAL_ERROR", "REVOCATION_UNCONFIRMED") }
        Unit
    }
    private suspend fun authenticated(path: String, method: String, body: String? = null, idempotencyKey: String? = null): BackendResponse {
        var current = session ?: throw SdkFailure("SESSION_EXPIRED")
        try { return backend.request(path, method, body, current.accessToken, idempotencyKey = idempotencyKey) }
        catch (failure: SdkFailure) { if (failure.code != "SESSION_EXPIRED") throw failure }
        val refreshBody = buildJsonObject { put("refreshToken", current.refreshToken) }.toString()
        // Persist a tombstone before rotation; after a lost response the old refresh token must never be reused.
        store.save("{\"state\":\"refresh_pending\"}")
        session = null
        val refreshed = wrap(decode<WireSession>(backend.request("/v1/auth/refresh", "POST", refreshBody).json))
        if (refreshed.userId != current.userId) throw SdkFailure("AUTH_FAILED")
        store.save(wireJson.encodeToString(refreshed)); session = refreshed; current = refreshed
        return backend.request(path, method, body, current.accessToken, idempotencyKey = idempotencyKey)
    }
    private fun loadBound(): SecretSession? {
        val stored = store.load() ?: return null
        val loaded = try { decode<SecretSession>(stored) } catch (_: Exception) { session = null; throw SdkFailure("SESSION_EXPIRED") }
        if (loaded.appId != config.appId || loaded.providerMode != config.mode.name || loaded.backendBaseUrl != config.backendBaseUrl) throw SdkFailure("SESSION_EXPIRED")
        if (loaded.accessToken.isBlank() || loaded.refreshToken.isBlank() || runCatching { UUID.fromString(loaded.userId).toString() == loaded.userId }.getOrDefault(false).not() ||
            runCatching { java.time.Instant.parse(loaded.expiresAt) }.isFailure) throw SdkFailure("SESSION_EXPIRED")
        return loaded
    }
    private fun wrap(value: WireSession): SecretSession {
        if (value.accessToken.isBlank() || value.refreshToken.isBlank() || runCatching { UUID.fromString(value.userId).toString() == value.userId }.getOrDefault(false).not() ||
            runCatching { java.time.Instant.parse(value.expiresAt) }.isFailure) throw SdkFailure("AUTH_FAILED")
        return SecretSession(value.accessToken, value.refreshToken, value.expiresAt, value.userId, config.appId, config.mode.name, config.backendBaseUrl!!)
    }
    private inline fun <reified T> decode(json: String): T = try { wireJson.decodeFromString(json) } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
}
