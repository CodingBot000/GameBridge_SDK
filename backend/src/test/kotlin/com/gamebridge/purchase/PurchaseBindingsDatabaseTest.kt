package com.gamebridge.purchase

import com.gamebridge.auth.IdentityProvider
import com.gamebridge.auth.VerifiedIdentity
import com.gamebridge.session.SessionService
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.server.ResponseStatusException
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
    @Test fun `binding scope comes only from active authenticated session`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")); val username = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")); val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, username, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_scope_test_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scopedUrl = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scopedUrl, username, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val source = DriverManagerDataSource(scopedUrl, username, password); val db = JdbcTemplate(source)
        val sessions = SessionService(db, TransactionTemplate(DataSourceTransactionManager(source)))
        val controller = PurchaseBindingController(db, PurchaseBindings(db))
        val identity = VerifiedIdentity(IdentityProvider.GOOGLE, "https://accounts.google.com", "test-subject", "test-client")
        val first = sessions.createVerified(identity, "app-one", null)
        val second = sessions.createVerified(identity, "app-two", null)
        fun auth(token: String) = UsernamePasswordAuthenticationToken(sessions.authenticate(token)!!, null, emptyList())
        val principal = sessions.authenticate(first.accessToken)!!
        val firstBinding = controller.binding(auth(first.accessToken))
        assertEquals(firstBinding, controller.binding(auth(first.accessToken)))
        assertNotEquals(firstBinding, controller.binding(auth(second.accessToken)))
        assertEquals("app-one", db.queryForObject("SELECT app_scope FROM sessions WHERE id=?", String::class.java, principal.sessionId))
        db.update("UPDATE sessions SET app_scope=NULL WHERE id=?", principal.sessionId)
        assertEquals(401, assertFailsWith<ResponseStatusException> { controller.binding(auth(first.accessToken)) }.statusCode.value())
        assertNull(db.queryForObject("SELECT app_scope FROM sessions WHERE id=?", String::class.java, principal.sessionId))
    }
}
