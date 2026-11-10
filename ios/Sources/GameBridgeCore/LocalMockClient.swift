import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

private struct WireSession: Codable, CustomStringConvertible {
    let accessToken, refreshToken, expiresAt, userId: String
    var description: String { "WireSession([redacted])" }
}
private struct SecretSession: Codable, CustomStringConvertible {
    let accessToken, refreshToken, expiresAt, userId: String
    let appId, providerMode, backendBaseURL: String
    var description: String { "SecretSession([redacted])" }
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
public struct XcodeMockAccount: Decodable {
    public let userId: UUID
    public let bindingId: UUID
}
public struct XcodeMockGrant: Decodable {
    public let userId, bindingId: UUID
    public let productId, transactionKey: String
    public let serverPurchaseId: UUID
    public let fulfillmentStatus: String
}
public struct LocalPushRegistration {
    public let tokenFingerprint, updatedAt: String
}
private struct PendingMockPurchase: Codable, Equatable {
    let appId, backendBaseURL, userId, productId, transactionId, attemptId: String
}
public struct LocalRecoveryCounts {
    public let examinedCount, recoveredCount, deferredCount, failureCount: Int
}
/// Native-owned tokens; this client only connects to the explicitly configured local mock backend.
public actor LocalMockClient {
    private let backend: BackendClient
    private let serviceConfig: ServiceConfigurationRepository
    private let config: GameBridgeConfig
    private let store: TokenStore
    private let developmentKey: String
    private let pendingStore: TokenStore?
    private let streamConfiguration: URLSessionConfiguration
    private var pushStream: MockPushStream?
    private var pushEpoch = 0
    func stopMockPush() { pushEpoch += 1; pushStream?.stop(); pushStream = nil }
    func startMockPush(installationId: UUID, listener: @escaping (PushPayload) -> Void) {
        stopMockPush()
        let epoch = pushEpoch
        guard let url = URL(string: config.backendBaseURL ?? "") else { return }
        let stream = MockPushStream(baseURL: url, installationId: installationId, configuration: streamConfiguration,
            token: { [weak self] in try await self?.streamToken(epoch: epoch) },
            onPush: { [weak self] value in Task { await self?.forwardMockPush(value, epoch: epoch, listener: listener) } })
        pushStream = stream; stream.start()
    }
    private func streamToken(epoch: Int) async throws -> String? {
        guard epoch == pushEpoch, session != nil else { return nil }
        _ = try await authenticated(path: "/v1/me", method: "GET")
        guard epoch == pushEpoch else { return nil }
        return session?.accessToken
    }
    private func forwardMockPush(_ value: PushPayload, epoch: Int, listener: (PushPayload) -> Void) {
        if epoch == pushEpoch { listener(value) }
    }
    private var session: SecretSession?
    private var refreshFlight: (id: UUID, task: Task<SecretSession, Error>)?
    private var generation = 0
    private var signingIn = false
    private var purchaseBusy = false
    public init(config: GameBridgeConfig, store: TokenStore, developmentKey: String, sessionConfiguration: URLSessionConfiguration = .default, pendingStore: TokenStore? = nil) throws {
        guard config.mode == .localMock else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard developmentKey.count >= 32 else { throw SdkFailure("CONFIG_REQUIRED") }
        if let pendingStore, (store as AnyObject) === (pendingStore as AnyObject) { throw SdkFailure("CONFIG_REQUIRED") }
        let backendClient = try BackendClient(config: config, sessionConfiguration: sessionConfiguration)
        backend = backendClient; serviceConfig = backendServiceConfiguration(backendClient)
        self.config = config; self.store = store; self.developmentKey = developmentKey; self.pendingStore = pendingStore; self.streamConfiguration = sessionConfiguration
    }
    public func signIn(subject: String) async throws -> UserProfile {
        guard ["A", "B"].contains(subject) else { throw SdkFailure("INVALID_ARGUMENT") }
        guard !signingIn else { throw SdkFailure("BUSY") }
        signingIn = true; defer { signingIn = false }
        generation += 1
        if refreshFlight != nil { session = nil }
        refreshFlight?.task.cancel(); refreshFlight = nil; let started = generation
        let response = try await backend.request(path: "/v1/dev/auth", method: "POST", body: encode(["subject": subject]), developmentKey: developmentKey)
        let next = try wrap(decode(response.json) as WireSession)
        guard generation == started else { throw SdkFailure("CANCELED") }
        try store.save(String(decoding: JSONEncoder().encode(next), as: UTF8.self)); session = next
        return UserProfile(userId: next.userId, displayName: nil, provider: "MOCK")
    }
    public func restore() async throws -> UserProfile? {
        guard !signingIn else { throw SdkFailure("BUSY") }
        if session == nil {
            guard let loaded = try loadBoundStored() else { return nil }
            generation += 1; session = loaded
        }
        let started = generation
        let me: Me = try decode(try await authenticated(path: "/v1/me", method: "GET").json)
        guard generation == started else { throw SdkFailure("CANCELED") }
        guard me.userId == session?.userId else { throw SdkFailure("AUTH_FAILED") }
        return UserProfile(userId: me.userId, displayName: nil, provider: "MOCK")
    }
    public func serviceSettings() async throws -> EffectiveServiceSettings {
        guard let settings = try await serviceConfig.current() else { throw SdkFailure("CONFIG_REQUIRED") }
        return settings
    }
    public func products() async throws -> [LocalProduct] { try decode(try await authenticated(path: "/v1/catalog", method: "GET").json) }
    public func wallet() async throws -> LocalWallet { try decode(try await authenticated(path: "/v1/entitlements", method: "GET").json) }
    public func purchase(productId: String, transactionId: UUID, attemptId: UUID) async throws -> LocalPurchase {
        guard !purchaseBusy else { throw SdkFailure("BUSY") }
        purchaseBusy = true; defer { purchaseBusy = false }
        guard ["coins_100", "premium_unlock"].contains(productId) else { throw SdkFailure("PRODUCT_NOT_FOUND") }
        guard let user = session?.userId else { throw SdkFailure("SESSION_EXPIRED") }
        let started = generation
        let maintenance: Bool?
        do { maintenance = try await serviceConfig.current()?.settings.maintenanceEnabled }
        catch is CancellationError { throw SdkFailure("CANCELED") }
        catch { maintenance = nil }
        guard generation == started, session?.userId == user else { throw SdkFailure("CANCELED") }
        guard MaintenanceGate.permits(maintenanceEnabled: maintenance, operation: .startPurchase) else { throw SdkFailure(maintenance == true ? "MAINTENANCE" : "CONFIG_REQUIRED") }
        guard let base = config.backendBaseURL else { throw SdkFailure("CONFIG_REQUIRED") }
        let item = PendingMockPurchase(appId: config.appId, backendBaseURL: base, userId: user, productId: productId,
                                       transactionId: transactionId.uuidString.lowercased(), attemptId: attemptId.uuidString.lowercased())
        let saved = try loadPending()
        if let existing = saved.first(where: { sameScope($0, user: user) }), existing != item { throw SdkFailure("BUSY") }
        if pendingStore != nil && !saved.contains(item) { try savePending(saved + [item]) }
        let result = try await verifyPending(item)
        guard generation == started, session?.userId == user else { throw SdkFailure("CANCELED") }
        if pendingStore != nil { try savePending(try loadPending().filter { $0 != item }) }
        return result
    }
    public func recoverPending() async throws -> LocalRecoveryCounts {
        guard !purchaseBusy else { throw SdkFailure("BUSY") }
        purchaseBusy = true; defer { purchaseBusy = false }
        guard pendingStore != nil else { throw SdkFailure("CONFIG_REQUIRED") }
        guard let user = session?.userId else { throw SdkFailure("SESSION_EXPIRED") }
        let started = generation; let pending = try loadPending().filter { sameScope($0, user: user) }
        var recovered = 0, deferred = 0, failed = 0
        for item in pending {
            do {
                _ = try await verifyPending(item)
                guard generation == started, session?.userId == user else { throw SdkFailure("CANCELED") }
                try savePending(try loadPending().filter { $0 != item }); recovered += 1
            } catch is CancellationError { throw SdkFailure("CANCELED") }
            catch let failure as SdkFailure {
                if ["SESSION_EXPIRED", "CANCELED"].contains(failure.code) { throw failure }
                if ["NETWORK_UNAVAILABLE", "TIMEOUT", "BUSY"].contains(failure.code) { deferred += 1 } else { failed += 1 }
            }
        }
        return LocalRecoveryCounts(examinedCount: pending.count, recoveredCount: recovered, deferredCount: deferred, failureCount: failed)
    }
    private func sameScope(_ item: PendingMockPurchase, user: String) -> Bool {
        item.appId == config.appId && item.backendBaseURL == config.backendBaseURL && item.userId == user
    }
    private func loadPending() throws -> [PendingMockPurchase] {
        guard let raw = try pendingStore?.load() else { return [] }
        let items: [PendingMockPurchase]
        do { items = try JSONDecoder().decode([PendingMockPurchase].self, from: Data(raw.utf8)) }
        catch { throw SdkFailure("INTERNAL_ERROR") }
        guard items.allSatisfy({ item in
            !item.appId.isEmpty && !item.backendBaseURL.isEmpty && ["coins_100", "premium_unlock"].contains(item.productId) &&
            [item.userId, item.transactionId, item.attemptId].allSatisfy { UUID(uuidString: $0)?.uuidString.lowercased() == $0 }
        }) else { throw SdkFailure("INTERNAL_ERROR") }
        return items
    }
    private func savePending(_ items: [PendingMockPurchase]) throws {
        guard let pendingStore else { throw SdkFailure("CONFIG_REQUIRED") }
        if items.isEmpty { try pendingStore.clear() }
        else { try pendingStore.save(String(decoding: JSONEncoder().encode(items), as: UTF8.self)) }
    }
    private func verifyPending(_ item: PendingMockPurchase) async throws -> LocalPurchase {
        guard let user = session?.userId else { throw SdkFailure("SESSION_EXPIRED") }
        guard sameScope(item, user: user) else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
        let proof = "mock:\(user):\(item.productId):\(item.transactionId)"
        let body = try encode(["productId": item.productId, "proof": proof, "quantity": 1])
        let result: LocalPurchase = try decode(try await authenticated(path: "/v1/purchases/verify", method: "POST", body: body, idempotencyKey: item.attemptId).json)
        guard result.entitlements.userId == user, ["GRANTED", "ALREADY_GRANTED"].contains(result.fulfillmentStatus),
              ["PENDING", "FINALIZED", "NOT_REQUIRED"].contains(result.finalizationStatus),
              UUID(uuidString: result.serverPurchaseId)?.uuidString.lowercased() == result.serverPurchaseId else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        return result
    }
    public func xcodeAccount() async throws -> XcodeMockAccount {
        let value: XcodeMockAccount = try decode(try await authenticated(path: "/v1/dev/xcode-storekit/account", method: "POST", development: true).json)
        guard value.userId == value.bindingId else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        return value
    }
    public func xcodeGrant(productId: String, transactionId: UInt64, account: XcodeMockAccount) async throws -> XcodeMockGrant {
        guard transactionId > 0 else { throw SdkFailure("INVALID_ARGUMENT") }
        return try await xcodeGrant(productId: productId, transactionKey: String(transactionId), account: account)
    }
    public func xcodeGrant(productId: String, transactionKey: String, account: XcodeMockAccount) async throws -> XcodeMockGrant {
        guard ["coins_100", "premium_unlock"].contains(productId),
              transactionKey.range(of: "^([1-9][0-9]{0,19}|[0-9a-f]{64})$", options: .regularExpression) != nil else { throw SdkFailure("INVALID_ARGUMENT") }
        let body = try encode(["productId": productId, "transactionId": transactionKey, "bindingId": account.bindingId.uuidString.lowercased()])
        let value: XcodeMockGrant = try decode(try await authenticated(path: "/v1/dev/xcode-storekit/grant", method: "POST", body: body, development: true).json)
        guard value.userId == account.userId, value.bindingId == account.bindingId, value.productId == productId,
              value.transactionKey == transactionKey, ["GRANTED", "ALREADY_GRANTED"].contains(value.fulfillmentStatus) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        return value
    }
    public func xcodeWallet(account: XcodeMockAccount) async throws -> LocalWallet {
        let value: LocalWallet = try decode(try await authenticated(path: "/v1/dev/xcode-storekit/wallet", method: "POST", development: true).json)
        guard value.userId == account.userId.uuidString.lowercased() else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        return value
    }
    public func registerMockPush(installationId: UUID) async throws -> LocalPushRegistration {
        struct Output: Decodable { let provider: String; let registered: Bool; let tokenFingerprint: String }
        let started = generation
        let body = try encode(["token": "mock:" + UUID().uuidString.lowercased(), "provider": "MOCK", "platform": "MOCK", "appId": config.appId])
        let response = try await authenticated(path: "/v1/devices/\(installationId.uuidString.lowercased())/push-token", method: "PUT", body: body)
        let output: Output = try decode(response.json)
        guard generation == started, output.provider == "MOCK", output.registered,
              output.tokenFingerprint.range(of: "^[0-9a-f]{12}$", options: .regularExpression) != nil else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
        return LocalPushRegistration(tokenFingerprint: output.tokenFingerprint, updatedAt: ISO8601DateFormatter().string(from: Date()))
    }
    public func unregisterMockPush(installationId: UUID) async throws {
        struct Output: Decodable { let registered: Bool }
        let started = generation
        let response = try await authenticated(path: "/v1/devices/\(installationId.uuidString.lowercased())/push-token", method: "DELETE")
        let output: Output = try decode(response.json)
        guard generation == started, !output.registered else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    }
    public func signOut() async throws {
        let raw = try store.load()
        let pending = raw == "{\"state\":\"refresh_pending\"}"
        let stored = pending ? nil : try loadBoundStored()
        let old = session ?? stored
        generation += 1; session = nil; refreshFlight?.task.cancel(); refreshFlight = nil
        try store.clear()
        if let old {
            do {
                do { _ = try await backend.request(path: "/v1/auth/logout", method: "POST", accessToken: old.accessToken) }
                catch let error as SdkFailure where error.code == "SESSION_EXPIRED" {
                    _ = try await backend.request(path: "/v1/auth/logout", method: "POST", body: encode(["refreshToken": old.refreshToken]))
                }
            } catch let error as SdkFailure { throw SdkFailure(error.code, nativeCode: "REVOCATION_UNCONFIRMED", retryable: error.retryable) }
            catch { throw SdkFailure("INTERNAL_ERROR", nativeCode: "REVOCATION_UNCONFIRMED") }
        } else if pending { throw SdkFailure("SESSION_EXPIRED", nativeCode: "REVOCATION_UNCONFIRMED") }
    }
    private func loadBoundStored() throws -> SecretSession? {
        guard let saved = try store.load() else { return nil }
        let loaded: SecretSession
        do { loaded = try decode(Data(saved.utf8)) } catch { throw SdkFailure("SESSION_EXPIRED") }
        guard loaded.appId == config.appId, loaded.providerMode == config.mode.rawValue, loaded.backendBaseURL == config.backendBaseURL,
              !loaded.accessToken.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, !loaded.refreshToken.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              UUID(uuidString: loaded.userId) != nil, Self.isUTCInstant(loaded.expiresAt) else { throw SdkFailure("SESSION_EXPIRED") }
        return loaded
    }
    private func authenticated(path: String, method: String, body: Data? = nil, idempotencyKey: String? = nil, development: Bool = false) async throws -> BackendResponse {
        guard !signingIn else { throw SdkFailure("BUSY") }
        guard let current = session else { throw SdkFailure("SESSION_EXPIRED") }
        let started = generation
        do {
            let response = try await backend.request(path: path, method: method, body: body, accessToken: current.accessToken, developmentKey: development ? developmentKey : nil, idempotencyKey: idempotencyKey)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return response
        } catch let error as SdkFailure where error.code == "SESSION_EXPIRED" {
            guard generation == started else { throw SdkFailure("CANCELED") }
            if let latest = session, latest.accessToken != current.accessToken {
                let response = try await backend.request(path: path, method: method, body: body, accessToken: latest.accessToken, developmentKey: development ? developmentKey : nil, idempotencyKey: idempotencyKey)
                guard generation == started else { throw SdkFailure("CANCELED") }
                return response
            }
            let flight: (id: UUID, task: Task<SecretSession, Error>)
            if let existing = refreshFlight { flight = existing }
            else {
                // A durable tombstone prevents replay if the rotation response is lost or the app exits.
                try store.save("{\"state\":\"refresh_pending\"}")
                let backend = self.backend; let config = self.config
                let task = Task {
                    let body = try JSONSerialization.data(withJSONObject: ["refreshToken": current.refreshToken])
                    let response = try await backend.request(path: "/v1/auth/refresh", method: "POST", body: body)
                    let wire: WireSession
                    do { wire = try JSONDecoder().decode(WireSession.self, from: response.json) }
                    catch { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
                    return try Self.wrap(wire, config: config)
                }
                flight = (UUID(), task); refreshFlight = flight
            }
            let refreshed: SecretSession
            do { refreshed = try await flight.task.value }
            catch {
                if generation == started && refreshFlight?.id == flight.id { refreshFlight = nil; session = nil }
                throw error
            }
            guard generation == started else { throw SdkFailure("CANCELED") }
            if refreshed.userId != current.userId {
                if refreshFlight?.id == flight.id { session = nil; refreshFlight = nil }
                throw SdkFailure("AUTH_FAILED")
            }
            if refreshFlight?.id == flight.id {
                do { try store.save(String(decoding: JSONEncoder().encode(refreshed), as: UTF8.self)) }
                catch { session = nil; refreshFlight = nil; throw SdkFailure("INTERNAL_ERROR") }
                session = refreshed; refreshFlight = nil
            }
            guard let usable = session else { throw SdkFailure("SESSION_EXPIRED") }
            let response = try await backend.request(path: path, method: method, body: body, accessToken: usable.accessToken, developmentKey: development ? developmentKey : nil, idempotencyKey: idempotencyKey)
            guard generation == started else { throw SdkFailure("CANCELED") }
            return response
        }
    }
    private func wrap(_ value: WireSession) throws -> SecretSession { try Self.wrap(value, config: config) }
    private static func wrap(_ value: WireSession, config: GameBridgeConfig) throws -> SecretSession {
        guard !value.accessToken.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, !value.refreshToken.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, UUID(uuidString: value.userId) != nil,
              let url = config.backendBaseURL, isUTCInstant(value.expiresAt) else { throw SdkFailure("AUTH_FAILED") }
        return SecretSession(accessToken: value.accessToken, refreshToken: value.refreshToken, expiresAt: value.expiresAt,
                             userId: value.userId, appId: config.appId, providerMode: config.mode.rawValue, backendBaseURL: url)
    }
    private static func isUTCInstant(_ value: String) -> Bool {
        guard value.hasSuffix("Z") else { return false }
        let fractional = ISO8601DateFormatter(); fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return fractional.date(from: value) != nil || ISO8601DateFormatter().date(from: value) != nil
    }
    private func encode(_ value: [String: Any]) throws -> Data { try JSONSerialization.data(withJSONObject: value) }
    private func decode<T: Decodable>(_ data: Data) throws -> T {
        do { return try JSONDecoder().decode(T.self, from: data) } catch { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    }
}
