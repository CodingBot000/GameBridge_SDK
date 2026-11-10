import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

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
    let appId, providerMode, backendBaseURL: String
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
    func refresh(session: AppleSession) async throws -> AppleSession
    func revoke(session: AppleSession) async throws
}

/// Apple token and Apple user identifier stay in Native memory/Keychain, not Unity results.
@MainActor public final class AppleAuthProvider {
    let gateway: AppleCredentialGateway
    private let backend: AppleAuthBackend
    private let config: GameBridgeConfig
    private let store: TokenStore
    private var busy = false
    private var generation = 0
    private var currentSession: AppleSession?
    private var refreshFlight: (id: UUID, task: Task<AppleSession, Error>)?
    init(config: GameBridgeConfig, store: TokenStore, gateway: AppleCredentialGateway, backend: AppleAuthBackend) {
        self.config = config; self.store = store; self.gateway = gateway; self.backend = backend
    }
    public func signIn() async throws -> UserProfile {
        guard config.mode == .platformSandbox else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard !busy else { throw SdkFailure("BUSY") }
        busy = true; defer { busy = false }
        generation += 1; let started = generation
        if refreshFlight != nil { currentSession = nil }
        refreshFlight?.task.cancel(); refreshFlight = nil
        let challenge = try await backend.challenge(appId: config.appId)
        guard UUID(uuidString: challenge.challengeId) != nil, !challenge.nonce.isEmpty,
              isUTCInstant(challenge.expiresAt) else { throw SdkFailure("AUTH_FAILED") }
        // Apple receives the raw server nonce; Backend must compare the signed claim to the same value.
        let credential = try await gateway.authorize(nonce: challenge.nonce)
        guard !credential.identityToken.isEmpty, !credential.userIdentifier.isEmpty else { throw SdkFailure("AUTH_FAILED") }
        let session = try await backend.exchange(challengeId: challenge.challengeId, credential: credential)
        guard UUID(uuidString: session.userId) != nil, !session.accessToken.isEmpty, !session.refreshToken.isEmpty,
              session.appleUserIdentifier == credential.userIdentifier, session.appId == config.appId,
              session.providerMode == config.mode.rawValue, session.backendBaseURL == config.backendBaseURL, isUTCInstant(session.expiresAt) else { throw SdkFailure("AUTH_FAILED") }
        let profile = try await backend.profile(session: session)
        guard profile.userId == session.userId, profile.provider == "APPLE" else { throw SdkFailure("AUTH_FAILED") }
        guard generation == started else { throw SdkFailure("CANCELED") }
        try store.save(String(decoding: JSONEncoder().encode(session), as: UTF8.self))
        currentSession = session
        return profile
    }
    private func isUTCInstant(_ value: String) -> Bool {
        guard value.hasSuffix("Z") else { return false }
        let fractional = ISO8601DateFormatter(); fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return fractional.date(from: value) != nil || ISO8601DateFormatter().date(from: value) != nil
    }
    public func restore() async throws -> UserProfile? {
        guard !busy else { throw SdkFailure("BUSY") }
        guard let current = try loadBound() else { return nil }
        let started = generation
        do {
            let profile = try await backend.profile(session: current)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return try validateProfile(profile, session: current)
        } catch let error as SdkFailure where error.code == "SESSION_EXPIRED" {
            guard generation == started else { throw SdkFailure("CANCELED") }
            if let latest = currentSession, latest.accessToken != current.accessToken {
                let profile = try await backend.profile(session: latest)
                guard generation == started else { throw SdkFailure("CANCELED") }
                return try validateProfile(profile, session: latest)
            }
            let flight: (id: UUID, task: Task<AppleSession, Error>)
            if let existing = refreshFlight { flight = existing }
            else {
                try store.save("{\"state\":\"refresh_pending\"}")
                let backend = self.backend
                let task = Task { try await backend.refresh(session: current) }
                flight = (UUID(), task); refreshFlight = flight
            }
            let refreshed: AppleSession
            do { refreshed = try await flight.task.value }
            catch {
                if generation == started && refreshFlight?.id == flight.id { refreshFlight = nil; currentSession = nil }
                if error is CancellationError { throw SdkFailure("CANCELED") }
                throw error
            }
            guard generation == started else { throw SdkFailure("CANCELED") }
            guard refreshed.userId == current.userId, refreshed.appleUserIdentifier == current.appleUserIdentifier,
                  matchesConfig(refreshed), !refreshed.accessToken.isEmpty, !refreshed.refreshToken.isEmpty,
                  isUTCInstant(refreshed.expiresAt) else {
                if refreshFlight?.id == flight.id { currentSession = nil; refreshFlight = nil }
                throw SdkFailure("AUTH_FAILED")
            }
            if refreshFlight?.id == flight.id {
                do { try store.save(String(decoding: JSONEncoder().encode(refreshed), as: UTF8.self)) }
                catch { currentSession = nil; refreshFlight = nil; throw SdkFailure("INTERNAL_ERROR") }
                currentSession = refreshed; refreshFlight = nil
            }
            guard let usable = currentSession else { throw SdkFailure("SESSION_EXPIRED") }
            let profile = try await backend.profile(session: usable)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return try validateProfile(profile, session: usable)
        }
    }
    internal var sessionGeneration: Int { generation }
    internal func withAuthenticatedSession<T>(_ action: (AppleSession) async throws -> T) async throws -> T? {
        guard let profile = try await restore(), let session = try loadBound(), profile.userId == session.userId else { return nil }
        let started = generation
        let result = try await action(session)
        guard generation == started, currentSession?.userId == session.userId else { throw SdkFailure("CANCELED") }
        return result
    }
    public func signOut() async throws {
        let raw = try store.load()
        let pending = raw == "{\"state\":\"refresh_pending\"}"
        let stored = pending ? nil : try loadStoredBound()
        let old = currentSession ?? stored
        generation += 1; refreshFlight?.task.cancel(); refreshFlight = nil; currentSession = nil
        try store.clear()
        if let old {
            do { try await backend.revoke(session: old) }
            catch let error as SdkFailure { throw SdkFailure(error.code, nativeCode: "REVOCATION_UNCONFIRMED", retryable: error.retryable) }
            catch { throw SdkFailure("INTERNAL_ERROR", nativeCode: "REVOCATION_UNCONFIRMED") }
        } else if pending { throw SdkFailure("SESSION_EXPIRED", nativeCode: "REVOCATION_UNCONFIRMED") }
    }
    public func checkCredentialState() async throws -> AppleCredentialState {
        guard !busy && refreshFlight == nil else { throw SdkFailure("BUSY") }
        busy = true; defer { busy = false }
        guard let session = try loadBound() else { return .notFound }
        let started = generation
        let result = try await gateway.credentialState(userIdentifier: session.appleUserIdentifier)
        guard generation == started else { throw SdkFailure("CANCELED") }
        if result == .revoked || result == .notFound {
            guard let persisted = try loadStoredBound(), persisted.userId == session.userId else { throw SdkFailure("SESSION_EXPIRED") }
            generation += 1; currentSession = nil
            try store.clear() // Local logout takes precedence even when server revoke fails.
            do { try await backend.revoke(session: session) }
            catch let error as SdkFailure { throw SdkFailure(error.code, nativeCode: "REVOCATION_UNCONFIRMED", retryable: error.retryable) }
            catch { throw SdkFailure("INTERNAL_ERROR", nativeCode: "REVOCATION_UNCONFIRMED") }
        }
        return result
    }
    private func loadBound() throws -> AppleSession? {
        if let currentSession { return currentSession }
        guard let loaded = try loadStoredBound() else { return nil }
        currentSession = loaded; return loaded
    }
    private func loadStoredBound() throws -> AppleSession? {
        guard let saved = try store.load() else { return nil }
        let loaded: AppleSession
        do { loaded = try JSONDecoder().decode(AppleSession.self, from: Data(saved.utf8)) }
        catch { throw SdkFailure("SESSION_EXPIRED") }
        guard matchesConfig(loaded), !loaded.accessToken.isEmpty, !loaded.refreshToken.isEmpty,
              UUID(uuidString: loaded.userId) != nil, isUTCInstant(loaded.expiresAt) else { throw SdkFailure("SESSION_EXPIRED") }
        return loaded
    }
    private func matchesConfig(_ session: AppleSession) -> Bool {
        session.appId == config.appId && session.providerMode == config.mode.rawValue && session.backendBaseURL == config.backendBaseURL
    }
    private func validateProfile(_ profile: UserProfile, session: AppleSession) throws -> UserProfile {
        guard profile.userId == session.userId, profile.provider == "APPLE" else { throw SdkFailure("AUTH_FAILED") }
        return profile
    }

}

struct HttpAppleBackend: AppleAuthBackend {
    private let client: BackendClient
    private let config: GameBridgeConfig
    init(config: GameBridgeConfig, sessionConfiguration: URLSessionConfiguration = .default) throws {
        self.config = config; client = try BackendClient(config: config, sessionConfiguration: sessionConfiguration)
    }
    func challenge(appId: String) async throws -> AppleChallenge {
        try decode(try await client.request(path: "/v1/auth/challenges", method: "POST", body: encode(["provider": "APPLE", "appId": appId])).json)
    }
    func exchange(challengeId: String, credential: AppleCredential) async throws -> AppleSession {
        var body: [String: Any] = ["challengeId": challengeId, "provider": "APPLE", "idToken": credential.identityToken]
        if let displayName = credential.displayName { body["displayName"] = displayName }
        let value: ExchangeSession = try decode(try await client.request(path: "/v1/auth/exchange", method: "POST", body: encode(body)).json)
        return AppleSession(accessToken: value.accessToken, refreshToken: value.refreshToken, expiresAt: value.expiresAt, userId: value.userId, appleUserIdentifier: credential.userIdentifier,
                            appId: config.appId, providerMode: config.mode.rawValue, backendBaseURL: config.backendBaseURL!)
    }
    func profile(session: AppleSession) async throws -> UserProfile {
        let me: AppleMe = try decode(try await client.request(path: "/v1/me", method: "GET", accessToken: session.accessToken).json)
        return UserProfile(userId: me.userId, displayName: me.displayName, provider: "APPLE")
    }
    func refresh(session: AppleSession) async throws -> AppleSession {
        let value: ExchangeSession = try decode(try await client.request(path: "/v1/auth/refresh", method: "POST", body: encode(["refreshToken": session.refreshToken])).json)
        return AppleSession(accessToken: value.accessToken, refreshToken: value.refreshToken, expiresAt: value.expiresAt, userId: value.userId,
                            appleUserIdentifier: session.appleUserIdentifier, appId: session.appId, providerMode: session.providerMode, backendBaseURL: session.backendBaseURL)
    }
    func revoke(session: AppleSession) async throws {
        do { _ = try await client.request(path: "/v1/auth/logout", method: "POST", accessToken: session.accessToken) }
        catch let error as SdkFailure where error.code == "SESSION_EXPIRED" {
            _ = try await client.request(path: "/v1/auth/logout", method: "POST", body: encode(["refreshToken": session.refreshToken]))
        }
    }
    private func encode(_ value: [String: Any]) throws -> Data { try JSONSerialization.data(withJSONObject: value) }
    private func decode<T: Decodable>(_ data: Data) throws -> T {
        do { return try JSONDecoder().decode(T.self, from: data) } catch { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    }
}
