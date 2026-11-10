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
}
