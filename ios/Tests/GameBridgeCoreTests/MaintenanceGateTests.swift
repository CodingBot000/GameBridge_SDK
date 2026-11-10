import XCTest
@testable import GameBridgeCore

final class MaintenanceGateTests: XCTestCase {
    func testMaintenanceBlocksOnlyNewPurchase() {
        XCTAssertFalse(MaintenanceGate.permits(maintenanceEnabled: true, operation: .startPurchase))
        for operation: ProtectedOperation in [.verifyPurchase, .recoverPurchase, .signOut] {
            XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: true, operation: operation))
        }
        XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: false, operation: .startPurchase))
    }
}
