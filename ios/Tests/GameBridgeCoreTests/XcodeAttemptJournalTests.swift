import Foundation
import XCTest
@testable import GameBridgeCore
@testable import GameBridgeApple

private final class XcodeJournalStore: TokenStore {
    var value: String?
    func load() throws -> String? { value }
    func save(_ value: String) throws { self.value = value }
    func clear() throws { value = nil }
}
final class XcodeAttemptJournalTests: XCTestCase {
    func testRestartReuseIsolationAndFinishDeletion() async throws {
        let store = XcodeJournalStore(); let user = UUID(); let key = String(repeating:"a", count:64)
        let first = XcodeAttemptJournal(store: store); let id = try await first.begin(account:user, key:key)
        XCTAssertFalse(store.value!.contains("signed"))
        let restarted = XcodeAttemptJournal(store: store); let again = try await restarted.begin(account:user, key:key)
        XCTAssertEqual(id, again)
        do { _ = try await restarted.begin(account:UUID(), key:key); XCTFail("foreign account") } catch let error as SdkFailure { XCTAssertEqual(error.code, "PURCHASE_ACCOUNT_MISMATCH") }
        do { _ = try await restarted.begin(account:user, key:String(repeating:"b", count:64)); XCTFail("other pending") } catch let error as SdkFailure { XCTAssertEqual(error.code, "BUSY") }
        try await restarted.reconcile(account:user, unfinished:[key], completed:[]); XCTAssertNotNil(store.value)
        try await restarted.finish(account:user, key:key, attempt:id); XCTAssertNil(store.value)
        try await restarted.ensureEmpty(account:user)
    }
    func testMissingAfterFinishAndCorruptRecordFailClosed() async throws {
        let store = XcodeJournalStore(); let user = UUID(); let key = String(repeating:"c", count:64); let journal = XcodeAttemptJournal(store:store)
        _ = try await journal.begin(account:user, key:key)
        try await journal.reconcile(account:user, unfinished:[], completed:[]); XCTAssertNotNil(store.value)
        try await journal.reconcile(account:user, unfinished:[], completed:[key]); XCTAssertNil(store.value)
        store.value = "invalid"
        do { _ = try await journal.begin(account:user, key:key); XCTFail("corrupt journal") } catch let error as SdkFailure { XCTAssertEqual(error.code, "INTERNAL_ERROR") }
    }
}
