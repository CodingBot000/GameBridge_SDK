// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GameBridge",
    platforms: [.iOS(.v16), .macOS(.v12)],
    products: [.library(name: "GameBridgeCore", targets: ["GameBridgeCore"]),
               .library(name: "GameBridgeTesting", targets: ["GameBridgeTesting"]),
               .library(name: "GameBridgeApple", targets: ["GameBridgeApple"]),
               .library(name: "GameBridgeUnityBridge", type: .static, targets: ["GameBridgeUnityBridge"])],
    targets: [
        .target(name: "GameBridgeCore"),
        .target(name: "GameBridgeTesting", dependencies: ["GameBridgeCore"]),
        .target(name: "GameBridgeApple", dependencies: ["GameBridgeCore"]),
        .target(name: "GameBridgeUnityBridge", dependencies: ["GameBridgeCore", "GameBridgeApple"], path: "UnityBridge"),
        .testTarget(name: "GameBridgeCoreTests", dependencies: ["GameBridgeCore", "GameBridgeTesting", "GameBridgeUnityBridge", "GameBridgeApple"]),
    ]
)
