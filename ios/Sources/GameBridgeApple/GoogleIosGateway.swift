#if canImport(UIKit) && canImport(GoogleSignIn)
import Foundation
import UIKit
import GoogleSignIn
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@MainActor final class GoogleIosGateway: SocialCredentialGateway {
    private weak var presenter:UIViewController?
    private let clientId:String, serverClientId:String
    private let resolveActive:Bool
    private var continuation:CheckedContinuation<SocialCredential,Error>?
    private var attempt:UUID?
    private static var activeAttempt:UUID?
    init(presenter:UIViewController?,clientId:String,serverClientId:String) {self.presenter=presenter;resolveActive=presenter==nil;self.clientId=clientId;self.serverClientId=serverClientId}
    func authorize(nonce:String) async throws -> SocialCredential {
        guard attempt==nil,Self.activeAttempt==nil else {throw SdkFailure("BUSY")}
        var host=presenter
        if resolveActive {
            host=UIApplication.shared.connectedScenes.compactMap {$0 as? UIWindowScene}.filter {$0.activationState == .foregroundActive}.flatMap {$0.windows}.first(where:{$0.isKeyWindow})?.rootViewController
            while let next=host?.presentedViewController {host=next}
        }
        guard let presenter=host,presenter.viewIfLoaded?.window != nil,!nonce.isEmpty else {throw SdkFailure("CONFIG_REQUIRED")}
        let reversed=clientId.components(separatedBy:".").reversed().joined(separator:".")
        let types=Bundle.main.object(forInfoDictionaryKey:"CFBundleURLTypes") as? [[String:Any]] ?? []
        let schemes=types.flatMap {$0["CFBundleURLSchemes"] as? [String] ?? []}
        guard clientId.hasSuffix(".apps.googleusercontent.com"),serverClientId.hasSuffix(".apps.googleusercontent.com"),schemes.contains(reversed) else {throw SdkFailure("CONFIG_REQUIRED")}
        if let existing=GIDSignIn.sharedInstance.configuration {
            guard existing.clientID==clientId,existing.serverClientID==serverClientId else {throw SdkFailure("CONFIG_REQUIRED")}
        } else { GIDSignIn.sharedInstance.configuration=GIDConfiguration(clientID:clientId,serverClientID:serverClientId) }
        let id=UUID();attempt=id;Self.activeAttempt=id
        return try await withTaskCancellationHandler(operation: {
            try await withCheckedThrowingContinuation { current in
                if Task.isCancelled {attempt=nil;Self.activeAttempt=nil;current.resume(throwing:SdkFailure("CANCELED"));return}
                continuation=current
                // Official9.2 overload passes the raw challenge nonce into the signed ID token.
                GIDSignIn.sharedInstance.signIn(withPresenting:presenter,hint:nil,additionalScopes:nil,nonce:nonce) { [weak self] result,error in
                    let rawToken=result?.user.idToken?.tokenString
                    let canceled=error.map {($0 as NSError).domain==kGIDSignInErrorDomain && ($0 as NSError).code==GIDSignInError.canceled.rawValue} ?? false
                    let failed=error != nil
                    Task { @MainActor [weak self] in
                        guard Self.activeAttempt==id else {return}
                        Self.activeAttempt=nil
                        guard let self,self.attempt==id else {return}
                        self.attempt=nil;let completion=self.continuation;self.continuation=nil
                        guard let completion else {return}
                        if failed {completion.resume(throwing:SdkFailure(canceled ? "CANCELED":"AUTH_FAILED"));return}
                        guard let token=rawToken,!token.isEmpty else {completion.resume(throwing:SdkFailure("AUTH_FAILED"));return}
                        completion.resume(returning:SocialCredential(value:token,proofType:"ID_TOKEN"))
                    }
                }
            }
        }, onCancel: {Task {@MainActor [weak self] in self?.cancel()}})
    }
    func cancel() { let pending=continuation;continuation=nil;pending?.resume(throwing:SdkFailure("CANCELED")) }
    func logout() {GIDSignIn.sharedInstance.signOut()}
}
public extension SocialAuthProvider {
    static func google(config:GameBridgeConfig,store:TokenStore,presenting:UIViewController? = nil,clientId:String,serverClientId:String) throws -> SocialAuthProvider {
        guard !clientId.isEmpty,!serverClientId.isEmpty else {throw SdkFailure("CONFIG_REQUIRED")}
        return try SocialAuthProvider(config:config,provider:"GOOGLE",settingsBinding:clientId+"|"+serverClientId,store:store,
            gateway:GoogleIosGateway(presenter:presenting,clientId:clientId,serverClientId:serverClientId))
    }
}
/// Host forwards its existing URL callback; the SDK does not install or replace an AppDelegate.
public enum GameBridgeGoogleHost {
    @MainActor public static func handle(_ url:URL) -> Bool {GIDSignIn.sharedInstance.handle(url)}
}
#endif
