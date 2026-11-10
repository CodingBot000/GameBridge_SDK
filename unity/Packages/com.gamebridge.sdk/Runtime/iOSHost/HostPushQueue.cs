#if UNITY_IOS && !UNITY_EDITOR
using System;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace GameBridge.iOSHost
{
    internal sealed class HostPushEvent { internal string Id, Route, Campaign; internal bool Opened; }
    internal enum HostPushEnqueue { Queued, Duplicate, Invalid, Busy }
    /// <summary>Only normalized fields are retained; no raw token or notification JSON is stored.</summary>
    internal sealed class HostPushQueue
    {
        private readonly Queue<HostPushEvent> pending = new Queue<HostPushEvent>();
        private readonly Dictionary<string, HashSet<bool>> seen = new Dictionary<string, HashSet<bool>>();
        private readonly LinkedList<string> recency = new LinkedList<string>();
        internal int Count => pending.Count;
        internal HostPushEvent Peek() => pending.Peek();
        internal void Complete(HostPushEvent value) { if (pending.Count > 0 && ReferenceEquals(value, pending.Peek())) pending.Dequeue(); }
        internal void Clear() { pending.Clear(); seen.Clear(); recency.Clear(); }
        internal HostPushEnqueue Add(string json, bool opened)
        {
            if (string.IsNullOrWhiteSpace(json)) return HostPushEnqueue.Invalid;
            try {
                var value = JObject.Parse(json);
                if (value["messageId"]?.Type != JTokenType.String || value["route"]?.Type != JTokenType.String) return HostPushEnqueue.Invalid;
                var id = (string)value["messageId"]; var route = (string)value["route"];
                var field = value["campaignId"];
                if (field != null && field.Type != JTokenType.Null && field.Type != JTokenType.String) return HostPushEnqueue.Invalid;
                var campaign = field?.Type == JTokenType.String ? (string)field : null;
                if (string.IsNullOrWhiteSpace(id) || (route != "home" && route != "store")) return HostPushEnqueue.Invalid;
                if (seen.TryGetValue(id, out var types) && types.Contains(opened)) { Touch(id); return HostPushEnqueue.Duplicate; }
                if (pending.Count >= 100) return HostPushEnqueue.Busy;
                if (types == null) { types = new HashSet<bool>(); seen[id] = types; }
                types.Add(opened); Touch(id); pending.Enqueue(new HostPushEvent { Id = id, Route = route, Campaign = campaign, Opened = opened });
                return HostPushEnqueue.Queued;
            } catch (Exception) { return HostPushEnqueue.Invalid; }
        }
        private void Touch(string id)
        {
            recency.Remove(id); recency.AddLast(id);
            if (recency.Count > 200) { var oldest = recency.First.Value; recency.RemoveFirst(); seen.Remove(oldest); }
        }
    }
}
#endif
