package com.gamebridge.android.auth

import android.app.Activity
import android.app.Application
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.browser.customtabs.CustomTabsIntent
import com.gamebridge.*
import kotlinx.coroutines.*
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.*
import java.lang.ref.WeakReference
import java.net.URI
import java.net.URLDecoder
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Instant
import java.util.Base64
import java.util.UUID
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** Pure Native URL checks also used by JVM negative tests; no secrets enter Unity. */
internal object AppleWebLinks {
    fun validReturn(value:String):Boolean=runCatching {
        val uri=URI(value)
        uri.scheme=="https" && uri.host?.matches(Regex("(?i)[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\\.[a-z][a-z0-9-]*"))==true &&
            uri.rawUserInfo==null && uri.rawQuery==null && uri.rawFragment==null && (uri.port==-1 || uri.port==443) && uri.rawPath.startsWith("/") && !uri.rawPath.contains("%") && !uri.rawPath.contains("..")
    }.getOrDefault(false)
    fun isReturn(url:String,expected:String):Boolean=runCatching {
        val uri=URI(url);val base=URI(expected)
        validReturn(expected) && uri.scheme==base.scheme && uri.host==base.host && uri.port==base.port && uri.rawPath==base.rawPath && uri.rawUserInfo==null
    }.getOrDefault(false)
    fun handle(url:String,expected:String,flow:String):String?=runCatching {
        val uri=URI(url);val base=URI(expected)
        if(!validReturn(expected) || uri.scheme!=base.scheme || uri.host!=base.host || uri.port!=base.port || uri.rawPath!=base.rawPath || uri.rawUserInfo!=null || uri.rawFragment!=null)return null
        val query=uri.rawQuery?:return null
        if(!query.startsWith("handle=") || query.contains('&') || query.length>200)return null
        URLDecoder.decode(query.substringAfter('='),Charsets.UTF_8).takeIf {it.matches(Regex("${Regex.escape(flow)}\\.[A-Za-z0-9_-]{43}"))}
    }.getOrNull()
    fun validAuthorization(url:String,servicesId:String):Boolean=runCatching {
        val uri=URI(url)
        if(uri.scheme!="https" || uri.host!="appleid.apple.com" || uri.port!=-1 || uri.path!="/auth/authorize" || uri.rawUserInfo!=null || uri.rawFragment!=null)return false
        val entries=uri.rawQuery.split('&').map {val p=it.split('=',limit=2);require(p.size==2);URLDecoder.decode(p[0],Charsets.UTF_8) to URLDecoder.decode(p[1],Charsets.UTF_8)}
        val q=entries.toMap()
        entries.size==q.size && q["client_id"]==servicesId && q["response_type"]=="code" && q["response_mode"]=="form_post" && q["scope"]=="name email" && validReturn(q["redirect_uri"].orEmpty()) &&
            q["state"]?.matches(Regex("[A-Za-z0-9_-]{43}"))==true && q["nonce"]?.matches(Regex("[A-Za-z0-9_-]{43}"))==true
    }.getOrDefault(false)
}
internal class AppleWebGateway(context:Context,config:GameBridgeConfig):SocialCredentialGateway {
    private val app=context.applicationContext as Application
    private val client=BackendClient(config)
    private val appId=config.appId
    private val json=Json {ignoreUnknownKeys=true}
    private val servicesId:String
    private val returnUri:String
    private val generation=java.util.concurrent.atomic.AtomicLong()
    private var host:WeakReference<Activity>?=null
    private var pending:CancellableContinuation<String>?=null
    private var flowId:String?=null
    private var lifecycle:Application.ActivityLifecycleCallbacks?=null
    private val main=Handler(Looper.getMainLooper())
    override val binding get()="$servicesId|$returnUri"
    companion object {
        private var active:AppleWebGateway?=null
        fun isReturn(context:Context,url:String):Boolean=runCatching {
            val meta=context.packageManager.getApplicationInfo(context.packageName,PackageManager.GET_META_DATA).metaData
            AppleWebLinks.isReturn(url,meta?.getString("com.gamebridge.apple.RETURN_URI").orEmpty())
        }.getOrDefault(false)
        fun forward(url:String):Boolean = if(Looper.myLooper()!=Looper.getMainLooper())false else active?.redirect(url)?:false
    }
    init {
        val metadata=context.packageManager.getApplicationInfo(context.packageName,PackageManager.GET_META_DATA).metaData
        servicesId=metadata?.getString("com.gamebridge.apple.SERVICES_ID").orEmpty()
        returnUri=metadata?.getString("com.gamebridge.apple.RETURN_URI").orEmpty()
        if(!servicesId.matches(Regex("[A-Za-z0-9.-]{3,255}")) || !AppleWebLinks.validReturn(returnUri))throw SdkFailure("CONFIG_REQUIRED","APPLE_WEB_HOST")
    }
    override fun attach(activity:Activity){host=WeakReference(activity)}
    override fun detach(){cancel();host?.clear();host=null}
    private fun cleanup(){lifecycle?.let {app.unregisterActivityLifecycleCallbacks(it)};lifecycle=null;pending=null;flowId=null;if(active===this)active=null}
    override suspend fun authorize(challenge:AuthChallenge?):NativeSocialCredential {
        if(challenge!=null)throw SdkFailure("AUTH_FAILED")
        val started=generation.get()
        fun requireActive(){if(generation.get()!=started)throw SdkFailure("CANCELED")}
        val verifier=Base64.getUrlEncoder().withoutPadding().encodeToString(ByteArray(32).also {SecureRandom().nextBytes(it)})
        val hash=Base64.getUrlEncoder().withoutPadding().encodeToString(MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray(Charsets.UTF_8)))
        try {return withTimeout(180_000) {
            val start=json.parseToJsonElement(client.request("/v1/auth/apple-web/start","POST",buildJsonObject {put("appId",appId);put("verifierChallenge",hash)}.toString(),null).json).jsonObject
            requireActive()
            fun field(key:String)=start[key]?.jsonPrimitive?.contentOrNull?:throw SdkFailure("AUTH_FAILED")
            val id=field("flowId");val url=field("authorizationUrl")
            if(runCatching {UUID.fromString(id).toString()==id && Instant.parse(field("expiresAt"))>Instant.now()}.getOrDefault(false).not() || field("returnUri")!=returnUri || !AppleWebLinks.validAuthorization(url,servicesId))throw SdkFailure("AUTH_FAILED")
            val handle=withContext(Dispatchers.Main.immediate) {
                requireActive()
                val activity=host?.get()?.takeUnless {it.isFinishing || it.isDestroyed}?:throw SdkFailure("CONFIG_REQUIRED","HOST_ACTIVITY")
                if(active!=null)throw SdkFailure("BUSY")
                suspendCancellableCoroutine<String> { continuation ->
                    active=this@AppleWebGateway;pending=continuation;flowId=id
                    var left=false
                    lifecycle=object:Application.ActivityLifecycleCallbacks {
                        override fun onActivityPaused(a:Activity){if(a===host?.get())left=true}
                        override fun onActivityResumed(a:Activity){if(a===host?.get() && left)main.postDelayed({if(pending===continuation && continuation.isActive){cleanup();continuation.resumeWithException(SdkFailure("CANCELED"))}},500)}
                        override fun onActivityCreated(a:Activity,b:Bundle?){}
                        override fun onActivityStarted(a:Activity){}
                        override fun onActivityStopped(a:Activity){}
                        override fun onActivitySaveInstanceState(a:Activity,b:Bundle){}
                        override fun onActivityDestroyed(a:Activity){if(a===host?.get())cancel()}
                    }
                    app.registerActivityLifecycleCallbacks(lifecycle!!)
                    continuation.invokeOnCancellation {main.post {if(pending===continuation)cleanup()}}
                    try {CustomTabsIntent.Builder().build().launchUrl(activity,Uri.parse(url))}
                    catch(_:Exception){cleanup();if(continuation.isActive)continuation.resumeWithException(SdkFailure("CONFIG_REQUIRED","EXTERNAL_BROWSER"))}
                }
            }
            currentCoroutineContext().ensureActive();requireActive()
            val response=json.parseToJsonElement(client.request("/v1/auth/apple-web/complete","POST",buildJsonObject {put("appId",appId);put("flowId",id);put("handle",handle);put("verifier",verifier)}.toString(),null).json).jsonObject
            when(response["status"]?.jsonPrimitive?.contentOrNull) {
                "COMPLETE"->NativeSocialCredential.AppleCompletion(json.decodeFromString<NativeSession>((response["session"]?:throw SdkFailure("AUTH_FAILED")).toString()))
                "CANCELED"->throw SdkFailure("CANCELED")
                else->throw SdkFailure("AUTH_FAILED")
            }
        }}catch(_:TimeoutCancellationException){throw SdkFailure("TIMEOUT",retryable=true)}
    }
    override fun redirect(url:String):Boolean {
        val id=flowId?:return false
        val handle=AppleWebLinks.handle(url,returnUri,id)?:return false
        val cont=pending?:return false
        cleanup();if(cont.isActive)cont.resume(handle);return true
    }
    override fun cancel(){generation.incrementAndGet();main.post {val cont=pending;cleanup();cont?.cancel()}}
    override fun logout()=cancel()
}
