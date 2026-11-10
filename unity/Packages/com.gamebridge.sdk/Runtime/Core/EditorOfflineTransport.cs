#if UNITY_EDITOR || GAMEBRIDGE_TEST_OFFLINE
using System;
using System.Collections.Generic;
using System.Globalization;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace GameBridge.Core
{
    /// <summary>Editor-only, in-memory fake. Never connects to a server or real store.</summary>
    internal sealed class EditorOfflineTransport : IWireTransport
    {
        private readonly object gate = new object();
        private const string UserId = "d2719c4e-d533-47ee-9efd-838791ea79c8";
        private const string FakeTime = "2026-01-01T00:00:00Z";
        private bool initialized, signedIn, permission, pushRegistered, disposed, wasShutdown;
        private JObject initialization;
        private long coins, revision;
        private bool premium;
        private readonly Dictionary<string, string> granted = new Dictionary<string, string>();
        public event Action<string> Message;
        public void Pump() { }
        public void Dispose() { lock (gate) { disposed = true; initialized = false; signedIn = false; Message = null; } }
        public void Dispatch(string json)
        {
            lock (gate)
            {
                if (disposed) throw new ObjectDisposedException(nameof(EditorOfflineTransport));
                var request = JObject.Parse(json);
                var operation = (string)request["operation"];
                var payload = request["payload"] as JObject ?? new JObject();
                JToken result = null;
                string error = null;
                if (operation == "sdk.initialize")
                {
                    if ((string)payload["providerMode"] != "EDITOR_OFFLINE") error = "UNSUPPORTED_PROVIDER";
                    else if (initialized && !JToken.DeepEquals(initialization, payload)) error = "ALREADY_INITIALIZED_DIFFERENT_CONFIG";
                    else { initialized = true; wasShutdown = false; initialization = (JObject)payload.DeepClone(); result = new JObject { ["state"] = "READY", ["mode"] = "EDITOR_OFFLINE", ["provider"] = "FAKE", ["capabilities"] = Capabilities() }; }
                }
                else if (operation == "sdk.status") result = new JObject { ["state"] = initialized ? "READY" : wasShutdown ? "SHUTDOWN" : "UNINITIALIZED", ["sdkVersion"] = "0.1.0-dev", ["mode"] = "EDITOR_OFFLINE" };
                else if (operation == "sdk.shutdown") { initialized = false; signedIn = false; pushRegistered = false; wasShutdown = true; initialization = null; result = new JObject { ["state"] = "SHUTDOWN" }; }
                else if (!initialized) error = "NOT_INITIALIZED";
                else switch (operation)
                {
                    case "auth.signIn":
                        if ((string)payload["provider"] != "MOCK") error = "UNSUPPORTED_PROVIDER";
                        else { signedIn = true; result = Profile(); }
                        break;
                    case "auth.signOut": signedIn = false; pushRegistered = false; result = new JObject(); break;
                    case "auth.restore": result = new JObject { ["signedIn"] = signedIn, ["user"] = signedIn ? (JToken)Profile() : JValue.CreateNull(), ["expiresAt"] = JValue.CreateNull(), ["sessionRestored"] = signedIn }; break;
                    case "store.products": result = new JArray(Product("coins_100", "CONSUMABLE"), Product("premium_unlock", "NON_CONSUMABLE")); break;
                    case "store.entitlements": if (!signedIn) error = "SESSION_EXPIRED"; else result = Wallet(); break;
                    case "store.purchase":
                        if (!signedIn) { error = "SESSION_EXPIRED"; break; }
                        var product = (string)payload["productId"];
                        var transaction = (string)payload["transactionId"];
                        var scenario = (string)payload["scenario"] ?? "SUCCESS";
                        if (product != "coins_100" && product != "premium_unlock") { error = "PRODUCT_NOT_FOUND"; break; }
                        if (!Guid.TryParseExact(transaction, "D", out _)) { error = "INVALID_ARGUMENT"; break; }
                        if (scenario == "NETWORK_FAILURE") { error = "NETWORK_UNAVAILABLE"; break; }
                        if (scenario != "SUCCESS" && scenario != "PENDING" && scenario != "CANCELED") { error = "INVALID_ARGUMENT"; break; }
                        if (granted.TryGetValue(transaction, out var prior) && prior != product) { error = "IDEMPOTENCY_CONFLICT"; break; }
                        var newGrant = scenario == "SUCCESS" && prior == null;
                        if (newGrant) { if (product == "coins_100") coins = checked(coins + 100); else premium = true; granted.Add(transaction, product); revision++; }
                        result = new JObject { ["attemptId"] = (string)request["requestId"], ["productId"] = product,
                            ["status"] = scenario == "SUCCESS" ? "PURCHASED" : scenario, ["serverPurchaseId"] = JValue.CreateNull(),
                            ["fulfillmentStatus"] = scenario != "SUCCESS" ? "NOT_GRANTED" : newGrant ? "GRANTED" : "ALREADY_GRANTED",
                            ["finalizationStatus"] = "NOT_REQUIRED", ["error"] = JValue.CreateNull() };
                        break;
                    case "store.sync": if (!signedIn) error = "SESSION_EXPIRED"; else result = new JObject { ["examinedCount"] = 0, ["recoveredCount"] = 0, ["deferredCount"] = 0, ["failureCount"] = 0, ["entitlements"] = Wallet() }; break;
                    case "push.permission": permission = true; result = new JObject { ["permission"] = "GRANTED", ["provider"] = "MOCK" }; break;
                    case "push.register":
                        if (!signedIn) error = "SESSION_EXPIRED";
                        else if (!permission) error = "PERMISSION_DENIED";
                        else { pushRegistered = true; result = new JObject { ["provider"] = "MOCK", ["registered"] = true, ["tokenFingerprint"] = "mock-fingerprint", ["permission"] = "GRANTED", ["updatedAt"] = FakeTime }; }
                        break;
                    case "push.unregister": pushRegistered = false; result = new JObject { ["registered"] = false }; break;
                    case "config.get": result = new JObject { ["revision"] = "0", ["maintenanceEnabled"] = false, ["message"] = JValue.CreateNull(), ["expiresAt"] = JValue.CreateNull(), ["source"] = "DEFAULT" }; break;
                    case "diagnostics.get": result = new JObject { ["mode"] = "EDITOR_OFFLINE", ["provider"] = "FAKE", ["pushRegistered"] = pushRegistered }; break;
                    default: error = "UNSUPPORTED_OPERATION"; break;
                }
                var response = new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = request["sdkSessionId"], ["kind"] = "response", ["requestId"] = request["requestId"], ["operation"] = operation,
                    ["ok"] = error == null, ["result"] = result ?? JValue.CreateNull(), ["error"] = error == null ? JValue.CreateNull() : (JToken)new JObject { ["code"] = error, ["retryable"] = error == "NETWORK_UNAVAILABLE" } };
                Message?.Invoke(response.ToString(Formatting.None));
            }
        }
        private static JObject Capabilities()
        {
            var result = new JObject();
            foreach (var name in new[] { "auth", "store", "push", "config" })
                result[name] = new JObject { ["supported"] = true, ["configured"] = true, ["mode"] = "EDITOR_OFFLINE", ["reason"] = "Editor fake" };
            return result;
        }
        private static JObject Profile() => new JObject { ["userId"] = UserId, ["displayName"] = "Mock User", ["provider"] = "MOCK" };
        private static JObject Product(string id, string type) => new JObject { ["productId"] = id, ["storeProductId"] = id, ["type"] = type, ["title"] = "Mock " + id, ["localizedPrice"] = "Mock price", ["currencyCode"] = "XXX", ["priceMicros"] = JValue.CreateNull() };
        private JObject Wallet() => new JObject { ["userId"] = UserId, ["premiumEnabled"] = premium, ["coinBalance"] = coins.ToString(CultureInfo.InvariantCulture), ["revision"] = revision.ToString(CultureInfo.InvariantCulture), ["updatedAt"] = FakeTime };
    }
}
#endif
