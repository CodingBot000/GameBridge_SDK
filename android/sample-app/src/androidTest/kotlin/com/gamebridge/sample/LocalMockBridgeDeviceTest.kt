package com.gamebridge.sample

import android.content.Intent
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gamebridge.bridge.BridgeCallback
import com.gamebridge.bridge.BridgeFacade
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

/** Opt-in instrumented LOCAL_MOCK test; does not execute Unity or a real provider. */
@RunWith(AndroidJUnit4::class)
class LocalMockBridgeDeviceTest {
    @Test fun kotlinBridgeCallsLocalBackend() {
        val args = InstrumentationRegistry.getArguments()
        val base = args.getString("gamebridge_mock_url")
        val key = args.getString("gamebridge_mock_key")
        assumeTrue("explicit synthetic local server and key required", base?.startsWith("http://10.0.2.2:") == true && (key?.length ?: 0) >= 32)
        val instrument = InstrumentationRegistry.getInstrumentation()
        val activity = instrument.startActivitySync(Intent(instrument.targetContext, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        val responses = LinkedBlockingQueue<String>()
        BridgeFacade.attachHost(activity); BridgeFacade.setCallback(BridgeCallback { responses.add(it) })
        val session = UUID.randomUUID().toString()
        fun call(operation: String, payload: JSONObject = JSONObject()): Any {
            val id = UUID.randomUUID().toString()
            val request = JSONObject().put("protocolVersion", 1).put("sdkSessionId", session).put("kind", "request")
                .put("requestId", id).put("operation", operation).put("payload", payload)
            BridgeFacade.dispatch(request.toString())
            val until = System.nanoTime() + TimeUnit.SECONDS.toNanos(40)
            while (System.nanoTime() < until) {
                val message = responses.poll(1, TimeUnit.SECONDS) ?: continue
                val response = JSONObject(message)
                if (response.optString("requestId") != id) continue
                assertTrue("operation $operation failed with " + response.optJSONObject("error")?.optString("code"), response.optBoolean("ok"))
                Log.i("GB_NATIVE_E2E", "operation=$operation requestId=$id status=PASS")
                return response.get("result")
            }
            error("operation timeout: $operation")
        }
        try {
            val config = JSONObject().put("providerMode", "LOCAL_MOCK").put("appId", "gamebridge-sample")
                .put("backendBaseUrl", base).put("requestTimeoutMs", 30000).put("developmentKey", key).put("mockSubject", "A")
            call("sdk.initialize", config)
            call("auth.signIn", JSONObject().put("provider", "MOCK"))
            val before = (call("store.entitlements") as JSONObject).getString("coinBalance").toLong()
            val products = call("store.products") as org.json.JSONArray
            assertTrue((0 until products.length()).any { products.getJSONObject(it).getString("productId") == "coins_100" })
            val purchase = call("store.purchase", JSONObject().put("productId", "coins_100")) as JSONObject
            assertEquals("PURCHASED", purchase.getString("status")); assertEquals("GRANTED", purchase.getString("fulfillmentStatus"))
            val after = (call("store.entitlements") as JSONObject).getString("coinBalance").toLong()
            assertEquals(before + 100, after)
            call("auth.signOut"); call("sdk.shutdown")
        } finally { BridgeFacade.setCallback(null); BridgeFacade.detachHost(); activity.finish() }
    }
}
