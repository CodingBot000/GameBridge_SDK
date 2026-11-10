import XCTest
@testable import GameBridgeCore

final class DiagnosticsTests: XCTestCase {
    func testDiagnosticsRetainNewest200TypedEvents() async {
        let diagnostics = Diagnostics(), first = UUID(), last = UUID()
        await diagnostics.record(.auth, .started, requestId: first)
        for _ in 0..<199 { await diagnostics.record(.push, .pending) }
        await diagnostics.record(.shutdown, .succeeded, requestId: last)
        let events = await diagnostics.snapshot()
        XCTAssertEqual(events.count, 200)
        XCTAssertFalse(events.contains { $0.requestId == first })
        XCTAssertEqual(events.last?.requestId, last)
    }
}
