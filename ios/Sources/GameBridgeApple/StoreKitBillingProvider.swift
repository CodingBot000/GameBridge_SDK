import Foundation
import StoreKit
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// StoreKit proofs stay internal and are never returned as public SDK results.
struct ApplePurchaseProof: CustomStringConvertible {
    let transactionId: UInt64
    let productId: String
    let binding: UUID?
    let signedTransaction: String
    var description: String { "ApplePurchaseProof([redacted])" }
}

/// Implementations must return only after the Backend durably commits the grant.
protocol ApplePurchaseProofSink {
    func verify(_ proof: ApplePurchaseProof, userId: UUID) async throws -> ServerGrant
}

struct ApplePurchaseAccount: Equatable {
    let userId: UUID
    let binding: UUID
}

enum ApplePurchaseOutcome { case pending, verificationPending, cancelled, verified(ServerGrant) }
public struct AppleRecoveryCounts {
    public internal(set) var examinedCount = 0
    public internal(set) var recoveredCount = 0
    public internal(set) var deferredCount = 0
    public internal(set) var failureCount = 0
    public init() {}
}

struct AppleRecoveryAccumulator {
    private var seen = Set<UInt64>()
    private(set) var counts = AppleRecoveryCounts()
    mutating func begin(_ transactionId: UInt64) -> Bool {
        guard seen.insert(transactionId).inserted else { return false }
        counts.examinedCount += 1; return true
    }
    mutating func success() { counts.recoveredCount += 1 }
    mutating func failure(_ error: Error) throws {
        if error is CancellationError { throw SdkFailure("CANCELED") }
        if let failure = error as? SdkFailure {
            if failure.code == "CANCELED" { throw failure }
            if ["VERIFICATION_FAILED", "PURCHASE_ACCOUNT_MISMATCH", "UNSUPPORTED_OPERATION"].contains(failure.code) { counts.failureCount += 1; return }
        }
        counts.deferredCount += 1
    }
}

func acceptAppleGrant(_ grant: ServerGrant, proof: ApplePurchaseProof, account: ApplePurchaseAccount, current: ApplePurchaseAccount?) throws {
    guard current == account, proof.binding == account.binding,
          grant.userId == account.userId, grant.bindingId == account.binding,
          grant.productId == proof.productId, grant.transactionKey == String(proof.transactionId) else {
        throw SdkFailure("VERIFICATION_FAILED")
    }
}

/// The caller supplies the current server-bound account and a real Backend sink.
/// No purchase sheet opens when those prerequisites or the concurrency policy are absent.
@MainActor
final class StoreKitBillingProvider {
    private let sink: ApplePurchaseProofSink?
    private let verificationConcurrency: Int?
    private let currentAccount: () -> ApplePurchaseAccount?
    private let uiGate: AppleUiGate
    private let limiter: AppleVerificationLimiter?
    private let onVerified: (ServerGrant) -> Void
    private var listener: Task<Void, Never>?
    private let recoveryFlight = AppleRecoveryFlight()

    init(sink: ApplePurchaseProofSink?, verificationConcurrency: Int? = 1, uiGate: AppleUiGate? = nil, onVerified: @escaping (ServerGrant) -> Void = { _ in }, currentAccount: @escaping () -> ApplePurchaseAccount?) {
        self.sink = sink
        self.verificationConcurrency = verificationConcurrency
        self.currentAccount = currentAccount
        self.uiGate = uiGate ?? AppleUiGate()
        self.onVerified = onVerified
        self.limiter = verificationConcurrency.flatMap { $0 > 0 ? AppleVerificationLimiter(limit: $0) : nil }
    }
    deinit { listener?.cancel() }

    func start() {
        guard listener == nil else { return }
        listener = Task { [weak self] in
            for await result in Transaction.updates {
                guard !Task.isCancelled, let self else { return }
                if let grant = try? await self.process(result) { self.onVerified(grant) }
            }
        }
    }
    func stop() { listener?.cancel(); listener = nil; recoveryFlight.cancel() }

    func products(ids: Set<String>) async throws -> [Product] {
        try await Product.products(for: ids)
    }

    func purchase(_ product: Product) async throws -> ApplePurchaseOutcome {
        guard sink != nil, let limit = verificationConcurrency, limit > 0, let account = currentAccount() else {
            throw SdkFailure("CONFIG_REQUIRED")
        }
        try uiGate.acquire()
        defer { uiGate.release() }
        switch try await product.purchase(options: [.appAccountToken(account.binding)]) {
        case .success(let result):
            do { return .verified(try await process(result)) }
            catch let failure as SdkFailure where ["VERIFICATION_FAILED", "PURCHASE_ACCOUNT_MISMATCH", "UNSUPPORTED_OPERATION"].contains(failure.code) { throw failure }
            catch { return .verificationPending }
        case .pending: return .pending
        case .userCancelled: return .cancelled
        @unknown default: throw SdkFailure("VERIFICATION_FAILED")
        }
    }

    func recoverUnfinished() async throws -> AppleRecoveryCounts {
        guard let account = currentAccount() else { throw SdkFailure("SESSION_EXPIRED") }
        return try await recoveryFlight.run(account: account, userInitiated: false) { [weak self] in
            guard let self, self.currentAccount() == account else { throw SdkFailure("CANCELED") }
            var accumulator = AppleRecoveryAccumulator()
            for await result in Transaction.unfinished { try await self.recordRecovery(result, accumulator: &accumulator) }
            guard self.currentAccount() == account else { throw SdkFailure("CANCELED") }
            return accumulator.counts
        }
    }
    /// Only call from an explicit user restore action, never during startup.
    func userRestore() async throws -> AppleRecoveryCounts {
        guard let account = currentAccount() else { throw SdkFailure("SESSION_EXPIRED") }
        return try await recoveryFlight.run(account: account, userInitiated: true) { [weak self] in
            guard let self, self.currentAccount() == account else { throw SdkFailure("CANCELED") }
            try self.uiGate.acquire(); defer { self.uiGate.release() }
            try await AppStore.sync()
            guard self.currentAccount() == account else { throw SdkFailure("CANCELED") }
            var accumulator = AppleRecoveryAccumulator()
            for await result in Transaction.unfinished { try await self.recordRecovery(result, accumulator: &accumulator) }
            for await result in Transaction.currentEntitlements { try await self.recordRecovery(result, accumulator: &accumulator) }
            guard self.currentAccount() == account else { throw SdkFailure("CANCELED") }
            return accumulator.counts
        }
    }
    private func recordRecovery(_ result: VerificationResult<Transaction>, accumulator: inout AppleRecoveryAccumulator) async throws {
        if Task.isCancelled { throw SdkFailure("CANCELED") }
        let transaction: Transaction
        switch result { case .verified(let value): transaction = value; case .unverified(let value, _): transaction = value }
        guard accumulator.begin(transaction.id) else { return }
        do { let grant = try await process(result); accumulator.success(); onVerified(grant) }
        catch { try accumulator.failure(error) }
    }

    @discardableResult private func process(_ result: VerificationResult<Transaction>) async throws -> ServerGrant {
        guard case .verified(let transaction) = result else { throw SdkFailure("VERIFICATION_FAILED") }
        guard let sink, let limiter, let account = currentAccount() else { throw SdkFailure("CONFIG_REQUIRED") }
        guard transaction.appAccountToken == account.binding, transaction.revocationDate == nil else {
            throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH")
        }
        return try await limiter.withPermit {
            guard currentAccount() == account else { throw SdkFailure("CANCELED") }
            let proof = ApplePurchaseProof(transactionId: transaction.id, productId: transaction.productID,
                                           binding: transaction.appAccountToken, signedTransaction: result.jwsRepresentation)
            let grant = try await sink.verify(proof, userId: account.userId)
            try acceptAppleGrant(grant, proof: proof, account: account, current: currentAccount())
            await transaction.finish()
            return grant
        }
    }
}
