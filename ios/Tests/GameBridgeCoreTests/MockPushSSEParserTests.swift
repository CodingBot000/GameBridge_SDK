import Foundation
import XCTest
@testable import GameBridgeCore

final class MockPushSSEParserTests: XCTestCase {
    func testIncrementalSSEIgnoresHeartbeatAndUntrustedFields() {
        var parser = MockPushSSEParser(); var received: [PushPayload] = []
        let input = ":heartbeat\n\nevent:push\ndata:{\"messageId\":\"one\",\"route\":\"home\",\"token\":\"secret\"}\n\n"
        for byte in input.utf8 { if let value = parser.append(byte) { received.append(value) } }
        XCTAssertEqual(received, [PushPayload(data: ["messageId": "one", "route": "home"])!])
    }
}
