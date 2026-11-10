package com.gamebridge.bridge

import com.gamebridge.BridgeDispatchResult
import com.gamebridge.PurchaseStatus
import com.gamebridge.android.purchase.GoogleStoreEvent
import kotlinx.serialization.json.*
import java.util.UUID
import kotlin.test.*

class PurchaseEventDeliveryTest {
    @Test fun `event sender drops stale account session and unconfirmed grant`() {
        val messages = mutableListOf<String>()
        BridgeFacade.setCallback(BridgeCallback { messages.add(it) })
        try {
            val facade = BridgeFacade::class.java
            val callbackGeneration = facade.getDeclaredField("callbackGeneration").apply { isAccessible = true }
                .get(BridgeFacade) as java.util.concurrent.atomic.AtomicLong
            val generation = callbackGeneration.get()
            val session = UUID.randomUUID().toString(); val requestId = UUID.randomUUID().toString()
            fun request(operation: String) = buildJsonObject {
                put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "request"); put("requestId", requestId)
                put("operation", operation); put("payload", buildJsonObject {})
            }.toString().toByteArray()
            val after = facade.getDeclaredMethod("afterDispatch", ByteArray::class.java, java.lang.Long.TYPE, BridgeDispatchResult::class.java).apply { isAccessible = true }
            val response = buildJsonObject {
                put("protocolVersion", 1); put("sdkSessionId", session); put("kind", "response"); put("requestId", requestId)
                put("operation", "sdk.initialize"); put("ok", true); put("result", buildJsonObject {}); put("error", JsonNull)
            }.toString()
            after.invoke(BridgeFacade, request("sdk.initialize"), generation, BridgeDispatchResult.Message(response))
            val make = facade.getDeclaredMethod("purchaseEmitter").apply { isAccessible = true }
            @Suppress("UNCHECKED_CAST") val emit = make.invoke(BridgeFacade) as (GoogleStoreEvent) -> Unit
            emit(GoogleStoreEvent("coins_100", PurchaseStatus.PURCHASED, null, null))
            assertEquals(0, messages.size)
            val purchase = UUID.randomUUID()
            emit(GoogleStoreEvent("coins_100", PurchaseStatus.PURCHASED, null, purchase))
            val result = Json.parseToJsonElement(messages.single()).jsonObject
            assertEquals(session, result.getValue("sdkSessionId").jsonPrimitive.content)
            assertEquals(purchase.toString(), result.getValue("payload").jsonObject.getValue("serverPurchaseId").jsonPrimitive.content)
            val before = facade.getDeclaredMethod("beforeDispatch", ByteArray::class.java, java.lang.Long.TYPE).apply { isAccessible = true }
            before.invoke(BridgeFacade, request("auth.signOut"), generation)
            emit(GoogleStoreEvent("coins_100", PurchaseStatus.PURCHASED, null, purchase))
            assertEquals(1, messages.size)
        } finally { BridgeFacade.setCallback(null) }
    }
}
