using System;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;
public sealed class MockPlayerScenario : MonoBehaviour
{
    private GameBridgeClient client;
    private string status = "Connecting";
    private bool ready, busy;
    private int urlEvents;
    private async void Start()
    {
        Application.deepLinkActivated += Url;
        await Run("PREFLIGHT", async () => {
            using var unity = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
            using var activity = unity.GetStatic<AndroidJavaObject>("currentActivity");
            using var intent = activity.Call<AndroidJavaObject>("getIntent");
            var endpoint = intent.Call<string>("getStringExtra", "gamebridge_google_url");
            var audience = intent.Call<string>("getStringExtra", "gamebridge_google_client");
            if (string.IsNullOrEmpty(endpoint) || !endpoint.StartsWith("https://localhost:", StringComparison.Ordinal) ||
                string.IsNullOrEmpty(audience))
                throw new InvalidOperationException("CONFIG_REQUIRED");
            var config = new GameBridgeConfig("gamebridge-google-oauth-test", ProviderMode.PlatformSandbox,
                endpoint, 300000, null, null, audience);
            client = GameBridgeSdk.Create(config);
            await client.InitializeAsync(config);
            await client.GetServiceConfigAsync();
            if (client.GetStatus().SdkVersion != "0.1.2-dev") throw new InvalidOperationException("SDK_VERSION_MISMATCH");
            ready = true;
            return "READY";
        });
    }
    private async Task Run(string operation, Func<Task<string>> action)
    {
        if (busy) return;
        busy = true;
        status = operation + " pending";
        try { status = operation + " " + await action(); }
        catch (SdkException error) { status = operation + " " + error.Code; }
        catch (Exception) { status = operation + " INTERNAL_ERROR"; }
        finally { Debug.Log("GB48 " + status + " URL_EVENTS " + urlEvents); busy = false; }
    }
    private const float LayoutWidth = 370f;
    private const float LayoutHeight = 800f;
    private GUIStyle labelStyle;
    private GUIStyle buttonStyle;

    private void OnGUI()
    {
        if (labelStyle == null)
        {
            labelStyle = new GUIStyle(GUI.skin.label)
            {
                margin = new RectOffset(),
                wordWrap = true,
                clipping = TextClipping.Clip
            };
            buttonStyle = new GUIStyle(GUI.skin.button)
            {
                margin = new RectOffset(),
                wordWrap = true,
                clipping = TextClipping.Clip
            };
        }

        var safe = Screen.safeArea;
        var scale = Mathf.Min(safe.width / LayoutWidth, safe.height / LayoutHeight);
        var origin = new Vector3(
            safe.x + (safe.width - LayoutWidth * scale) * 0.5f,
            Screen.height - safe.yMax + (safe.height - LayoutHeight * scale) * 0.5f,
            0f);
        var originalMatrix = GUI.matrix;
        var originalEnabled = GUI.enabled;
        GUI.matrix = Matrix4x4.TRS(origin, Quaternion.identity, new Vector3(scale, scale, 1f));
        GUILayout.BeginArea(new Rect(20f, 140f, 330f, 280f));
        try
        {
            GUILayout.Label("GameBridge Android Google", labelStyle, GUILayout.Height(35f));
            GUILayout.Space(5f);
            GUILayout.Label(status, labelStyle, GUILayout.Height(50f));
            GUILayout.Space(5f);

            GUI.enabled = originalEnabled && ready && !busy;
            if (GUILayout.Button("Google sign in", buttonStyle, GUILayout.Height(54f)))
                _ = Run("SIGN_IN", async () => (await client.SignInAsync(AuthProvider.GOOGLE)).provider == "GOOGLE" ? "PASS" : "WRONG_PROVIDER");

            GUILayout.Space(11f);
            if (GUILayout.Button("Restore SDK session", buttonStyle, GUILayout.Height(54f)))
                _ = Run("RESTORE", async () => (await client.RestoreSessionAsync()).signedIn ? "PASS" : "NO_SESSION");

            GUILayout.Space(11f);
            if (GUILayout.Button("Sign out", buttonStyle, GUILayout.Height(54f)))
                _ = Run("SIGN_OUT", async () => { await client.SignOutAsync(); return "PASS"; });
        }
        finally
        {
            GUILayout.EndArea();
            GUI.enabled = originalEnabled;
            GUI.matrix = originalMatrix;
        }
    }
    private void Url(string _) => urlEvents++;
    private void OnDestroy() { Application.deepLinkActivated -= Url; client?.Dispose(); }
}
