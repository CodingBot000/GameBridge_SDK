import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

public protocol TokenStore {
    func load() throws -> String?
    func save(_ value: String) throws
    func clear() throws
}
public struct BackendResponse: CustomStringConvertible {
    public let requestId: String?
    public let json: Data
    public var description: String { "BackendResponse([redacted])" }
}
private final class RejectRedirect: NSObject, URLSessionTaskDelegate {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) { completionHandler(nil) }
}
public final class BackendClient {
    private let config: GameBridgeConfig
    private let session: URLSession
    private let redirectGuard = RejectRedirect()
    public init(config: GameBridgeConfig, sessionConfiguration: URLSessionConfiguration = .default) throws {
        try config.validate()
        guard config.mode != .editorOffline else { throw SdkFailure("UNSUPPORTED_OPERATION") }
        self.config = config
        self.session = URLSession(configuration: sessionConfiguration, delegate: redirectGuard, delegateQueue: nil)
    }
    public func request(path: String, method: String, body: Data? = nil, accessToken: String? = nil,
                        developmentKey: String? = nil, idempotencyKey: String? = nil) async throws -> BackendResponse {
        guard path.hasPrefix("/v1/"), !path.contains("?"), !path.contains("#"), !path.contains("\\"), !path.contains(".."), !path.contains("%"),
              ["GET", "POST", "PUT", "DELETE"].contains(method),
              let base = config.backendBaseURL, var components = URLComponents(string: base) else { throw SdkFailure("INVALID_ARGUMENT") }
        if developmentKey != nil && (config.mode != .localMock || !["/v1/dev/auth", "/v1/dev/xcode-storekit/account", "/v1/dev/xcode-storekit/grant", "/v1/dev/xcode-storekit/wallet"].contains(path)) { throw SdkFailure("UNSUPPORTED_OPERATION") }
        if let idempotencyKey {
            guard ["/v1/purchases/verify", "/v1/purchases/apple/verify"].contains(path), let uuid = UUID(uuidString: idempotencyKey), uuid.uuidString.lowercased() == idempotencyKey else { throw SdkFailure("INVALID_ARGUMENT") }
        }
        components.path = path; components.query = nil; components.fragment = nil
        guard let url = components.url else { throw SdkFailure("INVALID_ARGUMENT") }
        var request = URLRequest(url: url, timeoutInterval: Double(config.requestTimeoutMs) / 1000)
        request.httpMethod = method; request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let accessToken { request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization") }
        if let developmentKey { request.setValue(developmentKey, forHTTPHeaderField: "X-Development-Key") }
        if let idempotencyKey { request.setValue(idempotencyKey, forHTTPHeaderField: "Idempotency-Key") }
        if let body { request.httpBody = body; request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        do {
            let (data, response) = try await session.data(for: request)
            guard let response = response as? HTTPURLResponse else { throw SdkFailure("NETWORK_UNAVAILABLE") }
            guard data.count <= 256 * 1024 else { throw SdkFailure("PAYLOAD_TOO_LARGE") }
            guard (200...299).contains(response.statusCode) else { throw Self.failure(status: response.statusCode, data: data) }
            guard let value = try? JSONSerialization.jsonObject(with: data), (value is [String: Any] || value is [Any]) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return BackendResponse(requestId: response.value(forHTTPHeaderField: "X-Request-Id"), json: data)
        } catch let error as SdkFailure { throw error }
        catch let error as URLError where error.code == .timedOut { throw SdkFailure("TIMEOUT", retryable: true) }
        catch let error as URLError where error.code == .cancelled { throw SdkFailure("CANCELED") }
        catch is CancellationError { throw SdkFailure("CANCELED") }
        catch { throw SdkFailure("NETWORK_UNAVAILABLE", retryable: true) }
    }
    private static func failure(status: Int, data: Data) -> SdkFailure {
        let candidate = (try? JSONSerialization.jsonObject(with: data) as? [String: Any])?["code"] as? String
        let allowed: Set<String>
        let fallback: String
        switch status {
        case 400: allowed = ["INVALID_ARGUMENT", "VERIFICATION_FAILED"]; fallback = "INVALID_ARGUMENT"
        case 401: allowed = ["AUTH_FAILED", "SESSION_EXPIRED"]; fallback = "SESSION_EXPIRED"
        case 403: allowed = ["PERMISSION_DENIED"]; fallback = "PERMISSION_DENIED"
        case 404: allowed = ["UNSUPPORTED_OPERATION", "PRODUCT_NOT_FOUND"]; fallback = "UNSUPPORTED_OPERATION"
        case 409: allowed = ["AUTH_REPLAY_DETECTED", "PURCHASE_ACCOUNT_MISMATCH", "IDEMPOTENCY_CONFLICT"]; fallback = "INTERNAL_ERROR"
        case 413: allowed = ["PAYLOAD_TOO_LARGE"]; fallback = "PAYLOAD_TOO_LARGE"
        case 429: allowed = ["BUSY"]; fallback = "BUSY"
        case 503: allowed = ["CONFIG_REQUIRED", "NETWORK_UNAVAILABLE"]; fallback = "NETWORK_UNAVAILABLE"
        case 500...599: allowed = []; fallback = "NETWORK_UNAVAILABLE"
        default: allowed = []; fallback = "INTERNAL_ERROR"
        }
        let code = candidate.flatMap { allowed.contains($0) ? $0 : nil } ?? fallback
        return SdkFailure(code, retryable: code == "BUSY" || code == "NETWORK_UNAVAILABLE")
    }
}
