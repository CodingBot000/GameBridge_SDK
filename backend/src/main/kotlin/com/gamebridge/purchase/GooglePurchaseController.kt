package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import org.springframework.http.HttpStatus
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import java.util.UUID

internal data class GoogleReadinessInput(@field:NotBlank val storeProductId: String)
internal data class GooglePurchaseInput(@field:NotBlank val storeProductId: String,
                                        @field:NotBlank @field:Size(max = 262144) val purchaseToken: String) {
    override fun toString() = "GooglePurchaseInput([redacted])"
}
@RestController
@Profile("sandbox", "production")
internal class GooglePurchaseController(private val pipeline: GooglePurchasePipeline, private val environment: Environment) {
    private fun mode() = if (environment.activeProfiles.contains("sandbox")) StoreEnvironment.SANDBOX else StoreEnvironment.PRODUCTION
    @PostMapping("/v1/purchases/google/readiness")
    fun readiness(authentication: Authentication, @Valid @RequestBody input: GoogleReadinessInput): Map<String, Boolean> {
        pipeline.ensureReady(authentication.principal as SessionPrincipal, mode(), input.storeProductId)
        return mapOf("ready" to true)
    }
    @PostMapping("/v1/purchases/google/verify")
    fun verify(authentication: Authentication, @RequestHeader("Idempotency-Key") key: String,
               @Valid @RequestBody input: GooglePurchaseInput): GoogleGrantResult {
        val attempt = try { UUID.fromString(key).also { require(it.toString() == key) } }
                      catch (_: Exception) { throw ResponseStatusException(HttpStatus.BAD_REQUEST) }
        return try { pipeline.verifyAndGrant(authentication.principal as SessionPrincipal, mode(), input.storeProductId, input.purchaseToken, attempt) }
        catch (_: GoogleProofRejected) { throw PurchaseConflict("VERIFICATION_FAILED") }
    }
}
