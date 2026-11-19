package com.gamebridge.testing

import com.gamebridge.*
import kotlinx.coroutines.runBlocking
import java.util.UUID
import kotlin.test.*

class OfflineFakeTest {
    @Test fun `fake scenario and idempotent wallet are isolated`() = runBlocking {
        val fake = OfflineFake()
        assertEquals("UNSUPPORTED_PROVIDER", assertFailsWith<SdkFailure> { fake.initialize(GameBridgeConfig("demo", ProviderMode.PLATFORM_SANDBOX, "https://example.com")) }.code)
        fake.initialize(GameBridgeConfig("demo", ProviderMode.EDITOR_OFFLINE, null))
        fake.signIn(); assertEquals(2, fake.products().size)
        val id = UUID.fromString("e576c264-01d7-44a5-a264-856e7c0d91c0")
        assertEquals(0, fake.purchase("coins_100", id, FakeScenario.PENDING).wallet.coinBalance)
        assertEquals(0, fake.purchase("coins_100", id, FakeScenario.CANCELED).wallet.coinBalance)
        assertTrue(fake.purchase("coins_100", id, FakeScenario.SUCCESS).granted)
        assertFalse(fake.purchase("coins_100", id, FakeScenario.SUCCESS).granted)
        assertEquals(100, fake.wallet().coinBalance)
        assertEquals("IDEMPOTENCY_CONFLICT", assertFailsWith<SdkFailure> { fake.purchase("premium_unlock", id, FakeScenario.SUCCESS) }.code)
        assertEquals("NETWORK_UNAVAILABLE", assertFailsWith<SdkFailure> { fake.purchase("coins_100", UUID.randomUUID(), FakeScenario.NETWORK_FAILURE) }.code)
        assertTrue(fake.requestPushPermission()); assertEquals("mock-fingerprint", fake.registerPush())
        fake.receivePush("message-1", "store"); fake.receivePush("message-1", "store")
        assertEquals(listOf(FakePushEvent("message-1", "store")), fake.drainPushEvents())
        assertEquals("INVALID_ARGUMENT", assertFailsWith<SdkFailure> { fake.receivePush("message-2", "https://example.com") }.code)
        assertEquals("INVALID_ARGUMENT", assertFailsWith<SdkFailure> { fake.receivePush("  ", "store") }.code)
        repeat(200) { fake.receivePush("next-$it", "home") }
        fake.receivePush("message-1", "store")
        assertEquals(201, fake.drainPushEvents().size)
        fake.shutdown()
        fake.initialize(GameBridgeConfig("demo", ProviderMode.EDITOR_OFFLINE, null)); fake.signIn(); fake.registerPush()
        fake.receivePush("message-1", "store")
        assertEquals(1, fake.drainPushEvents().size)
        fake.shutdown()
    }
}
