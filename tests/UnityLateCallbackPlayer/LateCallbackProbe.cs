using System;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using GameBridge;

// Test-only synthetic old-session callback. No production APIs or user messages are changed.
internal static class LateCallbackProbe
{
    private const BindingFlags Fields = BindingFlags.Instance | BindingFlags.NonPublic;
    internal static string Session(GameBridgeClient client)
    {
        var registry = typeof(GameBridgeClient).GetField("registry", Fields)?.GetValue(client) ?? throw new InvalidOperationException("REGISTRY_MISSING");
        return registry.GetType().GetField("sessionId", Fields)?.GetValue(registry) as string ?? throw new InvalidOperationException("SESSION_MISSING");
    }
    internal static async Task InjectAndVerify(GameBridgeClient client, string staleSession)
    {
        var before = client.GetDiagnostics().IgnoredMessages;
        var json = "{\"protocolVersion\":1,\"sdkSessionId\":\"" + staleSession + "\",\"kind\":\"event\",\"eventId\":\"" + Guid.NewGuid().ToString("D") + "\",\"type\":\"PushReceived\",\"occurredAt\":\"2026-11-12T00:00:00Z\",\"payload\":{\"messageId\":\"unity-late-a\",\"route\":\"home\",\"campaignId\":null}}";
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
        for (int i = 0; i < 50 && client.GetDiagnostics().IgnoredMessages <= before; i++) await Task.Delay(100);
        if (client.GetDiagnostics().IgnoredMessages <= before) throw new InvalidOperationException("STALE_CALLBACK_NOT_REJECTED");
        UnityEngine.Debug.Log("GB_PUSH_STEP synthetic-late-callback-rejected PASS");
    }
}
