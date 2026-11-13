import Foundation
import StoreKitTest
import XCTest

final class SessionTests: XCTestCase {
    private func createSession(_ name: String) throws {
        let bundle = Bundle(for: SessionTests.self)
        let url = try XCTUnwrap(bundle.url(forResource: name, withExtension: "storekit"))
        print("ISOLATION_SESSION_START \(name)")
        let session = try SKTestSession(contentsOf: url)
        print("ISOLATION_SESSION_CREATED \(name)")
        withExtendedLifetime(session) {}
    }
    func testMinimalConfiguration() throws { try createSession("Minimal") }
    func testExistingConfiguration() throws { try createSession("Current") }
}
