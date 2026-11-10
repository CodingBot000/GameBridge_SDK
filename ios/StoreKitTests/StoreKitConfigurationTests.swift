import XCTest
import StoreKit
import StoreKitTest

final class StoreKitConfigurationTests: XCTestCase {
    func testLocalProductsAreAvailable() async throws {
        let session = try SKTestSession(configurationFileNamed: "GameBridge")
        session.disableDialogs = true
        let products = try await Product.products(for: ["coins_100", "premium_unlock"])
        XCTAssertEqual(Set(products.map(\.id)), Set(["coins_100", "premium_unlock"]))
        XCTAssertEqual(products.first { $0.id == "coins_100" }?.price, Decimal(string: "0.99"))
        XCTAssertEqual(products.first { $0.id == "premium_unlock" }?.price, Decimal(string: "1.99"))
    }
}
