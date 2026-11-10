package com.gamebridge.purchase

import com.google.api.services.androidpublisher.model.ProductLineItem
import com.google.api.services.androidpublisher.model.ProductOfferDetails
import com.google.api.services.androidpublisher.model.ProductPurchaseV2
import com.google.api.services.androidpublisher.model.PurchaseStateContext
import com.google.api.services.androidpublisher.model.TestPurchaseContext
import java.io.IOException
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse

class GooglePurchaseVerifierTest {
    private fun purchase() = ProductPurchaseV2().setPurchaseStateContext(PurchaseStateContext().setPurchaseState("PURCHASED"))
        .setObfuscatedExternalAccountId("account").setTestPurchaseContext(TestPurchaseContext())
        .setProductLineItem(listOf(ProductLineItem().setProductId("coins").setProductOfferDetails(ProductOfferDetails().setQuantity(1))))
    private fun verifier(value: ProductPurchaseV2) = GooglePurchaseVerifier("test.package", setOf("coins"), true, GooglePurchaseLookup { app, _ ->
        assertEquals("test.package", app); value
    })
    @Test fun `purchase must match product account test environment and state`() {
        assertEquals("coins", verifier(purchase()).verify("secret-token", "coins", "account").productId)
        assertFalse(verifier(purchase()).verify("secret-token", "coins", "account").toString().contains("secret-token"))
        listOf(purchase().setPurchaseStateContext(PurchaseStateContext().setPurchaseState("PENDING")),
            purchase().setObfuscatedExternalAccountId("other"), purchase().setTestPurchaseContext(null),
            purchase().setProductLineItem(listOf(ProductLineItem().setProductId("other").setProductOfferDetails(ProductOfferDetails().setQuantity(1)))),
            purchase().setProductLineItem(listOf(ProductLineItem().setProductId("coins").setProductOfferDetails(ProductOfferDetails().setQuantity(2))))).forEach {
            assertFailsWith<GoogleProofRejected> { verifier(it).verify("synthetic", "coins", "account") }
        }
        assertFailsWith<GoogleProofRejected> { verifier(purchase()).verify("synthetic", "unknown", "account") }
    }
    @Test fun `network failure is not a forged proof`() {
        val verifier = GooglePurchaseVerifier("test.package", setOf("coins"), true, GooglePurchaseLookup { _, _ -> throw IOException("offline") })
        assertFailsWith<GoogleVerifierUnavailable> { verifier.verify("synthetic", "coins", "account") }
    }
}
