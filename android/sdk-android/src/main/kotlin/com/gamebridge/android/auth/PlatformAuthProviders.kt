package com.gamebridge.android.auth

import android.app.Activity
import android.content.Context
import android.content.Intent
import com.gamebridge.*
import com.gamebridge.android.purchase.GoogleStoreSession
import com.gamebridge.android.push.GooglePushClient
import java.util.UUID

/** Public Native facade. Third-party tokens and Backend sessions remain internal. */
interface PlatformAuthProvider:AutoCloseable {
    fun attachHost(activity:Activity)
    suspend fun signIn():UserProfile
    suspend fun restore():UserProfile?
    suspend fun signOut()
    fun storeSession():GoogleStoreSession
    fun pushClient(installationId:UUID):GooglePushClient
}
internal class NativePlatformAuth(private val context:Context,private val config:GameBridgeConfig,private val auth:SocialAuthProvider):PlatformAuthProvider {
    override fun attachHost(activity:Activity)=auth.attachHost(activity)
    override suspend fun signIn()=auth.signIn()
    override suspend fun restore()=auth.restore()
    override suspend fun signOut()=auth.signOut()
    override fun storeSession()=GoogleStoreSession.createSocial(context,config,auth)
    override fun pushClient(installationId:UUID)=GooglePushClient.createSocial(auth,config,installationId)
    override fun close()=auth.close()
}
object PlatformAuthProviders {
    @JvmStatic fun facebook(context:Context,config:GameBridgeConfig,store:TokenStore):PlatformAuthProvider {
        try {
            Class.forName("com.facebook.login.LoginManager",false,context.classLoader)
            return NativePlatformAuth(context.applicationContext,config,SocialAuthProvider(config,"FACEBOOK",store,FacebookGateway(context)))
        }catch(_:LinkageError){throw SdkFailure("CONFIG_REQUIRED","FACEBOOK_HOST")}
         catch(_:ClassNotFoundException){throw SdkFailure("CONFIG_REQUIRED","FACEBOOK_HOST")}
         catch(error:SdkFailure){throw error}
         catch(_:Exception){throw SdkFailure("CONFIG_REQUIRED","FACEBOOK_HOST")}
    }
    @JvmStatic fun forwardFacebookActivityResult(requestCode:Int,resultCode:Int,data:Intent?):Boolean = try {FacebookGateway.forward(requestCode,resultCode,data)}catch(_:LinkageError){false}
}
