#if UNITY_IOS && !UNITY_EDITOR
using System;
using GameBridge.Core;
using System.Collections.Concurrent;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using AOT;

namespace GameBridge.Platforms
{
    /// <summary>Copies native callback bytes immediately and delivers them from Pump.</summary>
    internal sealed class IosTransport : IWireTransport
    {
        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        private delegate void NativeCallback(IntPtr bytes, int length);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)] private static extern int GB_ProtocolVersion();
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)] private static extern void GB_SetCallback(NativeCallback callback);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)] private static extern void GB_Dispatch(IntPtr bytes, int length);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)] private static extern void GB_Shutdown();
        private static readonly NativeCallback Callback = OnNativeMessage;
        private static readonly object InstanceLock = new object();
        private static IosTransport current;
        private readonly ConcurrentQueue<string> queue = new ConcurrentQueue<string>();
        private readonly UTF8Encoding utf8 = new UTF8Encoding(false, true);
        private int queued;
        private int dropped;
        private int active = 1;
        public event Action<string> Message;
        internal int DroppedMessages => Volatile.Read(ref dropped);

        internal IosTransport()
        {
            lock (InstanceLock)
            {
                if (current != null) throw new InvalidOperationException("A bridge transport is already active.");
                if (GB_ProtocolVersion() != 1) throw new InvalidOperationException("BRIDGE_PROTOCOL_MISMATCH");
                Volatile.Write(ref current, this);
                try { GB_SetCallback(Callback); }
                catch { Volatile.Write(ref current, null); throw; }
            }
        }
        public void Dispatch(string json)
        {
            if (Volatile.Read(ref active) == 0) throw new ObjectDisposedException(nameof(IosTransport));
            var bytes = utf8.GetBytes(json ?? throw new ArgumentNullException(nameof(json)));
            if (bytes.Length == 0 || bytes.Length > 256 * 1024) throw new ArgumentOutOfRangeException(nameof(json));
            var pin = GCHandle.Alloc(bytes, GCHandleType.Pinned);
            try { GB_Dispatch(pin.AddrOfPinnedObject(), bytes.Length); }
            finally { pin.Free(); }
        }
        public void Pump()
        {
            if (Volatile.Read(ref active) == 0) return;
            while (queue.TryDequeue(out var message)) { Interlocked.Decrement(ref queued); Message?.Invoke(message); }
        }
        [MonoPInvokeCallback(typeof(NativeCallback))]
        private static void OnNativeMessage(IntPtr pointer, int length)
        {
            var target = Volatile.Read(ref current);
            if (target == null || pointer == IntPtr.Zero || length <= 0 || length > 256 * 1024 || Volatile.Read(ref target.active) == 0) return;
            try
            {
                var copy = new byte[length];
                Marshal.Copy(pointer, copy, 0, length);
                var message = target.utf8.GetString(copy);
                if (Interlocked.Increment(ref target.queued) > 100)
                {
                    Interlocked.Decrement(ref target.queued); Interlocked.Increment(ref target.dropped); return;
                }
                target.queue.Enqueue(message);
            }
            catch (DecoderFallbackException) { Interlocked.Increment(ref target.dropped); }
        }
        public void Dispose()
        {
            if (Interlocked.Exchange(ref active, 0) == 0) return;
            lock (InstanceLock)
            {
                if (ReferenceEquals(current, this)) { Volatile.Write(ref current, null); GB_SetCallback(null); GB_Shutdown(); }
            }
            Message = null;
            while (queue.TryDequeue(out _)) Interlocked.Decrement(ref queued);
        }
    }
}
#endif
