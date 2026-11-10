package com.gamebridge.push

import com.gamebridge.session.SessionPrincipal
import org.junit.jupiter.api.Test
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlin.test.*

class PushRetryWorkerTest {
    @Test fun `three retries after original attempt eventually stop`() {
        val calls = AtomicInteger(); val finished = CountDownLatch(4)
        val target = PushDispatchTarget(SessionPrincipal(UUID.randomUUID(), UUID.randomUUID()), "test-app", "sandbox", UUID.randomUUID())
        val worker = PushRetryWorker(PushRetryPolicy(maxRetries = 3, initialSeconds = 1), 1) { _, _ ->
            calls.incrementAndGet(); finished.countDown()
            PushDispatchOutcome(PushProvider.FCM, PushAttempt(PushSendResult.RETRYABLE, PushFailure.SERVER_ERROR))
        }
        try {
            assertTrue(worker.submit(target, PushContent("test", "home", "title", "body")))
            assertTrue(finished.await(12, TimeUnit.SECONDS))
            val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(2)
            while (worker.pendingCount() != 0 && System.nanoTime() < deadline) Thread.yield()
            assertEquals(0, worker.pendingCount()); assertEquals(4, calls.get())
        } finally { worker.close() }
    }
    @Test fun `queue rejects over one hundred pending requests`() {
        val entered = CountDownLatch(1); val release = CountDownLatch(1)
        val target = PushDispatchTarget(SessionPrincipal(UUID.randomUUID(), UUID.randomUUID()), "test-app", "sandbox", UUID.randomUUID())
        val worker = PushRetryWorker(PushRetryPolicy(), 1) { _, _ ->
            entered.countDown(); release.await(5, TimeUnit.SECONDS); PushDispatchOutcome(PushProvider.FCM, PushAttempt(PushSendResult.SENT))
        }
        try {
            assertTrue(worker.submit(target, PushContent("first", "home", "title", "body")))
            assertTrue(entered.await(5, TimeUnit.SECONDS))
            repeat(99) { assertTrue(worker.submit(target, PushContent("q$it", "home", "title", "body"))) }
            assertFalse(worker.submit(target, PushContent("overflow", "home", "title", "body")))
        } finally { release.countDown(); worker.close() }
    }
    @Test fun `transient database failure is retried without retaining a token`() {
        val calls = AtomicInteger(); val finished = CountDownLatch(1)
        val target = PushDispatchTarget(SessionPrincipal(UUID.randomUUID(), UUID.randomUUID()), "test-app", "sandbox", UUID.randomUUID())
        val worker = PushRetryWorker(PushRetryPolicy(maxRetries = 1, initialSeconds = 1), 1) { _, _ ->
            if (calls.incrementAndGet() == 1) throw org.springframework.dao.TransientDataAccessResourceException("test")
            finished.countDown(); PushDispatchOutcome(PushProvider.FCM, PushAttempt(PushSendResult.SENT))
        }
        try {
            assertTrue(worker.submit(target, PushContent("test", "home", "title", "body"), PushProvider.FCM))
            assertTrue(finished.await(5, TimeUnit.SECONDS)); assertEquals(2, calls.get())
        } finally { worker.close() }
    }
    @Test fun `one worker serializes attempts and retries transient failure`() {
        val entered = CountDownLatch(1); val release = CountDownLatch(1); val finished = CountDownLatch(2)
        val active = AtomicInteger(); val maximum = AtomicInteger(); val firstCalls = AtomicInteger()
        val target = PushDispatchTarget(SessionPrincipal(UUID.randomUUID(), UUID.randomUUID()), "test-app", "sandbox", UUID.randomUUID())
        val worker = PushRetryWorker(PushRetryPolicy(maxRetries = 1, initialSeconds = 1), 1) { _, content -> // Test-only short delay.
            val running = active.incrementAndGet(); maximum.updateAndGet { maxOf(it, running) }
            try {
                if (content.messageId == "first" && firstCalls.incrementAndGet() == 1) {
                    entered.countDown(); assertTrue(release.await(5, TimeUnit.SECONDS))
                    PushDispatchOutcome(PushProvider.FCM, PushAttempt(PushSendResult.RETRYABLE, PushFailure.RATE_LIMIT))
                } else { finished.countDown(); PushDispatchOutcome(PushProvider.FCM, PushAttempt(PushSendResult.SENT)) }
            } finally { active.decrementAndGet() }
        }
        try {
            assertTrue(worker.submit(target, PushContent("first", "home", "title", "body")))
            assertTrue(entered.await(5, TimeUnit.SECONDS))
            assertTrue(worker.submit(target, PushContent("second", "store", "title", "body")))
            assertEquals(2L, finished.count)
            release.countDown(); assertTrue(finished.await(5, TimeUnit.SECONDS))
            assertEquals(1, maximum.get()); assertEquals(2, firstCalls.get())
        } finally { release.countDown(); worker.close() }
    }
}
