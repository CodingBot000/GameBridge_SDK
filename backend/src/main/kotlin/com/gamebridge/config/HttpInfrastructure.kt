package com.gamebridge.config

import com.gamebridge.purchase.PurchaseConflict
import com.gamebridge.auth.AuthFlowException
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.http.MediaType
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.http.converter.HttpMessageNotReadableException
import org.springframework.web.bind.MissingServletRequestParameterException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.filter.OncePerRequestFilter
import org.springframework.stereotype.Component
import org.springframework.core.annotation.Order
import org.springframework.web.server.ResponseStatusException
import org.springframework.web.servlet.resource.NoResourceFoundException
import java.util.UUID

@Component
@Order(-110)
class RequestIdFilter : OncePerRequestFilter() {
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val requestId = UUID.randomUUID().toString()
        request.setAttribute("requestId", requestId)
        response.setHeader("X-Request-Id", requestId)
        chain.doFilter(request, response)
    }
}
@RestController
class HealthController {
    @GetMapping("/health") fun health(): Map<String, String> = mapOf("status" to "UP")
}
@RestControllerAdvice
class ApiErrors {
    @ExceptionHandler(AuthFlowException::class)
    fun authFailure(ex: AuthFlowException, request: HttpServletRequest): ResponseEntity<Map<String, Any>> {
        val status = when (ex.code) { "AUTH_REPLAY_DETECTED" -> HttpStatus.CONFLICT; "CONFIG_REQUIRED", "NETWORK_UNAVAILABLE" -> HttpStatus.SERVICE_UNAVAILABLE; else -> HttpStatus.UNAUTHORIZED }
        val code = if (ex.code in setOf("AUTH_REPLAY_DETECTED", "CONFIG_REQUIRED", "NETWORK_UNAVAILABLE")) ex.code else "AUTH_FAILED"
        return ResponseEntity.status(status).contentType(MediaType.APPLICATION_JSON).body(mapOf("code" to code, "message" to "Authentication failed", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to (code == "NETWORK_UNAVAILABLE")))
    }
    @ExceptionHandler(PurchaseConflict::class)
    fun purchaseConflict(ex: PurchaseConflict, request: HttpServletRequest): ResponseEntity<Map<String, Any>> = ResponseEntity.status(HttpStatus.CONFLICT).contentType(MediaType.APPLICATION_JSON)
        .body(mapOf("code" to ex.errorCode, "message" to "Purchase conflict", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))
    @ExceptionHandler(ResponseStatusException::class)
    fun status(ex: ResponseStatusException, request: HttpServletRequest): ResponseEntity<Map<String, Any>> {
        val code = when (ex.statusCode.value()) { 400 -> "INVALID_ARGUMENT"; 401 -> "SESSION_EXPIRED"; 403 -> "PERMISSION_DENIED"; 503 -> "CONFIG_REQUIRED"; else -> "INTERNAL_ERROR" }
        return ResponseEntity.status(ex.statusCode).contentType(MediaType.APPLICATION_JSON).body(mapOf("code" to code, "message" to "Request rejected", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))
    }
    @ExceptionHandler(NoResourceFoundException::class)
    fun notFound(request: HttpServletRequest): ResponseEntity<Map<String, Any>> = ResponseEntity.status(HttpStatus.NOT_FOUND).contentType(MediaType.APPLICATION_JSON)
        .body(mapOf("code" to "UNSUPPORTED_OPERATION", "message" to "Not found", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))
    @ExceptionHandler(MethodArgumentNotValidException::class, HttpMessageNotReadableException::class, MissingServletRequestParameterException::class)
    fun invalid(request: HttpServletRequest): ResponseEntity<Map<String, Any>> = ResponseEntity.status(HttpStatus.BAD_REQUEST).contentType(MediaType.APPLICATION_JSON)
        .body(mapOf("code" to "INVALID_ARGUMENT", "message" to "Invalid request", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))

    @ExceptionHandler(Exception::class)
    fun internal(request: HttpServletRequest): ResponseEntity<Map<String, Any>> = ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).contentType(MediaType.APPLICATION_JSON)
        .body(mapOf("code" to "INTERNAL_ERROR", "message" to "Request failed", "requestId" to (request.getAttribute("requestId") ?: "unknown"), "retryable" to false))
}
