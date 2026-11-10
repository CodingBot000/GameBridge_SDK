import XCTest
import UIKit
import UserNotifications
import GameBridgeApple
@testable import GameBridgeSample

private final class ExistingNotificationDelegate: NSObject, UNUserNotificationCenterDelegate {}
final class PushHostTests: XCTestCase {
    @MainActor func testSyntheticHostCallbacksAndCompletion() {
        let center = UNUserNotificationCenter.current(); let original = center.delegate
        let existing = ExistingNotificationDelegate(); center.delegate = existing
        defer { center.delegate = original }
        let adapter = ApplePushHostAdapter()
        XCTAssertTrue(center.delegate === existing, "adapter must not replace host notification delegate")
        var token: Data?, opened: Bool?, messageId: String?
        adapter.onDeviceToken = { token = $0 }
        adapter.onNotification = { payload, wasOpened in messageId = payload.messageId; opened = wasOpened }
        adapter.didRegister(deviceToken: Data([1, 2, 3]))
        XCTAssertEqual(token, Data([1, 2, 3]))
        adapter.received(userInfo: ["messageId": "test", "route": "store", "url": "https://ignored.invalid"], opened: true)
        XCTAssertEqual(messageId, "test"); XCTAssertEqual(opened, true)
        messageId = nil
        adapter.received(userInfo: ["messageId": "bad", "route": "https://ignored.invalid"], opened: true)
        XCTAssertNil(messageId)
        var completed = false
        SampleAppDelegate().application(UIApplication.shared, didReceiveRemoteNotification: [:]) { result in
            completed = true; XCTAssertEqual(result, .noData)
        }
        XCTAssertTrue(completed)
        XCTAssertTrue(center.delegate === existing, "forwarded callback must preserve host delegate")
    }
}
