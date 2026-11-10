package com.gamebridge.purchase

import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Test
import org.springframework.web.server.ResponseStatusException
import kotlin.test.*

class GoogleVerifierConfigurationTest {
    @Test fun `unconfigured provider fails closed without reading ambient credentials`() {
        val registry = ConfiguredGoogleVerifierRegistry("", ObjectMapper())
        assertEquals(503, assertFailsWith<ResponseStatusException> { registry.verifier("app", StoreEnvironment.SANDBOX) }.statusCode.value())
        val missing = ConfiguredGoogleVerifierRegistry("""{"app":{"packageName":"test.package","productIds":["coins"],"credentialPath":"/not-present/google-service-account"}}""", ObjectMapper())
        assertEquals(503, assertFailsWith<ResponseStatusException> { missing.verifier("app", StoreEnvironment.SANDBOX) }.statusCode.value())
    }
}
