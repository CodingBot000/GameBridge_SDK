package com.gamebridge.sample

import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.gamebridge.android.KeystoreTokenStore
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
}
