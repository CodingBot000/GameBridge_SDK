import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

/// Host supplies the installation ID; raw device token stays in the Native Backend channel.
@MainActor
final class ApplePushRegistration {
    private let auth: AppleAuthProvider
    private let installationId: UUID
    private let request: (String, String, Data?, String) async throws -> Data
    init(auth: AppleAuthProvider, installationId: UUID, request: @escaping (String, String, Data?, String) async throws -> Data) {
        self.auth = auth; self.installationId = installationId; self.request = request
    }
    convenience init(auth: AppleAuthProvider, installationId: UUID, client: BackendClient) {
        self.init(auth: auth, installationId: installationId) { path, method, body, token in
            try await client.request(path: path, method: method, body: body, accessToken: token).json
        }
    }
    private var path: String { "/v1/devices/\(installationId.uuidString.lowercased())/push-token" }
    func register(deviceToken: Data) async throws -> String {
        guard !deviceToken.isEmpty else { throw SdkFailure("INVALID_ARGUMENT") }
        let token = deviceToken.map { String(format: "%02x", $0) }.joined()
        let fingerprint: String? = try await auth.withAuthenticatedSession { session in
            let body = try JSONSerialization.data(withJSONObject: ["token": token, "provider": "APNS", "platform": "IOS"])
            let data = try await request(path, "PUT", body, session.accessToken)
            struct Result: Decodable { let provider: String; let registered: Bool; let tokenFingerprint: String }
            guard let result = try? JSONDecoder().decode(Result.self, from: data), result.provider == "APNS", result.registered,
                  result.tokenFingerprint.range(of: "^[0-9a-f]{12}$", options: .regularExpression) != nil else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return result.tokenFingerprint
        }
        guard let fingerprint else { throw SdkFailure("SESSION_EXPIRED") }
        return fingerprint
    }
    func unregister() async throws {
        let done: Bool? = try await auth.withAuthenticatedSession { session in
            let data = try await request(path, "DELETE", nil, session.accessToken)
            struct Result: Decodable { let registered: Bool }
            guard let result = try? JSONDecoder().decode(Result.self, from: data), !result.registered else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return true
        }
        guard done == true else { throw SdkFailure("SESSION_EXPIRED") }
    }
}
