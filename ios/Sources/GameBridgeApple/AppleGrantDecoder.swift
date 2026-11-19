import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

// Pure response decoding; attempt ownership, authenticated retry and finish remain with their owners.
func decodeAppleServerGrant(_ data: Data) throws -> ServerGrant {
    struct Output: Decodable {
        let userId, bindingId: UUID
        let productId, transactionKey: String
        let serverPurchaseId: UUID
        let fulfillmentStatus: String
    }
    guard let output = try? JSONDecoder().decode(Output.self, from: data),
          ["GRANTED", "ALREADY_GRANTED"].contains(output.fulfillmentStatus) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
    return ServerGrant(userId: output.userId, bindingId: output.bindingId, productId: output.productId,
                       transactionKey: output.transactionKey, serverPurchaseId: output.serverPurchaseId, fulfillmentStatus: output.fulfillmentStatus)
}
