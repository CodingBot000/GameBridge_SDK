using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

namespace GameBridge
{
    public enum AuthProvider { MOCK, GOOGLE, APPLE }
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
        { State = state; Mode = mode; InitializedAt = initialized; SnapshotAt = snapshot; Capabilities = capabilities; SdkVersion = "0.1.0-dev"; Platform = "Unity"; }
    }
    public sealed class InitResult { public SdkStatus Status { get; } internal InitResult(SdkStatus status) { Status = status; } }

    internal interface IHostPushDriver
    {
        Task<PushPermission> RequestPermissionAsync(CancellationToken cancellation);
        Task<PushRegistration> RegisterAsync(CancellationToken cancellation);
    }

    /// <summary>Public facade; call lifecycle methods from Unity's main thread.</summary>
    public sealed class GameBridgeClient : IDisposable
    {
        private readonly object gate = new object();
        private readonly IWireTransport transport;
        private RequestRegistry registry;
        private string state = "UNINITIALIZED";
        private GameBridgeConfig config;
        private Task<InitResult> initializing;
        private Task shuttingDown;
        private DateTimeOffset? initializedAt;
        private ProviderMode? lastMode;
        private DateTimeOffset snapshotAt = DateTimeOffset.UtcNow;
        private SdkCapabilities capabilities = new SdkCapabilities(false, new Dictionary<string, CapabilityStatus>(), DateTimeOffset.UtcNow);
        private int generation;
        private bool disposed;
        private IHostPushDriver hostPushDriver;
        internal event Action<GameBridgeClient> Disposed;
        public event Action<PurchaseUpdate> PurchaseUpdated;
        public event Action<PushUpdate> PushReceived;
        public event Action<PushUpdate> PushOpened;
        internal GameBridgeClient(IWireTransport transport)
        {
            this.transport = transport ?? throw new ArgumentNullException(nameof(transport));
            registry = CreateRegistry();
            transport.Message += OnMessage;
        }
        private RequestRegistry CreateRegistry()
        {
            var created = new RequestRegistry(transport.Dispatch, Guid.NewGuid());
            created.PurchaseUpdated += update => { lock (gate) { if (disposed || state != "READY" || !ReferenceEquals(registry, created)) return; } PurchaseUpdated?.Invoke(update); };
            created.PushUpdated += (update, opened) => {
                lock (gate) { if (disposed || state != "READY" || !ReferenceEquals(registry, created)) return; }
                if (opened) PushOpened?.Invoke(update); else PushReceived?.Invoke(update);
            };
            return created;
        }
        private void OnMessage(string json) { RequestRegistry current; lock (gate) current = registry; current?.HandleMessage(json); }
        internal void Pump() { transport.Pump(); }
        public SdkStatus GetStatus() { lock (gate) return Snapshot(); }
        private SdkStatus Snapshot() => new SdkStatus(state, lastMode, initializedAt, snapshotAt, capabilities);
        public SdkCapabilities GetCapabilities() { lock (gate) return capabilities; }
        public DiagnosticsSnapshot GetDiagnostics() { lock (gate) return new DiagnosticsSnapshot(lastMode, registry?.PendingCount ?? 0, registry?.IgnoredMessages ?? 0, DateTimeOffset.UtcNow); }
        public Task<InitResult> InitializeAsync(GameBridgeConfig value, CancellationToken cancellation = default)
        {
            if (cancellation.IsCancellationRequested) throw new SdkException("CANCELED");
            if (value == null) throw new SdkException("INVALID_ARGUMENT");
            try { value.Validate(); } catch (ConfigurationException) { throw new SdkException("CONFIG_REQUIRED"); }
            Task<InitResult> shared;
            TaskCompletionSource<InitResult> starter = null;
            RequestRegistry request = null;
            int epoch = 0;
            lock (gate)
            {
                if (disposed) throw new SdkException("NOT_INITIALIZED");
                if (state == "SHUTTING_DOWN") throw new SdkException("BUSY", true);
                if (state == "INITIALIZING" || state == "READY")
                {
                    if (!SameConfig(config, value)) throw new SdkException("ALREADY_INITIALIZED_DIFFERENT_CONFIG");
                    shared = state == "READY" ? Task.FromResult(new InitResult(Snapshot())) : initializing;
                }
                else
                {
                    if (registry == null) registry = CreateRegistry();
                    request = registry; config = value; lastMode = value.Mode; state = "INITIALIZING"; snapshotAt = DateTimeOffset.UtcNow; epoch = ++generation;
                    starter = new TaskCompletionSource<InitResult>(TaskCreationOptions.RunContinuationsAsynchronously);
                    initializing = starter.Task; shared = initializing;
                }
            }
            if (starter != null) _ = CompleteInitialization(request, value, epoch, starter);
            return WaitForCaller(shared, cancellation);
        }
        private async Task CompleteInitialization(RequestRegistry request, GameBridgeConfig value, int epoch, TaskCompletionSource<InitResult> completion)
        {
            try
            {
                var payload = new JObject { ["appId"] = value.AppId, ["providerMode"] = ModeString(value.Mode), ["backendBaseUrl"] = value.BackendBaseUrl == null ? JValue.CreateNull() : (JToken)value.BackendBaseUrl, ["requestTimeoutMs"] = value.RequestTimeoutMs };
                if (value.Mode == ProviderMode.LocalMock)
                {
                    payload["developmentKey"] = value.DevelopmentKey;
                    payload["mockSubject"] = value.MockSubject;
                }
                if (value.Mode == ProviderMode.PlatformSandbox && value.GoogleServerClientId != null) payload["googleServerClientId"] = value.GoogleServerClientId;
                if (value.Mode == ProviderMode.PlatformSandbox && value.CoinsStoreProductId != null)
                    payload["storeProductIds"] = new JObject { ["coins_100"] = value.CoinsStoreProductId, ["premium_unlock"] = value.PremiumStoreProductId };
                if (value.Mode == ProviderMode.PlatformSandbox && value.InstallationId != null) payload["installationId"] = value.InstallationId;
                var result = await request.RequestAsync("sdk.initialize", payload, TimeSpan.FromMilliseconds(value.RequestTimeoutMs)).ConfigureAwait(false);
                if (!(result is JObject obj) || obj["state"]?.Type != JTokenType.String || (string)obj["state"] != "READY" || obj["mode"]?.Type != JTokenType.String || (string)obj["mode"] != ModeString(value.Mode)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                var nextCapabilities = ReadCapabilities(obj["capabilities"], value.Mode);
                InitResult snapshot;
                lock (gate)
                {
                    if (disposed || generation != epoch || state != "INITIALIZING") throw new SdkException("CANCELED");
                    state = "READY"; initializedAt = snapshotAt = DateTimeOffset.UtcNow; capabilities = nextCapabilities; initializing = null; snapshot = new InitResult(Snapshot());
                }
                completion.TrySetResult(snapshot);
            }
            catch (Exception error)
            {
                lock (gate) { if (!disposed && generation == epoch && state == "INITIALIZING") { state = "UNINITIALIZED"; config = null; initializing = null; snapshotAt = DateTimeOffset.UtcNow; } }
                completion.TrySetException(error is SdkException ? error : new SdkException("INTERNAL_ERROR"));
            }
        }
        public async Task<UserProfile> SignInAsync(AuthProvider provider, CancellationToken cancellation = default)
        {
            if (!Enum.IsDefined(typeof(AuthProvider), provider)) throw new SdkException("INVALID_ARGUMENT");
            return WireModels.Decode<UserProfile>(await Invoke("auth.signIn", new JObject { ["provider"] = provider.ToString() }, false, cancellation));
        }
        public async Task SignOutAsync(CancellationToken cancellation = default) { await Invoke("auth.signOut", new JObject(), false, cancellation); }
        public async Task<SessionSnapshot> RestoreSessionAsync(CancellationToken cancellation = default)
        { return WireModels.Decode<SessionSnapshot>(await Invoke("auth.restore", new JObject(), false, cancellation)); }
        public async Task<IReadOnlyList<StoreProduct>> GetProductsAsync(CancellationToken cancellation = default)
        {
            var result = await Invoke("store.products", new JObject(), false, cancellation);
            if (!(result is JArray array)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
            var products = new List<StoreProduct>(); foreach (var item in array) products.Add(WireModels.Decode<StoreProduct>(item)); return products.AsReadOnly();
        }
        public async Task<PurchaseResult> PurchaseAsync(string productId, CancellationToken cancellation = default)
        {
            if (string.IsNullOrWhiteSpace(productId)) throw new SdkException("INVALID_ARGUMENT");
            var payload = new JObject { ["productId"] = productId };
            lock (gate) { if (config != null && config.Mode == ProviderMode.EditorOffline) payload["transactionId"] = Guid.NewGuid().ToString("D"); }
            return WireModels.Decode<PurchaseResult>(await Invoke("store.purchase", payload, true, cancellation));
        }
        public async Task<EntitlementSnapshot> GetEntitlementsAsync(CancellationToken cancellation = default)
        { return WireModels.Decode<EntitlementSnapshot>(await Invoke("store.entitlements", new JObject(), false, cancellation)); }
        public async Task<PurchaseSyncResult> SyncPurchasesAsync(SyncReason reason, CancellationToken cancellation = default)
        {
            if (!Enum.IsDefined(typeof(SyncReason), reason)) throw new SdkException("INVALID_ARGUMENT");
            return WireModels.Decode<PurchaseSyncResult>(await Invoke("store.sync", new JObject { ["reason"] = reason.ToString() }, false, cancellation));
        }
        internal void AttachHostPushDriver(IHostPushDriver driver) { lock (gate) { if (disposed) throw new SdkException("NOT_INITIALIZED"); hostPushDriver = driver; } }
        internal void DetachHostPushDriver(IHostPushDriver driver) { lock (gate) { if (ReferenceEquals(hostPushDriver, driver)) hostPushDriver = null; } }
        private IHostPushDriver ActiveHostPushDriver()
        {
            lock (gate) { if (disposed || state != "READY") throw new SdkException("NOT_INITIALIZED"); return hostPushDriver; }
        }
        public async Task<PushPermission> RequestPushPermissionAsync(CancellationToken cancellation = default)
        {
            if (cancellation.IsCancellationRequested) throw new SdkException("CANCELED");
            var host = ActiveHostPushDriver();
            return host != null ? await host.RequestPermissionAsync(cancellation) : WireModels.Decode<PushPermission>(await Invoke("push.permission", new JObject(), true, cancellation));
        }
        public async Task<PushRegistration> RegisterPushAsync(CancellationToken cancellation = default)
        {
            if (cancellation.IsCancellationRequested) throw new SdkException("CANCELED");
            var host = ActiveHostPushDriver();
            return host != null ? await host.RegisterAsync(cancellation) : WireModels.Decode<PushRegistration>(await Invoke("push.register", new JObject(), false, cancellation));
        }
        public async Task UnregisterPushAsync(CancellationToken cancellation = default) { await Invoke("push.unregister", new JObject(), false, cancellation); }
        public async Task<ServiceConfig> GetServiceConfigAsync(CancellationToken cancellation = default)
        { return WireModels.Decode<ServiceConfig>(await Invoke("config.get", new JObject(), false, cancellation)); }
        internal async Task<string> ForwardHostPushTokenAsync(string token, CancellationToken cancellation = default)
        {
            if (string.IsNullOrWhiteSpace(token)) throw new SdkException("INVALID_ARGUMENT");
            var result = await Invoke("host.pushToken", new JObject { ["provider"] = "APNS", ["token"] = token }, false, cancellation);
            if (!(result is JObject obj) || obj["registered"]?.Type != JTokenType.Boolean || !(bool)obj["registered"] ||
                obj["tokenFingerprint"]?.Type != JTokenType.String || !System.Text.RegularExpressions.Regex.IsMatch((string)obj["tokenFingerprint"], "^[0-9a-f]{12}$"))
                throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
            return (string)obj["tokenFingerprint"];
        }
        internal async Task ForwardHostPushEventAsync(string messageId, string route, string campaignId, bool opened)
        {
            var payload = new JObject { ["messageId"] = messageId, ["route"] = route, ["campaignId"] = campaignId == null ? JValue.CreateNull() : (JToken)campaignId };
            await Invoke(opened ? "host.pushOpened" : "host.pushReceived", payload, false, default);
        }
        private async Task<JToken> Invoke(string operation, JObject payload, bool interactive, CancellationToken cancellation)
        {
            RequestRegistry request; int epoch; TimeSpan timeout;
            lock (gate)
            {
                if (disposed || state != "READY" || registry == null) throw new SdkException("NOT_INITIALIZED");
                request = registry; epoch = generation; timeout = interactive ? TimeSpan.FromSeconds(180) : TimeSpan.FromMilliseconds(config.RequestTimeoutMs);
            }
            var result = await request.RequestAsync(operation, payload, timeout, cancellation);
            lock (gate) { if (disposed || epoch != generation || state != "READY") throw new SdkException("NOT_INITIALIZED"); }
            return result;
        }
        public Task ShutdownAsync()
        {
            TaskCompletionSource<bool> starter = null; RequestRegistry request = null; Task shared = null; bool immediate = false;
            lock (gate)
            {
                if (disposed || state == "SHUTDOWN") return Task.CompletedTask;
                if (state == "SHUTTING_DOWN") return shuttingDown;
                if (state == "UNINITIALIZED")
                {
                    state = "SHUTDOWN"; snapshotAt = DateTimeOffset.UtcNow; generation++; request = registry; registry = null; immediate = true;
                }
                else
                {
                    state = "SHUTTING_DOWN"; snapshotAt = DateTimeOffset.UtcNow; generation++; request = registry;
                    starter = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously); shuttingDown = starter.Task; shared = shuttingDown;
                }
            }
            if (immediate) { request?.Dispose(); return Task.CompletedTask; }
            _ = CompleteShutdown(request, starter); return shared;
        }
        private async Task CompleteShutdown(RequestRegistry request, TaskCompletionSource<bool> completion)
        {
            Exception failure = null;
            try { await request.RequestAsync("sdk.shutdown", new JObject(), TimeSpan.FromSeconds(30)).ConfigureAwait(false); }
            catch (Exception error) { failure = error is SdkException ? error : new SdkException("INTERNAL_ERROR"); }
            finally
            {
                request.Dispose();
                lock (gate) { if (ReferenceEquals(registry, request)) registry = null; if (!disposed) { state = "SHUTDOWN"; config = null; initializedAt = null; snapshotAt = DateTimeOffset.UtcNow; } shuttingDown = null; initializing = null; }
            }
            if (failure == null) completion.TrySetResult(true); else completion.TrySetException(failure);
        }
        public void Dispose()
        {
            RequestRegistry request;
            lock (gate) { if (disposed) return; disposed = true; generation++; state = "SHUTDOWN"; snapshotAt = DateTimeOffset.UtcNow; request = registry; registry = null; }
            request?.Dispose(); transport.Message -= OnMessage; transport.Dispose(); Disposed?.Invoke(this);
        }
        private static SdkCapabilities ReadCapabilities(JToken token, ProviderMode mode)
        {
            if (!(token is JObject root)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
            var result = new Dictionary<string, CapabilityStatus>();
            foreach (var name in new[] { "auth", "store", "push", "config" })
            {
                if (!(root[name] is JObject feature) || feature["supported"]?.Type != JTokenType.Boolean || feature["configured"]?.Type != JTokenType.Boolean ||
                    feature["mode"]?.Type != JTokenType.String || (string)feature["mode"] != ModeString(mode) || !feature.ContainsKey("reason") ||
                    (feature["reason"].Type != JTokenType.String && feature["reason"].Type != JTokenType.Null)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                result[name] = new CapabilityStatus((bool)feature["supported"], (bool)feature["configured"], mode,
                    feature["reason"].Type == JTokenType.Null ? null : (string)feature["reason"]);
            }
            return new SdkCapabilities(true, result, DateTimeOffset.UtcNow);
        }
        private static bool SameConfig(GameBridgeConfig a, GameBridgeConfig b) => a != null && a.AppId == b.AppId && a.Mode == b.Mode && a.BackendBaseUrl == b.BackendBaseUrl && a.RequestTimeoutMs == b.RequestTimeoutMs && a.DevelopmentKey == b.DevelopmentKey && a.MockSubject == b.MockSubject && a.GoogleServerClientId == b.GoogleServerClientId && a.CoinsStoreProductId == b.CoinsStoreProductId && a.PremiumStoreProductId == b.PremiumStoreProductId && a.InstallationId == b.InstallationId;
        private static string ModeString(ProviderMode mode)
        {
            switch (mode) { case ProviderMode.EditorOffline: return "EDITOR_OFFLINE"; case ProviderMode.LocalMock: return "LOCAL_MOCK"; case ProviderMode.XcodeStoreKit: return "XCODE_STOREKIT"; case ProviderMode.PlatformSandbox: return "PLATFORM_SANDBOX"; default: throw new SdkException("INVALID_ARGUMENT"); }
        }
        private static async Task<T> WaitForCaller<T>(Task<T> shared, CancellationToken cancellation)
        {
            if (!cancellation.CanBeCanceled) return await shared;
            var canceled = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            using (cancellation.Register(() => canceled.TrySetResult(true)))
            {
                if (await Task.WhenAny(shared, canceled.Task) != shared) throw new SdkException("CANCELED");
                return await shared;
            }
        }
    }
}
