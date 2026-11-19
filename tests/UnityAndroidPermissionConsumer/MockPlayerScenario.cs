using System;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Isolated Android OS permission test. No real account, Firebase or remote service.
public sealed class MockPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        GameBridgeClient client = null; string stage = "initialize";
        try
        {
            var config = new GameBridgeConfig("permission-test", ProviderMode.PlatformSandbox, "https://example.invalid", 15000,
                null, null, "synthetic-client", null, null, "00000000-0000-4000-8000-000000000001");
            client = GameBridgeSdk.Create(config); await client.InitializeAsync(config);
            stage = "first-request"; Debug.Log("GB_PERMISSION_REQUEST_FIRST");
            var first = await client.RequestPushPermissionAsync();
            if (first.permission != "DENIED") throw new InvalidOperationException("EXPECTED_DENIED");
            Debug.Log("GB_PERMISSION_FIRST_DENIED PASS");
            stage = "registration"; bool blocked = false;
            try { await client.RegisterPushAsync(); Debug.Log("GB_PERMISSION_REGISTRATION_UNEXPECTED_SUCCESS"); } catch (SdkException error) { Debug.Log("GB_PERMISSION_REGISTRATION_CODE " + error.Code); blocked = error.Code == "PERMISSION_DENIED"; }
            if (!blocked) throw new InvalidOperationException("REGISTRATION_NOT_BLOCKED");
            Debug.Log("GB_PERMISSION_REGISTRATION_BLOCKED PASS");
            stage = "second-request"; Debug.Log("GB_PERMISSION_REQUEST_SECOND");
            var second = await client.RequestPushPermissionAsync();
            if (second.permission != "DENIED") throw new InvalidOperationException("EXPECTED_SECOND_DENIED");
            Debug.Log("GB_PERMISSION_SECOND_DENIED PASS");
            Debug.Log("GB_PERMISSION_RESULT PASS ANDROID_OS_DENIED");
        }
        catch (SdkException error) { Debug.LogError("GB_PERMISSION_RESULT FAIL stage=" + stage + " code=" + error.Code); }
        catch (Exception error) { Debug.LogError("GB_PERMISSION_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield(); Debug.LogError("GB_PERMISSION_RESULT NOT_RUN requires Android Player");
#endif
    }
}
