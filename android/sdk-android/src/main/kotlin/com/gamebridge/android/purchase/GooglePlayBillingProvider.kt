package com.gamebridge.android.purchase

import android.app.Activity
import android.content.Context
import com.android.billingclient.api.*
import com.gamebridge.MaintenanceGate
import com.gamebridge.ProtectedOperation
import com.gamebridge.ProductType
import com.gamebridge.SdkFailure
import com.gamebridge.StoreProduct
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.lang.ref.WeakReference
import java.security.MessageDigest
import java.util.UUID
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

internal data class PlayCatalogItem(val storeId: String, val title: String, val price: String, val currency: String, val micros: Long)
internal data class BoundPlayAccount(val userId: UUID, val obfuscatedAccountId: String) { override fun toString() = "BoundPlayAccount([redacted])" }
internal class RawPlayPurchase(val storeId: String, val token: String, val accountId: String?, val quantity: Int, val state: Int) {
    override fun toString() = "RawPlayPurchase([redacted])"
}
internal data class PlayPurchaseEvent(val productId: String, val status: String, val errorCode: String? = null, val serverPurchaseId: UUID? = null)
internal data class ServerPlayResult(val userId: UUID, val accountId: String, val productId: String, val serverPurchaseId: UUID, val fulfillmentStatus: String, val proofFingerprint: ByteArray) {
    override fun toString() = "ServerPlayResult([redacted])"
}
internal fun interface PlayAccountSource { suspend fun current(): BoundPlayAccount? }
internal fun interface PlayProofSink { suspend fun verify(account: BoundPlayAccount, productId: String, proof: RawPlayPurchase): ServerPlayResult }
internal interface PlayGateway {
    fun attach(activity: Activity)
    fun detach()
    fun setObserver(observer: ((RawPlayPurchase) -> Unit)?)
    suspend fun products(storeIds: List<String>): List<PlayCatalogItem>
    suspend fun launch(storeId: String, account: BoundPlayAccount): String
    suspend fun recover(): List<RawPlayPurchase>
    fun close()
}

/** Play UI is real; server verification is mandatory before any entitlement is reported. */
internal class GooglePlayBillingProvider(
    private val gateway: PlayGateway,
    private val productIds: Map<String, String>,
    private val accountSource: PlayAccountSource,
    private val proofSink: PlayProofSink?,
    private val verificationConcurrency: Int? = 1,
    private val uiGate: Mutex = Mutex(),
    private val maintenanceState: suspend () -> Boolean? = { null },
    private val readiness: suspend (String) -> Unit = { throw SdkFailure("CONFIG_REQUIRED") },
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val mutableEvents = MutableSharedFlow<PlayPurchaseEvent>(extraBufferCapacity = 100, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val proofQueue = Channel<RawPlayPurchase>(capacity = 100)
    val events: SharedFlow<PlayPurchaseEvent> = mutableEvents
    init {
        if (productIds.keys != setOf("coins_100", "premium_unlock") || productIds.values.any { it.isBlank() } || productIds.values.toSet().size != 2) throw SdkFailure("CONFIG_REQUIRED")
        if (verificationConcurrency != null && verificationConcurrency <= 0) throw SdkFailure("CONFIG_REQUIRED")
        if (verificationConcurrency != null) repeat(verificationConcurrency) {
            scope.launch {
                for (raw in proofQueue) try { process(raw) }
                catch (cancel: CancellationException) { throw cancel }
                catch (_: Exception) {
                    val product = productIds.entries.firstOrNull { it.value == raw.storeId }?.key
                    if (product != null) mutableEvents.emit(PlayPurchaseEvent(product, "VERIFICATION_PENDING"))
                }
            }
        }
        gateway.setObserver(::enqueue)
    }
    fun attachHost(activity: Activity) = gateway.attach(activity)
    fun detachHost() = gateway.detach()
    suspend fun products(): List<StoreProduct> {
        val byStore = gateway.products(productIds.values.toList()).associateBy { it.storeId }
        return productIds.map { (logical, storeId) ->
            val item = byStore[storeId] ?: throw SdkFailure("PRODUCT_NOT_FOUND")
            StoreProduct(logical, storeId, if (logical == "coins_100") ProductType.CONSUMABLE else ProductType.NON_CONSUMABLE,
                item.title, item.price, item.currency, item.micros.toString())
        }
    }
    suspend fun purchase(productId: String): String {
        val storeId = productIds[productId] ?: throw SdkFailure("PRODUCT_NOT_FOUND")
        val account = accountSource.current() ?: throw SdkFailure("SESSION_EXPIRED")
        if (runCatching { UUID.fromString(account.obfuscatedAccountId).toString() == account.obfuscatedAccountId }.getOrDefault(false).not()) throw SdkFailure("CONFIG_REQUIRED")
        // Do not open a real store UI until a real backend verification path is configured.
        if (proofSink == null || verificationConcurrency == null) throw SdkFailure("CONFIG_REQUIRED")
        val maintenance = try { maintenanceState() } catch (cancel: CancellationException) { throw cancel } catch (_: Exception) { null }
        if (!MaintenanceGate.permits(maintenance, ProtectedOperation.START_PURCHASE)) throw SdkFailure(if (maintenance == true) "MAINTENANCE" else "CONFIG_REQUIRED")
        readiness(storeId)
        if (accountSource.current() != account) throw SdkFailure("CANCELED")
        if (!uiGate.tryLock()) throw SdkFailure("BUSY")
        return try { gateway.launch(storeId, account) } finally { uiGate.unlock() }
    }
    suspend fun recover() { gateway.recover().forEach(::enqueue) }
    fun close() { gateway.setObserver(null); proofQueue.close(); gateway.close(); scope.cancel() }
    private fun enqueue(raw: RawPlayPurchase) {
        if (verificationConcurrency == null || !proofQueue.trySend(raw).isSuccess) {
            val product = productIds.entries.firstOrNull { it.value == raw.storeId }?.key ?: return
            val status = if (raw.state == Purchase.PurchaseState.PENDING) "PENDING" else "VERIFICATION_PENDING"
            mutableEvents.tryEmit(PlayPurchaseEvent(product, status))
        }
    }
    private suspend fun process(raw: RawPlayPurchase) {
        val product = productIds.entries.firstOrNull { it.value == raw.storeId }?.key ?: return
        val account = accountSource.current()
        if (account == null) { mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "SESSION_EXPIRED")); return }
        if (raw.token.isBlank()) { mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "VERIFICATION_FAILED")); return }
        if (raw.quantity != 1) { mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "UNSUPPORTED_OPERATION")); return }
        if (raw.accountId != account.obfuscatedAccountId) { mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "PURCHASE_ACCOUNT_MISMATCH")); return }
        when (raw.state) {
            Purchase.PurchaseState.PENDING -> mutableEvents.emit(PlayPurchaseEvent(product, "PENDING"))
            Purchase.PurchaseState.PURCHASED -> {
                val sink = proofSink
                if (sink == null) { mutableEvents.emit(PlayPurchaseEvent(product, "VERIFICATION_PENDING")); return }
                val verified = try { sink.verify(account, product, raw) } catch (failure: SdkFailure) {
                    if (failure.code in setOf("PURCHASE_ACCOUNT_MISMATCH", "VERIFICATION_FAILED", "UNSUPPORTED_OPERATION")) mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", failure.code))
                    else mutableEvents.emit(PlayPurchaseEvent(product, "VERIFICATION_PENDING"))
                    return
                } catch (_: CancellationException) { throw CancellationException() }
                catch (_: Exception) { mutableEvents.emit(PlayPurchaseEvent(product, "VERIFICATION_PENDING")); return }
                val current = accountSource.current()
                if (current?.userId != account.userId || current.obfuscatedAccountId != account.obfuscatedAccountId) return
                val fingerprint = MessageDigest.getInstance("SHA-256").digest(raw.token.toByteArray(Charsets.UTF_8))
                if (verified.userId != account.userId || verified.accountId != account.obfuscatedAccountId || verified.productId != product ||
                    !MessageDigest.isEqual(fingerprint, verified.proofFingerprint) || verified.fulfillmentStatus !in setOf("GRANTED", "ALREADY_GRANTED")) {
                    mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "PURCHASE_ACCOUNT_MISMATCH")); return
                }
                mutableEvents.emit(PlayPurchaseEvent(product, "PURCHASED", serverPurchaseId = verified.serverPurchaseId))
            }
            else -> mutableEvents.emit(PlayPurchaseEvent(product, "FAILED", "PURCHASE_FAILED"))
        }
    }
}

internal class PlayWaiterRouter<T : Any> {
    private var entry: Pair<String, T>? = null
    @Synchronized fun register(storeId: String, value: T) { check(entry == null); entry = storeId to value }
    @Synchronized fun take(terminal: Boolean, products: Set<String>): T? {
        val current = entry ?: return null
        if (!terminal && current.first !in products) return null
        entry = null; return current.second
    }
    @Synchronized fun remove(value: T) { if (entry?.second === value) entry = null }
}

/** Concrete Play Billing 9 gateway; does not consume or acknowledge on the client. */
internal class AndroidPlayGateway(context: Context) : PlayGateway {
    private data class Waiter(val storeId: String, val accountId: String, val response: CompletableDeferred<String>)
    private val gate = Mutex()
    private val connectionGate = Mutex()
    private val router = PlayWaiterRouter<Waiter>()
    @Volatile private var closed = false
    @Volatile private var host: WeakReference<Activity>? = null
    @Volatile private var observer: ((RawPlayPurchase) -> Unit)? = null
    private val client: BillingClient = BillingClient.newBuilder(context.applicationContext)
        .setListener { result, purchases -> onUpdates(result, purchases) }
        .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
        .enableAutoServiceReconnection().build()

    override fun attach(activity: Activity) { host = WeakReference(activity) }
    override fun detach() { host?.clear(); host = null }
    override fun setObserver(observer: ((RawPlayPurchase) -> Unit)?) { this.observer = observer }
    override fun close() { closed = true; router.take(true, emptySet())?.response?.cancel(); observer = null; client.endConnection() }
    private suspend fun connect() = connectionGate.withLock {
        if (closed) throw SdkFailure("NOT_INITIALIZED")
        if (client.isReady) return@withLock
        suspendCancellableCoroutine<Unit> { continuation ->
            client.startConnection(object : BillingClientStateListener {
                override fun onBillingSetupFinished(result: BillingResult) {
                    if (!continuation.isActive) return
                    if (result.responseCode == BillingClient.BillingResponseCode.OK) continuation.resume(Unit)
                    else continuation.resumeWithException(failure(result))
                }
                override fun onBillingServiceDisconnected() {
                    if (continuation.isActive) continuation.resumeWithException(SdkFailure("STORE_UNAVAILABLE"))
                }
            })
        }
    }
    private suspend fun query(storeIds: List<String>): List<ProductDetails> {
        connect()
        val products = storeIds.map { QueryProductDetailsParams.Product.newBuilder().setProductId(it).setProductType(BillingClient.ProductType.INAPP).build() }
        val params = QueryProductDetailsParams.newBuilder().setProductList(products).build()
        return suspendCancellableCoroutine { continuation ->
            client.queryProductDetailsAsync(params) { result, details ->
                if (!continuation.isActive) return@queryProductDetailsAsync
                if (result.responseCode != BillingClient.BillingResponseCode.OK) continuation.resumeWithException(failure(result))
                else continuation.resume(details.productDetailsList)
            }
        }
    }
    @Suppress("DEPRECATION")
    override suspend fun products(storeIds: List<String>): List<PlayCatalogItem> = try {
        withTimeout(30_000) {
            query(storeIds).mapNotNull { details ->
                val offer = details.oneTimePurchaseOfferDetails ?: return@mapNotNull null
                PlayCatalogItem(details.productId, details.title, offer.formattedPrice, offer.priceCurrencyCode, offer.priceAmountMicros)
            }
        }
    } catch (_: TimeoutCancellationException) { throw SdkFailure("TIMEOUT") }
    @Suppress("DEPRECATION")
    override suspend fun launch(storeId: String, account: BoundPlayAccount): String = try {
        withTimeout(180_000) { launchWithinDeadline(storeId, account) }
    } catch (_: TimeoutCancellationException) { throw SdkFailure("TIMEOUT") }
    private suspend fun launchWithinDeadline(storeId: String, account: BoundPlayAccount): String {
        if (!gate.tryLock()) throw SdkFailure("BUSY")
        try {
            if (closed) throw SdkFailure("NOT_INITIALIZED")
            val activity = host?.get()?.takeUnless { it.isFinishing || it.isDestroyed } ?: throw SdkFailure("CONFIG_REQUIRED", "HOST_ACTIVITY")
            val details = query(listOf(storeId)).singleOrNull { it.productId == storeId } ?: throw SdkFailure("PRODUCT_NOT_FOUND")
            val offer = details.oneTimePurchaseOfferDetails ?: throw SdkFailure("PRODUCT_NOT_FOUND")
            val builder = BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(details)
            offer.offerToken?.takeIf { it.isNotBlank() }?.let { builder.setOfferToken(it) }
            val params = BillingFlowParams.newBuilder().setObfuscatedAccountId(account.obfuscatedAccountId)
                .setProductDetailsParamsList(listOf(builder.build())).build()
            if (closed) throw SdkFailure("NOT_INITIALIZED")
            val pending = Waiter(storeId, account.obfuscatedAccountId, CompletableDeferred())
            router.register(storeId, pending)
            try {
                val result = withContext(Dispatchers.Main.immediate) { client.launchBillingFlow(activity, params) }
                if (result.responseCode != BillingClient.BillingResponseCode.OK) throw failure(result)
                return pending.response.await()
            } finally { router.remove(pending); pending.response.cancel() }
        } finally { gate.unlock() }
    }
    override suspend fun recover(): List<RawPlayPurchase> = try { withTimeout(30_000) {
        connect()
        val params = QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()
        suspendCancellableCoroutine { continuation ->
            client.queryPurchasesAsync(params) { result, purchases ->
                if (!continuation.isActive) return@queryPurchasesAsync
                if (result.responseCode != BillingClient.BillingResponseCode.OK) continuation.resumeWithException(failure(result))
                else continuation.resume(purchases.mapNotNull(::raw))
            }
        }
    } } catch (_: TimeoutCancellationException) { throw SdkFailure("TIMEOUT") }
    private fun onUpdates(result: BillingResult, purchases: List<Purchase>?) {
        val raw = purchases.orEmpty().mapNotNull(::raw)
        raw.forEach { observer?.invoke(it) } // Also processes callbacks arriving after UI timeout.
        val pending = router.take(result.responseCode != BillingClient.BillingResponseCode.OK, purchases.orEmpty().flatMap { it.products }.toSet()) ?: return
        if (result.responseCode != BillingClient.BillingResponseCode.OK) { pending.response.completeExceptionally(failure(result)); return }
        val original = purchases.orEmpty().singleOrNull { pending.storeId in it.products }
        if (original != null && (original.products.size != 1 || original.quantity != 1)) { pending.response.completeExceptionally(SdkFailure("UNSUPPORTED_OPERATION")); return }
        val match = raw.singleOrNull { it.storeId == pending.storeId }
        if (match == null) { pending.response.completeExceptionally(SdkFailure("PURCHASE_FAILED")); return }
        if (match.quantity != 1) { pending.response.completeExceptionally(SdkFailure("UNSUPPORTED_OPERATION")); return }
        if (match.accountId != pending.accountId) { pending.response.completeExceptionally(SdkFailure("PURCHASE_ACCOUNT_MISMATCH")); return }
        when (match.state) {
            Purchase.PurchaseState.PENDING -> pending.response.complete("PENDING")
            Purchase.PurchaseState.PURCHASED -> pending.response.complete("VERIFICATION_PENDING")
            else -> pending.response.completeExceptionally(SdkFailure("PURCHASE_FAILED"))
        }
    }
    private fun raw(purchase: Purchase): RawPlayPurchase? {
        if (purchase.products.size != 1 || purchase.purchaseToken.isBlank()) return null
        return RawPlayPurchase(purchase.products.single(), purchase.purchaseToken, purchase.accountIdentifiers?.obfuscatedAccountId, purchase.quantity, purchase.purchaseState)
    }
    private fun failure(result: BillingResult): SdkFailure = when (result.responseCode) {
        BillingClient.BillingResponseCode.USER_CANCELED -> SdkFailure("CANCELED", result.responseCode.toString())
        BillingClient.BillingResponseCode.ITEM_UNAVAILABLE -> SdkFailure("PRODUCT_NOT_FOUND", result.responseCode.toString())
        BillingClient.BillingResponseCode.DEVELOPER_ERROR -> SdkFailure("CONFIG_REQUIRED", result.responseCode.toString())
        BillingClient.BillingResponseCode.SERVICE_DISCONNECTED, BillingClient.BillingResponseCode.SERVICE_UNAVAILABLE, BillingClient.BillingResponseCode.NETWORK_ERROR -> SdkFailure("STORE_UNAVAILABLE", result.responseCode.toString())
        else -> SdkFailure("PURCHASE_FAILED", result.responseCode.toString())
    }
}
