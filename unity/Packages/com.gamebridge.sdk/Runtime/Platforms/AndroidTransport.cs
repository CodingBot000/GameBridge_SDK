#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using GameBridge.Core;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Android;

namespace GameBridge.Platforms
{
    /// <summary>Queues callbacks until Pump is called from Unity's main thread.</summary>
    internal sealed class AndroidTransport : IWireTransport, IHostPushPermissionDriver
    {
        private const string FacadeName = "com.gamebridge.bridge.BridgeFacade";
        private readonly ConcurrentQueue<string> queue = new ConcurrentQueue<string>();
        private readonly AndroidJavaClass facade;
        private readonly CallbackProxy callback;
        private bool disposed;
        private const string NotificationPermission = "android.permission.POST_NOTIFICATIONS";
        private readonly object permissionGate = new object();
        private PermissionCallbacks permissionCallbacks;
        private TaskCompletionSource<PushPermission> permissionWaiter;
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
        public async Task<PushPermission> RequestPermissionAsync(CancellationToken cancellation)
        {
            if (cancellation.IsCancellationRequested) throw new SdkException("CANCELED");
            if (disposed) throw new SdkException("NOT_INITIALIZED");
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    if (version.GetStatic<int>("SDK_INT") < 33)
                        return new PushPermission { provider = "FCM", permission = NotificationsEnabled() ? "GRANTED" : "DENIED" };
                if (Permission.HasUserAuthorizedPermission(NotificationPermission))
                    return new PushPermission { provider = "FCM", permission = NotificationsEnabled() ? "GRANTED" : "DENIED" };
            }
            catch (Exception) { throw new SdkException("INTERNAL_ERROR"); }
            var completion = new TaskCompletionSource<PushPermission>(TaskCreationOptions.RunContinuationsAsynchronously);
            PermissionCallbacks callbacks;
            lock (permissionGate)
            {
                if (disposed) throw new SdkException("NOT_INITIALIZED");
                if (permissionCallbacks != null) throw new SdkException("BUSY", true);
                permissionWaiter = completion; callbacks = permissionCallbacks = new PermissionCallbacks();
                callbacks.PermissionGranted += _ => FinishPermission(completion, "GRANTED", null);
                callbacks.PermissionDenied += _ => FinishPermission(completion, "DENIED", null);
                callbacks.PermissionRequestDismissed += _ => FinishPermission(completion, null, "CANCELED");
            }
            try { if (cancellation.IsCancellationRequested) FinishPermission(completion, null, "CANCELED"); else Permission.RequestUserPermission(NotificationPermission, callbacks); }
            catch (Exception) { FinishPermission(completion, null, "INTERNAL_ERROR"); }
            using (cancellation.Register(() => completion.TrySetException(new SdkException("CANCELED")))) return await completion.Task;
        }
        private static bool NotificationsEnabled()
        {
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
            using (var manager = activity.Call<AndroidJavaObject>("getSystemService", "notification"))
                return manager.Call<bool>("areNotificationsEnabled");
        }
        private void FinishPermission(TaskCompletionSource<PushPermission> completion, string value, string error)
        {
            lock (permissionGate)
            {
                if (!ReferenceEquals(permissionWaiter, completion)) return;
                permissionWaiter = null; permissionCallbacks = null;
            }
            if (error != null) completion.TrySetException(new SdkException(error));
            else completion.TrySetResult(new PushPermission { provider = "FCM", permission = value });
        }
        public void Dispose()
        {
            if (disposed) return;
            disposed = true;
            lock (permissionGate) { permissionWaiter?.TrySetException(new SdkException("NOT_INITIALIZED")); }
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
