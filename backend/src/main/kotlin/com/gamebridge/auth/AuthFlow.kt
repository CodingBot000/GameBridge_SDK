package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import com.gamebridge.session.SessionService
import com.gamebridge.session.SessionTokens
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.Base64
import java.util.UUID

class AuthFlowException(val code: String) : IllegalArgumentException(code)
class AudiencePolicy private constructor(private val values: Map<Pair<String, IdentityProvider>, Set<String>>) {
    fun allowed(appId: String, provider: IdentityProvider): Set<String> = values[appId to provider]?.takeIf { it.isNotEmpty() }
        ?: throw AuthFlowException("CONFIG_REQUIRED")
    companion object {
        fun parse(raw: String?, mapper: ObjectMapper): AudiencePolicy {
            if (raw.isNullOrBlank()) return AudiencePolicy(emptyMap())
            try {
                val root = mapper.readTree(raw); require(root.isObject)
                val result = mutableMapOf<Pair<String, IdentityProvider>, Set<String>>()
                root.fields().forEachRemaining { app ->
                    require(app.key.isNotBlank() && app.value.isObject)
                    app.value.fields().forEachRemaining { provider ->
                        val type = IdentityProvider.valueOf(provider.key); require(provider.value.isArray)
                        val values = provider.value.map { require(it.isTextual && it.asText().isNotBlank()); it.asText() }.toSet()
                        require(values.isNotEmpty()); result[app.key to type] = values
                    }
                }
                return AudiencePolicy(result)
            } catch (_: Exception) { throw IllegalArgumentException("CONFIG_REQUIRED: GAMEBRIDGE_AUTH_AUDIENCES_JSON") }
        }
    }
}
@Configuration
@Profile("sandbox", "production")
class AudienceConfiguration {
    @Bean fun audiencePolicy(environment: Environment, mapper: ObjectMapper): AudiencePolicy =
        AudiencePolicy.parse(environment.getProperty("GAMEBRIDGE_AUTH_AUDIENCES_JSON"), mapper)
}

data class ChallengeOutput(val challengeId: String, val nonce: String, val expiresAt: String) {
    override fun toString() = "ChallengeOutput([redacted])"
}
private data class ChallengeRow(val provider: String, val appId: String, val nonceHash: ByteArray, val active: Boolean, val used: Boolean)
@Service
@Profile("sandbox", "production")
class AuthFlow(private val db: JdbcTemplate, private val tx: TransactionTemplate, private val audiencePolicy: AudiencePolicy,
               private val verifier: IdentityVerifier, private val sessions: SessionService) {
    fun challenge(appId: String, provider: IdentityProvider): ChallengeOutput {
        audiencePolicy.allowed(appId, provider)
        val id = UUID.randomUUID(); val nonce = Base64.getUrlEncoder().withoutPadding().encodeToString(ByteArray(32).also { SecureRandom().nextBytes(it) })
        val hash = MessageDigest.getInstance("SHA-256").digest(nonce.toByteArray(Charsets.UTF_8))
        val expiry = Instant.now().plus(5, ChronoUnit.MINUTES)
        db.update("INSERT INTO auth_challenges(id,provider,nonce_hash,app_id,expires_at) VALUES (?,?,?,?,?)", id, provider.name, hash, appId, java.sql.Timestamp.from(expiry))
        return ChallengeOutput(id.toString(), nonce, expiry.toString())
    }
    fun exchange(challengeId: UUID, provider: IdentityProvider, token: String, displayName: String?): SessionTokens {
        val row = db.query("SELECT provider,app_id,nonce_hash,expires_at > now() AS active,used_at IS NOT NULL AS used FROM auth_challenges WHERE id=?", { rs, _ ->
            ChallengeRow(rs.getString("provider"), rs.getString("app_id"), rs.getBytes("nonce_hash"), rs.getBoolean("active"), rs.getBoolean("used"))
        }, challengeId).firstOrNull() ?: throw AuthFlowException("AUTH_FAILED")
        if (row.used) throw AuthFlowException("AUTH_REPLAY_DETECTED")
        if (!row.active || row.provider != provider.name) throw AuthFlowException("AUTH_FAILED")
        val verified = try { verifier.verify(provider, token, audiencePolicy.allowed(row.appId, provider), row.nonceHash) }
            catch (error: IdentityVerificationException) { throw AuthFlowException(error.code) }
        return tx.execute {
            val consumed = db.update("UPDATE auth_challenges SET used_at=now() WHERE id=? AND used_at IS NULL AND expires_at>now()", challengeId)
            if (consumed != 1) {
                val used = db.query("SELECT used_at IS NOT NULL FROM auth_challenges WHERE id=?", { rs, _ -> rs.getBoolean(1) }, challengeId).firstOrNull() == true
                throw AuthFlowException(if (used) "AUTH_REPLAY_DETECTED" else "AUTH_FAILED")
            }
            sessions.createVerified(verified, row.appId, displayName)
        }!!
    }
}

data class ChallengeInput(@field:NotBlank val appId: String, val provider: IdentityProvider)
data class ExchangeInput(val challengeId: UUID, val provider: IdentityProvider, @field:NotBlank val idToken: String, val displayName: String? = null) {
    override fun toString() = "ExchangeInput([redacted])"
}
@RestController
@Profile("sandbox", "production")
class AuthFlowController(private val flow: AuthFlow) {
    @PostMapping("/v1/auth/challenges") fun challenge(@Valid @RequestBody input: ChallengeInput) = flow.challenge(input.appId, input.provider)
    @PostMapping("/v1/auth/exchange") fun exchange(@Valid @RequestBody input: ExchangeInput) = flow.exchange(input.challengeId, input.provider, input.idToken, input.displayName)
}
