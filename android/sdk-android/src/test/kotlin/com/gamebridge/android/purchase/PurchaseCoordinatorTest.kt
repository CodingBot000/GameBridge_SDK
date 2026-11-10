package com.gamebridge.android.purchase

import com.gamebridge.SdkFailure
import org.junit.jupiter.api.Test
import java.util.UUID
import kotlin.test.*

class PurchaseCoordinatorTest {
    @Test fun `pending cannot grant and server grant is idempotent and bound`() {
        val user = UUID.randomUUID(); val binding = UUID.randomUUID(); val serverId = UUID.randomUUID()
        val coordinator = PurchaseCoordinator(user, binding, "coins_100")
        val grant = ServerGrant(user, binding, "coins_100", "store-transaction", serverId)
        coordinator.observe(StoreTransactionState.PENDING, "store-transaction")
        assertEquals("VERIFICATION_FAILED", assertFailsWith<SdkFailure> { coordinator.acceptServerGrant(grant) }.code)
        coordinator.observe(StoreTransactionState.PURCHASED, "store-transaction")
        assertEquals("PURCHASE_ACCOUNT_MISMATCH", assertFailsWith<SdkFailure> { coordinator.acceptServerGrant(grant.copy(userId = UUID.randomUUID())) }.code)
        assertEquals("PURCHASE_ACCOUNT_MISMATCH", assertFailsWith<SdkFailure> { coordinator.acceptServerGrant(grant.copy(bindingId = UUID.randomUUID())) }.code)
        assertTrue(coordinator.acceptServerGrant(grant)); assertFalse(coordinator.acceptServerGrant(grant))
        assertEquals(FinalizationPhase.PENDING, coordinator.snapshot().finalization)
        coordinator.finalized(); coordinator.finalized(); assertEquals(FinalizationPhase.FINALIZED, coordinator.snapshot().finalization)
        assertEquals("INVALID_ARGUMENT", assertFailsWith<SdkFailure> { coordinator.observe(StoreTransactionState.PENDING) }.code)
    }
}
