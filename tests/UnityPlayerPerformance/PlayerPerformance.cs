using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using GameBridge;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Profiling;

// Dedicated Player measurement; no Provider, purchase or user account calls.
public sealed class PlayerPerformance : MonoBehaviour
{
    private readonly List<double> frames = new List<double>();
    private bool collecting;
    private void Update() { if (collecting) frames.Add(Time.unscaledDeltaTime * 1000.0); }
    private static object Distribution(List<double> values)
    {
        var sorted=values.OrderBy(x=>x).ToArray();
        if (sorted.Length==0) throw new InvalidOperationException("NO_MEASUREMENTS");
        return new { samples=sorted.Length,p50Ms=sorted[(int)Math.Ceiling(sorted.Length*.50)-1],p95Ms=sorted[(int)Math.Ceiling(sorted.Length*.95)-1],maxMs=sorted[sorted.Length-1] };
    }
    public static async Task Run(GameBridgeConfig config, int expectedThread)
    {
        var go=new GameObject("GameBridgeDedicatedPerformance"); DontDestroyOnLoad(go);
        var probe=go.AddComponent<PlayerPerformance>();
        var initialize=new List<double>();var callback=new List<double>();var shutdown=new List<double>();var scene=new List<double>();
        long before=Profiler.GetTotalAllocatedMemoryLong();long managedBefore=Profiler.GetMonoUsedSizeLong();
        var original=SceneManager.GetActiveScene();int pendingMax=0;GameBridgeClient active=null;
        var weak=new List<WeakReference>();
        try {
            for(int i=0;i<120;i++) {
                probe.collecting=i>=20;
                active=GameBridgeSdk.Create(config);weak.Add(new WeakReference(active));
                var timer=Stopwatch.StartNew();await active.InitializeAsync(config);double init=timer.Elapsed.TotalMilliseconds;
                timer.Restart();await active.GetNativeDiagnosticsAsync();double roundtrip=timer.Elapsed.TotalMilliseconds;
                if(Thread.CurrentThread.ManagedThreadId!=expectedThread)throw new InvalidOperationException("PERFORMANCE_MAIN_THREAD");
                timer.Restart();var temporary=SceneManager.CreateScene("GB_Performance_"+i);SceneManager.SetActiveScene(temporary);
                await Task.Yield();SceneManager.SetActiveScene(original);var unload=SceneManager.UnloadSceneAsync(temporary);
                while(!unload.isDone)await Task.Yield();double transition=timer.Elapsed.TotalMilliseconds;
                await active.GetNativeDiagnosticsAsync(); // Native callback must still reach the same main thread after scene changes.
                pendingMax=Math.Max(pendingMax,active.GetDiagnostics().PendingCount);
                timer.Restart();await active.ShutdownAsync();double close=timer.Elapsed.TotalMilliseconds;
                pendingMax=Math.Max(pendingMax,active.GetDiagnostics().PendingCount);active.Dispose();active=null;
                if(i>=20){initialize.Add(init);callback.Add(roundtrip);shutdown.Add(close);scene.Add(transition);}
            }
            probe.collecting=false;
            GC.Collect();GC.WaitForPendingFinalizers();GC.Collect();
            for(int i=0;i<5;i++)await Task.Yield();
            var result=new { scope="Actual Unity Player LOCAL_MOCK Native callback/lifecycle and temporary scene creation/unload; no real providers",warmup=20,samples=100,
                initialize=Distribution(initialize),nativeDiagnosticsRoundtripToMainThread=Distribution(callback),shutdown=Distribution(shutdown),sceneTransition=Distribution(scene),frameIntervals=Distribution(probe.frames),
                unityAllocatedBeforeBytes=before,unityAllocatedAfterBytes=Profiler.GetTotalAllocatedMemoryLong(),managedUsedBeforeBytes=managedBefore,managedUsedAfterBytes=Profiler.GetMonoUsedSizeLong(),
                managedWeakClientsRetained=weak.Count(x=>x.IsAlive),pendingAfterCompletedCallsMax=pendingMax,unityVersion=Application.unityVersion,platform=Application.platform.ToString(),
                firstMeasuredInitializationMeaning="Warmup excluded; app first initialization is the preceding baseline flow",memoryMeaning="Runtime Profiler API snapshots after forced managed GC; not Native heap or leak proof; Unity Profiler UI not used",mainThreadCpuBlocking="NOT_MEASURED" };
            UnityEngine.Debug.Log("GB_MOCK_PERFORMANCE_JSON "+JsonConvert.SerializeObject(result));
            if(pendingMax!=0)throw new InvalidOperationException("PERFORMANCE_PENDING_RETAINED");
        } finally {active?.Dispose();Destroy(go);}
    }
}
