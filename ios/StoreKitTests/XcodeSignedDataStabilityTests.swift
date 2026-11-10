import XCTest
import StoreKit
import StoreKitTest
import CryptoKit

final class XcodeSignedDataStabilityTests: XCTestCase {
    @MainActor func testUnfinishedSignedDataMatchesPurchase() async throws {
        let session = try SKTestSession(configurationFileNamed: "GameBridge"); session.disableDialogs = true
        let products = try await Product.products(for: ["coins_100"])
        let product = try XCTUnwrap(products.first)
        let result = try await product.purchase(options: [.appAccountToken(UUID())])
        guard case .success(let purchased) = result, case .verified(let transaction) = purchased else { XCTFail("expected local verified purchase"); return }
        XCTAssertEqual(transaction.environment, .xcode)
        let first = SHA256.hash(data: Data(purchased.jwsRepresentation.utf8))
        var matching = false
        for await value in Transaction.unfinished {
            if case .verified(let candidate) = value, candidate.appAccountToken == transaction.appAccountToken {
                matching = true
                XCTAssertEqual(first, SHA256.hash(data: Data(value.jwsRepresentation.utf8)))
            }
        }
        XCTAssertTrue(matching)
        await transaction.finish()
    }
}
