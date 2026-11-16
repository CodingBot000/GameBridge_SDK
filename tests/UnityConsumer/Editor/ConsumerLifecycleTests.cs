using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using GameBridge;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace GameBridgeConsumerTests
{
    public sealed class ConsumerLifecycleTests
    {
        private static class CountingAssert
        {
            internal static int Executed;
            internal static void Reset() { Executed = 0; }
            private static void Hit() { System.Threading.Interlocked.Increment(ref Executed); }
            internal static void AreEqual(object expected, object actual) { Hit(); Assert.AreEqual(expected, actual); }
            internal static void AreNotEqual(object expected, object actual) { Hit(); Assert.AreNotEqual(expected, actual); }
            internal static void IsTrue(bool value) { Hit(); Assert.IsTrue(value); }
            internal static void IsNotNull(object value) { Hit(); Assert.IsNotNull(value); }
        }
        private static int oldCalls, newCalls;
        private static void OldCallback(PushUpdate _) => oldCalls++;
        private static void NewCallback(PushUpdate _) => newCalls++;
        [UnityTest] public IEnumerator DomainReloadEnabled() { return Exercise(false); }
        [UnityTest] public IEnumerator DomainReloadDisabled() { return Exercise(true); }

        private static IEnumerator Exercise(bool disableReload)
        {
            var previousEnabled = EditorSettings.enterPlayModeOptionsEnabled;
            var previousOptions = EditorSettings.enterPlayModeOptions;
            EditorSettings.enterPlayModeOptionsEnabled = disableReload;
            EditorSettings.enterPlayModeOptions = disableReload ? EnterPlayModeOptions.DisableDomainReload : EnterPlayModeOptions.None;
            GameBridgeClient client = null, second = null;
            try
            {
                yield return new EnterPlayMode(!disableReload);
                CountingAssert.Reset();
                client = GameBridgeSdk.Create(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                var init = client.InitializeAsync(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                while (!init.IsCompleted) yield return null;
                init.GetAwaiter().GetResult();
                CountingAssert.AreEqual("READY", client.GetStatus().State);
                CountingAssert.AreEqual(1, DispatcherCount());
                var login = client.SignInAsync(AuthProvider.MOCK);
                while (!login.IsCompleted) yield return null;
                CountingAssert.AreEqual("MOCK", login.GetAwaiter().GetResult().provider);
                var products = client.GetProductsAsync();
                while (!products.IsCompleted) yield return null;
                CountingAssert.AreEqual(2, products.GetAwaiter().GetResult().Count);
                var old = SceneManager.GetActiveScene();
                var scene = SceneManager.CreateScene("GameBridgeConsumer-" + Guid.NewGuid());
                CountingAssert.IsTrue(SceneManager.SetActiveScene(scene));
                yield return null;
                CountingAssert.AreEqual(1, DispatcherCount());
                CountingAssert.IsTrue(SceneManager.SetActiveScene(old));
                var unload = SceneManager.UnloadSceneAsync(scene);
                while (unload != null && !unload.isDone) yield return null;
                var oldSession = SessionId(client);
                var shutdown = client.ShutdownAsync();
                while (!shutdown.IsCompleted) yield return null;
                shutdown.GetAwaiter().GetResult(); client.Dispose();
                yield return null;
                CountingAssert.AreEqual(0, DispatcherCount());
                // Recreate after disposal and inject one synthetic event for the old
                // session plus one for the current session. Neither an old subscriber
                // nor a duplicate dispatcher may survive the scene transition.
                oldCalls = 0; newCalls = 0;
                second = GameBridgeSdk.Create(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                var secondInit = second.InitializeAsync(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                while (!secondInit.IsCompleted) yield return null;
                secondInit.GetAwaiter().GetResult();
                CountingAssert.AreEqual(1, DispatcherCount());
                client.PushReceived += OldCallback;
                second.PushReceived += NewCallback;
                var newSession = SessionId(second);
                CountingAssert.AreNotEqual(oldSession, newSession);
                Inject(second, oldSession, "stale");
                Inject(second, newSession, "current");
                CountingAssert.AreEqual(0, oldCalls); CountingAssert.AreEqual(1, newCalls);
                second.Dispose();
                Inject(second, newSession, "after-dispose");
                yield return null;
                CountingAssert.AreEqual(1, newCalls); CountingAssert.AreEqual(0, DispatcherCount());
                Debug.Log("GB_ASSERTIONS_JSON {\"platform\":\"csharp-unity-editor\",\"test\":\"" + (disableReload ? "DomainReloadDisabled" : "DomainReloadEnabled") + "\",\"normalAssertions\":" + CountingAssert.Executed + ",\"expectedErrorChecks\":0,\"assertionsExecuted\":" + CountingAssert.Executed + ",\"assertionOutcomes\":\"UNMEASURED\",\"complete\":true}");
                Debug.Log("GB_CONSUMER_" + (disableReload ? "RELOAD_DISABLED" : "RELOAD_ENABLED") + "_COMPLETE");
                yield return new ExitPlayMode();
            }
            finally
            {
                second?.Dispose(); client?.Dispose();
                EditorSettings.enterPlayModeOptions = previousOptions;
                EditorSettings.enterPlayModeOptionsEnabled = previousEnabled;
            }
        }
        private static string SessionId(GameBridgeClient client)
        {
            var registry = typeof(GameBridgeClient).GetField("registry", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(client);
            CountingAssert.IsNotNull(registry);
            return (string)registry.GetType().GetField("sessionId", BindingFlags.Instance | BindingFlags.NonPublic).GetValue(registry);
        }
        private static void Inject(GameBridgeClient client, string session, string id)
        {
            var json = "{\"protocolVersion\":1,\"sdkSessionId\":\"" + session + "\",\"kind\":\"event\",\"eventId\":\"" + Guid.NewGuid().ToString("D") + "\",\"type\":\"PushReceived\",\"occurredAt\":\"2026-11-12T00:00:00Z\",\"payload\":{\"messageId\":\"" + id + "\",\"route\":\"home\",\"campaignId\":null}}";
            typeof(GameBridgeClient).GetMethod("OnMessage", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(client, new object[] { json });
        }
        private static int DispatcherCount() => Resources.FindObjectsOfTypeAll<GameObject>()
            .Count(item => item != null && item.name == "GameBridge.Dispatcher" && item.scene.IsValid());
    }
}
