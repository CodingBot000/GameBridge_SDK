package com.gamebridge.purchase

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.auth.oauth2.ServiceAccountCredentials
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.web.server.ResponseStatusException
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.ConcurrentHashMap

/** Reads an explicitly configured service account only when an app uses the real provider. */
internal class ConfiguredGoogleVerifierRegistry(private val raw: String, private val mapper: ObjectMapper) : GoogleVerifierRegistry {
    private val cache = ConcurrentHashMap<Pair<String, StoreEnvironment>, GooglePurchaseVerifier>()
    override fun verifier(appId: String, environment: StoreEnvironment): GooglePurchaseVerifier = cache.computeIfAbsent(appId to environment) {
        try {
            require(raw.isNotBlank())
            val node = mapper.readTree(raw).get(appId) ?: error("missing app")
            val packageName = node.get("packageName")?.asText()?.takeIf { it.isNotBlank() } ?: error("package")
            val products = node.get("productIds")?.takeIf { it.isArray }?.map { value ->
                require(value.isTextual && value.asText().isNotBlank()); value.asText()
            }?.toSet()?.takeIf { it.isNotEmpty() } ?: error("products")
            val credentialPath = node.get("credentialPath")?.asText()?.takeIf { it.isNotBlank() } ?: error("credential")
            val credentials = Files.newInputStream(Path.of(credentialPath)).use { ServiceAccountCredentials.fromStream(it) }
            GooglePurchaseVerifier.withCredentials(packageName, products, environment == StoreEnvironment.SANDBOX, credentials)
        } catch (_: Exception) { throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED") }
    }
}
@Configuration
@Profile("sandbox", "production")
internal class GoogleVerifierConfiguration {
    @Bean fun googleVerifierRegistry(@Value("\${GAMEBRIDGE_GOOGLE_PURCHASE_CONFIG_JSON:}") config: String, mapper: ObjectMapper): GoogleVerifierRegistry =
        ConfiguredGoogleVerifierRegistry(config, mapper)
    @Bean fun googlePurchasePipeline(db: JdbcTemplate, registry: GoogleVerifierRegistry, grants: GoogleGrantService) = GooglePurchasePipeline(db, registry, grants)
}
