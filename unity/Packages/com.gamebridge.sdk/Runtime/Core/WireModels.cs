using System;
using System.Globalization;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace GameBridge.Core
{
    internal static class WireModels
    {
        private sealed class ExactEnumConverter : JsonConverter
        {
            public override bool CanConvert(Type type) => type.IsEnum;
            public override object ReadJson(JsonReader reader, Type type, object existingValue, JsonSerializer serializer)
            {
                if (reader.TokenType != JsonToken.String || !(reader.Value is string name) || !Enum.IsDefined(type, name))
                    throw new JsonSerializationException("Unknown enum");
                return Enum.Parse(type, name, false);
            }
            public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) => writer.WriteValue(value.ToString());
        }
        private static JsonSerializer Serializer()
        {
            var serializer = JsonSerializer.Create(new JsonSerializerSettings { MissingMemberHandling = MissingMemberHandling.Ignore, DateParseHandling = DateParseHandling.None });
            serializer.Converters.Add(new ExactEnumConverter());
            return serializer;
        }
        internal static T Decode<T>(JToken token)
        {
            try
            {
                ValidateShape<T>(token);
                var value = token.ToObject<T>(Serializer());
                if (value == null) throw new JsonSerializationException("Null result");
                if (value is UserProfile profile) Validate(profile);
                if (value is StoreProduct product && product.priceMicros != null) Decimal64(product.priceMicros);
                if (value is PurchaseResult purchase)
                {
                    Uuid(purchase.attemptId);
                    if (purchase.serverPurchaseId != null) Uuid(purchase.serverPurchaseId);
                    if (purchase.error != null)
                    {
                        if (purchase.error.requestId != null) Uuid(purchase.error.requestId);
                        if (!RequestRegistry.IsKnownError(purchase.error.code)) { purchase.error.code = "INTERNAL_ERROR"; purchase.error.retryable = false; }
                        purchase.error.message = "Operation failed"; purchase.error.nativeCode = null; purchase.error.details = new Dictionary<string, string>();
                    }
                    if (purchase.status != PurchaseStatus.PURCHASED && purchase.fulfillmentStatus != FulfillmentStatus.NOT_GRANTED) throw new JsonSerializationException("Unverified grant");
                }
                if (value is EntitlementSnapshot wallet)
                {
                    Uuid(wallet.userId); Decimal64(wallet.coinBalance); Decimal64(wallet.revision); Timestamp(wallet.updatedAt);
                }
                if (value is SessionSnapshot session)
                {
                    if (session.user != null) Validate(session.user);
                    if (session.expiresAt != null) Timestamp(session.expiresAt);
                    if (session.signedIn != (session.user != null)) throw new JsonSerializationException("Inconsistent session");
                }
                return value;
            }
            catch (Exception error) when (error is JsonException || error is FormatException || error is OverflowException || error is ArgumentException)
            { throw new SdkException("BRIDGE_PROTOCOL_MISMATCH"); }
        }
        private static void ValidateShape<T>(JToken token)
        {
            if (!(token is JObject obj)) throw new JsonSerializationException("Expected object");
            if (typeof(T) == typeof(UserProfile)) ShapeProfile(obj);
            else if (typeof(T) == typeof(StoreProduct))
            {
                foreach (var name in new[] { "productId", "storeProductId", "type", "title", "localizedPrice", "currencyCode" }) Field(obj, name, JTokenType.String);
                Field(obj, "priceMicros", JTokenType.String, true);
            }
            else if (typeof(T) == typeof(PurchaseResult))
            {
                foreach (var name in new[] { "attemptId", "productId", "status", "fulfillmentStatus", "finalizationStatus" }) Field(obj, name, JTokenType.String);
                Field(obj, "serverPurchaseId", JTokenType.String, true); Field(obj, "error", JTokenType.Object, true);
                if (obj["error"] is JObject error)
                {
                    foreach (var name in new[] { "code", "message" }) Field(error, name, JTokenType.String);
                    Field(error, "retryable", JTokenType.Boolean); Field(error, "requestId", JTokenType.String, true);
                    Field(error, "nativeCode", JTokenType.String, true); Field(error, "details", JTokenType.Object);
                    foreach (var item in ((JObject)error["details"]).Properties()) if (item.Value.Type != JTokenType.String) throw new JsonSerializationException("Invalid detail");
                }
            }
            else if (typeof(T) == typeof(EntitlementSnapshot))
            {
                foreach (var name in new[] { "userId", "coinBalance", "revision", "updatedAt" }) Field(obj, name, JTokenType.String);
                Field(obj, "premiumEnabled", JTokenType.Boolean);
            }
            else if (typeof(T) == typeof(SessionSnapshot))
            {
                Field(obj, "signedIn", JTokenType.Boolean); Field(obj, "user", JTokenType.Object, true);
                Field(obj, "expiresAt", JTokenType.String, true); Field(obj, "sessionRestored", JTokenType.Boolean);
                if (obj["user"] is JObject user) ShapeProfile(user);
            }
        }
        private static void ShapeProfile(JObject obj) { Field(obj, "userId", JTokenType.String); Field(obj, "displayName", JTokenType.String, true); Field(obj, "provider", JTokenType.String); }
        private static void Field(JObject obj, string name, JTokenType expected, bool nullable = false)
        {
            if (!obj.TryGetValue(name, out var value) || (value.Type != expected && !(nullable && value.Type == JTokenType.Null))) throw new JsonSerializationException("Invalid field");
        }
        private static void Validate(UserProfile profile) { Uuid(profile.userId); }
        private static void Uuid(string value) { if (!Guid.TryParseExact(value, "D", out _)) throw new FormatException(); }
        private static void Decimal64(string value)
        {
            if (!long.TryParse(value, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var parsed) || parsed.ToString(CultureInfo.InvariantCulture) != value) throw new FormatException();
        }
        private static void Timestamp(string value)
        {
            if (string.IsNullOrEmpty(value) || !Regex.IsMatch(value, @"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,9})?Z$") || !DateTimeOffset.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out _)) throw new FormatException();
        }
    }
}
