package com.gamebridge.config

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.slf4j.LoggerFactory
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.context.annotation.Profile
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

/** Opt-in development evidence: never records headers, body, query, tokens or user IDs. */
@Component
@Profile("local-mock")
@ConditionalOnProperty(prefix = "gamebridge.local-trace", name = ["enabled"], havingValue = "true")
@Order(-109)
class LocalMockTraceFilter : OncePerRequestFilter() {
    private val logger = LoggerFactory.getLogger(LocalMockTraceFilter::class.java)
    private val operations = mapOf(
        "/v1/dev/auth" to "mock-auth",
        "/v1/catalog" to "catalog",
        "/v1/entitlements" to "entitlements",
        "/v1/purchases/verify" to "verify",
        "/v1/auth/logout" to "logout"
    )
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        try { chain.doFilter(request, response) }
        finally {
            val operation = operations[request.requestURI]
            val requestId = request.getAttribute("requestId")?.toString()
            val method = request.method
            if (operation != null && method in setOf("GET", "POST") && requestId != null &&
                runCatching { java.util.UUID.fromString(requestId) }.isSuccess) {
                logger.info("LOCAL_MOCK_TRACE operation={} method={} requestId={} status={}", operation, method, requestId, response.status)
            }
        }
    }
}
