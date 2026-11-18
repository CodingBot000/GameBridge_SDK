package com.gamebridge.auth

import com.gamebridge.session.SessionService
import com.gamebridge.session.SessionTokens
import jakarta.servlet.http.HttpServletRequest
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.context.annotation.Profile
import org.springframework.http.HttpHeaders
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Service
import org.springframework.transaction.support.TransactionTemplate
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController
import java.net.URI
import java.net.URLDecoder
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.util.Base64
import java.util.UUID

internal fun appleHash(value:String)=MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
private fun appleRandom()=Base64.getUrlEncoder().withoutPadding().encodeToString(ByteArray(32).also {SecureRandom().nextBytes(it)})
private fun appleFail():Nothing=throw AuthFlowException("AUTH_FAILED")
data class AppleWebStartInput(@field:NotBlank val appId:String,@field:NotBlank val verifierChallenge:String) {override fun toString()="AppleWebStartInput([redacted])"}
data class AppleWebStartOutput(val flowId:String,val authorizationUrl:String,val returnUri:String,val expiresAt:String) {override fun toString()="AppleWebStartOutput([redacted])"}
data class AppleWebCompleteInput(@field:NotBlank val appId:String,val flowId:UUID,@field:NotBlank val handle:String,@field:NotBlank val verifier:String) {override fun toString()="AppleWebCompleteInput([redacted])"}
data class AppleWebCompleteOutput(val status:String,val session:SessionTokens?=null) {override fun toString()="AppleWebCompleteOutput([redacted])"}
private data class AppleFlowRow(val id:UUID,val appId:String,val servicesId:String,val callbackUri:String,val returnUri:String,val nonceHash:ByteArray,val verifierChallenge:String,val stage:String,val active:Boolean,val handleActive:Boolean,val consumed:Boolean,val handleHash:ByteArray?,val issuer:String?,val subject:String?,val audience:String?)
@Service
@Profile("sandbox","production")
class AppleWebFlow(private val db:JdbcTemplate,private val tx:TransactionTemplate,private val settings:AppleWebSettings,
                   private val audience:AudiencePolicy,private val exchanger:AppleCodeExchanger,private val verifier:IdentityVerifier,private val sessions:SessionService) {
    private fun rows(where:String,vararg args:Any)=db.query("""SELECT *,expires_at>now() AS active,handle_expires_at>now() AS handle_active FROM apple_web_flows WHERE $where""",{rs,_->
        AppleFlowRow(rs.getObject("id",UUID::class.java),rs.getString("app_id"),rs.getString("services_id"),rs.getString("callback_uri"),rs.getString("return_uri"),rs.getBytes("nonce_hash"),rs.getString("verifier_challenge"),rs.getString("stage"),rs.getBoolean("active"),rs.getBoolean("handle_active"),rs.getTimestamp("consumed_at")!=null,rs.getBytes("handle_hash"),rs.getString("issuer"),rs.getString("subject"),rs.getString("audience"))
    },*args).firstOrNull()
    fun start(input:AppleWebStartInput):AppleWebStartOutput {
        if(!input.verifierChallenge.matches(Regex("[A-Za-z0-9_-]{43}")))appleFail()
        val app=settings.get(input.appId)
        if(app.servicesId !in audience.allowed(input.appId,IdentityProvider.APPLE))throw AuthFlowException("CONFIG_REQUIRED")
        exchanger.preflight(app)
        val id=UUID.randomUUID();val state=appleRandom();val nonce=appleRandom();val expiry=Instant.now().plusSeconds(300)
        db.update("""INSERT INTO apple_web_flows(id,app_id,services_id,callback_uri,return_uri,state_hash,nonce_hash,verifier_challenge,expires_at) VALUES(?,?,?,?,?,?,?,?,?)""",
            id,input.appId,app.servicesId,app.callbackUri,app.returnUri,appleHash(state),appleHash(nonce),input.verifierChallenge,java.sql.Timestamp.from(expiry))
        val query=mapOf("client_id" to app.servicesId,"redirect_uri" to app.callbackUri,"response_type" to "code","response_mode" to "form_post","scope" to "name email","state" to state,"nonce" to nonce)
            .entries.joinToString("&"){appleForm(it.key)+"="+appleForm(it.value)}
        return AppleWebStartOutput(id.toString(),"https://appleid.apple.com/auth/authorize?$query",app.returnUri,expiry.toString())
    }
    /** Form is parsed from bounded raw body, not servlet parameters consumed by the body-limit filter. */
    fun callback(form:String):URI {
        val values=try {
            require(form.length in 1..65536)
            val entries=form.split('&').map {part ->val pair=part.split('=',limit=2);require(pair.size==2);URLDecoder.decode(pair[0],Charsets.UTF_8) to URLDecoder.decode(pair[1],Charsets.UTF_8)}
            require(entries.map {it.first}.distinct().size==entries.size)
            entries.toMap()
        }catch(_:Exception){appleFail()}
        val state=values["state"]?.takeIf {it.matches(Regex("[A-Za-z0-9_-]{43}"))}?:appleFail()
        val row=rows("state_hash=?",appleHash(state))?:appleFail()
        if(row.stage!="STARTED" || !row.active)throw AuthFlowException(if(row.stage!="STARTED")"AUTH_REPLAY_DETECTED" else "AUTH_FAILED")
        val app=settings.get(row.appId)
        if(app.servicesId!=row.servicesId || app.callbackUri!=row.callbackUri || app.returnUri!=row.returnUri)appleFail()
        val error=values["error"];val code=values["code"]
        if(error==null && (code.isNullOrBlank() || code.length>8192))appleFail()
        if(error!=null && code!=null)appleFail()
        // Claim before network I/O; each code is consumed across all flows, even if Apple later rejects it.
        try {
            val claimed=db.update("UPDATE apple_web_flows SET stage='EXCHANGING',code_hash=? WHERE id=? AND stage='STARTED' AND expires_at>now()",
                code?.let(::appleHash),row.id)
            if(claimed!=1)throw AuthFlowException("AUTH_REPLAY_DETECTED")
        }catch(_:org.springframework.dao.DuplicateKeyException){throw AuthFlowException("AUTH_REPLAY_DETECTED")}
        var identity:VerifiedIdentity?=null
        val stage=if(error!=null) {if(error=="access_denied")"CANCELED" else "FAILED"} else try {
            val token=exchanger.exchange(app,code!!)
            identity=verifier.verify(IdentityProvider.APPLE,token,setOf(app.servicesId),row.nonceHash)
            "READY"
        }catch(_:IdentityVerificationException){"FAILED"}catch(_:AuthFlowException){"FAILED"}
        val handle="${row.id}.${appleRandom()}"
        val updated=db.update("""UPDATE apple_web_flows SET stage=?,handle_hash=?,handle_expires_at=LEAST(expires_at,now()+interval '60 seconds'),issuer=?,subject=?,audience=? WHERE id=? AND stage='EXCHANGING' AND expires_at>now()""",
            stage,appleHash(handle),identity?.issuer,identity?.subject,identity?.audience,row.id)
        if(updated!=1)appleFail()
        return URI(row.returnUri+"?handle="+appleForm(handle))
    }
    fun complete(input:AppleWebCompleteInput):AppleWebCompleteOutput {
        if(!input.verifier.matches(Regex("[A-Za-z0-9_-]{43}")) || !input.handle.matches(Regex("${input.flowId}\\.[A-Za-z0-9_-]{43}")))appleFail()
        return tx.execute {
            val row=rows("id=? FOR UPDATE",input.flowId)?:appleFail()
            if(row.appId!=input.appId)appleFail()
            if(row.consumed)throw AuthFlowException("AUTH_REPLAY_DETECTED")
            val challenge=Base64.getUrlEncoder().withoutPadding().encodeToString(appleHash(input.verifier))
            if(!row.active || !row.handleActive || row.stage !in setOf("READY","CANCELED","FAILED") ||
                !MessageDigest.isEqual(challenge.toByteArray(),row.verifierChallenge.toByteArray()) ||
                row.handleHash==null || !MessageDigest.isEqual(appleHash(input.handle),row.handleHash))appleFail()
            val app=settings.get(row.appId)
            if(app.servicesId!=row.servicesId || app.callbackUri!=row.callbackUri || app.returnUri!=row.returnUri || row.servicesId !in audience.allowed(row.appId,IdentityProvider.APPLE))appleFail()
            db.update("UPDATE apple_web_flows SET consumed_at=now() WHERE id=?",row.id)
            if(row.stage=="READY") AppleWebCompleteOutput("COMPLETE",sessions.createVerified(VerifiedIdentity(IdentityProvider.APPLE,row.issuer?:appleFail(),row.subject?:appleFail(),row.audience?:appleFail()),row.appId,null))
            else AppleWebCompleteOutput(row.stage)
        }!!
    }
}
@RestController
@Profile("sandbox","production")
class AppleWebController(private val flow:AppleWebFlow) {
    @PostMapping("/v1/auth/apple-web/start") fun start(@Valid @RequestBody input:AppleWebStartInput):ResponseEntity<AppleWebStartOutput> = ResponseEntity.ok().header(HttpHeaders.CACHE_CONTROL,"no-store").body(flow.start(input))
    @PostMapping("/v1/auth/apple-web/callback") fun callback(request:HttpServletRequest):ResponseEntity<Void> {
        if(request.contentType?.substringBefore(';')?.lowercase()!="application/x-www-form-urlencoded")appleFail()
        val bytes=request.inputStream.readNBytes(65537)
        if(bytes.size>65536)appleFail()
        val body=bytes.toString(Charsets.UTF_8)
        return ResponseEntity.status(HttpStatus.SEE_OTHER).location(flow.callback(body)).header(HttpHeaders.CACHE_CONTROL,"no-store").header("Referrer-Policy","no-referrer").build()
    }
    @PostMapping("/v1/auth/apple-web/complete") fun complete(@Valid @RequestBody input:AppleWebCompleteInput):ResponseEntity<AppleWebCompleteOutput> = ResponseEntity.ok().header(HttpHeaders.CACHE_CONTROL,"no-store").body(flow.complete(input))
}
