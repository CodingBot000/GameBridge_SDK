import Foundation
import XCTest
@testable import GameBridgeCore
@testable import GameBridgeApple

private final class SocialProtocol:URLProtocol {
    static var meUnauthorized=false
    static var requests=[String]()
    static var wrongUser=false
    static var nonce=""
    static let user="11111111-1111-4111-8111-111111111111"
    override class func canInit(with request:URLRequest)->Bool {true}
    override class func canonicalRequest(for request:URLRequest)->URLRequest {request}
    override func startLoading() {
        let path=request.url!.path;Self.requests.append(path)
        var status=200;var body:[String:Any]
        if path.hasSuffix("challenges") {body=["challengeId":"22222222-2222-4222-8222-222222222222","nonce":"server-nonce","expiresAt":"2035-01-01T00:00:00Z"]}
        else if path.hasSuffix("exchange") || path.hasSuffix("refresh") {
            if path.hasSuffix("refresh") {Self.meUnauthorized=false}
            body=["accessToken":"synthetic-native-access","refreshToken":"synthetic-native-refresh","userId":Self.user,"expiresAt":"2035-01-01T00:00:00Z"]
        } else if path=="/v1/me" {
            if Self.meUnauthorized {status=401;body=["code":"SESSION_EXPIRED"]}
            else {body=["userId":Self.wrongUser ? "33333333-3333-4333-8333-333333333333":Self.user,"displayName":"Test"]}
        } else {body=["signedOut":true]}
        let response=HTTPURLResponse(url:request.url!,statusCode:status,httpVersion:nil,headerFields:nil)!
        client?.urlProtocol(self,didReceive:response,cacheStoragePolicy:.notAllowed);client?.urlProtocol(self,didLoad:try! JSONSerialization.data(withJSONObject:body));client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
private final class SocialStore:TokenStore {var value:String?;func load()throws->String?{value};func save(_ value:String)throws{self.value=value};func clear()throws{value=nil}}
@MainActor private final class SocialGateway:SocialCredentialGateway {
    var kind="ID_TOKEN";var canceled=false;var fail=false;var blocked=false;var suspended:CheckedContinuation<SocialCredential,Error>?
    var challengeProofType:String {kind}
    func authorize(nonce:String)async throws->SocialCredential {SocialProtocol.nonce=nonce;if blocked {return try await withCheckedThrowingContinuation {suspended=$0}};if fail{throw SdkFailure("CANCELED")};return SocialCredential(value:"synthetic-provider-proof",proofType:kind)}
    func cancel(){canceled=true};func logout(){}
}
@MainActor final class SocialAuthProviderTests:XCTestCase {
    private func make(_ store:SocialStore,_ gateway:SocialGateway,app:String="test",binding:String="ios|server",name:String="GOOGLE")throws->SocialAuthProvider {
        let configuration=URLSessionConfiguration.ephemeral;configuration.protocolClasses=[SocialProtocol.self]
        return try SocialAuthProvider(config:GameBridgeConfig(appId:app,mode:.platformSandbox,backendBaseURL:"https://backend.invalid"),provider:name,settingsBinding:binding,store:store,gateway:gateway,sessionConfiguration:configuration)
    }
    override func setUp(){SocialProtocol.requests=[];SocialProtocol.meUnauthorized=false;SocialProtocol.wrongUser=false;SocialProtocol.nonce=""}
    func testNonceAndOpaqueSessionStayNativeAndRestoreRefreshLogout()async throws {
        let store=SocialStore();let gateway=SocialGateway();let provider=try make(store,gateway)
        let profile=try await provider.signIn();XCTAssertEqual(profile.provider,"GOOGLE");XCTAssertEqual(SocialProtocol.nonce,"server-nonce")
        XCTAssertFalse(store.value!.contains("synthetic-provider-proof"));XCTAssertFalse(String(describing:profile).contains("synthetic-native"))
        SocialProtocol.meUnauthorized=true;let restored=try await provider.restore();XCTAssertEqual(restored?.userId,SocialProtocol.user)
        XCTAssertEqual(SocialProtocol.requests.filter{$0=="/v1/auth/refresh"}.count,1)
        try await provider.signOut();XCTAssertNil(store.value);XCTAssertTrue(gateway.canceled)
    }
    func testWrongProfileNeverPersistsAndCancelDoesNotExchange()async throws {
        let store=SocialStore();let gateway=SocialGateway();let provider=try make(store,gateway)
        SocialProtocol.wrongUser=true
        do {_ = try await provider.signIn();XCTFail("mismatch")} catch let error as SdkFailure {XCTAssertEqual(error.code,"AUTH_FAILED")}
        XCTAssertNil(store.value)
        SocialProtocol.requests=[];gateway.fail=true
        do {_ = try await provider.signIn();XCTFail("cancel")} catch let error as SdkFailure {XCTAssertEqual(error.code,"CANCELED")}
        XCTAssertFalse(SocialProtocol.requests.contains("/v1/auth/exchange"));XCTAssertNil(store.value)
    }
    func testConfigurationAndProviderStorageDoNotCrossAppOrSettings()async throws {
        let store=SocialStore();let gateway=SocialGateway();_ = try await make(store,gateway).signIn()
        for changed in [try make(store,gateway,app:"other"),try make(store,gateway,binding:"different") ] {
            do {_ = try await changed.restore();XCTFail("scope") } catch let error as SdkFailure {XCTAssertEqual(error.code,"SESSION_EXPIRED")}
        }
        XCTAssertNotNil(store.value)
    }
    func testDuplicateLoginAndLateCredentialAfterCloseCannotCreateSession()async throws {
        let store=SocialStore();let gateway=SocialGateway();gateway.blocked=true;let provider=try make(store,gateway)
        let task=Task {try await provider.signIn()}
        for _ in 0..<1000 {if gateway.suspended != nil {break};try await Task.sleep(nanoseconds:1_000_000)}
        XCTAssertNotNil(gateway.suspended)
        do {_ = try await provider.signIn();XCTFail("duplicate")} catch let error as SdkFailure {XCTAssertEqual(error.code,"BUSY")}
        provider.close()
        gateway.suspended?.resume(returning:SocialCredential(value:"late-google-id-token",proofType:"ID_TOKEN"));gateway.suspended=nil
        do {_ = try await task.value;XCTFail("late")} catch let error as SdkFailure {XCTAssertEqual(error.code,"CANCELED")}
        XCTAssertNil(store.value);XCTAssertFalse(SocialProtocol.requests.contains("/v1/auth/exchange"))
    }
    func testFacebookKindsAndProviderMismatchAreNotSilentlyConverted()async throws {
        for kind in ["FACEBOOK_ACCESS_TOKEN","FACEBOOK_LIMITED_ID_TOKEN"] {
            let store=SocialStore();let gateway=SocialGateway();gateway.kind=kind
            let profile=try await make(store,gateway,binding:"fb123",name:"FACEBOOK").signIn()
            XCTAssertEqual(profile.provider,"FACEBOOK");XCTAssertFalse(store.value!.contains("synthetic-provider-proof"))
        }
        let store=SocialStore();let gateway=SocialGateway();gateway.kind="FACEBOOK_ACCESS_TOKEN"
        do {_ = try await make(store,gateway).signIn();XCTFail("wrong provider kind")} catch let error as SdkFailure {XCTAssertEqual(error.code,"AUTH_FAILED")}
        XCTAssertNil(store.value)
    }
    func testRefreshPendingLogoutClearsLocallyAndReportsUnconfirmed()async throws {
        let store=SocialStore();store.value="{\"state\":\"refresh_pending\"}"
        do {try await make(store,SocialGateway()).signOut();XCTFail("warning")} catch let error as SdkFailure {XCTAssertEqual(error.nativeCode,"REVOCATION_UNCONFIRMED")}
        XCTAssertNil(store.value)
    }
}
