package com.gamebridge.auth

import com.nimbusds.jose.*
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator
import com.nimbusds.jwt.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.context.annotation.*
import org.springframework.http.*
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder
import org.springframework.test.context.*
import org.springframework.test.annotation.DirtiesContext
import java.net.URI
import java.net.URLDecoder
import java.time.Instant
import java.util.*
import java.util.concurrent.*
import kotlin.test.*

private object AppleWebFixture {
    val key=RSAKeyGenerator(2048).generate()
    val badKey=RSAKeyGenerator(2048).generate()
    val codes=ConcurrentHashMap<String,String>()
}
@TestConfiguration
class AppleWebSyntheticConfiguration {
    @Bean @Primary fun appleWebVerifier()=IdentityVerifier(mapOf(IdentityProvider.APPLE to NimbusJwtDecoder.withPublicKey(AppleWebFixture.key.toRSAPublicKey()).build()))
    @Bean @Primary fun appleWebExchange()=AppleCodeExchanger {_,code->AppleWebFixture.codes[code]?:throw AuthFlowException("NETWORK_UNAVAILABLE")}
}
@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("sandbox")
@Import(AppleWebSyntheticConfiguration::class)
@DirtiesContext(classMode=DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
@EnabledIfEnvironmentVariable(named="GAMEBRIDGE_RUN_AUTH_DB_TESTS",matches="true")
class AppleWebAuthHttpTest {
    @Autowired lateinit var rest:TestRestTemplate
    @Autowired lateinit var db:JdbcTemplate
    companion object {
        @JvmStatic @DynamicPropertySource fun properties(registry:DynamicPropertyRegistry) {
            registry.add("DATABASE_URL"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_URL"))}
            registry.add("DATABASE_USERNAME"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_USER"))}
            registry.add("DATABASE_PASSWORD"){requireNotNull(System.getenv("GAMEBRIDGE_TEST_DB_PASSWORD"))}
            registry.add("GAMEBRIDGE_AUTH_AUDIENCES_JSON"){"""{"web-a":{"APPLE":["com.example.web","com.example.ios"]},"web-b":{"APPLE":["com.example.other"]}}"""}
            registry.add("GAMEBRIDGE_APPLE_WEB_CONFIG_JSON"){"""{"web-a":{"servicesId":"com.example.web","callbackUri":"https://auth.example.invalid/v1/auth/apple-web/callback","returnUri":"https://app.example.invalid/auth/apple","teamId":"TEAM000000","keyId":"KEY0000000","privateKeyPath":"/synthetic/not-a-real-key.p8"}}"""}
        }
    }
    @org.junit.jupiter.api.BeforeEach fun disableTestRedirects() {
        rest.restTemplate.requestFactory=object:org.springframework.http.client.SimpleClientHttpRequestFactory() {
            override fun prepareConnection(connection:java.net.HttpURLConnection,httpMethod:String) {
                super.prepareConnection(connection,httpMethod);connection.instanceFollowRedirects=false
            }
        }
    }
    private val verifier="v".repeat(43)
    private fun start():Map<*,*> = rest.postForEntity("/v1/auth/apple-web/start",mapOf("appId" to "web-a","verifierChallenge" to Base64.getUrlEncoder().withoutPadding().encodeToString(appleHash(verifier))),Map::class.java).also {assertEquals(200,it.statusCode.value())}.body!!
    private fun query(url:String)=URI(url).rawQuery.split('&').associate {val p=it.split('=',limit=2);URLDecoder.decode(p[0],Charsets.UTF_8) to URLDecoder.decode(p[1],Charsets.UTF_8)}
    private fun code(start:Map<*,*>,variant:String="valid"):String {
        val q=query(start["authorizationUrl"] as String);val jwt=SignedJWT(JWSHeader(JWSAlgorithm.RS256),JWTClaimsSet.Builder()
            .issuer(if(variant=="issuer")"https://evil.example.invalid" else "https://appleid.apple.com")
            .audience(if(variant=="audience")"com.example.ios" else "com.example.web").subject("apple-test-subject")
            .claim("nonce",if(variant=="nonce")"wrong" else q["nonce"])
            .expirationTime(Date.from(Instant.now().plusSeconds(if(variant=="expired")-60 else 60))).build())
        jwt.sign(RSASSASigner(if(variant=="signature")AppleWebFixture.badKey else AppleWebFixture.key))
        return UUID.randomUUID().toString().also {AppleWebFixture.codes[it]=jwt.serialize()}
    }
    private fun callback(start:Map<*,*>,code:String?=null,error:String?=null,state:String=query(start["authorizationUrl"] as String)["state"]!!):ResponseEntity<String> {
        val body=mapOf("state" to state)+ (if(error!=null)mapOf("error" to error) else mapOf("code" to (code?:code(start))))
        return rest.exchange("/v1/auth/apple-web/callback",HttpMethod.POST,HttpEntity(body.entries.joinToString("&"){appleForm(it.key)+"="+appleForm(it.value)},HttpHeaders().apply {contentType=MediaType.APPLICATION_FORM_URLENCODED}),String::class.java)
    }
    private fun handle(response:ResponseEntity<String>):String {
        assertEquals(303,response.statusCode.value());assertEquals("no-store",response.headers.cacheControl);assertEquals("no-referrer",response.headers.getFirst("Referrer-Policy"))
        val url=response.headers.location!!.toString();val q=query(url);assertEquals(setOf("handle"),q.keys);assertTrue(url.startsWith("https://app.example.invalid/auth/apple?"));assertTrue(response.body.isNullOrEmpty());return q["handle"]!!
    }
    private fun complete(start:Map<*,*>,handle:String,secret:String=verifier,app:String="web-a")=rest.postForEntity("/v1/auth/apple-web/complete",mapOf("appId" to app,"flowId" to start["flowId"],"handle" to handle,"verifier" to secret),Map::class.java)
    private fun sessionCount()=db.queryForObject("SELECT count(*) FROM sessions WHERE app_scope='web-a'",Long::class.java)!!
    @Test fun `verified callback mints only at one time Native redemption and uses existing ledger session`() {
        val s=start();val q=query(s["authorizationUrl"] as String);assertEquals("code",q["response_type"]);assertEquals("form_post",q["response_mode"])
        val before=sessionCount();val h=handle(callback(s));assertEquals(before,sessionCount())
        assertEquals(401,complete(s,h,"x".repeat(43)).statusCode.value());assertEquals(401,complete(s,h,app="web-b").statusCode.value())
        val out=complete(s,h);assertEquals(200,out.statusCode.value());assertEquals("COMPLETE",out.body!!["status"])
        val session=out.body!!["session"] as Map<*,*>;assertEquals(before+1,sessionCount());assertEquals(409,complete(s,h).statusCode.value())
        val headers=HttpHeaders().apply{setBearerAuth(session["accessToken"] as String)}
        assertEquals(200,rest.exchange("/v1/me",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
        assertEquals(200,rest.exchange("/v1/purchases/bindings",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
        assertEquals(200,rest.exchange("/v1/entitlements",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
        val refresh=rest.postForEntity("/v1/auth/refresh",mapOf("refreshToken" to session["refreshToken"]),Map::class.java);assertEquals(200,refresh.statusCode.value())
        headers.setBearerAuth(refresh.body!!["accessToken"] as String)
        assertEquals(200,rest.exchange("/v1/auth/logout",HttpMethod.POST,HttpEntity(emptyMap<String,String>(),headers),Map::class.java).statusCode.value())
        assertEquals(401,rest.exchange("/v1/me",HttpMethod.GET,HttpEntity<Void>(headers),Map::class.java).statusCode.value())
    }
    @Test fun `forged duplicate and expired state plus reused code are rejected`() {
        val s=start();val c=code(s)
        assertEquals(401,callback(s,c,state="z".repeat(43)).statusCode.value())
        handle(callback(s,c));assertEquals(409,callback(s,c).statusCode.value())
        val other=start();assertEquals(409,callback(other,c).statusCode.value())
        db.update("UPDATE apple_web_flows SET expires_at=now()-interval '1 second' WHERE id=?",UUID.fromString(other["flowId"] as String))
        assertEquals(401,callback(other,code(other)).statusCode.value())
    }
    @Test fun `invalid Apple JWT signature issuer service audience nonce expiry never creates a session`() {
        val before=sessionCount()
        for(variant in listOf("signature","issuer","audience","nonce","expired")) {
            val s=start();val h=handle(callback(s,code(s,variant)));val out=complete(s,h)
            assertEquals(200,out.statusCode.value());assertEquals("FAILED",out.body!!["status"]);assertNull(out.body!!["session"])
        }
        assertEquals(before,sessionCount())
    }
    @Test fun `cancel network error stale app restart and expired completion fail closed`() {
        val before=sessionCount();val canceled=start();val h=handle(callback(canceled,error="access_denied"))
        assertEquals("CANCELED",complete(canceled,h).body!!["status"])
        val failed=start();val failedHandle=handle(callback(failed,"synthetic-network-error"));assertEquals("FAILED",complete(failed,failedHandle).body!!["status"])
        val expired=start();val old=handle(callback(expired));assertEquals(401,complete(start(),old).statusCode.value())
        db.update("UPDATE apple_web_flows SET handle_expires_at=now()-interval '1 second' WHERE id=?",UUID.fromString(expired["flowId"] as String))
        assertEquals(401,complete(expired,old).statusCode.value());assertEquals(before,sessionCount())
    }
    @Test fun `concurrent completion issues exactly one existing session`() {
        val s=start();val h=handle(callback(s));val before=sessionCount();val pool=Executors.newFixedThreadPool(2)
        try {
            val tasks=(1..2).map {pool.submit(Callable {complete(s,h).statusCode.value()})}
            assertEquals(listOf(200,409),tasks.map {it.get(15,TimeUnit.SECONDS)}.sorted());assertEquals(before+1,sessionCount())
        }finally{pool.shutdownNow()}
    }
    @Test fun `callback requires form content and unique state keys`() {
        val s=start();val state=query(s["authorizationUrl"] as String)["state"]!!
        assertEquals(401,rest.postForEntity("/v1/auth/apple-web/callback",mapOf("state" to state,"code" to code(s)),Map::class.java).statusCode.value())
        val headers=HttpHeaders().apply{contentType=MediaType.APPLICATION_FORM_URLENCODED}
        assertEquals(401,rest.exchange("/v1/auth/apple-web/callback",HttpMethod.POST,HttpEntity("state=$state&state=$state&code=synthetic",headers),Map::class.java).statusCode.value())
    }
}
