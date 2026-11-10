package com.gamebridge.purchase

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.jdbc.datasource.DriverManagerDataSource
import org.springframework.transaction.support.TransactionTemplate
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** Opt-in against the dedicated local-mock DB only; creates uniquely identified test rows. */
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class FinalizationDatabaseTest {
    @Test fun `retry survives worker recreation without second grant`() {
        val source = DriverManagerDataSource(
            requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")),
            requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")),
            requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")),
        )
        val db = JdbcTemplate(source)
        val profile = db.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java)
        require(profile == "local-mock")
        val transaction = TransactionTemplate(DataSourceTransactionManager(source))
        val user = UUID.randomUUID(); val purchase = UUID.randomUUID(); val ledger = UUID.randomUUID()
        transaction.executeWithoutResult {
            db.update("INSERT INTO users(id,display_name) VALUES (?, 'finalization-test')", user)
            db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state)
                VALUES (?, 'gamebridge-sample', 'local-mock', 'MOCK', ?, ?, 'coins_100', 'PURCHASED', 'GRANTED', 'PENDING')""", purchase, UUID.randomUUID().toString().toByteArray(), user)
            db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) VALUES (?,?,?,100,'TEST')", ledger, purchase, user)
            db.update("INSERT INTO store_finalization_jobs(purchase_id,action,next_attempt_at,status) VALUES (?, 'MOCK', now(), 'PENDING')", purchase)
        }
        val first = FinalizationWorker(db, transaction, MockFinalizer())
        assertTrue(first.runOnce(purchase))
        assertEquals("PENDING", db.queryForObject("SELECT status FROM store_finalization_jobs WHERE purchase_id=?", String::class.java, purchase))
        db.update("UPDATE store_finalization_jobs SET next_attempt_at=now() WHERE purchase_id=?", purchase)
        val recreated = FinalizationWorker(db, transaction, MockFinalizer())
        assertTrue(recreated.runOnce(purchase))
        assertEquals("FINALIZED", db.queryForObject("SELECT finalization_state FROM purchases WHERE id=?", String::class.java, purchase))
        assertEquals(1, db.queryForObject("SELECT COUNT(*) FROM wallet_ledger WHERE purchase_id=?", Int::class.java, purchase))
        assertEquals(100L, db.queryForObject("SELECT SUM(delta) FROM wallet_ledger WHERE purchase_id=?", Long::class.java, purchase))
    }
}
