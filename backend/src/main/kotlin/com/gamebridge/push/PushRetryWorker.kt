package com.gamebridge.push

import jakarta.annotation.PreDestroy
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.dao.TransientDataAccessException
import org.springframework.jdbc.CannotGetJdbcConnectionException
import org.springframework.stereotype.Component
import java.time.Duration
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ScheduledThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

/** In-memory development retries; only targets/content are retained, never the device token. */
internal class PushRetryWorker(private val policy: PushRetryPolicy, concurrency: Int,
                               private val send: (PushDispatchTarget, PushContent) -> PushDispatchOutcome) {
    private val capacity = 100
    private val pending = AtomicInteger()
    private val executor = ScheduledThreadPoolExecutor(concurrency).apply {
        require(concurrency > 0)
        setExecuteExistingDelayedTasksAfterShutdownPolicy(false)
        removeOnCancelPolicy = true
    }
    fun submit(target: PushDispatchTarget, content: PushContent, provider: PushProvider? = null): Boolean {
        while (true) {
            val count = pending.get()
            if (count >= capacity) return false
            if (pending.compareAndSet(count, count + 1)) break
        }
        return schedule(target, content, provider, 0, Duration.ZERO)
    }
    private fun schedule(target: PushDispatchTarget, content: PushContent, provider: PushProvider?, retries: Int, delay: Duration): Boolean = try {
        val delayMillis = try { delay.toMillis() } catch (_: ArithmeticException) { Long.MAX_VALUE }
        executor.schedule({
            val outcome = try { send(target, content) }
                catch (_: TransientDataAccessException) { PushDispatchOutcome(provider, PushAttempt(PushSendResult.RETRYABLE, PushFailure.TIMEOUT)) }
                catch (_: CannotGetJdbcConnectionException) { PushDispatchOutcome(provider, PushAttempt(PushSendResult.RETRYABLE, PushFailure.TIMEOUT)) }
                catch (_: Exception) { PushDispatchOutcome(null, PushAttempt(PushSendResult.FAILED, PushFailure.PERMANENT)) }
            val next = if (outcome.attempt.result == PushSendResult.RETRYABLE && outcome.provider != null && outcome.attempt.failure != null)
                policy.delay(outcome.provider, outcome.attempt.failure, retries) else null
            if (next == null) pending.decrementAndGet() else schedule(target, content, outcome.provider, retries + 1, next)
        }, delayMillis, TimeUnit.MILLISECONDS)
        true
    } catch (_: RejectedExecutionException) { pending.decrementAndGet(); false }
    fun pendingCount(): Int = pending.get()
    fun close() { executor.shutdownNow() }
}
internal enum class PushQueueResult { QUEUED, NO_DEVICE, BUSY }
@Component
@Profile("sandbox")
internal class SandboxPushRuntime(private val dispatcher: PushDispatcher, private val senders: ConfiguredPushSenders,
                                  policy: PushRetryPolicy, @Value("\${gamebridge.push.worker-concurrency:1}") concurrency: Int) {
    private val worker = PushRetryWorker(policy, concurrency, dispatcher::send)
    fun enqueue(target: PushDispatchTarget, content: PushContent): PushQueueResult {
        val provider = dispatcher.providerFor(target) ?: return PushQueueResult.NO_DEVICE
        when (provider) {
            PushProvider.FCM -> senders.fcm(target.app)
            PushProvider.APNS -> senders.apns(target.app, ApnsEnvironment.SANDBOX)
        }
        return if (worker.submit(target, content, provider)) PushQueueResult.QUEUED else PushQueueResult.BUSY
    }
    @PreDestroy fun close() { worker.close() }
}
