package com.gamebridge.purchase

import com.google.api.services.androidpublisher.model.ProductPurchase
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.*

class GoogleStoreFinalizerTest {
    private class FakeGateway : GoogleFinalizationGateway {
        var lookups = 0; var consumes = 0; var acknowledges = 0
        var purchase = ProductPurchase().setPurchaseState(0).setObfuscatedExternalAccountId("account")
            .setProductId("coins.store").setQuantity(1).setConsumptionState(0).setAcknowledgementState(0)
        override fun lookup(input: GoogleFinalizationInput): ProductPurchase { lookups++; return purchase }
        override fun consume(input: GoogleFinalizationInput) { consumes++ }
        override fun acknowledge(input: GoogleFinalizationInput) { acknowledges++ }
    }
    private fun input(action: GoogleFinalizationAction) = GoogleFinalizationInput(UUID.randomUUID(), "test.package", "coins.store", "account", "secret-proof", action)
    @Test fun `only granted matching purchase can be finalized`() {
        val gateway = FakeGateway(); val work = input(GoogleFinalizationAction.CONSUME)
        assertFalse(work.toString().contains("secret-proof"))
        val denied = GoogleStoreFinalizer(DurableGoogleGrantCheck { _, _ -> false }, gateway)
        assertFailsWith<PurchaseConflict> { denied.finalize(work) }; assertEquals(0, gateway.lookups)
        val service = GoogleStoreFinalizer(DurableGoogleGrantCheck { _, hash -> hash.size == 32 }, gateway)
        gateway.purchase.obfuscatedExternalAccountId = "other"
        assertFailsWith<PurchaseConflict> { service.finalize(work) }; assertEquals(0, gateway.consumes)
        gateway.purchase.obfuscatedExternalAccountId = "account"
        service.finalize(work); assertEquals(1, gateway.consumes); assertEquals(0, gateway.acknowledges)
    }
    @Test fun `already finished is accepted only after store lookup and granted check`() {
        val gateway = FakeGateway(); val service = GoogleStoreFinalizer(DurableGoogleGrantCheck { _, _ -> true }, gateway)
        gateway.purchase.consumptionState = 1
        service.finalize(input(GoogleFinalizationAction.CONSUME)); assertEquals(1, gateway.lookups); assertEquals(0, gateway.consumes)
        gateway.purchase.acknowledgementState = 0
        service.finalize(input(GoogleFinalizationAction.ACKNOWLEDGE)); assertEquals(1, gateway.acknowledges)
        gateway.purchase.acknowledgementState = 1
        service.finalize(input(GoogleFinalizationAction.ACKNOWLEDGE)); assertEquals(1, gateway.acknowledges)
    }
}
