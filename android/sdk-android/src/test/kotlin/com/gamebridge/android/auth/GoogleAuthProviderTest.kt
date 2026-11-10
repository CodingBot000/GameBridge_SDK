package com.gamebridge.android.auth

import android.app.Activity
import com.gamebridge.GameBridgeConfig
import com.gamebridge.ProviderMode
import com.gamebridge.SdkFailure
import com.gamebridge.TokenStore
import com.gamebridge.UserProfile
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import kotlin.test.*

private class MemoryStore : TokenStore {
    var stored: String? = null
    override fun load() = stored
    override fun save(value: String) { stored = value }
    override fun clear() { stored = null }
}
private class StubGateway : GoogleCredentialGateway {
    var entered = CompletableDeferred<Unit>()
    var release: CompletableDeferred<Unit>? = null
    var nonce: String? = null
    var failure: Throwable? = null
    override fun attach(activity: Activity) {}
    override fun detach() {}
    override suspend fun get(clientId: String, nonce: String): GoogleIdToken {
        this.nonce = nonce; entered.complete(Unit); release?.await(); failure?.let { throw it }; return GoogleIdToken("test-id-token")
    }
}
private class StubBackend : GoogleAuthBackend {
    var exchanges = 0
    var challengeNonce = "server-nonce"
    var profileUser = "d2719c4e-d533-47ee-9efd-838791ea79c8"
    override suspend fun challenge(appId: String) = AuthChallenge("dc9a46f4-8e20-4880-bcbb-ac45033157ca", challengeNonce, "2030-01-01T00:00:00Z")
    override suspend fun exchange(challengeId: String, credential: GoogleIdToken): NativeSession {
        assertEquals("test-id-token", credential.value); exchanges++
        return NativeSession("test-access", "test-refresh", "2030-01-01T00:00:00Z", "d2719c4e-d533-47ee-9efd-838791ea79c8")
    }
    override suspend fun profile(session: NativeSession) = UserProfile(profileUser, null, "GOOGLE")
}
class GoogleAuthProviderTest {
    private fun config(clientId: String? = "test.apps.googleusercontent.com") = GameBridgeConfig("demo", ProviderMode.PLATFORM_SANDBOX, "https://example.com", clientId)
    @Test fun `server nonce is passed to gateway and session remains native`() = runBlocking {
        val store = MemoryStore(); val gateway = StubGateway(); val backend = StubBackend()
        val user = GoogleAuthProvider(config(), store, gateway, backend).signIn()
        assertEquals("server-nonce", gateway.nonce); assertEquals("GOOGLE", user.provider)
        assertNotNull(store.stored); assertFalse(user.toString().contains("test-id-token"))
        assertFalse(GoogleIdToken("test-id-token").toString().contains("test-id-token"))
        assertFalse(NativeSession("test-access", "test-refresh", "2030-01-01T00:00:00Z", user.userId).toString().contains("test-access"))
    }
    @Test fun `missing config and mismatched user fail without saving`() = runBlocking {
        val store = MemoryStore(); val backend = StubBackend(); val gateway = StubGateway()
        assertEquals("CONFIG_REQUIRED", assertFailsWith<SdkFailure> { GoogleAuthProvider(config(null), store, gateway, backend).signIn() }.code)
        assertEquals(0, backend.exchanges)
        backend.profileUser = "8e37925d-a1a8-4118-84eb-b00668b9d469"
        assertEquals("AUTH_FAILED", assertFailsWith<SdkFailure> { GoogleAuthProvider(config(), store, gateway, backend).signIn() }.code)
        assertNull(store.stored)
        backend.challengeNonce = ""
        assertEquals("AUTH_FAILED", assertFailsWith<SdkFailure> { GoogleAuthProvider(config(), store, gateway, backend).signIn() }.code)
        assertNull(store.stored)
    }
    @Test fun `cancellation is explicit and stores no session`() = runBlocking {
        val gateway = StubGateway(); gateway.failure = kotlinx.coroutines.CancellationException()
        val store = MemoryStore()
        assertEquals("CANCELED", assertFailsWith<SdkFailure> { GoogleAuthProvider(config(), store, gateway, StubBackend()).signIn() }.code)
        assertNull(store.stored)
    }
    @Test fun `concurrent ui request is busy`() = runBlocking {
        val gateway = StubGateway(); gateway.release = CompletableDeferred()
        val provider = GoogleAuthProvider(config(), MemoryStore(), gateway, StubBackend())
        val first = async { provider.signIn() }; gateway.entered.await()
        assertEquals("BUSY", assertFailsWith<SdkFailure> { provider.signIn() }.code)
        gateway.release!!.complete(Unit); first.await(); Unit
    }
}
