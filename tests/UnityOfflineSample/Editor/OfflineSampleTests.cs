using System;
using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.TestTools;
using UnityEngine.UI;

public sealed class OfflineSampleTests
{
    [UnityTest]
    public IEnumerator SampleInitializesAndCompletesMockPurchase()
    {
        yield return new EnterPlayMode();
        new GameObject("GameBridgeSampleEventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
        var owner = new GameObject("GameBridgeOfflineSample"); owner.AddComponent<OfflineDemo>();
        yield return WaitUntil(() => Texts().Any(text => text.Contains("EDITOR_OFFLINE ready")), "initialization");
        Press("Mock sign in");
        yield return WaitUntil(() => Texts().Any(text => text.Contains("Mock user signed in")), "sign in");
        Press("Store"); Press("Load products");
        yield return WaitUntil(() => Texts().Any(text => text.Contains("coins_100")), "product listing");
        Press("Mock buy 100 coins");
        yield return WaitUntil(() => Texts().Any(text => text.Contains("Coins: 100")), "mock purchase");
        Assert.IsTrue(Texts().Any(text => text == "GRANTED"));
        UnityEngine.Object.Destroy(owner);
        yield return null;
        Debug.Log("GB_OFFLINE_SAMPLE_FLOW PASS");
        yield return new ExitPlayMode();
    }
    private static string[] Texts() => UnityEngine.Object.FindObjectsByType<Text>(FindObjectsInactive.Include, FindObjectsSortMode.None)
        .Where(item => item != null).Select(item => item.text).ToArray();
    private static void Press(string caption)
    {
        var button = UnityEngine.Object.FindObjectsByType<Button>(FindObjectsInactive.Include, FindObjectsSortMode.None)
            .Single(item => item.GetComponentsInChildren<Text>(true).Any(text => text.text == caption));
        Assert.IsTrue(button.gameObject.activeInHierarchy && button.interactable, caption + " unavailable");
        button.onClick.Invoke();
    }
    private static IEnumerator WaitUntil(Func<bool> condition, string stage)
    {
        var deadline = Time.realtimeSinceStartup + 20;
        while (!condition() && Time.realtimeSinceStartup < deadline) yield return null;
        Assert.IsTrue(condition(), stage + " timeout");
    }
}
