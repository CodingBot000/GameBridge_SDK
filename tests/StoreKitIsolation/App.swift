import Foundation
import StoreKitTest
import UIKit

@main
final class IsolationApp: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    private var testSession: SKTestSession?
    func application(_ application: UIApplication, didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = UIViewController()
        window?.makeKeyAndVisible()
        if ProcessInfo.processInfo.environment["STOREKIT_ISOLATION_STANDALONE"] == "true" {
            DispatchQueue.main.async { self.runIsolation() }
        }
        return true
    }
    private func runIsolation() {
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        func checkpoint(_ phase: String, _ detail: String = "") {
            let data = try? JSONSerialization.data(withJSONObject: ["phase": phase, "detail": detail])
            try? data?.write(to: documents.appendingPathComponent("isolation-" + phase + ".json"), options: .atomic)
        }
        checkpoint("started")
        do {
            guard let url = Bundle.main.url(forResource: "Current", withExtension: "storekit") else {
                checkpoint("configuration-missing"); return
            }
            checkpoint("session-create-before")
            testSession = try SKTestSession(contentsOf: url)
            checkpoint("session-create-after")
        } catch {
            checkpoint("session-create-error", String(describing: type(of: error)))
        }
    }
}
