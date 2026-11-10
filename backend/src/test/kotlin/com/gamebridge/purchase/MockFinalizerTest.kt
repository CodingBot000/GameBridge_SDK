package com.gamebridge.purchase

import org.junit.jupiter.api.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class MockFinalizerTest {
    @Test fun `mock finalizer fails first and succeeds later`() {
        val finalizer = MockFinalizer()
        assertFalse(finalizer.finish(1))
        assertTrue(finalizer.finish(2))
        assertTrue(finalizer.finish(3))
    }
}
