package com.gamebridge

import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.*

class DiagnosticsTest {
    @Test fun `diagnostics retain newest 200 typed events`() {
        val diagnostics = Diagnostics(); val first = UUID.randomUUID(); val last = UUID.randomUUID()
        diagnostics.record(DiagnosticKind.AUTH, DiagnosticOutcome.STARTED, first)
        repeat(199) { diagnostics.record(DiagnosticKind.PUSH, DiagnosticOutcome.PENDING) }
        diagnostics.record(DiagnosticKind.SHUTDOWN, DiagnosticOutcome.SUCCEEDED, last)
        val events = diagnostics.snapshot()
        assertEquals(200, events.size); assertFalse(events.any { it.requestId == first }); assertEquals(last, events.last().requestId)
    }
}
