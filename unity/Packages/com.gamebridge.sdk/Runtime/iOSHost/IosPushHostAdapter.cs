#if UNITY_IOS && !UNITY_EDITOR
using System;
using System.Collections;
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
        private bool requesting, forwarding, paused;
        public event Action<string> Status;

        public void Attach(GameBridgeClient value) { client = value; paused = false; }
        public void Detach() { client = null; pending.Clear(); paused = false; }
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

        public void RequestRegistration()
        {
            if (requesting) { Status?.Invoke("BUSY"); return; }
            if (client == null || client.GetStatus().State != "READY") { Status?.Invoke("NOT_INITIALIZED"); return; }
            StartCoroutine(Register());
        }
        private IEnumerator Register()
        {
            requesting = true;
            try {
                using (var request = new AuthorizationRequest(AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound, true))
                {
                    while (!request.IsFinished) yield return null;
                    if (!string.IsNullOrEmpty(request.Error)) Status?.Invoke("INTERNAL_ERROR");
                    else if (!request.Granted) Status?.Invoke("PERMISSION_DENIED");
                    else if (string.IsNullOrEmpty(request.DeviceToken)) Status?.Invoke("CONFIG_REQUIRED");
                    else _ = ForwardToken(request.DeviceToken);
                }
            } finally { requesting = false; }
        }
        private async Task ForwardToken(string token)
        {
            var owner = client;
            if (owner == null) { Status?.Invoke("NOT_INITIALIZED"); return; }
            try { await owner.ForwardHostPushTokenAsync(token); if (ReferenceEquals(owner, client)) Status?.Invoke("REGISTERED"); }
            catch (SdkException error) { if (ReferenceEquals(owner, client)) Status?.Invoke(error.Code); }
            catch (Exception) { if (ReferenceEquals(owner, client)) Status?.Invoke("INTERNAL_ERROR"); }
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
