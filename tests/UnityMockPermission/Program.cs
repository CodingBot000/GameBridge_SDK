using System;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

internal static class Program
{
    private sealed class DeniedPermissionTransport : IWireTransport
    {
        private readonly EditorOfflineTransport inner = new EditorOfflineTransport();
        public event Action<string> Message;
        public DeniedPermissionTransport() { inner.Message += Forward; }
        private void Forward(string value) { Message?.Invoke(value); }
        public void Dispatch(string json)
        {
            var request = JObject.Parse(json);
            if ((string)request["operation"] != "push.permission") { inner.Dispatch(json); return; }
            Message?.Invoke(new JObject { ["protocolVersion"] = 1, ["sdkSessionId"] = request["sdkSessionId"],
                ["kind"] = "response", ["requestId"] = request["requestId"], ["operation"] = "push.permission",
                ["ok"] = true, ["result"] = new JObject { ["provider"] = "MOCK", ["permission"] = "DENIED" },
                ["error"] = JValue.CreateNull() }.ToString(Formatting.None));
        }
        public void Pump() { inner.Pump(); }
        public void Dispose() { inner.Message -= Forward; inner.Dispose(); Message = null; }
    }
    private static async Task Main()
    {
        var config = new GameBridgeConfig("permission-fake", ProviderMode.EditorOffline, null);
        using var client = new GameBridgeClient(new DeniedPermissionTransport());
        await client.InitializeAsync(config);
        await client.SignInAsync(AuthProvider.MOCK);
        if ((await client.RequestPushPermissionAsync()).permission != "DENIED") throw new Exception("first denial missing");
        try { await client.RegisterPushAsync(); throw new Exception("registration succeeded"); }
        catch (SdkException error) { if (error.Code != "PERMISSION_DENIED") throw; }
        if ((await client.RequestPushPermissionAsync()).permission != "DENIED") throw new Exception("second denial missing");
        await client.ShutdownAsync();
        Console.WriteLine("PASS: mock permission denied, registration blocked, re-request denied (standalone managed test)");
    }
}
