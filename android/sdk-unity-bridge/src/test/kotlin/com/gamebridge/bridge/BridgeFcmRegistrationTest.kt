package com.gamebridge.bridge

import com.gamebridge.SdkFailure
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class BridgeFcmRegistrationTest {
    @Test fun `class lookup failures refuse both providers before calling adapter`() = runBlocking {
        for (policy in BridgeFcmPolicy.entries) {
            for (missing in listOf(ClassNotFoundException("fixture"), NoClassDefFoundError("fixture"))) {
                val error = assertFailsWith<SdkFailure> {
                    acquireBridgeFcmToken(1000, policy, { throw missing }) { _, _ -> error("unexpected adapter") }
                }
                assertEquals("CONFIG_REQUIRED", error.code)
                assertEquals("FIREBASE_HOST", error.nativeCode)
            }
        }
    }

    @Test fun `adapter callback errors and synchronous linkage retain distinct policies`() = runBlocking {
        for (policy in BridgeFcmPolicy.entries) {
            val error = assertFailsWith<SdkFailure> {
                acquireBridgeFcmToken(1000, policy, { }) { _, fail -> fail(); true }
            }
            assertEquals("CONFIG_REQUIRED", error.code)
            assertEquals(policy.callbackNativeCode, error.nativeCode)
        }
        val error = assertFailsWith<SdkFailure> {
            acquireBridgeFcmToken(1000, BridgeFcmPolicy.GOOGLE, { }) { _, _ -> throw NoClassDefFoundError("fixture") }
        }
        assertEquals("FIREBASE_HOST", error.nativeCode)
        val social = assertFailsWith<NoClassDefFoundError> {
            acquireBridgeFcmToken(1000, BridgeFcmPolicy.SOCIAL, { }) { _, _ -> throw NoClassDefFoundError("fixture") }
        }
        assertEquals("fixture", social.message)
    }

    @Test fun `permission denial and timeout preserve their codes`() = runBlocking {
        for (policy in BridgeFcmPolicy.entries) {
            val denied = assertFailsWith<SdkFailure> { acquireBridgeFcmToken(1000, policy, { }) { _, _ -> false } }
            assertEquals("PERMISSION_DENIED", denied.code)
            val timeout = assertFailsWith<SdkFailure> { acquireBridgeFcmToken(20, policy, { }) { _, _ -> true } }
            assertEquals("TIMEOUT", timeout.code)
            assertTrue(timeout.retryable)
        }
    }

    @Test fun `first synchronous token wins sequential duplicate callbacks`() = runBlocking {
        for (policy in BridgeFcmPolicy.entries) {
            val value = acquireBridgeFcmToken(1000, policy, { }) { token, error ->
                token("fixture")
                token("duplicate")
                error()
                true
            }
            assertEquals("fixture", value)
        }
    }

    @Test fun `caller cancellation suppresses late token and error callbacks`() = runBlocking {
        val callbacks = CompletableDeferred<Pair<(String) -> Unit, () -> Unit>>()
        val request = async {
            acquireBridgeFcmToken(1000, BridgeFcmPolicy.SOCIAL, { }) { token, error ->
                callbacks.complete(token to error)
                true
            }
        }
        val (token, error) = callbacks.await()
        request.cancelAndJoin()
        token("late fixture")
        error()
        assertTrue(request.isCancelled)
    }
}
