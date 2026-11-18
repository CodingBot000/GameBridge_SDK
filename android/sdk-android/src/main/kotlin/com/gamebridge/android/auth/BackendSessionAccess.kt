package com.gamebridge.android.auth

import android.app.Activity
import com.gamebridge.GameBridgeConfig
import kotlinx.coroutines.sync.Mutex

internal interface BackendSessionAccess {
    val uiGate: Mutex
    fun usesConfiguration(config: GameBridgeConfig): Boolean
    fun attachHost(activity: Activity)
    fun detachHost()
    suspend fun <T> withAuthenticatedSession(block: suspend (NativeSession) -> T): T?
}
internal class GoogleSessionAccess(private val provider: GoogleAuthProvider): BackendSessionAccess {
    override val uiGate get()=provider.uiGate
    override fun usesConfiguration(config:GameBridgeConfig)=provider.usesConfiguration(config)
    override fun attachHost(activity:Activity)=provider.attachHost(activity)
    override fun detachHost()=provider.detachHost()
    override suspend fun <T> withAuthenticatedSession(block:suspend(NativeSession)->T)=provider.withAuthenticatedSession(block)
}
