using System;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Dedicated local-mock test: no remote FCM and no credentials in logs.
public sealed class MockIosPlayerScenario : MonoBehaviour
{
    private bool paused;
    private readonly TaskCompletionSource<bool> resumed = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
    private void OnApplicationPause(bool value)
    {
        if (value) { paused = true; Debug.Log("GB_PUSH_BACKGROUND"); }
        else if (paused) { Debug.Log("GB_PUSH_FOREGROUND"); resumed.TrySetResult(true); }
    }
    private async void Start()
    {
#if UNITY_IOS && !UNITY_EDITOR
        GameBridgeClient client = null; var stage = "configuration";
        var thread = Thread.CurrentThread.ManagedThreadId; int deliveries = 0; bool wrongThread = false;
        var received = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var reconnected = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        int offlineDeliveries = 0; int bDeliveries = 0;
        var bReceived = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        try
        {
            var url = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_URL");
            var key = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_KEY");
            var installation = Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_INSTALLATION");
            if (string.IsNullOrEmpty(url) || !url.StartsWith("http://127.0.0.1:", StringComparison.Ordinal) || string.IsNullOrEmpty(key) || key.Length < 32 || !Guid.TryParse(installation, out _)) throw new InvalidOperationException("CONFIG_REQUIRED");
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000, key, "A", null, null, null, installation); key = null;
            client = GameBridgeSdk.Create(config);
            client.PushReceived += item => { if (Thread.CurrentThread.ManagedThreadId != thread) wrongThread = true; if (item.MessageId == "unity-push-test") { deliveries++; Debug.Log("GB_PUSH_RECEIVED " + deliveries); received.TrySetResult(true); } if (item.MessageId == "unity-offline-test") offlineDeliveries++; if (item.MessageId == "unity-reconnected-test") { Debug.Log("GB_PUSH_RECONNECTED_RECEIVED"); reconnected.TrySetResult(true); } if (item.MessageId == "unity-session-b") { bDeliveries++; Debug.Log("GB_PUSH_B_RECEIVED " + bDeliveries); bReceived.TrySetResult(true); } };
            stage = "initialize"; await client.InitializeAsync(config); CheckThread(thread); Log("initialize");
            var sessionA = LateCallbackProbe.Session(client);
            stage = "login"; await client.SignInAsync(AuthProvider.MOCK); CheckThread(thread); Log("login");
            stage = "register"; var registered = await client.RegisterPushAsync(); CheckThread(thread);
            if (!registered.registered || registered.provider != "MOCK") throw new InvalidOperationException("REGISTER_FAILED");
            Debug.Log("GB_PUSH_READY");
            stage = "receive";
            if (await Task.WhenAny(received.Task, Task.Delay(60000)) != received.Task) throw new InvalidOperationException("RECEIVE_TIMEOUT");
            await Task.Delay(5000); CheckThread(thread);
            if (deliveries != 1 || wrongThread) throw new InvalidOperationException("DUPLICATE_OR_THREAD");
            Log("receive-deduplicate-main-thread");
            stage = "background"; Debug.Log("GB_PUSH_WAIT_BACKGROUND");
            if (await Task.WhenAny(resumed.Task, Task.Delay(60000)) != resumed.Task) throw new InvalidOperationException("LIFECYCLE_TIMEOUT");
            CheckThread(thread); Log("background-foreground-main-thread");
            stage = "network"; Debug.Log("GB_PUSH_WAIT_OFFLINE");
            if (await Task.WhenAny(reconnected.Task, Task.Delay(90000)) != reconnected.Task) throw new InvalidOperationException("RECONNECT_TIMEOUT");
            await Task.Delay(2000); CheckThread(thread);
            if (offlineDeliveries != 0 || wrongThread) throw new InvalidOperationException("OFFLINE_DELIVERY_OR_THREAD");
            Log("network-recovery-online-only");
            stage = "unregister"; await client.UnregisterPushAsync(); CheckThread(thread); Debug.Log("GB_PUSH_UNREGISTERED");
            stage = "logout"; await client.SignOutAsync(); CheckThread(thread); Debug.Log("GB_PUSH_LOGGED_OUT");
            await Task.Delay(5000); CheckThread(thread);
            if (deliveries != 1 || wrongThread) throw new InvalidOperationException("LATE_EVENT");
            Log("unregister-logout-no-late-event");
            stage = "switch-session"; await client.ShutdownAsync(); client.Dispose(); client = null; CheckThread(thread);
            var configB = new GameBridgeConfig("gamebridge-sample", ProviderMode.LocalMock, url, 30000,
                Environment.GetEnvironmentVariable("GAMEBRIDGE_IOS_MOCK_KEY"), "B", null, null, null, installation);
            client = GameBridgeSdk.Create(configB);
            client.PushReceived += item => {
                if (Thread.CurrentThread.ManagedThreadId != thread) wrongThread = true;
                if (item.MessageId == "unity-push-test" || item.MessageId == "unity-offline-test" || item.MessageId == "unity-late-a") deliveries++;
                if (item.MessageId == "unity-session-b") { bDeliveries++; Debug.Log("GB_PUSH_B_RECEIVED " + bDeliveries); bReceived.TrySetResult(true); }
            };
            await client.InitializeAsync(configB); await client.SignInAsync(AuthProvider.MOCK); await client.RegisterPushAsync(); CheckThread(thread);
            stage = "synthetic-late-callback"; await LateCallbackProbe.InjectAndVerify(client, sessionA); CheckThread(thread);
            Debug.Log("GB_PUSH_B_READY");
            if (await Task.WhenAny(bReceived.Task, Task.Delay(60000)) != bReceived.Task) throw new InvalidOperationException("SESSION_B_TIMEOUT");
            await Task.Delay(4000); CheckThread(thread);
            if (bDeliveries != 1 || deliveries != 1 || wrongThread) throw new InvalidOperationException("SESSION_OR_LATE_EVENT");
            await client.UnregisterPushAsync(); await client.SignOutAsync(); CheckThread(thread);
            Log("session-switch-no-stale-event");
            Debug.Log("GB_PUSH_RESULT PASS LOCAL_MOCK");
        }
        catch (SdkException error) { Debug.LogError("GB_PUSH_RESULT FAIL stage=" + stage + " code=" + error.Code); }
        catch (Exception error) { Debug.LogError("GB_PUSH_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield(); Debug.LogError("GB_PUSH_RESULT NOT_RUN requires iOS Player");
#endif
    }
    private static void CheckThread(int expected) { if (Thread.CurrentThread.ManagedThreadId != expected) throw new InvalidOperationException("MAIN_THREAD_MISMATCH"); }
    private static void Log(string stage) => Debug.Log("GB_PUSH_STEP " + stage + " PASS");
}
