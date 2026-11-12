using System;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Dedicated local-mock test: no remote FCM and no credentials in logs.
public sealed class MockPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        GameBridgeClient client = null; var stage = "configuration";
        var thread = Thread.CurrentThread.ManagedThreadId; int deliveries = 0; bool wrongThread = false;
        var received = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        try
        {
            using var unity = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            using var activity = unity.GetStatic<AndroidJavaObject>("currentActivity");
            using var intent = activity.Call<AndroidJavaObject>("getIntent");
            var url = intent.Call<string>("getStringExtra", "gamebridge_mock_url");
            var key = intent.Call<string>("getStringExtra", "gamebridge_mock_key");
            var installation = intent.Call<string>("getStringExtra", "gamebridge_installation");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://10.0.2.2:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32 || !Guid.TryParse(installation, out _)) throw new InvalidOperationException("CONFIG_REQUIRED");
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000, key, "A", null, null, null, installation); key = null;
            client = GameBridgeSdk.Create(config);
            client.PushReceived += item => { if (Thread.CurrentThread.ManagedThreadId != thread) wrongThread = true; if (item.MessageId == "unity-push-test") { deliveries++; Debug.Log("GB_PUSH_RECEIVED " + deliveries); received.TrySetResult(true); } };
            stage = "initialize"; await client.InitializeAsync(config); CheckThread(thread); Log("initialize");
            stage = "login"; await client.SignInAsync(AuthProvider.MOCK); CheckThread(thread); Log("login");
            stage = "register"; var registered = await client.RegisterPushAsync(); CheckThread(thread);
            if (!registered.registered || registered.provider != "MOCK") throw new InvalidOperationException("REGISTER_FAILED");
            Debug.Log("GB_PUSH_READY");
            stage = "receive";
            if (await Task.WhenAny(received.Task, Task.Delay(60000)) != received.Task) throw new InvalidOperationException("RECEIVE_TIMEOUT");
            await Task.Delay(5000); CheckThread(thread);
            if (deliveries != 1 || wrongThread) throw new InvalidOperationException("DUPLICATE_OR_THREAD");
            Log("receive-deduplicate-main-thread");
            stage = "unregister"; await client.UnregisterPushAsync(); CheckThread(thread); Debug.Log("GB_PUSH_UNREGISTERED");
            stage = "logout"; await client.SignOutAsync(); CheckThread(thread); Debug.Log("GB_PUSH_LOGGED_OUT");
            await Task.Delay(5000); CheckThread(thread);
            if (deliveries != 1 || wrongThread) throw new InvalidOperationException("LATE_EVENT");
            Log("unregister-logout-no-late-event");
            Debug.Log("GB_PUSH_RESULT PASS LOCAL_MOCK");
        }
        catch (SdkException error) { Debug.LogError("GB_PUSH_RESULT FAIL stage=" + stage + " code=" + error.Code); }
        catch (Exception error) { Debug.LogError("GB_PUSH_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield(); Debug.LogError("GB_PUSH_RESULT NOT_RUN requires Android Player");
#endif
    }
    private static void CheckThread(int expected) { if (Thread.CurrentThread.ManagedThreadId != expected) throw new InvalidOperationException("MAIN_THREAD_MISMATCH"); }
    private static void Log(string stage) => Debug.Log("GB_PUSH_STEP " + stage + " PASS");
}
