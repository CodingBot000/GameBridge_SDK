package com.gamebridge.sample

import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.gamebridge.android.KeystoreTokenStore
import com.gamebridge.BackendClient
import com.gamebridge.GameBridgeConfig
import com.gamebridge.ProviderMode
import com.gamebridge.LocalMockClient
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID

@RunWith(AndroidJUnit4::class)
class KeystoreNamespaceTest {
    @Test fun isolatedNamespacesDoNotOverwriteEachOther() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val prefix = "test_" + UUID.randomUUID().toString().replace("-", "")
        val first = KeystoreTokenStore(context, prefix + "a")
        val second = KeystoreTokenStore(context, prefix + "b")
        try {
            first.save("synthetic-a"); second.save("synthetic-b")
            assertEquals("synthetic-a", KeystoreTokenStore(context, prefix + "a").load())
            assertEquals("synthetic-b", second.load())
            first.clear(); assertNull(first.load()); assertEquals("synthetic-b", second.load())
        } finally { first.clear(); second.clear() }
    }
    @Test fun localMockSessionRestoresAndLogsOut() = runBlocking {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val namespace = "test_" + UUID.randomUUID().toString().replace("-", "")
        val store = KeystoreTokenStore(context, namespace)
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://10.0.2.2:18080")
        val key = "local-test-key-0123456789-abcdef0123456789" // Test-only local key.
        try {
            LocalMockClient(config, store, key).signIn("A")
            val restored = LocalMockClient(config, store, key)
            assertNotNull(restored.restore()); restored.signOut(); assertNull(store.load())
        } finally { store.clear() }
    }
    @Test fun probeBodylessLogoutPost() = runBlocking {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val store = KeystoreTokenStore(context, "test_" + UUID.randomUUID().toString().replace("-", ""))
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://10.0.2.2:18080")
        try {
            LocalMockClient(config, store, "local-test-key-0123456789-abcdef0123456789").signIn("A")
            val access = org.json.JSONObject(store.load()!!).getString("accessToken")
            val connection = java.net.URL("http://10.0.2.2:18080/v1/auth/logout").openConnection() as java.net.HttpURLConnection
            connection.requestMethod = "POST"; connection.setRequestProperty("Authorization", "Bearer $access")
            try { assertEquals(200, connection.responseCode) }
            catch (error: java.io.IOException) { fail("bodyless POST exception type=" + error.javaClass.simpleName) }
            finally { connection.disconnect() }
        } finally { store.clear() }
    }
    @Test fun pendingPurchaseSurvivesNewKeystoreInstancesAndDoesNotDoubleGrant() = runBlocking {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val prefix = "test_" + UUID.randomUUID().toString().replace("-", "")
        val sessions = KeystoreTokenStore(context, prefix + "s"); val pending = KeystoreTokenStore(context, prefix + "p")
        val config = GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, "http://10.0.2.2:18080")
        val key = "local-test-key-0123456789-abcdef0123456789"
        try {
            val client = LocalMockClient(config, sessions, key, pending); val user = client.signIn("B")
            val before = client.wallet().coinBalance.toLong(); val transaction = UUID.randomUUID().toString(); val attempt = UUID.randomUUID().toString()
            val access = org.json.JSONObject(sessions.load()!!).getString("accessToken")
            val item = org.json.JSONObject().put("appId", config.appId).put("backendBaseUrl", config.backendBaseUrl)
                .put("userId", user.userId).put("productId", "coins_100").put("transactionId", transaction).put("attemptId", attempt)
            pending.save(org.json.JSONArray().put(item).toString())
            val body = org.json.JSONObject().put("productId", "coins_100").put("quantity", 1)
                .put("proof", "mock:${user.userId}:coins_100:$transaction").toString()
            BackendClient(config).request("/v1/purchases/verify", "POST", body, accessToken = access, idempotencyKey = attempt)
            val restarted = LocalMockClient(config, KeystoreTokenStore(context, prefix + "s"), key, KeystoreTokenStore(context, prefix + "p"))
            assertNotNull(restarted.restore()); val counts = restarted.recoverPending()
            assertEquals(1, counts.examinedCount); assertEquals(1, counts.recoveredCount)
            assertNull(pending.load()); assertEquals(before + 100, restarted.wallet().coinBalance.toLong()); restarted.signOut()
        } finally { sessions.clear(); pending.clear() }
    }

}
