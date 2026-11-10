import XCTest
import GameBridgeCore
@testable import GameBridgeApple

final class StoreKitBillingProviderTests: XCTestCase {
    @MainActor func testVerificationLimiterSerializesAndReleasesCancelledWaiter() async throws {
        let limiter = AppleVerificationLimiter(limit: 1)
        var firstContinuation: CheckedContinuation<Void, Never>?
        var secondEntered = false
        let first = Task { @MainActor in
            try await limiter.withPermit { await withCheckedContinuation { firstContinuation = $0 } }
        }
        while firstContinuation == nil { await Task.yield() }
        let second = Task { @MainActor in try await limiter.withPermit { secondEntered = true } }
        for _ in 0..<20 { await Task.yield() }
        XCTAssertFalse(secondEntered)
        second.cancel()
        firstContinuation?.resume()
        _ = try await first.value
        do { _ = try await second.value; XCTFail("cancelled waiter") }
        catch let error as SdkFailure { XCTAssertEqual(error.code, "CANCELED") }
        let result = try await limiter.withPermit { 42 }
        XCTAssertEqual(result, 42)
        XCTAssertFalse(secondEntered)
    }
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
    func testRecoveryCountsDeduplicateAndSeparateFailures() throws {
        var counts = AppleRecoveryAccumulator()
        XCTAssertTrue(counts.begin(1)); counts.success()
        XCTAssertFalse(counts.begin(1))
        XCTAssertTrue(counts.begin(2)); try counts.failure(SdkFailure("NETWORK_UNAVAILABLE"))
        XCTAssertTrue(counts.begin(3)); try counts.failure(SdkFailure("PURCHASE_ACCOUNT_MISMATCH"))
        XCTAssertEqual(counts.counts.examinedCount, 3); XCTAssertEqual(counts.counts.recoveredCount, 1)
        XCTAssertEqual(counts.counts.deferredCount, 1); XCTAssertEqual(counts.counts.failureCount, 1)
        XCTAssertThrowsError(try counts.failure(SdkFailure("CANCELED")))
    }

}
