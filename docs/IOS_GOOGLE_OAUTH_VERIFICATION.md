# iOS Google OAuth verification

Native and Unity iOS Simulator sign-in with a real Google test account passed on **2026-11-20 (KST)**. Both apps used the same local HTTPS sandbox and the Web client audience. The Unity export integration was added and tested separately on **2026-11-22**. The callback in the previous real-account Unity run was attached locally to the generated project.

| Check | Native app | Unity iOS Player |
| --- | --- | --- |
| Build input | Native Host at `e76d066`, with local client configuration | Packaged SDK manifest SHA-256 `997fd8dea785aafa859c7ddb319492a101583bc6b59978e799ff3c8952a8bf36`, isolated C# test scene and locally attached native forwarding |
| Environment | iOS 18.6 iPhone 16 Simulator, ad-hoc signing, `com.gamebridge.sdk.googleoauth.test` | Unity 6000.5.8f1, the same Simulator and signing, `com.gamebridge.sdk.mockiosconsumer` |
| Account UI result | Native app showed SDK sign-in success after Google authorization | `SignInAsync(AuthProvider.GOOGLE)` returned a valid Google profile, confirmed by `GB_UNITY_GOOGLE SIGN_IN PASS` |
| Backend evidence at the time | One consumed Google challenge, one Google identity, one active SDK session | Consumed Google challenges increased from one to two, Google identity count stayed one, SDK sessions increased from one to two in total |
| Earlier failed attempt | `AUTH_FAILED`; no active session. Its challenge had expired when inspected. The exact cause was not established. | The final configured Player succeeded. Earlier Unity compilation failures were resolved before the account test. |

Both apps used `gamebridge-google-oauth-test` and `https://localhost:18443`, with certificate verification enabled. The Backend consumed a fresh challenge and created the session after validating the Google proof. The count of active sessions was one at each recorded inspection. The older session and new session were distinguished using the cumulative count. Native records are in `631fda2` and Unity records are in `bfbc644`. The [sanitized evidence](evidence/ios-google-oauth-verification.json) contains aggregates and build provenance.

Account restoration, refresh, cancellation, logout and physical-device sign-in were not exercised for either Host. No new Google account sign-in was run for the export change.

## Configure a fresh Unity export

1. Install the staged `com.gamebridge.sdk` with the matching iOS XCFramework. Select the iOS build target and use the bundle ID registered with the app's own iOS OAuth client.
2. For a standard Unity-generated AppController, add `GAMEBRIDGE_IOS_GOOGLE_AUTH_CALLBACK` in Player Settings under iOS **Scripting Define Symbols**, then export. For a custom AppController, scene delegate or Unity as a Library, use the actual Host URL delegate and the [native forwarding example](../ios/host-examples/SocialAuthCallbacks.md). Choose one forwarding path.
3. Supply the iOS Client ID as `GIDClientID`, the Web Client ID as `GIDServerClientID`, and the reversed **iOS** Client ID as a URL scheme in the exported app's Info.plist. Apply these with the Host's build settings or plist postprocessor. Keep account configuration in ignored local files. The Backend `GAMEBRIDGE_AUTH_AUDIENCES_JSON` entry for the app scope must allow that exact Web Client ID.
4. Build the iOS target, install on a Simulator that trusts the local CA, and set the SDK to `PLATFORM_SANDBOX` with the trusted HTTPS Backend URL. The test path uses `SignInAsync(AuthProvider.GOOGLE)`. The [preparation record](IOS_GOOGLE_OAUTH_PREP.md) describes the local Backend and Native Host setup.

The opt-in export hook uses Unity's existing iOS postprocessor. It inserts one native block at the start of the supported generated URL method. The lifecycle follow-up below covers the stock SceneDelegate paths as well. A URL with the registered Google callback scheme goes to `GB_HandleAuthURL` and is consumed before Unity's managed URL notification. Other schemes use the existing handler. An absent or changed handler, or a competing forwarding block in the generated controller, causes the opt-in export to fail with an explanation. The native SDK preflight separately validates the OAuth configuration. The hook leaves signing, Info.plist settings and the GoogleSignIn 9.2.0 / Meta 18.1.1 package versions under their existing owners.

References: [Google iOS redirect handling](https://developers.google.com/identity/sign-in/ios/sign-in), [Unity iOS Xcode project structure](https://docs.unity3d.com/Manual/StructureOfXcodeProject.html), [Unity as a Library for iOS](https://docs.unity3d.com/Manual/UnityasaLibrary-iOS.html).

## Callback regression

`scripts/smoke-ios-hook.sh` uses the Unity iOS Xcode assemblies and checks callback ownership, failure on missing or conflicting hooks, preservation of the fallback handler, idempotence and the Swift package graph. `scripts/smoke-unity-ios-hook-repeat.sh` produces a new export in an isolated consumer and runs the hook twice more against it. For a local run, set `GAMEBRIDGE_UPM_STAGING` and `GAMEBRIDGE_UNITY_PACKAGE_CACHE` to a verified staged package and resolved package cache, and set `PYTHONPATH="$PWD/harness"`. The fixture sets the iOS define itself. Use a new output directory when repeating the entire export.

| Regression (2026-11-22 KST) | Result |
| --- | --- |
| Independent hook fixture | Exit 0, 62 PBX and URL callback checks |
| First fresh Unity export and repeat hook | Exit 0, `GB_IOS_HOOK_REPEAT PASS` |
| Second fresh Unity export | Exit 0, repeat hook marker present; AppController byte-identical to the first export |
| Xcode Debug Simulator arm64 build | Exit 0; callback C ABI and existing protocol/dispatch symbols linked; final app signature verified |
| Provider dependencies | GoogleSignIn 9.2.0 and Meta 18.1.1 resolved; all four required Meta frameworks linked, embedded and signature-verified |

The regression was run with Unity 6000.5.8f1. The fresh Xcode app was built and checked on disk. This run did not install it, open an OAuth URL or launch an account session.

## Session lifecycle and automatic callback (2026-11-23 KST)

The lifecycle run starts from `ab75800af6fdf77dd9acc3adfb491f15622a29e2` (PR #7 merged). The existing Google test app scope and loopback HTTPS backend were reused. A new iOS 18.6 iPhone 16 Simulator was created for this run, with the existing development CA trusted only in that simulator. The CA-backed endpoint was reachable and its leaf certificate was valid at execution time. Existing simulator data and previous server session rows were preserved.

The Unity 6000.5.8f1 baseline consumer used staging manifest SHA-256 `cf27a37346525d62189511f05dec21ab6e20fa4a6bd132d2c8b2ac382294b36f`. The restaged callback fix uses `b318a58bb2bd50b78ba068e5794482198069a5b055ae30388e559e0b417b2f0b`. To reproduce the export, prepare a new consumer with `scripts/prepare-unity-ios-mock.sh --prepare`, replace its scenario script with [the lifecycle fixture](../tests/UnityIosGoogleLifecycle/MockIosPlayerScenario.cs), and enable the built-in IMGUI module for that fixture. Use the iOS scripting define and remove the development-only loopback HTTP exception in the consumer export hook. The lifecycle build uses trusted HTTPS. Compare the two bundle-specific iOS IDs, reverse schemes and common server audience in the signed app. Xcode 26.6 (17F113) built both apps. Both Unity exports applied their respective hooks automatically. The fixed output passed repeated-hook checks for the AppController, scene, PBX and XCFramework. The independent hook fixture passed 71 checks. The signed Player contains four Meta frameworks and resolves the unchanged GoogleSignIn 9.2.0 and Meta 18.1.1 dependencies.

### Real-account results

- Native sign-in, cold-launch restore and logout passed. The restore created neither a new challenge nor a new session. The isolated DB showed exactly the session issued during this test revoked; restoring after logout returned no SDK session.
- On the same Native app, canceling the Google sheet returned `CANCELED`. The canceled challenge was unused and created no SDK session. Opening the next login reached the Google sheet with no `BUSY` response. The reopened challenge expired while awaiting the account action. A successful sign-in after this Native cancellation was not observed.
- The first Unity Player with the PR #7 hook passed build and signing, but a synthetic URL for the registered scheme reached the Unity handler (one managed event, zero ABI breakpoint hits). The export's stock UnityScene forwarded URLs independently of the AppController. The hook now handles scene warm URLs before `UnitySetAbsoluteURL` and clears owned scene cold URLs before Unity reads the pending URL. After a fresh export and rebuild, a synthetic warm URL hit the C ABI entry once, produced zero C# URL events and caused no DB changes. There were no real credentials in the synthetic URL.
- The rebuilt Unity Player passed the Google UI cancellation check. It returned `CANCELED`, left its challenge unused, created no session and opened the next Google sheet without a restart. The first two account windows timed out without a session. After starting a fresh request in the Unity test app, the user completed real Google sign-in. The Player reported `SIGN_IN PASS URL_EVENTS 0`. The Backend consumed one new challenge and issued one session for the existing Google identity.
- A cold launch of the Unity app then restored the same SDK session without showing Google UI or creating a new challenge or session. Unity logout revoked precisely the session issued during this test. A subsequent restore returned `NO_SESSION`. The earlier Native and historical session rows were unchanged by Unity logout.
- The signed Unity app contained the automatically generated AppController and SceneDelegate forwarding. The live OAuth run did not hit the `GB_HandleAuthURL` breakpoint. AppAuth's iOS web authentication session can deliver its OAuth response directly to its completion handler. The observed runtime proof for the AppController/Scene forwarding change is the separate synthetic warm URL. The scene cold path passed export/source checks; direct cold URL injection was not run.

### Synthetic lifecycle checks

- Swift `SocialAuthProviderTests`: 10 tests, exit 0. Concurrent restores shared one refresh, rotation persisted the replacement credential, failed rotation did not replay an old token from storage, and sign-out during refresh canceled the client operation and reported server revocation as unconfirmed.
- Backend targeted Google HTTP regressions: 2 tests, exit 0 on a separate synthetic DB. It expired only its own synthetic access token and verified refresh rotation, old refresh rejection, family revocation on replay, continued use of a sibling session, and access/refresh rejection after logout. A repeated synthetic challenge was rejected with HTTP 409 and produced no second session.
- Real SDK-token refresh and replay using credentials from the user session were not exercised in these fixtures. The Swift cancellation regression, duplicate/late credential rejection and Backend replay checks do not substitute for observing live Google UI after cancel.

Google's [iOS reference](https://developers.google.com/identity/sign-in/ios/reference/Classes/GIDSignIn) documents interactive completion and the separate sign-out/disconnect operations. The existing gateway keeps the interaction owner until the Google callback completes. The managed Unity cancellation token stops waiting for a bridge result, and the user's dismissal of the Google sheet is a separate operation.
