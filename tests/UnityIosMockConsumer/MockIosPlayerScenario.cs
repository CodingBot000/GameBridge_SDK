using System;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Dedicated LOCAL_MOCK test consumer, never a production app.
public sealed class MockIosPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_IOS && !UNITY_EDITOR
        GameBridgeClient client = null;
        int unityMainThread = Thread.CurrentThread.ManagedThreadId;
        string stage = "configuration";
        try
        {
            stage = "simulator-environment";
            var url = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_URL");
            var key = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_KEY");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://127.0.0.1:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32)
                throw new InvalidOperationException("CONFIG_REQUIRED");
            stage = "config-validation";
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000, key, "A");
            key = null;
            stage = "native-transport";
            client = GameBridgeSdk.Create(config);
            stage = "initialize"; await client.InitializeAsync(config); Log(stage, unityMainThread);
            stage = "login"; await client.SignInAsync(AuthProvider.MOCK); Log(stage, unityMainThread);
            stage = "initial-wallet"; var before = await client.GetEntitlementsAsync();
            if (!long.TryParse(before.coinBalance, out var oldBalance)) throw new InvalidOperationException("INVALID_BALANCE");
            stage = "products"; var products = await client.GetProductsAsync();
            if (!products.Any(product => product.productId == "coins_100")) throw new InvalidOperationException("PRODUCT_NOT_FOUND"); Log(stage, unityMainThread);
            stage = "purchase"; var purchase = await client.PurchaseAsync("coins_100");
            if (purchase.status != PurchaseStatus.PURCHASED || (purchase.fulfillmentStatus != FulfillmentStatus.GRANTED && purchase.fulfillmentStatus != FulfillmentStatus.ALREADY_GRANTED)) throw new InvalidOperationException("PURCHASE_NOT_GRANTED"); Log(stage, unityMainThread);
            stage = "wallet"; var after = await client.GetEntitlementsAsync();
            if (!long.TryParse(after.coinBalance, out var newBalance) || newBalance != oldBalance + 100) throw new InvalidOperationException("BALANCE_MISMATCH"); Log(stage, unityMainThread);
            stage = "logout"; await client.SignOutAsync(); Log(stage, unityMainThread);
            stage = "diagnostics"; var events = await client.GetNativeDiagnosticsAsync();
            if (!events.Any(item => item.Kind == DiagnosticKind.INITIALIZE && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue) ||
                !events.Any(item => item.Kind == DiagnosticKind.AUTH && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue) ||
                !events.Any(item => item.Kind == DiagnosticKind.PURCHASE && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue)) throw new InvalidOperationException("NATIVE_DIAGNOSTICS_MISSING");
            if (Thread.CurrentThread.ManagedThreadId != unityMainThread) throw new InvalidOperationException("MAIN_THREAD_MISMATCH");
            Debug.Log("GB_MOCK_MAIN_THREAD PASS");
            foreach (var item in events) if (item.RequestId.HasValue) Debug.Log("GB_MOCK_NATIVE kind=" + item.Kind + " outcome=" + item.Outcome + " requestId=" + item.RequestId.Value);
            Debug.Log("GB_MOCK_RESULT PASS LOCAL_MOCK");
        }
        catch (SdkException failure) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " code=" + failure.Code); }
        catch (Exception error) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " code=INTERNAL_ERROR type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield();
        Debug.LogError("GB_MOCK_RESULT NOT_RUN requires iOS Player");
#endif
    }
    private static void Log(string stage, int expectedThread)
    {
        if (Thread.CurrentThread.ManagedThreadId != expectedThread) throw new InvalidOperationException("MAIN_THREAD_MISMATCH");
        Debug.Log("GB_MOCK_STEP " + stage + " PASS");
    }
}
