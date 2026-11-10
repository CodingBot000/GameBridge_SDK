package com.gamebridge.purchase

import com.gamebridge.auth.IdentityProvider
import com.gamebridge.auth.VerifiedIdentity
import com.gamebridge.session.SessionService
import com.google.api.services.androidpublisher.model.ProductLineItem
import com.google.api.services.androidpublisher.model.ProductOfferDetails
import com.google.api.services.androidpublisher.model.ProductPurchaseV2
import com.google.api.services.androidpublisher.model.PurchaseStateContext
import com.google.api.services.androidpublisher.model.TestPurchaseContext
import org.awaitility.Awaitility.await
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.mockito.Mockito
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Import
import org.springframework.context.annotation.Primary
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import org.springframework.test.context.bean.override.mockito.MockitoBean
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

private object FakeGoogleFinalizerProbe { val latches = ConcurrentHashMap<String, CountDownLatch>() }
@TestConfiguration
internal class FakeGoogleFinalizerConfiguration {
    @Bean @Primary fun fakeGoogleFinalizationExecutor(): GoogleFinalizationExecutor = GoogleFinalizationExecutor { claim, token ->
        check(claim.app.startsWith("test-")); check(token == "synthetic-google-proof")
        FakeGoogleFinalizerProbe.latches[claim.app]?.countDown()
    }
}
/** Synthetic store verifier/finalizer with real HTTP/auth and dedicated sandbox DB. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@Import(FakeGoogleFinalizerConfiguration::class)
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_AUTH_DB_TESTS", matches = "true")
class GooglePurchaseHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    @Autowired lateinit var db: JdbcTemplate
    @Autowired lateinit var sessions: SessionService
    @Autowired lateinit var bindings: PurchaseBindings
    @MockitoBean internal lateinit var registry: GoogleVerifierRegistry
    companion object {
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
            registry.add("SERVER_PURCHASE_ENCRYPTION_KEY") { java.util.Base64.getEncoder().encodeToString(ByteArray(32) { it.toByte() }) }
            registry.add("gamebridge.finalization.poll-interval-ms") { 100L } // Test-only polling.
        }
    }
    @Test fun `google verified fixture grants once and deletes proof after fake completion`() {
        val app = "test-" + UUID.randomUUID(); val finished = CountDownLatch(1); FakeGoogleFinalizerProbe.latches[app] = finished
        val tokens = sessions.createVerified(VerifiedIdentity(IdentityProvider.GOOGLE, "https://accounts.google.com", UUID.randomUUID().toString(), "test"), app, null)
        val principal = sessions.authenticate(tokens.accessToken)!!
        val binding = bindings.forUser(principal.userId, app).googleObfuscatedAccountId.toString()
        db.update("INSERT INTO products(app_id,logical_id,platform,store_id,type,grant_amount) VALUES (?, 'coins_100','GOOGLE','coins.play','CONSUMABLE',100)", app)
        val response = ProductPurchaseV2().setPurchaseStateContext(PurchaseStateContext().setPurchaseState("PURCHASED"))
            .setObfuscatedExternalAccountId(binding).setTestPurchaseContext(TestPurchaseContext())
            .setProductLineItem(listOf(ProductLineItem().setProductId("coins.play").setProductOfferDetails(ProductOfferDetails().setQuantity(1))))
        val verifier = GooglePurchaseVerifier("test.package", setOf("coins.play"), true, GooglePurchaseLookup { _, token -> if (token == "synthetic-google-proof") response else ProductPurchaseV2().setPurchaseStateContext(PurchaseStateContext().setPurchaseState("PENDING")) })
        Mockito.`when`(registry.verifier(app, StoreEnvironment.SANDBOX)).thenReturn(verifier)
        val headers = HttpHeaders().apply { setBearerAuth(tokens.accessToken); set("Idempotency-Key", UUID.randomUUID().toString()) }
        val ready = rest.exchange("/v1/purchases/google/readiness", HttpMethod.POST, HttpEntity(mapOf("storeProductId" to "coins.play"), headers), Map::class.java)
        assertEquals(200, ready.statusCode.value()); assertEquals(true, ready.body!!["ready"])
        val rejected = rest.exchange("/v1/purchases/google/verify", HttpMethod.POST,
            HttpEntity(mapOf("storeProductId" to "coins.play", "purchaseToken" to "synthetic-pending"), headers), Map::class.java)
        assertEquals(400, rejected.statusCode.value()); assertEquals("VERIFICATION_FAILED", rejected.body!!["code"])
        assertEquals(0, db.queryForObject("SELECT COUNT(*) FROM wallet_ledger WHERE user_id=?", Int::class.java, principal.userId))
        val entity = HttpEntity(mapOf("storeProductId" to "coins.play", "purchaseToken" to "synthetic-google-proof"), headers)
        val pool = Executors.newFixedThreadPool(10)
        val responses = try { (1..10).map { pool.submit<org.springframework.http.ResponseEntity<Map<*, *>>> {
            @Suppress("UNCHECKED_CAST")
            rest.exchange("/v1/purchases/google/verify", HttpMethod.POST, entity, Map::class.java) as org.springframework.http.ResponseEntity<Map<*, *>>
        } }.map { it.get(30, TimeUnit.SECONDS) } } finally { pool.shutdownNow() }
        assertTrue(responses.all { it.statusCode.value() == 200 }); assertEquals(1, responses.count { it.body!!["fulfillmentStatus"] == "GRANTED" })
        assertEquals(1, responses.map { it.body!!["serverPurchaseId"] }.toSet().size)
        assertFalse(responses.first().body?.toString().orEmpty().contains("synthetic-google-proof"))
        val id = UUID.fromString(responses.first().body!!["serverPurchaseId"] as String)
        assertTrue(finished.await(8, TimeUnit.SECONDS))
        await().atMost(5, TimeUnit.SECONDS).untilAsserted {
            assertEquals("FINALIZED", db.queryForObject("SELECT finalization_state FROM purchases WHERE id=?", String::class.java, id))
            assertNull(db.queryForObject("SELECT evidence_encrypted FROM purchases WHERE id=?", ByteArray::class.java, id))
        }
        assertEquals(100L, db.queryForObject("SELECT SUM(delta) FROM wallet_ledger WHERE user_id=?", Long::class.java, principal.userId))
    }
}
