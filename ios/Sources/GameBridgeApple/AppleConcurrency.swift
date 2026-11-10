import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@MainActor
final class AppleUiGate {
    private var held = false
    func acquire() throws { guard !held else { throw SdkFailure("BUSY") }; held = true }
    func release() { held = false }
}

/// Bounded waiting queue; a released slot is handed directly to the oldest waiter.
@MainActor
final class AppleVerificationLimiter {
    private let limit: Int
    private var active = 0
    private var waiters: [CheckedContinuation<Void, Never>] = []
    init(limit: Int) { precondition(limit > 0); self.limit = limit }
    func withPermit<T>(_ action: () async throws -> T) async throws -> T {
        if active < limit { active += 1 }
        else {
            guard waiters.count < 100 else { throw SdkFailure("BUSY") }
            await withCheckedContinuation { waiters.append($0) }
        }
        defer { release() }
        if Task.isCancelled { throw SdkFailure("CANCELED") }
        return try await action()
    }
    private func release() {
        if waiters.isEmpty { active -= 1 } else { waiters.removeFirst().resume() }
    }
}

/// Shares only equivalent account/reason recovery; a caller never cancels another caller's work.
@MainActor
final class AppleRecoveryFlight {
    private var current: (id: UUID, account: ApplePurchaseAccount, userInitiated: Bool, task: Task<AppleRecoveryCounts, Error>)?
    func run(account: ApplePurchaseAccount, userInitiated: Bool, work: @escaping @MainActor () async throws -> AppleRecoveryCounts) async throws -> AppleRecoveryCounts {
        if Task.isCancelled { throw SdkFailure("CANCELED") }
        let flight: (id: UUID, account: ApplePurchaseAccount, userInitiated: Bool, task: Task<AppleRecoveryCounts, Error>)
        if let active = current {
            guard active.account == account else { throw SdkFailure("CANCELED") }
            guard active.userInitiated == userInitiated else { throw SdkFailure("BUSY") }
            flight = active
        } else {
            let task = Task { @MainActor in try await work() }
            flight = (UUID(), account, userInitiated, task); current = flight
        }
        do {
            let value = try await flight.task.value
            if current?.id == flight.id { current = nil }
            if Task.isCancelled { throw SdkFailure("CANCELED") }
            return value
        } catch {
            if current?.id == flight.id { current = nil }
            if error is CancellationError { throw SdkFailure("CANCELED") }
            throw error
        }
    }
    func cancel() { current?.task.cancel(); current = nil }
}
