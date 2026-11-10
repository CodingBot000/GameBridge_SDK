package com.gamebridge.purchase

import jakarta.annotation.PreDestroy
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.scheduling.annotation.EnableScheduling
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import org.springframework.transaction.support.TransactionTemplate
import java.math.BigInteger
import java.time.Duration
import java.time.Instant
import java.util.UUID
import java.util.concurrent.SynchronousQueue
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import javax.sql.DataSource

@Component
@Profile("local-mock")
class FinalizationPolicy(
    @Value("\${gamebridge.finalization.worker-concurrency:1}") val concurrency: Int,
    @Value("\${gamebridge.finalization.initial-backoff-seconds:5}") val initialBackoffSeconds: Long,
    @Value("\${gamebridge.finalization.poll-interval-ms:5000}") val pollIntervalMs: Long,
) {
    init { require(concurrency > 0 && initialBackoffSeconds > 0 && pollIntervalMs > 0) { "CONFIG_REQUIRED: finalization policy" } }
    fun retryAt(attempt: Int, now: Instant): Instant {
        require(attempt > 0)
        // 9999 is a representational ceiling, not a retry limit; the job remains pending.
        val ceiling = Instant.parse("9999-12-31T23:59:59Z")
        val available = Duration.between(now, ceiling).seconds.coerceAtLeast(0)
        val seconds = BigInteger.valueOf(initialBackoffSeconds).shiftLeft((attempt - 1).coerceAtMost(63))
            .min(BigInteger.valueOf(available)).longValueExact()
        return now.plusSeconds(seconds)
    }
}

fun interface StoreFinalizer { fun finish(attempt: Int): Boolean }

/** Advisory slots bound active finalizers across workers sharing one configured database. */
@Component
@Profile("local-mock")
class FinalizationWorker(private val db: JdbcTemplate, private val tx: TransactionTemplate,
                         private val dataSource: DataSource, private val finalizer: StoreFinalizer,
                         private val policy: FinalizationPolicy) {
    data class Claim(val purchaseId: UUID, val attempt: Int)
    fun runOnce(onlyPurchaseId: UUID? = null): Boolean {
        dataSource.connection.use { connection ->
            var lockId: Long? = null
            try {
                for (slot in 0 until policy.concurrency) {
                    val candidate = 0x47424c1000000000L + slot
                    val acquired = connection.prepareStatement("SELECT pg_try_advisory_lock(?)").use { statement ->
                        statement.setLong(1, candidate)
                        statement.executeQuery().use { it.next() && it.getBoolean(1) }
                    }
                    if (acquired) { lockId = candidate; break }
                }
                if (lockId == null) return false
                return processOne(onlyPurchaseId)
            } finally {
                lockId?.let { held ->
                    connection.prepareStatement("SELECT pg_advisory_unlock(?)").use { statement ->
                        statement.setLong(1, held); statement.executeQuery().use { it.next() }
                    }
                }
            }
        }
    }
    private fun processOne(onlyPurchaseId: UUID?): Boolean {
        val claim = tx.execute {
            val filter = if (onlyPurchaseId == null) "" else " AND purchase_id=?"
            val args: Array<Any> = if (onlyPurchaseId == null) emptyArray() else arrayOf(onlyPurchaseId)
            val id = db.query("""SELECT purchase_id FROM store_finalization_jobs
                WHERE status IN ('PENDING','PROCESSING') AND next_attempt_at <= now()$filter
                ORDER BY next_attempt_at, purchase_id FOR UPDATE SKIP LOCKED LIMIT 1""", { rs, _ -> rs.getObject(1, UUID::class.java) }, *args).firstOrNull()
                ?: return@execute null
            db.queryForObject("""UPDATE store_finalization_jobs SET status='PROCESSING', attempt_count=attempt_count+1,
                next_attempt_at=now()+interval '30 seconds' WHERE purchase_id=? RETURNING attempt_count""", Int::class.java, id)
                ?.let { Claim(id, it) }
        } ?: return false
        // Mock store work runs after the claim transaction, while an advisory slot is held.
        val success = try { finalizer.finish(claim.attempt) } catch (_: Exception) { false }
        tx.executeWithoutResult {
            val status = if (success) "FINALIZED" else "PENDING"
            val nextAttempt = java.sql.Timestamp.from(policy.retryAt(claim.attempt, Instant.now()))
            val changed = db.update("""UPDATE store_finalization_jobs SET status=?, next_attempt_at=?,
                last_error=? WHERE purchase_id=? AND status='PROCESSING' AND attempt_count=?""",
                status, nextAttempt, if (success) null else "MOCK_TRANSIENT", claim.purchaseId, claim.attempt)
            if (changed == 1 && success) db.update("UPDATE purchases SET finalization_state='FINALIZED' WHERE id=? AND fulfillment_state='GRANTED'", claim.purchaseId)
        }
        return true
    }
}

@Component
@Profile("local-mock")
class MockFinalizer : StoreFinalizer {
    override fun finish(attempt: Int): Boolean = attempt > 1
}

@Configuration
@Profile("local-mock")
@EnableScheduling
class LocalFinalizationScheduling

@Component
@Profile("local-mock")
class FinalizationScheduler(private val worker: FinalizationWorker, private val policy: FinalizationPolicy) {
    private val executor = ThreadPoolExecutor(policy.concurrency, policy.concurrency, 0, TimeUnit.MILLISECONDS,
        SynchronousQueue(), ThreadPoolExecutor.DiscardPolicy())
    @Scheduled(fixedDelayString = "\${gamebridge.finalization.poll-interval-ms:5000}")
    fun poll() { repeat(policy.concurrency) { executor.execute { worker.runOnce() } } }
    @PreDestroy fun close() { executor.shutdown() }
}
