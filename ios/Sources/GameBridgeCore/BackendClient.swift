import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

public protocol TokenStore {
    func load() throws -> String?
    func save(_ value: String) throws
    func clear() throws
}
public struct BackendResponse {
    public let requestId: String?
    public let json: Data
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
    public func request(path: String, method: String, body: Data? = nil, accessToken: String? = nil) async throws -> BackendResponse {
        guard path.hasPrefix("/v1/"), !path.contains("?"), !path.contains("#"), !path.contains("\\"), !path.contains(".."), !path.contains("%"),
              ["GET", "POST", "PUT", "DELETE"].contains(method),
              let base = config.backendBaseURL, var components = URLComponents(string: base) else { throw SdkFailure("INVALID_ARGUMENT") }
        components.path = path; components.query = nil; components.fragment = nil
        guard let url = components.url else { throw SdkFailure("INVALID_ARGUMENT") }
        var request = URLRequest(url: url, timeoutInterval: Double(config.requestTimeoutMs) / 1000)
        request.httpMethod = method; request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let accessToken { request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization") }
        if let body { request.httpBody = body; request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        do {
            let (data, response) = try await session.data(for: request)
            guard let response = response as? HTTPURLResponse else { throw SdkFailure("NETWORK_UNAVAILABLE") }
            if response.statusCode == 401 { throw SdkFailure("SESSION_EXPIRED") }
            guard (200...299).contains(response.statusCode) else { throw SdkFailure(response.statusCode >= 500 ? "NETWORK_UNAVAILABLE" : "INTERNAL_ERROR") }
            guard data.count <= 256 * 1024 else { throw SdkFailure("PAYLOAD_TOO_LARGE") }
            guard let value = try? JSONSerialization.jsonObject(with: data), value is [String: Any] else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
            return BackendResponse(requestId: response.value(forHTTPHeaderField: "X-Request-Id"), json: data)
        } catch let error as SdkFailure { throw error }
        catch let error as URLError where error.code == .timedOut { throw SdkFailure("TIMEOUT") }
        catch let error as URLError where error.code == .cancelled { throw SdkFailure("CANCELED") }
        catch is CancellationError { throw SdkFailure("CANCELED") }
        catch { throw SdkFailure("NETWORK_UNAVAILABLE") }
    }
}
