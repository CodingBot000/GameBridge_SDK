package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.springframework.context.annotation.Profile
import org.springframework.stereotype.Component
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

/** Local-only transient subscribers. No message is stored for absent or disconnected clients. */
@Component
@Profile("local-mock")
internal class MockPushBroker {
    internal data class Target(val principal: SessionPrincipal, val app: String, val installationId: UUID)
    internal data class Event(val messageId: String, val route: String, val campaignId: String?)
    private data class Subscriber(val target: Target, val deliver: (Event) -> Boolean)
    private val subscribers = ConcurrentHashMap<UUID, Subscriber>()

    fun subscribe(target: Target, deliver: (Event) -> Boolean): UUID {
        val id = UUID.randomUUID()
        subscribers[id] = Subscriber(target, deliver)
        return id
    }
    fun unsubscribe(id: UUID) { subscribers.remove(id) }
    internal fun subscriberCount(): Int = subscribers.size
    fun publish(app: String, userId: UUID, installationId: UUID, event: Event): Int {
        var delivered = 0
        subscribers.forEach { (id, subscriber) ->
            val target = subscriber.target
            if (target.app == app && target.principal.userId == userId && target.installationId == installationId) {
                val accepted = try { subscriber.deliver(event) } catch (_: Exception) { false }
                if (accepted) delivered++ else subscribers.remove(id, subscriber)
            }
        }
        return delivered
    }
}
