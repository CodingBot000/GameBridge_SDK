import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

private struct XcodePendingAttempt: Codable {
    let accountId: UUID
    let transactionKey: String
    let attemptId: UUID
}
/// Only bounded identifiers are retained. Raw signed transactions and credentials are never stored here.
actor XcodeAttemptJournal {
    private let store: TokenStore
    init(store: TokenStore) { self.store = store }
    func begin(account: UUID, key: String) throws -> UUID {
        guard key.range(of: "^[0-9a-f]{64}$", options: .regularExpression) != nil else { throw SdkFailure("VERIFICATION_FAILED") }
        if let pending = try load() {
            guard pending.accountId == account else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
            guard pending.transactionKey == key else { throw SdkFailure("BUSY", retryable: true) }
            return pending.attemptId
        }
        let pending = XcodePendingAttempt(accountId: account, transactionKey: key, attemptId: UUID())
        do { try store.save(String(decoding: JSONEncoder().encode(pending), as: UTF8.self)) }
        catch { throw SdkFailure("INTERNAL_ERROR") }
        return pending.attemptId
    }
    func finish(account: UUID, key: String, attempt: UUID) throws {
        guard let pending = try load(), pending.accountId == account, pending.transactionKey == key, pending.attemptId == attempt else { throw SdkFailure("INTERNAL_ERROR") }
        do { try store.clear() } catch { throw SdkFailure("INTERNAL_ERROR") }
    }
    func reconcile(account: UUID, unfinished: Set<String>, completed: Set<String>) throws {
        guard let pending = try load() else { return }
        guard pending.accountId == account else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
        if !unfinished.contains(pending.transactionKey) && completed.contains(pending.transactionKey) {
            do { try store.clear() } catch { throw SdkFailure("INTERNAL_ERROR") }
        }
    }
    func ensureEmpty(account: UUID) throws {
        if let pending = try load() {
            guard pending.accountId == account else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
            throw SdkFailure("BUSY", retryable: true)
        }
    }
    private func load() throws -> XcodePendingAttempt? {
        let raw: String?
        do { raw = try store.load() } catch { throw SdkFailure("INTERNAL_ERROR") }
        guard let raw else { return nil }
        guard let pending = try? JSONDecoder().decode(XcodePendingAttempt.self, from: Data(raw.utf8)),
              pending.transactionKey.range(of: "^[0-9a-f]{64}$", options: .regularExpression) != nil else { throw SdkFailure("INTERNAL_ERROR") }
        return pending
    }
}
