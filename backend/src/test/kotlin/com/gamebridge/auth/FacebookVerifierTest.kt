package com.gamebridge.auth

import com.fasterxml.jackson.databind.ObjectMapper
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import java.security.MessageDigest
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import java.util.Date
import kotlin.test.*

class FacebookVerifierTest {
    private val mapper=ObjectMapper()
    private val now=Instant.parse("2026-11-19T00:00:00Z")
    private val app=FacebookApp("123","server-secret-test",setOf("public_profile"))
    @Test fun `classic checks Meta validity app user permissions and expiries without JWT nonce`() {
        val valid="""{"data":{"app_id":"123","user_id":"456","type":"USER","is_valid":true,"expires_at":1999999999,"data_access_expires_at":1999999999,"scopes":["public_profile"]}}"""
        val root=mapper.readTree(valid)
        fun verifier(value:com.fasterxml.jackson.databind.JsonNode)=FacebookAccessVerifier(mapOf("game" to app),FacebookDebugLookup {_,_->value},Clock.fixed(now,ZoneOffset.UTC))
        val result=verifier(root).verify("game","opaque-fb-token",setOf("123"));assertEquals("123:456",result.identity.subject);assertEquals(32,result.proofHash.size)
        for ((field,bad) in listOf("app_id" to "999","user_id" to "","type" to "APP")) {
            val changed=root.deepCopy<com.fasterxml.jackson.databind.node.ObjectNode>();(changed["data"] as com.fasterxml.jackson.databind.node.ObjectNode).put(field,bad)
            assertFailsWith<IdentityVerificationException>{verifier(changed).verify("game","opaque-fb-token",setOf("123"))}
        }
        for(field in listOf("expires_at","data_access_expires_at")) {
            val changed=root.deepCopy<com.fasterxml.jackson.databind.node.ObjectNode>();(changed["data"] as com.fasterxml.jackson.databind.node.ObjectNode).put(field,now.epochSecond)
            assertFailsWith<IdentityVerificationException>{verifier(changed).verify("game","opaque-fb-token",setOf("123"))}
        }
        for (changed in listOf(valid.replace("true","false"),valid.replace("\"public_profile\"","\"email\"")))assertFailsWith<IdentityVerificationException>{verifier(mapper.readTree(changed)).verify("game","opaque",setOf("123"))}
        assertFalse(app.toString().contains("server-secret-test"))
    }
    @Test fun `limited JWT requires signature issuer audience nonce expiry and stays separate from classic`() {
        val key=RSAKeyGenerator(2048).generate();val other=RSAKeyGenerator(2048).generate()
        val verifier=IdentityVerifier(mapOf(IdentityProvider.FACEBOOK to NimbusJwtDecoder.withPublicKey(key.toRSAPublicKey()).build()),Clock.systemUTC())
        val nonce=MessageDigest.getInstance("SHA-256").digest("nonce".toByteArray())
        fun token(issuer:String="https://www.facebook.com",audience:String="123",value:String="nonce",expiry:Instant=Instant.now().plusSeconds(60),wrongKey:Boolean=false):String {
            val jwt=SignedJWT(JWSHeader(JWSAlgorithm.RS256),JWTClaimsSet.Builder().issuer(issuer).audience(audience).subject("456").claim("nonce",value).expirationTime(Date.from(expiry)).build())
            jwt.sign(RSASSASigner(if(wrongKey)other else key));return jwt.serialize()
        }
        assertEquals("123:456",verifier.verify(IdentityProvider.FACEBOOK,token(),setOf("123"),nonce).subject)
        for (bad in listOf("opaque-fb-access-token",token(issuer="https://accounts.google.com"),token(audience="999"),token(value="wrong"),token(expiry=Instant.EPOCH),token(wrongKey=true)))
            assertFailsWith<IdentityVerificationException>{verifier.verify(IdentityProvider.FACEBOOK,bad,setOf("123"),nonce)}
    }
    @Test fun `malformed or duplicate scope config never leaks secret in exception`() {
        for (raw in listOf("""{"secret":"server-secret-test""", """{"a":{"appId":"123","appSecret":"server-secret-test"},"b":{"appId":"123","appSecret":"secret2"}}""")) {
            val error=assertFailsWith<IllegalArgumentException>{FacebookAccessVerifier.settings(raw,mapper)};assertFalse(error.toString().contains("server-secret-test"));assertNull(error.cause)
        }
    }
}
