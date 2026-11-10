# Native Mock and Sandbox Demo

Import this UPM sample, add `NativeDemo` to an empty GameObject, and provide a compatible EventSystem and the Unity UI package in the scene/project. This sample is intended for Android or iOS players; the Editor Offline Demo is separate.

Choose LOCAL_MOCK or PLATFORM_SANDBOX before initializing. Enter the Backend URL at runtime. LOCAL_MOCK additionally requires the local development key; Android emulators normally reach the host through `10.0.2.2`. Do not place development keys, service credentials, signing keys, or tokens in scenes, assets, logs, or Git. The development key field is cleared after successful initialization.

Sandbox login and store use the user's configured Backend and platform test accounts. Supply the two real test product IDs and, for Android, the Google server client ID. Push registration additionally requires a host-managed installation UUID and platform setup in `docs/USER_SETUP.md`. Android hosts must forward existing Firebase service/Activity callbacks as shown in `android/host-examples/UnityPushForwarding.kt.example`.

For iOS host-managed push, explicitly add `NativeDemoIosPush` to a scene GameObject. Its notification listener suppresses the Unity Notifications package's default foreground presentation. Permission is requested only when the user presses the permission or registration action. If the host component is absent, iOS push registration is unavailable.

The display distinguishes LOCAL_MOCK and PLATFORM_SANDBOX. A pending purchase is not a grant; a verified purchase update triggers a server balance refresh. The Backend's local SIMULATED push response is not a remote notification. Unity Editor/IL2CPP, platform sandbox accounts, and real remote push require the separate verification steps in the project documentation.
