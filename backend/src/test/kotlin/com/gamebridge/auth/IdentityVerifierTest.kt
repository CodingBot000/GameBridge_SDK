package com.gamebridge.auth

import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.RSAKey
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm
import org.springframework.security.oauth2.jwt.JwtException
import org.springframework.security.oauth2.jwt.JwtTimestampValidator
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import java.io.IOException
import java.security.MessageDigest
import java.time.Duration
import java.time.Instant
import java.util.Date
import kotlin.test.*

class IdentityVerifierTest {
    private val key = RSAKeyGenerator(2048).keyID("test-only").generate()
    private val wrongKey = RSAKeyGenerator(2048).keyID("wrong").generate()
    private fun decoder() = NimbusJwtDecoder.withPublicKey(key.toRSAPublicKey()).signatureAlgorithm(SignatureAlgorithm.RS256).build().apply { setJwtValidator(JwtTimestampValidator(Duration.ZERO)) }
    private fun verifier() = IdentityVerifier(mapOf(IdentityProvider.GOOGLE to decoder(), IdentityProvider.APPLE to decoder()))
    private fun digest(value: String) = MessageDigest.getInstance("SHA-256").digest(value.toByteArray())
    private fun token(issuer: String = "https://accounts.google.com", audience: String = "client-a", nonce: String = "server-nonce", exp: Instant = Instant.now().plusSeconds(600), signer: RSAKey = key, alg: JWSAlgorithm = JWSAlgorithm.RS256): String {
        val claims = JWTClaimsSet.Builder().issuer(issuer).subject("subject-123").audience(audience).expirationTime(Date.from(exp)).claim("nonce", nonce).build()
        return SignedJWT(JWSHeader.Builder(alg).keyID("test-only").build(), claims).apply { sign(RSASSASigner(signer.toPrivateKey())) }.serialize()
    }
    @Test fun `signed tokens validate identity without exposing token`() {
        val google = verifier().verify(IdentityProvider.GOOGLE, token(), "client-a", digest("server-nonce"))
        assertEquals("subject-123", google.subject)
        val legacyIssuer = verifier().verify(IdentityProvider.GOOGLE, token(issuer = "accounts.google.com"), "client-a", digest("server-nonce"))
        assertEquals("https://accounts.google.com", legacyIssuer.issuer)
        val apple = verifier().verify(IdentityProvider.APPLE, token(issuer = "https://appleid.apple.com"), "client-a", digest("server-nonce"))
        assertEquals(IdentityProvider.APPLE, apple.provider)
    }
    @Test fun `wrong audience issuer nonce expiry algorithm and signature fail closed`() {
        val tests = listOf(
            token(audience = "other"), token(issuer = "https://evil.example"), token(nonce = "wrong"),
            token(exp = Instant.now().minusSeconds(1)), token(signer = wrongKey), token(alg = JWSAlgorithm.RS512),
        )
        tests.forEach { value ->
            val error = assertFailsWith<IdentityVerificationException> { verifier().verify(IdentityProvider.GOOGLE, value, "client-a", digest("server-nonce")) }
            assertEquals("AUTH_FAILED", error.code); assertFalse(error.toString().contains(value))
        }
    }
    @Test fun `multiple audiences require matching authorized party`() {
        fun make(azp: String?): String {
            val builder = JWTClaimsSet.Builder().issuer("https://accounts.google.com").subject("subject-123")
                .audience(listOf("client-a", "client-b")).expirationTime(Date.from(Instant.now().plusSeconds(600))).claim("nonce", "server-nonce")
            if (azp != null) builder.claim("azp", azp)
            return SignedJWT(JWSHeader.Builder(JWSAlgorithm.RS256).keyID("test-only").build(), builder.build())
                .apply { sign(RSASSASigner(key.toPrivateKey())) }.serialize()
        }
        val verifier = verifier()
        assertEquals("client-b", verifier.verify(IdentityProvider.GOOGLE, make("client-b"), setOf("client-a", "client-b"), digest("server-nonce")).audience)
        assertFailsWith<IdentityVerificationException> { verifier.verify(IdentityProvider.GOOGLE, make(null), setOf("client-a", "client-b"), digest("server-nonce")) }
        assertFailsWith<IdentityVerificationException> { verifier.verify(IdentityProvider.GOOGLE, make("client-a"), setOf("client-b"), digest("server-nonce")) }
    }
    @Test fun `missing audience fails closed`() {
        val claims = JWTClaimsSet.Builder().issuer("https://accounts.google.com").subject("subject-123")
            .expirationTime(Date.from(Instant.now().plusSeconds(600))).claim("nonce", "server-nonce").build()
        val value = SignedJWT(JWSHeader.Builder(JWSAlgorithm.RS256).keyID("test-only").build(), claims)
            .apply { sign(RSASSASigner(key.toPrivateKey())) }.serialize()
        assertEquals("AUTH_FAILED", assertFailsWith<IdentityVerificationException> { verifier().verify(IdentityProvider.GOOGLE, value, "client-a", digest("server-nonce")) }.code)
    }
    @Test fun `missing required identity claims fail closed`() {
        for (missing in listOf("exp", "nonce", "sub")) {
            val claims = JWTClaimsSet.Builder().issuer("https://accounts.google.com").audience("client-a")
            if (missing != "sub") claims.subject("subject-123")
            if (missing != "exp") claims.expirationTime(Date.from(Instant.now().plusSeconds(600)))
            if (missing != "nonce") claims.claim("nonce", "server-nonce")
            val value = SignedJWT(JWSHeader.Builder(JWSAlgorithm.RS256).keyID("test-only").build(), claims.build())
                .apply { sign(RSASSASigner(key.toPrivateKey())) }.serialize()
            assertEquals("AUTH_FAILED", assertFailsWith<IdentityVerificationException> { verifier().verify(IdentityProvider.GOOGLE, value, "client-a", digest("server-nonce")) }.code)
        }
    }
    @Test fun `jwks network failure is not treated as authentication success`() {
        val verifier = IdentityVerifier(mapOf(IdentityProvider.GOOGLE to org.springframework.security.oauth2.jwt.JwtDecoder { throw JwtException("temporary", IOException()) }))
        assertEquals("NETWORK_UNAVAILABLE", assertFailsWith<IdentityVerificationException> { verifier.verify(IdentityProvider.GOOGLE, "a.b.c", "client-a", digest("server-nonce")) }.code)
    }
}
