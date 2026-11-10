import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeApple

final class PurchaseCoordinatorTests: XCTestCase {
    func testPendingCannotGrantAndVerifiedGrantIsBoundAndIdempotent() async throws {
        let user = UUID(), binding = UUID(), purchase = UUID()
        let coordinator = PurchaseCoordinator(userId: user, bindingId: binding, productId: "coins_100")
        let grant = ServerGrant(userId: user, bindingId: binding, productId: "coins_100", transactionKey: "store-transaction", serverPurchaseId: purchase)
        try await coordinator.observe(.pending, key: "store-transaction")
        do { _ = try await coordinator.acceptServerGrant(grant); XCTFail("pending grant") } catch let error as SdkFailure { XCTAssertEqual(error.code, "VERIFICATION_FAILED") }
        try await coordinator.observe(.purchased, key: "store-transaction")
        let wrong = ServerGrant(userId: UUID(), bindingId: binding, productId: "coins_100", transactionKey: "store-transaction", serverPurchaseId: purchase)
        do { _ = try await coordinator.acceptServerGrant(wrong); XCTFail("wrong account") } catch let error as SdkFailure { XCTAssertEqual(error.code, "PURCHASE_ACCOUNT_MISMATCH") }
        let first = try await coordinator.acceptServerGrant(grant), duplicate = try await coordinator.acceptServerGrant(grant)
        XCTAssertTrue(first); XCTAssertFalse(duplicate)
        let snapshot = await coordinator.snapshot(); XCTAssertEqual(snapshot.finalization, .pending)
        try await coordinator.markFinalized(); try await coordinator.markFinalized()
        let finished = await coordinator.snapshot(); XCTAssertEqual(finished.finalization, .finalized)
    }
}
