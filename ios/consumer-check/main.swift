import GameBridgeNative

@main
struct ConsumerCheck {
    @MainActor static func main() {
        _ = ApplePushHostAdapter()
        precondition(GB_ProtocolVersion() == 1)
    }
}
