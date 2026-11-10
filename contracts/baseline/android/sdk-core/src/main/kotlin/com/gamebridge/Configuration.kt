package com.gamebridge

import java.net.URI

enum class ProviderMode { EDITOR_OFFLINE, LOCAL_MOCK, XCODE_STOREKIT, PLATFORM_SANDBOX }

/** A configuration error contains key names only, never supplied values. */
class ConfigurationException(val missingKeys: List<String>) : IllegalArgumentException(
    "CONFIG_REQUIRED: " + missingKeys.joinToString(", ")
)

data class GameBridgeConfig(
    val appId: String,
    val mode: ProviderMode,
    val backendBaseUrl: String?,
    val googleServerClientId: String? = null,
    val requestTimeoutMs: Long = 30_000,
) {
    fun validate() {
        val missing = mutableListOf<String>()
        if (appId.isBlank()) missing += "appId"
        if (requestTimeoutMs <= 0) missing += "requestTimeoutMs"
        if (mode != ProviderMode.EDITOR_OFFLINE) {
            val uri = runCatching { URI(backendBaseUrl ?: "") }.getOrNull()
            val allowedScheme = uri?.scheme == "https" ||
                (mode == ProviderMode.LOCAL_MOCK && uri?.scheme == "http")
            if (uri?.host.isNullOrBlank() || !allowedScheme || uri?.userInfo != null) missing += "backendBaseUrl"
        }
        if (missing.isNotEmpty()) throw ConfigurationException(missing)
    }
}
