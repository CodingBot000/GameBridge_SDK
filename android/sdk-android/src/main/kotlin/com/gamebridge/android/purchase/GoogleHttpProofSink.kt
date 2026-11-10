package com.gamebridge.android.purchase

import com.gamebridge.BackendClient
import com.gamebridge.SdkFailure
import com.gamebridge.android.auth.GoogleAuthProvider
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import java.util.UUID

/** Native-only proof transport; token is sent exclusively to configured Backend. */
internal class GoogleHttpProofSink(
    private val auth: GoogleAuthProvider,
    private val request: suspend (path: String, body: String, accessToken: String, attemptId: String?) -> String,
) : PlayProofSink {
    constructor(auth: GoogleAuthProvider, client: BackendClient) : this(auth, { path, body, accessToken, attemptId ->
        client.request(path, "POST", body, accessToken = accessToken, idempotencyKey = attemptId).json
    })
    suspend fun ensureReady(storeProductId: String) {
        val ready = auth.withAuthenticatedSession { session ->
            val body = buildJsonObject { put("storeProductId", storeProductId) }.toString()
            val data = request("/v1/purchases/google/readiness", body, session.accessToken, null)
            try {
                val value = Json.parseToJsonElement(data).jsonObject.getValue("ready").jsonPrimitive
                !value.isString && value.content == "true"
            }
            catch (_: Exception) { false }
        } ?: throw SdkFailure("SESSION_EXPIRED")
        if (!ready) throw SdkFailure("CONFIG_REQUIRED")
    }
    override suspend fun verify(account: BoundPlayAccount, productId: String, proof: RawPlayPurchase): ServerPlayResult {
        if (proof.token.isBlank()) throw SdkFailure("VERIFICATION_FAILED")
        val attempt = UUID.randomUUID().toString()
        return auth.withAuthenticatedSession { session ->
            if (session.userId != account.userId.toString()) throw SdkFailure("PURCHASE_ACCOUNT_MISMATCH")
            val body = buildJsonObject { put("storeProductId", proof.storeId); put("purchaseToken", proof.token) }.toString()
            parseGoogleGrant(request("/v1/purchases/google/verify", body, session.accessToken, attempt), productId)
        } ?: throw SdkFailure("SESSION_EXPIRED")
    }
}
internal fun parseGoogleGrant(body: String, expectedProduct: String): ServerPlayResult {
    try {
        val value = Json.parseToJsonElement(body).jsonObject
        fun field(name: String) = value.getValue(name).jsonPrimitive.content
        val status = field("fulfillmentStatus")
        val product = field("productId")
        val hex = field("proofFingerprint")
        require(status in setOf("GRANTED", "ALREADY_GRANTED") && product == expectedProduct && hex.matches(Regex("[0-9a-f]{64}")))
        val fingerprint = ByteArray(32) { i -> hex.substring(i * 2, i * 2 + 2).toInt(16).toByte() }
        return ServerPlayResult(UUID.fromString(field("userId")), field("accountId"), product,
            UUID.fromString(field("serverPurchaseId")), status, fingerprint)
    } catch (_: Exception) { throw SdkFailure("BRIDGE_PROTOCOL_MISMATCH") }
}
