package com.gamebridge

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.boolean
import java.time.Instant

data class ServiceSettings(val revision: String, val maintenanceEnabled: Boolean, val message: String?, val expiresAt: Instant)
enum class ConfigurationSource { REMOTE, CACHE }
data class EffectiveServiceSettings(val settings: ServiceSettings, val source: ConfigurationSource)

/** An expired or malformed response never turns an unknown configuration into an allowed purchase. */
class ServiceConfigurationRepository(private val fetch: suspend () -> ServiceSettings, private val now: () -> Instant = Instant::now) {
    private val lock = Mutex()
    private var cached: ServiceSettings? = null
    suspend fun current(): EffectiveServiceSettings? = lock.withLock {
        val value = try { fetch() } catch (cancel: CancellationException) { throw cancel } catch (_: Exception) { null }
        if (value != null && value.revision.isNotBlank() && value.expiresAt.isAfter(now())) {
            cached = value; return@withLock EffectiveServiceSettings(value, ConfigurationSource.REMOTE)
        }
        cached?.takeIf { it.expiresAt.isAfter(now()) }?.let { EffectiveServiceSettings(it, ConfigurationSource.CACHE) }
    }
}
fun backendServiceConfiguration(client: BackendClient): ServiceConfigurationRepository = ServiceConfigurationRepository({
    val value = Json.parseToJsonElement(client.request("/v1/config", "GET").json).jsonObject
    val revision = value.getValue("revision").jsonPrimitive.content
    val maintenance = value.getValue("maintenanceEnabled").jsonPrimitive.boolean
    val expiry = Instant.parse(value.getValue("expiresAt").jsonPrimitive.content)
    val message = value["message"]?.takeUnless { it is kotlinx.serialization.json.JsonNull }?.jsonPrimitive?.content
    ServiceSettings(revision, maintenance, message, expiry)
})
