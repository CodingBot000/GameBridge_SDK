package com.gamebridge

import org.junit.jupiter.api.Test
import kotlin.test.*

class MaintenanceGateTest {
    @Test fun `maintenance blocks only new purchase`() {
        assertFalse(MaintenanceGate.permits(true, ProtectedOperation.START_PURCHASE))
        assertFalse(MaintenanceGate.permits(null, ProtectedOperation.START_PURCHASE))
        for (operation in listOf(ProtectedOperation.VERIFY_PURCHASE, ProtectedOperation.RECOVER_PURCHASE, ProtectedOperation.SIGN_OUT))
            { assertTrue(MaintenanceGate.permits(true, operation)); assertTrue(MaintenanceGate.permits(null, operation)) }
        for (operation in ProtectedOperation.entries) assertTrue(MaintenanceGate.permits(false, operation))
    }
}
