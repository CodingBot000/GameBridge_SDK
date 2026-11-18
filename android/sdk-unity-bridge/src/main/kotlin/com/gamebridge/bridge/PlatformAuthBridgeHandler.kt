package com.gamebridge.bridge

import com.gamebridge.*
import kotlinx.serialization.json.*

/** Selects an explicit Native auth provider; does not merge or fallback identities. */
internal class PlatformAuthBridgeHandler(private val google:BridgeOperationHandler,private val marker:TokenStore,
    private val create:(String)->BridgeOperationHandler):BridgeOperationHandler {
    private var selected="GOOGLE"
    private var payload:JsonObject?=null
    private val handlers=mutableMapOf<String,BridgeOperationHandler>("GOOGLE" to google)
    private fun handler(name:String)=handlers.getOrPut(name){create(name)}
    private fun string(body:JsonObject,key:String)=body[key]?.jsonPrimitive?.contentOrNull ?: throw SdkFailure("CONFIG_REQUIRED")
    override fun invoke(operation:String,body:JsonObject):JsonElement {
        if(operation=="sdk.initialize") {
            if(body["providerMode"]?.jsonPrimitive?.content!="PLATFORM_SANDBOX")throw SdkFailure("UNSUPPORTED_PROVIDER")
            if(payload!=null && payload!=body)throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")
            if(payload==null)selected="GOOGLE"
            marker.load()?.let {
                val saved=try {Json.parseToJsonElement(it).jsonObject}catch(_:Exception){throw SdkFailure("SESSION_EXPIRED")}
                if(saved["appId"]!=body["appId"] || saved["backendBaseUrl"]!=body["backendBaseUrl"])throw SdkFailure("SESSION_EXPIRED")
                selected=saved["provider"]?.jsonPrimitive?.content ?: throw SdkFailure("SESSION_EXPIRED")
                if(selected !in setOf("GOOGLE","FACEBOOK"))throw SdkFailure("SESSION_EXPIRED")
            }
            val result=handler(selected).invoke(operation,body);payload=body;return result
        }
        val initialization=payload ?:throw SdkFailure("NOT_INITIALIZED")
        if(operation=="sdk.shutdown") {
            var failure:Throwable?=null
            handlers.values.toSet().forEach {try {it.invoke(operation,body)}catch(error:Throwable){if(failure==null)failure=error}}
            payload=null;handlers.clear();handlers["GOOGLE"]=google;selected="GOOGLE"
            failure?.let {throw it};return buildJsonObject{}
        }
        if(operation=="auth.signIn") {
            val next=body["provider"]?.jsonPrimitive?.content ?:throw SdkFailure("UNSUPPORTED_PROVIDER")
            if(next !in setOf("GOOGLE","FACEBOOK"))throw SdkFailure("UNSUPPORTED_PROVIDER")
            if(next!=selected) {
                val target=handler(next);target.invoke("sdk.initialize",initialization) // preflight before clearing the current identity
                handler(selected).invoke("auth.signOut",buildJsonObject{})
                handler(selected).invoke("sdk.shutdown",buildJsonObject{})
                marker.clear();selected=next
            }
            return handler(selected).invoke(operation,body).also {
                marker.save(buildJsonObject {put("appId",string(initialization,"appId"));put("backendBaseUrl",string(initialization,"backendBaseUrl"));put("provider",selected)}.toString())
            }
        }
        val result=handler(selected).invoke(operation,body)
        if(operation=="auth.signOut")marker.clear()
        return result
    }
}
