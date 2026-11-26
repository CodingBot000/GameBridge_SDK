using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace GameBridge
{
    public sealed class CapabilityStatus
    {
        public bool Supported { get; }
        public bool Configured { get; }
        public ProviderMode Mode { get; }
        public string Reason { get; }
        internal CapabilityStatus(bool supported, bool configured, ProviderMode mode, string reason)
        { Supported = supported; Configured = configured; Mode = mode; Reason = reason; }
    }
    public sealed class SdkCapabilities
    {
        public bool Known { get; }
        public IReadOnlyDictionary<string, CapabilityStatus> Features { get; }
        public DateTimeOffset SnapshotAt { get; }
        internal SdkCapabilities(bool known, IDictionary<string, CapabilityStatus> features, DateTimeOffset snapshotAt)
        { Known = known; Features = new ReadOnlyDictionary<string, CapabilityStatus>(new Dictionary<string, CapabilityStatus>(features)); SnapshotAt = snapshotAt; }
    }
    public sealed class DiagnosticsSnapshot
    {
        public ProviderMode? Mode { get; }
        public int PendingCount { get; }
        public int IgnoredMessages { get; }
        public DateTimeOffset SnapshotAt { get; }
        internal DiagnosticsSnapshot(ProviderMode? mode, int pending, int ignored, DateTimeOffset snapshotAt)
        { Mode = mode; PendingCount = pending; IgnoredMessages = ignored; SnapshotAt = snapshotAt; }
    }
    public enum DiagnosticKind { INITIALIZE, AUTH, PURCHASE, PUSH, SHUTDOWN }
    public enum DiagnosticOutcome { STARTED, SUCCEEDED, FAILED, PENDING }
    public sealed class NativeDiagnosticEvent
    {
        public DiagnosticKind Kind { get; }
        public DiagnosticOutcome Outcome { get; }
        public DateTimeOffset Timestamp { get; }
        public Guid? RequestId { get; }
        internal NativeDiagnosticEvent(DiagnosticKind kind, DiagnosticOutcome outcome, DateTimeOffset timestamp, Guid? requestId)
        { Kind = kind; Outcome = outcome; Timestamp = timestamp; RequestId = requestId; }
    }
    public sealed class SdkStatus
    {
        public string State { get; }
        public string SdkVersion { get; }
        public string Platform { get; }
        public ProviderMode? Mode { get; }
        public DateTimeOffset? InitializedAt { get; }
        public DateTimeOffset SnapshotAt { get; }
        public SdkCapabilities Capabilities { get; }
        internal SdkStatus(string state, ProviderMode? mode, DateTimeOffset? initialized, DateTimeOffset snapshot, SdkCapabilities capabilities)
        { State = state; Mode = mode; InitializedAt = initialized; SnapshotAt = snapshot; Capabilities = capabilities; SdkVersion = "0.1.2-dev"; Platform = "Unity"; }
    }
}
