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

internal data class ApplePurchaseInput(@field:NotBlank val storeProductId: String,
                                       @field:NotBlank @field:Size(max = 262144) val signedTransaction: String) {
    override fun toString() = "ApplePurchaseInput([redacted])"
}
@RestController
@Profile("sandbox", "production")
internal class ApplePurchaseController(private val pipeline: ApplePurchasePipeline, private val environment: Environment) {
    @PostMapping("/v1/purchases/apple/verify")
    fun verify(authentication: Authentication, @RequestHeader("Idempotency-Key") key: String,
               @Valid @RequestBody input: ApplePurchaseInput): AppleGrantResult {
        val attempt = try { UUID.fromString(key).also { require(it.toString() == key) } }
                      catch (_: Exception) { throw ResponseStatusException(HttpStatus.BAD_REQUEST) }
        val principal = authentication.principal as SessionPrincipal
        val storeEnvironment = if (environment.activeProfiles.contains("sandbox")) StoreEnvironment.SANDBOX else StoreEnvironment.PRODUCTION
        return try { pipeline.verifyAndGrant(principal, storeEnvironment, input.storeProductId, input.signedTransaction, attempt) }
        catch (_: AppleProofRejected) { throw PurchaseConflict("VERIFICATION_FAILED") }
    }
}
