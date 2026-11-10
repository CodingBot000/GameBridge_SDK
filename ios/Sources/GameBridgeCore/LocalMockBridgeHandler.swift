import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// Development-only bridge. Authentication tokens and purchase proofs remain Native-owned.
public actor LocalMockBridgeHandler {
    private let tokenStore: () -> TokenStore
    private let sessionConfiguration: URLSessionConfiguration
    private let pendingStore: (() -> TokenStore)?
    private var client: LocalMockClient?
    private var config: GameBridgeConfig?
    private var developmentKey: String?
    private var subject: String?
    private var installationId: UUID?
    private var pushSinkFactory: (() -> ((PushPayload) -> Void))?
    public func setMockPushSinkFactory(_ factory: (() -> ((PushPayload) -> Void))?) { pushSinkFactory = factory }

    public init(tokenStore: @escaping () -> TokenStore, sessionConfiguration: URLSessionConfiguration = .default, pendingStore: (() -> TokenStore)? = nil) {
        self.tokenStore = tokenStore; self.sessionConfiguration = sessionConfiguration; self.pendingStore = pendingStore
    }

    public func invoke(_ operation: String, payload: [String: Any]) async throws -> Any {
        if operation == "sdk.initialize" { return try initialize(payload) }
        if operation == "sdk.shutdown" {
            await client?.stopMockPush(); client = nil; config = nil; developmentKey = nil; subject = nil; installationId = nil
            return ["state": "SHUTDOWN"]
        }
        guard let client else { throw SdkFailure("NOT_INITIALIZED") }
        switch operation {
        case "auth.signIn":
            guard payload["provider"] as? String == "MOCK" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
            await client.stopMockPush()
            return try object(try await client.signIn(subject: subject!))
        case "auth.restore":
            let user = try await client.restore()
            return ["signedIn": user != nil, "user": try user.map { try object($0) } ?? NSNull(),
                    "expiresAt": NSNull(), "sessionRestored": user != nil] as [String: Any]
        case "auth.signOut": await client.stopMockPush(); try await client.signOut(); return [String: Any]()
        case "push.permission": return ["provider": "MOCK", "permission": "GRANTED"]
        case "push.register":
            guard let installationId else { throw SdkFailure("CONFIG_REQUIRED") }
            let result = try await client.registerMockPush(installationId: installationId)
            if let listener = pushSinkFactory?() { await client.startMockPush(installationId: installationId, listener: listener) }
            return ["provider": "MOCK", "permission": "GRANTED", "registered": true,
                    "tokenFingerprint": result.tokenFingerprint, "updatedAt": result.updatedAt] as [String: Any]
        case "push.unregister":
            guard let installationId else { throw SdkFailure("CONFIG_REQUIRED") }
            await client.stopMockPush(); try await client.unregisterMockPush(installationId: installationId); return ["registered": false]
        case "config.get":
            let effective = try await client.serviceSettings()
            let formatter = ISO8601DateFormatter(); formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            return ["revision": effective.settings.revision, "maintenanceEnabled": effective.settings.maintenanceEnabled,
                    "message": effective.settings.message as Any? ?? NSNull(), "expiresAt": formatter.string(from: effective.settings.expiresAt),
                    "source": effective.source == .remote ? "NETWORK" : "CACHE"] as [String: Any]
        case "store.products":
            return try await client.products().map { product in
                ["productId": product.productId, "storeProductId": product.storeProductId, "type": product.type,
                 "title": "Mock \(product.productId)", "localizedPrice": "Mock price", "currencyCode": "XXX", "priceMicros": NSNull()] as [String: Any]
            }
        case "store.entitlements": return try object(try await client.wallet())
        case "store.sync":
            guard let reason = payload["reason"] as? String, ["APP_RESUME", "USER_RESTORE"].contains(reason) else { throw SdkFailure("INVALID_ARGUMENT") }
            let counts = try await client.recoverPending(); let wallet = try await client.wallet()
            return ["examinedCount": counts.examinedCount, "recoveredCount": counts.recoveredCount,
                    "deferredCount": counts.deferredCount, "failureCount": counts.failureCount, "entitlements": try object(wallet)] as [String: Any]
        case "store.purchase":
            guard let productId = payload["productId"] as? String, !productId.isEmpty else { throw SdkFailure("INVALID_ARGUMENT") }
            let attempt = UUID()
            let purchase = try await client.purchase(productId: productId, transactionId: UUID(), attemptId: attempt)
            return ["attemptId": attempt.uuidString.lowercased(), "productId": productId, "status": "PURCHASED",
                    "serverPurchaseId": purchase.serverPurchaseId, "fulfillmentStatus": purchase.fulfillmentStatus,
                    "finalizationStatus": purchase.finalizationStatus, "error": NSNull()] as [String: Any]
        default: throw SdkFailure("UNSUPPORTED_OPERATION")
        }
    }
    private func initialize(_ payload: [String: Any]) throws -> [String: Any] {
        guard payload["providerMode"] as? String == "LOCAL_MOCK" else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        guard let appId = payload["appId"] as? String, let base = payload["backendBaseUrl"] as? String,
              let timeout = payload["requestTimeoutMs"] as? Int, let key = payload["developmentKey"] as? String, key.count >= 32,
              let subject = payload["mockSubject"] as? String, ["A", "B"].contains(subject) else { throw SdkFailure("CONFIG_REQUIRED") }
        let next = GameBridgeConfig(appId: appId, mode: .localMock, backendBaseURL: base, requestTimeoutMs: timeout)
        do { try next.validate() } catch { throw SdkFailure("CONFIG_REQUIRED") }
        let installation: UUID?
        if let raw = payload["installationId"] {
            guard let text = raw as? String, let parsed = UUID(uuidString: text), parsed.uuidString.lowercased() == text.lowercased() else { throw SdkFailure("CONFIG_REQUIRED") }
            installation = parsed
        } else { installation = nil }
        if client != nil && (config != next || developmentKey != key || self.subject != subject || installationId != installation) { throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG") }
        if client == nil {
            client = try LocalMockClient(config: next, store: tokenStore(), developmentKey: key, sessionConfiguration: sessionConfiguration, pendingStore: pendingStore?())
            config = next; developmentKey = key; self.subject = subject; installationId = installation
        }
        var capabilities: [String: Any] = [:]
        for name in ["auth", "store", "push", "config"] {
            let available = name == "auth" || name == "store" || name == "config" || name == "push"
            let configured = name != "push" || installation != nil
            let reason: Any
            if name == "store" && pendingStore == nil { reason = "Purchase recovery storage is not configured" }
            else if name == "push" { reason = installation == nil ? "Installation ID required" : "Simulated Mock; no remote delivery" }
            else if available { reason = NSNull() }
            else { reason = "Bridge operation is not connected" }
            capabilities[name] = ["supported": available, "configured": configured, "mode": "LOCAL_MOCK", "reason": reason]
        }
        return ["state": "READY", "mode": "LOCAL_MOCK", "provider": "MOCK", "capabilities": capabilities]
    }
    private func object<T: Encodable>(_ value: T) throws -> Any {
        try JSONSerialization.jsonObject(with: JSONEncoder().encode(value))
    }
}
