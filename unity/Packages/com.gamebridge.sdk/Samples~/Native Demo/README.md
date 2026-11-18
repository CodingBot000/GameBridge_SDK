# Native Mock and Sandbox Demo

Import this UPM sample, add `NativeDemo` to an empty GameObject, and provide a compatible EventSystem and the Unity UI package in the scene/project. This sample is intended for Android or iOS players; the Editor Offline Demo is separate.

Choose LOCAL_MOCK or PLATFORM_SANDBOX before initializing. Enter the Backend URL at runtime. LOCAL_MOCK additionally requires the local development key; Android emulators normally reach the host through `10.0.2.2`. Do not place development keys, service credentials, signing keys, or tokens in scenes, assets, logs, or Git. The development key field is cleared after successful initialization.

Sandbox login and store use the user's configured Backend and platform test accounts. Supply the two real test product IDs and, for Android, the Google server client ID. Push registration additionally requires a host-managed installation UUID and platform setup in `docs/USER_SETUP.md`. Android hosts must forward existing Firebase service/Activity callbacks as shown in `android/host-examples/UnityPushForwarding.kt.example`.

For iOS host-managed push, explicitly add `NativeDemoIosPush` to a scene GameObject. Its notification listener suppresses the Unity Notifications package's default foreground presentation. Permission is requested only when the user presses the permission or registration action. If the host component is absent, iOS push registration is unavailable.

The display distinguishes LOCAL_MOCK and PLATFORM_SANDBOX. A pending purchase is not a grant; a verified purchase update triggers a server balance refresh. The Backend's local SIMULATED push response is not a remote notification. Unity Editor/IL2CPP, platform sandbox accounts, and real remote push require the separate verification steps in the project documentation.

The document37 social extension adds explicit Google, Apple and Facebook sandbox buttons. Google runs on Android and iOS; Apple uses AuthenticationServices on iOS and official web OAuth/Custom Tabs on Android; Facebook uses Android Classic and iOS Limited(default)/Classic. All require a configured Backend and Native Host callbacks/settings. No provider failure falls back to Mock.

For iOS provide Google iOS/server client IDs, reversed URL scheme, Meta App ID/Client Token and fb scheme; explicitly forward URLs via GB_HandleAuthURL and initialize Meta from the existing Host AppDelegate. For Android include the optional Meta18.3.0 dependency and forward Activity results; Apple requires public Services ID/HTTPS return metadata, verified App Link assetlinks and Native onNewIntent/cold-launch handling. Never forward raw auth URLs via Unity Application.deepLinkActivated. Apple p8/client secret and Meta App Secret stay on Backend. Follow the repository's docs/USER_SETUP.md and android/host-examples/ios/host-examples; do not serialize credentials into this sample.

Native/Fake/contract/package builds passed locally. Real Google/Meta/Apple account login and a new Unity Player run for this extension have not been executed. Meta18.1.1 iOS remote binary downloads were deferred; local builds used upstream-supported, checksum/signature-verified official binaries. See docs/SOCIAL_AUTH_HANDOFF.md in the source checkout for exact evidence and limitations.
