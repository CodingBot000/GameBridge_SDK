package com.gamebridge

import kotlinx.coroutines.runBlocking
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
        val restored = LocalMockClient(config, storage, key)
        assertEquals(user.userId, restored.restore()?.userId)
        assertEquals(before + 100, restored.wallet().coinBalance.toLong())
        restored.signOut(); assertNull(storage.load())
    }
}
