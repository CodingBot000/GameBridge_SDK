import Foundation

public enum DiagnosticKind: String { case initialize, auth, purchase, push, shutdown }
public enum DiagnosticOutcome: String { case started, succeeded, failed, pending }
public struct DiagnosticEvent {
    public let kind: DiagnosticKind
    public let outcome: DiagnosticOutcome
    public let timestamp: Date
    public let requestId: UUID?
}
/// Only typed categories and UUIDs are accepted; payloads and tokens have no input field.
public actor Diagnostics {
    private var events: [DiagnosticEvent] = []
    public init() {}
    public func record(_ kind: DiagnosticKind, _ outcome: DiagnosticOutcome, requestId: UUID? = nil) {
        if events.count == 200 { events.removeFirst() }
        events.append(DiagnosticEvent(kind: kind, outcome: outcome, timestamp: Date(), requestId: requestId))
    }
    public func clear() { events.removeAll() }
    public func snapshot() -> [DiagnosticEvent] { events }
}
