using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;
using UnityEngine.UI;

/// Native-only sample. Enter development credentials at runtime; do not serialize them into scene assets.
public sealed class NativeDemo : MonoBehaviour
{
    private GameBridgeClient client;
    private GameObject root;
    private Text modeLabel, status, balance, products;
    private InputField appId, backend, developmentKey, clientId, coinsId, premiumId, installationId;
    private readonly List<Button> actions = new List<Button>();
    private bool sandbox, busy, ready, pendingWalletRefresh, destroyed;
    public GameBridgeClient Client => client;

    private void Start()
    {
        BuildUi();
        if (Application.isEditor) { status.text = "Native demo requires an Android or iOS player. Use Editor Offline Demo in the Editor."; SetActions(false); }
        else status.text = "Enter configuration, choose a mode, then initialize.";
    }
    private void OnDestroy() { destroyed = true; ready = false; client?.Dispose(); client = null; if (root != null) Destroy(root); }
    private async Task Run(Func<Task> action)
    {
        if (busy) return;
        busy = true; SetActions(false);
        try { await action(); }
        catch (SdkException error) { if (!destroyed && status != null) status.text = error.Code; }
        catch (Exception) { if (!destroyed && status != null) status.text = "INTERNAL_ERROR"; }
        finally
        {
            busy = false;
            if (!destroyed) { SetActions(!Application.isEditor); if (pendingWalletRefresh && ready) { pendingWalletRefresh = false; _ = Run(RefreshWallet); } }
        }
    }
    private async Task Initialize()
    {
        if (client != null) throw new SdkException("BUSY");
        var mode = sandbox ? ProviderMode.PlatformSandbox : ProviderMode.LocalMock;
        var config = new GameBridgeConfig(appId.text, mode, backend.text, 30000,
            sandbox ? null : developmentKey.text, "A", Empty(clientId.text), Empty(coinsId.text), Empty(premiumId.text), Empty(installationId.text));
        var created = GameBridgeSdk.Create(config);
        try { await created.InitializeAsync(config); }
        catch { created.Dispose(); throw; }
        client = created; developmentKey.text = ""; ready = true;
        client.PurchaseUpdated += OnPurchaseUpdated;
        client.PushReceived += value => status.text = "Push received: " + value.Route;
        client.PushOpened += value => status.text = "Push opened: " + value.Route;
        client.PushTokenChanged += value => status.text = value.Registered ? "Push token registered" : "Push token: " + value.ErrorCode;
        var capabilities = client.GetCapabilities();
        status.text = (sandbox ? "PLATFORM_SANDBOX" : "LOCAL_MOCK") + " ready — store " + (capabilities.Features["store"].Configured ? "configured" : "not configured");
    }
    private void OnPurchaseUpdated(PurchaseUpdate value)
    {
        if (destroyed) return;
        status.text = "Purchase " + value.ProductId + ": " + value.Status;
        if (value.Status == PurchaseStatus.PURCHASED) { pendingWalletRefresh = true; if (!busy && ready) { pendingWalletRefresh = false; _ = Run(RefreshWallet); } }
    }
    private async Task RefreshWallet()
    {
        var wallet = await RequireClient().GetEntitlementsAsync();
        balance.text = "Coins: " + wallet.coinBalance + "   Premium: " + (wallet.premiumEnabled ? "yes" : "no");
    }
    private GameBridgeClient RequireClient() { if (!ready || client == null) throw new SdkException("NOT_INITIALIZED"); return client; }
    private AuthProvider Provider() => sandbox ? (Application.platform == RuntimePlatform.Android ? AuthProvider.GOOGLE : AuthProvider.APPLE) : AuthProvider.MOCK;
    private static string Empty(string value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();
    private void BuildUi()
    {
        root = new GameObject("GameBridgeNativeCanvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        root.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = root.GetComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize; scaler.referenceResolution = new Vector2(1080, 1920);
        var viewport = new GameObject("Viewport", typeof(RectTransform), typeof(Image), typeof(Mask), typeof(ScrollRect)); viewport.transform.SetParent(root.transform, false);
        var vr = viewport.GetComponent<RectTransform>(); vr.anchorMin = Vector2.zero; vr.anchorMax = Vector2.one; vr.offsetMin = Vector2.zero; vr.offsetMax = Vector2.zero;
        viewport.GetComponent<Image>().color = new Color(0.08f, 0.11f, 0.16f); viewport.GetComponent<Mask>().showMaskGraphic = true;
        var content = new GameObject("Content", typeof(RectTransform), typeof(VerticalLayoutGroup), typeof(ContentSizeFitter)); content.transform.SetParent(viewport.transform, false);
        var cr = content.GetComponent<RectTransform>(); cr.anchorMin = new Vector2(0, 1); cr.anchorMax = Vector2.one; cr.pivot = new Vector2(0.5f, 1); cr.offsetMin = new Vector2(32, 0); cr.offsetMax = new Vector2(-32, 0);
        var layout = content.GetComponent<VerticalLayoutGroup>(); layout.padding = new RectOffset(24, 24, 24, 24); layout.spacing = 12; layout.childControlWidth = true; layout.childControlHeight = true; layout.childForceExpandHeight = false;
        content.GetComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        var scroll = viewport.GetComponent<ScrollRect>(); scroll.viewport = vr; scroll.content = cr; scroll.horizontal = false;
        modeLabel = Label(content.transform, "LOCAL_MOCK — simulated, no real store", 60);
        status = Label(content.transform, "Not initialized", 60); balance = Label(content.transform, "Coins: —   Premium: —", 60);
        appId = Input(content.transform, "App ID", "gamebridge-sample", false);
        backend = Input(content.transform, "Backend URL (required)", "", false);
        developmentKey = Input(content.transform, "Local development key (runtime only)", "", true);
        clientId = Input(content.transform, "Google server client ID (Android sandbox)", "", false);
        coinsId = Input(content.transform, "Coins store product ID (sandbox)", "", false);
        premiumId = Input(content.transform, "Premium store product ID (sandbox)", "", false);
        installationId = Input(content.transform, "Installation UUID (push)", "", false);
        Button(content.transform, "Toggle LOCAL_MOCK / PLATFORM_SANDBOX", () => { if (client != null) { status.text = "Shutdown before changing mode"; return; } sandbox = !sandbox; modeLabel.text = sandbox ? "PLATFORM_SANDBOX — configured test services" : "LOCAL_MOCK — simulated, no real store"; });
        Button(content.transform, "Initialize", () => { _ = Run(Initialize); });
        Button(content.transform, "Sign in", () => { _ = Run(async () => { await RequireClient().SignInAsync(Provider()); status.text = "Signed in"; try { await RefreshWallet(); } catch (SdkException error) { status.text = "Signed in; balance: " + error.Code; } }); });
        Button(content.transform, "Restore session", () => { _ = Run(async () => { var session = await RequireClient().RestoreSessionAsync(); status.text = session.signedIn ? "Session restored" : "No session"; if (session.signedIn) { try { await RefreshWallet(); } catch (SdkException error) { status.text = "Session restored; balance: " + error.Code; } } }); });
        products = Label(content.transform, "Products not loaded", 80);
        Button(content.transform, "Load products", () => { _ = Run(async () => { var items = await RequireClient().GetProductsAsync(); products.text = string.Join(" / ", items.Select(x => x.productId + ": " + x.localizedPrice)); }); });
        Button(content.transform, "Buy coins", () => Buy("coins_100")); Button(content.transform, "Unlock premium", () => Buy("premium_unlock"));
        Button(content.transform, "Refresh balance", () => { _ = Run(RefreshWallet); });
        Button(content.transform, "Restore purchases", () => { _ = Run(async () => { var result = await RequireClient().SyncPurchasesAsync(SyncReason.USER_RESTORE); balance.text = "Coins: " + result.entitlements.coinBalance + "   Premium: " + result.entitlements.premiumEnabled; status.text = "Recovery: " + result.recoveredCount + " recovered, " + result.deferredCount + " deferred, " + result.failureCount + " failed"; }); });
        Button(content.transform, "Request notification permission", () => { _ = Run(async () => { var result = await RequireClient().RequestPushPermissionAsync(); status.text = result.provider + " permission: " + result.permission; }); });
        Button(content.transform, "Register push", () => { _ = Run(async () => { var result = await RequireClient().RegisterPushAsync(); status.text = result.provider + " registered: " + result.registered; }); });
        Button(content.transform, "Unregister push", () => { _ = Run(async () => { await RequireClient().UnregisterPushAsync(); status.text = "Push unregistered"; }); });
        Button(content.transform, "Sign out", () => { _ = Run(async () => { await RequireClient().SignOutAsync(); balance.text = "Coins: —   Premium: —"; status.text = "Signed out"; }); });
        Button(content.transform, "Shutdown", () => { _ = Run(async () => { await RequireClient().ShutdownAsync(); client.Dispose(); client = null; ready = false; status.text = "Shutdown"; }); });
    }
    private void Buy(string productId) { _ = Run(async () => { var result = await RequireClient().PurchaseAsync(productId); status.text = "Purchase: " + result.status; if (result.status == PurchaseStatus.PURCHASED) await RefreshWallet(); }); }
    private static Text Label(Transform parent, string text, float height)
    {
        var node = new GameObject("Label", typeof(RectTransform), typeof(Text), typeof(LayoutElement)); node.transform.SetParent(parent, false);
        var label = node.GetComponent<Text>(); label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); label.fontSize = 28; label.color = Color.white; label.text = text;
        node.GetComponent<LayoutElement>().preferredHeight = height; return label;
    }
    private static InputField Input(Transform parent, string hint, string initial, bool password)
    {
        var node = new GameObject("Input", typeof(RectTransform), typeof(Image), typeof(InputField), typeof(LayoutElement)); node.transform.SetParent(parent, false);
        node.GetComponent<Image>().color = new Color(0.18f, 0.22f, 0.28f); node.GetComponent<LayoutElement>().preferredHeight = 72;
        var text = Label(node.transform, initial, 72); var rect = text.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.offsetMin = new Vector2(12, 4); rect.offsetMax = new Vector2(-12, -4);
        var placeholder = Label(node.transform, hint, 72); var pr = placeholder.GetComponent<RectTransform>(); pr.anchorMin = Vector2.zero; pr.anchorMax = Vector2.one; pr.offsetMin = new Vector2(12, 4); pr.offsetMax = new Vector2(-12, -4); placeholder.color = Color.gray;
        var field = node.GetComponent<InputField>(); field.textComponent = text; field.placeholder = placeholder; field.text = initial;
        if (password) field.contentType = InputField.ContentType.Password;
        return field;
    }
    private void Button(Transform parent, string caption, UnityEngine.Events.UnityAction action)
    {
        var node = new GameObject("Button", typeof(RectTransform), typeof(Image), typeof(Button), typeof(LayoutElement)); node.transform.SetParent(parent, false);
        var image = node.GetComponent<Image>(); image.color = new Color(0.15f, 0.3f, 0.5f); node.GetComponent<LayoutElement>().preferredHeight = 72;
        var button = node.GetComponent<Button>(); button.targetGraphic = image; button.onClick.AddListener(action); actions.Add(button);
        var text = Label(node.transform, caption, 72); var rect = text.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.offsetMin = Vector2.zero; rect.offsetMax = Vector2.zero; text.alignment = TextAnchor.MiddleCenter;
    }
    private void SetActions(bool enabled) { foreach (var action in actions) if (action != null) action.interactable = enabled; }
}
