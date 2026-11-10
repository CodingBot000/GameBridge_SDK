package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.springframework.context.annotation.Profile
import org.springframework.context.SmartLifecycle
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.Authentication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter
import java.util.UUID
import jakarta.annotation.PreDestroy
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicReference
import java.util.concurrent.atomic.AtomicBoolean

/** Authenticated local development stream; never stores an event for a disconnected listener. */
@RestController
@Profile("local-mock")
internal class MockPushStreamController(private val db: JdbcTemplate, private val broker: MockPushBroker) : SmartLifecycle {
    private val emitters = ConcurrentHashMap.newKeySet<SseEmitter>()
    @Volatile private var running = false
    override fun start() { running = true }
    override fun stop() { closeStreams(); running = false }
    override fun isRunning() = running
    override fun getPhase() = Int.MAX_VALUE
    @PreDestroy fun closeStreams() { emitters.forEach { it.complete() }; emitters.clear() }
    @GetMapping("/v1/dev/push/stream")
    fun stream(authentication: Authentication, @RequestParam installationId: UUID): SseEmitter {
        val principal = authentication.principal as SessionPrincipal
        val app = db.query("SELECT app_scope FROM sessions WHERE id=? AND user_id=? AND revoked_at IS NULL AND expires_at>now()",
            { rs, _ -> rs.getString(1) }, principal.sessionId, principal.userId).firstOrNull()
            ?: throw ResponseStatusException(HttpStatus.UNAUTHORIZED)
        fun stillOwned(): Boolean = db.queryForObject("""SELECT EXISTS(SELECT 1 FROM device_tokens d JOIN sessions s ON s.id=d.session_id
            WHERE d.app_id=? AND d.environment='local-mock' AND d.installation_id=? AND d.user_id=? AND d.session_id=?
              AND s.user_id=? AND s.app_scope=? AND s.revoked_at IS NULL AND s.expires_at>now())""", Boolean::class.java,
            app, installationId, principal.userId, principal.sessionId, principal.userId, app) == true
        if (!stillOwned()) throw ResponseStatusException(HttpStatus.FORBIDDEN)
        val emitter = SseEmitter(0L)
        emitters.add(emitter)
        val id = AtomicReference<UUID>()
        val closed = AtomicBoolean(false)
        fun remove() { closed.set(true); emitters.remove(emitter); id.get()?.let(broker::unsubscribe) }
        emitter.onCompletion(::remove); emitter.onTimeout(::remove); emitter.onError { remove() }
        val subscription = broker.subscribe(MockPushBroker.Target(principal, app, installationId)) { event ->
            try {
                if (!stillOwned()) { emitter.complete(); false }
                else {
                    emitter.send(SseEmitter.event().name("push").data(mapOf("messageId" to event.messageId,
                        "route" to event.route, "campaignId" to event.campaignId)))
                    true
                }
            } catch (_: Exception) { false }
        }
        id.set(subscription)
        if (closed.get()) broker.unsubscribe(subscription)
        try { emitter.send(SseEmitter.event().name("ready").data("connected")) }
        catch (_: Exception) { remove(); emitter.complete() }
        return emitter
    }
}
