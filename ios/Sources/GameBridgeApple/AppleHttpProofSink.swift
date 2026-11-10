import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// Raw StoreKit JWS is transmitted only to the configured Backend over the Native channel.
@MainActor
final class AppleHttpProofSink: ApplePurchaseProofSink {
    private let auth: AppleAuthProvider
    private let client: BackendClient
    init(auth: AppleAuthProvider, client: BackendClient) { self.auth = auth; self.client = client }
    func verify(_ proof: ApplePurchaseProof, userId: UUID) async throws -> ServerGrant {
        struct Output: Decodable {
            let userId, bindingId: UUID
            let productId, transactionKey: String
            let serverPurchaseId: UUID
            let fulfillmentStatus: String
        }
        guard !proof.signedTransaction.isEmpty else { throw SdkFailure("VERIFICATION_FAILED") }
        let result: ServerGrant? = try await auth.withAuthenticatedSession { session in
            guard UUID(uuidString: session.userId) == userId else { throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH") }
            let body = try JSONSerialization.data(withJSONObject: ["storeProductId": proof.productId, "signedTransaction": proof.signedTransaction])
            let response = try await client.request(path: "/v1/purchases/apple/verify", method: "POST", body: body,
                                                    accessToken: session.accessToken, idempotencyKey: UUID().uuidString.lowercased())
            guard let output = try? JSONDecoder().decode(Output.self, from: response.json),
                  ["GRANTED", "ALREADY_GRANTED"].contains(output.fulfillmentStatus) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return ServerGrant(userId: output.userId, bindingId: output.bindingId, productId: output.productId,
                               transactionKey: output.transactionKey, serverPurchaseId: output.serverPurchaseId)
        }
        guard let result else { throw SdkFailure("SESSION_EXPIRED") }
        return result
    }
}
