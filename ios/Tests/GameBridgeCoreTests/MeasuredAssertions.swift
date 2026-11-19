import Foundation
import XCTest

// Test-only helper-entry counts. XCTest pass/fail remains the framework's result.
private enum AssertionMeter {
    static let lock = NSLock()
    static var active: String?
    static var normal = 0
    static var expected = 0
    static func begin(_ test: String) {
        lock.lock(); defer { lock.unlock() }
        precondition(active == nil, "overlapping assertion scopes")
        active = test; normal = 0; expected = 0
    }
    static func hit(_ error: Bool = false) {
        lock.lock(); defer { lock.unlock() }
        precondition(active != nil, "assertion outside measured test scope")
        if error { expected += 1 } else { normal += 1 }
    }
    static func end() {
        lock.lock(); defer { lock.unlock() }
        let report: [String: Any] = ["platform":"swift-xctest", "test":active ?? "UNKNOWN",
            "normalAssertions":normal, "expectedErrorChecks":expected, "assertionsExecuted":normal + expected,
            "assertionOutcomes":"UNMEASURED", "scope":"counted test helper invocations"]
        let data = try! JSONSerialization.data(withJSONObject:report,options:[.sortedKeys])
        print("GB_ASSERTIONS_JSON " + String(decoding:data,as:UTF8.self)); active = nil
    }
}
class MeasuredTestCase: XCTestCase {
    override func setUp() { super.setUp(); AssertionMeter.begin(name) }
    override func tearDown() { AssertionMeter.end(); super.tearDown() }
}
func GBAssertEqual<T: Equatable>(_ lhs: @autoclosure () throws -> T, _ rhs: @autoclosure () throws -> T,
    _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(); XCTAssertEqual(try lhs(),try rhs(),message(),file:file,line:line)
}
func GBAssertTrue(_ value: @autoclosure () throws -> Bool, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(); XCTAssertTrue(try value(),message(),file:file,line:line)
}
func GBAssertFalse(_ value: @autoclosure () throws -> Bool, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(); XCTAssertFalse(try value(),message(),file:file,line:line)
}
func GBAssertNil<T>(_ value: @autoclosure () throws -> T?, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(); XCTAssertNil(try value(),message(),file:file,line:line)
}
func GBAssertNotNil<T>(_ value: @autoclosure () throws -> T?, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(); XCTAssertNotNil(try value(),message(),file:file,line:line)
}
func GBUnwrap<T>(_ value: @autoclosure () throws -> T?, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) throws -> T {
    AssertionMeter.hit(); return try XCTUnwrap(try value(),message(),file:file,line:line)
}
func GBAssertThrowsError<T>(_ value: @autoclosure () throws -> T, _ message: @autoclosure () -> String = "", file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(true); XCTAssertThrowsError(try value(),message(),file:file,line:line)
}
func GBFail(_ message: String, file: StaticString = #filePath, line: UInt = #line) {
    AssertionMeter.hit(true); XCTFail(message,file:file,line:line)
}
