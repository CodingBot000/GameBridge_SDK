#if UNITY_IOS && !UNITY_EDITOR
using GameBridge;
using GameBridge.iOSHost;
using UnityEngine;

/// Add explicitly to the sample scene to enable host-managed iOS push.
public sealed class NativeDemoIosPush : MonoBehaviour
{
    [SerializeField] private NativeDemo demo;
    private IosPushHostAdapter adapter;
    private GameBridgeClient attached;
    private void Start()
    {
        if (demo == null) demo = FindAnyObjectByType<NativeDemo>();
        adapter = gameObject.AddComponent<IosPushHostAdapter>();
    }
    private void Update()
    {
        var current = demo != null ? demo.Client : null;
        if (ReferenceEquals(current, attached)) return;
        adapter.Detach(); attached = current;
        if (attached != null) adapter.Attach(attached);
    }
    private void OnDestroy() { if (adapter != null) adapter.Detach(); attached = null; }
}
#endif
