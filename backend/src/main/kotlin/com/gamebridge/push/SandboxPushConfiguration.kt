package com.gamebridge.push

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.jdbc.core.JdbcTemplate

@Configuration
@Profile("sandbox")
internal class SandboxPushConfiguration {
    @Bean fun sandboxPushDispatcher(db: JdbcTemplate, cipher: TokenCipher, invalidator: PushTokenInvalidator, senders: ConfiguredPushSenders): PushDispatcher =
        PushDispatcher(db, cipher, invalidator, PushProviderClient { app, provider, token, content ->
            when (provider) {
                "FCM" -> senders.fcm(app).send(token, content)
                "APNS" -> senders.apns(app, ApnsEnvironment.SANDBOX).send(token, content)
                else -> PushAttempt(PushSendResult.FAILED, PushFailure.PERMANENT)
            }
        })
}
