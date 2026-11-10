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

enum ApplePurchaseOutcome { case pending, cancelled, verified }

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
    private var listener: Task<Void, Never>?

    init(sink: ApplePurchaseProofSink?, verificationConcurrency: Int? = 1, uiGate: AppleUiGate? = nil, currentAccount: @escaping () -> ApplePurchaseAccount?) {
        self.sink = sink
        self.verificationConcurrency = verificationConcurrency
        self.currentAccount = currentAccount
        self.uiGate = uiGate ?? AppleUiGate()
        self.limiter = verificationConcurrency.flatMap { $0 > 0 ? AppleVerificationLimiter(limit: $0) : nil }
    }
    deinit { listener?.cancel() }

    func start() {
        guard listener == nil else { return }
        listener = Task { [weak self] in
            for await result in Transaction.updates {
                guard !Task.isCancelled, let self else { return }
                try? await self.process(result)
            }
        }
    }
    func stop() { listener?.cancel(); listener = nil }

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
        case .success(let result): try await process(result); return .verified
        case .pending: return .pending
        case .userCancelled: return .cancelled
        @unknown default: throw SdkFailure("VERIFICATION_FAILED")
        }
    }

    func recoverUnfinished() async {
        for await result in Transaction.unfinished { try? await process(result) }
    }
    func recoverEntitlements() async {
        for await result in Transaction.currentEntitlements { try? await process(result) }
    }
    /// Only call from an explicit user restore action, never during startup.
    func userRestore() async throws {
        try await AppStore.sync()
        await recoverUnfinished()
        await recoverEntitlements()
    }

    private func process(_ result: VerificationResult<Transaction>) async throws {
        guard case .verified(let transaction) = result else { throw SdkFailure("VERIFICATION_FAILED") }
        guard let sink, let limiter, let account = currentAccount() else { throw SdkFailure("CONFIG_REQUIRED") }
        guard transaction.appAccountToken == account.binding, transaction.revocationDate == nil else {
            throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH")
        }
        try await limiter.withPermit {
            guard currentAccount() == account else { throw SdkFailure("CANCELED") }
            let proof = ApplePurchaseProof(transactionId: transaction.id, productId: transaction.productID,
                                           binding: transaction.appAccountToken, signedTransaction: result.jwsRepresentation)
            let grant = try await sink.verify(proof, userId: account.userId)
            try acceptAppleGrant(grant, proof: proof, account: account, current: currentAccount())
            await transaction.finish()
        }
    }
}
