package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.assertEquals

class MockPushBrokerTest {
    @Test fun `delivery is transient and scoped to user app and installation`() {
        val broker = MockPushBroker()
        val user = UUID.randomUUID(); val session = UUID.randomUUID(); val install = UUID.randomUUID()
        val target = MockPushBroker.Target(SessionPrincipal(session, user), "app", install)
        val event = MockPushBroker.Event("message", "store", null)
        assertEquals(0, broker.publish("app", user, install, event))
        val received = mutableListOf<MockPushBroker.Event>()
        val subscription = broker.subscribe(target) { received.add(it); true }
        assertEquals(0, received.size)
        assertEquals(0, broker.publish("other", user, install, event))
        assertEquals(0, broker.publish("app", UUID.randomUUID(), install, event))
        assertEquals(0, broker.publish("app", user, UUID.randomUUID(), event))
        assertEquals(1, broker.publish("app", user, install, event))
        assertEquals(listOf(event), received)
        broker.unsubscribe(subscription)
        assertEquals(0, broker.publish("app", user, install, event))
        assertEquals(1, received.size)
    }
    @Test fun `failed subscribers are removed`() {
        val broker = MockPushBroker(); val user = UUID.randomUUID(); val install = UUID.randomUUID()
        var calls = 0
        broker.subscribe(MockPushBroker.Target(SessionPrincipal(UUID.randomUUID(), user), "app", install)) { calls++; false }
        repeat(2) { assertEquals(0, broker.publish("app", user, install, MockPushBroker.Event("id", "home", null))) }
        assertEquals(1, calls)
    }
}
