import XCTest

final class LocalMockSmokeTests: XCTestCase {
    private func reveal(_ element: XCUIElement, in app: XCUIApplication) {
        let window = app.windows.firstMatch
        for _ in 0..<10 {
            if element.exists {
                let frame = element.frame, bounds = window.frame
                if element.isHittable && frame.midY > bounds.minY + 100 && frame.midY < bounds.maxY - 150 { return }
                let downward = frame.midY < bounds.midY
                let start = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: downward ? 0.45 : 0.65))
                let end = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: downward ? 0.60 : 0.50))
                start.press(forDuration: 0.1, thenDragTo: end)
            } else {
                let start = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.65))
                let end = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.50))
                start.press(forDuration: 0.1, thenDragTo: end)
            }
        }
    }
    func testAppleSandboxScreenRejectsMissingConfiguration() {
        let app = XCUIApplication(); app.launch(); app.swipeUp()
        let sandbox = app.buttons["Apple Sandbox"]
        XCTAssertTrue(sandbox.waitForExistence(timeout: 10)); sandbox.tap()
        XCTAssertTrue(app.textFields["appleAppId"].waitForExistence(timeout: 5))
        let configure = app.buttons["appleConfigure"]
        XCTAssertTrue(configure.waitForExistence(timeout: 5)); configure.tap()
        let status = app.staticTexts["appleStatus"]
        reveal(status, in: app)
        expectation(for: NSPredicate(format: "label == %@", "CONFIG_REQUIRED"), evaluatedWith: status)
        waitForExpectations(timeout: 5)
    }
    func testMockLoginAndServerPurchase() throws {
        let app = XCUIApplication()
        app.launch()
        let key = app.secureTextFields["developmentKey"]
        XCTAssertTrue(key.waitForExistence(timeout: 10))
        key.tap()
        // Fixed, non-secret test-only value: the local server must be configured to match.
        key.typeText("local-test-key-0123456789-abcdef0123456789")
        if app.keyboards.buttons["done"].exists { app.keyboards.buttons["done"].tap() }
        else if app.keyboards.buttons["return"].exists { app.keyboards.buttons["return"].tap() }
        let initialize = app.buttons["initialize"]
        initialize.tap()
        let login = app.buttons["signIn"]
        if !login.isHittable {
            let from = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.75))
            let to = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.55))
            from.press(forDuration: 0.1, thenDragTo: to)
        }
        XCTAssertTrue(login.waitForExistence(timeout: 5)); login.tap()
        let loginStatus = app.staticTexts["status"]
        reveal(loginStatus, in: app)
        XCTAssertTrue(loginStatus.waitForExistence(timeout: 5))
        let signedIn = NSPredicate(format: "label BEGINSWITH %@", "Signed in:")
        expectation(for: signedIn, evaluatedWith: loginStatus)
        waitForExpectations(timeout: 10)
        let load = app.buttons["loadProducts"]
        if !load.isHittable { app.swipeUp() }
        XCTAssertTrue(load.waitForExistence(timeout: 5)); load.tap()
        let buy = app.buttons["buy_coins_100"]
        XCTAssertTrue(buy.waitForExistence(timeout: 10))
        if !buy.isHittable { app.swipeUp() }
        buy.tap()
        let status = app.staticTexts["status"]
        if !status.isHittable { app.swipeUp() }
        let granted = NSPredicate(format: "label CONTAINS %@", "GRANTED / PENDING")
        expectation(for: granted, evaluatedWith: status)
        waitForExpectations(timeout: 10)

        app.terminate(); app.launch()
        let restoredKey = app.secureTextFields["developmentKey"]
        XCTAssertTrue(restoredKey.waitForExistence(timeout: 10))
        restoredKey.tap(); restoredKey.typeText("local-test-key-0123456789-abcdef0123456789")
        if app.keyboards.buttons["done"].exists { app.keyboards.buttons["done"].tap() }
        else if app.keyboards.buttons["return"].exists { app.keyboards.buttons["return"].tap() }
        app.buttons["initialize"].tap()
        let restore = app.buttons["restore"]
        if !restore.isHittable {
            let from = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.75))
            let to = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.55))
            from.press(forDuration: 0.1, thenDragTo: to)
        }
        XCTAssertTrue(restore.waitForExistence(timeout: 5)); restore.tap()
        let signOut = app.buttons["signOut"]
        reveal(signOut, in: app)
        XCTAssertTrue(signOut.waitForExistence(timeout: 5))
        let restoredStatus = app.staticTexts["status"]
        if !restoredStatus.isHittable { app.swipeUp() }
        expectation(for: NSPredicate(format: "label BEGINSWITH %@", "Restored:"), evaluatedWith: restoredStatus)
        waitForExpectations(timeout: 10)
        reveal(signOut, in: app)
        expectation(for: NSPredicate(format: "enabled == 1"), evaluatedWith: signOut)
        waitForExpectations(timeout: 5)
        signOut.tap()
        let signedOut = app.staticTexts["status"]
        if !signedOut.isHittable { app.swipeUp() }
        expectation(for: NSPredicate(format: "label == %@", "Signed out"), evaluatedWith: signedOut)
        waitForExpectations(timeout: 10)
    }
}
