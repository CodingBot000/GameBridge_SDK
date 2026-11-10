import Foundation
import XCTest
@testable import GameBridgeCore

final class MockPushEventDecoderTests: XCTestCase {
    func testOnlyAllowlistedFieldsAndRoutes() throws {
        let payload = MockPushEventDecoder.decode(Data(#"{"messageId":"one","route":"store","campaignId":"campaign","token":"secret"}"#.utf8))
        XCTAssertEqual(payload?.messageId, "one")
        XCTAssertEqual(payload?.route, "store")
        XCTAssertEqual(payload?.campaignId, "campaign")
        XCTAssertNil(MockPushEventDecoder.decode(Data(#"{"messageId":"one","route":"https://bad"}"#.utf8)))
        XCTAssertNil(MockPushEventDecoder.decode(Data(#"{"messageId":"one","route":"home","campaignId":42}"#.utf8)))
        XCTAssertNil(MockPushEventDecoder.decode(Data(repeating: 0, count: BridgeProtocol.maxBytes + 1)))
        XCTAssertNil(MockPushEventDecoder.decode(Data([0xc3, 0x28])))
    }
}
