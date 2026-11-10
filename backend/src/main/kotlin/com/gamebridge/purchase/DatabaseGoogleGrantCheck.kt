package com.gamebridge.purchase

import org.springframework.jdbc.core.JdbcTemplate
import java.security.MessageDigest

/** Config maps an app to the only package that its Google client is authorized to query. */
internal class DatabaseGoogleGrantCheck(private val db: JdbcTemplate, private val packageForApp: (String) -> String?) : DurableGoogleGrantCheck {
    override fun isGranted(input: GoogleFinalizationInput, tokenHash: ByteArray): Boolean {
        val row = db.query("""SELECT p.app_id,p.proof_key_hash,p.fulfillment_state,b.google_obfuscated_id,pr.store_id,pr.type
            FROM purchases p JOIN purchase_account_bindings b ON b.user_id=p.user_id AND b.app_id=p.app_id
            JOIN products pr ON pr.app_id=p.app_id AND pr.platform='GOOGLE' AND pr.logical_id=p.product_id
            WHERE p.id=? AND p.platform='GOOGLE'""", { rs, _ ->
            GrantCheckRow(rs.getString(1), rs.getBytes(2), rs.getString(3), rs.getObject(4, java.util.UUID::class.java).toString(), rs.getString(5), rs.getString(6))
        }, input.purchaseId).firstOrNull() ?: return false
        val correctAction = (row.type == "CONSUMABLE" && input.action == GoogleFinalizationAction.CONSUME) ||
            (row.type == "NON_CONSUMABLE" && input.action == GoogleFinalizationAction.ACKNOWLEDGE)
        return row.fulfillment == "GRANTED" && row.account == input.accountId && row.storeId == input.productId &&
            packageForApp(row.appId) == input.packageName && correctAction && MessageDigest.isEqual(row.hash, tokenHash)
    }
    private data class GrantCheckRow(val appId: String, val hash: ByteArray, val fulfillment: String, val account: String, val storeId: String, val type: String)
}
