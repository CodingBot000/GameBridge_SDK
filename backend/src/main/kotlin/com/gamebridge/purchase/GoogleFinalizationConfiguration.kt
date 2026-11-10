package com.gamebridge.purchase

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport
import com.google.api.client.http.HttpRequestInitializer
import com.google.api.client.json.gson.GsonFactory
import com.google.api.services.androidpublisher.AndroidPublisher
import com.google.auth.http.HttpCredentialsAdapter
import com.google.auth.oauth2.ServiceAccountCredentials
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.jdbc.core.JdbcTemplate
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.ConcurrentHashMap

@Configuration
@Profile("sandbox", "production")
internal class GoogleFinalizationConfiguration {
    @Bean fun googleFinalizationExecutor(@Value("\${GAMEBRIDGE_GOOGLE_PURCHASE_CONFIG_JSON:}") raw: String,
                                         mapper: ObjectMapper, db: JdbcTemplate): GoogleFinalizationExecutor {
        data class Client(val packageName: String, val productIds: Set<String>, val finalizer: GoogleStoreFinalizer)
        val clients = ConcurrentHashMap<Pair<String, StoreEnvironment>, Client>()
        return GoogleFinalizationExecutor { claim, token ->
            val client = clients.computeIfAbsent(claim.app to claim.environment) {
                require(raw.isNotBlank())
                val node = mapper.readTree(raw).get(claim.app) ?: error("CONFIG_REQUIRED")
                val name = node.get("packageName")?.asText()?.takeIf { it.isNotBlank() } ?: error("CONFIG_REQUIRED")
                val products = node.get("productIds")?.takeIf { it.isArray }?.map { value ->
                    require(value.isTextual && value.asText().isNotBlank()); value.asText()
                }?.toSet()?.takeIf { it.isNotEmpty() } ?: error("CONFIG_REQUIRED")
                val path = node.get("credentialPath")?.asText()?.takeIf { it.isNotBlank() } ?: error("CONFIG_REQUIRED")
                val credentials = Files.newInputStream(Path.of(path)).use { ServiceAccountCredentials.fromStream(it) }
                    .createScoped(listOf("https://www.googleapis.com/auth/androidpublisher"))
                val adapter = HttpCredentialsAdapter(credentials)
                val initializer = HttpRequestInitializer { request -> adapter.initialize(request); request.connectTimeout = 30_000; request.readTimeout = 30_000 }
                val publisher = AndroidPublisher.Builder(GoogleNetHttpTransport.newTrustedTransport(), GsonFactory.getDefaultInstance(), initializer).setApplicationName("GameBridge SDK").build()
                val appId = claim.app
                val guard = DatabaseGoogleGrantCheck(db) { app -> if (app == appId) name else null }
                Client(name, products, GoogleStoreFinalizer.configured(guard, publisher))
            }
            require(claim.storeId in client.productIds)
            client.finalizer.finalize(GoogleFinalizationInput(claim.purchaseId, client.packageName, claim.storeId, claim.account, token, claim.action))
        }
    }
}
