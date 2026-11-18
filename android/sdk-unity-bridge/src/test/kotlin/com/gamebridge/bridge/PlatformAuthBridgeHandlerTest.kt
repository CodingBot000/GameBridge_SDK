package com.gamebridge.bridge

import com.gamebridge.*
import kotlinx.serialization.json.*
import kotlin.test.*

class PlatformAuthBridgeHandlerTest {
    private class Store:TokenStore {var value:String?=null;override fun load()=value;override fun save(value:String){this.value=value};override fun clear(){value=null}}
    private val init=buildJsonObject {put("providerMode","PLATFORM_SANDBOX");put("appId","game");put("backendBaseUrl","https://backend.invalid")}
    @Test fun `Apple and Facebook selected identity restores without invoking Google or mock`() {
        for(name in listOf("APPLE","FACEBOOK")) {
            val marker=Store();val calls=mutableListOf<String>()
            fun fake(provider:String)=BridgeOperationHandler {op,_->calls+="$provider:$op";buildJsonObject{put("provider",provider)}}
            val mux=PlatformAuthBridgeHandler(fake("GOOGLE"),marker){fake(it)}
            mux.invoke("sdk.initialize",init);mux.invoke("auth.signIn",buildJsonObject{put("provider",name)})
            assertTrue(calls.contains("GOOGLE:auth.signOut"));assertTrue(marker.value!!.contains(name))
            mux.invoke("sdk.shutdown",buildJsonObject{});calls.clear()
            val restored=PlatformAuthBridgeHandler(fake("GOOGLE"),marker){fake(it)}
            restored.invoke("sdk.initialize",init);val user=restored.invoke("auth.restore",buildJsonObject{}).jsonObject
            assertEquals(name,user["provider"]!!.jsonPrimitive.content);assertTrue(calls.all {it.startsWith(name+":")})
            assertEquals("UNSUPPORTED_PROVIDER",assertFailsWith<SdkFailure>{restored.invoke("auth.signIn",buildJsonObject{put("provider","MOCK")})}.code)
        }
    }
    @Test fun `new provider preflight failure preserves old identity and app marker cannot cross scope`() {
        val calls=mutableListOf<String>();val marker=Store()
        val google=BridgeOperationHandler {op,_->calls+=op;buildJsonObject{}}
        val mux=PlatformAuthBridgeHandler(google,marker){throw SdkFailure("CONFIG_REQUIRED")}
        mux.invoke("sdk.initialize",init)
        assertEquals("CONFIG_REQUIRED",assertFailsWith<SdkFailure>{mux.invoke("auth.signIn",buildJsonObject{put("provider","APPLE")})}.code)
        assertFalse(calls.contains("auth.signOut"));assertFalse(calls.contains("sdk.shutdown"));assertNull(marker.value)
        marker.value=buildJsonObject{put("appId","other");put("backendBaseUrl","https://backend.invalid");put("provider","APPLE")}.toString()
        assertEquals("SESSION_EXPIRED",assertFailsWith<SdkFailure>{PlatformAuthBridgeHandler(google,marker){error("must not create")}.invoke("sdk.initialize",init)}.code)
    }
}
