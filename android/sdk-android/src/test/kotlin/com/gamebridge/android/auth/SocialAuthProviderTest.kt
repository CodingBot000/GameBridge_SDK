package com.gamebridge.android.auth

import android.app.Activity
import com.gamebridge.*
import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import kotlin.test.*

private class SocialMemory:TokenStore {var raw:String?=null;override fun load()=raw;override fun save(value:String){raw=value};override fun clear(){raw=null}}
private class SocialFakeGateway:SocialCredentialGateway {
    override val binding="facebook-app-123"
    var waiting:CompletableDeferred<NativeSocialCredential>?=null
    override fun attach(activity:Activity){};override fun detach(){};override fun cancel(){};override fun logout(){}
    override suspend fun authorize(challenge:AuthChallenge?):NativeSocialCredential {assertEquals("server-nonce",challenge?.nonce);return waiting?.await() ?:NativeSocialCredential.FacebookAccess("opaque-fb-proof")}
}
class SocialAuthProviderTest {
    private val user="11111111-1111-4111-8111-111111111111"
    private fun make(store:SocialMemory,gateway:SocialFakeGateway,app:String="game",wrongUser:Boolean=false,requests:MutableList<String> = mutableListOf()):SocialAuthProvider {
        val config=GameBridgeConfig(app,ProviderMode.PLATFORM_SANDBOX,"https://backend.invalid")
        return SocialAuthProvider(config,"FACEBOOK",store,gateway) {path,_,body,_->
            requests+=path
            val result=when(path) {
                "/v1/auth/challenges"->{assertEquals("FACEBOOK_ACCESS_TOKEN",Json.parseToJsonElement(body!!).jsonObject["proofType"]!!.jsonPrimitive.content);"""{"challengeId":"22222222-2222-4222-8222-222222222222","nonce":"server-nonce","expiresAt":"2035-01-01T00:00:00Z"}"""}
                "/v1/auth/exchange"->{assertTrue(body!!.contains("FACEBOOK_ACCESS_TOKEN"));assertFalse(body.contains("idToken"));"""{"accessToken":"server-access","refreshToken":"server-refresh","expiresAt":"2035-01-01T00:00:00Z","userId":"$user"}"""}
                "/v1/me"->"""{"userId":"${if(wrongUser)"33333333-3333-4333-8333-333333333333" else user}","displayName":null}"""
                else->"{}"
            };BackendResponse(null,result)
        }
    }
    @Test fun `classic proof does not persist or enter public profile and restore is scoped`()=runBlocking {
        val store=SocialMemory();val provider=make(store,SocialFakeGateway());val profile=provider.signIn();assertEquals("FACEBOOK",profile.provider)
        assertFalse(store.raw!!.contains("opaque-fb-proof"));assertFalse(profile.toString().contains("server-access"));assertEquals(user,provider.restore()?.userId)
        assertFailsWith<SdkFailure>{make(store,SocialFakeGateway(),app="other").restore()}
        provider.signOut();assertNull(store.raw)
    }
    @Test fun `duplicate login and closed late result do not mint or persist session`()=runBlocking {
        val store=SocialMemory();val gateway=SocialFakeGateway();gateway.waiting=CompletableDeferred();val requests=mutableListOf<String>();val provider=make(store,gateway,requests=requests)
        val first=async {runCatching {provider.signIn()}};yield()
        assertEquals("BUSY",assertFailsWith<SdkFailure>{provider.signIn()}.code)
        provider.close();gateway.waiting!!.complete(NativeSocialCredential.FacebookAccess("late-proof"))
        assertEquals("CANCELED",(first.await().exceptionOrNull() as SdkFailure).code);assertFalse(requests.contains("/v1/auth/exchange"));assertNull(store.raw)
    }
    @Test fun `wrong profile never persists a new session`()=runBlocking {
        val store=SocialMemory();assertEquals("AUTH_FAILED",assertFailsWith<SdkFailure>{make(store,SocialFakeGateway(),wrongUser=true).signIn()}.code);assertNull(store.raw)
    }
}
