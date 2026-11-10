package com.gamebridge.purchase

import org.springframework.context.annotation.Profile
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Component
import org.springframework.transaction.support.TransactionTemplate
import java.util.UUID

/** One attempt per call; claim leases make a crashed worker's job eligible again. */
@Component
@Profile("local-mock")
class FinalizationWorker(private val db: JdbcTemplate, private val tx: TransactionTemplate, private val finalizer: MockFinalizer) {
    data class Claim(val purchaseId: UUID, val attempt: Int)
    fun runOnce(onlyPurchaseId: UUID? = null): Boolean {
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
        // Store or network work must remain outside the DB transaction.
        val success = finalizer.finish(claim.attempt)
        tx.executeWithoutResult {
            val status = if (success) "FINALIZED" else "PENDING"
            val changed = db.update("""UPDATE store_finalization_jobs SET status=?, next_attempt_at=now()+interval '1 second',
                last_error=? WHERE purchase_id=? AND status='PROCESSING' AND attempt_count=?""",
                status, if (success) null else "MOCK_TRANSIENT", claim.purchaseId, claim.attempt)
            if (changed == 1 && success) db.update("UPDATE purchases SET finalization_state='FINALIZED' WHERE id=? AND fulfillment_state='GRANTED'", claim.purchaseId)
        }
        return true
    }
}

/** Deterministic failure injection for the explicit local-mock mode only. */
@Component
@Profile("local-mock")
class MockFinalizer {
    fun finish(attempt: Int): Boolean = attempt > 1
}
