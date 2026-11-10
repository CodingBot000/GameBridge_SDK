import Foundation

public struct ServiceSettings: Equatable {
    public let revision: String
    public let maintenanceEnabled: Bool
    public let message: String?
    public let expiresAt: Date
    public init(revision: String, maintenanceEnabled: Bool, message: String?, expiresAt: Date) {
        self.revision = revision; self.maintenanceEnabled = maintenanceEnabled; self.message = message; self.expiresAt = expiresAt
    }
}
public enum ConfigurationSource { case remote, cache }
public struct EffectiveServiceSettings { public let settings: ServiceSettings; public let source: ConfigurationSource }
public actor ServiceConfigurationRepository {
    private let fetch: () async throws -> ServiceSettings
    private let now: () -> Date
    private var cached: ServiceSettings?
    private var flight: (id: UUID, task: Task<ServiceSettings, Error>)?
    public init(fetch: @escaping () async throws -> ServiceSettings, now: @escaping () -> Date = Date.init) { self.fetch = fetch; self.now = now }
    public func current() async throws -> EffectiveServiceSettings? {
        try Task.checkCancellation()
        let current: (id: UUID, task: Task<ServiceSettings, Error>)
        if let existing = flight { current = existing }
        else {
            let fetch = self.fetch
            current = (UUID(), Task { try await fetch() })
            flight = current
        }
        do {
            let value = try await current.task.value
            let ownsFlight = flight?.id == current.id
            if ownsFlight {
                flight = nil
                if !value.revision.isEmpty && value.expiresAt > now() { cached = value }
            }
            try Task.checkCancellation()
            if ownsFlight && !value.revision.isEmpty && value.expiresAt > now() { return EffectiveServiceSettings(settings: value, source: .remote) }
        } catch is CancellationError {
            if flight?.id == current.id { flight = nil }
            throw CancellationError()
        } catch let error as SdkFailure where error.code == "CANCELED" {
            if flight?.id == current.id { flight = nil }
            throw CancellationError()
        } catch {
            if flight?.id == current.id { flight = nil }
            /* Offline: only an unexpired known cache can be used. */
        }
        if let cached, cached.expiresAt > now() { return EffectiveServiceSettings(settings: cached, source: .cache) }
        return nil
    }
}
public func backendServiceConfiguration(_ client: BackendClient) -> ServiceConfigurationRepository {
    ServiceConfigurationRepository {
        struct Wire: Decodable { let revision: String; let maintenanceEnabled: Bool; let message: String?; let expiresAt: String? }
        let response = try await client.request(path: "/v1/config", method: "GET")
        let wire = try JSONDecoder().decode(Wire.self, from: response.json)
        guard let text = wire.expiresAt else { throw SdkFailure("CONFIG_REQUIRED") }
        let formatter = ISO8601DateFormatter(); formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let date = formatter.date(from: text) ?? ISO8601DateFormatter().date(from: text) else { throw SdkFailure("CONFIG_REQUIRED") }
        return ServiceSettings(revision: wire.revision, maintenanceEnabled: wire.maintenanceEnabled, message: wire.message, expiresAt: date)
    }
}
