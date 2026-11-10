import Foundation

private struct SecretSession: Codable {
    let accessToken, refreshToken, expiresAt, userId: String
}
private struct Me: Codable { let userId: String }
public struct LocalWallet: Codable {
    public let userId: String
    public let premiumEnabled: Bool
    public let coinBalance, revision, updatedAt: String
}
public struct LocalProduct: Codable, Identifiable {
    public let productId, storeProductId, type: String
    public var id: String { productId }
}
public struct LocalPurchase: Codable {
    public let serverPurchaseId, fulfillmentStatus, finalizationStatus: String
    public let entitlements: LocalWallet
}
/// Native-owned tokens; this client only connects to the explicitly configured local mock backend.
public actor LocalMockClient {
    private let backend: BackendClient
    private let store: TokenStore
    private let developmentKey: String
    private var session: SecretSession?
    private var refreshTask: Task<SecretSession, Error>?
    private var generation = 0
    public init(config: GameBridgeConfig, store: TokenStore, developmentKey: String) throws {
        guard config.mode == .localMock else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard developmentKey.count >= 32 else { throw SdkFailure("CONFIG_REQUIRED") }
        backend = try BackendClient(config: config); self.store = store; self.developmentKey = developmentKey
    }
    public func signIn(subject: String) async throws -> UserProfile {
        guard ["A", "B"].contains(subject) else { throw SdkFailure("INVALID_ARGUMENT") }
        generation += 1; refreshTask?.cancel(); refreshTask = nil; let started = generation
        let response = try await backend.request(path: "/v1/dev/auth", method: "POST", body: encode(["subject": subject]), developmentKey: developmentKey)
        let next: SecretSession = try decode(response.json)
        guard generation == started else { throw SdkFailure("CANCELED") }
        try store.save(String(decoding: JSONEncoder().encode(next), as: UTF8.self)); session = next
        return UserProfile(userId: next.userId, displayName: nil, provider: "MOCK")
    }
    public func restore() async throws -> UserProfile? {
        guard let saved = try store.load() else { return nil }
        let loaded: SecretSession
        do { loaded = try decode(Data(saved.utf8)) } catch { try store.clear(); session = nil; throw SdkFailure("SESSION_EXPIRED") }
        generation += 1; refreshTask?.cancel(); refreshTask = nil; let started = generation; session = loaded
        let me: Me = try decode(try await authenticated(path: "/v1/me", method: "GET").json)
        guard generation == started, me.userId == session?.userId else { throw SdkFailure("AUTH_FAILED") }
        return UserProfile(userId: me.userId, displayName: nil, provider: "MOCK")
    }
    public func products() async throws -> [LocalProduct] { try decode(try await authenticated(path: "/v1/catalog", method: "GET").json) }
    public func wallet() async throws -> LocalWallet { try decode(try await authenticated(path: "/v1/entitlements", method: "GET").json) }
    public func purchase(productId: String, transactionId: UUID, attemptId: UUID) async throws -> LocalPurchase {
        guard ["coins_100", "premium_unlock"].contains(productId) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        guard let user = session?.userId else { throw SdkFailure("SESSION_EXPIRED") }
        let proof = "mock:\(user):\(productId):\(transactionId.uuidString.lowercased())"
        let body = try encode(["productId": productId, "proof": proof, "quantity": 1])
        return try decode(try await authenticated(path: "/v1/purchases/verify", method: "POST", body: body, idempotencyKey: attemptId.uuidString.lowercased()).json)
    }
    public func signOut() async throws {
        generation += 1; let current = session; session = nil; refreshTask?.cancel(); refreshTask = nil; try store.clear()
        if let current { _ = try await backend.request(path: "/v1/auth/logout", method: "POST", accessToken: current.accessToken) }
    }
    private func authenticated(path: String, method: String, body: Data? = nil, idempotencyKey: String? = nil) async throws -> BackendResponse {
        guard let current = session else { throw SdkFailure("SESSION_EXPIRED") }
        let started = generation
        do {
            let response = try await backend.request(path: path, method: method, body: body, accessToken: current.accessToken, idempotencyKey: idempotencyKey)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return response
        } catch let error as SdkFailure where error.code == "SESSION_EXPIRED" {
            guard generation == started else { throw SdkFailure("CANCELED") }
            if let latest = session, latest.accessToken != current.accessToken {
                let response = try await backend.request(path: path, method: method, body: body, accessToken: latest.accessToken, idempotencyKey: idempotencyKey)
                guard generation == started else { throw SdkFailure("CANCELED") }
                return response
            }
            let task: Task<SecretSession, Error>
            if let existing = refreshTask { task = existing }
            else {
                let backend = self.backend
                task = Task {
                    let body = try JSONSerialization.data(withJSONObject: ["refreshToken": current.refreshToken])
                    let response = try await backend.request(path: "/v1/auth/refresh", method: "POST", body: body)
                    return try JSONDecoder().decode(SecretSession.self, from: response.json)
                }
                refreshTask = task
            }
            let refreshed: SecretSession
            do { refreshed = try await task.value }
            catch {
                if generation == started { refreshTask = nil; if (error as? SdkFailure)?.code == "SESSION_EXPIRED" { session = nil; try store.clear() } }
                throw error
            }
            guard generation == started, refreshed.userId == current.userId else { throw SdkFailure("AUTH_FAILED") }
            try store.save(String(decoding: JSONEncoder().encode(refreshed), as: UTF8.self)); session = refreshed; refreshTask = nil
            let response = try await backend.request(path: path, method: method, body: body, accessToken: refreshed.accessToken, idempotencyKey: idempotencyKey)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return response
        }
    }
    private func encode(_ value: [String: Any]) throws -> Data { try JSONSerialization.data(withJSONObject: value) }
    private func decode<T: Decodable>(_ data: Data) throws -> T {
        do { return try JSONDecoder().decode(T.self, from: data) } catch { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    }
}
