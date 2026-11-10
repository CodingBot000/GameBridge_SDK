using System;
using System.Collections.Generic;

namespace GameBridge
{
    public enum ProviderMode { EditorOffline, LocalMock, XcodeStoreKit, PlatformSandbox }

    public sealed class ConfigurationException : Exception
    {
        public IReadOnlyList<string> InvalidKeys { get; }

        public ConfigurationException(IReadOnlyList<string> invalidKeys)
            : base("CONFIG_REQUIRED: " + string.Join(", ", invalidKeys))
        {
            InvalidKeys = invalidKeys;
        }
    }

    public sealed class GameBridgeConfig
    {
        public string AppId { get; }
        public ProviderMode Mode { get; }
        public string BackendBaseUrl { get; }
        public int RequestTimeoutMs { get; }
        // Development-only credential. Do not serialize this into assets or logs.
        public string DevelopmentKey { get; }
        public string MockSubject { get; }
        public string GoogleServerClientId { get; }
        public string CoinsStoreProductId { get; }
        public string PremiumStoreProductId { get; }
        public string InstallationId { get; }

        public GameBridgeConfig(string appId, ProviderMode mode, string backendBaseUrl, int requestTimeoutMs = 30000)
            : this(appId, mode, backendBaseUrl, requestTimeoutMs, null, "A") { }

        public GameBridgeConfig(string appId, ProviderMode mode, string backendBaseUrl, int requestTimeoutMs, string developmentKey, string mockSubject)
            : this(appId, mode, backendBaseUrl, requestTimeoutMs, developmentKey, mockSubject, null) { }

        public GameBridgeConfig(string appId, ProviderMode mode, string backendBaseUrl, int requestTimeoutMs, string developmentKey, string mockSubject, string googleServerClientId)
            : this(appId, mode, backendBaseUrl, requestTimeoutMs, developmentKey, mockSubject, googleServerClientId, null, null) { }

        public GameBridgeConfig(string appId, ProviderMode mode, string backendBaseUrl, int requestTimeoutMs, string developmentKey, string mockSubject, string googleServerClientId, string coinsStoreProductId, string premiumStoreProductId)
            : this(appId, mode, backendBaseUrl, requestTimeoutMs, developmentKey, mockSubject, googleServerClientId, coinsStoreProductId, premiumStoreProductId, null) { }

        public GameBridgeConfig(string appId, ProviderMode mode, string backendBaseUrl, int requestTimeoutMs, string developmentKey, string mockSubject, string googleServerClientId, string coinsStoreProductId, string premiumStoreProductId, string installationId)
        {
            AppId = appId;
            Mode = mode;
            BackendBaseUrl = backendBaseUrl;
            RequestTimeoutMs = requestTimeoutMs;
            DevelopmentKey = developmentKey;
            MockSubject = mockSubject;
            GoogleServerClientId = googleServerClientId;
            CoinsStoreProductId = coinsStoreProductId;
            PremiumStoreProductId = premiumStoreProductId;
            InstallationId = installationId;
        }

        public void Validate()
        {
            var errors = new List<string>();
            if (string.IsNullOrWhiteSpace(AppId)) errors.Add("appId");
            if (RequestTimeoutMs <= 0) errors.Add("requestTimeoutMs");
            if (!Enum.IsDefined(typeof(ProviderMode), Mode)) errors.Add("providerMode");
            if (Mode == ProviderMode.LocalMock)
            {
                if (DevelopmentKey == null || DevelopmentKey.Length < 32) errors.Add("developmentKey");
                if (MockSubject != "A" && MockSubject != "B") errors.Add("mockSubject");
            }
            else if (!string.IsNullOrEmpty(DevelopmentKey)) errors.Add("developmentKey");
            if (InstallationId != null && ((Mode != ProviderMode.PlatformSandbox && Mode != ProviderMode.LocalMock) || !Guid.TryParseExact(InstallationId, "D", out _))) errors.Add("installationId");
            if (CoinsStoreProductId != null || PremiumStoreProductId != null)
            {
                if (Mode != ProviderMode.PlatformSandbox || string.IsNullOrWhiteSpace(CoinsStoreProductId) ||
                    string.IsNullOrWhiteSpace(PremiumStoreProductId) || CoinsStoreProductId == PremiumStoreProductId)
                    errors.Add("storeProductIds");
            }
            if (Mode != ProviderMode.EditorOffline)
            {
                if (!Uri.TryCreate(BackendBaseUrl, UriKind.Absolute, out var uri) ||
                    string.IsNullOrEmpty(uri.Host) || !string.IsNullOrEmpty(uri.UserInfo) ||
                    !(uri.Scheme == Uri.UriSchemeHttps || (Mode == ProviderMode.LocalMock && uri.Scheme == Uri.UriSchemeHttp)))
                    errors.Add("backendBaseUrl");
            }
            if (errors.Count > 0) throw new ConfigurationException(errors);
        }
    }
}
