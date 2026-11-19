using System;
using System.Threading.Tasks;
using GameBridge.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

internal static class Program
{
    private static void Check(bool value, string description) { if (!value) throw new Exception(description); }
    private static string Event(Guid session, string id) => new JObject {
        ["protocolVersion"] = 1, ["sdkSessionId"] = session.ToString("D"), ["kind"] = "event",
        ["eventId"] = Guid.NewGuid().ToString("D"), ["type"] = "PushReceived", ["occurredAt"] = "2026-11-12T00:00:00Z",
        ["payload"] = new JObject { ["messageId"] = id, ["route"] = "home", ["campaignId"] = JValue.CreateNull() }
    }.ToString(Formatting.None);
    private static async Task Main()
    {
        var sessionA = Guid.NewGuid(); var sessionB = Guid.NewGuid(); JObject sent = null;
        using var registryA = new RequestRegistry(text => sent = JObject.Parse(text), sessionA);
        var pending = registryA.RequestAsync("config.get", new JObject(), TimeSpan.FromMilliseconds(40));
        try { await pending; throw new Exception("missing timeout"); }
        catch (SdkException error) { Check(error.Code == "TIMEOUT", "wrong timeout"); }
        Check(sent != null && registryA.PendingCount == 0, "request was not retired");
        var response = new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = sessionA.ToString("D"), ["kind"] = "response",
            ["requestId"] = sent["requestId"], ["operation"] = "config.get", ["ok"] = true, ["result"] = new JObject(), ["error"] = JValue.CreateNull() }.ToString(Formatting.None);
        registryA.HandleMessage(response); registryA.HandleMessage(response);
        Check(pending.IsFaulted && registryA.PendingCount == 0 && registryA.IgnoredMessages >= 2, "late response completed or retained request");
        registryA.Dispose();
        using var registryB = new RequestRegistry(_ => { }, sessionB); int events = 0;
        registryB.PushUpdated += (_, _) => events++;
        registryB.HandleMessage(Event(sessionA, "old-session"));
        Check(events == 0 && registryB.IgnoredMessages == 1, "stale session event delivered");
        registryB.HandleMessage(Event(sessionB, "current-session"));
        Check(events == 1, "current session event missing");
        registryB.Dispose(); registryB.HandleMessage(Event(sessionB, "after-dispose"));
        Check(events == 1, "disposed session event delivered");
        Console.WriteLine("PASS: late response, stale session and disposed event; managed unit only");
    }
}
