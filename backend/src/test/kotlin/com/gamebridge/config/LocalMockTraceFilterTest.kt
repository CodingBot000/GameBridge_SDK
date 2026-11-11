package com.gamebridge.config

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import jakarta.servlet.FilterChain
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import org.springframework.boot.test.context.runner.ApplicationContextRunner
import org.springframework.mock.web.MockHttpServletRequest
import org.springframework.mock.web.MockHttpServletResponse
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class LocalMockTraceFilterTest {
    @Test fun `trace logs only allowlisted metadata and generated id`() {
        val logger = LoggerFactory.getLogger(LocalMockTraceFilter::class.java) as Logger
        val appender = ListAppender<ILoggingEvent>(); appender.start(); logger.addAppender(appender)
        try {
            val filter = LocalMockTraceFilter()
            val id = UUID.randomUUID().toString()
            val request = MockHttpServletRequest("POST", "/v1/dev/auth")
            request.setAttribute("requestId", id); request.queryString = "secret=SYNTHETIC_SECRET"
            request.addHeader("Authorization", "SYNTHETIC_SECRET"); request.setContent("SYNTHETIC_SECRET".toByteArray())
            val response = MockHttpServletResponse()
            filter.doFilter(request, response, FilterChain { _, result -> (result as MockHttpServletResponse).status = 200 })
            val message = appender.list.single().formattedMessage
            assertTrue(message.contains("operation=mock-auth")); assertTrue(message.contains("requestId=$id")); assertTrue(message.contains("status=200"))
            assertFalse(message.contains("SYNTHETIC_SECRET"))
            filter.doFilter(MockHttpServletRequest("GET", "/private/SYNTHETIC_SECRET"), MockHttpServletResponse(), FilterChain { _, _ -> })
            assertEquals(1, appender.list.size)
        } finally { logger.detachAppender(appender); appender.stop() }
    }
    @Test fun `trace requires both local mock profile and explicit opt in`() {
        val runner = ApplicationContextRunner().withUserConfiguration(LocalMockTraceFilter::class.java)
        runner.run { assertFalse(it.containsBean("localMockTraceFilter")) }
        runner.withPropertyValues("gamebridge.local-trace.enabled=true").run { assertFalse(it.containsBean("localMockTraceFilter")) }
        runner.withInitializer { it.environment.setActiveProfiles("local-mock") }.run { assertFalse(it.containsBean("localMockTraceFilter")) }
        runner.withInitializer { it.environment.setActiveProfiles("local-mock") }
            .withPropertyValues("gamebridge.local-trace.enabled=true").run { assertTrue(it.containsBean("localMockTraceFilter")) }
    }
}
