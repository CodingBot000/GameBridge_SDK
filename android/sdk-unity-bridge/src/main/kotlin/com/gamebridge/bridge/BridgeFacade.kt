package com.gamebridge.bridge

import android.app.Activity
import com.gamebridge.BridgeDispatcher
import com.gamebridge.BridgeDispatchResult
import com.gamebridge.LocalMockBridgeHandler
import com.gamebridge.android.auth.GoogleAuthProvider
import com.gamebridge.android.purchase.GooglePlayStore
import com.gamebridge.android.purchase.GoogleStoreEvent
import com.gamebridge.android.push.GooglePushClient
import com.gamebridge.android.push.AndroidPushHostAdapter
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import com.gamebridge.BridgeProtocol
import com.gamebridge.PurchaseStatus
import com.gamebridge.PushPayload
import com.gamebridge.PushRouter
import com.gamebridge.PushEventKind
import com.gamebridge.PushRouteEvent
import com.gamebridge.PushEnqueueResult
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
    private val localMock = LocalMockBridgeHandler(tokenStore = {
        val activity = host?.get() ?: throw com.gamebridge.SdkFailure("NOT_INITIALIZED")
        KeystoreTokenStore(activity.applicationContext, "unity_local_mock")
    }, pendingStore = {
        val activity = host?.get() ?: throw com.gamebridge.SdkFailure("NOT_INITIALIZED")
        KeystoreTokenStore(activity.applicationContext, "unity_mock_purchases")
    })
    private val google = GoogleAuthBridgeHandler { config, productIds, installationId ->
        val activity = host?.get() ?: throw com.gamebridge.SdkFailure("NOT_INITIALIZED")
        val provider = GoogleAuthProvider.create(activity.applicationContext, config, KeystoreTokenStore(activity.applicationContext, "unity_google"))
        val push = installationId?.let { GooglePushClient.create(provider, config, it) }
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
            override suspend fun recoverDetailed() = activeStore().recoverDetailed()
            override suspend fun registerPush(): String {
                val target = push ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED")
                val current = host?.get() ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED", "HOST_ACTIVITY")
                try { Class.forName("com.google.firebase.messaging.FirebaseMessaging") }
                catch (_: ClassNotFoundException) { throw com.gamebridge.SdkFailure("CONFIG_REQUIRED", "FIREBASE_HOST") }
                catch (_: LinkageError) { throw com.gamebridge.SdkFailure("CONFIG_REQUIRED", "FIREBASE_HOST") }
                val token = try { withTimeout(config.requestTimeoutMs) {
                    suspendCancellableCoroutine<String> { continuation ->
                        try {
                            val adapter = AndroidPushHostAdapter(
                                { if (continuation.isActive) continuation.resume(it) }, { _, _ -> },
                                { if (continuation.isActive) continuation.resumeWithException(com.gamebridge.SdkFailure("CONFIG_REQUIRED", "FIREBASE_HOST")) })
                            if (!adapter.hasNotificationPermission(current)) continuation.resumeWithException(com.gamebridge.SdkFailure("PERMISSION_DENIED"))
                            else adapter.register()
                        } catch (_: LinkageError) { if (continuation.isActive) continuation.resumeWithException(com.gamebridge.SdkFailure("CONFIG_REQUIRED", "FIREBASE_HOST")) }
                    }
                } } catch (_: TimeoutCancellationException) { throw com.gamebridge.SdkFailure("TIMEOUT", retryable = true) }
                return target.register(token)
            }
            override suspend fun registerPushToken(token: String): String = (push ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED")).register(token)
            override suspend fun unregisterPush() = (push ?: throw com.gamebridge.SdkFailure("CONFIG_REQUIRED")).unregister()
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
    private val pushRouter = PushRouter()
    @JvmStatic fun attachHost(activity: Activity) { host = WeakReference(activity) }
    @JvmStatic fun detachHost() { host?.clear(); host = null }
    @JvmStatic @Synchronized fun setCallback(value: BridgeCallback?) {
        callbackGeneration.incrementAndGet(); callback = value
        if (value == null) {
            eventSession = null; accountEpoch++; pushRouter.reset()
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
            request["operation"]?.jsonPrimitive?.content in setOf("auth.signIn", "auth.signOut", "sdk.shutdown")) {
            accountEpoch++; pushRouter.reset()
            if (request["operation"]?.jsonPrimitive?.content != "sdk.shutdown") pushRouter.setReady()
        }
    }
    @Synchronized private fun afterDispatch(bytes: ByteArray, generation: Long, result: BridgeDispatchResult) {
        if (generation != callbackGeneration.get() || result !is BridgeDispatchResult.Message) return
        val request = runCatching { BridgeProtocol.parse(bytes) }.getOrNull() ?: return
        val response = runCatching { BridgeProtocol.parse(result.json.toByteArray()) }.getOrNull() ?: return
        if (request["operation"] == JsonPrimitive("sdk.initialize") && response["ok"] == JsonPrimitive(true)) {
            val first = eventSession == null
            eventSession = request["sdkSessionId"]?.jsonPrimitive?.content
            if (first) pushRouter.setReady().forEach { emitPush(it) }
        }
        if (request["operation"] == JsonPrimitive("sdk.shutdown") && response["ok"] == JsonPrimitive(true)) eventSession = null
    }
    /** Returns QUEUED/DELIVER/DUPLICATE/BUSY, or INVALID_ARGUMENT; no arbitrary URL is opened. */
    @JvmStatic fun forwardNotification(messageId: String?, route: String?, campaignId: String?, opened: Boolean): String {
        val fields = mutableMapOf<String, String>()
        if (messageId != null) fields["messageId"] = messageId
        if (route != null) fields["route"] = route
        if (campaignId != null) fields["campaignId"] = campaignId
        val payload = PushPayload.parse(fields) ?: return "INVALID_ARGUMENT"
        val event = PushRouteEvent(payload, if (opened) PushEventKind.OPENED else PushEventKind.RECEIVED)
        val result = pushRouter.submit(event)
        if (result == PushEnqueueResult.DELIVER) emitPush(event)
        return result.name
    }
    @Synchronized private fun emitPush(event: PushRouteEvent) {
        val session = eventSession ?: return
        val send = callback ?: return
        val message = buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "event")
            put("eventId", UUID.randomUUID().toString()); put("occurredAt", Instant.now().toString())
            put("type", if (event.kind == PushEventKind.OPENED) "PushOpened" else "PushReceived")
            put("payload", buildJsonObject {
                put("messageId", event.payload.messageId); put("route", event.payload.route)
                put("campaignId", event.payload.campaignId?.let(::JsonPrimitive) ?: JsonNull)
            })
        }.toString()
        try { send.onMessage(message) } catch (_: Exception) { /* host owns callback */ }
    }
    /** A true result means queued, not that the Backend accepted the new token. */
    @JvmStatic @Synchronized fun forwardFcmToken(token: String?): Boolean {
        if (token.isNullOrBlank()) return false
        val session = eventSession ?: return false
        val generation = callbackGeneration.get(); val epoch = accountEpoch
        val request = buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "request")
            put("requestId", UUID.randomUUID().toString()); put("operation", "host.pushToken")
            put("payload", buildJsonObject { put("provider", "FCM"); put("token", token) })
        }.toString().toByteArray(Charsets.UTF_8)
        if (request.size > BridgeProtocol.MAX_BYTES) return false
        return try {
            executor.execute {
                if (isCurrentEventSession(generation, epoch, session)) {
                    val result = dispatcher.dispatch(request)
                    if (result is BridgeDispatchResult.Message) emitTokenResult(generation, epoch, session, result.json)
                }
            }; true
        } catch (_: RejectedExecutionException) { false }
    }
    @Synchronized private fun isCurrentEventSession(generation: Long, epoch: Long, session: String): Boolean =
        generation == callbackGeneration.get() && epoch == accountEpoch && session == eventSession && callback != null
    @Synchronized private fun emitTokenResult(generation: Long, epoch: Long, session: String, response: String) {
        if (!isCurrentEventSession(generation, epoch, session)) return
        val parsed = runCatching { BridgeProtocol.parse(response.toByteArray()) }.getOrNull() ?: return
        val ok = parsed["ok"] == JsonPrimitive(true)
        val fingerprint = if (ok) (parsed["result"] as? JsonObject)?.get("tokenFingerprint")?.jsonPrimitive?.content else null
        val allowed = setOf("NOT_INITIALIZED", "CONFIG_REQUIRED", "NETWORK_UNAVAILABLE", "TIMEOUT", "CANCELED", "BUSY", "SESSION_EXPIRED", "AUTH_FAILED", "PERMISSION_DENIED", "INTERNAL_ERROR", "BRIDGE_PROTOCOL_MISMATCH")
        val rawCode = if (!ok) (parsed["error"] as? JsonObject)?.get("code")?.jsonPrimitive?.content else null
        val success = ok && fingerprint?.matches(Regex("[0-9a-f]{12}")) == true
        val code = if (success) null else rawCode?.takeIf { it in allowed } ?: "INTERNAL_ERROR"
        val message = buildJsonObject {
            put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "event"); put("eventId", UUID.randomUUID().toString())
            put("occurredAt", Instant.now().toString()); put("type", "PushTokenChanged")
            put("payload", buildJsonObject {
                put("registered", success); put("tokenFingerprint", if (success) JsonPrimitive(fingerprint!!) else JsonNull)
                put("errorCode", code?.let(::JsonPrimitive) ?: JsonNull)
            })
        }.toString()
        try { callback?.onMessage(message) } catch (_: Exception) { /* host owns callback */ }
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
