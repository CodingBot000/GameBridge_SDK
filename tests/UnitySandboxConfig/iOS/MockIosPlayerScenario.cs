using System;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Dedicated configuration test. Never opens a real account or remote service.
public sealed class MockIosPlayerScenario : MonoBehaviour
{
    private async void Start()
    {
#if UNITY_IOS && !UNITY_EDITOR
        GameBridgeClient client = null; var stage = "initialize";
        try
        {
            var config = new GameBridgeConfig("configuration-test", ProviderMode.PlatformSandbox, "https://example.invalid");
            client = GameBridgeSdk.Create(config); await client.InitializeAsync(config);
            var capabilities = client.GetCapabilities();
            if (!capabilities.Known || capabilities.Features["store"].Configured || capabilities.Features["store"].Reason != "coinsStoreProductId, premiumStoreProductId required") throw new InvalidOperationException("STORE_CAPABILITY");
            if (capabilities.Features["push"].Configured || capabilities.Features["push"].Reason != "installationId required") throw new InvalidOperationException("PUSH_CAPABILITY");
            Debug.Log("GB_SANDBOX_CONFIG_CAPABILITIES PASS");
            stage = "missing-store-products"; bool rejected = false;
            try { await client.GetProductsAsync(); }
            catch (SdkException error) { rejected = error.Code == "CONFIG_REQUIRED"; }
            if (!rejected) throw new InvalidOperationException("MISSING_PRODUCTS_NOT_REJECTED");
            Debug.Log("GB_SANDBOX_CONFIG_NO_FALLBACK PASS");
            Debug.Log("GB_SANDBOX_CONFIG_RESULT PASS IOS");
        }
        catch (SdkException error) { Debug.LogError("GB_SANDBOX_CONFIG_RESULT FAIL stage=" + stage + " code=" + error.Code); }
        catch (Exception error) { Debug.LogError("GB_SANDBOX_CONFIG_RESULT FAIL stage=" + stage + " type=" + error.GetType().Name); }
        finally { client?.Dispose(); }
#else
        await Task.Yield(); Debug.LogError("GB_SANDBOX_CONFIG_RESULT NOT_RUN requires iOS Player");
#endif
    }
}
