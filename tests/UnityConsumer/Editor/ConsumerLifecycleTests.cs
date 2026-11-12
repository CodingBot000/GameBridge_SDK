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
                client = GameBridgeSdk.Create(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                var init = client.InitializeAsync(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                while (!init.IsCompleted) yield return null;
                init.GetAwaiter().GetResult();
                Assert.AreEqual("READY", client.GetStatus().State);
                Assert.AreEqual(1, DispatcherCount());
                var login = client.SignInAsync(AuthProvider.MOCK);
                while (!login.IsCompleted) yield return null;
                Assert.AreEqual("MOCK", login.GetAwaiter().GetResult().provider);
                var products = client.GetProductsAsync();
                while (!products.IsCompleted) yield return null;
                Assert.AreEqual(2, products.GetAwaiter().GetResult().Count);
                var old = SceneManager.GetActiveScene();
                var scene = SceneManager.CreateScene("GameBridgeConsumer-" + Guid.NewGuid());
                Assert.IsTrue(SceneManager.SetActiveScene(scene));
                yield return null;
                Assert.AreEqual(1, DispatcherCount());
                Assert.IsTrue(SceneManager.SetActiveScene(old));
                var unload = SceneManager.UnloadSceneAsync(scene);
                while (unload != null && !unload.isDone) yield return null;
                var oldSession = SessionId(client);
                var shutdown = client.ShutdownAsync();
                while (!shutdown.IsCompleted) yield return null;
                shutdown.GetAwaiter().GetResult(); client.Dispose();
                yield return null;
                Assert.AreEqual(0, DispatcherCount());
                // Recreate after disposal and inject one synthetic event for the old
                // session plus one for the current session. Neither an old subscriber
                // nor a duplicate dispatcher may survive the scene transition.
                oldCalls = 0; newCalls = 0;
                second = GameBridgeSdk.Create(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                var secondInit = second.InitializeAsync(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
                while (!secondInit.IsCompleted) yield return null;
                secondInit.GetAwaiter().GetResult();
                Assert.AreEqual(1, DispatcherCount());
                client.PushReceived += OldCallback;
                second.PushReceived += NewCallback;
                var newSession = SessionId(second);
                Assert.AreNotEqual(oldSession, newSession);
                Inject(second, oldSession, "stale");
                Inject(second, newSession, "current");
                Assert.AreEqual(0, oldCalls); Assert.AreEqual(1, newCalls);
                second.Dispose();
                Inject(second, newSession, "after-dispose");
                yield return null;
                Assert.AreEqual(1, newCalls); Assert.AreEqual(0, DispatcherCount());
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
            Assert.IsNotNull(registry);
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
