import XCTest
@testable import GameBridgeCore

final class ServiceConfigurationRepositoryTests: XCTestCase {
    func testConcurrentFetchesShareOneRequest() async throws {
        let gate = FetchGate()
        let repository = ServiceConfigurationRepository(fetch: { try await gate.fetch() })
        let first = Task { try await repository.current() }
        let second = Task { try await repository.current() }
        await gate.waitUntilStarted()
        await gate.release()
        let firstResult = try await first.value, secondResult = try await second.value
        XCTAssertNotNil(firstResult); XCTAssertNotNil(secondResult)
        let count = await gate.calls; XCTAssertEqual(count, 1)
    }
    func testOfflineCacheExpiresAndUnknownBlocksPurchase() async throws {
        var now = Date(timeIntervalSince1970: 1_000), available = true
        let repository = ServiceConfigurationRepository(fetch: {
            if !available { throw SdkFailure("NETWORK_UNAVAILABLE") }
            return ServiceSettings(revision: "test", maintenanceEnabled: false, message: nil, expiresAt: now.addingTimeInterval(300))
        }, now: { now })
        let remote = try await repository.current(); XCTAssertEqual(remote?.source, .remote)
        available = false; now = now.addingTimeInterval(299)
        let cached = try await repository.current(); XCTAssertEqual(cached?.source, .cache)
        now = now.addingTimeInterval(1)
        let expired = try await repository.current(); XCTAssertNil(expired)
        XCTAssertFalse(MaintenanceGate.permits(maintenanceEnabled: expired?.settings.maintenanceEnabled, operation: .startPurchase))
        XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: expired?.settings.maintenanceEnabled, operation: .recoverPurchase))
    }
}

private actor FetchGate {
    var calls = 0
    private var continuation: CheckedContinuation<Void, Never>?
    func fetch() async throws -> ServiceSettings {
        calls += 1
        await withCheckedContinuation { continuation = $0 }
        return ServiceSettings(revision: "test", maintenanceEnabled: false, message: nil, expiresAt: Date().addingTimeInterval(300))
    }
    func waitUntilStarted() async { while continuation == nil { await Task.yield() } }
    func release() { continuation?.resume(); continuation = nil }
}
