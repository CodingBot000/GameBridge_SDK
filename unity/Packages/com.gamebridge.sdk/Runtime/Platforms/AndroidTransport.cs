#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using GameBridge.Core;
using System.Collections.Concurrent;
using System.Threading;
using UnityEngine;

namespace GameBridge.Platforms
{
    /// <summary>Queues callbacks until Pump is called from Unity's main thread.</summary>
    internal sealed class AndroidTransport : IWireTransport
    {
        private const string FacadeName = "com.gamebridge.bridge.BridgeFacade";
        private readonly ConcurrentQueue<string> queue = new ConcurrentQueue<string>();
        private readonly AndroidJavaClass facade;
        private readonly CallbackProxy callback;
        private bool disposed;
        public event Action<string> Message;
        internal int DroppedMessages => callback.DroppedMessages;

        internal AndroidTransport()
        {
            facade = new AndroidJavaClass(FacadeName);
            callback = new CallbackProxy(queue); // Keep the proxy alive until disposal.
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                facade.CallStatic("attachHost", activity);
            facade.CallStatic("setCallback", callback);
        }
        public void Dispatch(string json)
        {
            if (disposed) throw new ObjectDisposedException(nameof(AndroidTransport));
            facade.CallStatic("dispatch", json);
        }
        public void Pump()
        {
            if (disposed) return;
            while (queue.TryDequeue(out var message)) { callback.Removed(); Message?.Invoke(message); }
        }
        public void Dispose()
        {
            if (disposed) return;
            disposed = true;
            callback.Deactivate();
            facade.CallStatic("setCallback", new object[] { null });
            facade.CallStatic("detachHost");
            Message = null;
            while (queue.TryDequeue(out _)) callback.Removed();
            facade.Dispose();
        }
        private sealed class CallbackProxy : AndroidJavaProxy
        {
            private readonly ConcurrentQueue<string> queue;
            private int queued;
            private int dropped;
            private int active = 1;
            internal int DroppedMessages => Volatile.Read(ref dropped);
            internal CallbackProxy(ConcurrentQueue<string> queue) : base("com.gamebridge.bridge.BridgeCallback") { this.queue = queue; }
            internal void Deactivate() => Interlocked.Exchange(ref active, 0);
            internal void Removed() => Interlocked.Decrement(ref queued);
            public void onMessage(string json)
            {
                if (json == null || Volatile.Read(ref active) == 0) return;
                if (Interlocked.Increment(ref queued) > 100)
                {
                    Interlocked.Decrement(ref queued);
                    Interlocked.Increment(ref dropped);
                    return;
                }
                queue.Enqueue(json);
            }
        }
    }
}
#endif
