#if DEBUG
import SwiftUI
import Foundation
import StoreKitTest
import StoreKit
import GameBridgeCore
import GameBridgeApple

private final class RecoveryFaultProtocol: URLProtocol {
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let session = URLSession(configuration:.ephemeral)
        session.dataTask(with:request) { data,response,error in
            defer { session.finishTasksAndInvalidate() }
            if let error { self.client?.urlProtocol(self, didFailWithError:error); return }
            guard let response = response as? HTTPURLResponse, let data else { self.client?.urlProtocol(self, didFailWithError:URLError(.badServerResponse)); return }
            if self.request.url?.path == "/v1/dev/xcode-storekit/grant", response.statusCode == 200 {
                let failure = HTTPURLResponse(url:self.request.url!, statusCode:503, httpVersion:nil, headerFields:["Content-Type":"application/json"])!
                self.client?.urlProtocol(self, didReceive:failure, cacheStoragePolicy:.notAllowed)
                self.client?.urlProtocol(self, didLoad:Data(#"{"code":"NETWORK_UNAVAILABLE"}"#.utf8))
            } else {
                self.client?.urlProtocol(self, didReceive:response, cacheStoragePolicy:.notAllowed)
                self.client?.urlProtocol(self, didLoad:data)
            }
            self.client?.urlProtocolDidFinishLoading(self)
        }.resume()
    }
    override func stopLoading() {}
}

private final class CountingStore: TokenStore {
    private let backing: TokenStore
    var saves = 0; var clears = 0; var clearErrors = 0
    init(_ backing: TokenStore) { self.backing = backing }
    func load() throws -> String? { try backing.load() }
    func save(_ value: String) throws { saves += 1; try backing.save(value) }
    func clear() throws { clears += 1; do { try backing.clear() } catch { clearErrors += 1; throw error } }
}

private func makeTestSession(initializer: String) throws -> SKTestSession {
    if initializer == "url" {
        guard let configuration = Bundle.main.url(forResource: "GameBridge", withExtension: "storekit") else { throw SdkFailure("CONFIG_REQUIRED") }
        return try SKTestSession(contentsOf: configuration)
    }
    if initializer == "named" { return try SKTestSession(configurationFileNamed: "GameBridge") }
    throw SdkFailure("CONFIG_REQUIRED")
}

@main struct GameBridgeRecoveryHarnessApp: App {
    var body: some Scene { WindowGroup { Text("GameBridge local recovery test").task { await run() } } }
    @MainActor private func run() async {
        let env = ProcessInfo.processInfo.environment
        let phase = env["GAMEBRIDGE_PROCESS_TEST_PHASE"] ?? ""
        let statusURL = FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0].appendingPathComponent("gamebridge-recovery-status.json")
        func report(_ values: [String: Any]) { if let data = try? JSONSerialization.data(withJSONObject:values) { try? data.write(to:statusURL,options:.atomic) } }
        var stage = "configuration"
        func checkpoint(_ value: String) { stage = value; report(["phase":"running", "stage":value]) }
        var historyBefore = 0
        var unfinishedBefore = 0
        let pendingStore = CountingStore(KeychainTokenStore(service:"com.gamebridge.process-test.pending"))
        do {
            guard ["prepare", "recover"].contains(phase), let base = env["GAMEBRIDGE_PROCESS_TEST_BASE_URL"], base.hasPrefix("http://127.0.0.1:"),
                  let key = env["GAMEBRIDGE_PROCESS_TEST_AUTH_KEY"], key.count >= 32 else { throw SdkFailure("CONFIG_REQUIRED") }
            let initializer = env["GAMEBRIDGE_PROCESS_STOREKIT_INIT"] ?? "named"
            let execution = env["GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR"] ?? "main"
            checkpoint("storekit-session-create")
            let testSession: SKTestSession
            if execution == "background" {
                testSession = try await Task.detached { try makeTestSession(initializer: initializer) }.value
            } else if execution == "main" {
                testSession = try makeTestSession(initializer: initializer)
            } else { throw SdkFailure("CONFIG_REQUIRED") }
            checkpoint("storekit-session-configure")
            testSession.disableDialogs = true
            let network = URLSessionConfiguration.ephemeral
            if phase == "prepare" { network.protocolClasses = [RecoveryFaultProtocol.self] }
            let sessionStore = KeychainTokenStore(service:"com.gamebridge.process-test.session")
            checkpoint("client")
            let client = try LocalMockClient(config:GameBridgeConfig(appId:"gamebridge-sample", mode:.localMock, backendBaseURL:base, requestTimeoutMs:5000),
                                             store:sessionStore, developmentKey:key, sessionConfiguration:network)
            checkpoint("authentication")
            if phase == "prepare" { _ = try await client.signIn(subject:"A") }
            else { guard try await client.restore() != nil else { throw SdkFailure("SESSION_EXPIRED") } }
            checkpoint("store-init")
            let store = try await XcodeStoreKitSession(client:client, pendingStore:pendingStore)
            checkpoint("store-history")
            for await _ in Transaction.all { historyBefore += 1 }
            for await _ in Transaction.unfinished { unfinishedBefore += 1 }
            checkpoint("store-start")
            try await store.start()
            if phase == "prepare" {
                checkpoint("purchase")
                let purchase = try await store.purchase("coins_100")
                checkpoint("pending-assertion")
                guard purchase.status == .verificationPending, try pendingStore.load() != nil else { throw SdkFailure("INTERNAL_ERROR") }
                checkpoint("wallet")
                let wallet = try await store.wallet()
                guard wallet.coinBalance == "100" else { throw SdkFailure("INTERNAL_ERROR") }
                report(["phase":"pending", "balance":wallet.coinBalance, "pid":ProcessInfo.processInfo.processIdentifier])
                // Keep the process alive until the test runner terminates it.
            } else {
                checkpoint("recover-wallet")
                let wallet = try await store.wallet()
                checkpoint("recover-again")
                let remaining = try await store.recover(userInitiated:false)
                checkpoint("await-journal-cleanup")
                for _ in 0..<100 {
                    if try pendingStore.load() == nil { break }
                    try await Task.sleep(nanoseconds:100_000_000)
                }
                // Give any already queued duplicate StoreKit delivery time to run.
                try await Task.sleep(nanoseconds:1_000_000_000)
                stage = "recovery-assertion-\(wallet.coinBalance)-\(remaining.examinedCount)-\(try pendingStore.load() == nil)-\(pendingStore.saves)"
                guard wallet.coinBalance == "100", try pendingStore.load() == nil, remaining.examinedCount == 0, pendingStore.saves == 0 else { throw SdkFailure("INTERNAL_ERROR") }
                report(["phase":"recovered", "balance":wallet.coinBalance, "pid":ProcessInfo.processInfo.processIdentifier])
                store.stop(); try await client.signOut()
            }
        } catch let failure as SdkFailure { report(["phase":"failed", "code":failure.code, "stage":stage, "historyBefore":historyBefore, "unfinishedBefore":unfinishedBefore, "saves":pendingStore.saves, "clears":pendingStore.clears, "clearErrors":pendingStore.clearErrors]) }
        catch { report(["phase":"failed", "code":"INTERNAL_ERROR", "stage":stage, "errorType":String(reflecting:type(of:error)), "historyBefore":historyBefore, "unfinishedBefore":unfinishedBefore, "saves":pendingStore.saves, "clears":pendingStore.clears, "clearErrors":pendingStore.clearErrors]) }
    }
}
#endif
