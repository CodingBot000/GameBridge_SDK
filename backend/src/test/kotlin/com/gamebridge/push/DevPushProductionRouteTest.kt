package com.gamebridge.push

import com.gamebridge.session.SessionService
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest
import org.springframework.http.MediaType
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.status

@WebMvcTest(DevPushController::class)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("production")
class DevPushProductionRouteTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean lateinit var sessions: SessionService
    @Test fun `production does not register development push endpoint`() {
        mvc.perform(post("/v1/dev/push/send").contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isNotFound)
    }
}
