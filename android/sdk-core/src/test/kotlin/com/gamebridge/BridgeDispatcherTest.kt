package com.gamebridge

import kotlinx.serialization.json.*
import java.io.File
import kotlin.test.*

class BridgeDispatcherTest {
    @Test fun `status returns correlated response and unimplemented purchase fails explicitly`() {
        val fixture = File("../../contracts/fixtures/bridge/request.json").readText()
        val dispatcher = BridgeDispatcher()
        val unsupported = dispatcher.dispatch(fixture.toByteArray()) as BridgeDispatchResult.Message
        val failure = Json.parseToJsonElement(unsupported.json).jsonObject
        assertFalse(failure.getValue("ok").jsonPrimitive.boolean)
        assertEquals("UNSUPPORTED_OPERATION", failure.getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
        val busy = dispatcher.busy(fixture.toByteArray()) as BridgeDispatchResult.Message
        assertEquals("BUSY", Json.parseToJsonElement(busy.json).jsonObject.getValue("error").jsonObject.getValue("code").jsonPrimitive.content)
        val status = fixture.replace("store.purchase", "sdk.status")
        val result = dispatcher.dispatch(status.toByteArray()) as BridgeDispatchResult.Message
        val response = BridgeProtocol.parse(result.json.toByteArray(), expectedRequest = "2efc133b-3138-4c3e-aa72-0532cd19056e")
        assertEquals("UNINITIALIZED", response.getValue("result").jsonObject.getValue("state").jsonPrimitive.content)
        val shutdown = fixture.replace("store.purchase", "sdk.shutdown")
        dispatcher.dispatch(shutdown.toByteArray())
        val after = dispatcher.dispatch(status.toByteArray()) as BridgeDispatchResult.Message
        assertEquals("SHUTDOWN", Json.parseToJsonElement(after.json).jsonObject.getValue("result").jsonObject.getValue("state").jsonPrimitive.content)
        assertEquals("PAYLOAD_TOO_LARGE", (dispatcher.dispatch(ByteArray(BridgeProtocol.MAX_BYTES + 1)) as BridgeDispatchResult.Rejected).code)
    }
    @Test fun `provider results and sanitized failures retain request correlation`() {
        val fixture = File("../../contracts/fixtures/bridge/request.json").readText()
        var calls = 0
        val dispatcher = BridgeDispatcher(BridgeOperationHandler { _, _ ->
            calls++
            if (calls == 1) JsonArray(listOf(JsonPrimitive("product")))
            else throw SdkFailure("NETWORK_UNAVAILABLE", retryable = true)
        })
        val success = dispatcher.dispatch(fixture.toByteArray()) as BridgeDispatchResult.Message
        val parsed = BridgeProtocol.parse(success.json.toByteArray())
        assertEquals(JsonArray(listOf(JsonPrimitive("product"))), parsed["result"])
        val failure = dispatcher.dispatch(fixture.toByteArray()) as BridgeDispatchResult.Message
        val error = BridgeProtocol.parse(failure.json.toByteArray())["error"]!!.jsonObject
        assertEquals("NETWORK_UNAVAILABLE", error["code"]!!.jsonPrimitive.content)
        assertTrue(error["retryable"]!!.jsonPrimitive.boolean)
        dispatcher.dispatch("invalid secret".toByteArray())
        assertEquals(2, calls)
        val unexpected = BridgeDispatcher(BridgeOperationHandler { _, _ -> throw IllegalStateException("secret") })
        val redacted = unexpected.dispatch(fixture.toByteArray()) as BridgeDispatchResult.Message
        assertFalse(redacted.json.contains("secret"))
        assertEquals("INTERNAL_ERROR", BridgeProtocol.parse(redacted.json.toByteArray())["error"]!!.jsonObject["code"]!!.jsonPrimitive.content)
    }

    @Test fun `diagnostics expose only typed bounded events without payload or failure details`() {
        val fixture = File("../../contracts/fixtures/bridge/request.json").readText()
        val dispatcher = BridgeDispatcher(BridgeOperationHandler { _, _ -> throw IllegalStateException("sensitive token") })
        repeat(101) { dispatcher.dispatch(fixture.toByteArray()) }
        val query = fixture.replace("store.purchase", "diagnostics.get")
        val response = dispatcher.dispatch(query.toByteArray()) as BridgeDispatchResult.Message
        val events = Json.parseToJsonElement(response.json).jsonObject["result"]!!.jsonObject["events"]!!.jsonArray
        assertEquals(200, events.size)
        assertEquals("PURCHASE", events.last().jsonObject["kind"]!!.jsonPrimitive.content)
        assertEquals("FAILED", events.last().jsonObject["outcome"]!!.jsonPrimitive.content)
        assertFalse(response.json.contains("sensitive"))
        assertFalse(response.json.contains("payload"))
    }

}
