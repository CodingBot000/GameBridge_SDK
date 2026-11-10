using System;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;

internal static class LegacyConsumer
{
    // Signatures available at the P08 source baseline; never supplies real credentials.
    private static void Bind(GameBridgeClient client)
    {
        Func<CancellationToken, Task> logout = client.SignOutAsync;
        Func<CancellationToken, Task<SessionSnapshot>> restore = client.RestoreSessionAsync;
        Func<string, CancellationToken, Task<PurchaseResult>> purchase = client.PurchaseAsync;
        client.PushOpened += value => { _ = value.Route; };
        _ = logout; _ = restore; _ = purchase;
    }
    private static void Main()
    {
        var config = new GameBridgeConfig("demo", ProviderMode.EditorOffline, null, 30000);
        var error = new SdkException("BUSY", true);
        if (config.RequestTimeoutMs != 30000 || !error.Retryable) throw new Exception("legacy API mismatch");
        Console.WriteLine("Legacy C# consumer source: PASS");
    }
}
