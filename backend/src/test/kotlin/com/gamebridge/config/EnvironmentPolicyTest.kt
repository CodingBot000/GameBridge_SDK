package com.gamebridge.config

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.springframework.mock.env.MockEnvironment

class EnvironmentPolicyTest {
    @Test fun `explicit single mode is accepted`() {
        for (mode in listOf("local-mock", "sandbox", "production")) {
            EnvironmentPolicy(MockEnvironment().withProperty("spring.profiles.active", mode)).validate()
        }
    }

    @Test fun `missing and mixed modes fail closed`() {
        assertThrows<IllegalArgumentException> { EnvironmentPolicy(MockEnvironment()).validate() }
        assertThrows<IllegalArgumentException> {
            EnvironmentPolicy(MockEnvironment().withProperty("spring.profiles.active", "local-mock,sandbox")).validate()
        }
    }
}
