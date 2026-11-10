package com.gamebridge.push

import org.junit.jupiter.api.Test
import java.time.Duration
import kotlin.test.*

class PushPoliciesTest {
    @Test fun `three retries use exponential delays with APNs server minimum`() {
        val policy = PushRetryPolicy()
        assertEquals(listOf(5L, 10L, 20L), (0..2).map { policy.delay(PushProvider.FCM, PushFailure.SERVER_ERROR, it)!!.seconds })
        assertEquals(listOf(900L, 900L, 900L), (0..2).map { policy.delay(PushProvider.APNS, PushFailure.SERVER_ERROR, it)!!.seconds })
        assertEquals(5L, policy.delay(PushProvider.APNS, PushFailure.RATE_LIMIT, 0)!!.seconds)
        assertNull(policy.delay(PushProvider.FCM, PushFailure.TIMEOUT, 3))
        assertNull(policy.delay(PushProvider.APNS, PushFailure.INVALID_TOKEN, 0))
    }
    @Test fun `dev admin keys have independent rolling minute limits`() {
        var now = 0L; val limiter = DevPushRateLimiter(nanoTime = { now })
        repeat(10) { assertTrue(limiter.allow("test-key-a")) }
        assertFalse(limiter.allow("test-key-a")); assertTrue(limiter.allow("test-key-b"))
        now = Duration.ofSeconds(59).toNanos(); assertFalse(limiter.allow("test-key-a"))
        now = Duration.ofSeconds(60).toNanos(); assertTrue(limiter.allow("test-key-a"))
    }
}
