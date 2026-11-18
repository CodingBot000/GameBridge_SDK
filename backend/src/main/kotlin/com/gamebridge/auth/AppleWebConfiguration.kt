package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import com.nimbusds.jose.JOSEObjectType
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.ECDSASigner
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.core.env.Environment
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.file.Files
import java.nio.file.Path
import java.security.KeyFactory
import java.security.interfaces.ECPrivateKey
import java.security.spec.PKCS8EncodedKeySpec
import java.time.Duration
import java.time.Instant
import java.util.Base64
import java.util.Date

internal fun appleForm(value:String)=URLEncoder.encode(value,Charsets.UTF_8)
internal fun validAppleHttps(value:String):Boolean = runCatching {
    val uri=URI(value)
    uri.scheme=="https" && uri.host?.matches(Regex("(?i)[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\\.[a-z][a-z0-9-]*"))==true &&
        uri.rawUserInfo==null && uri.rawQuery==null && uri.rawFragment==null && (uri.port==-1 || uri.port==443) &&
        uri.rawPath.startsWith("/") && !uri.rawPath.contains("%") && !uri.rawPath.contains("..")
}.getOrDefault(false)
class AppleWebApp(val servicesId:String,val callbackUri:String,val returnUri:String,val teamId:String,val keyId:String,val privateKeyPath:String) {
    override fun toString()="AppleWebApp([redacted])"
}
class AppleWebSettings(private val apps:Map<String,AppleWebApp>) {
    fun get(appId:String)=apps[appId]?:throw AuthFlowException("CONFIG_REQUIRED")
    companion object {
        fun parse(raw:String?,mapper:ObjectMapper):AppleWebSettings {
            if(raw.isNullOrBlank())return AppleWebSettings(emptyMap())
            try {
                val root=mapper.readTree(raw);require(root.isObject)
                val apps=mutableMapOf<String,AppleWebApp>()
                root.fields().forEachRemaining { entry ->
                    val n=entry.value
                    fun value(key:String)=n[key]?.takeIf {it.isTextual && it.asText().isNotBlank()}?.asText()?:error("missing")
                    val app=AppleWebApp(value("servicesId"),value("callbackUri"),value("returnUri"),value("teamId"),value("keyId"),value("privateKeyPath"))
                    require(entry.key.isNotBlank() && validAppleHttps(app.callbackUri) && validAppleHttps(app.returnUri) && app.callbackUri!=app.returnUri)
                    require(URI(app.callbackUri).path=="/v1/auth/apple-web/callback")
                    require(app.servicesId.matches(Regex("[A-Za-z0-9.-]{3,255}")) && app.teamId.matches(Regex("[A-Z0-9]{10}")) && app.keyId.matches(Regex("[A-Z0-9]{10}")))
                    apps[entry.key]=app
                }
                return AppleWebSettings(apps)
            }catch(_:Exception){throw IllegalArgumentException("CONFIG_REQUIRED: GAMEBRIDGE_APPLE_WEB_CONFIG_JSON")}
        }
    }
}
fun interface AppleCodeExchanger {fun exchange(app:AppleWebApp,code:String):String; fun preflight(app:AppleWebApp) {}}
/** Server-only p8/ES256 client secret. Never log requests, codes, tokens or original network exceptions. */
class AppleHttpCodeExchanger(private val mapper:ObjectMapper):AppleCodeExchanger {
    private val client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).followRedirects(HttpClient.Redirect.NEVER).build()
    internal fun clientSecret(app:AppleWebApp,now:Instant=Instant.now()):String {
        try {
            val path=Path.of(app.privateKeyPath);require(Files.size(path) in 1..16384)
            val pem=Files.readString(path)
            val der=Base64.getMimeDecoder().decode(pem.replace("-----BEGIN PRIVATE KEY-----","").replace("-----END PRIVATE KEY-----",""))
            val key=KeyFactory.getInstance("EC").generatePrivate(PKCS8EncodedKeySpec(der)) as ECPrivateKey
            require(key.params.curve.field.fieldSize==256)
            return SignedJWT(JWSHeader.Builder(JWSAlgorithm.ES256).keyID(app.keyId).type(JOSEObjectType.JWT).build(),
                JWTClaimsSet.Builder().issuer(app.teamId).subject(app.servicesId).audience("https://appleid.apple.com")
                    .issueTime(Date.from(now)).expirationTime(Date.from(now.plusSeconds(300))).build())
                .apply {sign(ECDSASigner(key))}.serialize()
        }catch(_:Exception){throw AuthFlowException("CONFIG_REQUIRED")}
    }
    override fun preflight(app:AppleWebApp) {clientSecret(app)}
    override fun exchange(app:AppleWebApp,code:String):String {
        val secret=clientSecret(app)
        try {
            val form=mapOf("grant_type" to "authorization_code","client_id" to app.servicesId,"client_secret" to secret,"code" to code,"redirect_uri" to app.callbackUri)
                .entries.joinToString("&"){appleForm(it.key)+"="+appleForm(it.value)}
            val request=HttpRequest.newBuilder(URI("https://appleid.apple.com/auth/token")).timeout(Duration.ofSeconds(30))
                .header("Content-Type","application/x-www-form-urlencoded").header("Accept","application/json").POST(HttpRequest.BodyPublishers.ofString(form)).build()
            val response=client.send(request,HttpResponse.BodyHandlers.ofInputStream())
            val bytes=response.body().use {it.readNBytes(65537)}
            if(response.statusCode()!=200 || bytes.size>65536)throw AuthFlowException("AUTH_FAILED")
            return mapper.readTree(bytes)["id_token"]?.takeIf {it.isTextual && it.asText().length in 20..32768}?.asText()?:throw AuthFlowException("AUTH_FAILED")
        }catch(e:AuthFlowException){throw e}
         catch(_:Exception){throw AuthFlowException("NETWORK_UNAVAILABLE")}
    }
}
@Configuration
@Profile("sandbox","production")
class AppleWebConfiguration {
    @Bean fun appleWebSettings(environment:Environment,mapper:ObjectMapper)=AppleWebSettings.parse(environment.getProperty("GAMEBRIDGE_APPLE_WEB_CONFIG_JSON"),mapper)
    @Bean fun appleCodeExchanger(mapper:ObjectMapper):AppleCodeExchanger=AppleHttpCodeExchanger(mapper)
}
