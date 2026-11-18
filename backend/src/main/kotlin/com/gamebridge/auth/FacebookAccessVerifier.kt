package com.gamebridge.auth

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.time.Clock
import java.time.Duration
import java.time.Instant

class FacebookApp(val appId: String, val appSecret: String?, val requiredScopes: Set<String>) {
    override fun toString() = "FacebookApp([redacted])"
}
class FacebookAccessResult(val identity: VerifiedIdentity, val proofHash: ByteArray, val expiresAt: Instant) {
    override fun toString() = "FacebookAccessResult([redacted])"
}
fun interface FacebookDebugLookup { fun inspect(token: String, app: FacebookApp): JsonNode }
class FacebookAccessVerifier(private val apps: Map<String, FacebookApp>, private val lookup: FacebookDebugLookup,
                             private val clock: Clock = Clock.systemUTC()) {
    fun verify(scope: String, token: String, allowedApps: Set<String>): FacebookAccessResult {
        val app = apps[scope] ?: throw IdentityVerificationException("CONFIG_REQUIRED")
        if (app.appSecret.isNullOrBlank() || app.appId !in allowedApps) throw IdentityVerificationException("CONFIG_REQUIRED")
        if (token.isBlank() || token.length > 16384) throw IdentityVerificationException("AUTH_FAILED")
        val data = try { lookup.inspect(token, app).path("data") }
                   catch (error: IdentityVerificationException) { throw error }
                   catch (_: Exception) { throw IdentityVerificationException("NETWORK_UNAVAILABLE") }
        val user = data.path("user_id").takeIf { it.isTextual }?.asText()
        val expiry = data.path("expires_at").takeIf { it.isIntegralNumber }?.asLong() ?: 0
        val dataExpiry = data.path("data_access_expires_at").takeIf { it.isIntegralNumber }?.asLong() ?: 0
        val scopes = data.path("scopes").takeIf { it.isArray }?.map { it.asText() }?.toSet() ?: emptySet()
        if (!data.path("is_valid").isBoolean || !data.path("is_valid").booleanValue() || data.path("type").asText() != "USER" ||
            data.path("app_id").asText() != app.appId || user.isNullOrBlank() || expiry <= clock.instant().epochSecond ||
            dataExpiry <= clock.instant().epochSecond || !scopes.containsAll(app.requiredScopes)) throw IdentityVerificationException("AUTH_FAILED")
        return FacebookAccessResult(VerifiedIdentity(IdentityProvider.FACEBOOK,"https://www.facebook.com","${app.appId}:$user",app.appId),
            MessageDigest.getInstance("SHA-256").digest(token.toByteArray(StandardCharsets.UTF_8)),Instant.ofEpochSecond(minOf(expiry,dataExpiry)))
    }
    companion object {
        fun settings(raw:String,mapper:ObjectMapper):Map<String,FacebookApp> = try {parseSettings(raw,mapper)} catch (_:Exception) {throw IllegalArgumentException("CONFIG_REQUIRED: Facebook auth settings")}
        private fun parseSettings(raw: String, mapper: ObjectMapper): Map<String, FacebookApp> {
            if (raw.isBlank()) return emptyMap()
            val root = mapper.readTree(raw);require(root.isObject) {"CONFIG_REQUIRED: Facebook settings"}
            val result = root.fields().asSequence().associate { entry ->
                val node=entry.value;val app=node.path("appId").asText();require(entry.key.isNotBlank() && app.matches(Regex("[0-9]+"))) {"CONFIG_REQUIRED: Facebook app"}
                val scopes=node.path("requiredScopes");require(scopes.isMissingNode || (scopes.isArray && scopes.all {it.isTextual && it.asText().isNotBlank()})) {"CONFIG_REQUIRED: Facebook scopes"}
                entry.key to FacebookApp(app,node.path("appSecret").takeIf {it.isTextual}?.asText(),if (scopes.isMissingNode) setOf("public_profile") else scopes.map {it.asText()}.toSet()+"public_profile")
            }
            require(result.values.map {it.appId}.toSet().size==result.size) {"CONFIG_REQUIRED: Facebook appId must not span app scopes"}
            return result
        }
    }
}
@Configuration
@Profile("sandbox", "production")
class FacebookAccessConfiguration {
    @Bean fun facebookAccessVerifier(mapper:ObjectMapper,@Value("\${GAMEBRIDGE_FACEBOOK_AUTH_CONFIG_JSON:}") raw:String):FacebookAccessVerifier {
        val client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).followRedirects(HttpClient.Redirect.NEVER).build()
        return FacebookAccessVerifier(FacebookAccessVerifier.settings(raw,mapper),FacebookDebugLookup { token,app ->
            // Graph requires input_token in its query. Do not log this URI or propagate HTTP exceptions containing it.
            val uri=URI.create("https://graph.facebook.com/v27.0/debug_token?input_token="+URLEncoder.encode(token,StandardCharsets.UTF_8))
            val request=HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(30)).header("Authorization","Bearer ${app.appId}|${app.appSecret}").GET().build()
            try {
                val response=client.send(request,HttpResponse.BodyHandlers.ofString())
                if (response.statusCode()>=500 || response.statusCode()==429) throw IdentityVerificationException("NETWORK_UNAVAILABLE")
                if (response.statusCode()!=200 || response.body().length>262144) throw IdentityVerificationException("AUTH_FAILED")
                mapper.readTree(response.body())
            } catch (error:IdentityVerificationException) {throw error}
              catch (_:Exception) {throw IdentityVerificationException("NETWORK_UNAVAILABLE")}
        })
    }
}
