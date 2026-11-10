package com.gamebridge.purchase

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

@WebMvcTest(MockXcodeStoreKitController::class)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("production")
class MockXcodeProductionRouteTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean lateinit var sessions: SessionService
    @Test fun `production has no xcode development grant endpoint`() {
        mvc.perform(post("/v1/dev/xcode-storekit/grant").contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isNotFound)
    }
}

@WebMvcTest(MockXcodeStoreKitController::class)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("sandbox")
class MockXcodeSandboxRouteTest {
    @Autowired lateinit var mvc: MockMvc
    @MockitoBean lateinit var sessions: SessionService
    @Test fun `sandbox has no xcode development grant endpoint`() {
        mvc.perform(post("/v1/dev/xcode-storekit/grant").contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isNotFound)
    }
}
