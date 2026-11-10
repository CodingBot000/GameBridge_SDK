import XCTest
import StoreKit
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

    @MainActor func testRecoveryFlightSharesEquivalentCallsButSeparatesReasonAndAccount() async throws {
        let flight = AppleRecoveryFlight()
        let account = ApplePurchaseAccount(userId: UUID(), binding: UUID())
        var continuation: CheckedContinuation<Void, Never>?
        var executions = 0
        let work: @MainActor () async throws -> AppleRecoveryCounts = {
            executions += 1; await withCheckedContinuation { continuation = $0 }
            var counts = AppleRecoveryCounts(); counts.examinedCount = 1; counts.recoveredCount = 1; return counts
        }
        let first = Task { @MainActor in try await flight.run(account: account, userInitiated: false, work: work) }
        while continuation == nil { await Task.yield() }
        let second = Task { @MainActor in try await flight.run(account: account, userInitiated: false, work: work) }
        for _ in 0..<20 { await Task.yield() }
        do { _ = try await flight.run(account: account, userInitiated: true, work: work); XCTFail("different reason") }
        catch let failure as SdkFailure { XCTAssertEqual(failure.code, "BUSY") }
        do { _ = try await flight.run(account: ApplePurchaseAccount(userId: UUID(), binding: UUID()), userInitiated: false, work: work); XCTFail("different account") }
        catch let failure as SdkFailure { XCTAssertEqual(failure.code, "CANCELED") }
        first.cancel(); continuation?.resume()
        let result = try await second.value; XCTAssertEqual(result.recoveredCount, 1); XCTAssertEqual(executions, 1)
        do { _ = try await first.value; XCTFail("caller canceled") }
        catch let failure as SdkFailure { XCTAssertEqual(failure.code, "CANCELED") }
    }

    func testXcodeEnvironmentRejectsSandboxAndProduction() {
        if #available(iOS 16.0, macOS 13.0, *) {
            XCTAssertTrue(isXcodeStoreEnvironment(.xcode))
            XCTAssertFalse(isXcodeStoreEnvironment(.sandbox))
            XCTAssertFalse(isXcodeStoreEnvironment(.production))
        }
    }

    func testXcodeCandidateIgnoresOnlyTransientFieldsAndRejectsMalformed() throws {
        func jws(_ payload: [String: Any]) throws -> String {
            let data = try JSONSerialization.data(withJSONObject: payload)
            let encoded = data.base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
            return "header." + encoded + ".signature"
        }
        let base: [String: Any] = ["transactionId":"0", "originalTransactionId":"0", "productId":"coins_100", "purchaseDate":1,
            "originalPurchaseDate":1, "appAccountToken":"synthetic-account", "bundleId":"test.bundle", "appTransactionId":"app"]
        var dynamic = base; dynamic["signedDate"] = 123; dynamic["deviceVerificationNonce"] = "changed"
        XCTAssertEqual(xcodeStableIdentity(try jws(base)), xcodeStableIdentity(try jws(dynamic)))
        dynamic["purchaseDate"] = 2
        XCTAssertNotEqual(xcodeStableIdentity(try jws(base)), xcodeStableIdentity(try jws(dynamic)))
        dynamic.removeValue(forKey: "appAccountToken"); XCTAssertNil(xcodeStableIdentity(try jws(dynamic)))
        dynamic = base; dynamic["purchaseDate"] = true; XCTAssertNil(xcodeStableIdentity(try jws(dynamic)))
        XCTAssertNil(xcodeStableIdentity("bad"))
    }

    func testXcodeIdentityRequiresExactlyOneMatch() throws {
        XCTAssertNoThrow(try validateXcodeIdentityMatches(1))
        XCTAssertThrowsError(try validateXcodeIdentityMatches(0)) { XCTAssertEqual(($0 as? SdkFailure)?.code, "NETWORK_UNAVAILABLE") }
        XCTAssertThrowsError(try validateXcodeIdentityMatches(2)) { XCTAssertEqual(($0 as? SdkFailure)?.code, "IDEMPOTENCY_CONFLICT") }
    }

}
