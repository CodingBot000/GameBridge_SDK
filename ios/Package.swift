// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GameBridge",
    platforms: [.iOS(.v16)],
    products: [.library(name: "GameBridgeCore", targets: ["GameBridgeCore"])],
    targets: [
        .target(name: "GameBridgeCore"),
        .testTarget(name: "GameBridgeCoreTests", dependencies: ["GameBridgeCore"]),
    ]
)
