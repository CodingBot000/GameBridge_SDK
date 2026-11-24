# iOS Google OAuth preparation — document43

**Current status:** Native and Unity iOS Simulator real Google sign-in passed on 2026-11-20. The 2026-11-23 lifecycle run also verified restore, Google UI cancellation, logout and account sign-in on the automatically exported Unity Player. See [current verification and Unity export setup](IOS_GOOGLE_OAUTH_VERIFICATION.md) for limitations, including synthetic-only refresh/replay and warm URL routing. The `NOT_RUN` values below describe the original preparation run.

Base:76c90b2bfec3ec9c5da34399e9f59f0193fe4e16. Preparation only; real OAuth, Console creation/login/consent, push/PR/main merge and Release are NOT_RUN.

## Exact Native and Unity identities

First use the independent **GameBridgeGoogleOAuthHost** scheme, **com.gamebridge.sdk.googleoauth.test** Bundle ID, **gamebridge-google-oauth-test** GameBridge app scope, PLATFORM_SANDBOX mode. GoogleSignIn9.2.0 and the existing nonce/challenge/JWT contract are unchanged.

The prepared Native Host runs on a dedicated iOS18.6 iPhone16 Simulator with local ad-hoc signing; no Apple Developer provisioning is used. Existing SampleApp uses com.gamebridge.sdk.sample.dev20261110 but mixes Mock/Apple/push controls, so it is not the selected first Google account Host. Physical-device testing needs user Team/provisioning and reachable LAN HTTPS with a matching trusted certificate; phone localhost is not the Mac.

The Host exposes manual Google sign-in/cancel/SDK-session restore/logout. Login is gated by public IDs/scheme preflight; no automatic account sign-in or restore. SwiftUI onOpenURL and AppDelegate openURL forward to GameBridgeGoogleHost.handle without logging callbacks. The preparation launch requests only public HTTPS config. Errors are sanitized codes, storage is a dedicated Native Keychain service, and no token/client secret is exposed.

Cancel/retry/restore/logout still require actual account tests later. The existing Google UI gate can remain BUSY until the real SDK callback returns; restart the test Host if the callback never arrives. No real cancellation outcome was verified here.

## User-owned Console clients

Create/select the user's Google Cloud test project, OAuth consent/audience and permitted test accounts. External Testing with the intended test user is suitable for personal testing; organization Internal policies are user-controlled.

| OAuth client | Identifier / purpose |
| --- | --- |
| iOS, first Native phase | com.gamebridge.sdk.googleoauth.test |
| Web application | Backend/server Client ID, used as the ID-token audience |
| iOS, later Unity phase | com.gamebridge.sdk.mockiosconsumer, only after Native account success |

Different iOS bundles require their own iOS Client IDs. The intended Web Client ID can be reused for the same allowed Backend scope. This existing ID-token signature verification flow does not need a Google client secret or service-account key. The agent did not create Console resources or perform user login/consent. Any organization/App Check enforcement is an additional user-controlled prerequisite, not bypassed.

Official references: [iOS setup](https://developers.google.com/identity/sign-in/ios/start-integrating), [backend authentication](https://developers.google.com/identity/sign-in/ios/backend-auth), [serverClientID audience](https://developers.google.com/identity/sign-in/ios/reference/Classes/GIDConfiguration).

## Where to inject public IDs

Copy ios/GoogleOAuthHost/GoogleOAuth.xcconfig.example to ignored ios/GoogleOAuthHost/GoogleOAuth.local.xcconfig:

| Build setting | Destination |
| --- | --- |
| GAMEBRIDGE_GOOGLE_IOS_CLIENT_ID | Info.plist GIDClientID |
| GAMEBRIDGE_GOOGLE_SERVER_CLIENT_ID | GIDServerClientID |
| GAMEBRIDGE_GOOGLE_IOS_REVERSED_CLIENT_ID | CFBundleURLTypes/CFBundleURLSchemes; reverse the iOS client, not the Web client |
| GAMEBRIDGE_GOOGLE_APP_ID | GameBridgeAppID; gamebridge-google-oauth-test |
| GAMEBRIDGE_GOOGLE_BACKEND_HOST /PORT | GameBridgeBackendURL; https://localhost:18443 |

Copy config/google-oauth-audiences.example.json to ignored config/google-oauth-audiences.local.json. Its GOOGLE array must contain the exact **Web Client ID**, keyed by gamebridge-google-oauth-test. The local launcher passes this JSON into GAMEBRIDGE_AUTH_AUDIENCES_JSON. A Native configuration check does not prove Console client type or Backend audience correctness.

GoogleSignIn receives the existing raw server challenge nonce. Backend checks signature/issuer/expiry/audience/nonce and consumes the challenge once. No TLS override, ATS HTTP exception or Mock fallback is added.

## Prepared local HTTPS and sandbox DB

- URL **https://localhost:18443**, loopback only, Spring sandbox profile.
- New DB **gamebridge_ci_f0ab9b0dfb**, existing local PostgreSQL container/port54329; no existing DB/volume reset.
- Local CA/server certificate/PKCS12 in the ignored run directory; private files0600. CA trust is installed only in the new owned Simulator; macOS/system trust is unchanged.
- Simulator **36AF68C1-490B-4D2C-965E-022B0B97E4F5**, GameBridge-Google-OAuth-Prep-0617a027, iOS18.6.
- Certificate expiry **2026-11-27 18:50:57 Asia/Seoul**; renew/retrust this preparation environment after expiry, never disable verification.
- Verified health200/config200 with CA+hostname validation, Mac curl without CA exit60, and Native URLSession/SDK HTTPS config PASS with no ATS exception.
- IDs/audience are absent: challenge returns503 CONFIG_REQUIRED; session/identity/challenge counts all0. This is expected fail-closed preparation, not account OAuth PASS.
- Backend is running locally with its owned PID/jar recorded; status/stop/start operate only on that process. Secrets remain in ignored0600 files and are not reproduced here.

New checkouts do not contain generated jar/certificates/private environment/Simulator. The following paths are actual prepared local paths, not portable generated assets.

## Commands after Console setup — account execution NOT_RUN here

```sh
cd /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/google-oauth43-0jo7b1cn/source
export GOOGLE_PREP_RUN="$PWD/artifacts/google-oauth-prep.3ms136td"
export GOOGLE_PREP_PROJECT="$PWD/artifacts/ios-project.K3bhDR/ios/Framework/GameBridgeSample.xcodeproj"
export GOOGLE_PREP_SIM="36AF68C1-490B-4D2C-965E-022B0B97E4F5"

cp ios/GoogleOAuthHost/GoogleOAuth.xcconfig.example ios/GoogleOAuthHost/GoogleOAuth.local.xcconfig
cp config/google-oauth-audiences.example.json config/google-oauth-audiences.local.json
# Edit both ignored files: replace placeholders with public Console IDs; no secrets/tokens.

python3 "$GOOGLE_PREP_RUN/backend-control.py" stop
python3 "$GOOGLE_PREP_RUN/backend-control.py" start   --audiences "$PWD/config/google-oauth-audiences.local.json"
xcodebuild -project "$GOOGLE_PREP_PROJECT" -scheme GameBridgeGoogleOAuthHost   -configuration Debug -sdk iphonesimulator -destination "id=$GOOGLE_PREP_SIM"   -derivedDataPath "$GOOGLE_PREP_RUN/AccountTestDerived"   -xcconfig "$PWD/ios/GoogleOAuthHost/GoogleOAuth.local.xcconfig"   CODE_SIGN_IDENTITY=- CODE_SIGNING_REQUIRED=YES build
xcrun simctl install "$GOOGLE_PREP_SIM"   "$GOOGLE_PREP_RUN/AccountTestDerived/Build/Products/Debug-iphonesimulator/GameBridgeGoogleOAuthHost.app"
xcrun simctl launch --terminate-running-process "$GOOGLE_PREP_SIM" com.gamebridge.sdk.googleoauth.test
```

If the owned Simulator was shut down, boot only that UUID and wait for bootstatus before install/launch. Then manually press Check configuration → Check HTTPS Backend → Google sign-in. The user performs login/consent and cancel/retry/restore/logout in the next authorized stage. Never print provider/SDK tokens. The xcconfig override was checked using synthetic public IDs via showBuildSettings only; no such app was rebuilt/launched.

Current preparation control:

```sh
python3 "$GOOGLE_PREP_RUN/backend-control.py" status
python3 "$GOOGLE_PREP_RUN/backend-control.py" stop
```

## Unity follow-on and remaining blockers

After Native real-account success, use Unity bundle **com.gamebridge.sdk.mockiosconsumer** with its own iOS Client ID in exported Info.plist GIDClientID/reversed URL scheme. Supply the same intended Web Client ID via GIDServerClientID and/or GameBridgeConfig.googleServerClientId; if both are set they must agree. Use PLATFORM_SANDBOX, the HTTPS URL/app scope, and the existing Demo Google button. The Host's native AppController must consume GB_HandleAuthURL before URLs bubble into Unity. No Unity OAuth build/callback integration/SignInAsync(GOOGLE) was performed here.

Required next: user Console project/consent/test user, real iOS/Web Client IDs, matching scheme and Backend audience. Physical-device signing/LAN certificate and extra organization policies are unprepared. Real OAuth remains WAITING_USER/NOT_RUN. Other providers, payments, push and Release are out of scope.

Evidence lives under artifacts/google-oauth-prep.3ms136td: native-host-readiness.json, https-preflight.json, config-injection-test.json, native-readiness.log, environment.json. Private backend-env.private.json/tls keys are intentionally not Git/report content. The built app screenshot shows WAITING_USER and HTTPS/config PASS. Initial artifact-helper log-handle and app-launch-env control issues were corrected without recreating DB/keys or attempting OAuth.
