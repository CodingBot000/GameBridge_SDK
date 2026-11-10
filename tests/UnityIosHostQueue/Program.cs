using System;
using GameBridge.iOSHost;
class Program {
 static string Json(string id, string route = "home") => "{\"messageId\":\"" + id + "\",\"route\":\"" + route + "\",\"url\":\"https://ignored.invalid\"}";
 static void Main() {
  var queue = new HostPushQueue();
  Check(queue.Add(Json("first"), false) == HostPushEnqueue.Queued);
  Check(queue.Add(Json("first"), false) == HostPushEnqueue.Duplicate);
  Check(queue.Add(Json("first"), true) == HostPushEnqueue.Queued);
  Check(queue.Add(Json("bad", "https://ignored.invalid"), false) == HostPushEnqueue.Invalid);
  Check(queue.Add("{\"messageId\":42,\"route\":\"home\"}", false) == HostPushEnqueue.Invalid);
  var first = queue.Peek(); Check(first.Id == "first" && first.Route == "home"); queue.Complete(first); queue.Complete(queue.Peek());
  for (int i = 0; i < 100; i++) Check(queue.Add(Json("q" + i), false) == HostPushEnqueue.Queued);
  Check(queue.Add(Json("overflow"), false) == HostPushEnqueue.Busy);
  while (queue.Count > 0) queue.Complete(queue.Peek());
  for (int i = 0; i < 200; i++) { Check(queue.Add(Json("new" + i), false) == HostPushEnqueue.Queued); queue.Complete(queue.Peek()); }
  Check(queue.Add(Json("first"), false) == HostPushEnqueue.Queued);
  queue.Clear(); Check(queue.Count == 0 && queue.Add(Json("new199"), false) == HostPushEnqueue.Queued);
  Console.WriteLine("Unity iOS host queue smoke: PASS");
 }
 static void Check(bool condition) { if (!condition) throw new Exception("Host push queue assertion failed"); }
}
