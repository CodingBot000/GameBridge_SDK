#if UNITY_IOS && !UNITY_EDITOR
using System;
using System.Collections;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using GameBridge.Core;
using Unity.Notifications.iOS;
using UnityEngine;

namespace GameBridge.iOSHost
{
    /// <summary>Host owns registration; no permission dialog appears until RequestRegistration is called.</summary>
    public sealed class IosPushHostAdapter : MonoBehaviour
    {
        private GameBridgeClient client;
        private readonly HostPushQueue pending = new HostPushQueue();
        private bool requesting, registering, forwarding, paused;
        private TaskCompletionSource<AuthorizationResult> authorization;
        private HostDriver driver;
        public event Action<string> Status;

        private sealed class AuthorizationResult { internal bool Granted; internal string Token; }
        private sealed class HostDriver : IHostPushDriver
        {
            private readonly IosPushHostAdapter owner;
            internal HostDriver(IosPushHostAdapter owner) { this.owner = owner; }
            public Task<PushPermission> RequestPermissionAsync(CancellationToken cancellation) => owner.RequestPermissionAsync(cancellation);
            public Task<PushRegistration> RegisterAsync(CancellationToken cancellation) => owner.RegisterAsync(cancellation);
        }
        public void Attach(GameBridgeClient value)
        {
            if (value == null) throw new ArgumentNullException(nameof(value));
            if (ReferenceEquals(client, value)) return;
            Detach(); client = value; driver = new HostDriver(this); value.AttachHostPushDriver(driver); value.Disposed += OnClientDisposed; paused = false;
        }
        public void Detach()
        {
            if (client != null && driver != null) { client.Disposed -= OnClientDisposed; client.DetachHostPushDriver(driver); }
            authorization?.TrySetException(new SdkException("NOT_INITIALIZED"));
            client = null; driver = null; pending.Clear(); paused = false;
        }
        private void OnClientDisposed(GameBridgeClient owner) { if (ReferenceEquals(client, owner)) Detach(); }
        public void RetryPending() { paused = false; }
        private void OnEnable() { iOSNotificationCenter.OnRemoteNotificationReceived += OnReceived; }
        private void OnDisable() { iOSNotificationCenter.OnRemoteNotificationReceived -= OnReceived; }
        private void OnDestroy() { Detach(); }
        private void OnApplicationFocus(bool focused) { if (focused && isActiveAndEnabled) StartCoroutine(QueryLastOpened()); }
        private IEnumerator QueryLastOpened()
        {
            var operation = iOSNotificationCenter.QueryLastRespondedNotification();
            yield return operation;
            Add(operation.Notification, true);
        }
        private void Update() { if (!forwarding && !paused && client != null && client.GetStatus().State == "READY" && pending.Count > 0) _ = ForwardNext(); }

        public void RequestRegistration() { _ = RegisterAndReport(); }
        private async Task RegisterAndReport()
        {
            var owner = client;
            try { await RegisterAsync(default); if (ReferenceEquals(owner, client)) Status?.Invoke("REGISTERED"); }
            catch (SdkException error) { if (ReferenceEquals(owner, client)) Status?.Invoke(error.Code); }
            catch (Exception) { if (ReferenceEquals(owner, client)) Status?.Invoke("INTERNAL_ERROR"); }
        }
        private async Task<PushPermission> RequestPermissionAsync(CancellationToken cancellation)
        {
            var result = await AuthorizeAsync(false, cancellation);
            return new PushPermission { provider = "APNS", permission = result.Granted ? "GRANTED" : "DENIED" };
        }
        private async Task<PushRegistration> RegisterAsync(CancellationToken cancellation)
        {
            if (registering) throw new SdkException("BUSY", true);
            registering = true; var owner = client;
            try
            {
                var result = await AuthorizeAsync(true, cancellation);
                if (!result.Granted) throw new SdkException("PERMISSION_DENIED");
                if (string.IsNullOrEmpty(result.Token)) throw new SdkException("CONFIG_REQUIRED");
                if (owner == null || !ReferenceEquals(owner, client)) throw new SdkException("NOT_INITIALIZED");
                var fingerprint = await owner.ForwardHostPushTokenAsync(result.Token, cancellation);
                if (!ReferenceEquals(owner, client)) throw new SdkException("NOT_INITIALIZED");
                return new PushRegistration { provider = "APNS", registered = true, permission = "GRANTED", tokenFingerprint = fingerprint,
                    updatedAt = DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", CultureInfo.InvariantCulture) };
            }
            finally { registering = false; }
        }
        private async Task<AuthorizationResult> AuthorizeAsync(bool registerRemote, CancellationToken cancellation)
        {
            if (cancellation.IsCancellationRequested) throw new SdkException("CANCELED");
            if (client == null || client.GetStatus().State != "READY" || !isActiveAndEnabled) throw new SdkException("NOT_INITIALIZED");
            if (requesting) throw new SdkException("BUSY", true);
            var completion = new TaskCompletionSource<AuthorizationResult>(TaskCreationOptions.RunContinuationsAsynchronously);
            authorization = completion; requesting = true;
            try { StartCoroutine(Authorize(registerRemote, completion)); }
            catch { requesting = false; authorization = null; throw; }
            using (cancellation.Register(() => completion.TrySetException(new SdkException("CANCELED")))) return await completion.Task;
        }
        private IEnumerator Authorize(bool registerRemote, TaskCompletionSource<AuthorizationResult> completion)
        {
            AuthorizationRequest request = null;
            try { request = new AuthorizationRequest(AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound, registerRemote); }
            catch (Exception) { completion.TrySetException(new SdkException("INTERNAL_ERROR")); }
            if (request == null) { if (ReferenceEquals(authorization, completion)) authorization = null; requesting = false; yield break; }
            try
            {
                using (request)
                {
                    while (!request.IsFinished) yield return null;
                    if (!string.IsNullOrEmpty(request.Error)) completion.TrySetException(new SdkException("INTERNAL_ERROR"));
                    else completion.TrySetResult(new AuthorizationResult { Granted = request.Granted, Token = request.DeviceToken });
                }
            }
            finally { if (ReferenceEquals(authorization, completion)) authorization = null; requesting = false; }
        }
        private void OnReceived(iOSNotification notification) { Add(notification, false); }
        private void Add(iOSNotification notification, bool opened)
        {
            if (notification == null || !(notification.Trigger is iOSNotificationPushTrigger)) return;
            var result = pending.Add(notification.Data, opened);
            if (result == HostPushEnqueue.Busy) Status?.Invoke("BUSY");
        }
        private async Task ForwardNext()
        {
            forwarding = true; var value = pending.Peek(); var owner = client;
            try {
                await owner.ForwardHostPushEventAsync(value.Id, value.Route, value.Campaign, value.Opened);
                if (ReferenceEquals(owner, client)) pending.Complete(value);
            } catch (SdkException error) { if (ReferenceEquals(owner, client)) { paused = true; Status?.Invoke(error.Code); } }
              catch (Exception) { if (ReferenceEquals(owner, client)) { paused = true; Status?.Invoke("INTERNAL_ERROR"); } }
            finally { forwarding = false; }
        }
    }
}
#endif
