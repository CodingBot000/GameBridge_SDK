package com.gamebridge.push

import org.junit.jupiter.api.Test
import org.springframework.web.server.ResponseStatusException
import java.time.Duration
import java.time.Instant
import kotlin.test.*

class PublicServiceConfigControllerTest {
    @Test fun `missing config fails closed and explicit setting has approved ttl`() {
        assertEquals(503, assertFailsWith<ResponseStatusException> { PublicServiceConfigController("", "", 300).config() }.statusCode.value())
        assertEquals(503, assertFailsWith<ResponseStatusException> { PublicServiceConfigController("invalid", "", 300).config() }.statusCode.value())
        val before = Instant.now(); val value = PublicServiceConfigController("false", "", 300).config()
        assertEquals(false, value["maintenanceEnabled"]); assertEquals("REMOTE", value["source"])
        val revision = value["revision"] as String
        assertTrue(revision.toLong() >= 0); assertEquals(revision, PublicServiceConfigController("false", "", 300).config()["revision"])
        assertNotEquals(revision, PublicServiceConfigController("true", "maintenance", 300).config()["revision"])
        assertTrue(Duration.between(before, Instant.parse(value["expiresAt"] as String)).seconds in 299..301)
        assertEquals(true, PublicServiceConfigController("true", "maintenance", 300).config()["maintenanceEnabled"])
        assertEquals(503, assertFailsWith<ResponseStatusException> { PublicServiceConfigController("false", "", 0).config() }.statusCode.value())
    }
}
