import XCTest
import StoreKit
import StoreKitTest
import CryptoKit

final class XcodeSignedDataStabilityTests: XCTestCase {
    @MainActor func testUnfinishedSignedDataMatchesPurchase() async throws {
        let session = try SKTestSession(configurationFileNamed: "GameBridge"); session.disableDialogs = true
        let products = try await Product.products(for: ["coins_100"]); let product = try XCTUnwrap(products.first)
        let account = UUID()
        func payload(_ jws: String) -> [String: Any] {
            let part = String(jws.split(separator: ".")[1]).replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
            let padded = part + String(repeating: "=", count: (4 - part.count % 4) % 4)
            guard let data = Data(base64Encoded: padded), let value = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return [:] }
            return value
        }
        let firstResult = try await product.purchase(options: [.appAccountToken(account)])
        guard case .success(let first) = firstResult, case .verified(let firstTransaction) = first else { XCTFail("expected local verified purchase"); return }
        let secondResult = try await product.purchase(options: [.appAccountToken(account)])
        guard case .success(let second) = secondResult, case .verified(let secondTransaction) = second else { await firstTransaction.finish(); XCTFail("expected second local verified purchase"); return }
        let lhs = payload(first.jwsRepresentation), rhs = payload(second.jwsRepresentation)
        let keys = ["transactionId", "originalTransactionId", "productId", "purchaseDate", "originalPurchaseDate", "appAccountToken", "bundleId", "appTransactionId"]
        XCTAssertTrue(keys.allSatisfy { lhs[$0] != nil && rhs[$0] != nil }, "missing stable identity field")
        func digest(_ value: [String: Any]) throws -> SHA256.Digest {
            let selected = Dictionary(uniqueKeysWithValues: keys.compactMap { key in value[key].map { (key, $0) } })
            return SHA256.hash(data: try JSONSerialization.data(withJSONObject: selected, options: [.sortedKeys]))
        }
        XCTAssertNotEqual(try digest(lhs), try digest(rhs), "distinct local purchases must have distinct stable identity")
        await firstTransaction.finish(); await secondTransaction.finish()
    }
}
