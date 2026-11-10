package com.gamebridge.android.push

import com.gamebridge.PushPayload
import org.junit.jupiter.api.Test
import kotlin.test.*

class AndroidPushHostAdapterTest {
    @Test fun `token rotation and opened routes are forwarded without arbitrary data`() {
        val tokens = mutableListOf<String>(); val opened = mutableListOf<Pair<PushPayload, Boolean>>(); var errors = 0
        val adapter = AndroidPushHostAdapter(tokens::add, { value, wasOpened -> opened.add(value to wasOpened) }, { errors++ })
        adapter.onNewToken("test-token-a"); adapter.onNewToken("test-token-b"); adapter.onNewToken("")
        assertEquals(listOf("test-token-a", "test-token-b"), tokens); assertEquals(1, errors)
        adapter.onNotificationOpened(mapOf("messageId" to "id", "route" to "store", "url" to "https://ignored.invalid"))
        adapter.onNotificationOpened(mapOf("messageId" to "other", "route" to "https://ignored.invalid"))
        assertEquals(listOf(PushPayload("id", "store", null) to true), opened)
    }
}
