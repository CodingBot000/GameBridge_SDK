package com.gamebridge.android.auth

import android.app.Activity
import android.content.Intent
import com.gamebridge.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.*
import java.time.Instant
import java.util.UUID

internal sealed interface NativeSocialCredential {
    class FacebookAccess(val value:String):NativeSocialCredential {override fun toString()="FacebookAccess([redacted])"}
    class AppleCompletion(val session:NativeSession):NativeSocialCredential {override fun toString()="AppleCompletion([redacted])"}
}
internal interface SocialCredentialGateway {
    val binding:String
    fun attach(activity:Activity)
    fun detach()
    suspend fun authorize(challenge:AuthChallenge?):NativeSocialCredential
    fun cancel()
    fun logout()
    fun activityResult(requestCode:Int,resultCode:Int,data:Intent?):Boolean=false
    fun redirect(url:String):Boolean=false
}
@Serializable private class SocialStored(val appId:String,val mode:String,val backend:String,val provider:String,val settings:String,val session:NativeSession) {
    override fun toString()="SocialStored([redacted])"
}
internal class SocialAuthProvider(private val config:GameBridgeConfig,private val name:String,private val store:TokenStore,
                                  val gateway:SocialCredentialGateway,
                                  private val request:suspend(String,String,String?,String?)->BackendResponse = BackendClient(config).let { client -> {path,method,body,token ->client.request(path,method,body,token)} }):BackendSessionAccess {
    override val uiGate=Mutex()
    private val sessionLock=Mutex()
    private val state=Any()
    private var generation=0L
    private var closed=false
    private val json=Json {ignoreUnknownKeys=true}
    init {if(config.mode!=ProviderMode.PLATFORM_SANDBOX || name !in setOf("FACEBOOK","APPLE"))throw SdkFailure("UNSUPPORTED_PROVIDER");config.validate()}
    override fun usesConfiguration(config:GameBridgeConfig)=this.config==config
    override fun attachHost(activity:Activity)=gateway.attach(activity)
    override fun detachHost()=gateway.detach()
    private fun epoch()=synchronized(state){generation}
    private fun requireEpoch(value:Long) {if(closed || generation!=value)throw SdkFailure("CANCELED")}
    private inline fun <reified T> decode(value:String):T = try {json.decodeFromString<T>(value)}catch(_:Exception){throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")}
    private fun validate(value:NativeSession) {
        if(runCatching {UUID.fromString(value.userId).toString()==value.userId && Instant.parse(value.expiresAt)!=null}.getOrDefault(false).not() || value.accessToken.isBlank() || value.refreshToken.isBlank())throw SdkFailure("AUTH_FAILED")
    }
    private fun load():NativeSession? = store.load()?.let {
        val saved=try {json.decodeFromString<SocialStored>(it)}catch(_:Exception){throw SdkFailure("SESSION_EXPIRED")}
        if(saved.appId!=config.appId || saved.mode!=config.mode.name || saved.backend!=config.backendBaseUrl || saved.provider!=name || saved.settings!=gateway.binding)throw SdkFailure("SESSION_EXPIRED")
        validate(saved.session);saved.session
    }
    private fun save(value:NativeSession,epoch:Long)=synchronized(state) {
        requireEpoch(epoch);store.save(json.encodeToString(SocialStored(config.appId,config.mode.name,config.backendBaseUrl!!,name,gateway.binding,value)))
    }
    private suspend fun profile(value:NativeSession):UserProfile {
        @Serializable class Me(val userId:String,val displayName:String?=null)
        val me=decode<Me>(request("/v1/me","GET",null,value.accessToken).json)
        if(me.userId!=value.userId)throw SdkFailure("AUTH_FAILED")
        return UserProfile(me.userId,me.displayName,name)
    }
    suspend fun signIn():UserProfile {
        synchronized(state){if(closed)throw SdkFailure("CANCELED")}
        if(!uiGate.tryLock())throw SdkFailure("BUSY")
        val started=synchronized(state){if(closed)throw SdkFailure("CANCELED");++generation}
        try {
            val challenge=if(name=="FACEBOOK") decode<AuthChallenge>(request("/v1/auth/challenges","POST",buildJsonObject {put("appId",config.appId);put("provider",name);put("proofType","FACEBOOK_ACCESS_TOKEN")}.toString(),null).json) else null
            if(challenge!=null && (runCatching {UUID.fromString(challenge.challengeId);Instant.parse(challenge.expiresAt)>Instant.now()}.getOrDefault(false).not() || challenge.nonce.isBlank()))throw SdkFailure("AUTH_FAILED")
            synchronized(state){requireEpoch(started)}
            val credential=gateway.authorize(challenge)
            synchronized(state){requireEpoch(started)}
            val session=when(credential) {
                is NativeSocialCredential.FacebookAccess -> {
                    if(name!="FACEBOOK" || challenge==null)throw SdkFailure("AUTH_FAILED")
                    decode<NativeSession>(request("/v1/auth/exchange","POST",buildJsonObject {put("challengeId",challenge.challengeId);put("provider","FACEBOOK");put("proofType","FACEBOOK_ACCESS_TOKEN");put("accessToken",credential.value)}.toString(),null).json)
                }
                is NativeSocialCredential.AppleCompletion -> {if(name!="APPLE")throw SdkFailure("AUTH_FAILED");credential.session}
            }
            validate(session);val user=profile(session);sessionLock.withLock {save(session,started)};return user
        }catch(_:CancellationException){throw SdkFailure("CANCELED")} finally {uiGate.unlock()}
    }
    suspend fun restore():UserProfile?=withAuthenticatedSession {profile(it)}
    override suspend fun <T> withAuthenticatedSession(block:suspend(NativeSession)->T):T?=sessionLock.withLock {
        val started=epoch();synchronized(state){requireEpoch(started)};val old=load()?:return@withLock null
        val result=try {block(old)}catch(error:SdkFailure) {
            if(error.code!="SESSION_EXPIRED")throw error
            synchronized(state){requireEpoch(started);store.save("{\"state\":\"refresh_pending\"}")}
            val fresh=decode<NativeSession>(request("/v1/auth/refresh","POST",buildJsonObject {put("refreshToken",old.refreshToken)}.toString(),null).json)
            validate(fresh);if(fresh.userId!=old.userId)throw SdkFailure("AUTH_FAILED");profile(fresh);save(fresh,started);block(fresh)
        }
        synchronized(state){requireEpoch(started)};result
    }
    suspend fun signOut()=sessionLock.withLock {
        val pending=store.load()=="{\"state\":\"refresh_pending\"}";val old=if(pending)null else load()
        synchronized(state){generation++;store.clear()};gateway.cancel();gateway.logout()
        if(pending)throw SdkFailure("SESSION_EXPIRED","REVOCATION_UNCONFIRMED")
        if(old!=null)try {request("/v1/auth/logout","POST",null,old.accessToken)}catch(error:SdkFailure) {
            if(error.code=="SESSION_EXPIRED")try {request("/v1/auth/logout","POST",buildJsonObject {put("refreshToken",old.refreshToken)}.toString(),null)}catch(_:Exception){throw SdkFailure("NETWORK_UNAVAILABLE","REVOCATION_UNCONFIRMED",true)}
            else throw SdkFailure(error.code,"REVOCATION_UNCONFIRMED",error.retryable)
        }
        Unit
    }
    fun close(){synchronized(state){closed=true;generation++};gateway.cancel();gateway.detach()}
}
