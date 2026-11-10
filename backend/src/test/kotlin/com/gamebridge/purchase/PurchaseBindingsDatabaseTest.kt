package com.gamebridge.purchase

import org.flywaydb.core.Flyway
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DriverManagerDataSource
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class PurchaseBindingsDatabaseTest {
    @Test fun `binding is stable and distinct under concurrent creation`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")); val username = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")); val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, username, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_binding_test_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scopedUrl = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scopedUrl, username, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val db = JdbcTemplate(DriverManagerDataSource(scopedUrl, username, password))
        val userA = UUID.randomUUID(); val userB = UUID.randomUUID(); val app = "test-" + UUID.randomUUID()
        db.update("INSERT INTO users(id) VALUES (?), (?)", userA, userB)
        val bindings = PurchaseBindings(db); val pool = Executors.newFixedThreadPool(5)
        try {
            val values = (1..10).map { pool.submit<PurchaseBinding> { bindings.forUser(userA, app) } }.map { it.get(10, TimeUnit.SECONDS) }
            assertEquals(1, values.toSet().size)
            assertNotEquals(values.first(), bindings.forUser(userA, app + "-other"))
            assertNotEquals(values.first(), bindings.forUser(userB, app))
            assertNotEquals(values.first().appleAccountToken, values.first().googleObfuscatedAccountId)
            assertNotEquals(userA, values.first().appleAccountToken)
        } finally { pool.shutdownNow() }
    }
}
