package com.gamebridge

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertFailsWith

class ConfigurationTest {
    @Test fun `mock url and offline without server are valid`() {
        GameBridgeConfig("sample", ProviderMode.LOCAL_MOCK, "http://127.0.0.1:8080").validate()
        GameBridgeConfig("sample", ProviderMode.EDITOR_OFFLINE, null).validate()
    }

    @Test fun `sandbox refuses insecure url without leaking it`() {
        val error = assertFailsWith<ConfigurationException> {
            GameBridgeConfig("sample", ProviderMode.PLATFORM_SANDBOX, "http://user:secret@example.com").validate()
        }
        assertEquals(listOf("backendBaseUrl"), error.missingKeys)
        assertFalse(error.message.orEmpty().contains("secret"))
    }
}
