#if canImport(UIKit) && canImport(UserNotifications)
import Foundation
import UIKit
import UserNotifications
import GameBridgeCore

/// The host owns UIApplicationDelegate and UNUserNotificationCenterDelegate.
/// Forward callbacks to this adapter; it never replaces either delegate.
@MainActor
public final class ApplePushHostAdapter {
    public var onDeviceToken: ((Data) -> Void)?
    public var onRegistrationFailure: (() -> Void)?
    public var onNotification: ((PushPayload, Bool) -> Void)?

    public init() {}
    public func authorizationStatus() async -> UNAuthorizationStatus {
        await UNUserNotificationCenter.current().notificationSettings().authorizationStatus
    }
    /// Permission is requested only when explicitly called by the host.
    public func requestAuthorization() async throws -> Bool {
        try await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound])
    }
    public func registerForRemoteNotifications() {
        UIApplication.shared.registerForRemoteNotifications()
    }
    public func didRegister(deviceToken: Data) { onDeviceToken?(deviceToken) }
    public func didFailRegistration() { onRegistrationFailure?() }
    public func received(userInfo: [AnyHashable: Any], opened: Bool) {
        guard let payload = PushPayload(data: userInfo) else { return }
        onNotification?(payload, opened)
    }
}
#endif
