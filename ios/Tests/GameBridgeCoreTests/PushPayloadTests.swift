import XCTest
@testable import GameBridgeCore

final class PushPayloadTests: XCTestCase {
    func testOnlyAllowlistedRoutesAndFieldsAreAccepted() {
        let message = PushPayload(data: ["messageId": "msg", "route": "store", "campaignId": "campaign", "url": "https://invalid.example"])
        XCTAssertEqual(message?.route, "store")
        XCTAssertEqual(message?.campaignId, "campaign")
        XCTAssertNil(PushPayload(data: ["messageId": "msg", "route": "https://invalid.example"]))
        XCTAssertNil(PushPayload(data: ["messageId": "", "route": "home"]))
        XCTAssertNil(PushPayload(data: ["messageId": "msg", "route": "home", "campaignId": 123]))
    }
}
