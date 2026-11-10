// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GameBridge",
    platforms: [.iOS(.v16), .macOS(.v12)],
    products: [.library(name: "GameBridgeCore", targets: ["GameBridgeCore"]),
               .library(name: "GameBridgeTesting", targets: ["GameBridgeTesting"])],
    targets: [
        .target(name: "GameBridgeCore"),
        .target(name: "GameBridgeTesting", dependencies: ["GameBridgeCore"]),
        .testTarget(name: "GameBridgeCoreTests", dependencies: ["GameBridgeCore", "GameBridgeTesting"]),
    ]
)
