package com.gamebridge.bridge

import android.app.Activity
import com.gamebridge.BridgeDispatcher
import com.gamebridge.BridgeDispatchResult
import com.gamebridge.LocalMockBridgeHandler
import com.gamebridge.android.auth.GoogleAuthProvider
import com.gamebridge.android.purchase.GooglePlayStore
import com.gamebridge.android.purchase.GoogleStoreEvent
import com.gamebridge.BridgeProtocol
import com.gamebridge.PurchaseStatus
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.collect
import kotlinx.serialization.json.*
import java.time.Instant
import java.util.UUID
import com.gamebridge.android.KeystoreTokenStore
import java.lang.ref.WeakReference
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicBoolean

fun interface BridgeCallback { fun onMessage(json: String) }

/** No Unity runtime linkage; a Unity AndroidJavaProxy may supply the callback. */
object BridgeFacade {
    private val executor = ThreadPoolExecutor(1, 1, 0, TimeUnit.MILLISECONDS, ArrayBlockingQueue(100))
    private val localMock = LocalMockBridgeHandler {
        val activity = host?.get() ?: throw com.gamebridge.SdkFailure("NOT_INITIALIZED")
        KeystoreTokenStore(activity.applicationContext, "unity_local_mock")
    }
    private val google = GoogleAuthBridgeHandler { config, productIds ->
        val activity = host?.get() ?: throw com.gamebridge.SdkFailure("NOT_INITIALIZED")
        val provider = GoogleAuthProvider.create(activity.applicationContext, config, KeystoreTokenStore(activity.applicationContext, "unity_google"))
        object : GoogleAuthBridgeApi {
            private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
            private var store: GooglePlayStore? = null
            private var eventJob: Job? = null
            private fun dropStore() { eventJob?.cancel(); eventJob = null; store?.close(); store = null }
            private fun activeStore(): GooglePlayStore {
                val current = host?.get() ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED", "HOST_ACTIVITY")
                val ids = productIds ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED")
                return (store ?: GooglePlayStore.create(current.applicationContext, config, provider, ids).also { created ->
                    val emitter = purchaseEmitter()
                    eventJob = scope.launch(start = CoroutineStart.UNDISPATCHED) { created.events.collect { emitter(it) } }
                    store = created
                }).also { it.attachHost(current) }
            }
            override suspend fun signIn(): com.gamebridge.UserProfile {
                dropStore()
                val current = host?.get() ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED", "HOST_ACTIVITY")
                provider.attachHost(current)
                return provider.signIn()
            }
            override suspend fun restore() = provider.restore()
            override suspend fun signOut() { dropStore(); provider.signOut() }
            override suspend fun products() = activeStore().products()
            override suspend fun purchase(productId: String) = activeStore().purchase(productId)
            override suspend fun entitlements() = activeStore().entitlements()
            override fun close() { dropStore(); scope.cancel(); provider.detachHost() }
        }
    }
    private val dispatcher = BridgeDispatcher(ModeBridgeHandler(localMock, google))
    private val callbackGeneration = AtomicLong()
    private val resetRequired = AtomicBoolean(false)
    @Volatile private var host: WeakReference<Activity>? = null
    @Volatile private var callback: BridgeCallback? = null
    private var eventSession: String? = null
    private var accountEpoch: Long = 0
    @JvmStatic fun attachHost(activity: Activity) { host = WeakReference(activity) }
    @JvmStatic fun detachHost() { host?.clear(); host = null }
    @JvmStatic @Synchronized fun setCallback(value: BridgeCallback?) {
        callbackGeneration.incrementAndGet(); callback = value
        if (value == null) {
            eventSession = null; accountEpoch++
            resetRequired.set(true)
            try { executor.execute { resetIfRequired() } }
            catch (_: RejectedExecutionException) { /* next accepted request performs cleanup */ }
        }
    }
    private fun resetIfRequired() {
        if (resetRequired.getAndSet(false)) dispatcher.reset()
    }
    @JvmStatic fun dispatch(json: String) {
        val bytes = json.toByteArray(Charsets.UTF_8)
        val generation = callbackGeneration.get()
        try { executor.execute {
            if (generation == callbackGeneration.get()) {
                resetIfRequired()
                beforeDispatch(bytes, generation)
                val result = dispatcher.dispatch(bytes)
                afterDispatch(bytes, generation, result)
                deliverIfCurrent(generation, result)
            }
        } }
        catch (_: RejectedExecutionException) { deliverIfCurrent(generation, dispatcher.busy(bytes)) }
    }
    @Synchronized private fun beforeDispatch(bytes: ByteArray, generation: Long) {
        val request = runCatching { BridgeProtocol.parse(bytes) }.getOrNull() ?: return
        if (generation == callbackGeneration.get() && request["sdkSessionId"]?.jsonPrimitive?.content == eventSession &&
            request["operation"]?.jsonPrimitive?.content in setOf("auth.signIn", "auth.signOut", "sdk.shutdown")) accountEpoch++
    }
    @Synchronized private fun afterDispatch(bytes: ByteArray, generation: Long, result: BridgeDispatchResult) {
        if (generation != callbackGeneration.get() || result !is BridgeDispatchResult.Message) return
        val request = runCatching { BridgeProtocol.parse(bytes) }.getOrNull() ?: return
        val response = runCatching { BridgeProtocol.parse(result.json.toByteArray()) }.getOrNull() ?: return
        if (request["operation"] == JsonPrimitive("sdk.initialize") && response["ok"] == JsonPrimitive(true))
            eventSession = request["sdkSessionId"]?.jsonPrimitive?.content
        if (request["operation"] == JsonPrimitive("sdk.shutdown") && response["ok"] == JsonPrimitive(true)) eventSession = null
    }
    @Synchronized private fun purchaseEmitter(): (GoogleStoreEvent) -> Unit {
        val generation = callbackGeneration.get(); val epoch = accountEpoch; val session = eventSession
        return { event -> emitPurchase(generation, epoch, session, event) }
    }
    @Synchronized private fun emitPurchase(generation: Long, epoch: Long, session: String?, event: GoogleStoreEvent) {
        if (session == null || session != eventSession || generation != callbackGeneration.get() || epoch != accountEpoch ||
            event.productId !in setOf("coins_100", "premium_unlock") ||
            (event.status == PurchaseStatus.PURCHASED && event.serverPurchaseId == null)) return
        val safeCodes = setOf("SESSION_EXPIRED", "VERIFICATION_FAILED", "UNSUPPORTED_OPERATION", "PURCHASE_ACCOUNT_MISMATCH", "PURCHASE_FAILED")
        val code = event.errorCode?.let { if (it in safeCodes) it else "INTERNAL_ERROR" }
        val message = buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "event")
            put("eventId", UUID.randomUUID().toString()); put("type", "PurchaseUpdated"); put("occurredAt", Instant.now().toString())
            put("payload", buildJsonObject {
                put("productId", event.productId); put("status", event.status.name)
                put("serverPurchaseId", event.serverPurchaseId?.let { JsonPrimitive(it.toString()) } ?: JsonNull)
                put("errorCode", code?.let(::JsonPrimitive) ?: JsonNull)
            })
        }.toString()
        try { callback?.onMessage(message) } catch (_: Exception) { /* host owns its callback */ }
    }
    @Synchronized private fun deliverIfCurrent(generation: Long, result: BridgeDispatchResult) {
        if (result is BridgeDispatchResult.Message && generation == callbackGeneration.get()) {
            try { callback?.onMessage(result.json) } catch (_: Exception) { /* host owns its callback */ }
        }
    }
}
