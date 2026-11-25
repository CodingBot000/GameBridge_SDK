package com.gamebridge.bridge

import com.gamebridge.android.purchase.GoogleStoreEvent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

/** Owns one adapter's Store and its purchase-event subscription. */
internal class BridgeStoreLifecycle<Store : AutoCloseable>(
    private val events: (Store) -> Flow<GoogleStoreEvent>,
    private val purchaseEmitter: () -> (GoogleStoreEvent) -> Unit,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var store: Store? = null
    private var eventJob: Job? = null

    fun activeStore(create: () -> Store, attachHost: (Store) -> Unit): Store {
        return (store ?: create().also { created ->
            val emit = purchaseEmitter()
            eventJob = scope.launch(start = CoroutineStart.UNDISPATCHED) { events(created).collect { emit(it) } }
            store = created
        }).also(attachHost)
    }

    fun dropStore() {
        eventJob?.cancel()
        eventJob = null
        store?.close()
        store = null
    }

    fun close() {
        dropStore()
        scope.cancel()
    }
}
