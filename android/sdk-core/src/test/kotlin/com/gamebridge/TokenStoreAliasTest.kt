package com.gamebridge

import kotlin.test.Test
import kotlin.test.assertFailsWith

class TokenStoreAliasTest {
    private class AliasStore : TokenStore, StorageIdentifiedTokenStore {
        override val storageIdentity = "synthetic-shared-slot"
        override fun load(): String? = null
        override fun save(value: String) {}
        override fun clear() {}
    }
    @Test fun `distinct objects that share a storage identity are rejected`() {
        val config = GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:8080")
        assertFailsWith<SdkFailure> { LocalMockClient(config, AliasStore(), "x".repeat(32), AliasStore()) }
    }
}
