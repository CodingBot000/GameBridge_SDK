package com.gamebridge.bridge

import android.app.Activity
import com.gamebridge.SdkFailure
import com.gamebridge.android.push.AndroidPushHostAdapter
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeout
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

private const val FIREBASE_HOST = "FIREBASE_HOST"

internal enum class BridgeFcmPolicy(val callbackNativeCode: String?) {
    GOOGLE(FIREBASE_HOST),
    SOCIAL(null),
}

internal suspend fun requestBridgeFcmToken(activity: Activity, timeoutMs: Long, policy: BridgeFcmPolicy): String =
    acquireBridgeFcmToken(timeoutMs, policy) { onToken, onError ->
        val adapter = AndroidPushHostAdapter(onToken, { _, _ -> }, onError)
        val permitted = adapter.hasNotificationPermission(activity)
        if (permitted) adapter.register()
        permitted
    }

internal suspend fun acquireBridgeFcmToken(
    timeoutMs: Long,
    policy: BridgeFcmPolicy,
    loadFirebase: () -> Unit = { Class.forName("com.google.firebase.messaging.FirebaseMessaging") },
    request: (onToken: (String) -> Unit, onError: () -> Unit) -> Boolean,
): String {
    try {
        loadFirebase()
    } catch (_: ClassNotFoundException) {
        throw SdkFailure("CONFIG_REQUIRED", FIREBASE_HOST)
    } catch (_: LinkageError) {
        throw SdkFailure("CONFIG_REQUIRED", FIREBASE_HOST)
    }
    return try {
        withTimeout(timeoutMs) {
            suspendCancellableCoroutine { continuation ->
                try {
                    val permitted = request(
                        { if (continuation.isActive) continuation.resume(it) },
                        {
                            if (continuation.isActive) {
                                continuation.resumeWithException(SdkFailure("CONFIG_REQUIRED", policy.callbackNativeCode))
                            }
                        },
                    )
                    if (!permitted) continuation.resumeWithException(SdkFailure("PERMISSION_DENIED"))
                } catch (error: LinkageError) {
                    if (policy != BridgeFcmPolicy.GOOGLE) throw error
                    if (continuation.isActive) {
                        continuation.resumeWithException(SdkFailure("CONFIG_REQUIRED", FIREBASE_HOST))
                    }
                }
            }
        }
    } catch (_: TimeoutCancellationException) {
        throw SdkFailure("TIMEOUT", retryable = true)
    }
}
