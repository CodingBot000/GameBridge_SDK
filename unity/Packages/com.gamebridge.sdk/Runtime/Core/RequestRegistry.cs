using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace GameBridge.Core
{
    public sealed class SdkException : Exception
    {
        public string Code { get; }
        public bool Retryable { get; }
        public SdkException(string code, bool retryable = false) : base(code) { Code = code; Retryable = retryable; }
    }

    /// <summary>Internal wire registry. Public consumers receive typed, sanitized results only.</summary>
    internal sealed class RequestRegistry : IDisposable
    {
        private sealed class Pending
        {
            internal readonly string Operation;
            internal readonly TaskCompletionSource<JToken> Completion = new TaskCompletionSource<JToken>(TaskCreationOptions.RunContinuationsAsynchronously);
            internal Pending(string operation) { Operation = operation; }
        }
        private static readonly HashSet<string> Allowed = new HashSet<string> {
            "sdk.initialize", "sdk.status", "sdk.capabilities", "auth.signIn", "auth.signOut", "auth.restore",
            "store.products", "store.purchase", "store.entitlements", "store.sync", "push.permission", "push.register",
            "push.unregister", "config.get", "diagnostics.get", "sdk.shutdown"
        };
        private static readonly HashSet<string> Errors = new HashSet<string> {
            "NOT_INITIALIZED", "ALREADY_INITIALIZED_DIFFERENT_CONFIG", "INVALID_ARGUMENT", "UNSUPPORTED_PLATFORM", "UNSUPPORTED_PROVIDER",
            "UNSUPPORTED_OPERATION", "CONFIG_REQUIRED", "NETWORK_UNAVAILABLE", "TIMEOUT", "CANCELED", "BUSY", "SESSION_EXPIRED",
            "AUTH_FAILED", "AUTH_REPLAY_DETECTED", "PRODUCT_NOT_FOUND", "STORE_UNAVAILABLE", "PURCHASE_FAILED", "VERIFICATION_FAILED",
            "PURCHASE_ACCOUNT_MISMATCH", "IDEMPOTENCY_CONFLICT", "PERMISSION_DENIED", "MAINTENANCE", "BRIDGE_PROTOCOL_MISMATCH",
            "PAYLOAD_TOO_LARGE", "INTERNAL_ERROR"
        };
        internal static bool IsKnownError(string code) => code != null && Errors.Contains(code);
        private readonly object gate = new object();
        private readonly Dictionary<string, Pending> pending = new Dictionary<string, Pending>();
        private readonly Action<string> dispatch;
        private readonly string sessionId;
        private bool disposed;
        private int ignored;
        internal int IgnoredMessages => Volatile.Read(ref ignored);
        internal RequestRegistry(Action<string> dispatch, Guid sessionId)
        {
            this.dispatch = dispatch ?? throw new ArgumentNullException(nameof(dispatch));
            this.sessionId = sessionId.ToString("D");
        }
        internal async Task<JToken> RequestAsync(string operation, JObject payload, TimeSpan timeout, CancellationToken cancellation = default)
        {
            if (!Allowed.Contains(operation) || payload == null || timeout <= TimeSpan.Zero || timeout.TotalMilliseconds > uint.MaxValue - 1) throw new SdkException("INVALID_ARGUMENT");
            var id = Guid.NewGuid().ToString("D");
            var entry = new Pending(operation);
            var envelope = new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = sessionId, ["kind"] = "request", ["requestId"] = id, ["operation"] = operation, ["payload"] = payload.DeepClone() };
            var json = envelope.ToString(Formatting.None);
            if (Encoding.UTF8.GetByteCount(json) > 256 * 1024) throw new SdkException("PAYLOAD_TOO_LARGE");
            lock (gate)
            {
                if (disposed) throw new SdkException("NOT_INITIALIZED");
                if (pending.Count >= 100) throw new SdkException("BUSY", true);
                pending.Add(id, entry);
            }
            using (var deadline = new CancellationTokenSource(timeout))
            using (var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellation, deadline.Token))
            using (linked.Token.Register(() => Finish(id, entry, null, new SdkException(cancellation.IsCancellationRequested ? "CANCELED" : "TIMEOUT", !cancellation.IsCancellationRequested))))
            {
                try
                {
                    if (!linked.IsCancellationRequested)
                    {
                        try { dispatch(json); }
                        catch { Finish(id, entry, null, new SdkException("INTERNAL_ERROR")); }
                    }
                    return await entry.Completion.Task.ConfigureAwait(false);
                }
                finally { lock (gate) { if (pending.TryGetValue(id, out var current) && ReferenceEquals(entry, current)) pending.Remove(id); } }
            }
        }
        internal void HandleMessage(string json)
        {
            if (json == null || Encoding.UTF8.GetByteCount(json) > 256 * 1024) { Interlocked.Increment(ref ignored); return; }
            JObject root;
            try
            {
                using (var reader = new JsonTextReader(new StringReader(json)) { DateParseHandling = DateParseHandling.None })
                {
                    root = JObject.Load(reader, new JsonLoadSettings { DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error });
                    if (reader.Read()) { Interlocked.Increment(ref ignored); return; }
                }
            }
            catch (JsonException) { Interlocked.Increment(ref ignored); return; }
            if (root["protocolVersion"]?.Type != JTokenType.Integer || (int)root["protocolVersion"] != 1 ||
                root["kind"]?.Type != JTokenType.String || (string)root["kind"] != "response" ||
                root["sdkSessionId"]?.Type != JTokenType.String || (string)root["sdkSessionId"] != sessionId ||
                root["requestId"]?.Type != JTokenType.String || !Guid.TryParseExact((string)root["requestId"], "D", out _) ||
                root["operation"]?.Type != JTokenType.String || root["ok"]?.Type != JTokenType.Boolean ||
                !root.ContainsKey("result") || !root.ContainsKey("error")) { Interlocked.Increment(ref ignored); return; }
            var id = (string)root["requestId"];
            Pending entry;
            lock (gate) { if (!pending.TryGetValue(id, out entry)) { Interlocked.Increment(ref ignored); return; } }
            if ((string)root["operation"] != entry.Operation) { Finish(id, entry, null, new SdkException("BRIDGE_PROTOCOL_MISMATCH")); return; }
            var ok = (bool)root["ok"];
            if (ok && root["error"].Type == JTokenType.Null)
                Finish(id, entry, root["result"].DeepClone(), null);
            else if (!ok && root["result"].Type == JTokenType.Null && root["error"] is JObject error && error["code"]?.Type == JTokenType.String && error["retryable"]?.Type == JTokenType.Boolean)
            {
                var code = (string)error["code"];
                Finish(id, entry, null, new SdkException(Errors.Contains(code) ? code : "INTERNAL_ERROR", (bool)error["retryable"]));
            }
            else Finish(id, entry, null, new SdkException("BRIDGE_PROTOCOL_MISMATCH"));
        }
        private void Finish(string id, Pending entry, JToken result, SdkException error)
        {
            lock (gate)
            {
                if (!pending.TryGetValue(id, out var current) || !ReferenceEquals(current, entry)) { Interlocked.Increment(ref ignored); return; }
                pending.Remove(id);
            }
            if (error != null) entry.Completion.TrySetException(error); else entry.Completion.TrySetResult(result);
        }
        public void Dispose()
        {
            List<Pending> abandoned;
            lock (gate) { if (disposed) return; disposed = true; abandoned = new List<Pending>(pending.Values); pending.Clear(); }
            foreach (var entry in abandoned) entry.Completion.TrySetException(new SdkException("NOT_INITIALIZED"));
        }
    }
}
