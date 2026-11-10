package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Test
import kotlin.test.*

class AudiencePolicyTest {
    @Test fun `audiences are scoped by app and provider and missing config fails closed`() {
        val policy = AudiencePolicy.parse("""{"native":{"GOOGLE":["web-client"],"APPLE":["native.bundle"]},"unity":{"APPLE":["unity.bundle"]}}""", ObjectMapper())
        assertEquals(setOf("web-client"), policy.allowed("native", IdentityProvider.GOOGLE))
        assertEquals(setOf("unity.bundle"), policy.allowed("unity", IdentityProvider.APPLE))
        assertEquals("CONFIG_REQUIRED", assertFailsWith<AuthFlowException> { policy.allowed("unity", IdentityProvider.GOOGLE) }.code)
        assertEquals("CONFIG_REQUIRED", assertFailsWith<AuthFlowException> { AudiencePolicy.parse(null, ObjectMapper()).allowed("native", IdentityProvider.GOOGLE) }.code)
        assertFailsWith<IllegalArgumentException> { AudiencePolicy.parse("{broken", ObjectMapper()) }
    }
}
