#if canImport(UIKit) && canImport(AuthenticationServices)
import Foundation
import UIKit
import AuthenticationServices
#if !GAMEBRIDGE_CORE_EMBEDDED
import GameBridgeCore
#endif

@MainActor final class AppleSystemGateway: NSObject, AppleCredentialGateway, ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    private weak var host: UIWindow?
    private var activeAnchor: UIWindow?
    private var controller: ASAuthorizationController?
    private var continuation: CheckedContinuation<AppleCredential, Error>?
    private var requestID: UUID?
    func attach(_ window: UIWindow) { host = window }
    func detach() { host = nil }
    func authorize(nonce: String) async throws -> AppleCredential {
        guard continuation == nil else { throw SdkFailure("BUSY") }
        guard let window = host, window.windowScene != nil else { throw SdkFailure("CONFIG_REQUIRED") }
        let requestID = UUID()
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]
        request.nonce = nonce
        do { return try await withTaskCancellationHandler(operation: {
            try Task.checkCancellation()
            return try await withCheckedThrowingContinuation { continuation in
                if Task.isCancelled { continuation.resume(throwing: SdkFailure("CANCELED")); return }
                self.requestID = requestID; self.continuation = continuation; self.activeAnchor = window
                let controller = ASAuthorizationController(authorizationRequests: [request])
                self.controller = controller; controller.delegate = self; controller.presentationContextProvider = self
                controller.performRequests()
            }
        }, onCancel: { Task { @MainActor [weak self] in self?.cancel(requestID: requestID) } }) }
        catch is CancellationError { throw SdkFailure("CANCELED") }
    }
    func credentialState(userIdentifier: String) async throws -> AppleCredentialState {
        try await withCheckedThrowingContinuation { continuation in
            ASAuthorizationAppleIDProvider().getCredentialState(forUserID: userIdentifier) { state, error in
                if error != nil { continuation.resume(throwing: SdkFailure("AUTH_FAILED")); return }
                switch state {
                case .authorized: continuation.resume(returning: .authorized)
                case .revoked: continuation.resume(returning: .revoked)
                case .notFound: continuation.resume(returning: .notFound)
                case .transferred: continuation.resume(returning: .transferred)
                @unknown default: continuation.resume(returning: .unknown)
                }
            }
        }
    }
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor { activeAnchor ?? host ?? ASPresentationAnchor() }
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        guard self.controller === controller else { return }
        guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential,
              let data = credential.identityToken, let token = String(data: data, encoding: .utf8), !token.isEmpty else { finish(.failure(SdkFailure("AUTH_FAILED"))); return }
        let formatted = credential.fullName.map { PersonNameComponentsFormatter().string(from: $0) }
        let name = formatted.flatMap { $0.isEmpty ? nil : $0 }
        finish(.success(AppleCredential(identityToken: token, userIdentifier: credential.user, displayName: name)))
    }
    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        guard self.controller === controller else { return }
        let canceled = (error as? ASAuthorizationError)?.code == .canceled
        finish(.failure(SdkFailure(canceled ? "CANCELED" : "AUTH_FAILED")))
    }
    private func cancel(requestID: UUID) {
        guard self.requestID == requestID else { return }
        controller?.cancel(); finish(.failure(SdkFailure("CANCELED")))
    }
    private func finish(_ result: Result<AppleCredential, Error>) {
        guard let current = continuation else { return }
        continuation = nil; requestID = nil
        controller?.delegate = nil; controller?.presentationContextProvider = nil
        controller = nil; activeAnchor = nil
        current.resume(with: result)
    }
}

public extension AppleAuthProvider {
    static func create(config: GameBridgeConfig, store: TokenStore, window: UIWindow) throws -> AppleAuthProvider {
        guard config.mode == .platformSandbox else { throw SdkFailure("UNSUPPORTED_PROVIDER") }
        try config.validate()
        let gateway = AppleSystemGateway(); gateway.attach(window)
        return AppleAuthProvider(config: config, store: store, gateway: gateway, backend: try HttpAppleBackend(config: config))
    }
    func attachHost(_ window: UIWindow) { (gateway as? AppleSystemGateway)?.attach(window) }
    func detachHost() { (gateway as? AppleSystemGateway)?.detach() }
}
#endif
