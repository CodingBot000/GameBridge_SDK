import Foundation

public enum ProductType: String, Codable { case consumable = "CONSUMABLE", nonConsumable = "NON_CONSUMABLE" }
public enum PurchaseStatus: String, Codable { case purchased = "PURCHASED", pending = "PENDING", canceled = "CANCELED", verificationPending = "VERIFICATION_PENDING", failed = "FAILED" }
public enum FulfillmentStatus: String, Codable { case notGranted = "NOT_GRANTED", granted = "GRANTED", alreadyGranted = "ALREADY_GRANTED" }
public enum FinalizationStatus: String, Codable { case notRequired = "NOT_REQUIRED", pending = "PENDING", finalized = "FINALIZED" }

public struct UserProfile: Codable, Equatable {
    public let userId: String
    public let displayName: String?
    public let provider: String
    enum CodingKeys: String, CodingKey { case userId, displayName, provider }
    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        userId = try c.decode(String.self, forKey: .userId)
        displayName = try c.decode(String?.self, forKey: .displayName)
        provider = try c.decode(String.self, forKey: .provider)
    }
    public func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(userId, forKey: .userId); try c.encode(displayName, forKey: .displayName); try c.encode(provider, forKey: .provider)
    }
}
public struct StoreProduct: Codable, Equatable {
    public let productId, storeProductId: String
    public let type: ProductType
    public let title, localizedPrice, currencyCode: String
    public let priceMicros: String?
    enum CodingKeys: String, CodingKey { case productId, storeProductId, type, title, localizedPrice, currencyCode, priceMicros }
    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        productId = try c.decode(String.self, forKey: .productId); storeProductId = try c.decode(String.self, forKey: .storeProductId)
        type = try c.decode(ProductType.self, forKey: .type); title = try c.decode(String.self, forKey: .title)
        localizedPrice = try c.decode(String.self, forKey: .localizedPrice); currencyCode = try c.decode(String.self, forKey: .currencyCode)
        priceMicros = try c.decode(String?.self, forKey: .priceMicros)
    }
    public func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(productId, forKey: .productId); try c.encode(storeProductId, forKey: .storeProductId); try c.encode(type, forKey: .type)
        try c.encode(title, forKey: .title); try c.encode(localizedPrice, forKey: .localizedPrice); try c.encode(currencyCode, forKey: .currencyCode)
        try c.encode(priceMicros, forKey: .priceMicros)
    }
}
public struct SdkError: Codable, Equatable {
    public let code, message: String
    public let retryable: Bool
    public let requestId, nativeCode: String?
    public let details: [String: String]
    enum CodingKeys: String, CodingKey { case code, message, retryable, requestId, nativeCode, details }
    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        code = try c.decode(String.self, forKey: .code); message = try c.decode(String.self, forKey: .message); retryable = try c.decode(Bool.self, forKey: .retryable)
        requestId = try c.decode(String?.self, forKey: .requestId); nativeCode = try c.decode(String?.self, forKey: .nativeCode); details = try c.decode([String: String].self, forKey: .details)
    }
    public func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(code, forKey: .code); try c.encode(message, forKey: .message); try c.encode(retryable, forKey: .retryable)
        try c.encode(requestId, forKey: .requestId); try c.encode(nativeCode, forKey: .nativeCode); try c.encode(details, forKey: .details)
    }
}
public struct PurchaseResult: Codable, Equatable {
    public let attemptId, productId: String
    public let status: PurchaseStatus
    public let serverPurchaseId: String?
    public let fulfillmentStatus: FulfillmentStatus
    public let finalizationStatus: FinalizationStatus
    public let error: SdkError?
    enum CodingKeys: String, CodingKey { case attemptId, productId, status, serverPurchaseId, fulfillmentStatus, finalizationStatus, error }
    public init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        attemptId = try c.decode(String.self, forKey: .attemptId); productId = try c.decode(String.self, forKey: .productId)
        status = try c.decode(PurchaseStatus.self, forKey: .status); serverPurchaseId = try c.decode(String?.self, forKey: .serverPurchaseId)
        fulfillmentStatus = try c.decode(FulfillmentStatus.self, forKey: .fulfillmentStatus); finalizationStatus = try c.decode(FinalizationStatus.self, forKey: .finalizationStatus)
        error = try c.decode(SdkError?.self, forKey: .error)
    }
    public func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(attemptId, forKey: .attemptId); try c.encode(productId, forKey: .productId); try c.encode(status, forKey: .status)
        try c.encode(serverPurchaseId, forKey: .serverPurchaseId); try c.encode(fulfillmentStatus, forKey: .fulfillmentStatus)
        try c.encode(finalizationStatus, forKey: .finalizationStatus); try c.encode(error, forKey: .error)
    }
}
public struct EntitlementSnapshot: Codable, Equatable {
    public let userId: String
    public let premiumEnabled: Bool
    public let coinBalance, revision, updatedAt: String
}
