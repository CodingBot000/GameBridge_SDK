package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import com.nimbusds.jose.crypto.ECDSAVerifier
import com.nimbusds.jose.jwk.Curve
import com.nimbusds.jose.jwk.gen.ECKeyGenerator
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import java.nio.file.Files
import java.time.Instant
import java.util.Base64
import kotlin.test.*

class AppleWebConfigurationTest {
    @Test fun `server client secret is ES256 service bound short lived and redacted`() {
        val key=ECKeyGenerator(Curve.P_256).generate();val path=Files.createTempFile("gamebridge-synthetic-apple-",".p8")
        try {
            Files.writeString(path,"-----BEGIN PRIVATE KEY-----\n"+Base64.getMimeEncoder().encodeToString(key.toECPrivateKey().encoded)+"\n-----END PRIVATE KEY-----\n")
            val app=AppleWebApp("com.example.web","https://auth.example.invalid/v1/auth/apple-web/callback","https://app.example.invalid/auth/apple","TEAM000000","KEY0000000",path.toString())
            val now=Instant.now();val token=AppleHttpCodeExchanger(ObjectMapper()).clientSecret(app,now);val jwt=SignedJWT.parse(token)
            assertTrue(jwt.verify(ECDSAVerifier(key.toECPublicKey())));assertEquals("ES256",jwt.header.algorithm.name);assertEquals("KEY0000000",jwt.header.keyID)
            assertEquals("com.example.web",jwt.jwtClaimsSet.subject);assertEquals("TEAM000000",jwt.jwtClaimsSet.issuer);assertEquals(listOf("https://appleid.apple.com"),jwt.jwtClaimsSet.audience)
            assertEquals(300,jwt.jwtClaimsSet.expirationTime.toInstant().epochSecond-jwt.jwtClaimsSet.issueTime.toInstant().epochSecond)
            assertFalse(app.toString().contains(path.toString()))
        }finally{Files.delete(path)}
    }
    @Test fun `unsafe redirects absent configuration and key errors are sanitized`() {
        for(url in listOf("http://app.example.invalid/callback","https://127.0.0.1/callback","https://localhost/callback","https://u:secret@app.example.invalid/callback","https://app.example.invalid/callback?next=x","https://app.example.invalid/callback#x")) assertFalse(validAppleHttps(url))
        assertFailsWith<AuthFlowException>{AppleWebSettings.parse(null,ObjectMapper()).get("app")}
        val error=assertFailsWith<AuthFlowException>{AppleHttpCodeExchanger(ObjectMapper()).clientSecret(AppleWebApp("service","callback","return","team","key","/synthetic-private-secret-key.p8"))}
        assertEquals("CONFIG_REQUIRED",error.message);assertNull(error.cause)
        val parse=assertFailsWith<IllegalArgumentException>{AppleWebSettings.parse("{\"private-secret\":true}",ObjectMapper())};assertFalse(parse.toString().contains("private-secret"));assertNull(parse.cause)
    }
}
