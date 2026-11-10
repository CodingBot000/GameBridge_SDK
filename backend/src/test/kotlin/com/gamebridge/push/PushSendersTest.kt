package com.gamebridge.push

import com.fasterxml.jackson.databind.ObjectMapper
import com.google.firebase.messaging.MessagingErrorCode
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
        assertEquals(PushSendResult.INVALID_TOKEN, mapFcmError(MessagingErrorCode.UNREGISTERED))
        assertEquals(PushSendResult.RETRYABLE, mapFcmError(MessagingErrorCode.QUOTA_EXCEEDED))
        assertEquals(PushSendResult.RETRYABLE, mapFcmError(MessagingErrorCode.UNAVAILABLE))
        assertEquals(PushSendResult.FAILED, mapFcmError(MessagingErrorCode.INVALID_ARGUMENT))
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
        assertEquals(PushSendResult.FAILED, sender.send("not-a-device-token", content)); assertFalse(called)
        assertEquals(PushSendResult.SENT, sender.send("aa11", content)); assertTrue(called)
        assertEquals(PushSendResult.INVALID_TOKEN, mapApnsStatus(410))
        assertEquals(PushSendResult.FAILED, mapApnsStatus(400))
        assertEquals(PushSendResult.RETRYABLE, mapApnsStatus(429))
        assertEquals(PushSendResult.RETRYABLE, mapApnsStatus(503))
        val offline = ApnsPushSender("test.bundle", ApnsEnvironment.PRODUCTION, { "fixture" }, ObjectMapper(), ApnsTransport { throw IOException("offline") })
        assertEquals(PushSendResult.RETRYABLE, offline.send("aa11", content))
        assertFailsWith<IllegalArgumentException> { PushContent("x", "https://example.invalid", "a", "b") }
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
