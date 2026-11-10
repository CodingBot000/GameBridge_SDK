package com.gamebridge.config

import org.junit.jupiter.api.Test
import com.gamebridge.session.SessionService
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest
import org.springframework.context.annotation.Import
import org.springframework.http.MediaType
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*

@WebMvcTest(HealthController::class)
@AutoConfigureMockMvc(addFilters = false)
@Import(ApiWebConfiguration::class)
class ApiWebConfigurationTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean lateinit var sessions: SessionService
    @Test fun `health defaults to json without accept header`() {
        mvc.perform(get("/health"))
            .andExpect(status().isOk)
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.status").value("UP"))
    }
}
