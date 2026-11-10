using System;

namespace GameBridge.Core
{
    internal interface IWireTransport : IDisposable
    {
        event Action<string> Message;
        void Dispatch(string json);
        void Pump();
    }
}
