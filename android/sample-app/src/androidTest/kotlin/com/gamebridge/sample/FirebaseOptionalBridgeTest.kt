package com.gamebridge.sample

import android.content.Intent
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.gamebridge.bridge.BridgeCallback
import com.gamebridge.bridge.BridgeFacade
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

@RunWith(AndroidJUnit4::class)
class FirebaseOptionalBridgeTest {
    @Test fun missingFirebaseFailsClosedWithoutNetwork() {
        assertTrue(runCatching { Class.forName("com.google.firebase.messaging.FirebaseMessaging") }.isFailure)
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        val activity = instrumentation.startActivitySync(Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        val responses = LinkedBlockingQueue<String>()
        BridgeFacade.attachHost(activity); BridgeFacade.setCallback(BridgeCallback { responses.add(it) })
        val session = UUID.randomUUID().toString()
        fun call(operation: String, payload: JSONObject = JSONObject()): JSONObject {
            val request = JSONObject().put("protocolVersion", 1).put("sdkSessionId", session).put("kind", "request")
                .put("requestId", UUID.randomUUID().toString()).put("operation", operation).put("payload", payload)
            BridgeFacade.dispatch(request.toString())
            return JSONObject(requireNotNull(responses.poll(5, TimeUnit.SECONDS)))
        }
        try {
            val config = JSONObject().put("providerMode", "PLATFORM_SANDBOX").put("appId", "demo")
                .put("backendBaseUrl", "https://example.invalid").put("requestTimeoutMs", 30000)
                .put("googleServerClientId", "synthetic-client").put("installationId", UUID.randomUUID().toString())
            assertTrue(call("sdk.initialize", config).getBoolean("ok"))
            val result = call("push.register")
            assertFalse(result.getBoolean("ok")); assertEquals("CONFIG_REQUIRED", result.getJSONObject("error").getString("code"))
        } finally { BridgeFacade.setCallback(null); BridgeFacade.detachHost(); activity.finish() }
    }
}
