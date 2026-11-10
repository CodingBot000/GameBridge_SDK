package com.gamebridge.session

import java.security.MessageDigest
import java.time.Duration
import java.time.Instant
import java.util.UUID
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.jdbc.datasource.DriverManagerDataSource
import org.springframework.transaction.support.TransactionTemplate
import kotlin.test.assertEquals
import kotlin.test.assertTrue

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_SESSION_DB_TESTS", matches = "true")
class SessionExpiryDatabaseTest {
    @Test fun `refresh rotation retains original seven day deadline`() {
        val source = DriverManagerDataSource(requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")),
            requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")), requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD")))
        val db = JdbcTemplate(source)
        require(db.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val service = SessionService(db, TransactionTemplate(DataSourceTransactionManager(source)))
        val session = service.createMock("expiry-test-" + UUID.randomUUID())
        fun expiration(token: String): Instant {
            val hash = MessageDigest.getInstance("SHA-256").digest(token.toByteArray())
            return db.queryForObject("SELECT refresh_expires_at FROM sessions WHERE refresh_hash=?", java.sql.Timestamp::class.java, hash)!!.toInstant()
        }
        val first = expiration(session.refreshToken)
        assertTrue(Duration.between(Instant.now(), first).seconds in 604790..604800)
        val next = service.refresh(session.refreshToken)
        assertEquals(first, expiration(next.refreshToken))
    }
}
