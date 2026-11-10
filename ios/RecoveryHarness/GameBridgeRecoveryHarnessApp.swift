#if DEBUG
import SwiftUI
import Foundation
import StoreKitTest
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

@main struct GameBridgeRecoveryHarnessApp: App {
    var body: some Scene { WindowGroup { Text("GameBridge local recovery test").task { await run() } } }
    @MainActor private func run() async {
        let env = ProcessInfo.processInfo.environment
        let phase = env["GAMEBRIDGE_PROCESS_TEST_PHASE"] ?? ""
        let statusURL = FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0].appendingPathComponent("gamebridge-recovery-status.json")
        func report(_ values: [String: Any]) { if let data = try? JSONSerialization.data(withJSONObject:values) { try? data.write(to:statusURL,options:.atomic) } }
        var stage = "configuration"
        do {
            guard ["prepare", "recover"].contains(phase), let base = env["GAMEBRIDGE_PROCESS_TEST_BASE_URL"], base.hasPrefix("http://127.0.0.1:"),
                  let key = env["GAMEBRIDGE_PROCESS_TEST_AUTH_KEY"], key.count >= 32 else { throw SdkFailure("CONFIG_REQUIRED") }
            stage = "storekit-session"
            let testSession = try SKTestSession(configurationFileNamed:"GameBridge"); testSession.disableDialogs = true
            let network = URLSessionConfiguration.ephemeral
            if phase == "prepare" { network.protocolClasses = [RecoveryFaultProtocol.self] }
            let sessionStore = KeychainTokenStore(service:"com.gamebridge.process-test.session")
            let pendingStore = KeychainTokenStore(service:"com.gamebridge.process-test.pending")
            stage = "client"
            let client = try LocalMockClient(config:GameBridgeConfig(appId:"gamebridge-sample", mode:.localMock, backendBaseURL:base, requestTimeoutMs:5000),
                                             store:sessionStore, developmentKey:key, sessionConfiguration:network)
            stage = "authentication"
            if phase == "prepare" { _ = try await client.signIn(subject:"A") }
            else { guard try await client.restore() != nil else { throw SdkFailure("SESSION_EXPIRED") } }
            stage = "store-init"
            let store = try await XcodeStoreKitSession(client:client, pendingStore:pendingStore)
            stage = "store-start"
            try await store.start()
            if phase == "prepare" {
                stage = "purchase"
                let purchase = try await store.purchase("coins_100")
                stage = "pending-assertion"
                guard purchase.status == .verificationPending, try pendingStore.load() != nil else { throw SdkFailure("INTERNAL_ERROR") }
                stage = "wallet"
                let wallet = try await store.wallet()
                guard wallet.coinBalance == "100" else { throw SdkFailure("INTERNAL_ERROR") }
                report(["phase":"pending", "balance":wallet.coinBalance, "pid":ProcessInfo.processInfo.processIdentifier])
                // Keep the process alive until the test runner terminates it.
            } else {
                stage = "recover-wallet"
                let wallet = try await store.wallet()
                stage = "recover-again"
                let remaining = try await store.recover(userInitiated:false)
                stage = "recovery-assertion-\(wallet.coinBalance)-\(remaining.examinedCount)-\(try pendingStore.load() == nil)"
                guard wallet.coinBalance == "100", try pendingStore.load() == nil, remaining.examinedCount == 0 else { throw SdkFailure("INTERNAL_ERROR") }
                report(["phase":"recovered", "balance":wallet.coinBalance, "pid":ProcessInfo.processInfo.processIdentifier])
                store.stop(); try await client.signOut()
            }
        } catch let failure as SdkFailure { report(["phase":"failed", "code":failure.code, "stage":stage]) }
        catch { report(["phase":"failed", "code":"INTERNAL_ERROR", "stage":stage, "errorType":String(reflecting:type(of:error))]) }
    }
}
#endif
