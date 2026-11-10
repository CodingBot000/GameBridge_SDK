package com.gamebridge

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class MockPushEventDecoderTest {
    @Test fun `accepts only safe route and fields`() {
        val valid = """{"messageId":"one","route":"store","campaignId":"campaign","token":"secret"}""".toByteArray()
        assertEquals(PushPayload("one", "store", "campaign"), MockPushEventDecoder.decode(valid))
        assertNull(MockPushEventDecoder.decode("""{"messageId":"one","route":"https://bad"}""".toByteArray()))
        assertNull(MockPushEventDecoder.decode("""{"messageId":"one","route":"home","campaignId":42}""".toByteArray()))
        assertNull(MockPushEventDecoder.decode(ByteArray(BridgeProtocol.MAX_BYTES + 1)))
        assertNull(MockPushEventDecoder.decode(byteArrayOf(0xc3.toByte(), 0x28)))
    }
}
