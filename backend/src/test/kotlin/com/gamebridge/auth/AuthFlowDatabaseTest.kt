package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import com.gamebridge.session.SessionService
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.jdbc.datasource.DriverManagerDataSource
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm
import org.springframework.security.oauth2.jwt.JwtTimestampValidator
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import org.springframework.transaction.support.TransactionTemplate
import java.security.MessageDigest
import java.time.Duration
import java.time.Instant
import java.util.Date
import java.util.UUID
import java.util.concurrent.CyclicBarrier
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

/** Explicit opt-in; targets an isolated sandbox-marked DB and leaves its test records intact. */
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_AUTH_DB_TESTS", matches = "true")
class AuthFlowDatabaseTest {
    @Test fun `challenge is single use and verified subject maps consistently`() {
        val source = DriverManagerDataSource(requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")),
            requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")), requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")))
        val db = JdbcTemplate(source)
        require(db.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "sandbox")
        val tx = TransactionTemplate(DataSourceTransactionManager(source))
        val app = "test-" + UUID.randomUUID(); val subject = "subject-" + UUID.randomUUID()
        val policy = AudiencePolicy.parse("""{"$app":{"GOOGLE":["client-a"]}}""", ObjectMapper())
        val key = RSAKeyGenerator(2048).keyID("test-only").generate()
        val decoder = NimbusJwtDecoder.withPublicKey(key.toRSAPublicKey()).signatureAlgorithm(SignatureAlgorithm.RS256).build().apply { setJwtValidator(JwtTimestampValidator(Duration.ZERO)) }
        val flow = AuthFlow(db, tx, policy, IdentityVerifier(mapOf(IdentityProvider.GOOGLE to decoder)), SessionService(db, tx))
        fun signed(nonce: String, audience: String = "client-a", issuer: String = "https://accounts.google.com"): String {
            val claims = JWTClaimsSet.Builder().issuer(issuer).subject(subject).audience(audience)
                .expirationTime(Date.from(Instant.now().plusSeconds(600))).claim("nonce", nonce).build()
            return SignedJWT(JWSHeader.Builder(JWSAlgorithm.RS256).keyID("test-only").build(), claims).apply { sign(RSASSASigner(key.toPrivateKey())) }.serialize()
        }
        val challenge = flow.challenge(app, IdentityProvider.GOOGLE)
        val challengeId = UUID.fromString(challenge.challengeId)
        val savedHash = db.queryForObject("SELECT nonce_hash FROM auth_challenges WHERE id=?", ByteArray::class.java, challengeId)!!
        assertContentEquals(MessageDigest.getInstance("SHA-256").digest(challenge.nonce.toByteArray()), savedHash)
        assertFalse(challenge.toString().contains(challenge.nonce))
        val proof = signed(challenge.nonce); val barrier = CyclicBarrier(2); val pool = Executors.newFixedThreadPool(2)
        val results = try {
            (1..2).map { pool.submit<Result<com.gamebridge.session.SessionTokens>> { barrier.await(); runCatching { flow.exchange(challengeId, IdentityProvider.GOOGLE, proof, null) } } }
                .map { it.get(10, TimeUnit.SECONDS) }
        } finally { pool.shutdownNow() }
        assertEquals(1, results.count { it.isSuccess })
        val failed = results.single { it.isFailure }.exceptionOrNull() as AuthFlowException
        assertEquals("AUTH_REPLAY_DETECTED", failed.code)
        val firstUser = results.single { it.isSuccess }.getOrThrow().userId
        val next = flow.challenge(app, IdentityProvider.GOOGLE)
        val secondUser = flow.exchange(UUID.fromString(next.challengeId), IdentityProvider.GOOGLE, signed(next.nonce, issuer = "accounts.google.com"), "First name").userId
        assertEquals(firstUser, secondUser)
        assertEquals("First name", db.queryForObject("SELECT display_name FROM users WHERE id=?", String::class.java, UUID.fromString(firstUser)))
        val rejected = flow.challenge(app, IdentityProvider.GOOGLE)
        assertEquals("AUTH_FAILED", assertFailsWith<AuthFlowException> { flow.exchange(UUID.fromString(rejected.challengeId), IdentityProvider.GOOGLE, signed(rejected.nonce, "wrong"), null) }.code)
        assertEquals(false, db.queryForObject("SELECT used_at IS NOT NULL FROM auth_challenges WHERE id=?", Boolean::class.java, UUID.fromString(rejected.challengeId)))
    }
}
