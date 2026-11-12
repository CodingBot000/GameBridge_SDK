using System;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json;
using UnityEngine;
#if UNITY_IOS && !UNITY_EDITOR
using Unity.Notifications.iOS;
using GameBridge.iOSHost;
using System.Reflection;
#endif

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
            var syntheticKey = key; key = null;
            stage = "native-transport";
            client = GameBridgeSdk.Create(config);
            stage = "initialize"; await client.InitializeAsync(config); Log(stage, unityMainThread);
            stage = "login"; var profile = await client.SignInAsync(AuthProvider.MOCK); RejectSecret(profile, syntheticKey); Log(stage, unityMainThread);
            stage = "synthetic-host-callback";
            var hostObject = new GameObject("SyntheticHostProbe");
            var host = hostObject.AddComponent<IosPushHostAdapter>(); host.Attach(client);
            int hostEvents = 0; bool wrongThread = false;
            var hostEvent = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            client.PushReceived += push => { if (push.MessageId != "synthetic-host-message") return; hostEvents++; if (Thread.CurrentThread.ManagedThreadId != unityMainThread) wrongThread = true; hostEvent.TrySetResult(true); };
            var notification = new iOSNotification { Trigger = new iOSNotificationPushTrigger(), Data = "{\"messageId\":\"synthetic-host-message\",\"route\":\"home\"}" };
            var method = typeof(IosPushHostAdapter).GetMethod("OnReceived", BindingFlags.Instance | BindingFlags.NonPublic) ?? throw new InvalidOperationException("HOST_CALLBACK_MISSING");
            method.Invoke(host, new object[] { notification }); method.Invoke(host, new object[] { notification });
            if (await Task.WhenAny(hostEvent.Task, Task.Delay(10000)) != hostEvent.Task) throw new InvalidOperationException("HOST_CALLBACK_TIMEOUT");
            await Task.Delay(1000);
            if (hostEvents != 1 || wrongThread) throw new InvalidOperationException("HOST_CALLBACK_DUPLICATE_OR_THREAD");
            host.Detach(); Destroy(hostObject);
            Debug.Log("GB_MOCK_HOST_CALLBACK PASS");
            stage = "initial-wallet"; var before = await client.GetEntitlementsAsync();
            if (!long.TryParse(before.coinBalance, out var oldBalance)) throw new InvalidOperationException("INVALID_BALANCE");
            stage = "products"; var products = await client.GetProductsAsync();
            if (!products.Any(product => product.productId == "coins_100")) throw new InvalidOperationException("PRODUCT_NOT_FOUND"); Log(stage, unityMainThread);
            stage = "purchase"; var purchase = await client.PurchaseAsync("coins_100"); RejectSecret(purchase, syntheticKey);
            if (purchase.status != PurchaseStatus.PURCHASED || (purchase.fulfillmentStatus != FulfillmentStatus.GRANTED && purchase.fulfillmentStatus != FulfillmentStatus.ALREADY_GRANTED)) throw new InvalidOperationException("PURCHASE_NOT_GRANTED"); Log(stage, unityMainThread);
            stage = "wallet"; var after = await client.GetEntitlementsAsync();
            if (!long.TryParse(after.coinBalance, out var newBalance) || newBalance != oldBalance + 100) throw new InvalidOperationException("BALANCE_MISMATCH"); Log(stage, unityMainThread);
            stage = "logout"; await client.SignOutAsync(); Log(stage, unityMainThread);
            stage = "diagnostics"; var events = await client.GetNativeDiagnosticsAsync(); RejectSecret(events, syntheticKey);
            Debug.Log("GB_MOCK_REDACTION PASS"); syntheticKey = null;
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
    private static void RejectSecret(object value, string secret)
    {
        if (string.IsNullOrEmpty(secret) || JsonConvert.SerializeObject(value).Contains(secret))
            throw new InvalidOperationException("SENSITIVE_RESULT");
    }
    private static void Log(string stage, int expectedThread)
    {
        if (Thread.CurrentThread.ManagedThreadId != expectedThread) throw new InvalidOperationException("MAIN_THREAD_MISMATCH");
        Debug.Log("GB_MOCK_STEP " + stage + " PASS");
    }
}
