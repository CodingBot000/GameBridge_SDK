import SwiftUI
import UIKit
import GameBridgeCore
import GameBridgeApple

@MainActor
final class AppleSandboxModel: ObservableObject {
    @Published var appId = ""
    @Published var backendURL = ""
    @Published var coinsStoreId = ""
    @Published var premiumStoreId = ""
    @Published private(set) var status = "Enter sandbox configuration."
    @Published private(set) var configured = false
    @Published private(set) var signedIn = false
    @Published private(set) var connected = false
    @Published private(set) var busy = false
    @Published private(set) var products: [StoreProduct] = []
    @Published private(set) var wallet: EntitlementSnapshot?
    private var auth: AppleAuthProvider?
    private var store: AppleStore?

    func configure() {
        perform {
            guard !self.configured else { throw SdkFailure("BUSY") }
            guard let window = UIApplication.shared.connectedScenes.compactMap({ $0 as? UIWindowScene }).flatMap(\.windows).first(where: \.isKeyWindow) else { throw SdkFailure("CONFIG_REQUIRED") }
            let config = GameBridgeConfig(appId: self.appId, mode: .platformSandbox, backendBaseURL: self.backendURL)
            let auth = try AppleAuthProvider.create(config: config, store: KeychainTokenStore(service: "com.gamebridge.sdk.sample.apple.session"), window: window)
            let store = try AppleStore(auth: auth, config: config, productIds: ["coins_100": self.coinsStoreId, "premium_unlock": self.premiumStoreId])
            self.auth = auth; self.store = store; self.configured = true; self.status = "Sandbox configured. Sign in to continue."
        }
    }
    func signIn() { perform { guard let auth = self.auth else { throw SdkFailure("CONFIG_REQUIRED") }; _ = try await auth.signIn(); self.signedIn = true; self.status = "Apple sign-in complete." } }
    func restoreSession() { perform { guard let auth = self.auth else { throw SdkFailure("CONFIG_REQUIRED") }; self.signedIn = try await auth.restore() != nil; self.status = self.signedIn ? "Session restored." : "No saved session." } }
    func connectStore() { perform { guard let store = self.store else { throw SdkFailure("CONFIG_REQUIRED") }; try await store.start(); self.connected = true; self.status = "Store connected." } }
    func load() { perform { guard let store = self.store else { throw SdkFailure("CONFIG_REQUIRED") }; self.products = try await store.products(); self.wallet = try await store.entitlements(); self.status = "Products and server balance loaded." } }
    func purchase(_ product: StoreProduct) { perform {
        guard let store = self.store else { throw SdkFailure("CONFIG_REQUIRED") }
        let result = try await store.purchase(productId: product.productId)
        if result.status == .purchased { self.wallet = try await store.entitlements() }
        self.status = "Purchase: \(String(describing: result.status))"
    } }
    func restorePurchases() { perform { guard let store = self.store else { throw SdkFailure("CONFIG_REQUIRED") }; try await store.restore(); self.wallet = try await store.entitlements(); self.status = "Restore requested." } }
    func signOut() { perform {
        guard let auth = self.auth else { throw SdkFailure("CONFIG_REQUIRED") }
        defer { self.store?.stop(); self.store = nil; self.auth = nil; self.configured = false; self.signedIn = false; self.connected = false; self.products = []; self.wallet = nil }
        try await auth.signOut(); self.status = "Signed out."
    } }
    private func perform(_ action: @escaping @MainActor () async throws -> Void) {
        guard !busy else { return }; busy = true
        Task {
            defer { busy = false }
            do { try await action() }
            catch is ConfigurationError { status = "CONFIG_REQUIRED" }
            catch let error as SdkFailure { status = error.nativeCode == "REVOCATION_UNCONFIRMED" ? "\(error.code) — local session cleared; server revoke unconfirmed" : error.code }
            catch { status = "INTERNAL_ERROR" }
        }
    }
}

struct AppleSandboxView: View {
    @ObservedObject var model: AppleSandboxModel
    var body: some View {
        Form {
            Section {
                Text("Apple Sandbox: use a configured test app and sandbox account.")
                TextField("App ID", text: $model.appId).textInputAutocapitalization(.never).autocorrectionDisabled().accessibilityIdentifier("appleAppId")
                TextField("HTTPS Backend URL", text: $model.backendURL).textInputAutocapitalization(.never).autocorrectionDisabled()
                TextField("Coins store product ID", text: $model.coinsStoreId).textInputAutocapitalization(.never).autocorrectionDisabled()
                TextField("Premium store product ID", text: $model.premiumStoreId).textInputAutocapitalization(.never).autocorrectionDisabled()
            }
            Section("Account") {
                Button("Sign in with Apple", action: model.signIn).disabled(model.busy || !model.configured || model.signedIn)
                Button("Restore session", action: model.restoreSession).disabled(model.busy || !model.configured || model.signedIn)
                Button("Sign out", action: model.signOut).disabled(model.busy || !model.configured)
            }
            Section("Store") {
                Button("Connect store", action: model.connectStore).disabled(model.busy || !model.signedIn || model.connected)
                Button("Load products and balance", action: model.load).disabled(model.busy || !model.connected)
                ForEach(model.products, id: \.productId) { product in
                    Button("\(product.title) — \(product.localizedPrice)") { model.purchase(product) }.disabled(model.busy || !model.connected)
                }
                Button("Restore purchases", action: model.restorePurchases).disabled(model.busy || !model.connected)
                Text("Coins: \(model.wallet?.coinBalance ?? "—"); premium: \(model.wallet?.premiumEnabled == true ? "yes" : "no")")
            }
        }
        .navigationTitle("Apple Sandbox")
        .toolbar { ToolbarItem(placement: .navigationBarTrailing) { Button("Configure", action: model.configure).disabled(model.busy || model.configured).accessibilityIdentifier("appleConfigure") } }
        .safeAreaInset(edge: .bottom) { Text(model.status).accessibilityIdentifier("appleStatus").frame(maxWidth: .infinity).padding().background(.regularMaterial) }
    }
}
