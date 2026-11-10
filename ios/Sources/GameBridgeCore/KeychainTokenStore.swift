#if canImport(Security)
import Foundation
import Security

/// Stores only the SDK session item using a device-only Keychain accessibility class.
public final class KeychainTokenStore: TokenStore {
    private let service: String
    private let account = "session"
    public init(service: String = "com.gamebridge.sdk.session") { self.service = service }
    private var query: [String: Any] { [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service, kSecAttrAccount as String: account] }
    public func save(_ value: String) throws {
        let data = Data(value.utf8)
        let status = SecItemUpdate(query as CFDictionary, [kSecValueData as String: data] as CFDictionary)
        if status == errSecItemNotFound {
            var insert = query; insert[kSecValueData as String] = data
            insert[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
            guard SecItemAdd(insert as CFDictionary, nil) == errSecSuccess else { throw SdkFailure("INTERNAL_ERROR") }
        } else if status != errSecSuccess { throw SdkFailure("INTERNAL_ERROR") }
    }
    public func load() throws -> String? {
        var request = query; request[kSecReturnData as String] = true; request[kSecMatchLimit as String] = kSecMatchLimitOne
        var result: CFTypeRef?
        let status = SecItemCopyMatching(request as CFDictionary, &result)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess, let data = result as? Data, let value = String(data: data, encoding: .utf8) else { throw SdkFailure("INTERNAL_ERROR") }
        return value
    }
    public func clear() throws {
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else { throw SdkFailure("INTERNAL_ERROR") }
    }
}
#endif
