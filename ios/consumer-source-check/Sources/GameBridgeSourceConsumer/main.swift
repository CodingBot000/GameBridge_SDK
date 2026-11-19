import GameBridgeCore
import GameBridgeApple

let configuration = GameBridgeConfig(appId: "independent-consumer", mode: .editorOffline, backendBaseURL: nil)
precondition(configuration.appId == "independent-consumer")
print("GameBridge independent SwiftPM source consumer PASS")
