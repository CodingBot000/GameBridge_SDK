import XCTest

final class LocalMockSmokeTests: XCTestCase {
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
        if !signOut.isHittable { app.swipeUp() }
        XCTAssertTrue(signOut.waitForExistence(timeout: 5))
        let restoredStatus = app.staticTexts["status"]
        if !restoredStatus.isHittable { app.swipeUp() }
        expectation(for: NSPredicate(format: "label BEGINSWITH %@", "Restored:"), evaluatedWith: restoredStatus)
        waitForExpectations(timeout: 10)
        if !signOut.isHittable { app.swipeDown() }
        signOut.tap()
        let signedOut = app.staticTexts["status"]
        if !signedOut.isHittable { app.swipeUp() }
        expectation(for: NSPredicate(format: "label == %@", "Signed out"), evaluatedWith: signedOut)
        waitForExpectations(timeout: 10)
    }
}
