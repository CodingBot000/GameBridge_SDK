package com.gamebridge.bridge

import com.gamebridge.BridgeDispatchResult
import kotlinx.serialization.json.*
import java.util.UUID
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import kotlin.test.*

class HostPushDeliveryTest {
    @Test fun `cold start route is queued and token result is redacted`() {
        val messages = LinkedBlockingQueue<String>()
        BridgeFacade.setCallback(null)
        assertEquals("QUEUED", BridgeFacade.forwardNotification("cold-id", "store", null, true))
        assertEquals("DUPLICATE", BridgeFacade.forwardNotification("cold-id", "store", null, true))
        assertEquals("INVALID_ARGUMENT", BridgeFacade.forwardNotification("bad", "https://ignored.invalid", null, true))
        assertFalse(BridgeFacade.forwardFcmToken("synthetic-secret-token"))
        BridgeFacade.setCallback(BridgeCallback { messages.add(it) })
        try {
            val facade = BridgeFacade::class.java
            val generation = (facade.getDeclaredField("callbackGeneration").apply { isAccessible = true }.get(BridgeFacade) as java.util.concurrent.atomic.AtomicLong).get()
            val session = UUID.randomUUID().toString(); val requestId = UUID.randomUUID().toString()
            val request = buildJsonObject {
                put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "request"); put("requestId", requestId)
                put("operation", "sdk.initialize"); put("payload", buildJsonObject {})
            }.toString().toByteArray()
            val response = buildJsonObject {
                put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "response"); put("requestId", requestId)
                put("operation", "sdk.initialize"); put("ok", true); put("result", buildJsonObject {}); put("error", JsonNull)
            }.toString()
            val after = facade.getDeclaredMethod("afterDispatch", ByteArray::class.java, java.lang.Long.TYPE, BridgeDispatchResult::class.java).apply { isAccessible = true }
            after.invoke(BridgeFacade, request, generation, BridgeDispatchResult.Message(response))
            val first = Json.parseToJsonElement(assertNotNull(messages.poll(2, TimeUnit.SECONDS))).jsonObject
            assertEquals("PushOpened", first.getValue("type").jsonPrimitive.content)
            assertEquals("store", first.getValue("payload").jsonObject.getValue("route").jsonPrimitive.content)
            assertTrue(BridgeFacade.forwardFcmToken("synthetic-secret-token"))
            val raw = assertNotNull(messages.poll(2, TimeUnit.SECONDS))
            assertFalse(raw.contains("synthetic-secret-token"))
            val failure = Json.parseToJsonElement(raw).jsonObject
            assertEquals("PushTokenChanged", failure.getValue("type").jsonPrimitive.content)
            assertFalse(failure.getValue("payload").jsonObject.getValue("registered").jsonPrimitive.boolean)
            assertEquals("NOT_INITIALIZED", failure.getValue("payload").jsonObject.getValue("errorCode").jsonPrimitive.content)
        } finally { BridgeFacade.setCallback(null) }
    }
}
