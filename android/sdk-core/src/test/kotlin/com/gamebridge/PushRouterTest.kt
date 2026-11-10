package com.gamebridge

import org.junit.jupiter.api.Test
import kotlin.test.*

class PushRouterTest {
    private fun event(id: String, kind: PushEventKind = PushEventKind.RECEIVED) = PushRouteEvent(PushPayload(id, "home", null), kind)
    @Test fun `queues until ready and preserves open separately from duplicate receive`() {
        val router = PushRouter(); val received = event("id"); val opened = event("id", PushEventKind.OPENED)
        assertEquals(PushEnqueueResult.QUEUED, router.submit(received)); assertEquals(PushEnqueueResult.DUPLICATE, router.submit(received))
        assertEquals(PushEnqueueResult.QUEUED, router.submit(opened)); assertEquals(listOf(received, opened), router.setReady())
        assertEquals(PushEnqueueResult.DUPLICATE, router.submit(opened)); router.reset()
        assertEquals(PushEnqueueResult.QUEUED, router.submit(received))
    }
    @Test fun `queue capacity and 200 recent ids are bounded`() {
        val router = PushRouter(); repeat(100) { assertEquals(PushEnqueueResult.QUEUED, router.submit(event("q$it"))) }
        assertEquals(PushEnqueueResult.BUSY, router.submit(event("overflow"))); assertEquals(100, router.setReady().size)
        assertEquals(PushEnqueueResult.DELIVER, router.submit(event("overflow")))
        repeat(200) { router.submit(event("new$it")) }
        assertEquals(PushEnqueueResult.DELIVER, router.submit(event("q0")))
        assertEquals(PushEnqueueResult.DUPLICATE, router.submit(event("new199")))
        assertEquals(PushEnqueueResult.DUPLICATE, router.submit(event("new1")))
        assertEquals(PushEnqueueResult.DELIVER, router.submit(event("new200")))
        assertEquals(PushEnqueueResult.DUPLICATE, router.submit(event("new1")))
        assertEquals(PushEnqueueResult.DELIVER, router.submit(event("new2")))
    }
}
