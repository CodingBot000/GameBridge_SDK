import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

// Only the Native store/push layer receives this account context. It never enters Unity payloads.
struct BackendAccountSession { let accessToken: String; let userId: String }
@MainActor protocol BackendSessionAccess: AnyObject {
    var uiGate: AppleUiGate { get }
    var sessionGeneration: Int { get }
    func usesConfiguration(_ config: GameBridgeConfig) -> Bool
    func withBackendSession<T>(_ action: (BackendAccountSession) async throws -> T) async throws -> T?
}
extension AppleAuthProvider: BackendSessionAccess {
    func withBackendSession<T>(_ action: (BackendAccountSession) async throws -> T) async throws -> T? {
        try await withAuthenticatedSession { try await action(BackendAccountSession(accessToken: $0.accessToken, userId: $0.userId)) }
    }
}
