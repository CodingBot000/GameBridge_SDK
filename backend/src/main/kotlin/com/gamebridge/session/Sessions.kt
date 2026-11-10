package com.gamebridge.session

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.boot.web.servlet.FilterRegistrationBean
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter
import org.springframework.stereotype.Component
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.*
import org.springframework.web.filter.OncePerRequestFilter
import org.springframework.web.server.ResponseStatusException
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.Base64
import java.util.UUID

private fun hash(value: String): ByteArray = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
private fun token(): String = ByteArray(32).also { SecureRandom().nextBytes(it) }.let { Base64.getUrlEncoder().withoutPadding().encodeToString(it) }
private fun unauthorized(): Nothing = throw ResponseStatusException(HttpStatus.UNAUTHORIZED, "Session expired")
data class SessionTokens(val accessToken: String, val refreshToken: String, val expiresAt: String, val userId: String)
data class SessionPrincipal(val sessionId: UUID, val userId: UUID)
private data class SessionRow(val id: UUID, val userId: UUID, val familyId: UUID, val refreshExpires: Instant, val revoked: Boolean)

@Service
class SessionService(private val db: JdbcTemplate, private val tx: TransactionTemplate) {
    fun createMock(subject: String): SessionTokens = tx.execute {
        val user = UUID.nameUUIDFromBytes("gamebridge-local-mock:$subject".toByteArray(Charsets.UTF_8))
        db.update("INSERT INTO users (id, display_name) VALUES (?, ?) ON CONFLICT (id) DO NOTHING", user, subject)
        db.update("INSERT INTO auth_identities (user_id,provider,issuer,subject,app_scope) VALUES (?, 'MOCK', 'local-mock', ?, 'gamebridge-sample') ON CONFLICT DO NOTHING", user, subject)
        val access = token(); val refresh = token(); val now = Instant.now(); val expires = now.plus(15, ChronoUnit.MINUTES)
        db.update("INSERT INTO sessions (id,user_id,access_hash,refresh_hash,expires_at,refresh_expires_at,family_id) VALUES (?,?,?,?,?,?,?)",
            UUID.randomUUID(), user, hash(access), hash(refresh), java.sql.Timestamp.from(expires), java.sql.Timestamp.from(now.plus(7, ChronoUnit.DAYS)), UUID.randomUUID())
        SessionTokens(access, refresh, expires.toString(), user.toString())
    }!!
    fun authenticate(access: String, allowRevokedForLogout: Boolean = false): SessionPrincipal? {
        if (access.length !in 20..256) return null
        return db.query("SELECT id,user_id FROM sessions WHERE access_hash=? AND (revoked_at IS NULL OR ?) AND expires_at > now()", { rs, _ -> SessionPrincipal(rs.getObject("id", UUID::class.java), rs.getObject("user_id", UUID::class.java)) }, hash(access), allowRevokedForLogout).firstOrNull()
    }
    fun refresh(refresh: String): SessionTokens {
        if (refresh.length !in 20..256) unauthorized()
        val digest = hash(refresh)
        val result = tx.execute {
            val rows = db.query("SELECT id,user_id,family_id,refresh_expires_at,revoked_at FROM sessions WHERE refresh_hash=? FOR UPDATE", { rs, _ ->
                SessionRow(rs.getObject("id", UUID::class.java), rs.getObject("user_id", UUID::class.java), rs.getObject("family_id", UUID::class.java), rs.getTimestamp("refresh_expires_at").toInstant(), rs.getTimestamp("revoked_at") != null)
            }, digest)
            val row = rows.firstOrNull()
            if (row == null) {
                val families = db.query("SELECT family_id FROM session_refresh_history WHERE consumed_refresh_hash=?", { rs, _ -> rs.getObject(1, UUID::class.java) }, digest)
                families.firstOrNull()?.let { db.update("UPDATE sessions SET revoked_at=COALESCE(revoked_at,now()) WHERE family_id=?", it) }
                null
            } else if (row.revoked || !row.refreshExpires.isAfter(Instant.now())) null
            else {
                val access = token(); val next = token(); val expires = Instant.now().plus(15, ChronoUnit.MINUTES)
                db.update("INSERT INTO session_refresh_history (consumed_refresh_hash,family_id,consumed_at) VALUES (?,?,now())", digest, row.familyId)
                db.update("UPDATE sessions SET access_hash=?,refresh_hash=?,expires_at=? WHERE id=?", hash(access), hash(next), java.sql.Timestamp.from(expires), row.id)
                SessionTokens(access, next, expires.toString(), row.userId.toString())
            }
        }
        return result ?: unauthorized()
    }
    fun logout(principal: SessionPrincipal) { db.update("UPDATE sessions SET revoked_at=COALESCE(revoked_at,now()) WHERE id=?", principal.sessionId) }
}

@Component
class SessionFilter(private val sessions: SessionService) : OncePerRequestFilter() {
    override fun doFilterInternal(request: HttpServletRequest, response: HttpServletResponse, chain: FilterChain) {
        val header = request.getHeader("Authorization")
        if (header != null && header.startsWith("Bearer ")) {
            sessions.authenticate(header.substring(7), request.method == "POST" && request.requestURI == "/v1/auth/logout")?.let {
                SecurityContextHolder.getContext().authentication = UsernamePasswordAuthenticationToken(it, null, emptyList())
            }
        }
        chain.doFilter(request, response)
    }
}
@Configuration
class SecurityConfiguration {
    @Bean fun disableServletRegistration(filter: SessionFilter) = FilterRegistrationBean(filter).apply { isEnabled = false }
    @Bean fun security(http: HttpSecurity, sessionFilter: SessionFilter): SecurityFilterChain = http
        .csrf { it.disable() }.sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }
        .authorizeHttpRequests { it.requestMatchers("/health", "/v1/config", "/v1/dev/auth", "/v1/auth/refresh").permitAll().anyRequest().authenticated() }
        .exceptionHandling { it.authenticationEntryPoint { request, response, _ ->
            response.status = 401; response.contentType = "application/json"
            val requestId = request.getAttribute("requestId")?.toString() ?: "unknown"
            response.writer.write("{\"code\":\"SESSION_EXPIRED\",\"message\":\"Authentication required\",\"requestId\":\"$requestId\",\"retryable\":false}")
        } }
        .addFilterBefore(sessionFilter, UsernamePasswordAuthenticationFilter::class.java).build()
}

data class RefreshInput(@field:NotBlank val refreshToken: String)
data class MockInput(@field:NotBlank val subject: String)
@RestController
class SessionsController(private val sessions: SessionService) {
    @PostMapping("/v1/auth/refresh") fun refresh(@Valid @RequestBody input: RefreshInput) = sessions.refresh(input.refreshToken)
    @GetMapping("/v1/me") fun me(auth: org.springframework.security.core.Authentication): Map<String, String> = mapOf("userId" to (auth.principal as SessionPrincipal).userId.toString())
    @PostMapping("/v1/auth/logout") fun logout(auth: org.springframework.security.core.Authentication): Map<String, Boolean> {
        sessions.logout(auth.principal as SessionPrincipal); return mapOf("signedOut" to true)
    }
}
@RestController
@Profile("local-mock")
class MockAuthController(private val sessions: SessionService, @Value("\${GAMEBRIDGE_DEV_AUTH_KEY:}") private val key: String) {
    @PostMapping("/v1/dev/auth") fun signIn(@RequestHeader("X-Development-Key", required = false) supplied: String?, @Valid @RequestBody input: MockInput): SessionTokens {
        if (key.length < 32 || supplied == null || !MessageDigest.isEqual(key.toByteArray(), supplied.toByteArray())) throw ResponseStatusException(HttpStatus.FORBIDDEN, "Forbidden")
        if (input.subject !in setOf("A", "B")) throw ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid subject")
        return sessions.createMock(input.subject)
    }
}
