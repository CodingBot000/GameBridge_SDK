import Foundation
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
import GameBridgeApple
#endif
#if canImport(UIKit)
import UIKit
#endif

/// Routes authentication without sharing credentials, provider storage or purchase owners.
@MainActor final class PlatformAuthBridgeHandler {
    private let apple:AppleAuthBridgeHandler
    private let marker:TokenStore
    private let factory:(String,GameBridgeConfig) throws -> SocialAuthProvider
    private let emitter:() -> (AppleStorePurchaseResult) -> Void
    private var payload:[String:Any]?
    private var config:GameBridgeConfig?
    private var selected="APPLE"
    private var appleInitialized=false
    private var social:SocialAuthProvider?
    private var store:AppleStore?
    private var storeSession:AppleStoreSession?
    private var push:ApplePushClient?
    init(apple:AppleAuthBridgeHandler,marker:TokenStore,factory:@escaping (String,GameBridgeConfig)throws->SocialAuthProvider,emitter:@escaping ()->(AppleStorePurchaseResult)->Void) {
        self.apple=apple;self.marker=marker;self.factory=factory;self.emitter=emitter
    }
    private func appleInvoke(_ op:String,_ body:[String:Any]) async throws -> Any {
        if !appleInitialized {guard let payload else {throw SdkFailure("NOT_INITIALIZED")};_ = try await apple.invoke("sdk.initialize",payload:payload);appleInitialized=true}
        return try await apple.invoke(op,payload:body)
    }
    private func socialProvider() throws -> SocialAuthProvider {
        if let social{return social};guard let config else {throw SdkFailure("NOT_INITIALIZED")}
        let value=try factory(selected,config);social=value;storeSession=try value.storeSession()
        if let text=payload?["installationId"] as? String,let id=UUID(uuidString:text) {push=try value.pushClient(installationId:id)}
        return value
    }
    private func activeStore() async throws -> AppleStore {
        if let store{return store};_ = try socialProvider()
        guard let ids=payload?["storeProductIds"] as? [String:String],let storeSession else {throw SdkFailure("CONFIG_REQUIRED")}
        let value=try storeSession.createStore(productIds:ids);value.setPurchaseUpdatedHandler(emitter());try await value.start();store=value;return value
    }
    func cancelInFlight() {store?.stop();store=nil;social?.close()}
    func invoke(_ op:String,payload body:[String:Any]) async throws -> Any {
        if op=="sdk.initialize" {
            guard body["providerMode"] as? String=="PLATFORM_SANDBOX",body["developmentKey"]==nil,
                  let app=body["appId"] as? String,let url=body["backendBaseUrl"] as? String,let timeout=body["requestTimeoutMs"] as? Int else {throw SdkFailure("CONFIG_REQUIRED")}
            let value=GameBridgeConfig(appId:app,mode:.platformSandbox,backendBaseURL:url,requestTimeoutMs:timeout);try value.validate()
            if let raw=body["storeProductIds"] {
                guard let ids=raw as? [String:String],Set(ids.keys)==Set(["coins_100","premium_unlock"]),ids.values.allSatisfy({!$0.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty}),Set(ids.values).count==2 else {throw SdkFailure("CONFIG_REQUIRED")}
            }
            if let raw=body["installationId"] {guard let text=raw as? String,let uuid=UUID(uuidString:text),uuid.uuidString.lowercased()==text.lowercased() else {throw SdkFailure("CONFIG_REQUIRED")}}
            if let config {guard config==value,let payload,try JSONSerialization.data(withJSONObject:payload,options:.sortedKeys)==JSONSerialization.data(withJSONObject:body,options:.sortedKeys) else {throw SdkFailure("ALREADY_INITIALIZED_DIFFERENT_CONFIG")}}
            if let raw=try marker.load() {
                guard let data=raw.data(using:.utf8),let saved=try? JSONSerialization.jsonObject(with:data) as? [String:String],saved["appId"]==app,saved["backend"]==url,
                      let provider=saved["provider"],["APPLE","GOOGLE"].contains(provider) else {throw SdkFailure("SESSION_EXPIRED")}
                selected=provider
            }
            config=value;payload=body
            var capabilities:[String:Any]=[:]
            for name in ["auth","store","push","config"] {let configured=name=="auth" || name=="config" || (name=="store" && body["storeProductIds"] != nil) || (name=="push" && body["installationId"] != nil);capabilities[name] = ["supported":true,"configured":configured,"mode":"PLATFORM_SANDBOX","reason":configured ? NSNull() as Any:"Host configuration required"]}
            return ["state":"READY","mode":"PLATFORM_SANDBOX","provider":selected,"capabilities":capabilities]
        }
        guard let config else {throw SdkFailure("NOT_INITIALIZED")}
        if op=="sdk.shutdown" {cancelInFlight();if appleInitialized {_ = try await apple.invoke(op,payload:body)};self.config=nil;payload=nil;social=nil;storeSession=nil;push=nil;appleInitialized=false;return [:] as [String:String]}
        if op=="auth.signIn" {
            guard let next=body["provider"] as? String,["APPLE","GOOGLE"].contains(next) else {throw SdkFailure("UNSUPPORTED_PROVIDER")}
            store?.stop();store=nil
            if next != selected {
                if selected=="APPLE" {_ = try await appleInvoke("auth.signOut",[:])} else {try await socialProvider().signOut();social?.close()}
                try marker.clear();social=nil;storeSession=nil;push=nil;selected=next
            }
            let result:Any = selected=="APPLE" ? try await appleInvoke(op,body) : try object(try await socialProvider().signIn())
            try marker.save(String(decoding:JSONSerialization.data(withJSONObject:["appId":config.appId,"backend":config.backendBaseURL!,"provider":selected]),as:UTF8.self))
            return result
        }
        if selected=="APPLE" {return try await appleInvoke(op,body)}
        let auth=try socialProvider()
        switch op {
        case "auth.restore":let user=try await auth.restore();return ["signedIn":user != nil,"user":try user.map(object) ?? NSNull(),"expiresAt":NSNull(),"sessionRestored":user != nil]
        case "auth.signOut":store?.stop();store=nil;try await auth.signOut();try marker.clear();return [:] as [String:String]
        case "config.get":guard let storeSession else {throw SdkFailure("NOT_INITIALIZED")};let effective=try await storeSession.serviceSettings();let f=ISO8601DateFormatter();f.formatOptions=[.withInternetDateTime,.withFractionalSeconds];return ["revision":effective.settings.revision,"maintenanceEnabled":effective.settings.maintenanceEnabled,"message":effective.settings.message as Any? ?? NSNull(),"expiresAt":f.string(from:effective.settings.expiresAt),"source":effective.source == .remote ? "NETWORK":"CACHE"]
        case "store.products":return try object(try await activeStore().products())
        case "store.entitlements":return try object(try await activeStore().entitlements())
        case "store.sync":guard let reason=body["reason"] as? String,["APP_RESUME","USER_RESTORE"].contains(reason) else {throw SdkFailure("INVALID_ARGUMENT")};let api=try await activeStore();let counts=try await api.recoverDetailed(userInitiated:reason=="USER_RESTORE");return ["examinedCount":counts.examinedCount,"recoveredCount":counts.recoveredCount,"deferredCount":counts.deferredCount,"failureCount":counts.failureCount,"entitlements":try object(try await api.entitlements())]
        case "store.purchase":guard let product=body["productId"] as? String else {throw SdkFailure("INVALID_ARGUMENT")};let result=try await activeStore().purchase(productId:product);let status:String
            switch result.status {case .purchased:status="PURCHASED";case .pending:status="PENDING";case .verificationPending:status="VERIFICATION_PENDING";case .cancelled:status="CANCELED"}
            return ["attemptId":UUID().uuidString.lowercased(),"productId":product,"status":status,"serverPurchaseId":result.serverPurchaseId?.uuidString.lowercased() as Any? ?? NSNull(),"fulfillmentStatus":result.fulfillmentStatus ?? "NOT_GRANTED","finalizationStatus":status=="PURCHASED" ? "FINALIZED":"PENDING","error":NSNull()]
        case "host.pushToken":guard let push,body["provider"] as? String=="APNS",let token=body["token"] as? String,!token.isEmpty,token.count.isMultiple(of:2),token.range(of:"^[0-9a-fA-F]+$",options:.regularExpression) != nil else {throw SdkFailure("CONFIG_REQUIRED")};var bytes=Data();var index=token.startIndex;while index<token.endIndex {let end=token.index(index,offsetBy:2);guard let byte=UInt8(token[index..<end],radix:16) else {throw SdkFailure("INVALID_ARGUMENT")};bytes.append(byte);index=end};return ["registered":true,"tokenFingerprint":try await push.register(deviceToken:bytes)]
        case "push.unregister":guard let push else {throw SdkFailure("CONFIG_REQUIRED")};try await push.unregister();return ["registered":false]
        default:throw SdkFailure("UNSUPPORTED_OPERATION")
        }
    }
    private func object<T:Encodable>(_ value:T)throws->Any {try JSONSerialization.jsonObject(with:JSONEncoder().encode(value))}
}
#if canImport(UIKit) && canImport(AuthenticationServices)
@MainActor func makePlatformAuthBridgeHandler(emitter:@escaping ()->(AppleStorePurchaseResult)->Void) -> PlatformAuthBridgeHandler {
    PlatformAuthBridgeHandler(apple:makeAppleAuthBridgeHandler(makeEmitter:emitter),marker:KeychainTokenStore(service:"com.gamebridge.sdk.unity.social.selection"),factory: { provider,config in
        guard provider=="GOOGLE" else {throw SdkFailure("UNSUPPORTED_PROVIDER")}
        guard let client=Bundle.main.object(forInfoDictionaryKey:"GIDClientID") as? String,let server=Bundle.main.object(forInfoDictionaryKey:"GIDServerClientID") as? String else {throw SdkFailure("CONFIG_REQUIRED")}
        return try SocialAuthProvider.google(config:config,store:KeychainTokenStore(service:"com.gamebridge.sdk.unity.google.ios"),clientId:client,serverClientId:server)
    },emitter:emitter)
}
#endif
