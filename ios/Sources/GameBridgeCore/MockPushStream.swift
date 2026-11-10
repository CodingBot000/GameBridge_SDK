import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

/// Incremental bounded SSE parser; arbitrary fields never leave the decoder.
struct MockPushSSEParser {
    private var line = Data()
    private var event: String?
    private var data: String?
    mutating func append(_ byte: UInt8) -> PushPayload? {
        if byte != 10 {
            if byte != 13 { line.append(byte) }
            if line.count > BridgeProtocol.maxBytes { line.removeAll(); event = nil; data = nil }
            return nil
        }
        guard let text = String(data: line, encoding: .utf8) else { line.removeAll(); event = nil; data = nil; return nil }
        line.removeAll()
        if text.isEmpty {
            defer { event = nil; data = nil }
            guard event == "push", let data else { return nil }
            return MockPushEventDecoder.decode(Data(data.utf8))
        }
        if text.hasPrefix("event:") { event = String(text.dropFirst(6)).trimmingCharacters(in: .whitespaces) }
        else if text.hasPrefix("data:") {
            guard data == nil else { event = nil; data = nil; return nil }
            data = String(text.dropFirst(5)).trimmingCharacters(in: .whitespaces)
        }
        return nil
    }
}
private final class RejectMockPushRedirect: NSObject, URLSessionTaskDelegate {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) { completionHandler(nil) }
}
/// Local-only stream. Cancellation closes URLSession and no credential or raw event is logged.
final class MockPushStream {
    private let baseURL: URL
    private let installationId: UUID
    private let token: () async throws -> String?
    private let onPush: (PushPayload) -> Void
    private let configuration: URLSessionConfiguration
    private let delegate = RejectMockPushRedirect()
    private var task: Task<Void, Never>?
    private var session: URLSession?
    init(baseURL: URL, installationId: UUID, configuration: URLSessionConfiguration = .ephemeral, token: @escaping () async throws -> String?, onPush: @escaping (PushPayload) -> Void) {
        self.baseURL = baseURL; self.installationId = installationId; self.configuration = configuration; self.token = token; self.onPush = onPush
    }
    func start() {
        configuration.timeoutIntervalForRequest = 90; configuration.timeoutIntervalForResource = 86400
        let session = URLSession(configuration: configuration, delegate: delegate, delegateQueue: nil)
        self.session = session
        task = Task {
            var retry: UInt64 = 5
            while !Task.isCancelled {
                do {
                    guard let credential = try await token() else { break }
                    try Task.checkCancellation()
                    guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else { break }
                    components.path = "/v1/dev/push/stream"; components.queryItems = [URLQueryItem(name: "installationId", value: installationId.uuidString.lowercased())]
                    guard let url = components.url, url.scheme == baseURL.scheme, url.host == baseURL.host, url.port == baseURL.port else { break }
                    var request = URLRequest(url: url); request.setValue("Bearer \(credential)", forHTTPHeaderField: "Authorization")
                    request.setValue("text/event-stream, application/json", forHTTPHeaderField: "Accept")
                    #if canImport(Darwin)
                    let (bytes, response) = try await session.bytes(for: request)
                    if (response as? HTTPURLResponse)?.statusCode == 200 {
                        retry = 5; var parser = MockPushSSEParser()
                        for try await byte in bytes {
                            try Task.checkCancellation()
                            if let value = parser.append(byte) { onPush(value) }
                        }
                    }
                    #else
                    break // URLSession.AsyncBytes unavailable in FoundationNetworking.
                    #endif
                } catch is CancellationError { break }
                catch { /* Retry without exposing credentials or response data. */ }
                do { try await Task.sleep(nanoseconds: retry * 1_000_000_000) } catch { break }
                retry = min(retry * 2, 60)
            }
        }
    }
    func stop() { task?.cancel(); task = nil; session?.invalidateAndCancel(); session = nil }
}
