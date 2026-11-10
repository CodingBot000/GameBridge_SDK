import Foundation
import CoreFoundation

public enum BridgeProtocolError: Error { case mismatch, payloadTooLarge }
public enum BridgeProtocol {
    public static let maxBytes = 256 * 1024
    private static let operations: Set<String> = [
        "sdk.initialize", "sdk.status", "sdk.capabilities", "auth.signIn", "auth.signOut", "auth.restore",
        "store.products", "store.purchase", "store.entitlements", "store.sync", "push.permission", "push.register",
        "push.unregister", "config.get", "diagnostics.get", "sdk.shutdown", "host.pushToken", "host.pushReceived",
        "host.pushOpened", "host.lifecycle"
    ]
    private static func uuid(_ value: Any?) -> String? {
        guard let s = value as? String, let parsed = UUID(uuidString: s), parsed.uuidString.lowercased() == s.lowercased() else { return nil }
        return s
    }
    public static func parse(_ data: Data, expectedSession: String? = nil, expectedRequest: String? = nil) throws -> [String: Any] {
        guard data.count <= maxBytes else { throw BridgeProtocolError.payloadTooLarge }
        guard String(data: data, encoding: .utf8) != nil,
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let version = json["protocolVersion"] as? NSNumber, CFGetTypeID(version) != CFBooleanGetTypeID(),
              version.doubleValue == 1,
              let session = uuid(json["sdkSessionId"]), expectedSession == nil || session == expectedSession,
              let kind = json["kind"] as? String else { throw BridgeProtocolError.mismatch }
        switch kind {
        case "request", "response":
            guard let request = uuid(json["requestId"]), expectedRequest == nil || request == expectedRequest,
                  let op = json["operation"] as? String, operations.contains(op) else { throw BridgeProtocolError.mismatch }
            if kind == "request" {
                guard json["payload"] is [String: Any] else { throw BridgeProtocolError.mismatch }
            } else {
                guard let number = json["ok"] as? NSNumber, CFGetTypeID(number) == CFBooleanGetTypeID(),
                      let result = json["result"], let error = json["error"] else { throw BridgeProtocolError.mismatch }
                if number.boolValue {
                    guard error is NSNull else { throw BridgeProtocolError.mismatch }
                } else {
                    guard result is NSNull, error is [String: Any] else { throw BridgeProtocolError.mismatch }
                }
            }
        case "event":
            guard uuid(json["eventId"]) != nil, json["payload"] is [String: Any] else { throw BridgeProtocolError.mismatch }
        default: throw BridgeProtocolError.mismatch
        }
        return json
    }
}
