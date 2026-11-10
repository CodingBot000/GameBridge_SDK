import XCTest
import StoreKit
import StoreKitTest
import CryptoKit
@testable import GameBridgeApple

final class XcodeSignedDataStabilityTests: XCTestCase {
    @MainActor func testUnfinishedSignedDataMatchesPurchase() async throws {
        let session = try SKTestSession(configurationFileNamed: "GameBridge"); session.disableDialogs = true
        let products = try await Product.products(for: ["coins_100"]); let product = try XCTUnwrap(products.first)
        let account = UUID()
        let firstResult = try await product.purchase(options: [.appAccountToken(account)])
        guard case .success(let first) = firstResult, case .verified(let firstTransaction) = first else { XCTFail("expected local verified purchase"); return }
        let firstKey = try XCTUnwrap(xcodeStableIdentity(first.jwsRepresentation))
        var recoveredKey: String?
        for await result in Transaction.unfinished {
            if case .verified(let value) = result, value.appAccountToken == account { recoveredKey = xcodeStableIdentity(result.jwsRepresentation) }
        }
        XCTAssertEqual(firstKey, recoveredKey, "same unfinished transaction must retain its candidate identity")
        await firstTransaction.finish()
        let secondResult = try await product.purchase(options: [.appAccountToken(account)])
        guard case .success(let second) = secondResult, case .verified(let secondTransaction) = second else { XCTFail("expected second local verified purchase"); return }
        let secondKey = try XCTUnwrap(xcodeStableIdentity(second.jwsRepresentation))
        XCTAssertNotEqual(firstKey, secondKey, "completed sequential purchases must have different candidate identities")
        await secondTransaction.finish()
    }
}
