import Foundation
import StoreKit
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
    func testExistingConfigurationProducts() async throws {
        let path = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("isolation-products.json")
        func record(_ stage: String, _ ids: [String] = []) {
            let data = try? JSONSerialization.data(withJSONObject: ["stage": stage, "productIDs": ids])
            try? data?.write(to: path, options: .atomic)
        }
        let bundle = Bundle(for: SessionTests.self)
        let url = try XCTUnwrap(bundle.url(forResource: "Current", withExtension: "storekit"))
        record("session-before")
        let session = try SKTestSession(contentsOf: url)
        record("session-created")
        do {
            let products = try await Product.products(for: ["coins_100", "premium_unlock"])
            let ids = products.map(\.id).sorted()
            record("products-returned", ids)
            XCTAssertEqual(Set(ids), Set(["coins_100", "premium_unlock"]))
        } catch {
            record("products-error")
            throw error
        }
        withExtendedLifetime(session) {}
    }
    func testMinimalConfiguration() throws { try createSession("Minimal") }
    func testExistingConfiguration() throws { try createSession("Current") }
}
