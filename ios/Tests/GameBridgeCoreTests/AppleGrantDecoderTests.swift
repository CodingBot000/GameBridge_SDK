import Foundation
import XCTest
import GameBridgeCore
@testable import GameBridgeApple

final class AppleGrantDecoderTests: XCTestCase {
    private func payload(_ status: String = "GRANTED") -> [String: Any] {
        ["userId":"d2719c4e-d533-47ee-9efd-838791ea79c8", "bindingId":"dc9a46f4-8e20-4880-bcbb-ac45033157ca", "serverPurchaseId":"e11d9511-5cc9-4c5d-81a5-28b6a8693831", "productId":"coins_100", "transactionKey":"fixture-transaction", "fulfillmentStatus":status]
    }
    func testAllowedStatusesAndUnknownFieldsPreserveDecodedGrant() throws {
        for status in ["GRANTED", "ALREADY_GRANTED"] {
            var body = payload(status); body["futureField"] = true
            let grant = try decodeAppleServerGrant(JSONSerialization.data(withJSONObject: body))
            XCTAssertEqual(grant.fulfillmentStatus, status); XCTAssertEqual(grant.productId, "coins_100")
            XCTAssertEqual(grant.userId, UUID(uuidString: "d2719c4e-d533-47ee-9efd-838791ea79c8"))
        }
    }
    func testMalformedMissingAndRejectedStatusKeepProtocolError() throws {
        var invalidUuid = payload(); invalidUuid["userId"] = "bad-uuid"
        var missing = payload(); missing.removeValue(forKey: "transactionKey")
        for body in [invalidUuid, missing, payload("PENDING")] {
            XCTAssertThrowsError(try decodeAppleServerGrant(JSONSerialization.data(withJSONObject: body))) { error in
                XCTAssertEqual((error as? SdkFailure)?.code, "BRIDGE_PROTOCOL_MISMATCH")
            }
        }
    }
    func testDecoderDoesNotTakeOverDownstreamProductBindingPolicy() throws {
        var body = payload(); body["productId"] = ""; body["transactionKey"] = ""
        let grant = try decodeAppleServerGrant(JSONSerialization.data(withJSONObject: body))
        XCTAssertEqual(grant.productId, ""); XCTAssertEqual(grant.transactionKey, "")
    }
}
