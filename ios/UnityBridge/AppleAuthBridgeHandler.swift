import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
import GameBridgeApple
#endif
#if canImport(UIKit) && canImport(AuthenticationServices)
import UIKit
import AuthenticationServices
#endif

@MainActor protocol AppleAuthBridgeApi {
    func signIn() async throws -> UserProfile
    func restore() async throws -> UserProfile?
    func signOut() async throws
    func close()
}

@MainActor final class AppleAuthBridgeHandler {
    private let factory: (GameBridgeConfig) throws -> AppleAuthBridgeApi
    private var provider: AppleAuthBridgeApi?
    private var config: GameBridgeConfig?
    init(factory: @escaping (GameBridgeConfig) throws -> AppleAuthBridgeApi) { self.factory = factory }
    func invoke(_ operation: String, payload: [String: Any]) async throws -> Any {
        if operation == "sdk.initialize" { return try initialize(payload) }
        if operation == "sdk.shutdown" { provider?.close(); provider = nil; config = nil; return [String: Any]() }
        guard let provider else { throw SdkFailure("NOT_INITIALIZED") }
        switch operation {
        case "auth.signIn":
            guard payload["provider"] as? String == "APPLE" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
            return try object(try await provider.signIn())
        case "auth.restore":
            let user = try await provider.restore()
            return ["signedIn": user != nil, "user": try user.map { try object($0) } ?? NSNull(),
                    "expiresAt": NSNull(), "sessionRestored": user != nil] as [String: Any]
        case "auth.signOut": try await provider.signOut(); return [String: Any]()
        default: throw SdkFailure("UNSUPPORTED_OPERATION")
        }
    }
    private func initialize(_ payload: [String: Any]) throws -> [String: Any] {
        guard payload["providerMode"] as? String == "PLATFORM_SANDBOX", payload["developmentKey"] == nil else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard let appId = payload["appId"] as? String, let base = payload["backendBaseUrl"] as? String,
              let timeout = payload["requestTimeoutMs"] as? Int else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = GameBridgeConfig(appId: appId, mode: .platformSandbox, backendBaseURL: base, requestTimeoutMs: timeout)
        do { try next.validate() } catch { throw SdkFailure("CONFIG_REQUIRED") }
        if provider != nil && config != next { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        if provider == nil { provider = try factory(next); config = next }
        var capabilities: [String: Any] = [:]
        for name in ["auth", "store", "push", "config"] {
            let available = name == "auth"
            capabilities[name] = ["supported": available, "configured": available, "mode": "PLATFORM_SANDBOX",
                                  "reason": available ? NSNull() as Any : "Bridge operation is not connected"]
        }
        return ["state": "READY", "mode": "PLATFORM_SANDBOX", "provider": "APPLE", "capabilities": capabilities]
    }
    private func object<T: Encodable>(_ value: T) throws -> Any { try JSONSerialization.jsonObject(with: JSONEncoder().encode(value)) }
}

#if canImport(UIKit) && canImport(AuthenticationServices)
@MainActor private final class AppleSystemAuthBridgeApi: AppleAuthBridgeApi {
    let provider: AppleAuthProvider
    init(config: GameBridgeConfig) throws {
        guard let window = Self.window() else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "HOST_WINDOW") }
        provider = try AppleAuthProvider.create(config: config, store: KeychainTokenStore(service: "com.gamebridge.sdk.unity.apple"), window: window)
    }
    private static func window() -> UIWindow? {
        UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
            .filter { $0.activationState == .foregroundActive }.flatMap(\.windows).first(where: \.isKeyWindow)
    }
    func signIn() async throws -> UserProfile {
        guard let window = Self.window() else { throw SdkFailure("CONFIG_REQUIRED", nativeCode: "HOST_WINDOW") }
        provider.attachHost(window); return try await provider.signIn()
    }
    func restore() async throws -> UserProfile? { try await provider.restore() }
    func signOut() async throws { try await provider.signOut() }
    func close() { provider.detachHost() }
}
@MainActor func makeAppleAuthBridgeHandler() -> AppleAuthBridgeHandler {
    AppleAuthBridgeHandler { try AppleSystemAuthBridgeApi(config: $0) }
}
#endif
