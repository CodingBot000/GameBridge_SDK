package com.gamebridge

import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.security.MessageDigest
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import java.util.UUID
import kotlin.test.*

private class MemoryTokenStore : TokenStore {
    var value: String? = null
    override fun load(): String? = value
    override fun save(value: String) { this.value = value }
    override fun clear() { value = null }
}
@EnabledIfEnvironmentVariable(named = "GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST", matches = "true")
class LocalMockIntegrationTest {
    private fun sql(statement: String): String {
        val process = ProcessBuilder("docker", "exec", "-i", "gamebridge-sdk-local-postgres-1", "psql", "-U", "gamebridge", "-d", "gamebridge_local", "-v", "ON_ERROR_STOP=1", "-tA").start()
        process.outputStream.bufferedWriter().use { it.write(statement) }
        val output = process.inputStream.bufferedReader().readText().trim()
        check(process.waitFor() == 0) { "Test SQL failed" }
        return output
    }
    @Test fun `concurrent expired requests rotate only once`() = runBlocking {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:18080")
        val storage = MemoryTokenStore(); val client = LocalMockClient(config, storage, key)
        client.signIn("A")
        val raw = Json.parseToJsonElement(storage.value!!).jsonObject.getValue("refreshToken").jsonPrimitive.content
        val digest = MessageDigest.getInstance("SHA-256").digest(raw.toByteArray()).joinToString("") { "%02x".format(it) }
        assertEquals("UPDATE 1", sql("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=decode('$digest','hex');"))
        val wallets = (1..8).map { async { client.wallet() } }.awaitAll()
        assertEquals(1, wallets.map { it.userId }.distinct().size)
        assertEquals("1", sql("SELECT count(*) FROM session_refresh_history WHERE consumed_refresh_hash=decode('$digest','hex');"))
        assertFalse(storage.value.orEmpty().contains(raw))
        client.signOut()
    }
    @Test fun `expired access logout uses refresh against local backend`() = runBlocking {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:18080")
        val storage = MemoryTokenStore(); val client = LocalMockClient(config, storage, key)
        client.signIn("A")
        val raw = Json.parseToJsonElement(storage.value!!).jsonObject.getValue("refreshToken").jsonPrimitive.content
        val digest = MessageDigest.getInstance("SHA-256").digest(raw.toByteArray()).joinToString("") { "%02x".format(it) }
        assertEquals("UPDATE 1", sql("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=decode('$digest','hex');"))
        client.signOut(); assertNull(storage.value)
        assertEquals("1", sql("SELECT count(*) FROM sessions WHERE refresh_hash=decode('$digest','hex') AND revoked_at IS NOT NULL;"))
    }
    @Test fun `native client uses server authoritative wallet and restores session`() = runBlocking {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:18080")
        val storage = MemoryTokenStore(); val client = LocalMockClient(config, storage, key)
        val user = client.signIn("A")
        assertEquals(2, client.products().size)
        val before = client.wallet().coinBalance.toLong()
        val transaction = UUID.randomUUID(); val request = UUID.randomUUID()
        val purchased = client.purchase("coins_100", transaction, request)
        assertEquals(before + 100, purchased.entitlements.coinBalance.toLong())
        assertEquals(before + 100, client.purchase("coins_100", transaction, request).entitlements.coinBalance.toLong())
        val premiumTransaction = UUID.randomUUID(); val premiumAttempt = UUID.randomUUID()
        assertTrue(client.purchase("premium_unlock", premiumTransaction, premiumAttempt).entitlements.premiumEnabled)
        assertEquals("ALREADY_GRANTED", client.purchase("premium_unlock", premiumTransaction, premiumAttempt).fulfillmentStatus)
        val restored = LocalMockClient(config, storage, key)
        assertEquals(user.userId, restored.restore()?.userId)
        assertEquals(before + 100, restored.wallet().coinBalance.toLong()); assertTrue(restored.wallet().premiumEnabled)
        assertEquals("ALREADY_GRANTED", restored.purchase("coins_100", transaction, request).fulfillmentStatus)
        assertEquals("ALREADY_GRANTED", restored.purchase("premium_unlock", premiumTransaction, premiumAttempt).fulfillmentStatus)
        assertEquals(before + 100, restored.wallet().coinBalance.toLong()); assertTrue(restored.wallet().premiumEnabled)
        restored.signOut(); assertNull(storage.load())
    }
    @Test fun `bridge uses real local backend for mock purchase and restore`() {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val store = MemoryTokenStore()
        val dispatcher = BridgeDispatcher(LocalMockBridgeHandler { store })
        val installation = UUID.randomUUID().toString()
        val session = UUID.randomUUID().toString()
        fun send(operation: String, payload: kotlinx.serialization.json.JsonObject = kotlinx.serialization.json.buildJsonObject {}): kotlinx.serialization.json.JsonObject {
            val request = kotlinx.serialization.json.buildJsonObject {
                put("protocolVersion", kotlinx.serialization.json.JsonPrimitive(1)); put("sdkSessionId", kotlinx.serialization.json.JsonPrimitive(session))
                put("kind", kotlinx.serialization.json.JsonPrimitive("request")); put("requestId", kotlinx.serialization.json.JsonPrimitive(UUID.randomUUID().toString()))
                put("operation", kotlinx.serialization.json.JsonPrimitive(operation)); put("payload", payload)
            }
            val encoded = (dispatcher.dispatch(request.toString().toByteArray()) as BridgeDispatchResult.Message).json
            assertFalse(encoded.contains(key)); assertFalse(encoded.contains("accessToken")); assertFalse(encoded.contains("refreshToken"))
            store.value?.let { stored ->
                val sessionTokens = Json.parseToJsonElement(stored).jsonObject
                for (field in listOf("accessToken", "refreshToken")) {
                    val raw = sessionTokens[field]?.jsonPrimitive?.content
                    if (!raw.isNullOrEmpty()) assertFalse(encoded.contains(raw), "session token leaked in bridge response")
                }
            }
            val response = BridgeProtocol.parse(encoded.toByteArray())
            assertEquals(kotlinx.serialization.json.JsonPrimitive(true), response["ok"], "operation $operation failed")
            return response.getValue("result").jsonObject
        }
        send("sdk.initialize", kotlinx.serialization.json.buildJsonObject {
            put("providerMode", kotlinx.serialization.json.JsonPrimitive("LOCAL_MOCK")); put("appId", kotlinx.serialization.json.JsonPrimitive("gamebridge-sample"))
            put("backendBaseUrl", kotlinx.serialization.json.JsonPrimitive("http://127.0.0.1:18080")); put("requestTimeoutMs", kotlinx.serialization.json.JsonPrimitive(30000))
            put("developmentKey", kotlinx.serialization.json.JsonPrimitive(key)); put("mockSubject", kotlinx.serialization.json.JsonPrimitive("B"))
            put("installationId", kotlinx.serialization.json.JsonPrimitive(installation))
        })
        send("auth.signIn", kotlinx.serialization.json.buildJsonObject { put("provider", kotlinx.serialization.json.JsonPrimitive("MOCK")) })
        val storedTokens = Json.parseToJsonElement(assertNotNull(store.value)).jsonObject
        val secretValues = listOf("accessToken", "refreshToken").map { storedTokens.getValue(it).jsonPrimitive.content }
        for (secret in secretValues) assertTrue(secret.isNotBlank(), "synthetic session token missing")
        assertEquals("MOCK", send("push.permission").getValue("provider").jsonPrimitive.content)
        assertTrue(send("push.register").getValue("registered").jsonPrimitive.content.toBoolean())
        send("push.unregister")
        val before = send("store.entitlements").getValue("coinBalance").jsonPrimitive.content.toLong()
        val purchase = send("store.purchase", kotlinx.serialization.json.buildJsonObject { put("productId", kotlinx.serialization.json.JsonPrimitive("coins_100")) })
        assertEquals("GRANTED", purchase.getValue("fulfillmentStatus").jsonPrimitive.content)
        assertEquals(before + 100, send("store.entitlements").getValue("coinBalance").jsonPrimitive.content.toLong())
        assertEquals(kotlinx.serialization.json.JsonPrimitive(true), send("auth.restore").getValue("sessionRestored"))
        send("auth.signOut"); assertNull(store.load()); send("sdk.shutdown")
        System.getenv("GAMEBRIDGE_R22_SERVER_LOG")?.let { path ->
            val serverLog = java.io.File(path).readText()
            for (secret in secretValues + key) assertFalse(serverLog.contains(secret), "synthetic credential leaked in server log")
            java.io.File(requireNotNull(System.getenv("GAMEBRIDGE_R22_ANDROID_MARKER"))).writeText("PASS\n")
        }
    }

    @Test fun `persisted mock transaction recovers after committed response is lost`() = runBlocking {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:18080")
        val sessions = MemoryTokenStore(); val pending = MemoryTokenStore()
        val client = LocalMockClient(config, sessions, key, pending); val user = client.signIn("B")
        val before = client.wallet().coinBalance.toLong(); val transaction = UUID.randomUUID().toString(); val attempt = UUID.randomUUID().toString()
        val token = Json.parseToJsonElement(sessions.value!!).jsonObject.getValue("accessToken").jsonPrimitive.content
        val item = kotlinx.serialization.json.buildJsonArray { add(kotlinx.serialization.json.buildJsonObject {
            put("appId", kotlinx.serialization.json.JsonPrimitive(config.appId)); put("backendBaseUrl", kotlinx.serialization.json.JsonPrimitive(config.backendBaseUrl!!))
            put("userId", kotlinx.serialization.json.JsonPrimitive(user.userId)); put("productId", kotlinx.serialization.json.JsonPrimitive("coins_100"))
            put("transactionId", kotlinx.serialization.json.JsonPrimitive(transaction)); put("attemptId", kotlinx.serialization.json.JsonPrimitive(attempt))
        }) }
        pending.save(item.toString())
        val body = kotlinx.serialization.json.buildJsonObject {
            put("productId", kotlinx.serialization.json.JsonPrimitive("coins_100")); put("quantity", kotlinx.serialization.json.JsonPrimitive(1))
            put("proof", kotlinx.serialization.json.JsonPrimitive("mock:${user.userId}:coins_100:$transaction"))
        }.toString()
        BackendClient(config).request("/v1/purchases/verify", "POST", body, accessToken = token, idempotencyKey = attempt)
        val restarted = LocalMockClient(config, sessions, key, pending); assertNotNull(restarted.restore())
        assertEquals(LocalRecoveryCounts(1, 1, 0, 0), restarted.recoverPending()); assertNull(pending.load())
        assertEquals(before + 100, restarted.wallet().coinBalance.toLong()); restarted.signOut()
    }

    @Test fun `mock push registration unregister and logout remove token`() = runBlocking {
        val key = requireNotNull(System.getenv("GAMEBRIDGE_DEV_AUTH_KEY"))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:18080")
        val client = LocalMockClient(config, MemoryTokenStore(), key); client.signIn("B")
        val id = UUID.randomUUID()
        val first = client.registerMockPush(id); assertTrue(first.tokenFingerprint.matches(Regex("[0-9a-f]{12}")))
        assertEquals("1", sql("SELECT count(*) FROM device_tokens WHERE installation_id='$id' AND environment='local-mock';"))
        client.unregisterMockPush(id)
        assertEquals("0", sql("SELECT count(*) FROM device_tokens WHERE installation_id='$id' AND environment='local-mock';"))
        client.registerMockPush(id); client.signOut()
        assertEquals("0", sql("SELECT count(*) FROM device_tokens WHERE installation_id='$id' AND environment='local-mock';"))
    }

}
