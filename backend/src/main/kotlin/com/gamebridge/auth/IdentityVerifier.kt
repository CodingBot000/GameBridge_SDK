package com.gamebridge.auth

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.http.client.SimpleClientHttpRequestFactory
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm
import org.springframework.security.oauth2.jwt.JwtDecoder
import org.springframework.security.oauth2.jwt.JwtException
import org.springframework.security.oauth2.jwt.JwtTimestampValidator
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import org.springframework.web.client.RestTemplate
import java.io.IOException
import java.security.MessageDigest
import java.time.Clock
import java.time.Duration

enum class IdentityProvider { GOOGLE, APPLE }
data class VerifiedIdentity(val provider: IdentityProvider, val issuer: String, val subject: String, val audience: String)
class IdentityVerificationException(val code: String) : IllegalArgumentException(code)

/** The nonce input is a SHA-256 hash stored with the single-use server challenge. */
class IdentityVerifier(private val decoders: Map<IdentityProvider, JwtDecoder>, private val clock: Clock = Clock.systemUTC()) {
    fun verify(provider: IdentityProvider, token: String, audience: String, expectedNonceHash: ByteArray): VerifiedIdentity =
        verify(provider, token, setOf(audience), expectedNonceHash)
    fun verify(provider: IdentityProvider, token: String, allowedAudiences: Set<String>, expectedNonceHash: ByteArray): VerifiedIdentity {
        if (token.isBlank() || allowedAudiences.isEmpty() || allowedAudiences.any { it.isBlank() } || expectedNonceHash.size != 32) throw IdentityVerificationException("AUTH_FAILED")
        val decoder = decoders[provider] ?: throw IdentityVerificationException("CONFIG_REQUIRED")
        val jwt = try { decoder.decode(token) } catch (error: JwtException) {
            val network = generateSequence<Throwable>(error) { it.cause }.take(16).any { it is IOException }
            throw IdentityVerificationException(if (network) "NETWORK_UNAVAILABLE" else "AUTH_FAILED")
        }
        val issuer = jwt.claims["iss"] as? String ?: throw IdentityVerificationException("AUTH_FAILED")
        val validIssuers = when (provider) {
            IdentityProvider.GOOGLE -> setOf("https://accounts.google.com", "accounts.google.com")
            IdentityProvider.APPLE -> setOf("https://appleid.apple.com")
        }
        val subject = jwt.subject?.takeIf { it.isNotBlank() } ?: throw IdentityVerificationException("AUTH_FAILED")
        val nonce = jwt.claims["nonce"] as? String ?: throw IdentityVerificationException("AUTH_FAILED")
        val nonceHash = MessageDigest.getInstance("SHA-256").digest(nonce.toByteArray(Charsets.UTF_8))
        val tokenAudiences = jwt.audience ?: emptyList()
        val matching = tokenAudiences.filter { it in allowedAudiences }
        val audience = if (tokenAudiences.size > 1) (jwt.claims["azp"] as? String)?.takeIf { it in matching } else matching.singleOrNull()
        if (jwt.headers["alg"] != "RS256" || issuer !in validIssuers || jwt.expiresAt?.isAfter(clock.instant()) != true ||
            audience == null || !MessageDigest.isEqual(nonceHash, expectedNonceHash)) throw IdentityVerificationException("AUTH_FAILED")
        val canonicalIssuer = if (provider == IdentityProvider.GOOGLE) "https://accounts.google.com" else issuer
        return VerifiedIdentity(provider, canonicalIssuer, subject, audience)
    }
}

@Configuration
@Profile("sandbox", "production")
class IdentityVerifierConfiguration {
    @Bean fun identityVerifier(): IdentityVerifier {
        val transport = SimpleClientHttpRequestFactory().apply {
            setConnectTimeout(Duration.ofSeconds(30)); setReadTimeout(Duration.ofSeconds(30))
        }
        fun decoder(uri: String): JwtDecoder = NimbusJwtDecoder.withJwkSetUri(uri)
            .jwsAlgorithm(SignatureAlgorithm.RS256).restOperations(RestTemplate(transport)).build()
            .apply { setJwtValidator(JwtTimestampValidator(Duration.ZERO)) }
        return IdentityVerifier(mapOf(
            IdentityProvider.GOOGLE to decoder("https://www.googleapis.com/oauth2/v3/certs"),
            IdentityProvider.APPLE to decoder("https://appleid.apple.com/auth/keys"),
        ))
    }
}
