package com.gamebridge.push

import com.gamebridge.session.SessionService
import org.flywaydb.core.Flyway
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.jdbc.datasource.DriverManagerDataSource
import org.springframework.mock.env.MockEnvironment
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.transaction.support.TransactionTemplate
import java.util.Base64
import java.util.UUID
import kotlin.test.*

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class PushDispatcherDatabaseTest {
    @Test fun `rotation and logout prevent stale invalidation or later sends`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")); val username = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")); val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, username, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_push_dispatch_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scoped = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scoped, username, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val source = DriverManagerDataSource(scoped, username, password); val db = JdbcTemplate(source); val tx = TransactionTemplate(DataSourceTransactionManager(source))
        val sessions = SessionService(db, tx); val subject = "test-" + UUID.randomUUID()
        val tokens = sessions.createMock(subject); val principal = sessions.authenticate(tokens.accessToken)!!
        val auth = UsernamePasswordAuthenticationToken(principal, null, emptyList()); val environment = MockEnvironment().apply { setActiveProfiles("sandbox") }
        val cipher = TokenCipher(Base64.getEncoder().encodeToString(ByteArray(32) { it.toByte() })) // Test-only key.
        val registrations = DeviceRegistrationController(db, cipher, tx, environment); val installation = UUID.randomUUID()
        fun register(token: String) = registrations.register(auth, installation, DeviceRegistrationInput(token, "FCM", "ANDROID"))
        register("synthetic-old")
        var calls = 0
        val provider = PushProviderClient { _, _, token, _ ->
            calls++
            if (calls == 1) { assertEquals("synthetic-old", token); register("synthetic-new"); PushAttempt(PushSendResult.INVALID_TOKEN, PushFailure.INVALID_TOKEN) }
            else { assertEquals("synthetic-new", token); PushAttempt(PushSendResult.SENT) }
        }
        val dispatcher = PushDispatcher(db, cipher, PushTokenInvalidator(db), provider)
        val target = PushDispatchTarget(principal, "gamebridge-sample", "sandbox", installation)
        val content = PushContent("test", "home", "title", "body")
        assertEquals(PushSendResult.INVALID_TOKEN, dispatcher.send(target, content).result)
        assertEquals(false, db.queryForObject("SELECT invalidated_at IS NOT NULL FROM device_tokens WHERE installation_id=?", Boolean::class.java, installation))
        assertEquals(PushSendResult.SENT, dispatcher.send(target, content).result)
        val next = sessions.authenticate(sessions.createMock(subject).accessToken)!!
        sessions.logout(principal)
        val nextAuth = UsernamePasswordAuthenticationToken(next, null, emptyList())
        registrations.register(nextAuth, installation, DeviceRegistrationInput("synthetic-next", "FCM", "ANDROID"))
        assertEquals(PushSendResult.FAILED, dispatcher.send(target, content).result)
        assertEquals(2, calls)
    }
}
