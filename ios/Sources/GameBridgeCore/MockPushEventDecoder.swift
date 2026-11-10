import Foundation

/// Decode only local-mock route fields; ignore arbitrary payload data.
enum MockPushEventDecoder {
    static func decode(_ data: Data) -> PushPayload? {
        guard data.count <= BridgeProtocol.maxBytes, String(data: data, encoding: .utf8) != nil,
              let json = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] else { return nil }
        var fields: [AnyHashable: Any] = [:]
        if let id = json["messageId"] { fields["messageId"] = id }
        if let route = json["route"] { fields["route"] = route }
        if let campaign = json["campaignId"], !(campaign is NSNull) { fields["campaignId"] = campaign }
        return PushPayload(data: fields)
    }
}
