package com.gamebridge.measure

import kotlinx.serialization.json.*
import org.junit.jupiter.api.extension.BeforeEachCallback
import org.junit.jupiter.api.extension.AfterEachCallback
import org.junit.jupiter.api.extension.ExtensionContext

/** Test-only invocation counts. Never infer assertions from test/static declaration counts. */
internal object AssertionMeter {
    private val gate = Any()
    private var active: String? = null
    private var normal = 0
    private var expected = 0
    fun begin(id: String) = synchronized(gate) {
        check(active == null) { "Overlapping assertion measurement scopes" }
        active = id; normal = 0; expected = 0
    }
    fun hit(kind: String) = synchronized(gate) {
        check(active != null) { "Assertion outside measured test scope" }
        if (kind == "expectedError") expected++ else normal++
    }
    fun end(context: ExtensionContext) = synchronized(gate) {
        check(active == context.uniqueId)
        println("GB_ASSERTIONS_JSON " + buildJsonObject {
            put("platform", "kotlin-jvm"); put("test", context.requiredTestClass.simpleName + "." + context.requiredTestMethod.name)
            put("normalAssertions", normal); put("expectedErrorChecks", expected); put("assertionsExecuted", normal + expected)
            put("assertionOutcomes", "UNMEASURED"); put("scope", "counted test helper invocations")
        })
        active = null
    }
}
internal class MeasuredAssertions : BeforeEachCallback, AfterEachCallback {
    override fun beforeEach(context: ExtensionContext) = AssertionMeter.begin(context.uniqueId)
    override fun afterEach(context: ExtensionContext) = AssertionMeter.end(context)
}
internal fun <T> assertEquals(expected: T, actual: T, message: String? = null) {
    AssertionMeter.hit("normal"); kotlin.test.assertEquals(expected, actual, message)
}
internal fun assertTrue(actual: Boolean, message: String? = null) {
    AssertionMeter.hit("normal"); kotlin.test.assertTrue(actual, message)
}
internal fun assertFalse(actual: Boolean, message: String? = null) {
    AssertionMeter.hit("normal"); kotlin.test.assertFalse(actual, message)
}
internal inline fun <reified T : Throwable> assertFailsWith(message: String? = null, block: () -> Unit): T {
    AssertionMeter.hit("expectedError"); return kotlin.test.assertFailsWith<T>(message, block)
}
internal inline fun assertFails(message: String? = null, block: () -> Unit): Throwable {
    AssertionMeter.hit("expectedError"); return kotlin.test.assertFails(message, block)
}
