package com.gamebridge.bridge

import com.gamebridge.PurchaseStatus
import com.gamebridge.android.purchase.GoogleStoreEvent
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertSame

class BridgeStoreLifecycleTest {
    private class Store(val event: GoogleStoreEvent, val closeAction: () -> Unit) : AutoCloseable {
        val detached = CompletableDeferred<Unit>()
        val events = flow {
            try {
                emit(event)
                awaitCancellation()
            } finally {
                detached.complete(Unit)
            }
        }

        override fun close() = closeAction()
    }

    @Test fun `lazy store subscribes before attach and recreates after drop`() = runBlocking {
        val calls = mutableListOf<String>()
        val lifecycle = BridgeStoreLifecycle(Store::events) {
            calls += "capture"
            { event: GoogleStoreEvent -> calls += event.productId }
        }
        val first = Store(GoogleStoreEvent("first", PurchaseStatus.PENDING, null, null)) { calls += "close first" }
        val second = Store(GoogleStoreEvent("second", PurchaseStatus.PENDING, null, null)) { calls += "close second" }
        lifecycle.dropStore()
        assertSame(first, lifecycle.activeStore({ calls += "create"; first }) { calls += "attach first" })
        assertSame(first, lifecycle.activeStore({ error("must reuse") }) { calls += "attach replacement host" })
        lifecycle.dropStore()
        lifecycle.dropStore()
        withTimeout(1000) { first.detached.await() }
        assertSame(second, lifecycle.activeStore({ second }) { calls += "attach second" })
        lifecycle.close()
        withTimeout(1000) { second.detached.await() }
        assertEquals(listOf("create", "capture", "first", "attach first", "attach replacement host",
            "close first", "capture", "second", "attach second", "close second"), calls)
    }

    @Test fun `failed close propagates and retains store until close succeeds`() {
        var shouldFail = true
        val lifecycle = BridgeStoreLifecycle(Store::events) { { } }
        val store = Store(GoogleStoreEvent("product", PurchaseStatus.PENDING, null, null)) {
            check(!shouldFail)
        }
        lifecycle.activeStore({ store }) { }
        assertFailsWith<IllegalStateException> { lifecycle.dropStore() }
        assertSame(store, lifecycle.activeStore({ error("must retain after failure") }) { })
        shouldFail = false
        lifecycle.close()
    }
}
