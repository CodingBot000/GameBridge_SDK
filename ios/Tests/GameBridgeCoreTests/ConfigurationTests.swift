import XCTest
@testable import GameBridgeCore

final class ConfigurationTests: XCTestCase {
    func testExplicitMockAndOfflineConfiguration() throws {
        try GameBridgeConfig(appId: "sample", mode: .editorOffline, backendBaseURL: nil).validate()
        try GameBridgeConfig(appId: "sample", mode: .localMock, backendBaseURL: "http://127.0.0.1:8080").validate()
    }

    func testSandboxRejectsCleartextAndCredentialsWithoutLeakingValue() {
        let secretURL = "http://user:secret@example.com"
        XCTAssertThrowsError(try GameBridgeConfig(appId: "sample", mode: .platformSandbox, backendBaseURL: secretURL).validate()) { error in
            XCTAssertEqual((error as? ConfigurationError)?.missingKeys, ["backendBaseUrl"])
            XCTAssertFalse(String(describing: error).contains("secret"))
        }
    }
}
