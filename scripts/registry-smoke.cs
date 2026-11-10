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
        Console.WriteLine("Registry smoke passed: correlation, errors, timeout, cancellation, capacity, disposal");
    }
}
