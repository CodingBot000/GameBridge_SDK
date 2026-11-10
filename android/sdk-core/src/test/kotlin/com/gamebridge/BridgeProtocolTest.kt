package com.gamebridge

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class BridgeProtocolTest {
    private fun fixture(name: String) = File("../../contracts/fixtures/bridge/$name.json").readBytes()
    @Test fun `accepts request and pending response`() {
        BridgeProtocol.parse(fixture("request"))
        BridgeProtocol.parse(fixture("pending"), "dc9a46f4-8e20-4880-bcbb-ac45033157ca", "2efc133b-3138-4c3e-aa72-0532cd19056e")
    }
    @Test fun `rejects invalid envelopes and unrelated requests`() {
        for (name in listOf("invalid-failure", "invalid-version", "invalid-operation"))
            assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(fixture(name)) }
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(fixture("pending"), expectedRequest = "other") }
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(byteArrayOf(0xC3.toByte())) }
        assertEquals("PAYLOAD_TOO_LARGE", assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(ByteArray(BridgeProtocol.MAX_BYTES + 1)) }.code)
    }
}
