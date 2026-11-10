using System;
using System.Collections.Generic;

namespace GameBridge
{
    // Serialization adapters must reject unknown enum values and missing required fields.
    public enum ProductType { CONSUMABLE, NON_CONSUMABLE }
    public enum PurchaseStatus { PURCHASED, PENDING, CANCELED, VERIFICATION_PENDING, FAILED }
    public enum FulfillmentStatus { NOT_GRANTED, GRANTED, ALREADY_GRANTED }
    public enum FinalizationStatus { NOT_REQUIRED, PENDING, FINALIZED }

    [Serializable] public sealed class UserProfile
    {
        public string userId;
        public string displayName;
        public string provider;
    }
    [Serializable] public sealed class StoreProduct
    {
        public string productId;
        public string storeProductId;
        public ProductType type;
        public string title;
        public string localizedPrice;
        public string currencyCode;
        public string priceMicros;
    }
    [Serializable] public sealed class SdkError
    {
        public string code;
        public string message;
        public bool retryable;
        public string requestId;
        public string nativeCode;
        public Dictionary<string, string> details;
    }
    [Serializable] public sealed class PurchaseResult
    {
        public string attemptId;
        public string productId;
        public PurchaseStatus status;
        public string serverPurchaseId;
        public FulfillmentStatus fulfillmentStatus;
        public FinalizationStatus finalizationStatus;
        public SdkError error;
    }
    [Serializable] public sealed class EntitlementSnapshot
    {
        public string userId;
        public bool premiumEnabled;
        public string coinBalance;
        public string revision;
        public string updatedAt;
    }
}
