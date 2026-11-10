using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;

internal static class Program
{
    private static async Task Main()
    {
        const int warmup = 5, samples = 100;
        var times = new List<double>();
        var config = new GameBridgeConfig("stress", ProviderMode.EditorOffline, null);
        for (var index = 0; index < warmup + samples; index++)
        {
            var watch = Stopwatch.StartNew();
            var client = new GameBridgeClient(new EditorOfflineTransport());
            await client.InitializeAsync(config);
            if (client.GetStatus().State != "READY") throw new Exception("initialization did not reach READY");
            if ((await client.GetProductsAsync()).Count != 2) throw new Exception("fake catalog mismatch");
            await client.ShutdownAsync(); watch.Stop();
            if (client.GetStatus().State != "SHUTDOWN" || client.GetDiagnostics().PendingCount != 0) throw new Exception("lifecycle cleanup failed");
            client.Dispose();
            if (index >= warmup) times.Add(watch.Elapsed.TotalMilliseconds);
        }
        times.Sort();
        var result = new {
            scope = "standalone-dotnet-editor-offline-fake", os = RuntimeInformation.OSDescription,
            runtime = RuntimeInformation.FrameworkDescription, architecture = RuntimeInformation.ProcessArchitecture.ToString(),
            sourceHead = Environment.GetEnvironmentVariable("GAMEBRIDGE_SOURCE_HEAD"),
            workingTree = "HEAD plus uncommitted changes may be present", warmup, samples,
            operation = "create + initialize + fake product query + shutdown", unit = "milliseconds",
            p50 = times[(samples * 50 + 99) / 100 - 1], p95 = times[(samples * 95 + 99) / 100 - 1],
            limitation = "Not Unity runtime, device performance, memory profiling, or a real provider."
        };
        var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        System.IO.File.WriteAllText(Environment.GetEnvironmentVariable("GAMEBRIDGE_STRESS_OUTPUT"), json + "\n");
        Console.WriteLine(json);
    }
}
