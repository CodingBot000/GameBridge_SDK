using System;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

// Installed only in the isolated iOS Google OAuth verification consumer.
public sealed class MockIosPlayerScenario : MonoBehaviour
{
    private GameBridgeClient client;
    private CancellationTokenSource signIn;
    private string status = "Checking HTTPS sandbox";
    private bool ready, busy;
    private int urlEvents;

    private async void Start()
    {
        Application.deepLinkActivated += OnDeepLink;
        await Run("PREFLIGHT", async () =>
        {
            var config = new GameBridgeConfig("gamebridge-google-oauth-test", ProviderMode.PlatformSandbox,
                "https://localhost:18443", 300000, null, null);
            client = GameBridgeSdk.Create(config);
            await client.InitializeAsync(config);
            await client.GetServiceConfigAsync();
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
        catch (SdkException error)
        {
            status = operation + " " + (error.NativeCode == "REVOCATION_UNCONFIRMED" ? error.NativeCode : error.Code);
        }
        catch (Exception) { status = operation + " INTERNAL_ERROR"; }
        finally
        {
            Debug.Log("GB45 " + status + " URL_EVENTS " + urlEvents);
            busy = false;
        }
    }

    private async Task<string> SignIn()
    {
        using var cancellation = new CancellationTokenSource();
        signIn = cancellation;
        try
        {
            var profile = await client.SignInAsync(AuthProvider.GOOGLE, cancellation.Token);
            return IsGoogle(profile) && urlEvents == 0 ? "PASS" : "INVALID_PROFILE_OR_URL_EVENT";
        }
        finally { signIn = null; }
    }

    private async Task<string> Restore()
    {
        var session = await client.RestoreSessionAsync();
        if (!session.signedIn) return "NO_SESSION";
        return IsGoogle(session.user) && session.sessionRestored ? "PASS" : "INVALID_RESTORE";
    }

    private static bool IsGoogle(UserProfile profile) =>
        profile?.provider == "GOOGLE" && Guid.TryParse(profile.userId, out _);

    private void OnDeepLink(string _) => urlEvents++;

    private void OnGUI()
    {
        GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 370f, Screen.height / 800f, 1));
        var label = new GUIStyle(GUI.skin.label) { fontSize = 18 };
        GUI.Label(new Rect(20, 140, 330, 32), "GameBridge Google OAuth lifecycle", label);
        GUI.Label(new Rect(20, 185, 330, 32), status, label);
        GUI.Label(new Rect(20, 220, 330, 32), "Unity URL events: " + urlEvents, label);
        GUI.enabled = ready && !busy;
        if (GUI.Button(new Rect(20, 265, 330, 54), "Google sign in")) _ = Run("SIGN_IN", SignIn);
        if (GUI.Button(new Rect(20, 330, 330, 54), "Restore SDK session")) _ = Run("RESTORE", Restore);
        if (GUI.Button(new Rect(20, 395, 330, 54), "Sign out")) _ = Run("SIGN_OUT", async () => { await client.SignOutAsync(); return "PASS"; });
        GUI.enabled = signIn != null;
        if (GUI.Button(new Rect(20, 460, 330, 54), "Cancel SDK request")) signIn?.Cancel();
        GUI.enabled = true;
    }

    private void OnDestroy()
    {
        Application.deepLinkActivated -= OnDeepLink;
        client?.Dispose();
    }
}
