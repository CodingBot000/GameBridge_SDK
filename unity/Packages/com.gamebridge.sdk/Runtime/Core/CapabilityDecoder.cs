using System;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace GameBridge.Core
{
    internal static class CapabilityDecoder
    {
        internal static SdkCapabilities Decode(JToken token, ProviderMode mode)
        {
            if (!(token is JObject root)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
            var result = new Dictionary<string, CapabilityStatus>();
            foreach (var name in new[] { "auth", "store", "push", "config" })
            {
                if (!(root[name] is JObject feature) || feature["supported"]?.Type != JTokenType.Boolean || feature["configured"]?.Type != JTokenType.Boolean ||
                    feature["mode"]?.Type != JTokenType.String || (string)feature["mode"] != ModeString(mode) || !feature.ContainsKey("reason") ||
                    (feature["reason"].Type != JTokenType.String && feature["reason"].Type != JTokenType.Null)) throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                result[name] = new CapabilityStatus((bool)feature["supported"], (bool)feature["configured"], mode,
                    feature["reason"].Type == JTokenType.Null ? null : (string)feature["reason"]);
            }
            return new SdkCapabilities(true, result, DateTimeOffset.UtcNow);
        }

        internal static string ModeString(ProviderMode mode)
        {
            switch (mode) { case ProviderMode.EditorOffline: return "EDITOR_OFFLINE"; case ProviderMode.LocalMock: return "LOCAL_MOCK"; case ProviderMode.XcodeStoreKit: return "XCODE_STOREKIT"; case ProviderMode.PlatformSandbox: return "PLATFORM_SANDBOX"; default: throw new SdkException("INVALID_ARGUMENT"); }
        }
    }
}
