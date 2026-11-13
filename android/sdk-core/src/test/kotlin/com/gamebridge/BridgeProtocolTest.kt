package com.gamebridge

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class BridgeProtocolTest {
    private fun fixture(name: String) = File(System.getenv("GAMEBRIDGE_CONTRACT_ROOT") ?: "../../contracts", "fixtures/bridge/$name.json").readBytes()
    @Test fun `accepts request and pending response`() {
        for (name in listOf("request", "success", "failure", "event", "unsupported")) BridgeProtocol.parse(fixture(name))
        BridgeProtocol.parse(fixture("pending"), "dc9a46f4-8e20-4880-bcbb-ac45033157ca", "2efc133b-3138-4c3e-aa72-0532cd19056e")
    }
    @Test fun `rejects invalid envelopes and unrelated requests`() {
        for (name in listOf("invalid-failure", "invalid-version", "invalid-operation"))
            assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(fixture(name)) }
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(fixture("pending"), expectedRequest = "other") }
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(byteArrayOf(0xC3.toByte())) }
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse("{".toByteArray()) }
        val request = kotlinx.serialization.json.Json.parseToJsonElement(fixture("request").decodeToString()) as kotlinx.serialization.json.JsonObject
        val missing = kotlinx.serialization.json.JsonObject(request - "requestId").toString().toByteArray()
        assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(missing) }
        val root = System.getenv("GAMEBRIDGE_CONTRACT_ROOT") ?: "../../contracts"
        val length = kotlinx.serialization.json.Json.parseToJsonElement(File(root, "fixtures/bridge-length.json").readText()) as kotlinx.serialization.json.JsonObject
        val maxBytes = length.getValue("maxBytes").toString().toInt()
        val invalidBytes = length.getValue("invalidBytes").toString().toInt()
        assertEquals(maxBytes, BridgeProtocol.MAX_BYTES)
        assertEquals(maxBytes + 1, invalidBytes)
        assertEquals("PAYLOAD_TOO_LARGE", assertFailsWith<BridgeProtocol.ProtocolException> { BridgeProtocol.parse(ByteArray(invalidBytes)) }.code)
    }
}
