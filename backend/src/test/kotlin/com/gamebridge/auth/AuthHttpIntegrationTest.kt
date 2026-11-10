package com.gamebridge.auth

import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
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
import java.security.MessageDigest
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm
import org.springframework.security.oauth2.jwt.JwtTimestampValidator
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import java.time.Duration
import java.time.Instant
import java.util.Date
import java.util.UUID
import kotlin.test.*

private object FixtureKey { val key = RSAKeyGenerator(2048).keyID("test-only").generate() }
@TestConfiguration
class TestIdentityConfiguration {
    @Bean @Primary fun testIdentityVerifier(): IdentityVerifier {
        fun decoder() = NimbusJwtDecoder.withPublicKey(FixtureKey.key.toRSAPublicKey()).signatureAlgorithm(SignatureAlgorithm.RS256).build()
            .apply { setJwtValidator(JwtTimestampValidator(Duration.ZERO)) }
        return IdentityVerifier(mapOf(IdentityProvider.GOOGLE to decoder(), IdentityProvider.APPLE to decoder()))
    }
}

/** Test-only signing key and decoder; production uses the official remote JWKS configuration. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@Import(TestIdentityConfiguration::class)
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_AUTH_DB_TESTS", matches = "true")
class AuthHttpIntegrationTest {
    @Autowired lateinit var rest: TestRestTemplate
    @Autowired lateinit var db: JdbcTemplate
    companion object {
        @JvmStatic @DynamicPropertySource fun properties(registry: DynamicPropertyRegistry) {
            registry.add("DATABASE_URL") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")) }
            registry.add("DATABASE_USERNAME") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")) }
            registry.add("DATABASE_PASSWORD") { requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")) }
            registry.add("gamebridge.session.access-ttl-seconds") { 120L }
            registry.add("gamebridge.session.refresh-ttl-seconds") { 600L }
            registry.add("GAMEBRIDGE_AUTH_AUDIENCES_JSON") { """{"test-app":{"GOOGLE":["test-google"],"APPLE":["test.apple.bundle"]}}""" }
        }
    }
    private fun signed(issuer: String, audience: String, nonce: String, subject: String): String {
        val claims = JWTClaimsSet.Builder().issuer(issuer).subject(subject).audience(audience)
            .expirationTime(Date.from(Instant.now().plusSeconds(600))).claim("nonce", nonce).build()
        return SignedJWT(JWSHeader.Builder(JWSAlgorithm.RS256).keyID("test-only").build(), claims)
            .apply { sign(RSASSASigner(FixtureKey.key.toPrivateKey())) }.serialize()
    }
    @Test fun `http exchange verifies tokens and challenge replay while retaining first display name`() {
        val dev = rest.postForEntity("/v1/dev/auth", mapOf("subject" to "A"), Map::class.java)
        assertEquals(404, dev.statusCode.value())
        val subject = "subject-" + UUID.randomUUID()
        fun challenge(provider: String): Map<*, *> {
            val response = rest.postForEntity("/v1/auth/challenges", mapOf("appId" to "test-app", "provider" to provider), Map::class.java)
            assertEquals(200, response.statusCode.value()); return response.body!!
        }
        fun exchange(challenge: Map<*, *>, provider: String, token: String, displayName: String? = null) = rest.postForEntity(
            "/v1/auth/exchange", mapOf("challengeId" to challenge["challengeId"], "provider" to provider, "idToken" to token, "displayName" to displayName), Map::class.java)
        val googleChallenge = challenge("GOOGLE")
        val googleToken = signed("https://accounts.google.com", "test-google", googleChallenge["nonce"] as String, subject)
        val google = exchange(googleChallenge, "GOOGLE", googleToken, "테스트 이름")
        assertEquals(200, google.statusCode.value())
        val session = google.body!!; assertFalse(session.toString().contains(googleToken))
        val remaining = Duration.between(Instant.now(), Instant.parse(session["expiresAt"] as String)).seconds
        assertTrue(remaining in 100..120)
        val headers = HttpHeaders().apply { setBearerAuth(session["accessToken"] as String) }
        val me = rest.exchange("/v1/me", HttpMethod.GET, HttpEntity<Void>(headers), Map::class.java)
        assertEquals(200, me.statusCode.value()); assertEquals("테스트 이름", me.body!!["displayName"])
        val refresh = session["refreshToken"] as String
        val digest = MessageDigest.getInstance("SHA-256").digest(refresh.toByteArray())
        assertEquals(1, db.update("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=?", digest))
        val logout = rest.postForEntity("/v1/auth/logout", mapOf("refreshToken" to refresh), Map::class.java)
        assertEquals(200, logout.statusCode.value())
        assertEquals(200, rest.postForEntity("/v1/auth/logout", mapOf("refreshToken" to refresh), Map::class.java).statusCode.value())
        assertEquals(401, rest.postForEntity("/v1/auth/refresh", mapOf("refreshToken" to refresh), Map::class.java).statusCode.value())
        val replay = exchange(googleChallenge, "GOOGLE", googleToken)
        assertEquals(409, replay.statusCode.value()); assertEquals("AUTH_REPLAY_DETECTED", replay.body!!["code"])
        val appleChallenge = challenge("APPLE")
        val appleToken = signed("https://appleid.apple.com", "test.apple.bundle", appleChallenge["nonce"] as String, "apple-" + subject)
        val apple = exchange(appleChallenge, "APPLE", appleToken)
        assertEquals(200, apple.statusCode.value()); assertNotEquals(session["userId"], apple.body!!["userId"])
        val retryChallenge = challenge("GOOGLE")
        val bad = signed("https://accounts.google.com", "wrong", retryChallenge["nonce"] as String, subject)
        assertEquals(401, exchange(retryChallenge, "GOOGLE", bad).statusCode.value())
        val correct = signed("https://accounts.google.com", "test-google", retryChallenge["nonce"] as String, subject)
        assertEquals(200, exchange(retryChallenge, "GOOGLE", correct).statusCode.value())
    }
}
