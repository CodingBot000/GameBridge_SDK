import SwiftUI
import UIKit
import GameBridgeCore

final class SampleAppDelegate: NSObject, UIApplicationDelegate {}

@main
struct GameBridgeSampleApp: App {
    @UIApplicationDelegateAdaptor(SampleAppDelegate.self) private var appDelegate
    @StateObject private var model = SampleModel()
    var body: some Scene { WindowGroup { SampleView(model: model) } }
}

@MainActor
final class SampleModel: ObservableObject {
    @Published var url = "http://127.0.0.1:18080"
    @Published var developmentKey = ""
    @Published private(set) var message = "LOCAL_MOCK — not connected"
    @Published private(set) var products: [LocalProduct] = []
    @Published private(set) var wallet: LocalWallet?
    @Published private(set) var busy = false
    @Published private(set) var initialized = false
    private var client: LocalMockClient?

    func initialize() {
        perform {
            let config = GameBridgeConfig(appId: "gamebridge-sample", mode: .localMock, backendBaseURL: self.url)
            self.client = try LocalMockClient(config: config, store: KeychainTokenStore(service: "com.gamebridge.sdk.sample.local.session"), developmentKey: self.developmentKey)
            self.initialized = true; self.message = "Initialized LOCAL_MOCK"
        }
    }
    func signIn() { perform { guard let client = self.client else { return }; let user = try await client.signIn(subject: "A"); self.message = "Signed in: \(user.userId)" } }
    func restore() { perform { guard let client = self.client else { return }; let user = try await client.restore(); self.message = user.map { "Restored: \($0.userId)" } ?? "No session" } }
    func load() { perform { guard let client = self.client else { return }; self.products = try await client.products(); self.wallet = try await client.wallet(); self.message = "Server state loaded" } }
    func purchase(_ product: LocalProduct) { perform {
        guard let client = self.client else { return }
        let result = try await client.purchase(productId: product.productId, transactionId: UUID(), attemptId: UUID())
        self.wallet = result.entitlements; self.message = "\(result.fulfillmentStatus) / \(result.finalizationStatus)"
    } }
    func signOut() { perform {
        guard let client = self.client else { return }
        defer { self.products = []; self.wallet = nil }
        try await client.signOut(); self.message = "Signed out"
    } }
    private func perform(_ action: @escaping @MainActor () async throws -> Void) {
        guard !busy else { return }; busy = true
        Task {
            defer { busy = false }
            do { try await action() }
            catch let error as SdkFailure { message = error.nativeCode == "REVOCATION_UNCONFIRMED" ? "\(error.code) — local session cleared; server revoke unconfirmed" : error.code }
            catch { message = "INTERNAL_ERROR" }
        }
    }
}

struct SampleView: View {
    @ObservedObject var model: SampleModel
    @FocusState private var keyFocused: Bool
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Text("LOCAL_MOCK — no real store purchase is performed.")
                    TextField("Backend URL", text: $model.url).textInputAutocapitalization(.never).autocorrectionDisabled().accessibilityIdentifier("backendURL")
                    SecureField("Development key", text: $model.developmentKey).textInputAutocapitalization(.never).autocorrectionDisabled().focused($keyFocused).submitLabel(.done).onSubmit { keyFocused = false }.accessibilityIdentifier("developmentKey")
                    Button("Initialize") { keyFocused = false; model.initialize() }.disabled(model.busy).accessibilityIdentifier("initialize")
                }
                Section("Session") {
                    Button("Mock login A", action: model.signIn).disabled(model.busy || !model.initialized).accessibilityIdentifier("signIn")
                    Button("Restore", action: model.restore).disabled(model.busy || !model.initialized).accessibilityIdentifier("restore")
                    Button("Sign out", action: model.signOut).disabled(model.busy || !model.initialized).accessibilityIdentifier("signOut")
                }
                Section("Mock store") {
                    Button("Load products & balance", action: model.load).disabled(model.busy || !model.initialized).accessibilityIdentifier("loadProducts")
                    ForEach(model.products) { product in
                        Button("Mock purchase \(product.productId)") { model.purchase(product) }.disabled(model.busy).accessibilityIdentifier("buy_\(product.productId)")
                    }
                    Text("Coins: \(model.wallet?.coinBalance ?? "—"); premium: \(model.wallet?.premiumEnabled == true ? "true" : "false")").accessibilityIdentifier("balance")
                }
                Section("Status") { Text(model.message).accessibilityIdentifier("status") }
            }.navigationTitle("GameBridge")
        }
    }
}
