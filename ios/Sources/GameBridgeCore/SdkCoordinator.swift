import Foundation

public enum SdkState: String { case uninitialized, initializing, ready, shuttingDown, shutdown }
public struct Capability: Equatable {
    public let supported: Bool
    public let configured: Bool
    public let mode: ProviderMode
    public let reason: String?
    public init(supported: Bool, configured: Bool, mode: ProviderMode, reason: String?) {
        self.supported = supported; self.configured = configured; self.mode = mode; self.reason = reason
    }
}
public struct InitSnapshot: Equatable {
    public let capabilities: [String: Capability]
    public init(capabilities: [String: Capability]) { self.capabilities = capabilities }
}
public struct SdkFailure: Error, Equatable {
    public let code: String
    public let nativeCode: String?
    public let retryable: Bool
    public init(_ code: String, nativeCode: String? = nil, retryable: Bool = false) { self.code = code; self.nativeCode = nativeCode; self.retryable = retryable }
}
public protocol SdkProvider {
    func initialize(_ config: GameBridgeConfig) async throws -> InitSnapshot
    func shutdown() async throws
}
public actor SdkCoordinator {
    private let provider: SdkProvider
    private var state: SdkState = .uninitialized
    private var config: GameBridgeConfig?
    private var initialization: Task<InitSnapshot, Error>?
    private var shuttingDown: Task<Void, Error>?
    private var generation = 0
    private var uiBusy = false

    public init(provider: SdkProvider) { self.provider = provider }
    public func status() -> SdkState { state }
    public func initialize(_ value: GameBridgeConfig) async throws -> InitSnapshot {
        try value.validate()
        if state == .shuttingDown { throw SdkFailure("BUSY") }
        let task: Task<InitSnapshot, Error>
        if state == .ready || state == .initializing {
            guard config == value, let current = initialization else { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
            task = current
        } else {
            config = value; state = .initializing; generation += 1
            let provider = self.provider
            task = Task { try await provider.initialize(value) }
            initialization = task
        }
        let thisGeneration = generation
        do {
            let result = try await task.value
            guard generation == thisGeneration, state == .initializing || state == .ready else { throw SdkFailure("NOT_INITIALIZED") }
            state = .ready
            return result
        } catch {
            if generation == thisGeneration && state == .initializing {
                state = .uninitialized; config = nil; initialization = nil
            }
            throw error
        }
    }
    public func requireReady() throws { if state != .ready { throw SdkFailure("NOT_INITIALIZED") } }
    public func withInteractiveUI<T>(_ action: () async throws -> T) async throws -> T {
        try requireReady()
        guard !uiBusy else { throw SdkFailure("BUSY") }
        uiBusy = true
        defer { uiBusy = false }
        return try await action()
    }
    public func shutdown() async throws {
        if state == .shuttingDown, let current = shuttingDown { return try await current.value }
        if state == .uninitialized || state == .shutdown { state = .shutdown; return }
        state = .shuttingDown; generation += 1
        let initial = initialization
        initial?.cancel()
        let provider = self.provider
        let task = Task {
            if let initial { _ = await initial.result }
            try await provider.shutdown()
        }
        shuttingDown = task
        do {
            try await task.value
            state = .shutdown; config = nil; initialization = nil; shuttingDown = nil
        } catch {
            state = .shutdown; config = nil; initialization = nil; shuttingDown = nil
            throw error
        }
    }
}
