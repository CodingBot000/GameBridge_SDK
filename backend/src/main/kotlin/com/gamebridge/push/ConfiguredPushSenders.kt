package com.gamebridge.push

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
import com.google.firebase.messaging.FirebaseMessaging
import jakarta.annotation.PreDestroy
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component
import org.springframework.web.server.ResponseStatusException
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.security.KeyFactory
import java.security.interfaces.ECPrivateKey
import java.security.spec.PKCS8EncodedKeySpec
import java.util.Base64
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

/** App-specific providers and credentials are loaded only when explicitly used. */
@Component
@Profile("sandbox", "production")
internal class ConfiguredPushSenders(
    @Value("\${GAMEBRIDGE_FCM_CONFIG_JSON:}") private val fcmConfig: String,
    @Value("\${GAMEBRIDGE_APNS_CONFIG_JSON:}") private val apnsConfig: String,
    private val mapper: ObjectMapper,
) {
    private val fcm = ConcurrentHashMap<String, Pair<FirebaseApp, FcmPushSender>>()
    private val apns = ConcurrentHashMap<Pair<String, ApnsEnvironment>, ApnsPushSender>()
    fun fcm(app: String): FcmPushSender = fcm.computeIfAbsent(app) {
        try {
            require(fcmConfig.isNotBlank())
            val node = mapper.readTree(fcmConfig).get(app) ?: error("CONFIG_REQUIRED")
            val project = node.get("projectId")?.asText()?.takeIf { it.isNotBlank() } ?: error("CONFIG_REQUIRED")
            val path = node.get("credentialPath")?.asText()?.takeIf { it.isNotBlank() } ?: error("CONFIG_REQUIRED")
            val credentials = Files.newInputStream(Path.of(path)).use { ServiceAccountCredentials.fromStream(it) }
            val options = FirebaseOptions.builder().setProjectId(project).setCredentials(credentials)
                .setConnectTimeout(30_000).setReadTimeout(30_000).setWriteTimeout(30_000).build()
            val instance = FirebaseApp.initializeApp(options, "gamebridge-" + UUID.randomUUID())
            instance to FcmPushSender(FirebaseMessaging.getInstance(instance))
        } catch (_: Exception) { throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED") }
    }.second
    fun apns(app: String, environment: ApnsEnvironment): ApnsPushSender = apns.computeIfAbsent(app to environment) {
        try {
            require(apnsConfig.isNotBlank())
            val node = mapper.readTree(apnsConfig).get(app) ?: error("CONFIG_REQUIRED")
            fun field(name: String) = node.get(name)?.asText()?.takeIf { it.isNotBlank() } ?: error("CONFIG_REQUIRED")
            val pem = Files.readString(Path.of(field("privateKeyPath")), StandardCharsets.US_ASCII)
            require(pem.contains("-----BEGIN PRIVATE KEY-----") && pem.contains("-----END PRIVATE KEY-----"))
            val base64 = pem.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").filterNot(Char::isWhitespace)
            val key = KeyFactory.getInstance("EC").generatePrivate(PKCS8EncodedKeySpec(Base64.getDecoder().decode(base64))) as ECPrivateKey
            ApnsPushSender.configured(field("topic"), environment, field("teamId"), field("keyId"), key, mapper)
        } catch (_: Exception) { throw ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "CONFIG_REQUIRED") }
    }
    @PreDestroy fun close() { fcm.values.forEach { it.first.delete() }; fcm.clear(); apns.clear() }
}
