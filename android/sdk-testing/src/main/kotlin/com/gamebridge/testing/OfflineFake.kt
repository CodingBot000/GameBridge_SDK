package com.gamebridge.testing

import com.gamebridge.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.UUID

enum class FakeScenario { SUCCESS, CANCELED, PENDING, NETWORK_FAILURE }
data class FakeWallet(val coinBalance: Long, val premiumEnabled: Boolean)
data class FakePushEvent(val messageId: String, val route: String)
data class FakePurchase(val status: String, val transactionId: String, val granted: Boolean, val wallet: FakeWallet)

/** Standalone offline test double. It never represents server or real-store fulfillment. */
class OfflineFake : SdkProvider {
    private val lock = Mutex()
    private var ready = false
    private var signedIn = false
    private var coins = 0L
    private var premium = false
    private val grantedTransactions = mutableMapOf<String, String>()
    private var pushPermission = false
    private var pushRegistered = false
    private val seenMessages = mutableSetOf<String>()
    private val events = mutableListOf<FakePushEvent>()
    override suspend fun initialize(config: GameBridgeConfig): InitSnapshot = lock.withLock {
        if (config.mode != ProviderMode.EDITOR_OFFLINE) throw SdkFailure("UNSUPPORTED_PROVIDER")
        ready = true
        InitSnapshot(mapOf("fake" to Capability(true, true, config.mode, "Offline fake only")))
    }
    override suspend fun shutdown() { lock.withLock { ready = false; signedIn = false; pushRegistered = false; events.clear() } }
    suspend fun signIn(): UserProfile = lock.withLock {
        checkReady(); signedIn = true
        UserProfile("d2719c4e-d533-47ee-9efd-838791ea79c8", "Mock User", "MOCK")
    }
    suspend fun products(): List<StoreProduct> = lock.withLock {
        checkReady(); listOf(
            StoreProduct("coins_100", "coins_100", ProductType.CONSUMABLE, "Mock coins", "Mock price", "XXX", null),
            StoreProduct("premium_unlock", "premium_unlock", ProductType.NON_CONSUMABLE, "Mock premium", "Mock price", "XXX", null),
        )
    }
    suspend fun purchase(productId: String, transactionId: UUID, scenario: FakeScenario): FakePurchase = lock.withLock {
        checkReady(); if (!signedIn) throw SdkFailure("SESSION_EXPIRED")
        if (productId !in setOf("coins_100", "premium_unlock")) throw SdkFailure("PRODUCT_NOT_FOUND")
        if (scenario == FakeScenario.NETWORK_FAILURE) throw SdkFailure("NETWORK_UNAVAILABLE")
        val id = "mock:$transactionId"
        val previous = grantedTransactions[id]
        if (previous != null && previous != productId) throw SdkFailure("IDEMPOTENCY_CONFLICT")
        val grant = scenario == FakeScenario.SUCCESS && previous == null
        if (grant) {
            if (productId == "coins_100") coins = Math.addExact(coins, 100) else premium = true
            grantedTransactions[id] = productId
        }
        val status = when (scenario) { FakeScenario.SUCCESS -> "PURCHASED"; FakeScenario.CANCELED -> "CANCELED"; FakeScenario.PENDING -> "PENDING"; FakeScenario.NETWORK_FAILURE -> error("unreachable") }
        FakePurchase(status, id, grant, FakeWallet(coins, premium))
    }
    suspend fun requestPushPermission(): Boolean = lock.withLock { checkReady(); pushPermission = true; true }
    suspend fun registerPush(): String = lock.withLock {
        checkReady(); if (!signedIn) throw SdkFailure("SESSION_EXPIRED")
        if (!pushPermission) throw SdkFailure("PERMISSION_DENIED")
        pushRegistered = true; "mock-fingerprint"
    }
    suspend fun receivePush(messageId: String, route: String) = lock.withLock {
        checkReady(); if (!pushRegistered) throw SdkFailure("PERMISSION_DENIED")
        if (messageId.isBlank() || route !in setOf("home", "store")) throw SdkFailure("INVALID_ARGUMENT")
        if (seenMessages.add(messageId)) events.add(FakePushEvent(messageId, route))
    }
    suspend fun drainPushEvents(): List<FakePushEvent> = lock.withLock { checkReady(); events.toList().also { events.clear() } }
    suspend fun wallet(): FakeWallet = lock.withLock { checkReady(); FakeWallet(coins, premium) }
    private fun checkReady() { if (!ready) throw SdkFailure("NOT_INITIALIZED") }
}
