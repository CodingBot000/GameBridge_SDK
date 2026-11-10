package com.gamebridge

import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

enum class SdkState { UNINITIALIZED, INITIALIZING, READY, SHUTTING_DOWN, SHUTDOWN }
data class Capability(val supported: Boolean, val configured: Boolean, val mode: ProviderMode, val reason: String?)
data class InitSnapshot(val capabilities: Map<String, Capability>)
class SdkFailure(val code: String, val nativeCode: String? = null) : IllegalStateException(code)

interface SdkProvider {
    suspend fun initialize(config: GameBridgeConfig): InitSnapshot
    suspend fun shutdown()
}

/** Provider owns native state; concurrent equal initialization callers share one operation. */
class SdkCoordinator(private val provider: SdkProvider) {
    private val lock = Mutex()
    private val uiGate = Mutex()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var state = SdkState.UNINITIALIZED
    private var config: GameBridgeConfig? = null
    private var current: Deferred<InitSnapshot>? = null
    private var shutdownTask: Deferred<Unit>? = null

    suspend fun status(): SdkState = lock.withLock { state }
    suspend fun initialize(value: GameBridgeConfig): InitSnapshot {
        value.validate()
        val task = lock.withLock {
            if (state == SdkState.SHUTTING_DOWN) throw SdkFailure("BUSY")
            if (state == SdkState.READY || state == SdkState.INITIALIZING) {
                if (config != value) throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
                return@withLock current!!
            }
            config = value
            state = SdkState.INITIALIZING
            val created = scope.async(start = CoroutineStart.LAZY) { provider.initialize(value) }
            current = created
            created.invokeOnCompletion { cause ->
                scope.launch {
                    lock.withLock {
                        if (current === created && state == SdkState.INITIALIZING) {
                            if (cause == null) state = SdkState.READY else { state = SdkState.UNINITIALIZED; config = null; current = null }
                        }
                    }
                }
            }
            created.start()
            created
        }
        val result = try { task.await() } catch (failure: Throwable) {
            lock.withLock {
                if (current === task && state == SdkState.INITIALIZING && task.isCompleted) {
                    state = SdkState.UNINITIALIZED; config = null; current = null
                }
            }
            throw failure
        }
        lock.withLock {
            if (current !== task || (state != SdkState.INITIALIZING && state != SdkState.READY)) throw SdkFailure("NOT_INITIALIZED")
            state = SdkState.READY
        }
        return result
    }
    suspend fun requireReady() { if (status() != SdkState.READY) throw SdkFailure("NOT_INITIALIZED") }
    suspend fun <T> withInteractiveUi(block: suspend () -> T): T {
        requireReady()
        if (!uiGate.tryLock()) throw SdkFailure("BUSY")
        try { return block() } finally { uiGate.unlock() }
    }
    suspend fun shutdown() {
        val task = lock.withLock {
            if (state == SdkState.SHUTTING_DOWN) return@withLock shutdownTask!!
            if (state == SdkState.UNINITIALIZED || state == SdkState.SHUTDOWN) { state = SdkState.SHUTDOWN; return }
            state = SdkState.SHUTTING_DOWN
            val initializing = current
            scope.async(start = CoroutineStart.LAZY) {
                initializing?.cancelAndJoin()
                try { provider.shutdown() } finally {
                    lock.withLock { state = SdkState.SHUTDOWN; config = null; current = null; shutdownTask = null }
                }
            }.also { shutdownTask = it; it.start() }
        }
        task.await()
    }
}
