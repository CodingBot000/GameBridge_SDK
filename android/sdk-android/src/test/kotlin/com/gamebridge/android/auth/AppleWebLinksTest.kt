package com.gamebridge.android.auth

import kotlin.test.*
import java.util.UUID

class AppleWebLinksTest {
    private val base="https://app.example.invalid/auth/apple"
    private val flow=UUID.randomUUID().toString()
    private val handle="$flow.${"h".repeat(43)}"
    @Test fun `only exact https return and current flow opaque handle are accepted`() {
        assertEquals(handle,AppleWebLinks.handle("$base?handle=$handle",base,flow))
        for(url in listOf("http://app.example.invalid/auth/apple?handle=$handle","https://evil.example.invalid/auth/apple?handle=$handle","$base/extra?handle=$handle","$base?handle=$handle&code=secret","$base?handle=$handle#access_token=secret","$base?code=secret","$base?handle=$handle&handle=$handle","$base?handle=${UUID.randomUUID()}.${"h".repeat(43)}"))assertNull(AppleWebLinks.handle(url,base,flow))
        assertNull(AppleWebLinks.handle("$base?handle=$handle",base,UUID.randomUUID().toString()))
    }
    @Test fun `authorization must be official Apple code form post with service and nonce`() {
        val url="https://appleid.apple.com/auth/authorize?client_id=com.example.web&response_type=code&response_mode=form_post&scope=name+email&redirect_uri=https%3A%2F%2Fauth.example.invalid%2Fv1%2Fauth%2Fapple-web%2Fcallback&state=${"s".repeat(43)}&nonce=${"n".repeat(43)}"
        assertTrue(AppleWebLinks.validAuthorization(url,"com.example.web"))
        for(bad in listOf(url.replace("appleid.apple.com","appleid.apple.com.evil.invalid"),url.replace("response_type=code","response_type=token"),url.replace("form_post","fragment"),url+"&client_id=wrong",url.replace("nonce=","bad=")))assertFalse(AppleWebLinks.validAuthorization(bad,"com.example.web"))
        assertFalse(AppleWebLinks.validAuthorization(url,"wrong-service"))
        assertFalse(AppleWebLinks.validReturn("myapp://callback"));assertFalse(AppleWebLinks.validReturn("https://localhost/callback"))
    }
}
