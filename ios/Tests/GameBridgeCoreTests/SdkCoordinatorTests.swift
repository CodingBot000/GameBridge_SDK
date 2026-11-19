import XCTest
@testable import GameBridgeCore

private actor ControlledProvider: SdkProvider {
    private(set) var starts = 0
    private var continuation: CheckedContinuation<Void, Never>?
    func initialize(_ config: GameBridgeConfig) async throws -> InitSnapshot {
        starts += 1
        await withCheckedContinuation { continuation = $0 }
        return InitSnapshot(capabilities: [:])
    }
    func shutdown() async throws {}
    func waitForStart() async { while continuation == nil { await Task.yield() } }
    func release() { continuation?.resume(); continuation = nil }
}
private actor CancellableProvider: SdkProvider {
    private var started = false
    func initialize(_ config: GameBridgeConfig) async throws -> InitSnapshot {
        started = true
        try await Task.sleep(nanoseconds: 60_000_000_000)
        return InitSnapshot(capabilities: [:])
    }
    func shutdown() async throws {}
    func waitForStart() async { while !started { await Task.yield() } }
}
private actor InteractiveGate {
    private var continuation: CheckedContinuation<Void, Never>?
    func hold() async { await withCheckedContinuation { continuation = $0 } }
    func waitUntilHeld() async { while continuation == nil { await Task.yield() } }
    func release() { continuation?.resume(); continuation = nil }
}
final class SdkCoordinatorTests: MeasuredTestCase {
    func testRequireReadyBeforeInitializationFails() async throws {
        let sdk = SdkCoordinator(provider: ControlledProvider())
        do { try await sdk.requireReady(); GBFail("uninitialized API") }
        catch let error as SdkFailure { GBAssertEqual(error.code, "NOT_INITIALIZED") }
    }
    func testShutdownDuringInitialization() async throws {
        let provider = CancellableProvider(); let sdk = SdkCoordinator(provider: provider)
        let pending = Task { try await sdk.initialize(GameBridgeConfig(appId: "demo", mode: .editorOffline, backendBaseURL: nil)) }
        await provider.waitForStart(); try await sdk.shutdown()
        do { _ = try await pending.value; GBFail("initialization should not succeed") } catch {}
        let state = await sdk.status(); GBAssertEqual(state, .shutdown)
    }
    func testInteractiveCallsAreMutuallyExclusive() async throws {
        let provider = ControlledProvider(); let sdk = SdkCoordinator(provider: provider)
        let config = GameBridgeConfig(appId: "demo", mode: .editorOffline, backendBaseURL: nil)
        let initializing = Task { try await sdk.initialize(config) }
        await provider.waitForStart(); await provider.release(); _ = try await initializing.value
        let gate = InteractiveGate()
        let held = Task { try await sdk.withInteractiveUI { await gate.hold() } }
        await gate.waitUntilHeld()
        do { try await sdk.withInteractiveUI {}; GBFail("concurrent UI accepted") }
        catch let error as SdkFailure { GBAssertEqual(error.code, "BUSY") }
        await gate.release(); try await held.value; try await sdk.shutdown()
    }
    func testConcurrentInitializeAndShutdown() async throws {
        let provider = ControlledProvider(); let sdk = SdkCoordinator(provider: provider)
        let config = GameBridgeConfig(appId: "demo", mode: .editorOffline, backendBaseURL: nil)
        let first = Task { try await sdk.initialize(config) }
        await provider.waitForStart()
        let second = Task { try await sdk.initialize(config) }
        do {
            _ = try await sdk.initialize(GameBridgeConfig(appId: "other", mode: .editorOffline, backendBaseURL: nil))
            GBFail("different configuration should fail")
        } catch let error as SdkFailure { GBAssertEqual(error.code, "ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        await provider.release()
        _ = try await first.value; _ = try await second.value
        let starts = await provider.starts; GBAssertEqual(starts, 1)
        let ready = await sdk.status(); GBAssertEqual(ready, .ready)
        try await sdk.shutdown(); try await sdk.shutdown()
        let stopped = await sdk.status(); GBAssertEqual(stopped, .shutdown)
        let restarted = Task { try await sdk.initialize(config) }
        await provider.waitForStart(); await provider.release()
        _ = try await restarted.value
        let restartedStarts = await provider.starts; GBAssertEqual(restartedStarts, 2)
        let restartedState = await sdk.status(); GBAssertEqual(restartedState, .ready)
        try await sdk.shutdown()
    }
}
