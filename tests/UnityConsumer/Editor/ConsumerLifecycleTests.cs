using System;
using System.Collections;
using System.Linq;
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
        [UnityTest] public IEnumerator DomainReloadEnabled() { return Exercise(false); }
        [UnityTest] public IEnumerator DomainReloadDisabled() { return Exercise(true); }

        private static IEnumerator Exercise(bool disableReload)
        {
            var previousEnabled = EditorSettings.enterPlayModeOptionsEnabled;
            var previousOptions = EditorSettings.enterPlayModeOptions;
            EditorSettings.enterPlayModeOptionsEnabled = disableReload;
            EditorSettings.enterPlayModeOptions = disableReload ? EnterPlayModeOptions.DisableDomainReload : EnterPlayModeOptions.None;
            try
            {
                yield return new EnterPlayMode(!disableReload);
                var client = GameBridgeSdk.Create(new GameBridgeConfig("consumer", ProviderMode.EditorOffline, null));
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
                var shutdown = client.ShutdownAsync();
                while (!shutdown.IsCompleted) yield return null;
                shutdown.GetAwaiter().GetResult(); client.Dispose();
                yield return null;
                Assert.AreEqual(0, DispatcherCount());
                yield return new ExitPlayMode();
            }
            finally
            {
                EditorSettings.enterPlayModeOptions = previousOptions;
                EditorSettings.enterPlayModeOptionsEnabled = previousEnabled;
            }
        }
        private static int DispatcherCount() => Resources.FindObjectsOfTypeAll<GameObject>()
            .Count(item => item != null && item.name == "GameBridge.Dispatcher" && item.scene.IsValid());
    }
}
