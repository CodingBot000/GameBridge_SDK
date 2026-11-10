import XCTest
@testable import GameBridgeCore

final class VersionTests: XCTestCase {
    func testDevelopmentVersion() {
        XCTAssertEqual(GameBridgeVersion.current, "0.1.0-dev")
    }
}
