package com.gamebridge.push

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.firebase.messaging.MessagingErrorCode
import com.google.firebase.ErrorCode
import com.nimbusds.jose.crypto.ECDSAVerifier
import com.nimbusds.jwt.SignedJWT
import java.io.IOException
import java.security.KeyPairGenerator
import java.security.interfaces.ECPrivateKey
import java.security.interfaces.ECPublicKey
import java.security.spec.ECGenParameterSpec
import org.junit.jupiter.api.Test
import kotlin.test.*

class PushSendersTest {
    private val content = PushContent("message-1", "home", "title", "body", "campaign")
    @Test fun `fcm maps only unregistered to invalid token`() {
        assertEquals(PushSendResult.INVALID_TOKEN, mapFcmError(MessagingErrorCode.UNREGISTERED).result)
        assertEquals(PushSendResult.RETRYABLE, mapFcmError(MessagingErrorCode.QUOTA_EXCEEDED).result)
        assertEquals(PushSendResult.RETRYABLE, mapFcmError(MessagingErrorCode.UNAVAILABLE).result)
        assertEquals(PushSendResult.FAILED, mapFcmError(MessagingErrorCode.INVALID_ARGUMENT).result)
        assertEquals(PushFailure.TIMEOUT, mapFcmError(null, ErrorCode.DEADLINE_EXCEEDED).failure)
        assertEquals(PushFailure.SERVER_ERROR, mapFcmError(null, ErrorCode.UNAVAILABLE).failure)
    }
    @Test fun `apns request uses fixed host topic and maps results without leaking token`() {
        var called = false
        val sender = ApnsPushSender("test.bundle", ApnsEnvironment.SANDBOX, { "test-provider-token" }, ObjectMapper(), ApnsTransport { req ->
            called = true
            assertEquals("api.sandbox.push.apple.com", req.uri().host)
            assertEquals("test.bundle", req.headers().firstValue("apns-topic").orElse(null))
            assertEquals("alert", req.headers().firstValue("apns-push-type").orElse(null))
            200
        })
        assertEquals(PushSendResult.FAILED, sender.send("not-a-device-token", content).result); assertFalse(called)
        assertEquals(PushSendResult.FAILED, sender.send("aa11", content.copy(body = "x".repeat(4097))).result); assertFalse(called)
        assertEquals(PushSendResult.SENT, sender.send("aa11", content).result); assertTrue(called)
        assertEquals(PushSendResult.INVALID_TOKEN, mapApnsStatus(410).result)
        assertEquals(PushSendResult.FAILED, mapApnsStatus(400).result)
        assertEquals(PushSendResult.RETRYABLE, mapApnsStatus(429).result)
        assertEquals(PushSendResult.RETRYABLE, mapApnsStatus(503).result)
        assertEquals(PushFailure.SERVER_ERROR, mapApnsStatus(503).failure)
        assertEquals(PushFailure.RATE_LIMIT, mapApnsStatus(429).failure)
        val offline = ApnsPushSender("test.bundle", ApnsEnvironment.PRODUCTION, { "fixture" }, ObjectMapper(), ApnsTransport { throw IOException("offline") })
        assertEquals(PushSendResult.RETRYABLE, offline.send("aa11", content).result)
        assertFailsWith<IllegalArgumentException> { PushContent("x", "https://example.invalid", "a", "b") }
        assertFalse(PushContent("id", "home", "secret-title", "secret-body").toString().contains("secret-body"))
    }
    @Test fun `provider token is reused and refreshed after forty minutes`() {
        var nanos = 0L; var created = 0
        val cache = CachedApnsProviderToken({ nanos }) { "signed-" + ++created }
        assertEquals("signed-1", cache.get()); nanos = java.time.Duration.ofMinutes(39).toNanos()
        assertEquals("signed-1", cache.get()); nanos = java.time.Duration.ofMinutes(40).toNanos()
        assertEquals("signed-2", cache.get()); assertEquals(2, created)
    }
    @Test fun `apns provider jwt signs with ES256 and configured identifiers`() {
        val generator = KeyPairGenerator.getInstance("EC"); generator.initialize(ECGenParameterSpec("secp256r1"))
        val pair = generator.generateKeyPair(); val jwt = SignedJWT.parse(apnsProviderToken("test-team", "test-key", pair.private as ECPrivateKey))
        assertTrue(jwt.verify(ECDSAVerifier(pair.public as ECPublicKey)))
        assertEquals("test-team", jwt.jwtClaimsSet.issuer); assertEquals("test-key", jwt.header.keyID)
    }
}
