package com.gamebridge.android.auth

import android.app.Activity
import com.android.billingclient.api.Purchase
import com.gamebridge.android.purchase.BoundPlayAccount
import com.gamebridge.android.purchase.GoogleHttpProofSink
import com.gamebridge.android.purchase.RawPlayPurchase
import java.security.MessageDigest
import java.util.UUID
import com.gamebridge.GameBridgeConfig
import com.gamebridge.BackendResponse
import com.gamebridge.LocalMockClient
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
    var expired = false
    var refreshes = 0
    var failRefresh = false
    var failRevoke = false
    override suspend fun challenge(appId: String) = AuthChallenge("dc9a46f4-8e20-4880-bcbb-ac45033157ca", challengeNonce, "2030-01-01T00:00:00Z")
    override suspend fun exchange(challengeId: String, credential: GoogleIdToken): NativeSession {
        assertEquals("test-id-token", credential.value); exchanges++
        return NativeSession("test-access", "test-refresh", "2030-01-01T00:00:00Z", "d2719c4e-d533-47ee-9efd-838791ea79c8")
    }
    override suspend fun profile(session: NativeSession): UserProfile {
        if (expired && session.accessToken == "test-access") throw SdkFailure("SESSION_EXPIRED")
        return UserProfile(profileUser, null, "GOOGLE")
    }
    override suspend fun refresh(session: NativeSession): NativeSession {
        refreshes++
        if (failRefresh) throw SdkFailure("TIMEOUT")
        return NativeSession("test-access-new", "test-refresh-new", "2030-01-01T00:00:00Z", session.userId)
    }
    override suspend fun revoke(session: NativeSession) { if (failRevoke) throw SdkFailure("NETWORK_UNAVAILABLE") }
}
class GoogleAuthProviderTest {
    private fun config(clientId: String? = "test.apps.googleusercontent.com") = GameBridgeConfig("demo", ProviderMode.PLATFORM_SANDBOX, "https://example.com", clientId)
    @Test fun `server nonce is passed to gateway and session remains native`() = runBlocking {
        val store = MemoryStore(); val gateway = StubGateway(); val backend = StubBackend()
        val user = GoogleAuthProvider(config(), store, gateway, backend).signIn()
        assertEquals("server-nonce", gateway.nonce); assertEquals("GOOGLE", user.provider)
        assertNotNull(store.stored); assertFalse(user.toString().contains("test-id-token"))
        val saved = store.stored
        val mock = LocalMockClient(GameBridgeConfig("demo", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:1"), store, "x".repeat(32))
        assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { mock.restore() }.code)
        assertEquals(saved, store.stored)
        assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { mock.signOut() }.code)
        assertEquals(saved, store.stored)
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
    @Test fun `google proof sink sends only to injected backend and requires granted result`() = runBlocking {
        val provider = GoogleAuthProvider(config(), MemoryStore(), StubGateway(), StubBackend())
        val user = provider.signIn(); val binding = UUID.randomUUID().toString(); val purchase = UUID.randomUUID()
        val token = "synthetic-proof"; val hash = MessageDigest.getInstance("SHA-256").digest(token.toByteArray()).joinToString("") { "%02x".format(it) }
        var status = "GRANTED"
        val sink = GoogleHttpProofSink(provider) { body, access, attempt ->
            assertTrue(body.contains(token)); assertEquals("test-access", access); assertNotNull(UUID.fromString(attempt))
            """{"userId":"${user.userId}","accountId":"$binding","productId":"coins_100","serverPurchaseId":"$purchase","fulfillmentStatus":"$status","proofFingerprint":"$hash"}"""
        }
        val account = BoundPlayAccount(UUID.fromString(user.userId), binding)
        val proof = RawPlayPurchase("coins.store", token, binding, 1, Purchase.PurchaseState.PURCHASED)
        val result = sink.verify(account, "coins_100", proof)
        assertEquals(purchase, result.serverPurchaseId); assertFalse(result.toString().contains(token))
        status = "PENDING"
        assertEquals("BRIDGE_PROTOCOL_MISMATCH", assertFailsWith<SdkFailure> { sink.verify(account, "coins_100", proof) }.code)
    }
    @Test fun `authenticated purchase request completes before logout clears session`() = runBlocking {
        val provider = GoogleAuthProvider(config(), MemoryStore(), StubGateway(), StubBackend())
        provider.signIn()
        val entered = CompletableDeferred<Unit>(); val release = CompletableDeferred<Unit>()
        val request = async {
            provider.withAuthenticatedSession { session ->
                entered.complete(Unit); release.await(); session.userId
            }
        }
        entered.await()
        val logout = async { provider.signOut() }
        kotlinx.coroutines.yield()
        assertFalse(logout.isCompleted)
        release.complete(Unit)
        assertEquals("d2719c4e-d533-47ee-9efd-838791ea79c8", request.await())
        logout.await()
        assertNull(provider.withAuthenticatedSession { it.userId })
    }
    @Test fun `concurrent restores rotate once and offline logout clears local session`() = runBlocking {
        val gateway = StubGateway(); val backend = StubBackend(); val store = MemoryStore()
        val provider = GoogleAuthProvider(config(), store, gateway, backend)
        provider.signIn(); backend.expired = true
        val restores = (1..8).map { async { provider.restore() } }.map { it.await() }
        assertEquals(8, restores.size); assertEquals(1, backend.refreshes)
        backend.failRevoke = true
        val logout = assertFailsWith<SdkFailure> { provider.signOut() }
        assertEquals("NETWORK_UNAVAILABLE", logout.code); assertEquals("REVOCATION_UNCONFIRMED", logout.nativeCode)
        assertNull(store.stored)
    }
    @Test fun `lost refresh response never reuses old google refresh`() = runBlocking {
        val gateway = StubGateway(); val backend = StubBackend(); val store = MemoryStore()
        val provider = GoogleAuthProvider(config(), store, gateway, backend)
        provider.signIn(); backend.expired = true; backend.failRefresh = true
        assertEquals("TIMEOUT", assertFailsWith<SdkFailure> { provider.restore() }.code)
        assertEquals("{\"state\":\"refresh_pending\"}", store.stored)
        assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { provider.restore() }.code)
        assertEquals(1, backend.refreshes)
        val logout = assertFailsWith<SdkFailure> { provider.signOut() }
        assertEquals("REVOCATION_UNCONFIRMED", logout.nativeCode); assertNull(store.stored)
    }
    @Test fun `http logout falls back to refresh when access expired`() = runBlocking {
        var calls = 0
        val backend = HttpGoogleBackend { path, method, body, access ->
            assertEquals("/v1/auth/logout", path); assertEquals("POST", method); calls++
            if (access != null) throw SdkFailure("SESSION_EXPIRED")
            assertTrue(body.orEmpty().contains("test-refresh")); BackendResponse(null, "{}")
        }
        backend.revoke(NativeSession("test-access", "test-refresh", "2030-01-01T00:00:00Z", "d2719c4e-d533-47ee-9efd-838791ea79c8"))
        assertEquals(2, calls)
    }
    @Test fun `concurrent ui request is busy`() = runBlocking {
        val gateway = StubGateway(); gateway.release = CompletableDeferred()
        val provider = GoogleAuthProvider(config(), MemoryStore(), gateway, StubBackend())
        val first = async { provider.signIn() }; gateway.entered.await()
        assertEquals("BUSY", assertFailsWith<SdkFailure> { provider.signIn() }.code)
        gateway.release!!.complete(Unit); first.await(); Unit
    }
}
