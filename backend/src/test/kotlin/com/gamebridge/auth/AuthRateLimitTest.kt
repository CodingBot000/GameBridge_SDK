package com.gamebridge.auth

import org.junit.jupiter.api.Test
import kotlin.test.*

class AuthRateLimitTest {
    @Test fun `per ip and operation rolling limits reset after one minute`() {
        var now = 0L
        val limiter = AuthRateLimiter(30, 10) { now }
        repeat(30) { assertTrue(limiter.allow("127.0.0.1", "challenge")) }
        assertFalse(limiter.allow("127.0.0.1", "challenge"))
        repeat(10) { assertTrue(limiter.allow("127.0.0.1", "exchange")) }
        assertFalse(limiter.allow("127.0.0.1", "exchange"))
        assertTrue(limiter.allow("127.0.0.2", "challenge"))
        now += 60_000_000_000L
        assertTrue(limiter.allow("127.0.0.1", "challenge")); assertTrue(limiter.allow("127.0.0.1", "exchange"))
    }
}
