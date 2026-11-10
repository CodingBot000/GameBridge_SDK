import Foundation
import GameBridgeCore

public enum AppleCredentialState { case authorized, revoked, notFound, transferred, unknown }
struct AppleCredential: CustomStringConvertible {
    let identityToken: String
    let userIdentifier: String
    let displayName: String?
    var description: String { "AppleCredential([redacted])" }
}
struct AppleChallenge: Decodable, CustomStringConvertible {
    let challengeId, nonce, expiresAt: String
    var description: String { "AppleChallenge([redacted])" }
}
private struct AppleMe: Decodable { let userId: String; let displayName: String? }
struct AppleSession: Codable, CustomStringConvertible {
    let accessToken, refreshToken, expiresAt, userId, appleUserIdentifier: String
    var description: String { "AppleSession([redacted])" }
}
private struct ExchangeSession: Decodable, CustomStringConvertible {
    let accessToken, refreshToken, expiresAt, userId: String
    var description: String { "ExchangeSession([redacted])" }
}

@MainActor protocol AppleCredentialGateway {
    func authorize(nonce: String) async throws -> AppleCredential
    func credentialState(userIdentifier: String) async throws -> AppleCredentialState
}
protocol AppleAuthBackend {
    func challenge(appId: String) async throws -> AppleChallenge
    func exchange(challengeId: String, credential: AppleCredential) async throws -> AppleSession
    func profile(session: AppleSession) async throws -> UserProfile
    func revoke(session: AppleSession) async throws
}

/// Apple token and Apple user identifier stay in Native memory/Keychain, not Unity results.
@MainActor public final class AppleAuthProvider {
    let gateway: AppleCredentialGateway
    private let backend: AppleAuthBackend
    private let config: GameBridgeConfig
    private let store: TokenStore
    private var busy = false
    init(config: GameBridgeConfig, store: TokenStore, gateway: AppleCredentialGateway, backend: AppleAuthBackend) {
        self.config = config; self.store = store; self.gateway = gateway; self.backend = backend
    }
    public func signIn() async throws -> UserProfile {
        guard config.mode == .platformSandbox else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard !busy else { throw SdkFailure("BUSY") }
        busy = true; defer { busy = false }
        let challenge = try await backend.challenge(appId: config.appId)
        guard UUID(uuidString: challenge.challengeId) != nil, !challenge.nonce.isEmpty,
              isUTCInstant(challenge.expiresAt) else { throw SdkFailure("AUTH_FAILED") }
        // Apple receives the raw server nonce; Backend must compare the signed claim to the same value.
        let credential = try await gateway.authorize(nonce: challenge.nonce)
        guard !credential.identityToken.isEmpty, !credential.userIdentifier.isEmpty else { throw SdkFailure("AUTH_FAILED") }
        let session = try await backend.exchange(challengeId: challenge.challengeId, credential: credential)
        guard UUID(uuidString: session.userId) != nil, !session.accessToken.isEmpty, !session.refreshToken.isEmpty,
              session.appleUserIdentifier == credential.userIdentifier, isUTCInstant(session.expiresAt) else { throw SdkFailure("AUTH_FAILED") }
        let profile = try await backend.profile(session: session)
        guard profile.userId == session.userId, profile.provider == "APPLE" else { throw SdkFailure("AUTH_FAILED") }
        try store.save(String(decoding: JSONEncoder().encode(session), as: UTF8.self))
        return profile
    }
    private func isUTCInstant(_ value: String) -> Bool {
        guard value.hasSuffix("Z") else { return false }
        let fractional = ISO8601DateFormatter(); fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return fractional.date(from: value) != nil || ISO8601DateFormatter().date(from: value) != nil
    }
    public func checkCredentialState() async throws -> AppleCredentialState {
        guard !busy else { throw SdkFailure("BUSY") }
        busy = true; defer { busy = false }
        guard let saved = try store.load() else { return .notFound }
        let session: AppleSession
        do { session = try JSONDecoder().decode(AppleSession.self, from: Data(saved.utf8)) }
        catch { throw SdkFailure("SESSION_EXPIRED") }
        let result = try await gateway.credentialState(userIdentifier: session.appleUserIdentifier)
        if result == .revoked || result == .notFound {
            try store.clear() // Local logout takes precedence even when server revoke fails.
            try await backend.revoke(session: session)
        }
        return result
    }
}

struct HttpAppleBackend: AppleAuthBackend {
    private let client: BackendClient
    init(config: GameBridgeConfig) throws { client = try BackendClient(config: config) }
    func challenge(appId: String) async throws -> AppleChallenge {
        try decode(try await client.request(path: "/v1/auth/challenges", method: "POST", body: encode(["provider": "APPLE", "appId": appId])).json)
    }
    func exchange(challengeId: String, credential: AppleCredential) async throws -> AppleSession {
        var body: [String: Any] = ["challengeId": challengeId, "provider": "APPLE", "idToken": credential.identityToken]
        if let displayName = credential.displayName { body["displayName"] = displayName }
        let value: ExchangeSession = try decode(try await client.request(path: "/v1/auth/exchange", method: "POST", body: encode(body)).json)
        return AppleSession(accessToken: value.accessToken, refreshToken: value.refreshToken, expiresAt: value.expiresAt, userId: value.userId, appleUserIdentifier: credential.userIdentifier)
    }
    func profile(session: AppleSession) async throws -> UserProfile {
        let me: AppleMe = try decode(try await client.request(path: "/v1/me", method: "GET", accessToken: session.accessToken).json)
        return UserProfile(userId: me.userId, displayName: me.displayName, provider: "APPLE")
    }
    func revoke(session: AppleSession) async throws { _ = try await client.request(path: "/v1/auth/logout", method: "POST", accessToken: session.accessToken) }
    private func encode(_ value: [String: Any]) throws -> Data { try JSONSerialization.data(withJSONObject: value) }
    private func decode<T: Decodable>(_ data: Data) throws -> T {
        do { return try JSONDecoder().decode(T.self, from: data) } catch { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    }
}
