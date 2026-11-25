import Foundation
import XCTest
@testable import GameBridgeCore

final class VersionTests: XCTestCase {
    func testDevelopmentVersion() throws {
        let root = (0..<4).reduce(URL(fileURLWithPath: #filePath)) { url, _ in url.deletingLastPathComponent() }
        let version = try String(contentsOf: root.appendingPathComponent("VERSION"), encoding: .utf8)
        XCTAssertEqual(GameBridgeVersion.current, version.trimmingCharacters(in: .whitespacesAndNewlines))
    }
}
