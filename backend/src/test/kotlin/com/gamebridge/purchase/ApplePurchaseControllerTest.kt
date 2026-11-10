package com.gamebridge.purchase

import com.gamebridge.session.SessionPrincipal
import com.gamebridge.session.SessionService
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest
import org.springframework.http.MediaType
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*
import java.util.UUID

@WebMvcTest(ApplePurchaseController::class)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("sandbox")
class ApplePurchaseControllerTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean internal lateinit var pipeline: ApplePurchasePipeline
    @MockitoBean lateinit var sessions: SessionService
    @Test fun `authenticated apple verify forwards scoped principal and idempotency`() {
        val principal = SessionPrincipal(UUID.randomUUID(), UUID.randomUUID())
        val auth = UsernamePasswordAuthenticationToken(principal, null, emptyList())
        val attempt = UUID.randomUUID(); val binding = UUID.randomUUID(); val purchase = UUID.randomUUID()
        val result = AppleGrantResult(principal.userId, binding, "coins.apple", "123", purchase, "GRANTED")
        Mockito.`when`(pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "coins.apple", "synthetic-jws", attempt)).thenReturn(result)
        mvc.perform(post("/v1/purchases/apple/verify").principal(auth).header("Idempotency-Key", attempt.toString())
            .contentType(MediaType.APPLICATION_JSON).content("""{"storeProductId":"coins.apple","signedTransaction":"synthetic-jws"}"""))
            .andExpect(status().isOk).andExpect(jsonPath("$.serverPurchaseId").value(purchase.toString()))
            .andExpect(jsonPath("$.fulfillmentStatus").value("GRANTED"))
        mvc.perform(post("/v1/purchases/apple/verify").principal(auth).header("Idempotency-Key", "invalid")
            .contentType(MediaType.APPLICATION_JSON).content("""{"storeProductId":"coins.apple","signedTransaction":"synthetic-jws"}"""))
            .andExpect(status().isBadRequest)
        Mockito.reset(pipeline)
        Mockito.`when`(pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "coins.apple", "synthetic-jws", attempt)).thenThrow(AppleProofRejected())
        mvc.perform(post("/v1/purchases/apple/verify").principal(auth).header("Idempotency-Key", attempt.toString())
            .contentType(MediaType.APPLICATION_JSON).content("""{"storeProductId":"coins.apple","signedTransaction":"synthetic-jws"}"""))
            .andExpect(status().isBadRequest).andExpect(jsonPath("$.code").value("VERIFICATION_FAILED"))
        Mockito.reset(pipeline)
        Mockito.`when`(pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "coins.apple", "synthetic-jws", attempt)).thenThrow(AppleVerifierUnavailable())
        mvc.perform(post("/v1/purchases/apple/verify").principal(auth).header("Idempotency-Key", attempt.toString())
            .contentType(MediaType.APPLICATION_JSON).content("""{"storeProductId":"coins.apple","signedTransaction":"synthetic-jws"}"""))
            .andExpect(status().isServiceUnavailable).andExpect(jsonPath("$.code").value("NETWORK_UNAVAILABLE"))
    }
}
