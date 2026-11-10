import Foundation

public enum PushEventKind: Hashable { case received, opened }
public struct PushRouteEvent: Equatable {
    public let payload: PushPayload
    public let kind: PushEventKind
    public init(payload: PushPayload, kind: PushEventKind) { self.payload = payload; self.kind = kind }
}
public enum PushEnqueueResult { case queued, deliver, duplicate, busy }
/// One instance per SDK session. Reset it on logout or account change.
public actor PushRouter {
    private var ready = false
    private var queue: [PushRouteEvent] = []
    private var seen: [String: Set<PushEventKind>] = [:]
    private var recency: [String] = []
    public init() {}
    public func submit(_ event: PushRouteEvent) -> PushEnqueueResult {
        let id = event.payload.messageId
        if seen[id]?.contains(event.kind) == true {
            recency.removeAll { $0 == id }; recency.append(id)
            return .duplicate
        }
        if !ready && queue.count >= 100 {
            if seen[id] != nil { recency.removeAll { $0 == id }; recency.append(id) }
            return .busy
        }
        seen[id, default: []].insert(event.kind)
        recency.removeAll { $0 == id }; recency.append(id)
        if recency.count > 200 { let oldest = recency.removeFirst(); seen.removeValue(forKey: oldest) }
        if ready { return .deliver }
        queue.append(event); return .queued
    }
    public func setReady() -> [PushRouteEvent] { ready = true; defer { queue.removeAll() }; return queue }
    public func reset() { ready = false; queue.removeAll(); seen.removeAll(); recency.removeAll() }
}
