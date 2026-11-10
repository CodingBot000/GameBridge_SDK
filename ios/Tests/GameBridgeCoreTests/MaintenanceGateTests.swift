import XCTest
@testable import GameBridgeCore

final class MaintenanceGateTests: XCTestCase {
    func testMaintenanceBlocksOnlyNewPurchase() {
        XCTAssertFalse(MaintenanceGate.permits(maintenanceEnabled: true, operation: .startPurchase))
        XCTAssertFalse(MaintenanceGate.permits(maintenanceEnabled: nil, operation: .startPurchase))
        for operation: ProtectedOperation in [.verifyPurchase, .recoverPurchase, .signOut] {
            XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: true, operation: operation))
            XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: nil, operation: operation))
        }
        XCTAssertTrue(MaintenanceGate.permits(maintenanceEnabled: false, operation: .startPurchase))
    }
}
