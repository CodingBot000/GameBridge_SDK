package com.gamebridge.android.auth

import android.app.Activity
import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.exceptions.GetCredentialCancellationException
import androidx.credentials.exceptions.GetCredentialException
import androidx.credentials.exceptions.GetCredentialProviderConfigurationException
import androidx.credentials.exceptions.GetCredentialUnsupportedException
import androidx.credentials.exceptions.NoCredentialException
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import com.gamebridge.BackendClient
import com.gamebridge.GameBridgeConfig
import com.gamebridge.ProviderMode
import com.gamebridge.SdkFailure
import com.gamebridge.TokenStore
import com.gamebridge.UserProfile
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import java.lang.ref.WeakReference
import java.util.UUID

internal class GoogleIdToken(val value: String) { override fun toString() = "GoogleIdToken([redacted])" }
@Serializable internal class AuthChallenge(val challengeId: String, val nonce: String, val expiresAt: String) {
    override fun toString() = "AuthChallenge([redacted])"
}
@Serializable internal class NativeSession(val accessToken: String, val refreshToken: String, val expiresAt: String, val userId: String) {
    override fun toString() = "NativeSession([redacted])"
}
internal interface GoogleCredentialGateway {
    fun attach(activity: Activity)
    fun detach()
    suspend fun get(clientId: String, nonce: String): GoogleIdToken
}
internal interface GoogleAuthBackend {
    suspend fun challenge(appId: String): AuthChallenge
    suspend fun exchange(challengeId: String, credential: GoogleIdToken): NativeSession
    suspend fun profile(session: NativeSession): UserProfile
}

/** Real Google credential path; raw tokens are sent only to Backend and encrypted Native storage. */
class GoogleAuthProvider internal constructor(
    private val config: GameBridgeConfig,
    private val store: TokenStore,
    private val gateway: GoogleCredentialGateway,
    private val backend: GoogleAuthBackend,
) {
    private val uiGate = Mutex()
    companion object {
        @JvmStatic fun create(context: Context, config: GameBridgeConfig, store: TokenStore): GoogleAuthProvider {
            if (config.mode != ProviderMode.PLATFORM_SANDBOX) throw SdkFailure("UNSUPPORTED_PROVIDER")
            config.validate()
            return GoogleAuthProvider(config, store, AndroidGoogleGateway(context.applicationContext), HttpGoogleBackend(config))
        }
    }
    fun attachHost(activity: Activity) = gateway.attach(activity)
    fun detachHost() = gateway.detach()
    suspend fun signIn(): UserProfile {
        if (config.mode != ProviderMode.PLATFORM_SANDBOX) throw SdkFailure("UNSUPPORTED_PROVIDER")
        val clientId = config.googleServerClientId?.takeIf { it.isNotBlank() } ?: throw SdkFailure("CONFIG_REQUIRED")
        if (!uiGate.tryLock()) throw SdkFailure("BUSY")
        try {
            val challenge = backend.challenge(config.appId)
            if (runCatching { UUID.fromString(challenge.challengeId).toString() == challenge.challengeId }.getOrDefault(false).not() ||
                challenge.nonce.isBlank() || runCatching { java.time.Instant.parse(challenge.expiresAt) }.isFailure) throw SdkFailure("AUTH_FAILED")
            val credential = gateway.get(clientId, challenge.nonce)
            val session = backend.exchange(challenge.challengeId, credential)
            val validUser = runCatching { UUID.fromString(session.userId).toString() == session.userId }.getOrDefault(false)
            val validExpiry = runCatching { java.time.Instant.parse(session.expiresAt) }.isSuccess
            if (!validUser || !validExpiry || session.accessToken.isBlank() || session.refreshToken.isBlank()) throw SdkFailure("AUTH_FAILED")
            val profile = backend.profile(session)
            if (profile.userId != session.userId || profile.provider != "GOOGLE") throw SdkFailure("AUTH_FAILED")
            store.save(Json.encodeToString(session))
            return profile
        } catch (_: CancellationException) { throw SdkFailure("CANCELED") }
        finally { uiGate.unlock() }
    }
}

internal class AndroidGoogleGateway(context: Context) : GoogleCredentialGateway {
    private val manager = CredentialManager.create(context)
    @Volatile private var host: WeakReference<Activity>? = null
    override fun attach(activity: Activity) { host = WeakReference(activity) }
    override fun detach() { host?.clear(); host = null }
    override suspend fun get(clientId: String, nonce: String): GoogleIdToken = withContext(Dispatchers.Main.immediate) {
        val activity = host?.get()?.takeUnless { it.isFinishing || it.isDestroyed } ?: throw SdkFailure("CONFIG_REQUIRED", "HOST_ACTIVITY")
        val option = GetGoogleIdOption.Builder().setFilterByAuthorizedAccounts(false).setAutoSelectEnabled(false)
            .setServerClientId(clientId).setNonce(nonce).build()
        val request = GetCredentialRequest.Builder().addCredentialOption(option).build()
        try {
            val credential = manager.getCredential(activity, request).credential
            if (credential !is CustomCredential || credential.type != GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL) throw SdkFailure("AUTH_FAILED")
            val token = GoogleIdTokenCredential.createFrom(credential.data).idToken
            if (token.isBlank()) throw SdkFailure("AUTH_FAILED")
            GoogleIdToken(token)
        } catch (_: GetCredentialCancellationException) { throw SdkFailure("CANCELED") }
        catch (_: NoCredentialException) { throw SdkFailure("AUTH_FAILED", "NO_CREDENTIAL") }
        catch (_: GetCredentialProviderConfigurationException) { throw SdkFailure("CONFIG_REQUIRED", "CREDENTIAL_PROVIDER") }
        catch (_: GetCredentialUnsupportedException) { throw SdkFailure("UNSUPPORTED_PLATFORM") }
        catch (_: GoogleIdTokenParsingException) { throw SdkFailure("AUTH_FAILED", "INVALID_CREDENTIAL") }
        catch (_: GetCredentialException) { throw SdkFailure("AUTH_FAILED") }
        catch (error: SdkFailure) { throw error }
        catch (_: IllegalArgumentException) { throw SdkFailure("AUTH_FAILED") }
    }
}

internal class HttpGoogleBackend(config: GameBridgeConfig) : GoogleAuthBackend {
    private val client = BackendClient(config)
    private val json = Json { ignoreUnknownKeys = true }
    override suspend fun challenge(appId: String): AuthChallenge = parse(client.request("/v1/auth/challenges", "POST", buildJsonObject { put("provider", "GOOGLE"); put("appId", appId) }.toString()).json)
    override suspend fun exchange(challengeId: String, credential: GoogleIdToken): NativeSession = parse(client.request("/v1/auth/exchange", "POST", buildJsonObject { put("challengeId", challengeId); put("provider", "GOOGLE"); put("idToken", credential.value) }.toString()).json)
    override suspend fun profile(session: NativeSession): UserProfile {
        @Serializable data class Me(val userId: String, val displayName: String? = null)
        val me: Me = parse(client.request("/v1/me", "GET", accessToken = session.accessToken).json)
        return UserProfile(me.userId, me.displayName, "GOOGLE")
    }
    private inline fun <reified T> parse(value: String): T = try { json.decodeFromString(value) } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
}
