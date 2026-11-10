package com.gamebridge.bridge

import com.gamebridge.*
import com.gamebridge.android.purchase.GoogleRecoveryCounts
import kotlinx.serialization.json.*
import java.util.UUID
import kotlin.test.*

class GoogleAuthBridgeHandlerTest {
    @Test fun `sandbox auth uses only Google and never falls back to mock`() {
        var signIns = 0; var closed = false; var mockCalls = 0
        val fake = object : GoogleAuthBridgeApi {
            override suspend fun signIn(): UserProfile { signIns++; return UserProfile("d2719c4e-d533-47ee-9efd-838791ea79c8", null, "GOOGLE") }
            override suspend fun restore(): UserProfile? = null
            override suspend fun signOut() {}
            override fun close() { closed = true }
        }
        val local = BridgeOperationHandler { _, _ -> mockCalls++; buildJsonObject {} }
        val dispatcher = BridgeDispatcher(ModeBridgeHandler(local, GoogleAuthBridgeHandler { _, _ -> fake }))
        val session = UUID.randomUUID().toString()
        fun send(operation: String, payload: JsonObject = buildJsonObject {}): JsonObject {
            val request = buildJsonObject {
                put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "request")
                put("requestId", UUID.randomUUID().toString()); put("operation", operation); put("payload", payload)
            }
            val message = dispatcher.dispatch(request.toString().toByteArray()) as BridgeDispatchResult.Message
            return BridgeProtocol.parse(message.json.toByteArray())
        }
        val init = send("sdk.initialize", buildJsonObject {
            put("providerMode", "PLATFORM_SANDBOX"); put("appId", "demo"); put("backendBaseUrl", "https://example.invalid")
            put("requestTimeoutMs", 30000); put("googleServerClientId", "public-test-client-id")
        })
        assertTrue(init.getValue("ok").jsonPrimitive.boolean)
        assertEquals("UNSUPPORTED_PROVIDER", send("auth.signIn", buildJsonObject { put("provider", "MOCK") }).getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
        val profile = send("auth.signIn", buildJsonObject { put("provider", "GOOGLE") }).getValue("result").jsonObject
        assertEquals("GOOGLE", profile.getValue("provider").jsonPrimitive.content)
        assertEquals(1, signIns); assertEquals(0, mockCalls)
        assertEquals("INVALID_ARGUMENT", send("store.purchase").getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
        send("sdk.shutdown"); assertTrue(closed)
    }
    @Test fun `sandbox purchase is pending until server confirmation`() {
        val fake = object : GoogleAuthBridgeApi {
            override suspend fun signIn() = UserProfile("d2719c4e-d533-47ee-9efd-838791ea79c8", null, "GOOGLE")
            override suspend fun restore(): UserProfile? = null
            override suspend fun signOut() {}
            override suspend fun purchase(productId: String) = PurchaseStatus.VERIFICATION_PENDING
            override suspend fun recoverDetailed() = GoogleRecoveryCounts(4, 1, 2, 1)
            override suspend fun entitlements() = EntitlementSnapshot("d2719c4e-d533-47ee-9efd-838791ea79c8", false, "100", "1", "2026-01-01T00:00:00Z")
            override fun close() {}
        }
        var mapping: Map<String, String>? = null
        val handler = GoogleAuthBridgeHandler { _, ids -> mapping = ids; fake }
        val result = handler.invoke("sdk.initialize", buildJsonObject {
            put("providerMode", "PLATFORM_SANDBOX"); put("appId", "demo"); put("backendBaseUrl", "https://example.invalid")
            put("requestTimeoutMs", 30000); put("googleServerClientId", "test-client")
            put("storeProductIds", buildJsonObject { put("coins_100", "test_coins"); put("premium_unlock", "test_premium") })
        }).jsonObject
        assertEquals("test_coins", mapping?.get("coins_100"))
        assertTrue(result.getValue("capabilities").jsonObject.getValue("store").jsonObject.getValue("configured").jsonPrimitive.boolean)
        val purchase = handler.invoke("store.purchase", buildJsonObject { put("productId", "coins_100") }).jsonObject
        assertEquals("VERIFICATION_PENDING", purchase.getValue("status").jsonPrimitive.content)
        assertEquals("NOT_GRANTED", purchase.getValue("fulfillmentStatus").jsonPrimitive.content)
        assertEquals(JsonNull, purchase.getValue("serverPurchaseId"))
        val sync = handler.invoke("store.sync", buildJsonObject { put("reason", "APP_RESUME") }).jsonObject
        assertEquals(4, sync.getValue("examinedCount").jsonPrimitive.int)
        assertEquals(2, sync.getValue("deferredCount").jsonPrimitive.int)
        assertEquals("100", sync.getValue("entitlements").jsonObject.getValue("coinBalance").jsonPrimitive.content)
        assertEquals("INVALID_ARGUMENT", assertFailsWith<SdkFailure> { handler.invoke("store.sync", buildJsonObject { put("reason", "OTHER") }) }.code)
    }
    @Test fun `invalid store mapping never creates provider`() {
        var created = false
        val handler = GoogleAuthBridgeHandler { _, _ -> created = true; error("unexpected") }
        val failure = assertFailsWith<SdkFailure> {
            handler.invoke("sdk.initialize", buildJsonObject {
                put("providerMode", "PLATFORM_SANDBOX"); put("appId", "demo"); put("backendBaseUrl", "https://example.invalid")
                put("requestTimeoutMs", 30000); put("storeProductIds", buildJsonObject { put("coins_100", "same"); put("premium_unlock", "same") })
            })
        }
        assertEquals("CONFIG_REQUIRED", failure.code); assertFalse(created)
    }

}
