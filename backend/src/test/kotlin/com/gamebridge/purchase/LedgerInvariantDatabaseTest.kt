package com.gamebridge.purchase

import org.flywaydb.core.Flyway
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.dao.DataIntegrityViolationException
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DriverManagerDataSource
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

/** Creates and preserves a unique test-only schema; never mutates an existing schema. */
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class LedgerInvariantDatabaseTest {
    @Test fun `one ledger entry per purchase is enforced by database`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL"))
        val user = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER"))
        val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, user, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_ledger_invariant_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scoped = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scoped, user, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val db = JdbcTemplate(DriverManagerDataSource(scoped, user, password))
        if (System.getenv("GAMEBRIDGE_MUTATE_LEDGER_TEST") == "true") {
            // This mutation is restricted to the unique schema created immediately above.
            db.execute("ALTER TABLE wallet_ledger DROP CONSTRAINT wallet_ledger_purchase_id_key")
        }
        val userId = UUID.randomUUID(); val purchase = UUID.randomUUID()
        db.update("INSERT INTO users(id) VALUES (?)", userId)
        db.update("""INSERT INTO purchases(id,app_id,environment,platform,proof_key_hash,user_id,product_id,store_state,fulfillment_state,finalization_state)
            VALUES (?, 'test-app', 'local-mock', 'MOCK', ?, ?, 'coins_100', 'PURCHASED', 'GRANTED', 'PENDING')""", purchase, UUID.randomUUID().toString().toByteArray(), userId)
        fun insert() = db.update("INSERT INTO wallet_ledger(id,purchase_id,user_id,delta,reason) VALUES (?,?,?,100,'TEST')", UUID.randomUUID(), purchase, userId)
        assertEquals(1, insert())
        assertFailsWith<DataIntegrityViolationException> { insert() }
        assertEquals(1, db.queryForObject("SELECT count(*) FROM wallet_ledger WHERE purchase_id=?", Int::class.java, purchase))
    }
}
