package com.gamebridge.contracts

import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.jupiter.api.Test
import kotlin.test.*
class OpenApiCaptureTest {
    @Test fun `structural evidence erases nested strings while preserving schema types`() {
        val mapper=ObjectMapper()
        val shape=OpenApiCapture.shape(mapper.readTree("""{"accessToken":"synthetic-sensitive-token","nested":[{"proof":"synthetic-sensitive-proof"}],"ok":true,"count":4,"nullable":null}"""))
        val encoded=mapper.writeValueAsString(shape)
        assertFalse(encoded.contains("synthetic-sensitive-token"));assertFalse(encoded.contains("synthetic-sensitive-proof"))
        val result=mapper.readTree(encoded)
        assertEquals("redacted",result["accessToken"].asText());assertEquals("redacted",result["nested"][0]["proof"].asText())
        assertTrue(result["ok"].isBoolean);assertTrue(result["count"].isIntegralNumber);assertTrue(result["nullable"].isNull)
    }
}
