package com.gamebridge

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
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
@Serializable private data class PendingMockPurchase(val appId: String, val backendBaseUrl: String, val userId: String,
                                                     val productId: String, val transactionId: String, val attemptId: String)
data class LocalRecoveryCounts(val examinedCount: Int, val recoveredCount: Int, val deferredCount: Int, val failureCount: Int)
data class LocalPushRegistration(val tokenFingerprint: String, val updatedAt: String)

/** Native-only local development path. Tokens remain in Native memory/storage. */
class LocalMockClient @JvmOverloads constructor(private val config: GameBridgeConfig, private val store: TokenStore,
                                                private val developmentKey: String, private val pendingStore: TokenStore? = null) {
    private val backend = BackendClient(config)
    private val serviceConfig = backendServiceConfiguration(backend)
    private val lock = Mutex()
    private var session: SecretSession? = null
    private var pushStream: MockPushStream? = null
    private val pushEpoch = java.util.concurrent.atomic.AtomicLong()
    internal fun stopMockPush() {
        pushEpoch.incrementAndGet()
        pushStream?.stop(); pushStream = null
    }
    internal fun startMockPush(installationId: UUID, listener: (PushPayload) -> Unit) {
        stopMockPush()
        val epoch = pushEpoch.get()
        val stream = MockPushStream(config.backendBaseUrl!!, installationId, {
            lock.withLock {
                if (session == null) null else {
                    authenticated("/v1/me", "GET")
                    session?.accessToken
                }
            }
        }) { value -> if (epoch == pushEpoch.get()) listener(value) }
        pushStream = stream; stream.start()
    }
    init {
        if (config.mode != ProviderMode.LOCAL_MOCK) throw SdkFailure("UNSUPPORTED_PROVIDER")
        val left = (store as? StorageIdentifiedTokenStore)?.storageIdentity
        val right = (pendingStore as? StorageIdentifiedTokenStore)?.storageIdentity
        val sameIdentity = left != null && left == right
        if (developmentKey.length < 32 || pendingStore === store || sameIdentity) throw SdkFailure("CONFIG_REQUIRED")
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
        val pending = PendingMockPurchase(config.appId, config.backendBaseUrl!!, userId, productId, transactionId.toString(), attemptId.toString())
        val saved = loadPending()
        val existing = saved.firstOrNull { sameScope(it, userId) }
        if (existing != null && existing != pending) throw SdkFailure("BUSY")
        if (pendingStore != null && existing == null) savePending(saved + pending)
        val result = verifyPending(pending)
        if (pendingStore != null) savePending(loadPending().filterNot { it == pending })
        result
    }
    suspend fun recoverPending(): LocalRecoveryCounts = lock.withLock {
        if (pendingStore == null) throw SdkFailure("CONFIG_REQUIRED")
        val userId = session?.userId ?: throw SdkFailure("SESSION_EXPIRED")
        val pending = loadPending().filter { sameScope(it, userId) }
        var recovered = 0; var deferred = 0; var failed = 0
        for (item in pending) {
            try {
                verifyPending(item)
                savePending(loadPending().filterNot { it == item }); recovered++
            } catch (cancel: kotlinx.coroutines.CancellationException) { throw cancel }
            catch (failure: SdkFailure) {
                if (failure.code in setOf("SESSION_EXPIRED", "CANCELED")) throw failure
                if (failure.code in setOf("NETWORK_UNAVAILABLE", "TIMEOUT", "BUSY")) deferred++ else failed++
            }
        }
        LocalRecoveryCounts(pending.size, recovered, deferred, failed)
    }
    private fun sameScope(item: PendingMockPurchase, userId: String) = item.appId == config.appId && item.backendBaseUrl == config.backendBaseUrl && item.userId == userId
    private fun loadPending(): List<PendingMockPurchase> {
        val raw = pendingStore?.load() ?: return emptyList()
        val list = try { wireJson.decodeFromString<List<PendingMockPurchase>>(raw) } catch (_: Exception) { throw SdkFailure("INTERNAL_ERROR") }
        if (list.any { it.appId.isBlank() || it.backendBaseUrl.isBlank() || it.productId !in setOf("coins_100", "premium_unlock") ||
            listOf(it.userId, it.transactionId, it.attemptId).any { id -> runCatching { UUID.fromString(id).toString() != id }.getOrDefault(true) } }) throw SdkFailure("INTERNAL_ERROR")
        return list
    }
    private fun savePending(items: List<PendingMockPurchase>) {
        val target = pendingStore ?: throw SdkFailure("CONFIG_REQUIRED")
        if (items.isEmpty()) target.clear() else target.save(wireJson.encodeToString(items))
    }
    private suspend fun verifyPending(item: PendingMockPurchase): LocalPurchase {
        val userId = session?.userId ?: throw SdkFailure("SESSION_EXPIRED")
        if (!sameScope(item, userId)) throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH")
        val proof = "mock:$userId:${item.productId}:${item.transactionId}"
        val body = buildJsonObject { put("productId", item.productId); put("proof", proof); put("quantity", 1) }.toString()
        val result = decode<LocalPurchase>(authenticated("/v1/purchases/verify", "POST", body, item.attemptId).json)
        if (result.entitlements.userId != userId || result.fulfillmentStatus !in setOf("GRANTED", "ALREADY_GRANTED") ||
            result.finalizationStatus !in setOf("PENDING", "FINALIZED", "NOT_REQUIRED") ||
            runCatching { UUID.fromString(result.serverPurchaseId).toString() != result.serverPurchaseId }.getOrDefault(true)) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
        return result
    }
    suspend fun registerMockPush(installationId: UUID): LocalPushRegistration = lock.withLock {
        val body = buildJsonObject { put("token", "mock:" + UUID.randomUUID()); put("provider", "MOCK"); put("platform", "MOCK"); put("appId", config.appId) }.toString()
        val response = authenticated("/v1/devices/$installationId/push-token", "PUT", body)
        val json = try { kotlinx.serialization.json.Json.parseToJsonElement(response.json).jsonObject } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        val fingerprint = (json["tokenFingerprint"] as? kotlinx.serialization.json.JsonPrimitive)?.takeIf { it.isString }?.content ?: throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
        if (json["provider"] != kotlinx.serialization.json.JsonPrimitive("MOCK") || json["registered"] != kotlinx.serialization.json.JsonPrimitive(true) || !fingerprint.matches(Regex("[0-9a-f]{12}"))) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
        LocalPushRegistration(fingerprint, java.time.Instant.now().toString())
    }
    suspend fun unregisterMockPush(installationId: UUID) = lock.withLock {
        val response = authenticated("/v1/devices/$installationId/push-token", "DELETE")
        val json = try { kotlinx.serialization.json.Json.parseToJsonElement(response.json).jsonObject } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        if (json["registered"] != kotlinx.serialization.json.JsonPrimitive(false)) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
        Unit
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
