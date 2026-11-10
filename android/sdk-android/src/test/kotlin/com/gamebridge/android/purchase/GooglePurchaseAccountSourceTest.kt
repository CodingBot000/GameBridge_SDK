package com.gamebridge.android.purchase

import com.gamebridge.SdkFailure
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.*

class GooglePurchaseAccountSourceTest {
    @Test fun `only valid server binding forms an internal account`() {
        val user = UUID.randomUUID(); val binding = UUID.randomUUID()
        val account = parseGoogleBinding(user.toString(), """{"googleObfuscatedAccountId":"$binding"}""")
        assertEquals(user, account.userId); assertEquals(binding.toString(), account.obfuscatedAccountId)
        assertFalse(account.toString().contains(binding.toString()))
        assertEquals("BRIDGE_PROTOCOL_MISMATCH", assertFailsWith<SdkFailure> { parseGoogleBinding(user.toString(), "{}") }.code)
        assertEquals("BRIDGE_PROTOCOL_MISMATCH", assertFailsWith<SdkFailure> { parseGoogleBinding(user.toString(), """{"googleObfuscatedAccountId":"bad"}""") }.code)
    }
    @Test fun `store entitlement must match authenticated user`() {
        val user = UUID.randomUUID().toString()
        val body = """{"userId":"$user","premiumEnabled":true,"coinBalance":"100","revision":"1","updatedAt":"2026-01-01T00:00:00Z"}"""
        assertEquals("100", decodeGoogleEntitlements(body, user).coinBalance)
        assertEquals("BRIDGE_PROTOCOL_MISMATCH", assertFailsWith<SdkFailure> { decodeGoogleEntitlements(body, UUID.randomUUID().toString()) }.code)
    }
}
