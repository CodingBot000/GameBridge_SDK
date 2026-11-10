using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

internal static class Program
{
    private sealed class HeldTransport : IWireTransport
    {
        public event Action<string> Message;
        internal readonly List<JObject> Requests = new List<JObject>();
        public void Dispatch(string json) { Requests.Add(JObject.Parse(json)); }
        public void Pump() { }
        public void Dispose() { Message = null; }
        internal void Reply(JObject request, JObject result)
        {
            Message?.Invoke(new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = request["sdkSessionId"], ["kind"] = "response",
                ["requestId"] = request["requestId"], ["operation"] = request["operation"], ["ok"] = true,
                ["result"] = result, ["error"] = JValue.CreateNull() }.ToString(Newtonsoft.Json.Formatting.None));
        }
    }
    private static void Check(bool condition, string label) { if (!condition) throw new Exception(label); }
    private static async Task Expect(string code, Task task)
    {
        try { await task; throw new Exception("expected " + code); }
        catch (SdkException error) { Check(error.Code == code, "expected " + code + ", got " + error.Code); }
    }
    private static string Response(JObject request, string session = null, string operation = null, bool ok = true) => new JObject {
        ["protocolVersion"] = 1, ["sdkSessionId"] = session ?? (string)request["sdkSessionId"], ["kind"] = "response",
        ["requestId"] = request["requestId"], ["operation"] = operation ?? (string)request["operation"], ["ok"] = ok,
        ["result"] = ok ? (JToken)new JObject { ["state"] = "READY" } : JValue.CreateNull(),
        ["error"] = ok ? JValue.CreateNull() : (JToken)new JObject { ["code"] = "BUSY", ["retryable"] = true }
    }.ToString(Newtonsoft.Json.Formatting.None);
    private static JObject InitResponse()
    {
        var caps = new JObject();
        foreach (var name in new[] { "auth", "store", "push", "config" }) caps[name] = new JObject { ["supported"] = true, ["configured"] = true, ["mode"] = "EDITOR_OFFLINE", ["reason"] = JValue.CreateNull() };
        return new JObject { ["state"] = "READY", ["mode"] = "EDITOR_OFFLINE", ["capabilities"] = caps };
    }
    private static async Task Main()
    {
        string sent = null;
        var registry = new RequestRegistry(value => sent = value, Guid.NewGuid());
        var one = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5));
        var request = JObject.Parse(sent);
        registry.HandleMessage(Response(request, session: Guid.NewGuid().ToString("D")));
        Check(!one.IsCompleted, "stale session must be ignored");
        registry.HandleMessage(Response(request) + "{}");
        Check(!one.IsCompleted, "trailing JSON must be ignored");
        registry.HandleMessage(Response(request));
        Check((string)(await one)["state"] == "READY", "correlated response");
        registry.HandleMessage(Response(request));
        Check(registry.IgnoredMessages >= 2, "duplicate response ignored");
        var mismatch = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5));
        request = JObject.Parse(sent); registry.HandleMessage(Response(request, operation: "auth.signIn"));
        await Expect("BRIDGE_PROTOCOL_MISMATCH", mismatch);
        var malformed = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5));
        request = JObject.Parse(sent); var invalid = JObject.Parse(Response(request, ok: false)); invalid["error"] = JValue.CreateNull();
        registry.HandleMessage(invalid.ToString()); await Expect("BRIDGE_PROTOCOL_MISMATCH", malformed);
        var busy = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5));
        request = JObject.Parse(sent); registry.HandleMessage(Response(request, ok: false));
        await Expect("BUSY", busy);
        await Expect("TIMEOUT", registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromMilliseconds(30)));
        using (var cts = new CancellationTokenSource())
        {
            var canceled = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5), cts.Token);
            cts.Cancel(); await Expect("CANCELED", canceled);
        }
        var waiting = new List<Task>();
        for (var i = 0; i < 100; i++) waiting.Add(registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5)));
        await Expect("BUSY", registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5)));
        registry.Dispose();
        foreach (var task in waiting) await Expect("NOT_INITIALIZED", task);
        var fixture = JObject.Parse(System.IO.File.ReadAllText(System.IO.Path.Combine(Environment.GetEnvironmentVariable("GAMEBRIDGE_ROOT"), "contracts/fixtures/models/roundtrip.json")));
        Check(WireModels.Decode<GameBridge.UserProfile>(fixture["profile"]).displayName == "별빛 🎮", "Korean profile");
        Check(WireModels.Decode<GameBridge.StoreProduct>(fixture["product"]).priceMicros == "9223372036854775807", "64-bit string");
        var invalidProduct = (JObject)fixture["product"].DeepClone(); invalidProduct["type"] = "UNKNOWN";
        try { WireModels.Decode<GameBridge.StoreProduct>(invalidProduct); throw new Exception("unknown enum accepted"); }
        catch (SdkException error) { Check(error.Code == "BRIDGE_PROTOCOL_MISMATCH", "unknown enum"); }
        var numericPrice = (JObject)fixture["product"].DeepClone(); numericPrice["priceMicros"] = 123;
        try { WireModels.Decode<GameBridge.StoreProduct>(numericPrice); throw new Exception("numeric price accepted"); }
        catch (SdkException error) { Check(error.Code == "BRIDGE_PROTOCOL_MISMATCH", "strict numeric string"); }
        var secretError = (JObject)fixture["purchase"].DeepClone();
        secretError["error"] = new JObject { ["code"] = "AUTH_FAILED", ["message"] = "sensitive-token", ["retryable"] = false,
            ["requestId"] = JValue.CreateNull(), ["nativeCode"] = "sensitive-token", ["details"] = new JObject { ["token"] = "sensitive-token" } };
        var safeError = WireModels.Decode<GameBridge.PurchaseResult>(secretError).error;
        Check(safeError.message == "Operation failed" && safeError.nativeCode == null && safeError.details.Count == 0, "public error redaction");
        var badPush = new JObject { ["provider"] = "MOCK", ["registered"] = true, ["permission"] = "GRANTED", ["tokenFingerprint"] = new string('a', 64), ["updatedAt"] = "2026-01-01T00:00:00Z" };
        try { WireModels.Decode<GameBridge.PushRegistration>(badPush); throw new Exception("raw token-sized fingerprint accepted"); }
        catch (SdkException error) { Check(error.Code == "BRIDGE_PROTOCOL_MISMATCH", "fingerprint redaction"); }
        var missingProfile = (JObject)fixture["profile"].DeepClone(); missingProfile.Remove("displayName");
        try { WireModels.Decode<GameBridge.UserProfile>(missingProfile); throw new Exception("missing nullable field accepted"); }
        catch (SdkException error) { Check(error.Code == "BRIDGE_PROTOCOL_MISMATCH", "required nullable"); }
        var fake = new EditorOfflineTransport();
        var fakeRegistry = new RequestRegistry(fake.Dispatch, Guid.NewGuid());
        fake.Message += fakeRegistry.HandleMessage;
        await Expect("UNSUPPORTED_PROVIDER", fakeRegistry.RequestAsync("sdk.initialize", new JObject { ["providerMode"] = "PLATFORM_SANDBOX" }, TimeSpan.FromSeconds(2)));
        await fakeRegistry.RequestAsync("sdk.initialize", new JObject { ["providerMode"] = "EDITOR_OFFLINE" }, TimeSpan.FromSeconds(2));
        await fakeRegistry.RequestAsync("sdk.initialize", new JObject { ["providerMode"] = "EDITOR_OFFLINE" }, TimeSpan.FromSeconds(2));
        await Expect("ALREADY_INITIALIZED_DIFFERENT_CONFIG", fakeRegistry.RequestAsync("sdk.initialize", new JObject { ["providerMode"] = "EDITOR_OFFLINE", ["appId"] = "other" }, TimeSpan.FromSeconds(2)));
        await fakeRegistry.RequestAsync("auth.signIn", new JObject { ["provider"] = "MOCK" }, TimeSpan.FromSeconds(2));
        var transaction = Guid.NewGuid().ToString("D");
        var body = new JObject { ["productId"] = "coins_100", ["transactionId"] = transaction };
        var pending = (JObject)body.DeepClone(); pending["scenario"] = "PENDING";
        var before = await fakeRegistry.RequestAsync("store.purchase", pending, TimeSpan.FromSeconds(2));
        Check((string)before["fulfillmentStatus"] == "NOT_GRANTED", "pending must not grant");
        var cancel = (JObject)body.DeepClone(); cancel["scenario"] = "CANCELED";
        var canceledPurchase = await fakeRegistry.RequestAsync("store.purchase", cancel, TimeSpan.FromSeconds(2));
        Check((string)canceledPurchase["fulfillmentStatus"] == "NOT_GRANTED", "canceled must not grant");
        await fakeRegistry.RequestAsync("store.purchase", body, TimeSpan.FromSeconds(2));
        var duplicate = await fakeRegistry.RequestAsync("store.purchase", body, TimeSpan.FromSeconds(2));
        Check((string)duplicate["fulfillmentStatus"] == "ALREADY_GRANTED", "fake duplicate");
        var wallet = await fakeRegistry.RequestAsync("store.entitlements", new JObject(), TimeSpan.FromSeconds(2));
        Check((string)wallet["coinBalance"] == "100", "fake wallet grants once");
        await fakeRegistry.RequestAsync("push.permission", new JObject(), TimeSpan.FromSeconds(2));
        var registration = await fakeRegistry.RequestAsync("push.register", new JObject(), TimeSpan.FromSeconds(2));
        Check((string)registration["provider"] == "MOCK", "fake push");
        await fakeRegistry.RequestAsync("sdk.shutdown", new JObject(), TimeSpan.FromSeconds(2));
        var stopped = await fakeRegistry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(2));
        Check((string)stopped["state"] == "SHUTDOWN", "shutdown status");
        fakeRegistry.Dispose(); fake.Dispose();
        var config = new GameBridge.GameBridgeConfig("demo", GameBridge.ProviderMode.EditorOffline, null);
        var facade = new GameBridge.GameBridgeClient(new EditorOfflineTransport());
        Check(facade.GetStatus().Mode == null, "initial mode unknown");
        await facade.InitializeAsync(config);
        Check(facade.GetStatus().State == "READY", "facade initialized");
        Check(facade.GetCapabilities().Known && facade.GetCapabilities().Features["auth"].Supported, "capability snapshot");
        var profile = await facade.SignInAsync(GameBridge.AuthProvider.MOCK); Check(profile.provider == "MOCK", "facade sign-in");
        Check((await facade.GetProductsAsync()).Count == 2, "facade products");
        var purchase = await facade.PurchaseAsync("coins_100"); Check(purchase.fulfillmentStatus == GameBridge.FulfillmentStatus.GRANTED, "facade fake purchase");
        Check((await facade.GetEntitlementsAsync()).coinBalance == "100", "facade wallet");
        Check((await facade.RestoreSessionAsync()).signedIn, "facade restore");
        Check((await facade.SyncPurchasesAsync(GameBridge.SyncReason.USER_RESTORE)).entitlements.coinBalance == "100", "facade sync");
        Check((await facade.RequestPushPermissionAsync()).permission == "GRANTED", "fake permission");
        Check((await facade.RegisterPushAsync()).tokenFingerprint == "mock-fingerprint", "fake registration");
        await facade.UnregisterPushAsync(); Check((await facade.GetServiceConfigAsync()).source == "DEFAULT", "fake config");
        Check(facade.GetDiagnostics().PendingCount == 0, "diagnostic snapshot");
        await facade.SignOutAsync(); await facade.ShutdownAsync(); await facade.ShutdownAsync();
        Check(facade.GetStatus().State == "SHUTDOWN", "facade shutdown");
        await facade.InitializeAsync(config); facade.Dispose();
        var held = new HeldTransport(); var concurrent = new GameBridge.GameBridgeClient(held);
        using (var callerCancellation = new CancellationTokenSource())
        {
            var firstInit = concurrent.InitializeAsync(config, callerCancellation.Token);
            var secondInit = concurrent.InitializeAsync(config);
            Check(held.Requests.Count == 1, "same configuration joins initialization");
            try { _ = concurrent.InitializeAsync(new GameBridge.GameBridgeConfig("other", GameBridge.ProviderMode.EditorOffline, null)); throw new Exception("different config accepted"); }
            catch (SdkException error) { Check(error.Code == "ALREADY_INITIALIZED_DIFFERENT_CONFIG", "different config"); }
            callerCancellation.Cancel(); await Expect("CANCELED", firstInit);
            held.Reply(held.Requests[0], InitResponse());
            await secondInit;
            var oldSession = (string)held.Requests[0]["sdkSessionId"];
            var shutdown = concurrent.ShutdownAsync();
            held.Reply(held.Requests[1], new JObject { ["state"] = "SHUTDOWN" }); await shutdown;
            var reinit = concurrent.InitializeAsync(config);
            Check((string)held.Requests[2]["sdkSessionId"] != oldSession, "new session after shutdown");
            held.Reply(held.Requests[2], InitResponse()); await reinit;
        }
        concurrent.Dispose();
        Console.WriteLine("Registry, facade and offline fake smoke passed; no Unity runtime or real provider tested");
    }
}
