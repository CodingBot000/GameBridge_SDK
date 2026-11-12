using System;
using System.Linq;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

// Isolated sample consumer: inputs and button callbacks are test-driven, not pointer or visual QA.
public sealed class MockPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        NativeDemo demo = null; string stage = "configuration";
        try
        {
            using var unity = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            using var activity = unity.GetStatic<AndroidJavaObject>("currentActivity");
            using var intent = activity.Call<AndroidJavaObject>("getIntent");
            var url = intent.Call<string>("getStringExtra", "gamebridge_mock_url");
            var key = intent.Call<string>("getStringExtra", "gamebridge_mock_key");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://10.0.2.2:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32) throw new InvalidOperationException("CONFIG_REQUIRED");
            var syntheticKey = key;
            new GameObject("SampleEventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            demo = gameObject.AddComponent<NativeDemo>(); await Until(() => GameObject.Find("GameBridgeNativeCanvas") != null);
            var canvas = GameObject.Find("GameBridgeNativeCanvas");
            Input(canvas, "Backend URL (required)").text = url;
            var keyField = Input(canvas, "Local development key (runtime only)"); keyField.text = key; key = null;
            stage = "initialize"; await Press(canvas, "Initialize"); await Until(() => demo.Client != null && Texts(canvas).Any(t => t.StartsWith("LOCAL_MOCK ready", StringComparison.Ordinal)));
            if (!string.IsNullOrEmpty(keyField.text)) throw new InvalidOperationException("KEY_NOT_CLEARED"); Log(stage);
            stage = "login"; await Press(canvas, "Sign in"); await Until(() => Texts(canvas).Any(t => t == "Signed in"));
            var session = await demo.Client.RestoreSessionAsync(); RejectSecret(session, syntheticKey); if (!session.signedIn) throw new InvalidOperationException("NOT_SIGNED_IN"); Log(stage);
            var before = await demo.Client.GetEntitlementsAsync(); if (!long.TryParse(before.coinBalance, out var oldBalance)) throw new InvalidOperationException("INVALID_BALANCE");
            stage = "products"; await Press(canvas, "Load products"); await Until(() => Texts(canvas).Any(t => t.Contains("coins_100"))); Log(stage);
            stage = "purchase"; await Press(canvas, "Buy coins"); await Until(() => Texts(canvas).Any(t => t.Contains("Coins: " + (oldBalance + 100)))); Log(stage);
            stage = "wallet"; var after = await demo.Client.GetEntitlementsAsync(); RejectSecret(after, syntheticKey);
            if (!long.TryParse(after.coinBalance, out var newBalance) || newBalance != oldBalance + 100) throw new InvalidOperationException("BALANCE_MISMATCH"); Log(stage);
            stage = "logout"; await Press(canvas, "Sign out"); await Until(() => Texts(canvas).Any(t => t == "Signed out")); Log(stage);
            stage = "diagnostics"; var events = await demo.Client.GetNativeDiagnosticsAsync(); RejectSecret(events, syntheticKey);
            foreach (var item in events) if (item.RequestId.HasValue) Debug.Log("GB_MOCK_NATIVE kind=" + item.Kind + " outcome=" + item.Outcome + " requestId=" + item.RequestId.Value);
            Debug.Log("GB_MOCK_REDACTION PASS"); Debug.Log("GB_NATIVE_DEMO_FLOW PASS"); Debug.Log("GB_MOCK_RESULT PASS LOCAL_MOCK");
        }
        catch (SdkException failure) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " code=" + failure.Code); }
        catch (Exception error) { Debug.LogError("GB_MOCK_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { if (demo != null) Destroy(demo); }
#else
        await Task.Yield(); Debug.LogError("GB_MOCK_RESULT NOT_RUN requires Android Player");
#endif
    }
    private static InputField Input(GameObject canvas, string hint) => canvas.GetComponentsInChildren<InputField>(true).Single(item => (item.placeholder as Text)?.text == hint);
    private static string[] Texts(GameObject canvas) => canvas.GetComponentsInChildren<Text>(true).Select(item => item.text).ToArray();
    private static async Task Press(GameObject canvas, string caption)
    {
        var button = canvas.GetComponentsInChildren<Button>(true).Single(item => item.GetComponentsInChildren<Text>(true).Any(text => text.text == caption));
        await Until(() => button.interactable); button.onClick.Invoke();
    }
    private static async Task Until(Func<bool> condition)
    {
        var deadline = DateTime.UtcNow.AddSeconds(25);
        while (!condition() && DateTime.UtcNow < deadline) await Task.Delay(50);
        if (!condition()) throw new InvalidOperationException("SAMPLE_TIMEOUT");
    }
    private static void RejectSecret(object value, string secret) { if (JsonConvert.SerializeObject(value).Contains(secret)) throw new InvalidOperationException("SENSITIVE_RESULT"); }
    private static void Log(string stage) => Debug.Log("GB_MOCK_STEP " + stage + " PASS");
}
