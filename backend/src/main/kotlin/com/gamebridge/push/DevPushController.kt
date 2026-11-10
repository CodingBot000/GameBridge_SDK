package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import java.security.MessageDigest
import java.util.UUID

internal data class DevPushInput(val installationId: UUID, @field:NotBlank val messageId: String, val route: String,
                                 val title: String, val body: String, val campaignId: String? = null) {
    override fun toString() = "DevPushInput([redacted])"
}
internal fun interface DevPushSender { fun send(principal: SessionPrincipal, app: String, input: DevPushInput): String }
@Configuration
@Profile("local-mock", "sandbox")
internal class DevPushSenderConfiguration {
    @Bean @Profile("local-mock") fun mockDevPushSender(): DevPushSender = DevPushSender { _, _, _ -> "SIMULATED" }
    @Bean @Profile("sandbox") fun sandboxDevPushSender(runtime: SandboxPushRuntime): DevPushSender = DevPushSender { principal, app, input ->
        val target = PushDispatchTarget(principal, app, "sandbox", input.installationId)
        val content = PushContent(input.messageId, input.route, input.title, input.body, input.campaignId)
        when (runtime.enqueue(target, content)) {
            PushQueueResult.QUEUED -> "QUEUED"
            PushQueueResult.NO_DEVICE -> throw ResponseStatusException(HttpStatus.FORBIDDEN)
            PushQueueResult.BUSY -> throw ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS)
        }
    }
}
@RestController
@Profile("local-mock", "sandbox")
internal class DevPushController(private val db: JdbcTemplate, private val environment: Environment, private val limiter: DevPushRateLimiter,
                                 private val sender: DevPushSender,
                                 @Value("\${GAMEBRIDGE_DEV_PUSH_ADMIN_KEY:}") private val adminKey: String,
                                 @Value("\${GAMEBRIDGE_DEV_AUTH_KEY:}") private val authKey: String,
                                 @Value("\${GAMEBRIDGE_DEV_PUSH_ALLOWLIST:}") private val allowlist: String) {
    @PostMapping("/v1/dev/push/send")
    fun send(authentication: Authentication, @RequestHeader("X-Admin-Key", required = false) supplied: String?,
             @Valid @RequestBody input: DevPushInput): Map<String, Any> {
        if (adminKey.length < 32 || adminKey == authKey || allowlist.isBlank()) throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE)
        if (supplied == null || !MessageDigest.isEqual(adminKey.toByteArray(Charsets.UTF_8), supplied.toByteArray(Charsets.UTF_8))) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        val allowed = try { allowlist.split(',').map { UUID.fromString(it.trim()) }.toSet() } catch (_: Exception) { throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE) }
        if (input.installationId !in allowed) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        if (input.route !in setOf("home", "store")) throw ResponseStatusException(HttpStatus.BAD_REQUEST)
        if (!limiter.allow(supplied)) throw ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS)
        val principal = authentication.principal as SessionPrincipal
        val profile = if (environment.activeProfiles.contains("local-mock")) "local-mock" else "sandbox"
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull() ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
        val owns = db.queryForObject("SELECT EXISTS(SELECT 1 FROM device_tokens WHERE app_id=? AND environment=? AND installation_id=? AND user_id=?)",
            Boolean::class.java, app, profile, input.installationId, principal.userId) == true
        if (!owns) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        return mapOf("accepted" to true, "delivery" to sender.send(principal, app, input))
    }
}
