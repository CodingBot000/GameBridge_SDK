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
import kotlinx.coroutines.sync.withLock
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
@Serializable internal class StoredGoogleSession(val appId: String, val providerMode: String, val backendBaseUrl: String, val provider: String, val session: NativeSession) {
    override fun toString() = "StoredGoogleSession([redacted])"
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
    suspend fun refresh(session: NativeSession): NativeSession
    suspend fun revoke(session: NativeSession)
}

/** Real Google credential path; raw tokens are sent only to Backend and encrypted Native storage. */
class GoogleAuthProvider internal constructor(
    private val config: GameBridgeConfig,
    private val store: TokenStore,
    private val gateway: GoogleCredentialGateway,
    private val backend: GoogleAuthBackend,
) {
    internal val uiGate = Mutex()
    private val sessionLock = Mutex()
    private val storageJson = Json { ignoreUnknownKeys = true }
    companion object {
        @JvmStatic fun create(context: Context, config: GameBridgeConfig, store: TokenStore): GoogleAuthProvider {
            if (config.mode != ProviderMode.PLATFORM_SANDBOX) throw SdkFailure("UNSUPPORTED_PROVIDER")
            config.validate()
            return GoogleAuthProvider(config, store, AndroidGoogleGateway(context.applicationContext), HttpGoogleBackend(config))
        }
    }
    internal fun usesConfiguration(candidate: GameBridgeConfig): Boolean = config == candidate
    fun attachHost(activity: Activity) = gateway.attach(activity)
    fun detachHost() = gateway.detach()
    suspend fun signIn(): UserProfile {
        if (config.mode != ProviderMode.PLATFORM_SANDBOX) throw SdkFailure("UNSUPPORTED_PROVIDER")
        val clientId = config.googleServerClientId?.takeIf { it.isNotBlank() } ?: throw SdkFailure("CONFIG_REQUIRED", "googleServerClientId")
        if (!uiGate.tryLock()) throw SdkFailure("BUSY")
        try { return sessionLock.withLock {
            val challenge = backend.challenge(config.appId)
            if (runCatching { UUID.fromString(challenge.challengeId).toString() == challenge.challengeId }.getOrDefault(false).not() ||
                challenge.nonce.isBlank() || runCatching { java.time.Instant.parse(challenge.expiresAt) }.isFailure) throw SdkFailure("AUTH_FAILED")
            val credential = gateway.get(clientId, challenge.nonce)
            val session = backend.exchange(challenge.challengeId, credential)
            validate(session)
            val profile = backend.profile(session)
            if (profile.userId != session.userId || profile.provider != "GOOGLE") throw SdkFailure("AUTH_FAILED")
            val saved = StoredGoogleSession(config.appId, config.mode.name, config.backendBaseUrl!!, "GOOGLE", session)
            store.save(storageJson.encodeToString(saved))
            profile
        } } catch (_: CancellationException) { throw SdkFailure("CANCELED") }
        finally { uiGate.unlock() }
    }
    suspend fun restore(): UserProfile? = try { sessionLock.withLock {
        val saved = loadBound() ?: return@withLock null
        var session = saved.session
        val profile = try { backend.profile(session) } catch (failure: SdkFailure) {
            if (failure.code != "SESSION_EXPIRED") throw failure
            // Keep a durable tombstone before rotation so an ambiguous response is never replayed.
            store.save("{\"state\":\"refresh_pending\"}")
            val refreshed = backend.refresh(session)
            validate(refreshed)
            if (refreshed.userId != session.userId) throw SdkFailure("AUTH_FAILED")
            session = refreshed
            store.save(storageJson.encodeToString(StoredGoogleSession(config.appId, config.mode.name, config.backendBaseUrl!!, "GOOGLE", session)))
            backend.profile(session)
        }
        if (profile.userId != session.userId || profile.provider != "GOOGLE") { store.clear(); throw SdkFailure("AUTH_FAILED") }
        profile
    } } catch (_: CancellationException) { throw SdkFailure("CANCELED") }
    internal suspend fun <T> withAuthenticatedSession(block: suspend (NativeSession) -> T): T? {
        val profile = restore() ?: return null
        return sessionLock.withLock {
            val session = loadBound()?.session ?: return@withLock null
            if (session.userId != profile.userId) throw SdkFailure("CANCELED")
            try { block(session) } catch (failure: SdkFailure) {
                if (failure.code != "SESSION_EXPIRED") throw failure
                // A 401 can arrive after the preflight profile check. Keep the rotation tombstone
                // durable and retry only once, while the session lock prevents account changes.
                store.save("{\"state\":\"refresh_pending\"}")
                val refreshed = backend.refresh(session)
                validate(refreshed)
                if (refreshed.userId != session.userId) throw SdkFailure("AUTH_FAILED")
                val verifiedProfile = backend.profile(refreshed)
                if (verifiedProfile.userId != refreshed.userId || verifiedProfile.provider != "GOOGLE") throw SdkFailure("AUTH_FAILED")
                store.save(storageJson.encodeToString(StoredGoogleSession(config.appId, config.mode.name, config.backendBaseUrl!!, "GOOGLE", refreshed)))
                block(refreshed)
            }
        }
    }
    suspend fun signOut() = sessionLock.withLock {
        if (store.load() == "{\"state\":\"refresh_pending\"}") { store.clear(); throw SdkFailure("SESSION_EXPIRED", "REVOCATION_UNCONFIRMED") }
        val saved = loadBound()
        store.clear()
        if (saved != null) try { backend.revoke(saved.session) }
        catch (failure: SdkFailure) { throw SdkFailure(failure.code, "REVOCATION_UNCONFIRMED", failure.retryable) }
        catch (_: CancellationException) { throw SdkFailure("CANCELED", "REVOCATION_UNCONFIRMED") }
        catch (_: Exception) { throw SdkFailure("INTERNAL_ERROR", "REVOCATION_UNCONFIRMED") }
    }
    private fun loadBound(): StoredGoogleSession? {
        val raw = store.load() ?: return null
        val saved = try { storageJson.decodeFromString<StoredGoogleSession>(raw) } catch (_: Exception) { throw SdkFailure("SESSION_EXPIRED") }
        if (saved.appId != config.appId || saved.providerMode != config.mode.name || saved.backendBaseUrl != config.backendBaseUrl || saved.provider != "GOOGLE") throw SdkFailure("SESSION_EXPIRED")
        validate(saved.session)
        return saved
    }
    private fun validate(session: NativeSession) {
        val validUser = runCatching { UUID.fromString(session.userId).toString() == session.userId }.getOrDefault(false)
        val validExpiry = runCatching { java.time.Instant.parse(session.expiresAt) }.isSuccess
        if (!validUser || !validExpiry || session.accessToken.isBlank() || session.refreshToken.isBlank()) throw SdkFailure("AUTH_FAILED")
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

private fun googleTransport(config: GameBridgeConfig): suspend (String, String, String?, String?) -> com.gamebridge.BackendResponse {
    val client = BackendClient(config)
    return { path, method, body, token -> client.request(path, method, body, token) }
}
internal class HttpGoogleBackend(private val request: suspend (String, String, String?, String?) -> com.gamebridge.BackendResponse) : GoogleAuthBackend {
    constructor(config: GameBridgeConfig) : this(googleTransport(config))
    private val json = Json { ignoreUnknownKeys = true }
    override suspend fun challenge(appId: String): AuthChallenge = parse(request("/v1/auth/challenges", "POST", buildJsonObject { put("provider", "GOOGLE"); put("appId", appId) }.toString(), null).json)
    override suspend fun exchange(challengeId: String, credential: GoogleIdToken): NativeSession = parse(request("/v1/auth/exchange", "POST", buildJsonObject { put("challengeId", challengeId); put("provider", "GOOGLE"); put("idToken", credential.value) }.toString(), null).json)
    override suspend fun refresh(session: NativeSession): NativeSession = parse(request("/v1/auth/refresh", "POST", buildJsonObject { put("refreshToken", session.refreshToken) }.toString(), null).json)
    override suspend fun revoke(session: NativeSession) {
        try { request("/v1/auth/logout", "POST", null, session.accessToken) }
        catch (failure: SdkFailure) {
            if (failure.code != "SESSION_EXPIRED") throw failure
            request("/v1/auth/logout", "POST", buildJsonObject { put("refreshToken", session.refreshToken) }.toString(), null)
        }
    }
    override suspend fun profile(session: NativeSession): UserProfile {
        @Serializable data class Me(val userId: String, val displayName: String? = null)
        val me: Me = parse(request("/v1/me", "GET", null, session.accessToken).json)
        return UserProfile(me.userId, me.displayName, "GOOGLE")
    }
    private inline fun <reified T> parse(value: String): T = try { json.decodeFromString(value) } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
}
