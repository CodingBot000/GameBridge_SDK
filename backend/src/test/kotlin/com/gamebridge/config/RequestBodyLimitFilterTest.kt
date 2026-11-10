package com.gamebridge.config

import com.fasterxml.jackson.databind.ObjectMapper
import jakarta.servlet.FilterChain
import org.junit.jupiter.api.Test
import org.springframework.mock.web.MockFilterChain
import org.springframework.mock.web.MockHttpServletRequest
import org.springframework.mock.web.MockHttpServletResponse
import kotlin.test.*

class RequestBodyLimitFilterTest {
    private val mapper = ObjectMapper()
    private fun run(size: Int, unknownLength: Boolean): Pair<MockHttpServletResponse, MockFilterChain> {
        val request = object : MockHttpServletRequest("POST", "/v1/test") {
            override fun getContentLengthLong(): Long = if (unknownLength) -1 else super.getContentLengthLong()
        }
        request.setContent(ByteArray(size) { 'x'.code.toByte() })
        val response = MockHttpServletResponse(); val chain = MockFilterChain()
        val next = FilterChain { req, res -> RequestBodyLimitFilter(mapper).doFilter(req, res, chain) }
        RequestIdFilter().doFilter(request, response, next)
        return response to chain
    }
    @Test fun `exact limit is forwarded and unknown length excess is rejected`() {
        val (allowed, chain) = run(RequestBodyLimitFilter.MAX_BYTES, true)
        assertEquals(200, allowed.status); assertEquals(RequestBodyLimitFilter.MAX_BYTES, chain.request!!.inputStream.readAllBytes().size)
        for (unknown in listOf(false, true)) {
            val (response, rejected) = run(RequestBodyLimitFilter.MAX_BYTES + 1, unknown)
            assertEquals(413, response.status); assertNull(rejected.request)
            val body = mapper.readTree(response.contentAsByteArray)
            assertEquals("PAYLOAD_TOO_LARGE", body["code"].asText()); assertEquals(response.getHeader("X-Request-Id"), body["requestId"].asText())
        }
    }
}
