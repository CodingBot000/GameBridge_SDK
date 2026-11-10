package com.gamebridge.purchase

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpMethod
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import java.util.UUID
import kotlin.test.*

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("local-mock")
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class MockXcodeHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    companion object {
        private const val key = "synthetic-only-development-key-0123456789"
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
            registry.add("GAMEBRIDGE_DEV_AUTH_KEY") { key }
        }
    }
    @Test fun `xcode fake grant is isolated idempotent and session owned`() {
        fun login(subject: String): String {
            val headers = HttpHeaders().apply { set("X-Development-Key", key) }
            return rest.exchange("/v1/dev/auth", HttpMethod.POST, HttpEntity(mapOf("subject" to subject), headers), Map::class.java).body!!["accessToken"] as String
        }
        val a = login("A"); val b = login("B")
        fun call(path: String, token: String, body: Any = emptyMap<String,String>(), secret: String? = key) =
            rest.exchange(path, HttpMethod.POST, HttpEntity(body, HttpHeaders().apply { setBearerAuth(token); if (secret != null) set("X-Development-Key", secret) }), Map::class.java)
        val accountPath = "/v1/dev/xcode-storekit/account"; val grantPath = "/v1/dev/xcode-storekit/grant"; val walletPath = "/v1/dev/xcode-storekit/wallet"
        assertEquals(403, call(accountPath, a, secret = null).statusCode.value())
        val aAccount = call(accountPath, a).body!!; val bAccount = call(accountPath, b).body!!
        val aId = aAccount["userId"] as String; val bId = bAccount["userId"] as String
        assertNotEquals(aId, bId); assertEquals(aId, aAccount["bindingId"])
        val input = mapOf("productId" to "coins_100", "transactionId" to "123", "bindingId" to aId)
        val first = call(grantPath, a, input); assertEquals(200, first.statusCode.value()); assertEquals("GRANTED", first.body!!["fulfillmentStatus"])
        val duplicate = call(grantPath, a, input); assertEquals("ALREADY_GRANTED", duplicate.body!!["fulfillmentStatus"]); assertEquals(first.body!!["serverPurchaseId"], duplicate.body!!["serverPurchaseId"])
        assertEquals(409, call(grantPath, b, input + ("bindingId" to bId)).statusCode.value())
        assertEquals(400, call(grantPath, a, input + ("transactionId" to "0")).statusCode.value())
        assertEquals("100", call(walletPath, a).body!!["coinBalance"]); assertEquals("0", call(walletPath, b).body!!["coinBalance"])
        val concurrent = (1..8).map { java.util.concurrent.CompletableFuture.supplyAsync { call(grantPath, a, input + ("transactionId" to "124")) } }
            .map { it.get(10, java.util.concurrent.TimeUnit.SECONDS) }
        assertTrue(concurrent.all { it.statusCode.value() == 200 })
        assertEquals(1, concurrent.count { it.body!!["fulfillmentStatus"] == "GRANTED" })
        assertEquals("200", call(walletPath, a).body!!["coinBalance"])
        val digest = "a".repeat(64); val hashInput = input + ("transactionId" to digest)
        assertEquals("GRANTED", call(grantPath, a, hashInput).body!!["fulfillmentStatus"])
        assertEquals("ALREADY_GRANTED", call(grantPath, a, hashInput).body!!["fulfillmentStatus"])
        assertEquals(400, call(grantPath, a, hashInput + ("transactionId" to "G".repeat(64))).statusCode.value())
        assertEquals("300", call(walletPath, a).body!!["coinBalance"])
        val normal = rest.exchange("/v1/entitlements", HttpMethod.GET, HttpEntity<Any>(HttpHeaders().apply { setBearerAuth(a) }), Map::class.java)
        assertEquals("0", normal.body!!["coinBalance"])
    }
}
