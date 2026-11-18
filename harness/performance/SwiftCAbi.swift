import Foundation
import Darwin
import GameBridgeNative

private let completed = DispatchSemaphore(value: 0)
private let lock = NSLock()
private var response: [String:Any]?
private var outstanding = 0
private var callbacks = 0
private let callback: GBCallback = { pointer, count in
    guard let pointer, count > 0 else { return }
    let data=Data(bytes:pointer,count:Int(count))
    let decoded=(try? JSONSerialization.jsonObject(with:data)) as? [String:Any]
    guard decoded?["kind"] as? String == "response" else { return }
    lock.lock(); response=decoded; callbacks += 1; outstanding -= 1; lock.unlock(); completed.signal()
}
@main struct CAbiMeasurement {
    static func rss() -> Int64 { var value=rusage(); getrusage(RUSAGE_SELF,&value); return Int64(value.ru_maxrss) }
    static func main() throws {
        precondition(GB_ProtocolVersion()==1); GB_SetCallback(callback)
        var timing=[String:[Double]](); let before=rss()
        func invoke(_ op:String,_ session:String,_ payload:[String:Any]) throws -> Double {
            let id=UUID().uuidString.lowercased()
            let data=try JSONSerialization.data(withJSONObject:["protocolVersion":1,"sdkSessionId":session,"kind":"request","requestId":id,"operation":op,"payload":payload])
            lock.lock(); outstanding += 1; response=nil; lock.unlock()
            let start=DispatchTime.now().uptimeNanoseconds
            data.withUnsafeBytes { GB_Dispatch($0.bindMemory(to:UInt8.self).baseAddress,Int32(data.count)) }
            precondition(completed.wait(timeout:.now()+10) == .success,"C ABI response timeout")
            let elapsed=Double(DispatchTime.now().uptimeNanoseconds-start)/1e6
            lock.lock(); let result=response; lock.unlock()
            precondition(result?["requestId"] as? String==id && result?["sdkSessionId"] as? String==session && result?["ok"] as? Bool==true)
            return elapsed
        }
        for index in 0..<120 {
            let session=UUID().uuidString.lowercased()
            let initialize=try invoke("sdk.initialize",session,["providerMode":"LOCAL_MOCK","appId":"performance-local","backendBaseUrl":"http://127.0.0.1:1","requestTimeoutMs":1000,"developmentKey":String(repeating:"x",count:32),"mockSubject":"A"])
            let status=try invoke("sdk.status",session,[:])
            let shutdown=try invoke("sdk.shutdown",session,[:])
            if index>=20 { timing["initialize",default:[]].append(initialize);timing["statusRoundtrip",default:[]].append(status);timing["shutdown",default:[]].append(shutdown) }
        }
        var summaries=[String:[String:Double]]()
        for (name,values) in timing { let sorted=values.sorted(); summaries[name] = ["p50Ms":sorted[49],"p95Ms":sorted[94],"maxMs":sorted[99]] }
        lock.lock(); let remaining=outstanding; let delivered=callbacks; lock.unlock()
        GB_Shutdown()
        let report:[String:Any] = ["scope":"Actual packaged Swift C ABI; LOCAL_MOCK initialization without HTTP requests; 120 independent sessions", "warmup":20,"samplesPerOperation":100,"timings":summaries,"callbacks":delivered,"harnessOutstandingCallbacks":remaining,"peakRssBeforeBytes":before,"peakRssAfterBytes":rss(),"os":ProcessInfo.processInfo.operatingSystemVersionString,"taskCancellation":"NOT_RUN","continuationLifetime":"NOT_RUN","sdkPrivatePending":"NOT_OBSERVED","memoryMeaning":"Process high-water RSS, not a leak measurement"]
        print(String(data:try JSONSerialization.data(withJSONObject:report,options:[.sortedKeys]),encoding:.utf8)!)
    }
}
