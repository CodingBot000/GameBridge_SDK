import Foundation

public enum ProtectedOperation { case startPurchase, verifyPurchase, recoverPurchase, signOut }
public enum MaintenanceGate {
    public static func permits(maintenanceEnabled: Bool?, operation: ProtectedOperation) -> Bool {
        operation != .startPurchase || maintenanceEnabled == false
    }
}
