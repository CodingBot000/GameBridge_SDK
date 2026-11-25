# 선택적 실서비스 연동 준비

> 현재 Provider별 상태는 [기능 매트릭스](FEATURE_MATRIX.md), 이전 이력은 [SOCIAL_AUTH_HANDOFF](SOCIAL_AUTH_HANDOFF.md)를 따릅니다. 실제 Google 검증은 [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md)에 있습니다.


현재 Android API 34 AVD 및 iOS 18.6 Simulator Native·Unity에서 Google 실제 계정 로그인·복원·UI 취소·로그아웃 및 해당 Backend 세션 폐기를 확인했습니다. 신규 환경에서는 여전히 OAuth 콘솔·Host·Backend 설정이 필요합니다. 문서36 당시 13개 외부 연동 Task 집계는 소급 변경하지 않습니다. [Quick Start](INTEGRATION.md) · [COMPATIBILITY](COMPATIBILITY.md).

## 다음 단계 — 실제 소셜 로그인 검증 준비

Android/iOS LOCAL_MOCK과 실제 Google OAuth 결과를 분리합니다. 양 플랫폼 Apple/Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs, 실기기 및 실제 Google 갱신/replay는 별도 승인·설정 후 검증합니다. iOS Native 취소 후 재로그인 성공도 미확인입니다.

| 시험 경로 | 사용자가 준비해야 하는 사항 | 코드·테스트 준비 상태 |
| --- | --- | --- |
| Android Google | APK applicationId·서명 SHA-1, Web Client ID·Backend audience, 테스트 계정·신뢰된 HTTPS | Native/Unity API 34 AVD 로그인·취소 후 재시도·복원·로그아웃 PASS |
| iOS Google | Bundle별 iOS OAuth Client ID, Backend Web Client ID, URL Scheme·테스트 계정·신뢰된 HTTPS | GoogleSignIn 9.2.0; Native/Unity 실제 Simulator 로그인·복원·UI 취소·로그아웃 PASS (실계정 refresh/replay NOT_RUN) |
| Android Facebook | Meta App ID/Client Token, Android 패키지·서명 Key Hash·테스트 계정·서버 전용 App Secret | Meta 18.3.0 Classic, Backend debug 검증·Fake/계약 PASS |
| iOS Facebook | 동일 Meta 앱의 iOS 플랫폼 설정·URL Scheme·테스트 계정 및 Backend App Secret | Meta 18.1.1 Limited/Classic·Backend JWT 검증·Fake/계약 PASS |
| Android Apple | Apple Developer Primary App ID·Services ID, Team/Key ID·서버 전용 p8, 소유 HTTPS callback/return 도메인·Android App Links | 웹 OAuth·Custom Tabs·서버 code 교환·일회용 handle 구현·보안 테스트 PASS |

새로운 Provider 또는 새 환경을 검증할 때는 **1개 플랫폼/Provider를 선택해 시험용 Host 앱과 별도 Backend Sandbox에서 실행**합니다. 단순 로그인 성공뿐 아니라 Provider 계정과 GameBridge Backend 사용자·세션 결속, 취소·재시도·세션 복원·로그아웃을 확인하고 나머지 경로로 확장합니다. 새 Unity Player의 LOCAL_MOCK 결과를 실제 OAuth PASS로 승격하지 않습니다.

**보안:** 실제 App Secret·Apple p8·로그인 토큰·개인 식별 정보는 Git/Unity 에셋/채팅/원본 로그에 넣지 않습니다. 사용자 로컬 비밀 저장소에서 공급하고, Codex는 사용자의 콘솔 로그인·약관 동의·비밀키 발급을 자동으로 가정하지 않습니다.

## 준비·권한 경계

| ID | 코드/로컬 준비 | 사용자가 할 일 | 현재 실연동 |
| --- | --- | --- | --- |
| USER-GIT | 실제 identity로 commit/FF 인계 및 Hosted 기록 존재 | 이미 설정된 계정/identity 유지 | 포트폴리오 Git 인계와 Provider 인증은 별개 |
| USER-UNITY |6000.5.8f1·모듈·새 양 Player 실제 검증 | 자기 환경의 Editor·module·license 준비, 약관/로그인 직접 처리 | 전용 self-hosted/Release는 미검증 |
| USER-DEVICE | Android API34 AVD/iOS18.6 Simulator, 무서명 archive·ad-hoc Simulator | 실제 단말·앱 ID·서명·capability·기기 신뢰 | 실기기 미검증 |
| USER-BACKEND | local/synthetic profile·DB·HTTP·verifier/sender 코드 | sandbox URL·별도 DB/role·secret 범위와 Provider 권한 준비 | 운영/외부 연결 미검증 |
| USER-AUTH-GOOGLE | Android Credential Manager, iOS GoogleSignIn/nonce·서버 verifier | Bundle/패키지별 Client ID·Web audience·서명 조건·테스트 계정 | Android AVD·iOS Simulator Native/Unity 실계정 및 기본 세션 수명 PASS; 실계정 refresh/replay·실기기 NOT_RUN |
| USER-AUTH-APPLE | AuthenticationServices·nonce·서버 verifier·fake 경계 | Bundle/App ID·Sign in with Apple capability·audience·서명·계정 | WAITING_USER |
| USER-BILLING-GOOGLE | Play Billing·검증/Google finalizer·synthetic 회귀 | 앱/internal testing·일회성 두 상품·테스터·서버 서비스 계정 권한 | WAITING_USER |
| USER-BILLING-APPLE | StoreKit2·검증/finish·Xcode 로컬 일부 | App Store 상품·Sandbox tester·Bundle/환경·검증 신뢰 설정 | WAITING_USER, P05-T03 FAIL 별도 유지 |
| USER-PUSH-GOOGLE | FCM adapter/sender·fake HTTP | Firebase 프로젝트/앱·Host 초기화·google-services 설정·서버 권한 | WAITING_USER |
| USER-PUSH-APPLE | APNs adapter/sender·Host forwarding·fake HTTP | Push capability·aps-environment·topic/Team/Key·서버 .p8·실기기 | WAITING_USER |

실제 key·서명·계정 정보를 생성하거나 ChatGPT로 전송할 필요가 없습니다. 사용자가 자기 로컬 secret 파일/환경에서 설정합니다. Codex는 계정 로그인·약관 동의·키 발급/삭제를 대신하지 않습니다. 실서비스 시험은 별도로 명시 승인된 범위에서만 실행합니다.

## 현재 구현의 실제 설정 이름

아래는 [verify-external-config.py](../scripts/verify-external-config.py)와 현재 Backend loader가 사용하는 이름입니다. 과거 계획 변수명을 새 설정 이름으로 혼동하지 않습니다.

| 변수 | 앱별 JSON/파일 형태 | 연결 |
| --- | --- | --- |
| `GAMEBRIDGE_AUTH_AUDIENCES_JSON` | appId→GOOGLE/APPLE/FACEBOOK의 비어 있지 않은 문자열 배열 | OAuth/Apple audience와 서버 identity 검증 |
| `GAMEBRIDGE_FACEBOOK_AUTH_CONFIG_JSON` | appId→Meta appId·Backend 전용 appSecret·requiredScopes | Facebook Classic Access Token 검증 |
| `GAMEBRIDGE_APPLE_WEB_CONFIG_JSON` | appId→Services ID·callbackUri·returnUri·teamId·keyId·privateKeyPath | Android Apple 웹 OAuth 서버 code 교환 |
| `GAMEBRIDGE_GOOGLE_PURCHASE_CONFIG_JSON` | appId→packageName·productIds 문자열 배열·credentialPath | Google purchase/finalizer |
| `GAMEBRIDGE_APPLE_PURCHASE_CONFIG_JSON` | appId→bundleId·productIds 배열·rootCertificatePaths 파일 배열 | Apple server library 검증 |
| `GAMEBRIDGE_FCM_CONFIG_JSON` | appId→projectId·credentialPath | Firebase Admin 발송 |
| `GAMEBRIDGE_APNS_CONFIG_JSON` | appId→teamId·keyId·topic·privateKeyPath | APNs token-auth 발송 |
| `SERVER_PURCHASE_ENCRYPTION_KEY` | Base64 decode32 bytes | 서버 구매 증빙 암호화 |
| `SERVER_TOKEN_ENCRYPTION_KEY` | Base64 decode32 bytes | 서버 Push token 암호화 |

값은 예제 repository의 실제 서비스 credential이 아닙니다. 파일은 서버 로컬의 읽기 가능한 경로로 공급하며 SDK/UPM/Host 앱에 서버 credential을 내장하지 않습니다. 기존 DB 비밀번호·암호화키를 재실행 때 임의로 바꾸지 않습니다.

```sh
bash scripts/verify-external.sh --check-config
```

값을 출력하거나 Provider에 요청하지 않는 존재/기본 자료형 검사입니다. 마지막 실제 실행은7항목 모두 `MISSING_OR_INVALID`, exit2였습니다. 올바른 JSON과 파일이 있어도 identity·권한·앱 등록·상품·서명·네트워크·실제 기능 PASS가 되지는 않습니다. 배열 대신 문자열 등 잘못된 자료형은 성공으로 처리하지 않습니다.

## 실제 연동을 선택할 때의 순서

1. **도구·Host:** 기존 앱과 분리한 sandbox 앱/단말을 선택하고 app/package/bundle ID·서명·capability를 맞춥니다. Unity는 staged Native package와 같은 설치 조건을 사용합니다.
2. **Backend:** production과 다른 sandbox DB/role/URL·암호화키·최소 Provider 권한을 로컬에서 준비합니다. profile 표식 충돌은 기존 데이터를 지워 해결하지 않습니다.
3. **인증:** Google server client ID와 서버 audience, Apple bundle/audience/nonce를 맞춥니다. 실제 로그인→서버 검증→복원·갱신→취소·logout을 Native 앱과 Unity에서 각각 확인합니다. 토큰 원문은 기록하지 않습니다.
4. **스토어:** `coins_100/premium_unlock` 논리 ID를 실제 테스트 product ID에 매핑합니다. 가격은 스토어 localized price를 표시합니다. 정상/pending/cancel/재시작·복구/계정 불일치/지급 후 응답 유실과 서버 원장·완료 처리를 확인합니다. 실제 Google consume/ack는 서버 소유입니다.
5. **FCM/APNs:** Host의 기존 service/Activity 또는 Delegate/completion을 연결합니다. 권한 거부·token 회전·명시적 등록/해제·foreground/열기·logout 후 소유 해제를 확인하고, 원격 전달은 실제 단말에서 별도로 확인합니다.
6. **증거:** 사용한 source/package/checksum/OS·mode, 요청별 익명 requestId·status·원장 결과를 정제해 기록합니다. 준비 상태와 실제 PASS를 별도로 바꿉니다.

개발 send는 admin key·allowlist가 있어야 하고 LOCAL_MOCK의 `SIMULATED`/Sandbox의 `QUEUED`는 단말 전달 성공이 아닙니다. Xcode 로컬 StoreKit은 별도 개발 모드이며 실제 Apple 서버 증빙 검증을 대신하지 않습니다. iOS26.5 실패·18.6 간헐 위험은 [Known Limitations](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)에 남겨 두었습니다.

## 안전한 재실행 도구

[Android 소비 runner](../harness/run-unity-android-mock-e2e.py)는 staging과 명시한 전용 serial/AVD/PID·ADB 실행파일 및 build/runtime endpoint를 검증합니다. [iOS 소비 runner](../harness/run-unity-ios-mock-e2e.py)는 새 소비 프로젝트·Simulator·DB를 사용합니다. 실제 검증 명령·결과는 [배치34 증거](evidence/p10-batch34-integrated.md)에 있습니다. 자신의 환경에서 소유권과 조건을 확인하지 않은 채 과거 PID/UUID를 복사해 실행하지 않습니다.

원래 Strict는58개 required lane과 recorded P05 실패를 보존합니다. [preflight](../harness/strict-preflight.py)의 E2 생성/전 wrapper 소유권 계약이 아직 미완성이므로 전체 실행0회입니다. self-check9개 PASS를 전체 Strict로 해석하지 않습니다. self-hosted 등록·Unity opt-in·Release 준비는 이 포트폴리오 종료 작업에서 수행하지 않습니다.

과거 설정 지시는 Git의 이전 `USER_SETUP.md`와 WORK_LOG에 보존했습니다. 이후 작업은 명시적으로 실서비스 연동을 선택한 경우에만 진행하며, 위 목록을 자동 필수 배치로 전환하지 않습니다.

## 문서37 A — iOS Google (별도 승인 확장)

공식 GoogleSignIn-iOS9.2.0을pin했다. Google OAuth의iOS Client ID,Backend용Server Client ID,Bundle ID와reversed iOS Client ID URL Scheme을Host에설정한다. sample은 GIDClientID/GIDServerClientID 및CFBundleURLTypes를 build setting GAMEBRIDGE_GOOGLE_IOS_CLIENT_ID/GAMEBRIDGE_GOOGLE_SERVER_CLIENT_ID/GAMEBRIDGE_GOOGLE_IOS_REVERSED_CLIENT_ID로받는다. 값은public client identifier이며서버secret이아니다.

표준 Unity AppController 및 stock UnityScene을 사용하는 iOS 프로젝트는 iOS Scripting Define Symbols에 `GAMEBRIDGE_IOS_GOOGLE_AUTH_CALLBACK`을 추가한 후 Export한다. 별도 AppController/scene delegate 또는 Unity as a Library Host는 자동 연결을 끄고 실제 네이티브 URL 핸들러에 `GB_HandleAuthURL`을 한 번 연결한다. 두 경로는 각 Host에서 하나만 사용한다. [Host 예시](../ios/host-examples/SocialAuthCallbacks.md)를 따른다. Backend `GAMEBRIDGE_AUTH_AUDIENCES_JSON`의 Google audience는 Web Client ID와 일치해야 한다. 인증 URL과 토큰은 네이티브에서 처리한다.

계정/콘솔이 없는 신규 환경의 실계정 시험은 WAITING_USER다. source fake와 archive는 실제 로그인 성공이 아니다. iOS Google은 후속 Native/Unity Simulator 실계정 로그인·복원·UI 취소·로그아웃을 별도로 확인했다. [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md). 새 Native framework는 GoogleSignIn 및 AppAuth/SPM resource를 소비자에서 link해야 하며 Unity hook은 exact 9.2.0 dependency를 추가한다. 옛 포트폴리오 DEV_RC는 이 코드를 포함하지 않는다.

## 소셜 확장 B — Facebook (문서37)

Android Meta Login18.3.0은 Host의 `implementation("com.facebook.android:facebook-login:18.3.0")`이 필요하다. SDK는 compileOnly로 사용해 기존 Mock 앱에 Meta 초기화를 강제하지 않는다. Host Manifest에 공식 FacebookAppID/ClientToken 및 FacebookActivity·CustomTabActivity 설정을 제공하고 Meta 콘솔에 package name과 debug/release signing key hash를 등록한다. App Secret은 앱에 넣지 않는다. Host의 onActivityResult에서 `BridgeFacade.onSocialActivityResult(requestCode,resultCode,data)`를 먼저 호출하고 false일 때 기존 처리를 계속한다. Native 직접 사용은 `PlatformAuthProviders.facebook(context,config,tokenStore)` 후 `attachHost(activity)`이다.

iOS는 공식 SPM FacebookLogin18.1.1을 링크한다. Info.plist에 FacebookAppID, FacebookClientToken, CFBundleURLTypes의 `fb<APP_ID>`를 설정하고 Host didFinishLaunching에서 `GameBridgeFacebookHost.initialize`를 호출한다. Host URL callback은 `GB_HandleAuthURL` 또는 Swift Facebook/Google helper로 전달한다. Host delegate를 SDK가 교체하지 않는다. `GameBridgeFacebookLoginMode`는 기본 LIMITED, 명시 CLASSIC도 지원한다. Limited는 JWT+서버 nonce, Classic은 Meta debug access token 검증이다. ATT 등에 따라 Classic 요청의 실제 결과가 Limited이면 실제 증명 종류를 전송한다. Meta App Secret은 Backend 전용이다.

Backend `GAMEBRIDGE_AUTH_AUDIENCES_JSON`에 앱별 FACEBOOK App ID를 추가하고 `GAMEBRIDGE_FACEBOOK_AUTH_CONFIG_JSON`은 서버 비밀 저장소에서 `{ "gamebridge-sample": { "appId": "123456789", "appSecret": "<server-only>", "requiredScopes": ["public_profile"] } }` 형태로 제공한다. 같은 Meta App ID를 서로 다른 GameBridge 앱에 중복 설정하지 않는다. 실제 값은 Git/Unity 에셋/명령 로그에 넣지 않는다. Meta 개발모드에는 로그인 테스트 계정·권한·플랫폼 등록이 필요하다.

검증 명령: `ANDROID_HOME="$HOME/Library/Android/sdk" android/gradlew -p android :sdk-android:testDebugUnitTest :sdk-unity-bridge:testDebugUnitTest`, `backend/gradlew -p backend test --tests '*FacebookVerifierTest'`, opt-in 소유 DB의 `FacebookAuthHttpTest`, `swift test --package-path ios --filter 'SocialAuthProviderTests|AppleAuthProviderTests|CBridgeTests'`. Fake/계약/빌드는 실로그인 증거가 아니다. 실제 Android/iOS Facebook 로그인·취소·앱 복귀는 콘솔 설정 후 별도 확인해야 한다.

의존성 환경: SwiftPM 원격 Meta binary 다운로드가 지연되어 공식 ZIP 6개의 upstream SHA256과 codesign을 확인한 뒤 upstream의 `USE_LOCAL_FB_BINARIES=1` 기능으로 로컬 검증했다. 제품 manifest는 공식 URL/exact version을 유지한다. 기본 원격 다운로드 경로는 DEFERRED_ENV이며 서명 검사 해제·SDK 소스 패치는 하지 않았다.

공식 근거: [Meta Android Login](https://developers.facebook.com/docs/facebook-login/android/), [Meta Limited Login](https://developers.facebook.com/docs/facebook-login/limited-login/), [iOS SDK18.1.1](https://github.com/facebook/facebook-ios-sdk/releases/tag/v18.1.1). 증명 계약은 [social-auth](../contracts/social-auth.md)를 따른다.

## 소셜 확장 C — Android Apple 웹 인증 (문서37)

구현 완료, 로컬 Fake/Contract·Native/패키지 빌드 검증 완료. 실제 Apple 인증은 WAITING_USER다. iOS AuthenticationServices 경로는 유지한다. Android는 AndroidX Browser1.9.0 Custom Tabs를 사용하며 WebView를 만들지 않는다.

1. Apple Developer에서 Sign in with Apple을 활성화한 Primary App ID와 웹 Services ID를 연결한다. Services ID는 Backend가 허용하는 APPLE audience에 별도로 등록한다. 네이티브 Bundle ID만 허용하면 웹 인증이 성공하지 않는다.
2. Apple에 `https://auth.example.invalid/v1/auth/apple-web/callback` 형태의 실제 HTTPS callback domain/return URL을 등록한다. 예시 도메인을 실제 소유 도메인으로 바꾼다. Apple callback은 POST form으로 Backend까지 도달해야 한다. reverse proxy도 이 경로·본문을 보존하고 query/body·authorization 헤더를 로그에 남기지 않는다.
3. Backend 비밀 저장소에 `GAMEBRIDGE_APPLE_WEB_CONFIG_JSON`을 아래 구조로 제공한다. 실제 p8와 App Secret은 Git/Unity/Android/iOS 설정에 넣지 않는다. 서버 프로세스만 p8를 읽게 한다. 코드가 ES256 client secret(5분)을 서버에서 생성한다.

```json
{
  "gamebridge-sample": {
    "servicesId": "com.example.web",
    "callbackUri": "https://auth.example.invalid/v1/auth/apple-web/callback",
    "returnUri": "https://app.example.invalid/auth/apple",
    "teamId": "TEAM000000",
    "keyId": "KEY0000000",
    "privateKeyPath": "/run/secrets/apple-signin-key.p8"
  }
}
```

`GAMEBRIDGE_AUTH_AUDIENCES_JSON`에는 해당 GameBridge app의 `"APPLE": ["com.example.ios", "com.example.web"]`를 추가한다. Team ID/Key ID/p8 경로는 서버 설정이며 Native에는 Services ID와 HTTPS return URI만 둔다. 키가 없거나 잘못됐으면 start에서 CONFIG_REQUIRED로 실패한다.

4. Android Host Manifest의 `com.gamebridge.apple.SERVICES_ID`, `com.gamebridge.apple.RETURN_URI`와 Backend 값을 일치시킨다. 기존 Activity에 autoVerify HTTPS App Link intent-filter와 singleTask를 설정하고 return host의 `/.well-known/assetlinks.json`에 실제 package와 debug/release SHA256 signing certificate를 등록한다. Host의 onNewIntent와 cold-launch intent를 Native에서 먼저 처리한다. [Host 예시](../android/host-examples/SocialAuthHost.kt.example), [Manifest 예시](../android/host-examples/social-auth-manifest.xml.example)를 기존 Host에 병합한다. SDK가 Activity를 교체하지 않는다. Native 직접 호출은 `PlatformAuthProviders.apple(context,config,tokenStore)` 후 attachHost/signIn이다.
5. Unity에서는 `await sdk.SignInAsync(AuthProvider.APPLE)`만 호출한다. 완료 URL/handle/verifier/code를 C#에 전달하거나 로그에 남기지 않는다. 프로세스가 죽으면 verifier를 복원하지 않아 이전 callback을 수령해도 세션을 만들 수 없다. 등록된 stale/취소 URL도 Native에서 소비하고 Unity로 전달하지 않는다.

흐름 수명은5분, 완료 handle은최대60초·1회, Native UI는180초다. start는 기존 challenge rate bucket(30/min), callback/complete는 기존 exchange bucket(10/min/IP)을 공유한다. 이 값은 이번 명시 승인 문서37의 권장 선택이며 신규 무제한 경로를 추가하지 않았다. callback의 state/code 재생과 handle 동시 수령을 DB에서 방어한다. handle은 시도별 verifier(SHA256 challenge)에 결속된다. callback에서는 검증된 identity만 저장하고 Native complete에서 기존 SessionService로 세션을 발급하므로 앱 종료 후 callback만으로 orphan SDK session을 발급하지 않는다.

인증 취소/브라우저 닫기/timeout은 실패로 종료한다. Native logout은 SDK 세션을 폐기하며 브라우저의 Apple SSO 쿠키를 관리하지 않는다. 실기기 브라우저 복귀·App Link 검증·Apple 실제 로그인은 아직 실행하지 않았다. 신규 flow 행은 감사용 hash/verified identity를 보존하며 이번 코드가 기존 데이터나 흐름을 자동 삭제하지 않는다. 운영 보존 정책/정리 작업을 임의 도입하지 않았다.

공식 근거: [다른 플랫폼 Apple 인증](https://developer.apple.com/documentation/signinwithapple/incorporating-sign-in-with-apple-into-other-platforms), [웹 Services ID 구성](https://developer.apple.com/help/account/capabilities/configure-sign-in-with-apple-for-the-web), [서버 code 교환](https://developer.apple.com/documentation/signinwithapplerestapi/generate-and-validate-tokens), [Android Browser 릴리스](https://developer.android.com/jetpack/androidx/releases/browser).

## 문서43 — iOS Google 실제 OAuth 사전 준비

독립 Native Host와 Unity iOS 앱은 별도 iOS Client ID와 콜백 Scheme을 사용한다. 로컬 HTTPS 백엔드와 전용 sandbox DB 준비 명령은 [IOS_GOOGLE_OAUTH_PREP](IOS_GOOGLE_OAUTH_PREP.md)에 있다. 두 앱의 실계정 로그인 결과와 현재 Unity Export 절차는 [IOS_GOOGLE_OAUTH_VERIFICATION](IOS_GOOGLE_OAUTH_VERIFICATION.md)에 있다.

## Batch A 다음 Android Google 계정 시험

- 설치할 앱의 실제 `applicationId`와 APK 서명 인증서 SHA-1을 확인해 해당 Android OAuth 클라이언트에 등록한다. 독립 샘플의 앱 ID는 `com.gamebridge.sample`이다. Unity 소비 앱의 ID와 서명은 실제 Export를 기준으로 확인한다.
- 기존 테스트 Google 프로젝트의 Web Client ID를 앱의 Google server client ID와 Backend의 해당 `appId` Google audience 양쪽에서 일치시킨다. 테스트 계정을 허용 목록에 추가한다.
- Google Play 서비스가 있는 Android 기기 또는 Google APIs AVD, 기기가 신뢰하는 HTTPS를 제공하는 Sandbox Backend를 사용한다. Native 샘플 화면에서 appId, HTTPS URL, Web Client ID와 샘플 구성이 요구하는 상품 ID를 입력한다. 본인 인증과 동의는 사용자가 진행한다.

위 Android 설정을 적용해 2026-11-25 실제 계정 검증을 완료했다. [Android Google 검증](evidence/android-google-live-20261125.md). 다른 앱이나 서명으로 다시 실행할 때는 해당 환경을 새로 등록해야 한다.
