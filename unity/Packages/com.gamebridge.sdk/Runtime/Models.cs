using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace GameBridge
{
    public enum ProductType { CONSUMABLE, NON_CONSUMABLE }
    public enum PurchaseStatus { PURCHASED, PENDING, CANCELED, VERIFICATION_PENDING, FAILED }
    public enum FulfillmentStatus { NOT_GRANTED, GRANTED, ALREADY_GRANTED }
    public enum FinalizationStatus { NOT_REQUIRED, PENDING, FINALIZED }

    [Serializable] public sealed class UserProfile
    {
        [JsonProperty(Required = Required.Always)] public string userId;
        [JsonProperty(Required = Required.AllowNull)] public string displayName;
        [JsonProperty(Required = Required.Always)] public string provider;
    }
    [Serializable] public sealed class StoreProduct
    {
        [JsonProperty(Required = Required.Always)] public string productId;
        [JsonProperty(Required = Required.Always)] public string storeProductId;
        [JsonProperty(Required = Required.Always)] public ProductType type;
        [JsonProperty(Required = Required.Always)] public string title;
        [JsonProperty(Required = Required.Always)] public string localizedPrice;
        [JsonProperty(Required = Required.Always)] public string currencyCode;
        [JsonProperty(Required = Required.AllowNull)] public string priceMicros;
    }
    [Serializable] public sealed class SdkError
    {
        [JsonProperty(Required = Required.Always)] public string code;
        [JsonProperty(Required = Required.Always)] public string message;
        [JsonProperty(Required = Required.Always)] public bool retryable;
        [JsonProperty(Required = Required.AllowNull)] public string requestId;
        [JsonProperty(Required = Required.AllowNull)] public string nativeCode;
        [JsonProperty(Required = Required.Always)] public Dictionary<string, string> details;
    }
    [Serializable] public sealed class PurchaseResult
    {
        [JsonProperty(Required = Required.Always)] public string attemptId;
        [JsonProperty(Required = Required.Always)] public string productId;
        [JsonProperty(Required = Required.Always)] public PurchaseStatus status;
        [JsonProperty(Required = Required.AllowNull)] public string serverPurchaseId;
        [JsonProperty(Required = Required.Always)] public FulfillmentStatus fulfillmentStatus;
        [JsonProperty(Required = Required.Always)] public FinalizationStatus finalizationStatus;
        [JsonProperty(Required = Required.AllowNull)] public SdkError error;
    }
    [Serializable] public sealed class EntitlementSnapshot
    {
        [JsonProperty(Required = Required.Always)] public string userId;
        [JsonProperty(Required = Required.Always)] public bool premiumEnabled;
        [JsonProperty(Required = Required.Always)] public string coinBalance;
        [JsonProperty(Required = Required.Always)] public string revision;
        [JsonProperty(Required = Required.Always)] public string updatedAt;
    }
    [Serializable] public sealed class SessionSnapshot
    {
        [JsonProperty(Required = Required.Always)] public bool signedIn;
        [JsonProperty(Required = Required.AllowNull)] public UserProfile user;
        [JsonProperty(Required = Required.AllowNull)] public string expiresAt;
        [JsonProperty(Required = Required.Always)] public bool sessionRestored;
    }
}
