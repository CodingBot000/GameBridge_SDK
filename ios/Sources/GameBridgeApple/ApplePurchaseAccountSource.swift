import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@MainActor
final class ApplePurchaseAccountSource {
    private let auth: AppleAuthProvider
    private let request: (String) async throws -> Data
    private var cached: (generation: Int, account: ApplePurchaseAccount)?
    init(auth: AppleAuthProvider, request: @escaping (String) async throws -> Data) { self.auth = auth; self.request = request }
    convenience init(auth: AppleAuthProvider, client: BackendClient) {
        self.init(auth: auth) { accessToken in
            try await client.request(path: "/v1/purchases/bindings", method: "GET", accessToken: accessToken).json
        }
    }
    func current() -> ApplePurchaseAccount? {
        guard let cached, cached.generation == auth.sessionGeneration else { return nil }
        return cached.account
    }
    func refresh() async throws -> ApplePurchaseAccount? {
        let account = try await auth.withAuthenticatedSession { session in
            let data = try await request(session.accessToken)
            return try parseAppleBinding(userId: session.userId, data: data)
        }
        cached = account.map { (auth.sessionGeneration, $0) }
        return account
    }
}

func parseAppleBinding(userId: String, data: Data) throws -> ApplePurchaseAccount {
    struct Binding: Decodable { let appleAccountToken: UUID }
    guard let user = UUID(uuidString: userId), let binding = try? JSONDecoder().decode(Binding.self, from: data) else {
        throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH")
    }
    return ApplePurchaseAccount(userId: user, binding: binding.appleAccountToken)
}
