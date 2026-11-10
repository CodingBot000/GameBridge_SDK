package com.gamebridge.android.purchase

import android.app.Activity
import com.android.billingclient.api.Purchase
import com.gamebridge.SdkFailure
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import org.junit.jupiter.api.Test
import java.security.MessageDigest
import java.util.UUID
import kotlin.test.*

private class FakePlayGateway : PlayGateway {
    var listener: ((RawPlayPurchase) -> Unit)? = null
    var launches = 0
    var recoveries = 0
    var recoveredPurchases: List<RawPlayPurchase> = emptyList()
    override fun attach(activity: Activity) {}
    override fun detach() {}
    override fun setObserver(observer: ((RawPlayPurchase) -> Unit)?) { this.listener = observer }
    override suspend fun products(storeIds: List<String>) = storeIds.map { PlayCatalogItem(it, "title-$it", "₩1,000", "KRW", 1_000_000) }
    override suspend fun launch(storeId: String, account: BoundPlayAccount): String { launches++; return "VERIFICATION_PENDING" }
    override suspend fun recover(): List<RawPlayPurchase> { recoveries++; return recoveredPurchases }
    override fun close() {}
}
class GooglePlayBillingProviderTest {
    private val mapping = mapOf("coins_100" to "coins.store", "premium_unlock" to "premium.store")
    private val account = BoundPlayAccount(UUID.randomUUID(), UUID.randomUUID().toString())
    private fun proof(state: Int, quantity: Int = 1, accountId: String? = account.obfuscatedAccountId) = RawPlayPurchase("coins.store", "test-secret-proof", accountId, quantity, state)
    private suspend fun next(provider: GooglePlayBillingProvider, gateway: FakePlayGateway, raw: RawPlayPurchase): PlayPurchaseEvent = kotlinx.coroutines.coroutineScope {
        val result = async(start = CoroutineStart.UNDISPATCHED) { withTimeout(2000) { provider.events.first() } }
        gateway.listener!!.invoke(raw); result.await()
    }
    @Test fun `unrelated callback does not consume active waiter`() {
        val router = PlayWaiterRouter<Any>(); val waiting = Any()
        router.register("coins.store", waiting)
        assertNull(router.take(false, setOf("premium.store")))
        assertSame(waiting, router.take(false, setOf("coins.store")))
        assertNull(router.take(true, emptySet()))
    }
    @Test fun `missing verifier cannot launch real purchase`() = runBlocking {
        val gateway = FakePlayGateway(); val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, null)
        assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { provider.purchase("coins_100") }.code)
        assertEquals(0, gateway.launches); provider.close()
    }
    @Test fun `unspecified verification concurrency blocks purchase`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, raw -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, verificationConcurrency = null)
        assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { provider.purchase("coins_100") }.code)
        assertEquals(0, gateway.launches); provider.close()
    }
    @Test fun `default verification concurrency serializes transactions`() = runBlocking {
        val gateway = FakePlayGateway()
        val firstEntered = CompletableDeferred<Unit>()
        val releaseFirst = CompletableDeferred<Unit>()
        val secondEntered = CompletableDeferred<Unit>()
        val calls = java.util.concurrent.atomic.AtomicInteger()
        val sink = PlayProofSink { _, _, raw ->
            if (calls.incrementAndGet() == 1) { firstEntered.complete(Unit); releaseFirst.await() }
            else secondEntered.complete(Unit)
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try {
            gateway.listener!!.invoke(proof(Purchase.PurchaseState.PURCHASED))
            withTimeout(2000) { firstEntered.await() }
            gateway.listener!!.invoke(proof(Purchase.PurchaseState.PURCHASED))
            assertNull(withTimeoutOrNull(150) { secondEntered.await() })
            releaseFirst.complete(Unit)
            withTimeout(2000) { secondEntered.await() }
            assertEquals(2, calls.get())
        } finally { provider.close() }
    }
    @Test fun `missing or maintenance config blocks purchase ui`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, raw -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val missing = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { missing.purchase("coins_100") }.code)
        missing.recover(); assertEquals(1, gateway.recoveries)
        missing.close()
        val maintenance = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, maintenanceState = { true })
        assertEquals("MAINTENANCE", assertFailsWith<SdkFailure> { maintenance.purchase("coins_100") }.code)
        assertEquals(0, gateway.launches); maintenance.close()
    }
    @Test fun `missing readiness blocks billing ui even with valid config`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, raw -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, maintenanceState = { false })
        try { assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { provider.purchase("coins_100") }.code); assertEquals(0, gateway.launches) }
        finally { provider.close() }
    }
    @Test fun `shared ui gate blocks billing while another ui owns it`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, raw -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val gate = Mutex(locked = true)
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, uiGate = gate, maintenanceState = { false }, readiness = {})
        try {
            assertEquals("BUSY", assertFailsWith<SdkFailure> { provider.purchase("coins_100") }.code)
            assertEquals(0, gateway.launches)
            gate.unlock()
            assertEquals("VERIFICATION_PENDING", provider.purchase("coins_100"))
            assertEquals(1, gateway.launches)
        } finally { provider.close() }
    }
    @Test fun `account switch suppresses stale verified event`() = runBlocking {
        val gateway = FakePlayGateway(); var current: BoundPlayAccount? = account
        val sink = PlayProofSink { _, _, raw ->
            current = BoundPlayAccount(UUID.randomUUID(), UUID.randomUUID().toString())
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { current }, sink, verificationConcurrency = 1)
        val event = async(start = CoroutineStart.UNDISPATCHED) { withTimeoutOrNull(200) { provider.events.first() } }
        gateway.listener!!.invoke(proof(Purchase.PurchaseState.PURCHASED))
        assertNull(event.await()); provider.close()
    }
    @Test fun `pending wrong account and quantity never reach verifier`() = runBlocking {
        val gateway = FakePlayGateway(); var verifies = 0
        val sink = PlayProofSink { _, _, raw -> verifies++; ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, verificationConcurrency = 1)
        assertEquals("PENDING", next(provider, gateway, proof(Purchase.PurchaseState.PENDING)).status)
        assertEquals("PURCHASE_ACCOUNT_MISMATCH", next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED, accountId = UUID.randomUUID().toString())).errorCode)
        assertEquals("UNSUPPORTED_OPERATION", next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED, quantity = 2)).errorCode)
        assertEquals(0, verifies); provider.close()
    }
    @Test fun `verified result is bound to proof and raw proof is redacted`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, raw -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray())) }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, verificationConcurrency = 1, maintenanceState = { false }, readiness = {})
        val products = provider.products(); assertEquals("₩1,000", products.first().localizedPrice)
        assertEquals("VERIFICATION_PENDING", provider.purchase("coins_100")); assertEquals(1, gateway.launches)
        val raw = proof(Purchase.PurchaseState.PURCHASED)
        val event = next(provider, gateway, raw)
        assertEquals("PURCHASED", event.status); assertNotNull(event.serverPurchaseId)
        assertFalse(raw.toString().contains("test-secret-proof")); assertFalse(event.toString().contains("test-secret-proof"))
        provider.close()
    }
    @Test fun `mismatched proof fingerprint is rejected`() = runBlocking {
        val gateway = FakePlayGateway()
        val sink = PlayProofSink { _, _, _ -> ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", ByteArray(32)) }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, verificationConcurrency = 1)
        assertEquals("PURCHASE_ACCOUNT_MISMATCH", next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED)).errorCode)
        provider.close()
    }
    @Test fun `recovery counts only observed verification outcomes`() = runBlocking {
        val gateway = FakePlayGateway()
        gateway.recoveredPurchases = listOf(proof(Purchase.PurchaseState.PURCHASED), proof(Purchase.PurchaseState.PENDING),
            proof(Purchase.PurchaseState.PURCHASED, quantity = 2), RawPlayPurchase("coins.store", "retry", account.obfuscatedAccountId, 1, Purchase.PurchaseState.PURCHASED))
        val sink = PlayProofSink { _, _, raw ->
            if (raw.token == "retry") throw SdkFailure("NETWORK_UNAVAILABLE")
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try { assertEquals(PlayRecoveryCounts(4, 1, 2, 1), provider.recoverDetailed()) }
        finally { provider.close() }
    }
    @Test fun `recovery shares the one transaction verification limit with callbacks`() = runBlocking {
        val gateway = FakePlayGateway(); gateway.recoveredPurchases = listOf(proof(Purchase.PurchaseState.PURCHASED))
        val entered = CompletableDeferred<Unit>(); val release = CompletableDeferred<Unit>(); val count = java.util.concurrent.atomic.AtomicInteger()
        val sink = PlayProofSink { _, _, raw ->
            if (count.incrementAndGet() == 1) { entered.complete(Unit); release.await() }
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try {
            gateway.listener!!.invoke(proof(Purchase.PurchaseState.PURCHASED)); withTimeout(2000) { entered.await() }
            val recovery = async { provider.recoverDetailed() }
            assertNull(withTimeoutOrNull(150) { recovery.await() }); assertEquals(1, count.get())
            release.complete(Unit); assertEquals(1, withTimeout(2000) { recovery.await() }.recovered); assertEquals(2, count.get())
        } finally { provider.close() }
    }

    @Test fun `concurrent recovery shares one query and caller cancellation does not stop it`() = runBlocking {
        val gateway = FakePlayGateway(); gateway.recoveredPurchases = listOf(proof(Purchase.PurchaseState.PURCHASED))
        val entered = CompletableDeferred<Unit>(); val release = CompletableDeferred<Unit>()
        val sink = PlayProofSink { _, _, raw ->
            entered.complete(Unit); release.await()
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try {
            val first = async { provider.recoverDetailed() }; withTimeout(2000) { entered.await() }
            val second = async(start = CoroutineStart.UNDISPATCHED) { provider.recoverDetailed() }
            first.cancel(); release.complete(Unit)
            assertEquals(1, withTimeout(2000) { second.await() }.recovered); assertEquals(1, gateway.recoveries)
        } finally { provider.close() }
    }
    @Test fun `recovery flight is not shared with a different account`() = runBlocking {
        val gateway = FakePlayGateway(); gateway.recoveredPurchases = listOf(proof(Purchase.PurchaseState.PURCHASED))
        val current = java.util.concurrent.atomic.AtomicReference(account)
        val entered = CompletableDeferred<Unit>(); val release = CompletableDeferred<Unit>()
        val sink = PlayProofSink { _, _, raw ->
            entered.complete(Unit); release.await()
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", UUID.randomUUID(), "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { current.get() }, sink)
        try {
            val first = async { runCatching { provider.recoverDetailed() }.exceptionOrNull() }
            withTimeout(2000) { entered.await() }; current.set(BoundPlayAccount(UUID.randomUUID(), UUID.randomUUID().toString()))
            assertEquals("CANCELED", assertFailsWith<SdkFailure> { provider.recoverDetailed() }.code)
            release.complete(Unit); assertEquals("CANCELED", (withTimeout(2000) { first.await() } as SdkFailure).code)
            assertEquals(1, gateway.recoveries)
        } finally { provider.close() }
    }

    @Test fun `pending to purchased verifies before one durable grant`() = runBlocking {
        val gateway = FakePlayGateway(); var verifies = 0; var grants = 0; val purchaseId = UUID.randomUUID()
        val sink = PlayProofSink { _, _, raw ->
            verifies++; if (grants == 0) grants++
            ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", purchaseId,
                if (verifies == 1) "GRANTED" else "ALREADY_GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try {
            assertEquals("PENDING", next(provider, gateway, proof(Purchase.PurchaseState.PENDING)).status)
            assertEquals(0, verifies); assertEquals(0, grants)
            val completed = next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED))
            assertEquals("PURCHASED", completed.status); assertEquals(purchaseId, completed.serverPurchaseId)
            val duplicate = next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED))
            assertEquals(purchaseId, duplicate.serverPurchaseId); assertEquals(2, verifies); assertEquals(1, grants)
        } finally { provider.close() }
    }
    @Test fun `timeout keeps purchase unfulfilled until later verification`() = runBlocking {
        val gateway = FakePlayGateway(); var fail = true; var grants = 0; val purchaseId = UUID.randomUUID()
        val sink = PlayProofSink { _, _, raw ->
            if (fail) throw SdkFailure("TIMEOUT", retryable = true)
            grants++; ServerPlayResult(account.userId, account.obfuscatedAccountId, "coins_100", purchaseId, "GRANTED", MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray()))
        }
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink)
        try {
            val pending = next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED))
            assertEquals("VERIFICATION_PENDING", pending.status); assertNull(pending.serverPurchaseId); assertEquals(0, grants)
            fail = false
            val recovered = next(provider, gateway, proof(Purchase.PurchaseState.PURCHASED))
            assertEquals("PURCHASED", recovered.status); assertEquals(purchaseId, recovered.serverPurchaseId); assertEquals(1, grants)
        } finally { provider.close() }
    }

}
