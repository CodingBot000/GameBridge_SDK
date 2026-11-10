package com.gamebridge.push

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingException
import com.google.firebase.messaging.Message
import com.google.firebase.messaging.MessagingErrorCode
import com.google.firebase.messaging.Notification
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.ECDSASigner
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import java.io.IOException
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.security.interfaces.ECPrivateKey
import java.time.Duration
import java.time.Instant
import java.util.Date

enum class PushSendResult { SENT, INVALID_TOKEN, RETRYABLE, FAILED }
internal data class PushContent(val messageId: String, val route: String, val title: String, val body: String, val campaignId: String? = null) {
    init { require(messageId.isNotBlank() && route in setOf("home", "store")) }
    fun data(): Map<String, String> = buildMap { put("messageId", messageId); put("route", route); campaignId?.let { put("campaignId", it) } }
}

/** One attempt only; scheduling and durable token lifecycle are owned by the caller. */
internal class FcmPushSender(private val messaging: FirebaseMessaging) {
    fun send(token: String, content: PushContent): PushSendResult {
        if (token.isBlank()) return PushSendResult.FAILED
        val message = Message.builder().setToken(token).putAllData(content.data())
            .setNotification(Notification.builder().setTitle(content.title).setBody(content.body).build()).build()
        return try { messaging.send(message); PushSendResult.SENT } catch (e: FirebaseMessagingException) { mapFcmError(e.messagingErrorCode) }
    }
}
internal fun mapFcmError(code: MessagingErrorCode?): PushSendResult = when (code) {
    MessagingErrorCode.UNREGISTERED -> PushSendResult.INVALID_TOKEN
    MessagingErrorCode.QUOTA_EXCEEDED, MessagingErrorCode.UNAVAILABLE, MessagingErrorCode.INTERNAL -> PushSendResult.RETRYABLE
    else -> PushSendResult.FAILED
}

internal enum class ApnsEnvironment(val host: String) {
    SANDBOX("api.sandbox.push.apple.com"), PRODUCTION("api.push.apple.com")
}
internal fun interface ApnsTransport { fun send(request: HttpRequest): Int }
internal class ApnsPushSender(
    private val topic: String,
    private val environment: ApnsEnvironment,
    private val tokenProvider: () -> String,
    private val mapper: ObjectMapper,
    private val transport: ApnsTransport,
) {
    init { require(topic.isNotBlank()) }
    fun send(deviceToken: String, content: PushContent): PushSendResult {
        if (deviceToken.length !in 2..512 || deviceToken.length % 2 != 0 || !deviceToken.all { it in '0'..'9' || it in 'a'..'f' || it in 'A'..'F' }) return PushSendResult.FAILED
        val payload = mutableMapOf<String, Any>("aps" to mapOf("alert" to mapOf("title" to content.title, "body" to content.body)))
        payload.putAll(content.data())
        val payloadBytes = mapper.writeValueAsBytes(payload)
        if (payloadBytes.size > 4096) return PushSendResult.FAILED
        val request = HttpRequest.newBuilder(URI("https://${environment.host}/3/device/$deviceToken"))
            .version(HttpClient.Version.HTTP_2).timeout(Duration.ofSeconds(10))
            .header("authorization", "bearer ${tokenProvider()}")
            .header("apns-topic", topic).header("apns-push-type", "alert")
            .header("content-type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofByteArray(payloadBytes)).build()
        return try { mapApnsStatus(transport.send(request)) } catch (_: IOException) { PushSendResult.RETRYABLE }
        catch (_: InterruptedException) { Thread.currentThread().interrupt(); PushSendResult.RETRYABLE }
    }
    companion object {
        fun configured(topic: String, environment: ApnsEnvironment, teamId: String, keyId: String, key: ECPrivateKey, mapper: ObjectMapper): ApnsPushSender {
            require(teamId.isNotBlank() && keyId.isNotBlank())
            val client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).connectTimeout(Duration.ofSeconds(10)).build()
            val cachedToken = CachedApnsProviderToken { apnsProviderToken(teamId, keyId, key) }
            return ApnsPushSender(topic, environment, { cachedToken.get() }, mapper,
                ApnsTransport {
                    val response = client.send(it, HttpResponse.BodyHandlers.discarding())
                    if (response.version() != HttpClient.Version.HTTP_2) throw IOException("APNs requires HTTP/2")
                    response.statusCode()
                })
        }
    }
}
internal fun mapApnsStatus(status: Int): PushSendResult = when (status) {
    200 -> PushSendResult.SENT
    410 -> PushSendResult.INVALID_TOKEN
    429, in 500..599 -> PushSendResult.RETRYABLE
    else -> PushSendResult.FAILED
}
internal fun apnsProviderToken(teamId: String, keyId: String, key: ECPrivateKey): String =
    SignedJWT(JWSHeader.Builder(JWSAlgorithm.ES256).keyID(keyId).build(), JWTClaimsSet.Builder().issuer(teamId).issueTime(Date.from(Instant.now())).build())
        .apply { sign(ECDSASigner(key)) }.serialize()

/** APNs requires rotating between 20 and 60 minutes, not once per request. */
internal class CachedApnsProviderToken(
    private val clock: () -> Long = System::nanoTime,
    private val create: () -> String,
) {
    private var value: String? = null
    private var createdAt = 0L
    @Synchronized fun get(): String {
        val now = clock()
        val cached = value
        if (cached != null && now - createdAt >= 0 && now - createdAt < Duration.ofMinutes(40).toNanos()) return cached
        return create().also { value = it; createdAt = now }
    }
}
