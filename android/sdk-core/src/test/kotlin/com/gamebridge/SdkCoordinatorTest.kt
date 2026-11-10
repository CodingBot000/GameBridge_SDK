package com.gamebridge

import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger
import kotlin.test.*

class SdkCoordinatorTest {
    @Test fun `initialization joins same config and rejects different config`() = runBlocking {
        val starts = AtomicInteger(); val entered = CompletableDeferred<Unit>(); val finish = CompletableDeferred<Unit>()
        val provider = object : SdkProvider {
            override suspend fun initialize(config: GameBridgeConfig): InitSnapshot { starts.incrementAndGet(); entered.complete(Unit); finish.await(); return InitSnapshot(emptyMap()) }
            override suspend fun shutdown() {}
        }
        val sdk = SdkCoordinator(provider); val config = GameBridgeConfig("demo", ProviderMode.EDITOR_OFFLINE, null)
        assertEquals("NOT_INITIALIZED", assertFailsWith<SdkFailure> { sdk.requireReady() }.code)
        val first = async { sdk.initialize(config) }; entered.await()
        val second = async { sdk.initialize(config) }
        assertEquals("ALREADY_INITIALIZED_DIFFERENT_CONFIG", assertFailsWith<SdkFailure> { sdk.initialize(config.copy(appId = "other")) }.code)
        finish.complete(Unit); first.await(); second.await()
        assertEquals(1, starts.get()); assertEquals(SdkState.READY, sdk.status())
        sdk.shutdown(); sdk.shutdown(); assertEquals(SdkState.SHUTDOWN, sdk.status())
        sdk.initialize(config); assertEquals(2, starts.get()); sdk.shutdown()
    }
    @Test fun `shutdown cancels an unfinished initialization`() = runBlocking {
        val entered = CompletableDeferred<Unit>()
        val sdk = SdkCoordinator(object : SdkProvider {
            override suspend fun initialize(config: GameBridgeConfig): InitSnapshot { entered.complete(Unit); awaitCancellation() }
            override suspend fun shutdown() {}
        })
        val init = async { runCatching { sdk.initialize(GameBridgeConfig("demo", ProviderMode.EDITOR_OFFLINE, null)) } }
        entered.await(); sdk.shutdown()
        assertTrue(init.await().isFailure)
        assertEquals(SdkState.SHUTDOWN, sdk.status())
    }
    @Test fun `interactive calls are mutually exclusive`() = runBlocking {
        val sdk = SdkCoordinator(object : SdkProvider {
            override suspend fun initialize(config: GameBridgeConfig) = InitSnapshot(emptyMap())
            override suspend fun shutdown() {}
        })
        sdk.initialize(GameBridgeConfig("demo", ProviderMode.EDITOR_OFFLINE, null))
        val entered = CompletableDeferred<Unit>(); val release = CompletableDeferred<Unit>()
        val held = async { sdk.withInteractiveUi { entered.complete(Unit); release.await() } }
        entered.await()
        assertEquals("BUSY", assertFailsWith<SdkFailure> { sdk.withInteractiveUi { } }.code)
        release.complete(Unit); held.await(); sdk.shutdown()
    }
}
