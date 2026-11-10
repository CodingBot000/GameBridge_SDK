using System;
using GameBridge.Core;
#if (UNITY_ANDROID || UNITY_IOS) && !UNITY_EDITOR
using GameBridge.Platforms;
#endif
using UnityEngine;

namespace GameBridge
{
    /// <summary>Creates one facade and one persistent main-thread callback pump.</summary>
    public static class GameBridgeSdk
    {
        private static GameBridgeClient active;
        private static GameBridgeDriver driver;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            var old = active; active = null;
            var previous = driver; driver = null;
            if (previous != null) { previous.Detach(); UnityEngine.Object.Destroy(previous.gameObject); }
            if (old != null) { old.Disposed -= OnDisposed; old.Dispose(); }
        }
        public static GameBridgeClient Create(GameBridgeConfig config)
        {
            if (config == null) throw new SdkException("INVALID_ARGUMENT");
            try { config.Validate(); } catch (ConfigurationException) { throw new SdkException("CONFIG_REQUIRED"); }
            if (active != null) throw new SdkException("BUSY", true);
#if UNITY_EDITOR || UNITY_ANDROID || UNITY_IOS
            IWireTransport transport;
#endif
#if UNITY_EDITOR
            if (config.Mode != ProviderMode.EditorOffline) throw new SdkException("UNSUPPORTED_PROVIDER");
            transport = new EditorOfflineTransport();
#elif UNITY_ANDROID
            if (config.Mode == ProviderMode.EditorOffline || config.Mode == ProviderMode.XcodeStoreKit) throw new SdkException("UNSUPPORTED_PROVIDER");
            transport = new AndroidTransport();
#elif UNITY_IOS
            if (config.Mode == ProviderMode.EditorOffline) throw new SdkException("UNSUPPORTED_PROVIDER");
            transport = new IosTransport();
#else
            throw new SdkException("UNSUPPORTED_PLATFORM");
#endif
#if UNITY_EDITOR || UNITY_ANDROID || UNITY_IOS
            var client = new GameBridgeClient(transport);
            GameObject host = null;
            try
            {
                host = new GameObject("GameBridge.Dispatcher");
                UnityEngine.Object.DontDestroyOnLoad(host);
                driver = host.AddComponent<GameBridgeDriver>();
                driver.Attach(client);
                active = client; client.Disposed += OnDisposed;
                return client;
            }
            catch
            {
                client.Dispose();
                if (host != null) UnityEngine.Object.Destroy(host);
                throw;
            }
#endif
        }
        private static void OnDisposed(GameBridgeClient client)
        {
            if (!ReferenceEquals(active, client)) return;
            active = null;
            if (driver != null)
            {
                var previous = driver; driver = null; previous.Detach();
                UnityEngine.Object.Destroy(previous.gameObject);
            }
        }
    }
    internal sealed class GameBridgeDriver : MonoBehaviour
    {
        private GameBridgeClient client;
        internal void Attach(GameBridgeClient value) { client = value; }
        internal void Detach() { client = null; }
        private void Update() { client?.Pump(); }
        private void OnDestroy() { var owner = client; client = null; owner?.Dispose(); }
    }
}
