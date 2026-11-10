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
