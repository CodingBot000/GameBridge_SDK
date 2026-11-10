package com.gamebridge

import org.junit.jupiter.api.Test
import kotlin.test.*

class PushPayloadTest {
    @Test fun `only allowlisted routes and fields are accepted`() {
        val message = PushPayload.parse(mapOf("messageId" to "msg", "route" to "store", "campaignId" to "campaign", "url" to "https://invalid.example"))
        assertEquals(PushPayload("msg", "store", "campaign"), message)
        assertNull(PushPayload.parse(mapOf("messageId" to "msg", "route" to "https://invalid.example")))
        assertNull(PushPayload.parse(mapOf("messageId" to "", "route" to "home")))
    }
}
