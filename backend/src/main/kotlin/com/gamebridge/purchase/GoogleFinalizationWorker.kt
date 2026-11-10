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

internal data class GoogleFinalizationClaim(val purchaseId: UUID, val attempt: Int, val app: String, val environment: StoreEnvironment,
                                            val storeId: String, val account: String, val encrypted: ByteArray, val action: GoogleFinalizationAction) {
    override fun toString() = "GoogleFinalizationClaim([redacted])"
}
internal fun interface GoogleFinalizationExecutor { fun finish(claim: GoogleFinalizationClaim, token: String) }

@Component
@Profile("sandbox", "production")
internal class GoogleFinalizationPolicy(
    @Value("\${gamebridge.finalization.worker-concurrency:1}") val concurrency: Int,
    @Value("\${gamebridge.finalization.initial-backoff-seconds:5}") val initialBackoffSeconds: Long,
) {
    init { require(concurrency > 0 && initialBackoffSeconds > 0) }
    fun retryAt(attempt: Int, now: Instant): Instant {
        val ceiling = Instant.parse("9999-12-31T23:59:59Z")
        val remaining = Duration.between(now, ceiling).seconds.coerceAtLeast(0)
        val seconds = BigInteger.valueOf(initialBackoffSeconds).shiftLeft((attempt - 1).coerceIn(0, 63)).min(BigInteger.valueOf(remaining)).longValueExact()
        return now.plusSeconds(seconds)
    }
}

/** Holds an advisory slot across the external call, never a database transaction. */
@Component
@Profile("sandbox", "production")
internal class GoogleFinalizationWorker(private val db: JdbcTemplate, private val tx: TransactionTemplate, private val dataSource: DataSource,
                                         private val cipher: GoogleEvidenceCipher, private val executor: GoogleFinalizationExecutor,
                                         private val policy: GoogleFinalizationPolicy) {
    fun runOnce(onlyPurchaseId: UUID? = null): Boolean = dataSource.connection.use { connection ->
        var slot: Long? = null
        try {
            for (i in 0 until policy.concurrency) {
                val candidate = 0x47424c2000000000L + i
                val acquired = connection.prepareStatement("SELECT pg_try_advisory_lock(?)").use { statement ->
                    statement.setLong(1, candidate); statement.executeQuery().use { it.next() && it.getBoolean(1) }
                }
                if (acquired) { slot = candidate; break }
            }
            if (slot == null) false else processOne(onlyPurchaseId)
        } finally {
            slot?.let { held -> connection.prepareStatement("SELECT pg_advisory_unlock(?)").use { statement ->
                statement.setLong(1, held); statement.executeQuery().use { it.next() }
            } }
        }
    }
    private fun processOne(onlyPurchaseId: UUID?): Boolean {
        val claim = tx.execute {
            val filter = if (onlyPurchaseId == null) "" else " AND j.purchase_id=?"
            val args: Array<Any> = if (onlyPurchaseId == null) emptyArray() else arrayOf(onlyPurchaseId)
            val id = db.query("""SELECT j.purchase_id FROM store_finalization_jobs j JOIN purchases p ON p.id=j.purchase_id
                WHERE j.status IN ('PENDING','PROCESSING') AND j.action IN ('GOOGLE_CONSUME','GOOGLE_ACKNOWLEDGE')
                AND p.platform='GOOGLE' AND p.fulfillment_state='GRANTED' AND p.evidence_encrypted IS NOT NULL AND j.next_attempt_at<=now()$filter
                ORDER BY j.next_attempt_at,j.purchase_id FOR UPDATE OF j SKIP LOCKED LIMIT 1""", { rs, _ -> rs.getObject(1, UUID::class.java) }, *args).firstOrNull() ?: return@execute null
            val attempt = db.queryForObject("UPDATE store_finalization_jobs SET status='PROCESSING',attempt_count=attempt_count+1,next_attempt_at=now()+interval '90 seconds' WHERE purchase_id=? RETURNING attempt_count", Int::class.java, id)!!
            db.queryForObject("""SELECT p.app_id,p.environment,pr.store_id,b.google_obfuscated_id,p.evidence_encrypted,j.action
                FROM purchases p JOIN store_finalization_jobs j ON j.purchase_id=p.id
                JOIN products pr ON pr.app_id=p.app_id AND pr.platform='GOOGLE' AND pr.logical_id=p.product_id
                JOIN purchase_account_bindings b ON b.app_id=p.app_id AND b.user_id=p.user_id WHERE p.id=?""", { rs, _ ->
                GoogleFinalizationClaim(id, attempt, rs.getString(1), StoreEnvironment.valueOf(rs.getString(2)), rs.getString(3),
                    rs.getObject(4, UUID::class.java).toString(), rs.getBytes(5),
                    if (rs.getString(6) == "GOOGLE_CONSUME") GoogleFinalizationAction.CONSUME else GoogleFinalizationAction.ACKNOWLEDGE)
            }, id)
        } ?: return false
        val success = try {
            val token = cipher.decrypt(claim.encrypted, "${claim.app}:${claim.environment.name}:GOOGLE:${claim.purchaseId}")
            executor.finish(claim, token); true
        } catch (_: InterruptedException) { Thread.currentThread().interrupt(); false }
        catch (_: Exception) { false }
        tx.executeWithoutResult {
            val changed = if (success) db.update("UPDATE store_finalization_jobs SET status='DONE',last_error=NULL WHERE purchase_id=? AND status='PROCESSING' AND attempt_count=?", claim.purchaseId, claim.attempt)
                else db.update("UPDATE store_finalization_jobs SET status='PENDING',next_attempt_at=?,last_error='STORE_RETRY' WHERE purchase_id=? AND status='PROCESSING' AND attempt_count=?", java.sql.Timestamp.from(policy.retryAt(claim.attempt, Instant.now())), claim.purchaseId, claim.attempt)
            if (success && changed == 1) check(db.update("UPDATE purchases SET finalization_state='FINALIZED',evidence_encrypted=NULL WHERE id=? AND fulfillment_state='GRANTED'", claim.purchaseId) == 1)
        }
        return true
    }
}
@Configuration
@Profile("sandbox", "production")
@EnableScheduling
internal class GoogleFinalizationScheduling
@Component
@Profile("sandbox", "production")
internal class GoogleFinalizationScheduler(private val worker: GoogleFinalizationWorker, policy: GoogleFinalizationPolicy) {
    private val count = policy.concurrency
    private val executor = ThreadPoolExecutor(count, count, 0, TimeUnit.MILLISECONDS, SynchronousQueue(), ThreadPoolExecutor.DiscardPolicy())
    @Scheduled(fixedDelayString = "\${gamebridge.finalization.poll-interval-ms:5000}")
    fun poll() { repeat(count) { executor.execute { worker.runOnce() } } }
    @PreDestroy fun close() { executor.shutdown() }
}
