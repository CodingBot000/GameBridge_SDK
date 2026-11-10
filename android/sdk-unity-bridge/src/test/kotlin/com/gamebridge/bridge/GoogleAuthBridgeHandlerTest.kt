package com.gamebridge.bridge

import com.gamebridge.*
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
        val dispatcher = BridgeDispatcher(ModeBridgeHandler(local, GoogleAuthBridgeHandler { fake }))
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
        assertEquals("UNSUPPORTED_OPERATION", send("store.purchase").getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
        send("sdk.shutdown"); assertTrue(closed)
    }
}
