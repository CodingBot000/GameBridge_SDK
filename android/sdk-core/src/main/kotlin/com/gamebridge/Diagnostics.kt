package com.gamebridge

import java.time.Instant
import java.util.UUID

enum class DiagnosticKind { INITIALIZE, AUTH, PURCHASE, PUSH, SHUTDOWN }
enum class DiagnosticOutcome { STARTED, SUCCEEDED, FAILED, PENDING }
data class DiagnosticEvent(val kind: DiagnosticKind, val outcome: DiagnosticOutcome, val timestamp: Instant, val requestId: UUID?)

/** Diagnostics accept structured enums and UUIDs only; no messages, payloads, or tokens. */
class Diagnostics {
    private val events = ArrayDeque<DiagnosticEvent>(200)
    @Synchronized fun record(kind: DiagnosticKind, outcome: DiagnosticOutcome, requestId: UUID? = null) {
        if (events.size == 200) events.removeFirst()
        events.addLast(DiagnosticEvent(kind, outcome, Instant.now(), requestId))
    }
    @Synchronized fun snapshot(): List<DiagnosticEvent> = events.toList()
}
