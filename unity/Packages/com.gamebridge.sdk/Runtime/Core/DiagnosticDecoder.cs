using System;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace GameBridge.Core
{
    internal static class DiagnosticDecoder
    {
        internal static IReadOnlyList<NativeDiagnosticEvent> Decode(JToken result)
        {
            if (!(result is JObject obj) || !(obj["events"] is JArray events) || events.Count > 200)
                throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
            var parsed = new List<NativeDiagnosticEvent>(events.Count);
            foreach (var item in events)
            {
                if (!(item is JObject value) || value["kind"]?.Type != JTokenType.String || value["outcome"]?.Type != JTokenType.String ||
                    value["timestamp"]?.Type != JTokenType.String ||
                    !Enum.TryParse((string)value["kind"], out DiagnosticKind kind) || !Enum.IsDefined(typeof(DiagnosticKind), kind) || kind.ToString() != (string)value["kind"] ||
                    !Enum.TryParse((string)value["outcome"], out DiagnosticOutcome outcome) || !Enum.IsDefined(typeof(DiagnosticOutcome), outcome) || outcome.ToString() != (string)value["outcome"] ||
                    !DateTimeOffset.TryParse((string)value["timestamp"], System.Globalization.CultureInfo.InvariantCulture, System.Globalization.DateTimeStyles.RoundtripKind, out var timestamp))
                    throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                Guid? requestId = null;
                if (value["requestId"] == null || (value["requestId"].Type != JTokenType.Null &&
                    (value["requestId"].Type != JTokenType.String || !Guid.TryParseExact((string)value["requestId"], "D", out _))))
                    throw new SdkException("BRIDGE_PROTOCOL_MISMATCH");
                if (value["requestId"].Type == JTokenType.String) requestId = Guid.Parse((string)value["requestId"]);
                parsed.Add(new NativeDiagnosticEvent(kind, outcome, timestamp, requestId));
            }
            return parsed.AsReadOnly();
        }
    }
}
