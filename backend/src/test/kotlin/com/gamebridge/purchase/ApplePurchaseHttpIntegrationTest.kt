package com.gamebridge.purchase

import com.apple.itunes.storekit.model.Environment
import com.apple.itunes.storekit.model.JWSTransactionDecodedPayload
import com.apple.itunes.storekit.model.Type
import com.gamebridge.auth.IdentityProvider
import com.gamebridge.auth.VerifiedIdentity
import com.gamebridge.session.SessionService
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.mockito.Mockito
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import org.springframework.test.context.bean.override.mockito.MockitoBean
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

/** Synthetic decoder and isolated sandbox DB; does not represent real Apple signature validation. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_AUTH_DB_TESTS", matches = "true")
class ApplePurchaseHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    @Autowired lateinit var db: JdbcTemplate
    @Autowired lateinit var sessions: SessionService
    @Autowired lateinit var bindings: PurchaseBindings
    @MockitoBean internal lateinit var registry: AppleVerifierRegistry
    companion object {
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
        }
    }
    @Test fun `verified fixture concurrent HTTP requests produce one ledger entry`() {
        val app = "test-" + UUID.randomUUID()
        val tokens = sessions.createVerified(VerifiedIdentity(IdentityProvider.APPLE, "https://appleid.apple.com", UUID.randomUUID().toString(), "test"), app, null)
        val principal = sessions.authenticate(tokens.accessToken)!!
        val binding = bindings.forUser(principal.userId, app).appleAccountToken
        db.update("INSERT INTO products(app_id,logical_id,platform,store_id,type,grant_amount) VALUES (?, 'coins_100','APPLE','coins.apple','CONSUMABLE',100)", app)
        val payload = JWSTransactionDecodedPayload().bundleId("test.bundle").environment(Environment.SANDBOX)
            .productId("coins.apple").appAccountToken(binding).transactionId("test-" + UUID.randomUUID()).quantity(1).type(Type.CONSUMABLE)
        val verifier = ApplePurchaseVerifier("test.bundle", Environment.SANDBOX, setOf("coins.apple"), AppleSignedTransactionDecoder { payload })
        Mockito.`when`(registry.verifier(app, StoreEnvironment.SANDBOX)).thenReturn(verifier)
        val headers = HttpHeaders().apply { setBearerAuth(tokens.accessToken); set("Idempotency-Key", UUID.randomUUID().toString()) }
        val entity = HttpEntity(mapOf("storeProductId" to "coins.apple", "signedTransaction" to "synthetic-jws"), headers)
        val pool = Executors.newFixedThreadPool(10)
        val responses = try { (1..10).map { pool.submit<org.springframework.http.ResponseEntity<Map<*, *>>> {
            @Suppress("UNCHECKED_CAST")
            rest.exchange("/v1/purchases/apple/verify", HttpMethod.POST, entity, Map::class.java) as org.springframework.http.ResponseEntity<Map<*, *>>
        } }.map { it.get(30, TimeUnit.SECONDS) } } finally { pool.shutdownNow() }
        assertTrue(responses.all { it.statusCode.value() == 200 })
        assertEquals(1, responses.count { it.body!!["fulfillmentStatus"] == "GRANTED" })
        assertEquals(1, responses.map { it.body!!["serverPurchaseId"] }.toSet().size)
        assertEquals(1, db.queryForObject("SELECT COUNT(*) FROM wallet_ledger WHERE user_id=?", Int::class.java, principal.userId))
        assertEquals(100L, db.queryForObject("SELECT SUM(delta) FROM wallet_ledger WHERE user_id=?", Long::class.java, principal.userId))
        val readHeaders = HttpHeaders().apply { setBearerAuth(tokens.accessToken) }
        val wallet = rest.exchange("/v1/entitlements", HttpMethod.GET, HttpEntity<Void>(readHeaders), Map::class.java)
        assertEquals(200, wallet.statusCode.value()); assertEquals("100", wallet.body!!["coinBalance"])
        val catalog = rest.exchange("/v1/catalog", HttpMethod.GET, HttpEntity<Void>(readHeaders), List::class.java)
        assertEquals(200, catalog.statusCode.value()); assertEquals(1, catalog.body!!.size)
        val id = responses.first().body!!["serverPurchaseId"] as String
        val own = rest.exchange("/v1/purchases/$id", HttpMethod.GET, HttpEntity<Void>(readHeaders), Map::class.java)
        assertEquals(200, own.statusCode.value()); assertEquals("PENDING", own.body!!["finalizationStatus"])
        val other = sessions.createVerified(VerifiedIdentity(IdentityProvider.APPLE, "https://appleid.apple.com", UUID.randomUUID().toString(), "test"), app, null)
        val otherHeaders = HttpHeaders().apply { setBearerAuth(other.accessToken) }
        val foreign = rest.exchange("/v1/purchases/$id", HttpMethod.GET, HttpEntity<Void>(otherHeaders), Map::class.java)
        assertEquals(404, foreign.statusCode.value()); assertFalse(foreign.body?.toString().orEmpty().contains(id))
    }
}
