import XCTest
import GameBridgeCore
@testable import GameBridgeUnityBridge

@MainActor final class ProviderSelectionTests: XCTestCase {
    private final class MemoryStore: TokenStore {
        var value: String?
        var unreadable = false
        func load() throws -> String? {
            if unreadable { throw SdkFailure("INTERNAL_ERROR") }
            return value
        }
        func save(_ value: String) throws { self.value = value }
        func clear() throws { value = nil }
    }

    private final class Apple: AppleAuthBridgeApi {
        let user = UserProfile(userId: "00000000-0000-4000-8000-000000000001", displayName: nil, provider: "APPLE")
        let storage: MemoryStore
        init(_ storage: MemoryStore) { self.storage = storage }
        var logoutFailure: SdkFailure?
        func signIn() async throws -> UserProfile { try storage.save("existing-opaque-session"); return user }
        func restore() async throws -> UserProfile? { try storage.load() == "existing-opaque-session" ? user : nil }
        func signOut() async throws {
            try storage.clear()
            if let logoutFailure { throw logoutFailure }
        }
        func close() {}
    }

    private let marker = MemoryStore()
    private let appleSession = MemoryStore()
    private lazy var apple = Apple(appleSession)

    private func router() -> PlatformAuthBridgeHandler {
        PlatformAuthBridgeHandler(apple: AppleAuthBridgeHandler { _, _, _ in self.apple },
                                  marker: marker, appleSessionStore: appleSession, factory: { _, _, _ in throw SdkFailure("UNSUPPORTED_PROVIDER") },
                                  emitter: { { _ in } })
    }

    private func initialize(_ handler: PlatformAuthBridgeHandler, _ app: String) async throws {
        _ = try await handler.invoke("sdk.initialize", payload: ["appId": app, "providerMode": "PLATFORM_SANDBOX",
                                                               "backendBaseUrl": "https://example.invalid", "requestTimeoutMs": 30000])
    }

    func testAppleLogoutAllowsAnotherScopeOnNextLaunch() async throws {
        let first = router()
        try await initialize(first, "a")
        _ = try await first.invoke("auth.signIn", payload: ["provider": "APPLE"])
        XCTAssertNotNil(marker.value)
        _ = try await first.invoke("auth.signOut", payload: [:])
        XCTAssertNil(marker.value)
        XCTAssertNil(appleSession.value)
        try await initialize(router(), "b")
    }

    private func legacyMarker(_ provider: String = "APPLE") -> String {
        "{\"appId\":\"a\",\"backend\":\"https://example.invalid\",\"provider\":\"" + provider + "\"}"
    }

    func testOrphanLegacyAppleSelectionCanChangeScope() async throws {
        marker.value = legacyMarker()
        try await initialize(router(), "b")
        XCTAssertNil(marker.value)
    }

    func testExistingSelectionRestoresWithinItsScope() async throws {
        marker.value = legacyMarker()
        appleSession.value = "existing-opaque-session"
        let current = router()
        try await initialize(current, "a")
        let restored = try await current.invoke("auth.restore", payload: [:]) as? [String: Any]
        XCTAssertEqual(restored?["signedIn"] as? Bool, true)
        XCTAssertEqual(marker.value, legacyMarker())
    }

    func testForeignOrUncertainSelectionIsPreserved() async throws {
        let cases: [(String, String?, Bool)] = [
            (legacyMarker(), "existing-opaque-session", false),
            (legacyMarker(), "{\"state\":\"refresh_pending\"}", false),
            (legacyMarker(), nil, true),
            (legacyMarker("GOOGLE"), nil, false),
            ("{}", nil, false)
        ]
        for (selection, session, unreadable) in cases {
            marker.value = selection
            appleSession.value = session
            appleSession.unreadable = unreadable
            do {
                try await initialize(router(), "b")
                XCTFail("expected binding rejection")
            } catch let error as SdkFailure {
                XCTAssertEqual(error.code, "SESSION_EXPIRED")
            }
            XCTAssertEqual(marker.value, selection)
            XCTAssertEqual(appleSession.value, session)
        }
    }

    func testUnconfirmedRevocationIsReturnedToCaller() async throws {
        let first = router()
        try await initialize(first, "a")
        _ = try await first.invoke("auth.signIn", payload: ["provider": "APPLE"])
        apple.logoutFailure = SdkFailure("NETWORK_UNAVAILABLE", nativeCode: "REVOCATION_UNCONFIRMED")
        do {
            _ = try await first.invoke("auth.signOut", payload: [:])
            XCTFail("expected revocation warning")
        } catch let error as SdkFailure {
            XCTAssertEqual(error.nativeCode, "REVOCATION_UNCONFIRMED")
            XCTAssertNil(appleSession.value)
            XCTAssertNotNil(marker.value)
        }
    }
}
