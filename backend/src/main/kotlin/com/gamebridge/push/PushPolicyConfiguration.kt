package com.gamebridge.push

import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile

@Configuration
@Profile("local-mock", "sandbox", "production")
internal class PushPolicyConfiguration {
    @Bean fun pushRetryPolicy(@Value("\${gamebridge.push.max-retries:3}") maxRetries: Int,
                              @Value("\${gamebridge.push.initial-backoff-seconds:5}") initialSeconds: Long) = PushRetryPolicy(maxRetries, initialSeconds)
    @Bean @Profile("local-mock", "sandbox") fun devPushRateLimiter(@Value("\${gamebridge.push.dev-per-minute:10}") limit: Int) = DevPushRateLimiter(limit)
}
