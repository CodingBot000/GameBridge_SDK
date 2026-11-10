package com.gamebridge.purchase

import com.apple.itunes.storekit.model.Environment
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.web.server.ResponseStatusException
import java.io.ByteArrayInputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.ConcurrentHashMap

/** User-supplied production trust roots and app mapping are loaded only on first use. */
internal class ConfiguredAppleVerifierRegistry(private val raw: String, private val mapper: ObjectMapper) : AppleVerifierRegistry {
    private val cache = ConcurrentHashMap<Pair<String, StoreEnvironment>, ApplePurchaseVerifier>()
    override fun verifier(appId: String, environment: StoreEnvironment): ApplePurchaseVerifier = cache.computeIfAbsent(appId to environment) {
        try {
            require(raw.isNotBlank())
            val node = mapper.readTree(raw).get(appId) ?: error("missing app")
            val bundle = node.get("bundleId")?.asText()?.takeIf { it.isNotBlank() } ?: error("bundle")
            val products = node.get("productIds")?.takeIf { it.isArray }?.map { value ->
                require(value.isTextual && value.asText().isNotBlank()); value.asText()
            }?.toSet()?.takeIf { it.isNotEmpty() } ?: error("products")
            val certs = node.get("rootCertificatePaths")?.takeIf { it.isArray }?.map { value ->
                require(value.isTextual && value.asText().isNotBlank()); Files.readAllBytes(Path.of(value.asText()))
            }?.takeIf { it.isNotEmpty() } ?: error("roots")
            val appleId = node.get("appAppleId")?.takeUnless { it.isNull }?.let { value ->
                require(value.isIntegralNumber && value.canConvertToLong() && value.asLong() > 0); value.asLong()
            }
            val appleEnvironment = if (environment == StoreEnvironment.SANDBOX) Environment.SANDBOX else Environment.PRODUCTION
            ApplePurchaseVerifier.configured(bundle, appleId, appleEnvironment, products, certs.map { bytes -> ByteArrayInputStream(bytes) }.toSet())
        } catch (_: Exception) { throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED") }
    }
}
@Configuration
@Profile("sandbox", "production")
internal class AppleVerifierConfiguration {
    @Bean fun appleVerifierRegistry(@Value("\${GAMEBRIDGE_APPLE_PURCHASE_CONFIG_JSON:}") config: String, mapper: ObjectMapper): AppleVerifierRegistry =
        ConfiguredAppleVerifierRegistry(config, mapper)
    @Bean fun applePurchasePipeline(db: org.springframework.jdbc.core.JdbcTemplate, registry: AppleVerifierRegistry, grants: AppleGrantService) = ApplePurchasePipeline(db, registry, grants)
}
