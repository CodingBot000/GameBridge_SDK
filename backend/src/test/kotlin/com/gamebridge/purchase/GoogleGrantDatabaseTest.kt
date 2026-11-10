package com.gamebridge.purchase

import com.google.api.services.androidpublisher.model.ProductPurchaseV2
import com.google.api.services.androidpublisher.model.ProductLineItem
import com.google.api.services.androidpublisher.model.ProductOfferDetails
import com.google.api.services.androidpublisher.model.PurchaseStateContext
import com.google.api.services.androidpublisher.model.TestPurchaseContext
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
import java.security.MessageDigest
import java.util.Base64
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.*

@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_DB_TESTS", matches = "true")
class GoogleGrantDatabaseTest {
    @Test fun `verified fixture grants once and stores only authenticated encrypted evidence`() {
        val url = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL")); val user = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER")); val password = requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))
        val base = JdbcTemplate(DriverManagerDataSource(url, user, password))
        require(base.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java) == "local-mock")
        val schema = "gb_google_grant_" + UUID.randomUUID().toString().replace("-", "")
        base.execute("CREATE SCHEMA $schema")
        val scoped = url + (if ('?' in url) "&" else "?") + "currentSchema=$schema"
        Flyway.configure().dataSource(scoped, user, password).schemas(schema).defaultSchema(schema)
            .locations("classpath:db/migration", "classpath:db/mock-migration").load().migrate()
        val source = DriverManagerDataSource(scoped, user, password); val db = JdbcTemplate(source)
        val tx = TransactionTemplate(DataSourceTransactionManager(source)); val sessions = SessionService(db, tx)
        val app = "test-" + UUID.randomUUID()
        db.update("INSERT INTO products(app_id,logical_id,platform,store_id,type,grant_amount) VALUES (?, 'coins_100','GOOGLE','coins.play','CONSUMABLE',100)", app)
        val tokens = sessions.createVerified(VerifiedIdentity(IdentityProvider.GOOGLE, "https://accounts.google.com", "test-user", "test"), app, null)
        val principal = sessions.authenticate(tokens.accessToken)!!
        val binding = PurchaseBindings(db).forUser(principal.userId, app).googleObfuscatedAccountId.toString()
        val token = "synthetic-secret-proof"; val hash = MessageDigest.getInstance("SHA-256").digest(token.toByteArray())
        val cipher = GoogleEvidenceCipher(Base64.getEncoder().encodeToString(ByteArray(32) { it.toByte() })) // Test-only key.
        val service = GoogleGrantService(db, tx, cipher); val verified = VerifiedGooglePurchase(hash, "coins.play", binding); val attempt = UUID.randomUUID()
        val storeResponse = ProductPurchaseV2().setPurchaseStateContext(PurchaseStateContext().setPurchaseState("PURCHASED"))
            .setObfuscatedExternalAccountId(binding).setTestPurchaseContext(TestPurchaseContext())
            .setProductLineItem(listOf(ProductLineItem().setProductId("coins.play").setProductOfferDetails(ProductOfferDetails().setQuantity(1))))
        val verifier = GooglePurchaseVerifier("test.package", setOf("coins.play"), true, GooglePurchaseLookup { _, _ -> storeResponse })
        val pipeline = GooglePurchasePipeline(db, GoogleVerifierRegistry { scope, env -> assertEquals(app, scope); assertEquals(StoreEnvironment.SANDBOX, env); verifier }, service)
        val pool = Executors.newFixedThreadPool(10)
        val results = try { (1..10).map { pool.submit<GoogleGrantResult> { pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "coins.play", token, attempt) } }.map { it.get(20, TimeUnit.SECONDS) } }
                      finally { pool.shutdownNow() }
        assertEquals(1, results.count { it.fulfillmentStatus == "GRANTED" }); assertEquals(1, results.map { it.serverPurchaseId }.toSet().size)
        assertEquals(100L, db.queryForObject("SELECT SUM(delta) FROM wallet_ledger WHERE user_id=?", Long::class.java, principal.userId))
        assertFailsWith<GoogleProofRejected> { pipeline.verifyAndGrant(principal, StoreEnvironment.SANDBOX, "unknown", token, UUID.randomUUID()) }
        val id = results.first().serverPurchaseId
        val encrypted = db.queryForObject("SELECT evidence_encrypted FROM purchases WHERE id=?", ByteArray::class.java, id)!!
        assertFalse(encrypted.toString(Charsets.ISO_8859_1).contains(token))
        assertEquals(token, cipher.decrypt(encrypted, "$app:SANDBOX:GOOGLE:$id"))
        assertFails { cipher.decrypt(encrypted, "$app:PRODUCTION:GOOGLE:$id") }
        assertEquals("GOOGLE_CONSUME", db.queryForObject("SELECT action FROM store_finalization_jobs WHERE purchase_id=?", String::class.java, id))
        assertEquals("VERIFICATION_FAILED", assertFailsWith<PurchaseConflict> { service.grant(principal, StoreEnvironment.SANDBOX, verified, "other-token", UUID.randomUUID()) }.errorCode)
    }
}
