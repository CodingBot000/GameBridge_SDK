using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

internal static class Program
{
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
        Console.WriteLine("Registry and offline fake smoke passed; no Unity runtime or real provider tested");
    }
}
