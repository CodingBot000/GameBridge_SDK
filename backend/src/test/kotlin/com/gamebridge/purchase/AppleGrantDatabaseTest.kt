package com.gamebridge.purchase

import com.apple.itunes.storekit.model.Environment
import com.apple.itunes.storekit.model.JWSTransactionDecodedPayload
import com.apple.itunes.storekit.model.Type
import com.gamebridge.auth.IdentityProvider
import com.gamebridge.auth.VerifiedIdentity
import com.gamebridge.session.SessionService
import org.flywaydb.core.Flyway
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.datasource.DataSourceTransactionManager
import org.springframework.jdbc.datasource.DriverManagerDataSource
import org.springframework.transaction.support.TransactionTemplate
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class AppleGrantDatabaseTest {
    @Test fun `concurrent verified transactions grant once and cannot change owner`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")); val user = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")); val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, user, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_apple_grant_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scoped = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scoped, user, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val source = DriverManagerDataSource(scoped, user, password); val db = JdbcTemplate(source)
        val tx = TransactionTemplate(DataSourceTransactionManager(source)); val sessions = SessionService(db, tx)
        val app = "test-" + UUID.randomUUID()
        db.update("INSERT INTO products(app_id,logical_id,platform,store_id,type,grant_amount) VALUES (?, 'coins_100', 'APPLE', 'coins.apple', 'CONSUMABLE', 100)", app)
        fun session(subject: String) = sessions.createVerified(VerifiedIdentity(IdentityProvider.APPLE, "https://appleid.apple.com", subject, "test"), app, null)
        val token = session("user-a"); val principal = sessions.authenticate(token.accessToken)!!
        val binding = PurchaseBindings(db).forUser(principal.userId, app).appleAccountToken
        val verified = VerifiedApplePurchase("synthetic-transaction", "coins.apple", binding)
        val service = AppleGrantService(db, tx)
        val payload = JWSTransactionDecodedPayload().bundleId("test.bundle").environment(Environment.SANDBOX)
            .productId("coins.apple").appAccountToken(binding).transactionId("synthetic-transaction").quantity(1).type(Type.CONSUMABLE)
        val verifier = ApplePurchaseVerifier("test.bundle", Environment.SANDBOX, setOf("coins.apple"), AppleSignedTransactionDecoder { payload })
        val pipeline = ApplePurchasePipeline(db, AppleVerifierRegistry { scope, environment ->
            assertEquals(app, scope); assertEquals(StoreEnvironment.SANDBOX, environment); verifier
        }, service)
        val pool = Executors.newFixedThreadPool(10)
        val results = try { (1..10).map { pool.submit<AppleGrantResult> { pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "coins.apple", "synthetic-jws") } }.map { it.get(20, TimeUnit.SECONDS) } }
            finally { pool.shutdownNow() }
        assertEquals(1, results.count { it.fulfillmentStatus == "GRANTED" })
        assertEquals(1, results.map { it.serverPurchaseId }.toSet().size)
        assertEquals(100L, db.queryForObject("SELECT COALESCE(SUM(delta),0) FROM wallet_ledger WHERE user_id=?", Long::class.java, principal.userId))
        val other = sessions.authenticate(session("user-b").accessToken)!!
        val otherBinding = PurchaseBindings(db).forUser(other.userId, app).appleAccountToken
        assertFailsWith<AppleProofRejected> { pipeline.verifyAndGrant(other, StoreEnvironment.SANDBOX, "coins.apple", "synthetic-jws") }
        assertEquals("PURCHASE_ACCOUNT_MISMATCH", assertFailsWith<PurchaseConflict> {
            service.grant(other, StoreEnvironment.SANDBOX, verified.copy(account = otherBinding))
        }.errorCode)
        assertEquals(1, db.queryForObject("SELECT COUNT(*) FROM wallet_ledger", Int::class.java))
    }
}
