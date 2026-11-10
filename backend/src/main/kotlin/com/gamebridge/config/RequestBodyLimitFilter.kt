package com.gamebridge.config

import com.fasterxml.jackson.databind.ObjectMapper
import jakarta.servlet.FilterChain
import jakarta.servlet.ReadListener
import jakarta.servlet.ServletInputStream
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletRequestWrapper
import jakarta.servlet.http.HttpServletResponse
import org.springframework.core.annotation.Order
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.io.ByteArrayInputStream
import java.io.BufferedReader
import java.io.InputStreamReader

/** Bounded replayable body for synchronous JSON API requests, including chunked requests. */
@Component
@Order(-105)
class RequestBodyLimitFilter(private val mapper: ObjectMapper) : OncePerRequestFilter() {
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        if (!request.requestURI.startsWith("/v1/") || request.method !in setOf("POST", "PUT", "PATCH", "DELETE")) {
            chain.doFilter(request, response); return
        }
        if (request.contentLengthLong > MAX_BYTES) { reject(request, response); return }
        val bytes = request.inputStream.readNBytes(MAX_BYTES + 1)
        if (bytes.size > MAX_BYTES) { reject(request, response); return }
        chain.doFilter(BufferedBodyRequest(request, bytes), response)
    }
    private fun reject(request: HttpServletRequest, response: HttpServletResponse) {
        response.status = HttpServletResponse.SC_REQUEST_ENTITY_TOO_LARGE
        response.contentType = MediaType.APPLICATION_JSON_VALUE
        mapper.writeValue(response.outputStream, mapOf("code" to "PAYLOAD_TOO_LARGE", "message" to "Request too large",
            "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))
    }
    companion object { const val MAX_BYTES = 256 * 1024 }
}
private class BufferedBodyRequest(request: HttpServletRequest, private val body: ByteArray) : HttpServletRequestWrapper(request) {
    override fun getInputStream(): ServletInputStream {
        val input = ByteArrayInputStream(body)
        return object : ServletInputStream() {
            override fun read(): Int = input.read()
            override fun read(bytes: ByteArray, offset: Int, length: Int): Int = input.read(bytes, offset, length)
            override fun isFinished(): Boolean = input.available() == 0
            override fun isReady(): Boolean = true
            override fun setReadListener(listener: ReadListener?) { throw IllegalStateException("Async request bodies are not supported") }
        }
    }
    override fun getReader(): BufferedReader = BufferedReader(InputStreamReader(inputStream, characterEncoding ?: "UTF-8"))
}
