package com.gamebridge.android.purchase

import android.app.Activity
import com.android.billingclient.api.Purchase
import com.gamebridge.SdkFailure
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import org.junit.jupiter.api.Test
import java.security.MessageDigest
import java.util.UUID
import kotlin.test.*

private class FakePlayGateway : PlayGateway {
    var listener: ((RawPlayPurchase) -> Unit)? = null
    var launches = 0
    override fun attach(activity: Activity) {}
    override fun detach() {}
    override fun setObserver(observer: ((RawPlayPurchase) -> Unit)?) { this.listener = observer }
    override suspend fun products(storeIds: List<String>) = storeIds.map { PlayCatalogItem(it, "title-$it", "₩1,000", "KRW", 1_000_000) }
    override suspend fun launch(storeId: String, account: BoundPlayAccount): String { launches++; return "VERIFICATION_PENDING" }
    override suspend fun recover(): List<RawPlayPurchase> = emptyList()
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
        val provider = GooglePlayBillingProvider(gateway, mapping, PlayAccountSource { account }, sink, verificationConcurrency = 1)
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
}
