package com.gamebridge.android.auth

import com.gamebridge.GameBridgeConfig
import com.gamebridge.ProviderMode
import com.gamebridge.SdkFailure
import kotlin.test.*

class StoredGoogleSessionCodecTest {
    private val config = GameBridgeConfig("demo", ProviderMode.PLATFORM_SANDBOX, "https://example.com", googleServerClientId = "client")
    private val codec = StoredGoogleSessionCodec(config)
    private val session = NativeSession("fixture-access", "fixture-refresh", "2030-01-01T00:00:00Z", "d2719c4e-d533-47ee-9efd-838791ea79c8")
    @Test fun `storage bytes preserve the existing field order and unknown field tolerance`() {
        val expected = """{"appId":"demo","providerMode":"PLATFORM_SANDBOX","backendBaseUrl":"https://example.com","provider":"GOOGLE","session":{"accessToken":"fixture-access","refreshToken":"fixture-refresh","expiresAt":"2030-01-01T00:00:00Z","userId":"d2719c4e-d533-47ee-9efd-838791ea79c8"}}"""
        assertEquals(expected, codec.encode(session))
        assertEquals(session.userId, codec.decodeBound(expected.dropLast(1) + ",\"futureField\":true}").session.userId)
    }
    @Test fun `binding failure keeps precedence over malformed session validation`() {
        val raw = codec.encode(session).replace("\"appId\":\"demo\"", "\"appId\":\"other\"").replace("fixture-access", "")
        assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { codec.decodeBound(raw) }.code)
        assertEquals("SESSION_EXPIRED", assertFailsWith<SdkFailure> { codec.decodeBound("{\"state\":\"refresh_pending\"}") }.code)
    }
}
