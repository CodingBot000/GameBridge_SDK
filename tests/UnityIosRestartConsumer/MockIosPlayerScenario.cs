using System;
using System.Threading;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

public sealed class MockIosPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_IOS && !UNITY_EDITOR
        GameBridgeClient client = null; string stage = "configuration"; int main = Thread.CurrentThread.ManagedThreadId;
        try
        {
            var url = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_URL");
            var key = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_KEY");
            var phase = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_PHASE");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://127.0.0.1:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32 || (phase != "prepare" && phase != "recover")) throw new InvalidOperationException("CONFIG_REQUIRED");
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000, key, "A"); key = null;
            client = GameBridgeSdk.Create(config); stage = "initialize"; await client.InitializeAsync(config); Check(main);
            if (phase == "prepare")
            {
                stage = "login"; await client.SignInAsync(AuthProvider.MOCK); Check(main);
                stage = "purchase"; bool deferred = false;
                try { await client.PurchaseAsync("coins_100"); }
                catch (SdkException error) { deferred = error.Code == "NETWORK_UNAVAILABLE" || error.Code == "TIMEOUT"; }
                Check(main); if (!deferred) throw new InvalidOperationException("EXPECTED_DEFERRED_PURCHASE");
                Debug.Log("GB_RESTART_PENDING PASS pid=" + getpid()); await Task.Delay(180000);
                throw new InvalidOperationException("EXPECTED_PROCESS_TERMINATION");
            }
            stage = "restore"; var session = await client.RestoreSessionAsync(); Check(main);
            if (!session.signedIn || !session.sessionRestored) throw new InvalidOperationException("RESTORE_FAILED");
            stage = "sync"; var result = await client.SyncPurchasesAsync(SyncReason.APP_RESUME); Check(main);
            if (result.examinedCount != 1 || result.recoveredCount != 1 || result.deferredCount != 0 || result.failureCount != 0 || result.entitlements.coinBalance != "100") throw new InvalidOperationException("PENDING_RECOVERY_FAILED");
            stage = "resync"; var again = await client.SyncPurchasesAsync(SyncReason.APP_RESUME); Check(main);
            if (again.examinedCount != 0 || again.entitlements.coinBalance != "100") throw new InvalidOperationException("DUPLICATE_RECOVERY");
            stage = "logout"; await client.SignOutAsync(); Check(main);
            Debug.Log("GB_RESTART_RESULT PASS LOCAL_MOCK MAIN_THREAD pid=" + getpid());
        }
        catch (SdkException error) { Debug.LogError("GB_RESTART_RESULT FAIL stage=" + stage + " code=" + error.Code); }
        catch (Exception error) { Debug.LogError("GB_RESTART_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield(); Debug.LogError("GB_RESTART_RESULT NOT_RUN requires iOS Player");
#endif
    }
    [DllImport("__Internal")] private static extern int getpid();
    private static void Check(int expected) { if (Thread.CurrentThread.ManagedThreadId != expected) throw new InvalidOperationException("MAIN_THREAD_MISMATCH"); }
}
