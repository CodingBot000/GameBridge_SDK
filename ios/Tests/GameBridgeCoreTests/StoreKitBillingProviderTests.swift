import XCTest
@testable import GameBridgeApple

final class StoreKitBillingProviderTests: XCTestCase {
    func testGrantMustMatchAccountAndTransactionAndDoesNotExposeProof() throws {
        let account = ApplePurchaseAccount(userId: UUID(), binding: UUID())
        let proof = ApplePurchaseProof(transactionId: 42, productId: "coins", binding: account.binding, signedTransaction: "secret-jws")
        let grant = ServerGrant(userId: account.userId, bindingId: account.binding, productId: "coins", transactionKey: "42", serverPurchaseId: UUID())
        XCTAssertNoThrow(try acceptAppleGrant(grant, proof: proof, account: account, current: account))
        XCTAssertThrowsError(try acceptAppleGrant(grant, proof: proof, account: account, current: ApplePurchaseAccount(userId: UUID(), binding: UUID())))
        let wrong = ServerGrant(userId: account.userId, bindingId: account.binding, productId: "coins", transactionKey: "43", serverPurchaseId: UUID())
        XCTAssertThrowsError(try acceptAppleGrant(wrong, proof: proof, account: account, current: account))
        XCTAssertFalse(String(describing: proof).contains("secret-jws"))
    }
}
