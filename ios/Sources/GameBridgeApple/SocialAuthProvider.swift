import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

struct SocialCredential: CustomStringConvertible {
    let value: String
    let proofType: String
    var description: String { "SocialCredential([redacted])" }
}
@MainActor protocol SocialCredentialGateway: AnyObject {
    var challengeProofType:String {get}
    func preflight() throws
    func authorize(nonce: String) async throws -> SocialCredential
    func cancel()
    func logout()
}
extension SocialCredentialGateway {var challengeProofType:String {"ID_TOKEN"};func preflight() throws {}}
struct SocialChallenge: Decodable { let challengeId, nonce, expiresAt: String }
private struct SocialWireSession: Codable { let accessToken, refreshToken, expiresAt, userId: String }
private struct SocialStoredSession: Codable {
    let session: SocialWireSession
    let appId, mode, backend, provider, settingsBinding: String
}

/// Native-only third-party credential -> existing GameBridge session. Provider tokens are not persisted here.
@MainActor public final class SocialAuthProvider: BackendSessionAccess {
    private let config: GameBridgeConfig
    private let provider: String
    private let binding: String
    private let store: TokenStore
    private let gateway: SocialCredentialGateway
    private let http: BackendClient
    let uiGate = AppleUiGate()
    private(set) var sessionGeneration = 0
    private var closed=false
    private var current: SocialWireSession?
    private var refreshFlight: (UUID, Task<SocialWireSession, Error>)?
    init(config: GameBridgeConfig, provider: String, settingsBinding: String, store: TokenStore,
         gateway: SocialCredentialGateway, sessionConfiguration: URLSessionConfiguration = .default) throws {
        guard config.mode == .platformSandbox, ["GOOGLE", "FACEBOOK"].contains(provider), !settingsBinding.isEmpty else { throw SdkFailure("CONFIG_REQUIRED") }
        self.config=config; self.provider=provider; binding=settingsBinding; self.store=store; self.gateway=gateway
        http=try BackendClient(config:config,sessionConfiguration:sessionConfiguration)
    }
    func usesConfiguration(_ value: GameBridgeConfig) -> Bool { config==value }
    private func encode(_ value: Any) throws -> Data { try JSONSerialization.data(withJSONObject:value) }
    private func decode<T: Decodable>(_ type: T.Type, _ data: Data) throws -> T {
        guard let value=try? JSONDecoder().decode(type,from:data) else { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }; return value
    }
    private func valid(_ value: SocialWireSession) -> Bool {
        UUID(uuidString:value.userId) != nil && !value.accessToken.isEmpty && !value.refreshToken.isEmpty && value.expiresAt.hasSuffix("Z") &&
        (ISO8601DateFormatter().date(from:value.expiresAt) != nil || {let f=ISO8601DateFormatter();f.formatOptions=[.withInternetDateTime,.withFractionalSeconds];return f.date(from:value.expiresAt) != nil}())
    }
    public func validateSignInConfiguration() throws {try gateway.preflight()}
    public func signIn() async throws -> UserProfile {
        try gateway.preflight()
        guard !closed else {throw SdkFailure("CANCELED")}
        try uiGate.acquire(); defer { uiGate.release() }
        sessionGeneration += 1; let epoch=sessionGeneration
        if refreshFlight != nil { current=nil }; refreshFlight?.1.cancel(); refreshFlight=nil
        let challenge=try decode(SocialChallenge.self,try await http.request(path:"/v1/auth/challenges",method:"POST",body:encode(["appId":config.appId,"provider":provider,"proofType":gateway.challengeProofType])).json)
        let dateParser=ISO8601DateFormatter(); dateParser.formatOptions=[.withInternetDateTime,.withFractionalSeconds]
        let expiry=dateParser.date(from:challenge.expiresAt) ?? ISO8601DateFormatter().date(from:challenge.expiresAt)
        guard UUID(uuidString:challenge.challengeId) != nil, !challenge.nonce.isEmpty, let expiry, expiry>Date() else { throw SdkFailure("AUTH_FAILED") }
        guard !closed,epoch==sessionGeneration,!Task.isCancelled else {throw SdkFailure("CANCELED")}
        let credential=try await gateway.authorize(nonce:challenge.nonce)
        guard !Task.isCancelled else { throw SdkFailure("CANCELED") }
        guard !closed,epoch==sessionGeneration, !credential.value.isEmpty else { throw SdkFailure("CANCELED") }
        guard (provider=="GOOGLE" && credential.proofType=="ID_TOKEN") || (provider=="FACEBOOK" && ["FACEBOOK_ACCESS_TOKEN","FACEBOOK_LIMITED_ID_TOKEN"].contains(credential.proofType)) else {throw SdkFailure("AUTH_FAILED")}
        var body:[String:Any] = ["challengeId":challenge.challengeId,"provider":provider]
        if credential.proofType=="ID_TOKEN" { body["idToken"]=credential.value }
        else { body["proofType"]=credential.proofType;body[credential.proofType=="FACEBOOK_ACCESS_TOKEN" ? "accessToken":"idToken"]=credential.value }
        let value=try decode(SocialWireSession.self,try await http.request(path:"/v1/auth/exchange",method:"POST",body:encode(body)).json)
        guard valid(value) else { throw SdkFailure("AUTH_FAILED") }
        let profile=try await profile(value)
        guard !closed,epoch==sessionGeneration, !Task.isCancelled else { throw SdkFailure("CANCELED") }
        try persist(value);current=value;return profile
    }
    private func profile(_ session:SocialWireSession) async throws -> UserProfile {
        struct Me:Decodable {let userId:String;let displayName:String?}
        let me=try decode(Me.self,try await http.request(path:"/v1/me",method:"GET",accessToken:session.accessToken).json)
        guard me.userId==session.userId else { throw SdkFailure("AUTH_FAILED") }
        return UserProfile(userId:me.userId,displayName:me.displayName,provider:provider)
    }
    private func load() throws -> SocialWireSession? {
        if let current { return current };guard let raw=try store.load() else {return nil}
        guard let stored=try? JSONDecoder().decode(SocialStoredSession.self,from:Data(raw.utf8)),stored.appId==config.appId,
              stored.mode==config.mode.rawValue,stored.backend==config.backendBaseURL,stored.provider==provider,stored.settingsBinding==binding,valid(stored.session) else {throw SdkFailure("SESSION_EXPIRED")}
        current=stored.session;return stored.session
    }
    private func persist(_ session:SocialWireSession) throws {
        let stored=SocialStoredSession(session:session,appId:config.appId,mode:config.mode.rawValue,backend:config.backendBaseURL!,provider:provider,settingsBinding:binding)
        try store.save(String(decoding:JSONEncoder().encode(stored),as:UTF8.self))
    }
    private func refresh(_ old:SocialWireSession,epoch:Int) async throws -> SocialWireSession {
        guard !closed,epoch==sessionGeneration else {throw SdkFailure("CANCELED")}
        if let current,current.accessToken != old.accessToken {return current}
        let flight:(UUID,Task<SocialWireSession,Error>)
        if let existing=refreshFlight {flight=existing}
        else {
            try store.save("{\"state\":\"refresh_pending\"}")
            flight=(UUID(),Task {
                let value=try self.decode(SocialWireSession.self,try await self.http.request(path:"/v1/auth/refresh",method:"POST",body:self.encode(["refreshToken":old.refreshToken])).json)
                guard self.valid(value),value.userId==old.userId else {throw SdkFailure("AUTH_FAILED")}
                _ = try await self.profile(value);return value
            });refreshFlight=flight
        }
        do {
            let value=try await flight.1.value
            guard !closed,epoch==sessionGeneration else {throw SdkFailure("CANCELED")}
            if refreshFlight?.0==flight.0 {try persist(value);current=value;refreshFlight=nil}
            return value
        } catch {
            if epoch==sessionGeneration,refreshFlight?.0==flight.0 {current=nil;refreshFlight=nil}
            throw error
        }
    }
    public func restore() async throws -> UserProfile? { try await withBackendSession { _ in guard let value=self.current else {throw SdkFailure("SESSION_EXPIRED")};return try await self.profile(value) } }
    func withBackendSession<T>(_ action:(BackendAccountSession) async throws -> T) async throws -> T? {
        guard !closed else {throw SdkFailure("CANCELED")}
        guard let value=try load() else {return nil};let epoch=sessionGeneration
        do {
            let result=try await action(BackendAccountSession(accessToken:value.accessToken,userId:value.userId))
            guard !closed,epoch==sessionGeneration else {throw SdkFailure("CANCELED")};return result
        } catch let error as SdkFailure where error.code=="SESSION_EXPIRED" {
            let value=try await refresh(value,epoch:epoch)
            let result=try await action(BackendAccountSession(accessToken:value.accessToken,userId:value.userId))
            guard !closed,epoch==sessionGeneration else {throw SdkFailure("CANCELED")};return result
        }
    }
    public func signOut() async throws {
        let pending=try store.load()=="{\"state\":\"refresh_pending\"}"
        let value=pending ? nil : try load();sessionGeneration += 1;refreshFlight?.1.cancel();refreshFlight=nil;current=nil
        gateway.cancel();gateway.logout();try store.clear()
        if pending {throw SdkFailure("SESSION_EXPIRED",nativeCode:"REVOCATION_UNCONFIRMED")}
        if let value {
            do { _ = try await http.request(path:"/v1/auth/logout",method:"POST",accessToken:value.accessToken) }
            catch let error as SdkFailure where error.code=="SESSION_EXPIRED" {
                do { _ = try await http.request(path:"/v1/auth/logout",method:"POST",body:encode(["refreshToken":value.refreshToken])) }
                catch { throw SdkFailure("NETWORK_UNAVAILABLE",nativeCode:"REVOCATION_UNCONFIRMED",retryable:true) }
            } catch {throw SdkFailure("NETWORK_UNAVAILABLE",nativeCode:"REVOCATION_UNCONFIRMED",retryable:true)}
        }
    }
    public func close() {closed=true;sessionGeneration += 1;refreshFlight?.1.cancel();refreshFlight=nil;current=nil;gateway.cancel()}
    public func storeSession() throws -> AppleStoreSession {try AppleStoreSession(access:self,config:config)}
    public func pushClient(installationId:UUID) throws -> ApplePushClient {try ApplePushClient(access:self,config:config,installationId:installationId)}
}
