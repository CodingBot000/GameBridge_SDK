package com.gamebridge.config

import org.springframework.context.annotation.Configuration
import org.springframework.core.env.Environment
import jakarta.annotation.PostConstruct

/** Prevent ambiguous profiles from ever silently enabling development routes. */
@Configuration
class EnvironmentPolicy(private val environment: Environment) {
    @PostConstruct
    fun validate() {
        val modes = environment.activeProfiles.filter { it in allowed }
        require(modes.size == 1) {
            "CONFIG_REQUIRED: select exactly one of local-mock, sandbox, production"
        }
    }

    companion object {
        private val allowed = setOf("local-mock", "sandbox", "production")
    }
}
