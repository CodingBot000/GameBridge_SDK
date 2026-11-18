import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// Raw StoreKit JWS is transmitted only to the configured Backend over the Native channel.
@MainActor
final class AppleHttpProofSink: ApplePurchaseProofSink {
    private let auth: any BackendSessionAccess
    private let client: BackendClient
    init(auth: any BackendSessionAccess, client: BackendClient) { self.auth = auth; self.client = client }
    func ensureReady(storeProductId: String) async throws {
        let ready: Bool? = try await auth.withBackendSession { session in
            let body = try JSONSerialization.data(withJSONObject: ["storeProductId": storeProductId])
            let response = try await client.request(path: "/v1/purchases/apple/readiness", method: "POST", body: body, accessToken: session.accessToken)
            struct Readiness: Decodable { let ready: Bool }
            guard let value = try? JSONDecoder().decode(Readiness.self, from: response.json), value.ready else { throw SdkFailure("CONFIG_REQUIRED") }
            return true
        }
        guard ready == true else { throw SdkFailure("SESSION_EXPIRED") }
    }
    func verify(_ proof: ApplePurchaseProof, userId: UUID) async throws -> ServerGrant {
        guard !proof.signedTransaction.isEmpty else { throw SdkFailure("VERIFICATION_FAILED") }
        let attemptId = UUID().uuidString.lowercased()
        let result: ServerGrant? = try await auth.withBackendSession { session in
            guard UUID(uuidString: session.userId) == userId else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
            let body = try JSONSerialization.data(withJSONObject: ["storeProductId": proof.productId, "signedTransaction": proof.signedTransaction])
            let response = try await client.request(path: "/v1/purchases/apple/verify", method: "POST", body: body,
                                                    accessToken: session.accessToken, idempotencyKey: attemptId)
            return try decodeAppleServerGrant(response.json)
        }
        guard let result else { throw SdkFailure("SESSION_EXPIRED") }
        return result
    }
}
