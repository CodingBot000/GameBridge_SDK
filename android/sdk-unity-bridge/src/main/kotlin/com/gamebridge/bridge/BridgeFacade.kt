package com.gamebridge.bridge

import android.app.Activity
import com.gamebridge.BridgeDispatcher
import com.gamebridge.BridgeDispatchResult
import java.lang.ref.WeakReference
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong

fun interface BridgeCallback { fun onMessage(json: String) }

/** No Unity runtime linkage; a Unity AndroidJavaProxy may supply the callback. */
object BridgeFacade {
    private val executor = ThreadPoolExecutor(1, 1, 0, TimeUnit.MILLISECONDS, ArrayBlockingQueue(100))
    private val dispatcher = BridgeDispatcher()
    private val callbackGeneration = AtomicLong()
    @Volatile private var host: WeakReference<Activity>? = null
    @Volatile private var callback: BridgeCallback? = null
    @JvmStatic fun attachHost(activity: Activity) { host = WeakReference(activity) }
    @JvmStatic fun detachHost() { host?.clear(); host = null }
    @JvmStatic @Synchronized fun setCallback(value: BridgeCallback?) { callbackGeneration.incrementAndGet(); callback = value }
    @JvmStatic fun dispatch(json: String) {
        val bytes = json.toByteArray(Charsets.UTF_8)
        val generation = callbackGeneration.get()
        try { executor.execute { deliverIfCurrent(generation, dispatcher.dispatch(bytes)) } }
        catch (_: RejectedExecutionException) { deliverIfCurrent(generation, dispatcher.busy(bytes)) }
    }
    @Synchronized private fun deliverIfCurrent(generation: Long, result: BridgeDispatchResult) {
        if (result is BridgeDispatchResult.Message && generation == callbackGeneration.get()) {
            try { callback?.onMessage(result.json) } catch (_: Exception) { /* host owns its callback */ }
        }
    }
}
