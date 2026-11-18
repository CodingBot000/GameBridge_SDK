# Explicit Host integration (social extension)

Google iOS uses GoogleSignIn9.2.0, iOS OAuth client ID and Backend server client ID. Supply GIDClientID/GIDServerClientID and the reversed iOS client ID in CFBundleURLTypes. The sample plist uses GAMEBRIDGE_GOOGLE_IOS_CLIENT_ID, GAMEBRIDGE_GOOGLE_SERVER_CLIENT_ID and GAMEBRIDGE_GOOGLE_IOS_REVERSED_CLIENT_ID build settings; they are public client identifiers, not server secrets. Never add Apple private keys or Meta App Secret here.

Swift Host forwards its existing callback on the main actor:

```swift
func application(_ app: UIApplication, open url: URL,
                 options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
    GameBridgeGoogleHost.handle(url)
}
```

A Unity Host can forward from its own native AppController URL handler using the framework header's C ABI:

```objc
// Inside the Host's existing native URL handler; not a replacement AppDelegate.
const char *bytes = url.absoluteString.UTF8String;
if (GB_HandleAuthURL((const uint8_t *)bytes, (int32_t)strlen(bytes)) != 0) return YES;
// Continue the Host's existing handlers for other URLs.
```

Do not forward raw OAuth URLs through C# Application.deepLinkActivated, Unity events or logs. The new C ABI returns only an accepted flag. The SDK does not install/swap a delegate or automatically handle every URL.

The static GameBridgeNative framework references the official Google SDK; it is not a vendored copy of all Google/AppAuth resources. Native Hosts link the pinned GoogleSignIn SPM product. The Unity Xcode hook adds the same exact package to UnityFramework and records its own package GUID. A conflicting pre-existing Host package is rejected rather than overwritten. Xcode must resolve the dependency/resource bundles; archive success alone is not a consumer-link or real-login result.
