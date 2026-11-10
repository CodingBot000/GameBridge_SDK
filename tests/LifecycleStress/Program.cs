using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading.Tasks;
using System.Reflection;
using Newtonsoft.Json.Linq;
using GameBridge;
using GameBridge.Core;

internal static class Program
{
    private sealed class QueuedPushTransport : IWireTransport
    {
        private readonly EditorOfflineTransport inner = new EditorOfflineTransport();
        public event Action<string> Message;
        public QueuedPushTransport() { inner.Message += Forward; }
        private void Forward(string value) { Message?.Invoke(value); }
        public void Dispatch(string json)
        {
            var request = JObject.Parse(json);
            if ((string)request["operation"] == "sdk.initialize")
                Message?.Invoke(new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = request["sdkSessionId"], ["kind"] = "event",
                    ["eventId"] = Guid.NewGuid().ToString("D"), ["type"] = "PushReceived", ["occurredAt"] = "2026-11-10T00:00:00Z",
                    ["payload"] = new JObject { ["messageId"] = Guid.NewGuid().ToString("D"), ["route"] = "home", ["campaignId"] = JValue.CreateNull() } }.ToString(Newtonsoft.Json.Formatting.None));
            inner.Dispatch(json);
        }
        public void Pump() { inner.Pump(); }
        public void Dispose() { inner.Message -= Forward; inner.Dispose(); Message = null; }
    }
    private static int QueueCount(GameBridgeClient client)
    {
        var field = typeof(GameBridgeClient).GetField("pendingPushEvents", BindingFlags.Instance | BindingFlags.NonPublic);
        return ((System.Collections.ICollection)field.GetValue(client)).Count;
    }
    [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
    private static async Task<(double elapsed, WeakReference client, WeakReference transport)> Cycle(GameBridgeConfig config)
    {
        var watch = Stopwatch.StartNew();
        var transport = new QueuedPushTransport(); var client = new GameBridgeClient(transport);
        await client.InitializeAsync(config);
        if (client.GetStatus().State != "READY" || QueueCount(client) != 1) throw new Exception("initialization or queued push mismatch");
        if ((await client.GetProductsAsync()).Count != 2) throw new Exception("fake catalog mismatch");
        await client.ShutdownAsync(); watch.Stop();
        if (client.GetStatus().State != "SHUTDOWN" || client.GetDiagnostics().PendingCount != 0 || QueueCount(client) != 0)
            throw new Exception("registry or push queue cleanup failed");
        client.Dispose();
        return (watch.Elapsed.TotalMilliseconds, new WeakReference(client), new WeakReference(transport));
    }
    private static async Task Main()
    {
        const int warmup = 5, samples = 100;
        var times = new List<double>();
        var config = new GameBridgeConfig("stress", ProviderMode.EditorOffline, null);
        var clients = new List<WeakReference>(); var transports = new List<WeakReference>();
        for (var index = 0; index < warmup + samples; index++)
        {
            var cycle = await Cycle(config);
            if (index >= warmup) { times.Add(cycle.elapsed); clients.Add(cycle.client); transports.Add(cycle.transport); }
        }
        GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
        var liveClients = clients.Count(item => item.IsAlive); var liveTransports = transports.Count(item => item.IsAlive);
        if (liveClients != 0 || liveTransports != 0) throw new Exception($"disposed objects retained: clients={liveClients}, transports={liveTransports}");
        times.Sort();
        var result = new {
            scope = "standalone-dotnet-editor-offline-fake", os = RuntimeInformation.OSDescription,
            runtime = RuntimeInformation.FrameworkDescription, architecture = RuntimeInformation.ProcessArchitecture.ToString(),
            sourceHead = Environment.GetEnvironmentVariable("GAMEBRIDGE_SOURCE_HEAD"),
            workingTree = "HEAD plus uncommitted changes may be present", warmup, samples,
            operation = "create + initialize + queued fake push + product query + shutdown", liveClients, liveTransports, unit = "milliseconds",
            p50 = times[(samples * 50 + 99) / 100 - 1], p95 = times[(samples * 95 + 99) / 100 - 1],
            limitation = "Not Unity runtime, device performance, long-duration memory profiling, or a real provider."
        };
        var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        System.IO.File.WriteAllText(Environment.GetEnvironmentVariable("GAMEBRIDGE_STRESS_OUTPUT"), json + "\n");
        Console.WriteLine(json);
    }
}
