package com.gamebridge.android.auth

import com.gamebridge.GameBridgeConfig
import com.gamebridge.SdkFailure
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.util.UUID

@Serializable internal class StoredGoogleSession(val appId: String, val providerMode: String, val backendBaseUrl: String, val provider: String, val session: NativeSession) {
    override fun toString() = "StoredGoogleSession([redacted])"
}

/** Storage bytes and configuration binding only; network/rotation/save ordering stays in the provider. */
internal class StoredGoogleSessionCodec(private val config: GameBridgeConfig) {
    private val json = Json { ignoreUnknownKeys = true }
    fun encode(session: NativeSession): String = json.encodeToString(
        StoredGoogleSession(config.appId, config.mode.name, config.backendBaseUrl!!, "GOOGLE", session))
    fun decodeBound(raw: String): StoredGoogleSession {
        val saved = try { json.decodeFromString<StoredGoogleSession>(raw) } catch (_: Exception) { throw SdkFailure("SESSION_EXPIRED") }
        if (saved.appId != config.appId || saved.providerMode != config.mode.name || saved.backendBaseUrl != config.backendBaseUrl || saved.provider != "GOOGLE") throw SdkFailure("SESSION_EXPIRED")
        validate(saved.session)
        return saved
    }
    fun validate(session: NativeSession) {
        val validUser = runCatching { UUID.fromString(session.userId).toString() == session.userId }.getOrDefault(false)
        val validExpiry = runCatching { java.time.Instant.parse(session.expiresAt) }.isSuccess
        if (!validUser || !validExpiry || session.accessToken.isBlank() || session.refreshToken.isBlank()) throw SdkFailure("AUTH_FAILED")
    }
}
