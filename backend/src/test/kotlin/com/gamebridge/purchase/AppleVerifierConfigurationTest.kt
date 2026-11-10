package com.gamebridge.purchase

import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Test
import org.springframework.web.server.ResponseStatusException
import kotlin.test.*

class AppleVerifierConfigurationTest {
    @Test fun `missing and malformed config fail closed on use`() {
        val absent = ConfiguredAppleVerifierRegistry("", ObjectMapper())
        assertEquals(503, assertFailsWith<ResponseStatusException> { absent.verifier("app", StoreEnvironment.SANDBOX) }.statusCode.value())
        val malformed = ConfiguredAppleVerifierRegistry("""{"app":{"bundleId":"com.example","productIds":["coins"],"rootCertificatePaths":["/not-present/gamebridge-root"]}}""", ObjectMapper())
        assertEquals(503, assertFailsWith<ResponseStatusException> { malformed.verifier("app", StoreEnvironment.SANDBOX) }.statusCode.value())
        assertEquals(503, assertFailsWith<ResponseStatusException> { malformed.verifier("other", StoreEnvironment.PRODUCTION) }.statusCode.value())
    }
}
