import Foundation

public enum ProviderMode: String, Codable, Sendable {
    case editorOffline = "EDITOR_OFFLINE"
    case localMock = "LOCAL_MOCK"
    case xcodeStoreKit = "XCODE_STOREKIT"
    case platformSandbox = "PLATFORM_SANDBOX"
}

public struct ConfigurationError: Error, Equatable {
    public let missingKeys: [String]
}

public struct GameBridgeConfig: Equatable, Sendable {
    public let appId: String
    public let mode: ProviderMode
    public let backendBaseURL: String?
    public let requestTimeoutMs: Int

    public init(appId: String, mode: ProviderMode, backendBaseURL: String?, requestTimeoutMs: Int = 30_000) {
        self.appId = appId
        self.mode = mode
        self.backendBaseURL = backendBaseURL
        self.requestTimeoutMs = requestTimeoutMs
    }

    public func validate() throws {
        var missing: [String] = []
        if appId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { missing.append("appId") }
        if requestTimeoutMs <= 0 { missing.append("requestTimeoutMs") }
        if mode != .editorOffline {
            let url = backendBaseURL.flatMap { URLComponents(string: $0) }
            let validScheme = url?.scheme == "https" || (mode == .localMock && url?.scheme == "http")
            if !validScheme || url?.host?.isEmpty != false || url?.user != nil || url?.password != nil {
                missing.append("backendBaseUrl")
            }
        }
        if !missing.isEmpty { throw ConfigurationError(missingKeys: missing) }
    }
}
