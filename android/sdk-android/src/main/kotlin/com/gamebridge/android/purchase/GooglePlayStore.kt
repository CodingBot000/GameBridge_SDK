package com.gamebridge.android.purchase

import android.app.Activity
import android.content.Context
import com.gamebridge.BackendClient
import com.gamebridge.EntitlementSnapshot
import com.gamebridge.GameBridgeConfig
import com.gamebridge.ProviderMode
import com.gamebridge.PurchaseStatus
import com.gamebridge.SdkFailure
import com.gamebridge.StoreProduct
import com.gamebridge.android.auth.GoogleAuthProvider
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.util.UUID

/** No token, receipt or account binding is exposed in public results. */
data class GoogleStoreEvent(val productId: String, val status: PurchaseStatus, val errorCode: String?, val serverPurchaseId: UUID?)
class GooglePlayStore internal constructor(private val auth: GoogleAuthProvider, private val client: BackendClient,
                                           private val provider: GooglePlayBillingProvider) : AutoCloseable {
    companion object {
        @JvmStatic fun create(context: Context, config: GameBridgeConfig, auth: GoogleAuthProvider, productIds: Map<String, String>): GooglePlayStore {
            validateGoogleStoreConfiguration(config, auth, productIds)
            val client = BackendClient(config)
            return GooglePlayStore(auth, client, GoogleStoreRuntime.create(context, auth, client, productIds))
        }
    }
    val events: Flow<GoogleStoreEvent> = provider.events.map { event ->
        val status = try { PurchaseStatus.valueOf(event.status) } catch (_: IllegalArgumentException) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        GoogleStoreEvent(event.productId, status, event.errorCode, event.serverPurchaseId)
    }
    fun attachHost(activity: Activity) { auth.attachHost(activity); provider.attachHost(activity) }
    fun detachHost() { provider.detachHost(); auth.detachHost() }
    suspend fun products(): List<StoreProduct> = provider.products()
    suspend fun purchase(productId: String): PurchaseStatus = try { PurchaseStatus.valueOf(provider.purchase(productId)) }
        catch (_: IllegalArgumentException) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    suspend fun entitlements(): EntitlementSnapshot = auth.withAuthenticatedSession { session ->
        decodeGoogleEntitlements(client.request("/v1/entitlements", "GET", accessToken = session.accessToken).json, session.userId)
    } ?: throw SdkFailure("SESSION_EXPIRED")
    suspend fun recover() = provider.recover()
    override fun close() { provider.close() }
}

private val entitlementJson = Json { ignoreUnknownKeys = true }
internal fun decodeGoogleEntitlements(body: String, expectedUser: String): EntitlementSnapshot {
    val value = try { entitlementJson.decodeFromString<EntitlementSnapshot>(body) }
                catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    if (value.userId != expectedUser) throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
    return value
}

internal fun validateGoogleStoreConfiguration(config: GameBridgeConfig, auth: GoogleAuthProvider, productIds: Map<String, String>) {
    if (config.mode != ProviderMode.PLATFORM_SANDBOX) throw SdkFailure("UNSUPPORTED_PROVIDER")
    config.validate()
    if (!auth.usesConfiguration(config) || productIds.keys != setOf("coins_100", "premium_unlock") ||
        productIds.values.any { it.isBlank() } || productIds.values.toSet().size != 2) throw SdkFailure("CONFIG_REQUIRED")
}
