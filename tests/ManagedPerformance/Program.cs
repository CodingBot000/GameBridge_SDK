using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json.Linq;

internal static class Program
{
    const int Warmup = 20, Samples = 100, InFlight = 8;
    sealed class Transport : IWireTransport
    {
        readonly EditorOfflineTransport inner = new EditorOfflineTransport();
        public event Action<string> Message;
        public Transport() { inner.Message += Forward; }
        void Forward(string value) => Message?.Invoke(value);
        public void Dispatch(string value) => inner.Dispatch(value);
        public void Pump() => inner.Pump();
        public void Dispose() { inner.Message -= Forward; inner.Dispose(); Message = null; }
    }
    static double Milliseconds(long start) => (Stopwatch.GetTimestamp() - start) * 1000.0 / Stopwatch.Frequency;
    [MethodImpl(MethodImplOptions.NoInlining)]
    static async Task<(double init, double callback, double shutdown, WeakReference client, WeakReference transport)> ClientCycle()
    {
        long start = Stopwatch.GetTimestamp();
        var transport = new Transport(); var client = new GameBridgeClient(transport);
        await client.InitializeAsync(new GameBridgeConfig("performance", ProviderMode.EditorOffline, null));
        double init = Milliseconds(start); start = Stopwatch.GetTimestamp();
        var products = await client.GetProductsAsync(); double callback = Milliseconds(start);
        if (products.Count != 2 || client.GetStatus().State != "READY") throw new Exception("CLIENT_RESPONSE_INVARIANT");
        start = Stopwatch.GetTimestamp(); await client.ShutdownAsync(); client.Dispose(); double shutdown = Milliseconds(start);
        if (client.GetDiagnostics().PendingCount != 0 || client.GetStatus().State != "SHUTDOWN") throw new Exception("CLIENT_CLEANUP_INVARIANT");
        return (init, callback, shutdown, new WeakReference(client), new WeakReference(transport));
    }
    static string Response(string request)
    {
        var q = JObject.Parse(request);
        return new JObject { ["protocolVersion"] = 1, ["kind"] = "response", ["sdkSessionId"] = q["sdkSessionId"],
            ["requestId"] = q["requestId"], ["operation"] = q["operation"], ["ok"] = true,
            ["result"] = new JObject { ["fixture"] = true }, ["error"] = JValue.CreateNull() }.ToString(Newtonsoft.Json.Formatting.None);
    }
    static async Task<double> RegistryCycle()
    {
        long start = Stopwatch.GetTimestamp(); var sent = new List<string>();
        using var registry = new RequestRegistry(sent.Add, Guid.NewGuid());
        var tasks = Enumerable.Range(0, InFlight).Select(_ => registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5))).ToArray();
        if (registry.PendingCount != InFlight || sent.Count != InFlight) throw new Exception("INFLIGHT_INVARIANT");
        for (int i = sent.Count - 1; i >= 0; i--) registry.HandleMessage(Response(sent[i]));
        await Task.WhenAll(tasks); registry.HandleMessage(Response(sent[0]));
        using var cancel = new CancellationTokenSource();
        var canceled = registry.RequestAsync("sdk.status", new JObject(), TimeSpan.FromSeconds(5), cancel.Token);
        string delayed = Response(sent[sent.Count - 1]); cancel.Cancel();
        try { await canceled; throw new Exception("CANCELLATION_NOT_OBSERVED"); }
        catch (SdkException error) when (error.Code == "CANCELED") { }
        registry.HandleMessage(delayed);
        if (registry.PendingCount != 0 || registry.IgnoredMessages != 2 || tasks.Any(t => !t.IsCompletedSuccessfully)) throw new Exception("REGISTRY_CLEANUP_INVARIANT");
        return Milliseconds(start);
    }
    static object Summary(List<double> raw)
    {
        var x = raw.OrderBy(v => v).ToArray();
        if (x.Length != Samples || x.Any(v => double.IsNaN(v) || double.IsInfinity(v) || v < 0)) throw new Exception("INVALID_TIMING_SAMPLES");
        return new { samples = x.Length, unit = "milliseconds", p50 = x[(Samples * 50 + 99) / 100 - 1],
            p95 = x[(Samples * 95 + 99) / 100 - 1], max = x[x.Length - 1], samplesMilliseconds = raw };
    }
    static async Task<int> Main()
    {
        var path = Environment.GetEnvironmentVariable("GAMEBRIDGE_PERFORMANCE_OUTPUT");
        try
        {
            var init = new List<double>(); var callback = new List<double>(); var shutdown = new List<double>(); var registryTimes = new List<double>();
            var clients = new List<WeakReference>(); var transports = new List<WeakReference>();
            for (int i = 0; i < Warmup + Samples; i++)
            {
                var c = await ClientCycle(); double r = await RegistryCycle();
                if (i >= Warmup) { init.Add(c.init); callback.Add(c.callback); shutdown.Add(c.shutdown); registryTimes.Add(r); clients.Add(c.client); transports.Add(c.transport); }
            }
            GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
            int liveClients = clients.Count(x => x.IsAlive), liveTransports = transports.Count(x => x.IsAlive);
            if (liveClients != 0 || liveTransports != 0) throw new Exception("DISPOSED_MANAGED_OBJECT_RETAINED");
            var report = new { status = "PASS", scope = "standalone .NET SDK Core + EDITOR_OFFLINE fake transport; not Unity Player/Native IPC", sourceHead = Environment.GetEnvironmentVariable("GAMEBRIDGE_SOURCE_HEAD"),
                os = RuntimeInformation.OSDescription, runtime = RuntimeInformation.FrameworkDescription, architecture = RuntimeInformation.ProcessArchitecture.ToString(),
                build = "Release/Optimize=true", clock = "Stopwatch monotonic", clockFrequency = Stopwatch.Frequency, warmup = Warmup, samples = Samples,
                timings = new { createInitialize = Summary(init), callbackProductQuery = Summary(callback), shutdownDispose = Summary(shutdown), registryEightInflightDuplicateCancelLate = Summary(registryTimes) },
                measuredWorkload = new { inFlightPerCycle = InFlight, successfulResponses = Samples * InFlight, expectedCancellations = Samples, ignoredDuplicateResponses = Samples, ignoredLateResponses = Samples, finalPending = 0, liveClients, liveTransports },
                limit = "No Unity startup/jank/native memory profile or real provider measurement; no performance improvement comparison." };
            string json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
            System.IO.File.WriteAllText(path, json + "\n"); Console.WriteLine("MANAGED_PERFORMANCE PASS"); return 0;
        }
        catch (Exception error)
        {
            System.IO.File.WriteAllText(path, JsonSerializer.Serialize(new { status = "FAIL", errorType = error.GetType().Name, code = error.Message }) + "\n");
            Console.WriteLine("MANAGED_PERFORMANCE FAIL"); return 1;
        }
    }
}
