package com.gamebridge.config

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import org.slf4j.LoggerFactory
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.junit.jupiter.api.Test
import org.springframework.http.MediaType
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*
import org.springframework.test.web.servlet.setup.MockMvcBuilders
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController

@RestController
private class ValidationController {
    data class Input(@field:NotBlank val value: String)
    @PostMapping("/validation-test") fun post(@Valid @RequestBody input: Input) = input
    @PostMapping("/error-test") fun error(@RequestBody input: Input): Nothing = throw IllegalStateException(input.value)
}

class HttpInfrastructureTest {
    @Test fun `invalid inputs produce sanitized 400 and a request id`() {
        val mvc = MockMvcBuilders.standaloneSetup(ValidationController()).setControllerAdvice(ApiErrors())
            .addFilters<org.springframework.test.web.servlet.setup.StandaloneMockMvcBuilder>(RequestIdFilter()).build()
        for (body in listOf("{\"value\":\"\"}", "{")) {
            val result = mvc.perform(post("/validation-test").contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isBadRequest).andExpect(jsonPath("$.code").value("INVALID_ARGUMENT"))
                .andExpect(header().exists("X-Request-Id")).andReturn()
            val id = result.response.getHeader("X-Request-Id")!!
            check(result.response.contentAsString.contains(id))
        }
    }
    @Test fun `unexpected exception never exposes request secret in response or application error log`() {
        val secret = "synthetic-error-secret-93f4"
        val logger = LoggerFactory.getLogger(ApiErrors::class.java) as Logger
        val appender = ListAppender<ILoggingEvent>().apply { start() }
        logger.addAppender(appender)
        try {
            val mvc = MockMvcBuilders.standaloneSetup(ValidationController()).setControllerAdvice(ApiErrors())
                .addFilters<org.springframework.test.web.servlet.setup.StandaloneMockMvcBuilder>(RequestIdFilter()).build()
            val result = mvc.perform(post("/error-test").contentType(MediaType.APPLICATION_JSON)
                .header("Authorization", "Bearer $secret").content("{\"value\":\"$secret\"}"))
                .andExpect(status().isInternalServerError).andExpect(jsonPath("$.code").value("INTERNAL_ERROR"))
                .andReturn()
            check(!result.response.contentAsString.contains(secret))
            check(appender.list.isNotEmpty())
            check(appender.list.all { !it.formattedMessage.contains(secret) && it.throwableProxy == null })
        } finally {
            logger.detachAppender(appender)
            appender.stop()
        }
    }

}
