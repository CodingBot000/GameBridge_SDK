// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GameBridge",
    platforms: [.iOS(.v16), .macOS(.v12)],
    products: [.library(name: "GameBridgeCore", targets: ["GameBridgeCore"]),
               .library(name: "GameBridgeTesting", targets: ["GameBridgeTesting"]),
               .library(name: "GameBridgeApple", targets: ["GameBridgeApple"]),
               .library(name: "GameBridgeUnityBridge", type: .static, targets: ["GameBridgeUnityBridge"])],
    dependencies: [.package(url: "https://github.com/google/GoogleSignIn-iOS", exact: "9.2.0")],
    targets: [
        .target(name: "GameBridgeCore"),
        .target(name: "GameBridgeTesting", dependencies: ["GameBridgeCore"]),
        .target(name: "GameBridgeApple", dependencies: ["GameBridgeCore", .product(name: "GoogleSignIn", package: "GoogleSignIn-iOS", condition: .when(platforms: [.iOS]))]),
        .target(name: "GameBridgeUnityBridge", dependencies: ["GameBridgeCore", "GameBridgeApple"], path: "UnityBridge"),
        .testTarget(name: "GameBridgeCoreTests", dependencies: ["GameBridgeCore", "GameBridgeTesting", "GameBridgeUnityBridge", "GameBridgeApple"]),
    ]
)
