package com.gamebridge.auth

import com.gamebridge.session.SessionService
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Import
import org.springframework.context.annotation.Primary
import org.springframework.http.*
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.context.DynamicPropertyRegistry
import org.springframework.test.context.DynamicPropertySource
import java.time.Instant
import java.util.*
import kotlin.test.*

private object FacebookSigningFixture {val key=RSAKeyGenerator(2048).generate()}
@TestConfiguration
class FacebookSyntheticConfiguration {
    @Bean @Primary fun facebookJwtFixture()=IdentityVerifier(mapOf(IdentityProvider.FACEBOOK to NimbusJwtDecoder.withPublicKey(FacebookSigningFixture.key.toRSAPublicKey()).build()))
    @Bean @Primary fun facebookAccessFixture(mapper:com.fasterxml.jackson.databind.ObjectMapper)=FacebookAccessVerifier(
        mapOf("fb-a" to FacebookApp("123","synthetic-meta-app-secret",setOf("public_profile")),"fb-b" to FacebookApp("456","synthetic-meta-app-secret",setOf("public_profile"))),
        FacebookDebugLookup {token,_->
            if(token=="network-failure")throw java.io.IOException()
            mapper.readTree(if(token=="classic-valid") """{"data":{"app_id":"123","user_id":"1001","type":"USER","is_valid":true,"expires_at":1999999999,"data_access_expires_at":1999999999,"scopes":["public_profile"]}}""" else """{"data":{"is_valid":false}}""")
        })
}
@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@Import(FacebookSyntheticConfiguration::class)
@org.springframework.test.annotation.DirtiesContext(classMode=org.springframework.test.annotation.DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
@EnabledIfEnvironmentVariable(named="GAMEBRIDGE_RUN_AUTH_DB_TESTS",matches="true")
class FacebookAuthHttpTest {
    @Autowired lateinit var rest:TestRestTemplate
    @Autowired lateinit var db:JdbcTemplate
    @Autowired lateinit var sessions:SessionService
    companion object {
        @JvmStatic @DynamicPropertySource fun properties(registry:DynamicPropertyRegistry) {
            registry.add("DATABASE_URL"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL"))}
            registry.add("DATABASE_USERNAME"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER"))}
            registry.add("DATABASE_PASSWORD"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))}
            registry.add("GAMEBRIDGE_AUTH_AUDIENCES_JSON"){"""{"fb-a":{"FACEBOOK":["123"],"GOOGLE":["server"],"APPLE":["apple"]},"fb-b":{"FACEBOOK":["456"]}}"""}
        }
    }
    private fun challenge(kind:String,app:String="fb-a"):Map<*,*> = rest.postForEntity("/v1/auth/challenges",mapOf("appId" to app,"provider" to "FACEBOOK","proofType" to kind),Map::class.java).also{assertEquals(200,it.statusCode.value())}.body!!
    private fun exchange(c:Map<*,*>,kind:String,token:String,provider:String="FACEBOOK",extra:Map<String,Any> = emptyMap()) = rest.postForEntity("/v1/auth/exchange",mapOf("challengeId" to c["challengeId"],"provider" to provider,"proofType" to kind,(if(kind=="FACEBOOK_ACCESS_TOKEN")"accessToken" else "idToken") to token)+extra,Map::class.java)
    private fun signed(c:Map<*,*>,nonce:String=c["nonce"] as String):String {
        val jwt=SignedJWT(JWSHeader(JWSAlgorithm.RS256),JWTClaimsSet.Builder().issuer("https://www.facebook.com").audience("123").subject("1001").claim("nonce",nonce).expirationTime(Date.from(Instant.now().plusSeconds(60))).build())
        jwt.sign(RSASSASigner(FacebookSigningFixture.key));return jwt.serialize()
    }
    @Test fun `classic and limited share only verified provider identity not an email across providers`() {
        val google=sessions.createVerified(VerifiedIdentity(IdentityProvider.GOOGLE,"https://accounts.google.com","1001","server"),"fb-a","same@example.invalid")
        val c=challenge("FACEBOOK_ACCESS_TOKEN");val classic=exchange(c,"FACEBOOK_ACCESS_TOKEN","classic-valid",extra=mapOf("displayName" to "same@example.invalid"))
        assertEquals(200,classic.statusCode.value());assertNotEquals(google.userId,classic.body!!["userId"])
        assertEquals(409,exchange(c,"FACEBOOK_ACCESS_TOKEN","classic-valid").statusCode.value())
        // Classic is a reusable bearer credential: fresh challenge + new Meta validity check is required.
        val fresh=exchange(challenge("FACEBOOK_ACCESS_TOKEN"),"FACEBOOK_ACCESS_TOKEN","classic-valid");assertEquals(200,fresh.statusCode.value());assertEquals(classic.body!!["userId"],fresh.body!!["userId"])
        val limitedChallenge=challenge("FACEBOOK_LIMITED_ID_TOKEN");val limited=exchange(limitedChallenge,"FACEBOOK_LIMITED_ID_TOKEN",signed(limitedChallenge));assertEquals(200,limited.statusCode.value());assertEquals(classic.body!!["userId"],limited.body!!["userId"])
        val headers=HttpHeaders().apply{setBearerAuth(limited.body!!["accessToken"] as String)}
        val wallet=rest.exchange("/v1/entitlements",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java)
        assertEquals(200,wallet.statusCode.value());assertEquals(limited.body!!["userId"],wallet.body!!["userId"]);assertEquals("0",wallet.body!!["coinBalance"])
        assertEquals(200,rest.exchange("/v1/purchases/bindings",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
        val refreshed=rest.postForEntity("/v1/auth/refresh",mapOf("refreshToken" to limited.body!!["refreshToken"]),Map::class.java);assertEquals(200,refreshed.statusCode.value())
        headers.setBearerAuth(refreshed.body!!["accessToken"] as String)
        assertEquals(200,rest.exchange("/v1/auth/logout",HttpMethod.POST,HttpEntity(emptyMap<String,String>(),headers),Map::class.java).statusCode.value())
        assertEquals(401,rest.exchange("/v1/me",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
    }
    @Test fun `wrong app wrong nonce mixed proof and downgrade cannot mint session`() {
        assertEquals(401,exchange(challenge("FACEBOOK_ACCESS_TOKEN","fb-b"),"FACEBOOK_ACCESS_TOKEN","classic-valid").statusCode.value())
        val c=challenge("FACEBOOK_LIMITED_ID_TOKEN")
        assertEquals(401,exchange(c,"FACEBOOK_ACCESS_TOKEN","classic-valid").statusCode.value())
        assertEquals(401,exchange(c,"FACEBOOK_LIMITED_ID_TOKEN",signed(c,"wrong")).statusCode.value())
        assertEquals(401,exchange(c,"FACEBOOK_LIMITED_ID_TOKEN","classic-valid").statusCode.value())
        assertEquals(401,exchange(c,"FACEBOOK_ACCESS_TOKEN","classic-valid",extra=mapOf("idToken" to signed(c))).statusCode.value())
        assertEquals(false,db.queryForObject("SELECT used_at IS NOT NULL FROM auth_challenges WHERE id=?",Boolean::class.java,UUID.fromString(c["challengeId"] as String)))
    }
    @Test fun `expired challenge revoked proof and transport errors are sanitized`() {
        val expired=challenge("FACEBOOK_ACCESS_TOKEN");db.update("UPDATE auth_challenges SET expires_at=now()-interval '1 second' WHERE id=?",UUID.fromString(expired["challengeId"] as String))
        assertEquals(401,exchange(expired,"FACEBOOK_ACCESS_TOKEN","classic-valid").statusCode.value())
        val c=challenge("FACEBOOK_ACCESS_TOKEN");assertEquals(401,exchange(c,"FACEBOOK_ACCESS_TOKEN","revoked-proof").statusCode.value())
        val response=exchange(c,"FACEBOOK_ACCESS_TOKEN","network-failure");assertEquals(503,response.statusCode.value());assertEquals("NETWORK_UNAVAILABLE",response.body!!["code"]);assertFalse(response.body.toString().contains("network-failure"))
    }
}
