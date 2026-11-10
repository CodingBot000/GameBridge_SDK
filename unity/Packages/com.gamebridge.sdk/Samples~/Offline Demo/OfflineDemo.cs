using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using UnityEngine;

/// A self-contained in-memory demo. Add this component to an empty GameObject in an Editor scene.
public sealed class OfflineDemo : MonoBehaviour
{
    private GameBridgeClient client;
    private GameObject canvasRoot, home, store;
    private UnityEngine.UI.Text status, balance, products;
    private readonly List<UnityEngine.UI.Button> actions = new List<UnityEngine.UI.Button>();
    private bool busy, ready;

    private async void Start()
    {
        BuildUi();
        if (!Application.isEditor) { status.text = "Editor offline demo is unavailable in player builds."; SetActions(false); return; }
        await Run(async () => {
            var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.EditorOffline, null);
            client = GameBridgeSdk.Create(config);
            await client.InitializeAsync(config);
            ready = true;
            status.text = UnityEngine.EventSystems.EventSystem.current == null
                ? "Add a compatible EventSystem to use the buttons."
                : "EDITOR_OFFLINE ready — simulated data only";
        });
    }
    private void OnDestroy()
    {
        ready = false; client?.Dispose(); client = null;
        if (canvasRoot != null) Destroy(canvasRoot);
    }
    private async Task Run(Func<Task> action)
    {
        if (busy) return;
        busy = true; SetActions(false);
        try { await action(); }
        catch (SdkException error) { status.text = error.Code; }
        catch (Exception) { status.text = "INTERNAL_ERROR"; }
        finally { busy = false; SetActions(ready && client != null && Application.isEditor); }
    }
    private async Task RefreshWallet()
    {
        var value = await client.GetEntitlementsAsync();
        balance.text = "Coins: " + value.coinBalance + "   Premium: " + (value.premiumEnabled ? "yes" : "no");
    }
    private void BuildUi()
    {
        canvasRoot = new GameObject("GameBridgeOfflineCanvas", typeof(RectTransform), typeof(Canvas), typeof(UnityEngine.UI.CanvasScaler), typeof(UnityEngine.UI.GraphicRaycaster));
        var canvas = canvasRoot.GetComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvasRoot.GetComponent<UnityEngine.UI.CanvasScaler>(); scaler.uiScaleMode = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1080, 1920); scaler.matchWidthOrHeight = 0.5f;
        var panel = new GameObject("Panel", typeof(RectTransform), typeof(UnityEngine.UI.Image), typeof(UnityEngine.UI.VerticalLayoutGroup));
        panel.transform.SetParent(canvasRoot.transform, false);
        var rect = panel.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.offsetMin = Vector2.zero; rect.offsetMax = Vector2.zero;
        panel.GetComponent<UnityEngine.UI.Image>().color = new Color(0.08f, 0.11f, 0.16f);
        var layout = panel.GetComponent<UnityEngine.UI.VerticalLayoutGroup>(); layout.padding = new RectOffset(48, 48, 48, 48); layout.spacing = 16; layout.childControlWidth = true; layout.childControlHeight = true; layout.childForceExpandHeight = false;
        Label(panel.transform, "GameBridge — EDITOR OFFLINE", 72);
        status = Label(panel.transform, "Initializing…", 64);
        balance = Label(panel.transform, "Coins: —   Premium: —", 64);
        Button(panel.transform, "Home", () => Show(true)); Button(panel.transform, "Store", () => Show(false));
        home = Section(panel.transform, "HomeSection"); store = Section(panel.transform, "StoreSection");
        Button(home.transform, "Mock sign in", () => { _ = Run(async () => { await client.SignInAsync(AuthProvider.MOCK); await RefreshWallet(); status.text = "Mock user signed in"; }); });
        Button(home.transform, "Refresh balance", () => { _ = Run(RefreshWallet); });
        Button(home.transform, "Sign out", () => { _ = Run(async () => { await client.SignOutAsync(); balance.text = "Coins: —   Premium: —"; status.text = "Signed out"; }); });
        products = Label(store.transform, "Products not loaded", 70);
        Button(store.transform, "Load products", () => { _ = Run(async () => { var items = await client.GetProductsAsync(); products.text = string.Join(" / ", System.Linq.Enumerable.Select(items, item => item.productId + ": " + item.localizedPrice)); }); });
        Button(store.transform, "Mock buy 100 coins", () => { _ = Run(async () => { var result = await client.PurchaseAsync("coins_100"); await RefreshWallet(); status.text = result.fulfillmentStatus.ToString(); }); });
        Button(store.transform, "Mock unlock premium", () => { _ = Run(async () => { var result = await client.PurchaseAsync("premium_unlock"); await RefreshWallet(); status.text = result.fulfillmentStatus.ToString(); }); });
        Show(true);
    }
    private void Show(bool showHome) { home.SetActive(showHome); store.SetActive(!showHome); }
    private static GameObject Section(Transform parent, string name)
    {
        var obj = new GameObject(name, typeof(RectTransform), typeof(UnityEngine.UI.VerticalLayoutGroup), typeof(UnityEngine.UI.LayoutElement)); obj.transform.SetParent(parent, false);
        var layout = obj.GetComponent<UnityEngine.UI.VerticalLayoutGroup>(); layout.spacing = 16; layout.childControlWidth = true; layout.childControlHeight = true; layout.childForceExpandHeight = false;
        obj.GetComponent<UnityEngine.UI.LayoutElement>().preferredHeight = 430; return obj;
    }
    private static UnityEngine.UI.Text Label(Transform parent, string value, float height)
    {
        var obj = new GameObject("Label", typeof(RectTransform), typeof(UnityEngine.UI.Text), typeof(UnityEngine.UI.LayoutElement)); obj.transform.SetParent(parent, false);
        var label = obj.GetComponent<UnityEngine.UI.Text>(); label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); label.fontSize = 30; label.color = Color.white; label.text = value; label.alignment = TextAnchor.MiddleLeft;
        obj.GetComponent<UnityEngine.UI.LayoutElement>().preferredHeight = height; return label;
    }
    private void Button(Transform parent, string caption, UnityEngine.Events.UnityAction action)
    {
        var obj = new GameObject("Button", typeof(RectTransform), typeof(UnityEngine.UI.Image), typeof(UnityEngine.UI.Button), typeof(UnityEngine.UI.LayoutElement)); obj.transform.SetParent(parent, false);
        var image = obj.GetComponent<UnityEngine.UI.Image>(); image.color = new Color(0.15f, 0.3f, 0.5f);
        var button = obj.GetComponent<UnityEngine.UI.Button>(); button.targetGraphic = image; button.onClick.AddListener(action); actions.Add(button);
        obj.GetComponent<UnityEngine.UI.LayoutElement>().preferredHeight = 76;
        var text = Label(obj.transform, caption, 76); var rect = text.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.offsetMin = Vector2.zero; rect.offsetMax = Vector2.zero; text.alignment = TextAnchor.MiddleCenter;
    }
    private void SetActions(bool enabled) { foreach (var button in actions) if (button != null) button.interactable = enabled; }
}
