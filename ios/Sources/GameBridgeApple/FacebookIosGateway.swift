#if canImport(UIKit) && canImport(FacebookLogin)
import Foundation
import UIKit
import FacebookLogin
import FBSDKCoreKit
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@MainActor final class FacebookIosGateway:SocialCredentialGateway {
    private let appId:String
    private let limited:Bool
    var challengeProofType:String {limited ? "FACEBOOK_LIMITED_ID_TOKEN":"FACEBOOK_ACCESS_TOKEN"}
    private let manager=LoginManager()
    private var continuation:CheckedContinuation<SocialCredential,Error>?
    private var attempt:UUID?
    private static var active:UUID?
    init(appId:String,limited:Bool){self.appId=appId;self.limited=limited}
    func preflight() throws {
        let suffix=Settings.shared.appURLSchemeSuffix ?? ""
        let schemes=(Bundle.main.object(forInfoDictionaryKey:"CFBundleURLTypes") as? [[String:Any]] ?? []).flatMap {$0["CFBundleURLSchemes"] as? [String] ?? []}
        guard GameBridgeFacebookHost.initialized,Settings.shared.appID==appId,!(Settings.shared.clientToken ?? "").isEmpty,schemes.contains("fb"+appId+suffix) else {throw SdkFailure("CONFIG_REQUIRED")}
    }
    func authorize(nonce:String)async throws->SocialCredential {
        try preflight()
        guard Self.active==nil else {throw SdkFailure("BUSY")}
        guard GameBridgeFacebookHost.initialized,Settings.shared.appID==appId,!(Settings.shared.clientToken ?? "").isEmpty,
              !nonce.isEmpty,let root=UIApplication.shared.connectedScenes.compactMap({$0 as? UIWindowScene}).filter({$0.activationState == .foregroundActive}).flatMap({$0.windows}).first(where:{$0.isKeyWindow})?.rootViewController else {throw SdkFailure("CONFIG_REQUIRED")}
        var presenter=root;while let next=presenter.presentedViewController{presenter=next}
        guard let configuration=LoginConfiguration(permissions:["public_profile"],tracking:limited ? .limited:.enabled,nonce:nonce,messengerPageId:nil) else {throw SdkFailure("CONFIG_REQUIRED")}
        let id=UUID();attempt=id;Self.active=id
        return try await withTaskCancellationHandler(operation:{
            try await withCheckedThrowingContinuation {current in
                if Task.isCancelled {Self.active=nil;attempt=nil;current.resume(throwing:SdkFailure("CANCELED"));return}
                continuation=current;manager.logOut()
                manager.logIn(viewController:presenter,configuration:configuration){[weak self] result in
                    guard Self.active==id else{return};Self.active=nil
                    guard let self,self.attempt==id else{return};self.attempt=nil
                    let completion=self.continuation;self.continuation=nil;guard let completion else{return}
                    switch result {
                    case .cancelled:completion.resume(throwing:SdkFailure("CANCELED"))
                    case .failed:completion.resume(throwing:SdkFailure("AUTH_FAILED"))
                    case .success(_,_,let token):
                        if let token {
                            guard !self.limited,!token.isExpired,token.appID==self.appId,token.permissions.contains("public_profile") else {completion.resume(throwing:SdkFailure("AUTH_FAILED"));return}
                            completion.resume(returning:SocialCredential(value:token.tokenString,proofType:"FACEBOOK_ACCESS_TOKEN"))
                        } else if let value=AuthenticationToken.current?.tokenString,!value.isEmpty {
                            // Classic may be downgraded by the SDK/ATT state. Tag the actual OIDC proof, never a Graph token.
                            completion.resume(returning:SocialCredential(value:value,proofType:"FACEBOOK_LIMITED_ID_TOKEN"))
                        } else {completion.resume(throwing:SdkFailure("AUTH_FAILED"))}
                    }
                }
            }
        },onCancel:{Task{@MainActor[weak self] in self?.cancel()}})
    }
    func cancel(){let value=continuation;continuation=nil;value?.resume(throwing:SdkFailure("CANCELED"))}
    func logout(){manager.logOut()}
}
public extension SocialAuthProvider {
    static func facebook(config:GameBridgeConfig,store:TokenStore,appId:String,limited:Bool=true)throws->SocialAuthProvider {
        guard !appId.isEmpty,appId.allSatisfy({$0.isNumber}) else {throw SdkFailure("CONFIG_REQUIRED")}
        return try SocialAuthProvider(config:config,provider:"FACEBOOK",settingsBinding:appId+(limited ? "|LIMITED":"|CLASSIC"),store:store,gateway:FacebookIosGateway(appId:appId,limited:limited))
    }
}
/// Explicit Host lifecycle/URL forwarding. No delegate replacement or C# token forwarding.
public enum GameBridgeFacebookHost {
    @MainActor static var initialized=false
    @MainActor public static func initialize(_ app:UIApplication,options:[UIApplication.LaunchOptionsKey:Any]?=nil)->Bool {
        guard let id=Bundle.main.object(forInfoDictionaryKey:"FacebookAppID") as? String,!id.isEmpty,id.allSatisfy({$0.isNumber}),
              let client=Bundle.main.object(forInfoDictionaryKey:"FacebookClientToken") as? String,!client.isEmpty else{return false}
        let suffix=Bundle.main.object(forInfoDictionaryKey:"FacebookUrlSchemeSuffix") as? String ?? ""
        let schemes=(Bundle.main.object(forInfoDictionaryKey:"CFBundleURLTypes") as? [[String:Any]] ?? []).flatMap {$0["CFBundleURLSchemes"] as? [String] ?? []}
        guard schemes.contains("fb"+id+suffix) else{return false}
        _ = ApplicationDelegate.shared.application(app,didFinishLaunchingWithOptions:options);initialized=true;return true
    }
    @MainActor public static func handle(_ url:URL)->Bool {
        guard let id=Bundle.main.object(forInfoDictionaryKey:"FacebookAppID") as? String,url.scheme=="fb"+id+(Bundle.main.object(forInfoDictionaryKey:"FacebookUrlSchemeSuffix") as? String ?? "") else{return false}
        if initialized {_ = ApplicationDelegate.shared.application(UIApplication.shared,open:url,options:[:])}
        return true // recognized callback consumed, including after cancellation/restart
    }
}
#endif
