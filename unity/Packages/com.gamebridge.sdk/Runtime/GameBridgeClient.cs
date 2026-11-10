using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

namespace GameBridge
{
    public enum AuthProvider { MOCK, GOOGLE, APPLE }
    public sealed class SdkStatus
    {
        public string State { get; }
        public string SdkVersion { get; }
        public string Platform { get; }
        public ProviderMode? Mode { get; }
        public DateTimeOffset? InitializedAt { get; }
        public DateTimeOffset SnapshotAt { get; }
        internal SdkStatus(string state, ProviderMode? mode, DateTimeOffset? initialized, DateTimeOffset snapshot)
        { State = state; Mode = mode; InitializedAt = initialized; SnapshotAt = snapshot; SdkVersion = "0.1.0-dev"; Platform = "Unity"; }
    }
    public sealed class InitResult { public SdkStatus Status { get; } internal InitResult(SdkStatus status) { Status = status; } }

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
        private int generation;
        private bool disposed;
        internal event Action<GameBridgeClient> Disposed;
        internal GameBridgeClient(IWireTransport transport)
        {
            this.transport = transport ?? throw new ArgumentNullException(nameof(transport));
            registry = new RequestRegistry(transport.Dispatch, Guid.NewGuid());
            transport.Message += OnMessage;
        }
        private void OnMessage(string json) { RequestRegistry current; lock (gate) current = registry; current?.HandleMessage(json); }
        internal void Pump() { transport.Pump(); }
        public SdkStatus GetStatus() { lock (gate) return Snapshot(); }
        private SdkStatus Snapshot() => new SdkStatus(state, lastMode, initializedAt, snapshotAt);
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
                    if (registry == null) registry = new RequestRegistry(transport.Dispatch, Guid.NewGuid());
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
                var result = await request.RequestAsync("sdk.initialize", payload, TimeSpan.FromMilliseconds(value.RequestTimeoutMs)).ConfigureAwait(false);
                if (!(result is JObject obj) || obj["state"]?.Type != JTokenType.String || (string)obj["state"] != "READY" || obj["mode"]?.Type != JTokenType.String || (string)obj["mode"] != ModeString(value.Mode)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                InitResult snapshot;
                lock (gate)
                {
                    if (disposed || generation != epoch || state != "INITIALIZING") throw new SdkException("CANCELED");
                    state = "READY"; initializedAt = snapshotAt = DateTimeOffset.UtcNow; initializing = null; snapshot = new InitResult(Snapshot());
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
        private static bool SameConfig(GameBridgeConfig a, GameBridgeConfig b) => a != null && a.AppId == b.AppId && a.Mode == b.Mode && a.BackendBaseUrl == b.BackendBaseUrl && a.RequestTimeoutMs == b.RequestTimeoutMs;
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
