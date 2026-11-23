import SwiftUI
import UIKit
import GameBridgeCore
import GameBridgeApple
import GoogleSignInSwift

final class GoogleOAuthHostDelegate: NSObject, UIApplicationDelegate {
    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        GameBridgeGoogleHost.handle(url)
    }
}

@MainActor final class GoogleOAuthHostModel: ObservableObject {
    @Published private(set) var status = "WAITING_USER — configure the iOS and Web OAuth clients"
    @Published private(set) var backendStatus = "HTTPS not checked"
    @Published private(set) var configured = false
    @Published private(set) var busy = false
    private var provider: SocialAuthProvider?
    private var task: Task<Void, Never>?
    let bundleID = Bundle.main.bundleIdentifier ?? ""
    let appID = Bundle.main.object(forInfoDictionaryKey: "GameBridgeAppID") as? String ?? ""
    let backendURL = Bundle.main.object(forInfoDictionaryKey: "GameBridgeBackendURL") as? String ?? ""

    private func configuration() throws -> GameBridgeConfig {
        let value = GameBridgeConfig(appId: appID, mode: .platformSandbox, backendBaseURL: backendURL)
        try value.validate(); return value
    }
    func checkConfiguration() {
        do {
            let ios = Bundle.main.object(forInfoDictionaryKey: "GIDClientID") as? String ?? ""
            let server = Bundle.main.object(forInfoDictionaryKey: "GIDServerClientID") as? String ?? ""
            guard !ios.isEmpty, !server.isEmpty, !ios.hasPrefix("REPLACE_"), !server.hasPrefix("REPLACE_"), ios != server else { throw SdkFailure("CONFIG_REQUIRED") }
            let value = try SocialAuthProvider.google(config: configuration(), store: KeychainTokenStore(service: "com.gamebridge.sdk.googleoauth.native"), clientId: ios, serverClientId: server)
            try value.validateSignInConfiguration()
            provider?.close(); provider = value; configured = true; status = "Native configuration ready; real OAuth NOT_RUN"
        } catch { configured = false; status = "WAITING_USER — client IDs / URL scheme / HTTPS configuration required" }
    }
    func checkBackend() async {
        do {
            let client = try BackendClient(config: configuration())
            _ = try await client.request(path: "/v1/config", method: "GET")
            backendStatus = "HTTPS/config PASS; OAuth NOT_RUN"
            print("GB_GOOGLE_PREP TLS PASS")
        } catch { backendStatus = "HTTPS/config unavailable — check server and trusted certificate"; print("GB_GOOGLE_PREP TLS FAIL") }
    }
    func preparationProbe() async {
        guard ProcessInfo.processInfo.environment["GAMEBRIDGE_GOOGLE_PREFLIGHT_ONLY"] == "1" else { return }
        checkConfiguration(); print("GB_GOOGLE_PREP AUTH_CONFIG " + (configured ? "READY" : "WAITING_USER"))
        await checkBackend() // Public config only. Never starts OAuth or exchanges a token.
    }
    private func perform(_ operation: @escaping @MainActor (SocialAuthProvider) async throws -> String) {
        guard configured, let provider, !busy else { return }
        busy = true
        task = Task {
            defer { busy = false; task = nil }
            do { status = try await operation(provider) }
            catch let error as SdkFailure { status = error.code }
            catch { status = "AUTH_OPERATION_FAILED" } // Never print underlying OAuth errors/tokens/URLs.
        }
    }
    func signIn() { perform { let user = try await $0.signIn(); return "Signed in SDK user: " + user.userId } }
    func restore() { perform { let user = try await $0.restore(); return user == nil ? "No SDK session" : "SDK session restored" } }
    func signOut() { perform { try await $0.signOut(); return "Signed out; Native SDK session cleared" } }
    func cancel() { task?.cancel() }
}

@main struct GameBridgeGoogleOAuthHost: App {
    @UIApplicationDelegateAdaptor(GoogleOAuthHostDelegate.self) private var delegate
    @StateObject private var model = GoogleOAuthHostModel()
    var body: some Scene {
        WindowGroup {
            Form {
                Section("Native Google OAuth test Host") {
                    Text(model.bundleID).accessibilityIdentifier("bundleID")
                    Text(model.appID)
                    Text(model.backendURL)
                    Text(model.status).accessibilityIdentifier("authStatus")
                    Text(model.backendStatus).accessibilityIdentifier("backendStatus")
                }
                Section("Preparation — no authentication") {
                    Button("Check configuration", action: model.checkConfiguration).disabled(model.busy)
                    Button("Check HTTPS Backend") { Task { await model.checkBackend() } }.disabled(model.busy)
                }
                Section("Manual account tests — next authorized step") {
                    GoogleSignInButton(action: model.signIn).disabled(!model.configured || model.busy)
                    Button("Cancel pending attempt", action: model.cancel).disabled(!model.busy)
                    Button("Restore SDK session", action: model.restore).disabled(!model.configured || model.busy)
                    Button("Sign out", action: model.signOut).disabled(!model.configured || model.busy)
                }
                Text("Preparation is not real OAuth PASS. Tokens stay Native; no purchase or push controls.")
            }
            .onOpenURL { _ = GameBridgeGoogleHost.handle($0) }
            .task { await model.preparationProbe() }
        }
    }
}
