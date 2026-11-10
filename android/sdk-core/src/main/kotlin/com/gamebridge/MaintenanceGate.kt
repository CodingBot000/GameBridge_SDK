package com.gamebridge

enum class ProtectedOperation { START_PURCHASE, VERIFY_PURCHASE, RECOVER_PURCHASE, SIGN_OUT }
object MaintenanceGate {
    fun permits(maintenanceEnabled: Boolean?, operation: ProtectedOperation): Boolean =
        operation != ProtectedOperation.START_PURCHASE || maintenanceEnabled == false
}
