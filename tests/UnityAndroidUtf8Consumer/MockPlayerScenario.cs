using System;
using System.Linq;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json;
using UnityEngine;

// Dedicated LOCAL_MOCK test consumer, never a production app.
public sealed class MockPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        GameBridgeClient client = null;
        string stage = "configuration";
        try
        {
            stage = "android-intent";
            using var unity = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            using var activity = unity.GetStatic<AndroidJavaObject>("currentActivity");
            using var intent = activity.Call<AndroidJavaObject>("getIntent");
            var url = intent.Call<string>("getStringExtra", "gamebridge_mock_url");
            var key = intent.Call<string>("getStringExtra", "gamebridge_mock_key");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://10.0.2.2:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32)
                throw new InvalidOperationException("CONFIG_REQUIRED");
            stage = "config-validation";
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000, key, "A");
            var syntheticKey = key; key = null;
            stage = "native-transport";
            client = GameBridgeSdk.Create(config);
            stage = "initialize"; await client.InitializeAsync(config); Log(stage);
            stage = "login"; var profile = await client.SignInAsync(AuthProvider.MOCK); RejectSecret(profile, syntheticKey); Log(stage);
            stage = "utf8-jni";
            const string unicode = "한글 🎮🚀";
            var utf8Event = new TaskCompletionSource<string>(TaskCreationOptions.RunContinuationsAsynchronously);
            int mainThread = System.Threading.Thread.CurrentThread.ManagedThreadId;
            client.PushReceived += push => { if (System.Threading.Thread.CurrentThread.ManagedThreadId != mainThread) utf8Event.TrySetException(new InvalidOperationException("THREAD")); else utf8Event.TrySetResult(push.MessageId); };
            using (var facade = new AndroidJavaClass("com.gamebridge.bridge.BridgeFacade"))
                if (facade.CallStatic<string>("forwardNotification", unicode, "home", null, false) != "DELIVER") throw new InvalidOperationException("JNI_EVENT_NOT_DELIVERED");
            if (await Task.WhenAny(utf8Event.Task, Task.Delay(10000)) != utf8Event.Task || await utf8Event.Task != unicode) throw new InvalidOperationException("JNI_UTF8_MISMATCH");
            Debug.Log("GB_UTF8_JNI_ROUNDTRIP PASS");
            stage = "initial-wallet"; var before = await client.GetEntitlementsAsync();
            if (!long.TryParse(before.coinBalance, out var oldBalance)) throw new InvalidOperationException("INVALID_BALANCE");
            stage = "products"; var products = await client.GetProductsAsync();
            if (!products.Any(product => product.productId == "coins_100")) throw new InvalidOperationException("PRODUCT_NOT_FOUND"); Log(stage);
            stage = "purchase"; var purchase = await client.PurchaseAsync("coins_100"); RejectSecret(purchase, syntheticKey);
            if (purchase.status != PurchaseStatus.PURCHASED || (purchase.fulfillmentStatus != FulfillmentStatus.GRANTED && purchase.fulfillmentStatus != FulfillmentStatus.ALREADY_GRANTED)) throw new InvalidOperationException("PURCHASE_NOT_GRANTED"); Log(stage);
            stage = "wallet"; var after = await client.GetEntitlementsAsync();
            if (!long.TryParse(after.coinBalance, out var newBalance) || newBalance != oldBalance + 100) throw new InvalidOperationException("BALANCE_MISMATCH"); Log(stage);
            stage = "logout"; await client.SignOutAsync(); Log(stage);
            stage = "diagnostics"; var events = await client.GetNativeDiagnosticsAsync(); RejectSecret(events, syntheticKey);
            Debug.Log("GB_MOCK_REDACTION PASS"); syntheticKey = null;
            if (!events.Any(item => item.Kind == DiagnosticKind.INITIALIZE && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue) ||
                !events.Any(item => item.Kind == DiagnosticKind.AUTH && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue) ||
                !events.Any(item => item.Kind == DiagnosticKind.PURCHASE && item.Outcome == DiagnosticOutcome.SUCCEEDED && item.RequestId.HasValue)) throw new InvalidOperationException("NATIVE_DIAGNOSTICS_MISSING");
            foreach (var item in events) if (item.RequestId.HasValue) Debug.Log("GB_MOCK_NATIVE kind=" + item.Kind + " outcome=" + item.Outcome + " requestId=" + item.RequestId.Value);
            Debug.Log("GB_MOCK_RESULT PASS LOCAL_MOCK");
        }
        catch (SdkException failure) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " code=" + failure.Code); }
        catch (Exception error) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " code=INTERNAL_ERROR type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield();
        Debug.LogError("GB_MOCK_RESULT NOT_RUN requires Android Player");
#endif
    }
    private static void RejectSecret(object value, string secret)
    {
        if (string.IsNullOrEmpty(secret) || JsonConvert.SerializeObject(value).Contains(secret))
            throw new InvalidOperationException("SENSITIVE_RESULT");
    }
    private static void Log(string stage) => Debug.Log("GB_MOCK_STEP " + stage + " PASS");
}
