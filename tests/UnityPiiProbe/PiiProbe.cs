using System;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using GameBridge;
using Newtonsoft.Json;

// Test-only synthetic callback; never uses real personal information or remote push.
internal static class PiiProbe
{
    internal const string Email = "synthetic-person@example.invalid";
    internal const string Phone = "+1-202-555-0107";
    private const BindingFlags Fields = BindingFlags.Instance | BindingFlags.NonPublic;
    internal static async Task Run(GameBridgeClient client)
    {
        var registry = typeof(GameBridgeClient).GetField("registry", Fields)?.GetValue(client) ?? throw new InvalidOperationException("REGISTRY_MISSING");
        var session = registry.GetType().GetField("sessionId", Fields)?.GetValue(registry) as string ?? throw new InvalidOperationException("SESSION_MISSING");
        var completion = new TaskCompletionSource<PushUpdate>(TaskCreationOptions.RunContinuationsAsynchronously);
        void OnPush(PushUpdate value) { if (value.MessageId == "synthetic-pii-event") completion.TrySetResult(value); }
        client.PushReceived += OnPush;
        try
        {
            var json = "{\"protocolVersion\":1,\"sdkSessionId\":\"" + session + "\",\"kind\":\"event\",\"eventId\":\"" + Guid.NewGuid().ToString("D") + "\",\"type\":\"PushReceived\",\"occurredAt\":\"2026-11-13T00:00:00Z\",\"payload\":{\"messageId\":\"synthetic-pii-event\",\"route\":\"home\",\"campaignId\":null,\"email\":\"" + Email + "\",\"phone\":\"" + Phone + "\"}}";
            var transport = typeof(GameBridgeClient).GetField("transport", Fields)?.GetValue(client) ?? throw new InvalidOperationException("TRANSPORT_MISSING");
#if UNITY_ANDROID && !UNITY_EDITOR
            var callback = transport.GetType().GetField("callback", Fields)?.GetValue(transport) ?? throw new InvalidOperationException("CALLBACK_MISSING");
            var method = callback.GetType().GetMethod("onMessage", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic) ?? throw new InvalidOperationException("CALLBACK_METHOD_MISSING");
            method.Invoke(callback, new object[] { json });
#elif UNITY_IOS && !UNITY_EDITOR
            var method = transport.GetType().GetMethod("OnNativeMessage", BindingFlags.Static | BindingFlags.NonPublic) ?? throw new InvalidOperationException("CALLBACK_METHOD_MISSING");
            var bytes = Encoding.UTF8.GetBytes(json); var pointer = Marshal.AllocHGlobal(bytes.Length);
            try { Marshal.Copy(bytes, 0, pointer, bytes.Length); method.Invoke(null, new object[] { pointer, bytes.Length }); }
            finally { Marshal.FreeHGlobal(pointer); }
#else
            throw new InvalidOperationException("UNSUPPORTED_TEST_PLATFORM");
#endif
            if (await Task.WhenAny(completion.Task, Task.Delay(10000)) != completion.Task) throw new InvalidOperationException("PII_CALLBACK_TIMEOUT");
            var serialized = JsonConvert.SerializeObject(await completion.Task);
            if (serialized.Contains(Email) || serialized.Contains(Phone)) throw new InvalidOperationException("SENSITIVE_EVENT_RESULT");
            UnityEngine.Debug.Log("GB_PII_PROBE PASS");
        }
        finally { client.PushReceived -= OnPush; }
    }
}
