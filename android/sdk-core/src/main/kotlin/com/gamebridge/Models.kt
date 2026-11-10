package com.gamebridge

import kotlinx.serialization.Serializable

@Serializable data class UserProfile(val userId: String, val displayName: String?, val provider: String)
@Serializable enum class ProductType { CONSUMABLE, NON_CONSUMABLE }
@Serializable data class StoreProduct(
    val productId: String, val storeProductId: String, val type: ProductType,
    val title: String, val localizedPrice: String, val currencyCode: String, val priceMicros: String?,
)
@Serializable data class SdkError(
    val code: String, val message: String, val retryable: Boolean,
    val requestId: String?, val nativeCode: String?, val details: Map<String, String>,
)
@Serializable enum class PurchaseStatus { PURCHASED, PENDING, CANCELED, VERIFICATION_PENDING, FAILED }
@Serializable enum class FulfillmentStatus { NOT_GRANTED, GRANTED, ALREADY_GRANTED }
@Serializable enum class FinalizationStatus { NOT_REQUIRED, PENDING, FINALIZED }
@Serializable data class PurchaseResult(
    val attemptId: String, val productId: String, val status: PurchaseStatus,
    val serverPurchaseId: String?, val fulfillmentStatus: FulfillmentStatus,
    val finalizationStatus: FinalizationStatus, val error: SdkError?,
)
@Serializable data class EntitlementSnapshot(
    val userId: String, val premiumEnabled: Boolean, val coinBalance: String,
    val revision: String, val updatedAt: String,
)
