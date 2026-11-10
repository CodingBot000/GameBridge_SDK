import XCTest
@testable import GameBridgeCore

final class PushRouterTests: XCTestCase {
    private func event(_ id: String, _ kind: PushEventKind = .received) -> PushRouteEvent {
        PushRouteEvent(payload: PushPayload(data: ["messageId": id, "route": "home"])!, kind: kind)
    }
    func testQueueDedupAndBoundedRecency() async {
        let router = PushRouter(), first = event("id"), opened = event("id", .opened)
        let firstResult = await router.submit(first), duplicate = await router.submit(first), openResult = await router.submit(opened)
        XCTAssertEqual(firstResult, .queued); XCTAssertEqual(duplicate, .duplicate); XCTAssertEqual(openResult, .queued)
        let drained = await router.setReady(); XCTAssertEqual(drained, [first, opened])
        await router.reset()
        for i in 0..<100 { _ = await router.submit(event("q\(i)")) }
        let overflow = await router.submit(event("overflow")); XCTAssertEqual(overflow, .busy)
        let queued = await router.setReady(); XCTAssertEqual(queued.count, 100)
        for i in 0..<200 { _ = await router.submit(event("new\(i)")) }
        let old = await router.submit(event("q0")), recent = await router.submit(event("new199"))
        XCTAssertEqual(old, .deliver); XCTAssertEqual(recent, .duplicate)
        let touch = await router.submit(event("new1")); XCTAssertEqual(touch, .duplicate)
        _ = await router.submit(event("new200"))
        let stillRecent = await router.submit(event("new1")), evicted = await router.submit(event("new2"))
        XCTAssertEqual(stillRecent, .duplicate); XCTAssertEqual(evicted, .deliver)
    }
}
