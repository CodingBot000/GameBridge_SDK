// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GameBridgeSourceConsumer",
    platforms: [.macOS(.v12)],
    dependencies: [.package(path: "..")],
    targets: [.executableTarget(name: "GameBridgeSourceConsumer", dependencies: [
        .product(name: "GameBridgeCore", package: "ios"),
        .product(name: "GameBridgeApple", package: "ios")
    ])]
)
