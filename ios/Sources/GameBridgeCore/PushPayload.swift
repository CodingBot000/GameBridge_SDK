import Foundation

public struct PushPayload: Equatable {
    public let messageId: String
    public let route: String
    public let campaignId: String?
    public init?(data: [AnyHashable: Any]) {
        guard let id = data["messageId"] as? String, !id.isEmpty,
              let destination = data["route"] as? String, ["home", "store"].contains(destination) else { return nil }
        if let campaign = data["campaignId"], !(campaign is String) { return nil }
        messageId = id; route = destination; campaignId = data["campaignId"] as? String
    }
}
