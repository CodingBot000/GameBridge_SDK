package com.gamebridge.auth

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.security.MessageDigest
import java.util.ArrayDeque

/** Per-process rolling-minute limits; keys are hashed, not logged or persisted. */
class AuthRateLimiter(private val challengeLimit: Int, private val exchangeLimit: Int, private val now: () -> Long = System::nanoTime) {
    private val buckets = mutableMapOf<Pair<String, String>, ArrayDeque<Long>>()
    init { require(challengeLimit > 0 && exchangeLimit > 0) { "CONFIG_REQUIRED: auth rate limits" } }
    @Synchronized fun allow(remoteAddress: String, operation: String): Boolean {
        val limit = when (operation) { "challenge" -> challengeLimit; "exchange" -> exchangeLimit; else -> return false }
        val instant = now(); val window = 60_000_000_000L
        val iterator = buckets.entries.iterator()
        while (iterator.hasNext()) {
            val entry = iterator.next()
            while (entry.value.isNotEmpty() && instant - entry.value.first >= window) entry.value.removeFirst()
            if (entry.value.isEmpty()) iterator.remove()
        }
        val digest = MessageDigest.getInstance("SHA-256").digest(remoteAddress.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
        val events = buckets.getOrPut(digest to operation) { ArrayDeque() }
        if (events.size >= limit) return false
        events.addLast(instant)
        return true
    }
}

@Component
@Order(-105)
class AuthRateLimitFilter(
    @Value("\${gamebridge.auth-rate.challenge-per-minute:30}") challengeLimit: Int,
    @Value("\${gamebridge.auth-rate.exchange-per-minute:10}") exchangeLimit: Int,
) : OncePerRequestFilter() {
    private val limiter = AuthRateLimiter(challengeLimit, exchangeLimit)
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val operation = if (request.method == "POST") when (request.requestURI) {
            "/v1/auth/challenges" -> "challenge"
            "/v1/auth/exchange" -> "exchange"
            else -> null
        } else null
        if (operation != null && !limiter.allow(request.remoteAddr ?: "unknown", operation)) {
            response.status = 429; response.contentType = "application/json"
            val id = request.getAttribute("requestId")?.toString() ?: "unknown"
            response.writer.write("{\"code\":\"BUSY\",\"message\":\"Request limit reached\",\"requestId\":\"$id\",\"retryable\":true}")
            return
        }
        chain.doFilter(request, response)
    }
}
