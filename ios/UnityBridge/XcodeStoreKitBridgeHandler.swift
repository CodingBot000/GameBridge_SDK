#if canImport(StoreKit)
import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
import GameBridgeApple
#endif

@MainActor final class XcodeStoreKitBridgeHandler {
    private let makeClient: (GameBridgeConfig, String) throws -> LocalMockClient
    private let makeEmitter: () -> (AppleStorePurchaseResult) -> Void
    private var client: LocalMockClient?
    private var config: GameBridgeConfig?
    private var key: String?
    private var subject: String?
    private var store: XcodeStoreKitSession?
    init(makeClient: @escaping (GameBridgeConfig, String) throws -> LocalMockClient,
         makeEmitter: @escaping () -> (AppleStorePurchaseResult) -> Void) {
        self.makeClient = makeClient; self.makeEmitter = makeEmitter
    }
    func invoke(_ operation: String, payload: [String: Any]) async throws -> Any {
        if operation == "sdk.initialize" { return try initialize(payload) }
        if operation == "sdk.shutdown" { store?.stop(); store = nil; client = nil; config = nil; key = nil; subject = nil; return ["state":"SHUTDOWN"] }
        guard let client else { throw SdkFailure("NOT_INITIALIZED") }
        switch operation {
        case "auth.signIn":
            guard payload["provider"] as? String == "MOCK" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
            store?.stop(); store = nil
            _ = try await client.signIn(subject: subject!)
            let account = try await client.xcodeAccount()
            return try object(UserProfile(userId: account.userId.uuidString.lowercased(), displayName: nil, provider: "MOCK"))
        case "auth.restore":
            guard try await client.restore() != nil else { return ["signedIn":false, "user":NSNull(), "expiresAt":NSNull(), "sessionRestored":false] }
            let account = try await client.xcodeAccount()
            let profile = UserProfile(userId: account.userId.uuidString.lowercased(), displayName: nil, provider: "MOCK")
            return ["signedIn":true, "user":try object(profile), "expiresAt":NSNull(), "sessionRestored":true]
        case "auth.signOut": store?.stop(); store = nil; try await client.signOut(); return [String: Any]()
        case "config.get":
            let effective = try await client.serviceSettings()
            let formatter = ISO8601DateFormatter(); formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            return ["revision":effective.settings.revision, "maintenanceEnabled":effective.settings.maintenanceEnabled,
                    "message":effective.settings.message as Any? ?? NSNull(), "expiresAt":formatter.string(from: effective.settings.expiresAt),
                    "source":effective.source == .remote ? "NETWORK" : "CACHE"] as [String: Any]
        case "store.products": return try object(try await activeStore(client).products())
        case "store.entitlements": return try object(try await activeStore(client).wallet())
        case "store.purchase":
            guard let productId = payload["productId"] as? String else { throw SdkFailure("INVALID_ARGUMENT") }
            let result = try await activeStore(client).purchase(productId)
            let status: String, fulfillment: String, finalization: String
            switch result.status {
            case .purchased: status = "PURCHASED"; fulfillment = result.fulfillmentStatus ?? "NOT_GRANTED"; finalization = "FINALIZED"
            case .pending: status = "PENDING"; fulfillment = "NOT_GRANTED"; finalization = "NOT_REQUIRED"
            case .verificationPending: status = "VERIFICATION_PENDING"; fulfillment = "NOT_GRANTED"; finalization = "NOT_REQUIRED"
            case .cancelled: status = "CANCELED"; fulfillment = "NOT_GRANTED"; finalization = "NOT_REQUIRED"
            }
            return ["attemptId":UUID().uuidString.lowercased(), "productId":productId, "status":status,
                    "serverPurchaseId":result.serverPurchaseId?.uuidString.lowercased() as Any? ?? NSNull(),
                    "fulfillmentStatus":fulfillment, "finalizationStatus":finalization, "error":NSNull()] as [String: Any]
        case "store.sync":
            guard let reason = payload["reason"] as? String, ["APP_RESUME", "USER_RESTORE"].contains(reason) else { throw SdkFailure("INVALID_ARGUMENT") }
            let active = try await activeStore(client); let counts = try await active.recover(userInitiated: reason == "USER_RESTORE")
            return ["examinedCount":counts.examinedCount, "recoveredCount":counts.recoveredCount, "deferredCount":counts.deferredCount,
                    "failureCount":counts.failureCount, "entitlements":try object(try await active.wallet())] as [String: Any]
        default: throw SdkFailure("UNSUPPORTED_OPERATION")
        }
    }
    private func activeStore(_ client: LocalMockClient) async throws -> XcodeStoreKitSession {
        if let store { return store }
        let next = try await XcodeStoreKitSession(client: client, onVerified: makeEmitter())
        do { try await next.start(); store = next; return next } catch { next.stop(); throw error }
    }
    private func initialize(_ payload: [String: Any]) throws -> [String: Any] {
        guard payload["providerMode"] as? String == "XCODE_STOREKIT" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard let app = payload["appId"] as? String, app == "gamebridge-sample", let base = payload["backendBaseUrl"] as? String,
              let timeout = payload["requestTimeoutMs"] as? Int, let key = payload["developmentKey"] as? String, key.count >= 32,
              let subject = payload["mockSubject"] as? String, ["A", "B"].contains(subject) else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = GameBridgeConfig(appId: app, mode: .localMock, backendBaseURL: base, requestTimeoutMs: timeout)
        do { try next.validate() } catch { throw SdkFailure("CONFIG_REQUIRED") }
        if client != nil && (config != next || self.key != key || self.subject != subject) { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        if client == nil { client = try makeClient(next, key); config = next; self.key = key; self.subject = subject }
        var capabilities: [String: Any] = [:]
        for name in ["auth", "store", "push", "config"] {
            let supported = name != "push"
            capabilities[name] = ["supported":supported, "configured":supported, "mode":"XCODE_STOREKIT", "reason":supported ? NSNull() as Any : "Not available in Xcode StoreKit mode"]
        }
        return ["state":"READY", "mode":"XCODE_STOREKIT", "provider":"MOCK", "capabilities":capabilities]
    }
    private func object<T: Encodable>(_ value: T) throws -> Any { try JSONSerialization.jsonObject(with: JSONEncoder().encode(value)) }
}
#endif
