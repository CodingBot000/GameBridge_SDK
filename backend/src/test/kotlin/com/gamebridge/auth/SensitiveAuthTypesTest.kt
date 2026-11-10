package com.gamebridge.auth

import com.gamebridge.session.RefreshInput
import com.gamebridge.session.SessionTokens
import com.gamebridge.push.MockDeviceInput
import com.gamebridge.purchase.MockPurchaseInput
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.assertFalse

class SensitiveAuthTypesTest {
    @Test fun `request and response diagnostic strings do not expose secrets`() {
        val secret = "test-sensitive-token"
        val values = listOf(
            RefreshInput(secret), SessionTokens(secret, secret, "time", "user"),
            MockDeviceInput(secret, "MOCK", "MOCK", "app"), MockPurchaseInput("coins_100", secret, 1),
            ExchangeInput(UUID.randomUUID(), IdentityProvider.GOOGLE, secret), ChallengeOutput("id", secret, "time"),
        )
        values.forEach { assertFalse(it.toString().contains(secret)) }
    }
}
