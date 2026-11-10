package com.gamebridge.purchase

import org.junit.jupiter.api.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class MockFinalizerTest {
    @Test fun `backoff starts at five seconds and doubles`() {
        val policy = FinalizationPolicy(1, 5, 5000)
        val now = java.time.Instant.parse("2026-01-01T00:00:00Z")
        assertTrue(policy.retryAt(1, now) == now.plusSeconds(5))
        assertTrue(policy.retryAt(2, now) == now.plusSeconds(10))
        assertTrue(policy.retryAt(3, now) == now.plusSeconds(20))
    }
    @Test fun `mock finalizer fails first and succeeds later`() {
        val finalizer = MockFinalizer()
        assertFalse(finalizer.finish(1))
        assertTrue(finalizer.finish(2))
        assertTrue(finalizer.finish(3))
    }
}
