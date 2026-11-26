using System;
using System.Collections.Generic;
using System.Linq;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

internal static class BridgeDecoderChecks
{
    private static readonly string[] Names = { "auth", "store", "push", "config" };

    internal static void Run()
    {
        CheckDiagnostics();
        CheckCapabilities();
        Console.WriteLine("Bridge decoder contracts PASS");
    }

    private static void CheckDiagnostics()
    {
        var id = Guid.NewGuid();
        var expectedTimestamp = new DateTimeOffset(2026, 1, 2, 3, 4, 5, TimeSpan.FromHours(9));
        JObject Entry() => new JObject
        {
            ["kind"] = "AUTH", ["outcome"] = "STARTED", ["timestamp"] = "2026-01-02T03:04:05+09:00",
            ["requestId"] = id.ToString("D"), ["ignored"] = true,
        };
        JToken Payload(params JToken[] entries) => new JObject { ["events"] = new JArray(entries), ["ignoredRoot"] = true };

        Check(DiagnosticDecoder.Decode(Payload()).Count == 0, "empty diagnostics");
        var events = new List<JToken>();
        var kinds = Enum.GetNames(typeof(DiagnosticKind));
        var outcomes = Enum.GetNames(typeof(DiagnosticOutcome));
        for (int i = 0; i < 200; i++)
        {
            var entry = Entry();
            entry["kind"] = kinds[i % kinds.Length];
            entry["outcome"] = outcomes[i % outcomes.Length];
            if (i == 0) entry["requestId"] = JValue.CreateNull();
            events.Add(entry);
        }
        var decoded = DiagnosticDecoder.Decode(Payload(events.ToArray()));
        Check(decoded.Count == 200 && decoded[0].RequestId == null && decoded[1].RequestId == id, "count and request IDs");
        Check(decoded.All(e => e.Timestamp == expectedTimestamp && e.Timestamp.Offset == expectedTimestamp.Offset), "timestamp and offset");
        for (int i = 0; i < decoded.Count; i++)
            Check(decoded[i].Kind.ToString() == kinds[i % kinds.Length] &&
                decoded[i].Outcome.ToString() == outcomes[i % outcomes.Length], "diagnostic ordering");
        Check(((ICollection<NativeDiagnosticEvent>)decoded).IsReadOnly, "diagnostics must be read-only");
        events.Add(Entry());
        Reject(() => DiagnosticDecoder.Decode(Payload(events.ToArray())));
        foreach (var token in new JToken[] { new JArray(), new JObject(), new JObject { ["events"] = 1 }, Payload(Entry(), new JValue(1)) })
            Reject(() => DiagnosticDecoder.Decode(token));

        foreach (var pair in new (string Key, JToken Value)[] {
            ("kind", "auth"), ("kind", "1"), ("kind", "UNKNOWN"), ("kind", 1),
            ("outcome", "started"), ("outcome", "0"), ("outcome", "UNKNOWN"),
            ("timestamp", 1), ("timestamp", "bad"), ("requestId", 1), ("requestId", id.ToString("N")),
        })
        {
            var entry = Entry();
            entry[pair.Key] = pair.Value;
            Reject(() => DiagnosticDecoder.Decode(Payload(Entry(), entry)));
        }
        var missing = Entry();
        missing.Remove("requestId");
        Reject(() => DiagnosticDecoder.Decode(Payload(missing)));
    }

    private static void CheckCapabilities()
    {
        JObject Payload(string wireMode)
        {
            var root = new JObject { ["extra"] = 42 };
            foreach (var name in Names)
                root[name] = new JObject {
                    ["supported"] = false, ["configured"] = true, ["mode"] = wireMode,
                    ["reason"] = name == "auth" ? new JValue("fixture") : JValue.CreateNull(), ["extra"] = 42,
                };
            return root;
        }

        foreach (var pair in new[] {
            (ProviderMode.EditorOffline, "EDITOR_OFFLINE"), (ProviderMode.LocalMock, "LOCAL_MOCK"),
            (ProviderMode.XcodeStoreKit, "XCODE_STOREKIT"), (ProviderMode.PlatformSandbox, "PLATFORM_SANDBOX"),
        })
        {
            var before = DateTimeOffset.UtcNow;
            var value = CapabilityDecoder.Decode(Payload(pair.Item2), pair.Item1);
            Check(value.Known && value.SnapshotAt >= before && value.SnapshotAt <= DateTimeOffset.UtcNow, "known and snapshot");
            Check(value.Features.Keys.SequenceEqual(Names), "fixed features, ignore extensions");
            Check(value.Features.Values.All(f => f.Mode == pair.Item1 && !f.Supported && f.Configured), "preserve feature flags");
            Check(value.Features["auth"].Reason == "fixture" && value.Features["push"].Reason == null, "reason string/null");
        }

        foreach (var pair in new (string Key, JToken Value)[] {
            ("supported", null), ("supported", 1), ("configured", null), ("configured", "true"),
            ("mode", null), ("mode", 1), ("mode", "PLATFORM_SANDBOX"), ("reason", null), ("reason", 1),
        })
        {
            var payload = Payload("LOCAL_MOCK");
            var feature = (JObject)payload["auth"];
            if (pair.Value == null) feature.Remove(pair.Key);
            else feature[pair.Key] = pair.Value;
            Reject(() => CapabilityDecoder.Decode(payload, ProviderMode.LocalMock));
        }
        Reject(() => CapabilityDecoder.Decode(new JArray(), (ProviderMode)99));
        Reject(() => CapabilityDecoder.Decode(new JObject(), ProviderMode.LocalMock));
        var wrongFeature = Payload("LOCAL_MOCK");
        wrongFeature["store"] = "invalid";
        Reject(() => CapabilityDecoder.Decode(wrongFeature, ProviderMode.LocalMock));
        Reject(() => CapabilityDecoder.Decode(Payload("LOCAL_MOCK"), (ProviderMode)99), "INVALID_ARGUMENT");

        var input = new Dictionary<string, CapabilityStatus> { ["auth"] = new CapabilityStatus(true, true, ProviderMode.LocalMock, null) };
        var snapshot = new SdkCapabilities(true, input, DateTimeOffset.UtcNow);
        input.Clear();
        Check(snapshot.Features.Count == 1 && ((IDictionary<string, CapabilityStatus>)snapshot.Features).IsReadOnly, "copy and read-only snapshot");
    }

    private static void Reject(Action action, string code = "BRIDGE_PROTOCOL_MISMATCH")
    {
        try { action(); }
        catch (SdkException error) when (error.Code == code) { return; }
        throw new InvalidOperationException("Expected " + code);
    }

    private static void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }
}
