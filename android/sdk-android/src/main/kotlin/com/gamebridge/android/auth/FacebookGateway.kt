package com.gamebridge.android.auth

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import com.facebook.*
import com.facebook.login.LoginManager
import com.facebook.login.LoginResult
import com.gamebridge.SdkFailure
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.TimeoutCancellationException
import java.lang.ref.WeakReference
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** Host initializes Meta and forwards its Activity result; no Activity/delegate replacement. */
internal class FacebookGateway(context:Context):SocialCredentialGateway {
    private val appId:String
    private val callbacks:CallbackManager
    private val manager:LoginManager
    companion object {
        private var active:FacebookGateway?=null
        fun forward(requestCode:Int,resultCode:Int,data:Intent?):Boolean = if(Looper.myLooper()!=Looper.getMainLooper())false else active?.callbacks?.onActivityResult(requestCode,resultCode,data) ?: false
    }
    private var host:WeakReference<Activity>?=null
    private var pending:kotlinx.coroutines.CancellableContinuation<NativeSocialCredential>?=null
    override val binding get()=appId
    init {
        if(!FacebookSdk.isInitialized())throw SdkFailure("CONFIG_REQUIRED","FACEBOOK_HOST")
        appId=FacebookSdk.getApplicationId()
        callbacks=CallbackManager.Factory.create();manager=LoginManager.getInstance()
        if(!appId.matches(Regex("[0-9]+")) || FacebookSdk.getClientToken().isNullOrBlank())throw SdkFailure("CONFIG_REQUIRED","FACEBOOK_CLIENT")
    }
    override fun attach(activity:Activity){host=WeakReference(activity)}
    override fun detach(){host?.clear();host=null;cancel()}
    override suspend fun authorize(challenge:AuthChallenge?):NativeSocialCredential=withContext(Dispatchers.Main.immediate) {
        if(challenge==null)throw SdkFailure("AUTH_FAILED")
        val activity=host?.get()?.takeUnless {it.isDestroyed || it.isFinishing} ?:throw SdkFailure("CONFIG_REQUIRED","HOST_ACTIVITY")
        if(active!=null)throw SdkFailure("BUSY")
        try {withTimeout(180_000) {
            suspendCancellableCoroutine { continuation ->
                pending=continuation;active=this@FacebookGateway
                manager.registerCallback(callbacks,object:FacebookCallback<LoginResult> {
                    private fun take():Boolean {
                        if(active!==this@FacebookGateway)return false
                        active=null;manager.unregisterCallback(callbacks)
                        val valid=pending===continuation && continuation.isActive;pending=null;return valid
                    }
                    override fun onSuccess(result:LoginResult){
                        if(!take())return
                        val token=result.accessToken
                        if(token.applicationId!=appId || token.isExpired || !token.permissions.contains("public_profile"))continuation.resumeWithException(SdkFailure("AUTH_FAILED"))
                        else continuation.resume(NativeSocialCredential.FacebookAccess(token.token))
                    }
                    override fun onCancel(){if(take())continuation.resumeWithException(SdkFailure("CANCELED"))}
                    override fun onError(error:FacebookException){if(take())continuation.resumeWithException(SdkFailure("AUTH_FAILED"))}
                })
                continuation.invokeOnCancellation {Handler(Looper.getMainLooper()).post {if(pending===continuation){pending=null}}}
                try {manager.logOut();manager.logInWithReadPermissions(activity,listOf("public_profile"))}
                catch(_:Exception){active=null;pending=null;manager.unregisterCallback(callbacks);if(continuation.isActive)continuation.resumeWithException(SdkFailure("AUTH_FAILED"))}
            }
        }}catch(_:TimeoutCancellationException){throw SdkFailure("TIMEOUT",retryable=true)}
    }
    override fun activityResult(requestCode:Int,resultCode:Int,data:Intent?):Boolean = callbacks.onActivityResult(requestCode,resultCode,data)
    override fun cancel(){Handler(Looper.getMainLooper()).post {pending?.cancel();pending=null}}
    override fun logout(){Handler(Looper.getMainLooper()).post {manager.logOut()}}
}
