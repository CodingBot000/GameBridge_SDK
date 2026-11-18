import Foundation
import Darwin

final class WeakHolder { weak var value: AnyObject? }
struct ImmediateProvider: SdkProvider {
    func initialize(_ config: GameBridgeConfig) async throws -> InitSnapshot { InitSnapshot(capabilities: [:]) }
    func shutdown() async throws {}
}
@main struct Measurement {
    static func peakRSS() -> Int64 {
        var usage = rusage(); getrusage(RUSAGE_SELF, &usage); return Int64(usage.ru_maxrss)
    }
    static func main() async throws {
        let config = GameBridgeConfig(appId: "measurement", mode: .editorOffline, backendBaseURL: nil)
        var initialize = [Double](); var shutdown = [Double](); var holders = [WeakHolder]()
        let before = peakRSS()
        for i in 0..<120 {
            let holder = WeakHolder()
            do {
                let coordinator = SdkCoordinator(provider: ImmediateProvider()); holder.value = coordinator
                let start = DispatchTime.now().uptimeNanoseconds
                _ = try await coordinator.initialize(config)
                let middle = DispatchTime.now().uptimeNanoseconds
                try await coordinator.shutdown()
                let end = DispatchTime.now().uptimeNanoseconds
                let state = await coordinator.status(); precondition(state == .shutdown)
                if i >= 20 { initialize.append(Double(middle-start)/1e6); shutdown.append(Double(end-middle)/1e6) }
            }
            holders.append(holder)
        }
        // Allow completed executor jobs to release their last strong references.
        try await Task.sleep(nanoseconds: 50_000_000)
        func summary(_ values: [Double]) -> [String:Double] {
            let s=values.sorted(); return ["p50Ms":s[49],"p95Ms":s[94],"maxMs":s[99]]
        }
        let result: [String:Any] = ["scope":"Swift Core coordinator with immediate fake provider; no C ABI, store or UI", "warmup":20,"samples":100,"initialize":summary(initialize),"shutdown":summary(shutdown),"weakCoordinatorRetained":holders.filter{$0.value != nil}.count,"peakRssBeforeBytes":before,"peakRssAfterBytes":peakRSS(),"memoryInterpretation":"process high-water RSS; includes runtime/allocator, does not prove leaks", "os":ProcessInfo.processInfo.operatingSystemVersionString]
        print(String(data:try JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]),encoding:.utf8)!)
    }
}
