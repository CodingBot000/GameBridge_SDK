# Quick Start와 Host 통합

목표는 기존 샘플을 통해 LOCAL_MOCK의 초기화→로그인→상품/구매→서버 잔액→Push→종료 경계를 확인하는 것입니다. 실제 스토어 거래·원격 푸시를 실행하지 않습니다. 검증된 환경은 [COMPATIBILITY](COMPATIBILITY.md), 내부 소유권은 [ENGINEERING_NOTES](ENGINEERING_NOTES.md), 실제 계정 설정은 [USER_SETUP](USER_SETUP.md)을 따릅니다.

## 1. 패키지 준비

저장소 루트에서 작업합니다. 이 개발 환경의 최종 로컬 후보는 `artifacts/portfolio-final/DEV_RC`입니다. 그 안의 `upm`에는 SDK147파일의 `SHA256SUMS`, 상위에는 문서/manifest까지 포함한 별도 checksum이 있습니다.

```sh
export GAMEBRIDGE_UPM_STAGING="$PWD/artifacts/portfolio-final/DEV_RC/upm"
python3 harness/check-staging.py "$GAMEBRIDGE_UPM_STAGING"
```

다른 checkout에는 생성 바이너리가 없습니다. 아래는 **새 패키지가 필요한 경우**의 기존 빌드 명령입니다. 이미 검증된 동일 산출물을 검토하는 데 재실행할 필요는 없습니다. 출력 경로는 존재하지 않는 새 절대 경로여야 합니다.

```sh
export GAMEBRIDGE_MAVEN_REPO="$PWD/artifacts/my-dev-maven"
bash scripts/build-android.sh --mock
export GAMEBRIDGE_IOS_OUTPUT_DIR="$PWD/artifacts/my-dev-ios"
bash scripts/build-ios.sh --xcframework
bash scripts/package-sdk.sh "$GAMEBRIDGE_MAVEN_REPO" \
  "$GAMEBRIDGE_IOS_OUTPUT_DIR/GameBridgeNative.xcframework" \
  "$PWD/artifacts/my-dev-upm"
```

이후 `GAMEBRIDGE_UPM_STAGING`을 새 `my-dev-upm`의 절대 경로로 바꿉니다. 각 build는 별도 consumer/R8 또는 archive를 수행하며, 패키지 생성만으로 Unity Player가 실행됐다고 판정하지 않습니다.

## 2. Unity UPM과 기존 샘플

1. Unity6000.5.8f1 및 필요한 Android/iOS Build Support를 준비합니다. 계정·라이선스·약관은 사용자가 처리합니다.
2. 새 소비 프로젝트의 Package Manager에서 **Add package from disk**로 staging의 `com.gamebridge.sdk/package.json`을 선택합니다. 소스만 Git으로 설치하면 Native artifact가 없으므로 hook이 setup error로 실패합니다.
3. Package Manager Samples에서 **Native Mock and Sandbox Demo**를 import합니다. Unity UI와 호환 EventSystem을 준비하고 빈 GameObject에 `NativeDemo`를 붙입니다. 실제 검증에서 UI 패키지는2.5.0을 사용했습니다. [샘플 안내](<../unity/Packages/com.gamebridge.sdk/Samples~/Native Demo/README.md>)를 따릅니다.
4. Native Demo는 Android/iOS Player용입니다. Editor에서 빠르게 fake UI를 볼 때는 **Editor Offline Demo**를 사용합니다. 두 모드의 결과를 합치지 않습니다.
5. Android export는 SDK의 Maven hook, iOS export는 `IosXcodeBuildHook`이 staged XCFramework를 UnityFramework target에 연결합니다. Host 프로젝트의 기존 hook과 delegate를 임의 교체하지 않습니다.

자동화된 별도 소비 프로젝트가 필요하면 다음 준비 명령을 사용합니다. 출력의 `Prepared consumer:` 경로는 이후 build script의 인자입니다. 준비만으로 import/build/Player가 수행되지는 않습니다.

```sh
bash scripts/prepare-unity-android-mock.sh --prepare
# 또는
bash scripts/prepare-unity-ios-mock.sh --prepare
```

실제 build script의 서명은 아래와 같습니다. `<...>`는 준비 명령이 반환한 **절대 경로**로 바꿉니다.

```text
bash scripts/build-unity-android-mock.sh <준비한 project 절대경로> <새 APK 절대경로>
bash scripts/build-unity-ios-mock.sh <준비한 project 절대경로> <새 Xcode export 절대경로>
```

APK build, Xcode export, Xcode app build와 실제 Player 실행은 서로 다른 단계입니다. 안전한 재실행기는 전용 AVD/ADB 소유권 또는 새 Simulator와 격리 DB를 요구합니다. [Android runner](../harness/run-unity-android-mock-e2e.py), [iOS runner](../harness/run-unity-ios-mock-e2e.py)를 참고하되 기존 사용자 기기를 테스트 대상으로 추정하지 않습니다.

## 3. LOCAL_MOCK Backend

새 개발 환경에서는 Docker/JDK21을 준비하고 아래 환경값을 로컬 비밀 환경에 설정한 뒤 실행합니다. 실제 값·`.env`·서명 파일을 Git/채팅/화면 로그에 넣지 않습니다.

| 변수 | 용도 |
| --- | --- |
| `GAMEBRIDGE_DB_PASSWORD` | 로컬 Compose DB 비밀번호 |
| `GAMEBRIDGE_DEV_AUTH_KEY` |32자 이상 개발 인증키, Native Demo에서 LOCAL_MOCK을 선택할 때만 사용 |
| `SERVER_TOKEN_ENCRYPTION_KEY` | Base64 decode32 bytes, 서버 token 저장 암호화 |
| `GAMEBRIDGE_MAINTENANCE_ENABLED` | 로컬 정상 이용은 명시적 `false` |

```sh
bash scripts/run-demo-backend.sh
```

이 스크립트는 local Compose volume을 보존하고 `local-mock` profile을 사용합니다. 기존 DB가 있다면 이전 비밀번호·암호화키를 유지합니다. 개인/운영 DB를 가리키지 말고, 깨끗한 시험에는 [격리 smoke](../harness/run-backend-smoke-isolated.py)를 사용합니다. 이 시험도 별도 role/DB를 생성해 보존하므로 환경을 먼저 확인해야 합니다.

Host에 입력하는 URL은 Android emulator에서 `http://10.0.2.2:18080`, iOS Simulator에서 `http://127.0.0.1:18080`입니다. 실제 포트를 변경했다면 URL도 일치시킵니다. HTTP 허용은 LOCAL_MOCK 개발 소비자에만 적용합니다. 자동 Android 테스트 consumer는 개발용 cleartext 설정을 포함하므로 그 manifest/APK를 배포용으로 사용하지 않습니다.

## 4. 초기화·로그인·상점

Native Demo의 UI에 LOCAL_MOCK, URL, 개발키와 installation UUID를 런타임에 입력합니다. 아래는 같은 공개 API의 호출 순서입니다. `backendUrl`, `developmentKey`, `installationId`는 Host가 메모리에서 제공하는 값이며 아래 코드는 Unity main thread에서 호출합니다. 완전한 UI/예외 처리는 기존 [NativeDemo.cs](<../unity/Packages/com.gamebridge.sdk/Samples~/Native Demo/NativeDemo.cs>)를 재사용합니다.

```csharp
var config = new GameBridgeConfig(
    "gamebridge-sample", ProviderMode.LocalMock, backendUrl, 30000,
    developmentKey, "A", null, null, null, installationId);
var client = GameBridgeSdk.Create(config);
await client.InitializeAsync(config);
var user = await client.SignInAsync(AuthProvider.MOCK);
var products = await client.GetProductsAsync();
var purchase = await client.PurchaseAsync("coins_100");
var wallet = await client.GetEntitlementsAsync();
```

`coins_100`과 `premium_unlock`은 논리 상품 ID입니다. UI는 `wallet.coinBalance`/`premiumEnabled`를 표시합니다. `PENDING`/`VERIFICATION_PENDING`을 지급 성공으로 표시하거나 자체 카운터로 코인을 더하지 않습니다. 후속 `PurchaseUpdated` 이벤트가 오면 서버 잔액을 다시 조회합니다. 같은 지급의 재요청도 서버 원장·멱등성으로 한 번만 반영됩니다. 지급 후 응답 유실에는 `SyncPurchasesAsync(SyncReason.APP_RESUME)` 같은 복구 경로를 사용하며 새 구매 UI를 자동으로 열지 않습니다.

`GetStatus()`, `GetCapabilities()`, `GetDiagnostics()`는 동기 snapshot입니다. Native 진단이 필요하면 `GetNativeDiagnosticsAsync()`를 await합니다. `.Wait()`/`.Result`로 main thread를 막지 않습니다.

## 5. Push 등록·수신·해제와 종료

LOCAL_MOCK은 installation UUID를 사용하는 simulated 등록/전달입니다. OS permission이나 FCM/APNs 성공이 아닙니다.

```csharp
System.Action<PushUpdate> onPush = update => UnityEngine.Debug.Log("LOCAL_MOCK push received");
client.PushReceived += onPush;
var permission = await client.RequestPushPermissionAsync();
var registration = await client.RegisterPushAsync();
```

등록 후 앱을 연결 상태로 유지합니다. Native Demo에는 **등록/해제·수신 표시**가 있고 발송 API는 SDK 공개 facade에 없습니다. 개발 send는 별도의 admin key·allowlist·session 소유권이 필요합니다. 미연결 시 LOCAL_MOCK 메시지는 버립니다.

수신까지 확인하려면 서버를 시작하기 전에 `GAMEBRIDGE_DEV_PUSH_ADMIN_KEY`(32자 이상, auth key와 다른 값)와 `GAMEBRIDGE_DEV_PUSH_ALLOWLIST`(테스트 installation UUID)를 로컬 환경에 추가합니다. Native Demo에는 같은 UUID를 입력합니다. 다음은 기존 [개발 Push HTTP 시험](../backend/src/test/kotlin/com/gamebridge/push/DevPushHttpIntegrationTest.kt)의 호출 순서에 따른 개발자용 예시입니다. `GAMEBRIDGE_TEST_INSTALLATION_ID`에는 그 UUID를 설정합니다. UI/Native가 보관한 session token을 추출하지 않고 별도의 LOCAL_MOCK A session을 메모리에서 발급받아 사용한 뒤 종료합니다.

```sh
python3 - <<'PY_SEND'
import json, os, urllib.request, uuid
base = "http://127.0.0.1:18080"  # 위 local-mock 서버. 포트를 바꿨다면 일치시킨다.
def call(path, body, headers):
    request = urllib.request.Request(base + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)
installation = str(uuid.UUID(os.environ["GAMEBRIDGE_TEST_INSTALLATION_ID"]))
auth = call("/v1/dev/auth", {"subject": "A"},
            {"X-Development-Key": os.environ["GAMEBRIDGE_DEV_AUTH_KEY"]})
headers = {"Authorization": "Bearer " + auth["accessToken"]}
try:
    result = call("/v1/dev/push/send", {
        "installationId": installation, "messageId": str(uuid.uuid4()),
        "route": "home", "title": "LOCAL_MOCK", "body": "Local test"
    }, {**headers, "X-Admin-Key": os.environ["GAMEBRIDGE_DEV_PUSH_ADMIN_KEY"]})
    assert result["accepted"] and result["delivery"] == "SIMULATED"
    print("SIMULATED; confirm the connected Player receive UI separately")
finally:
    call("/v1/auth/logout", {}, headers)
PY_SEND
```

이 예시는 문서의 호출 설명이며 이번 최종화에서 새 실행 결과로 세지 않습니다. 서버의 `accepted/SIMULATED`와 Player의 수신 표시를 각각 확인합니다. 동작·권한 경계는 [HTTP 계약](API.md#local_mock-sse와-map-응답)을 따릅니다. 실제 Provider 발송으로 전환하지 않습니다.

사용자가 종료할 때 UI 구독을 해제하고 아래 순서로 정리합니다. 오류가 나도 `Dispose()`가 실행되도록 Host의 `try/finally`를 사용합니다. [Player 시나리오](../tests/UnityIosPiiConsumer/MockIosPlayerScenario.cs)에도 최종 Dispose가 있습니다.

```csharp
try
{
    client.PushReceived -= onPush;
    await client.UnregisterPushAsync();
    await client.SignOutAsync();
    await client.ShutdownAsync();
}
finally { client.Dispose(); }
```

동시 활성 facade는 하나입니다. 여러 Scene에서 공유할 경우 소유자는 유지하고 Scene UI의 이벤트 구독만 해제합니다. Scene마다 종료한다면 Shutdown/Dispose 후 새 `Create`를 합니다. SDK의 persistent dispatcher와 Host의 client 수명을 혼동하지 않습니다.

## 6. Native 단독 앱과 Host 연결

### Android Maven/AAR

AAR 하나만 복사하면 전이 의존성이 빠질 수 있으므로 제공 Maven repository를 권장합니다.

```sh
export GAMEBRIDGE_MAVEN_REPO="$GAMEBRIDGE_UPM_STAGING/com.gamebridge.sdk/Editor/GameBridgeArtifacts~/Android/maven-repo"
```

Host의 `dependencyResolutionManagement.repositories`에 해당 local Maven 경로와 `google()`/`mavenCentral()`을 추가합니다. 아래 coordinate는 [독립 소비 앱](../android/consumer-check/app/build.gradle.kts)과 같습니다.

```kotlin
implementation("com.gamebridge:sdk-android:0.1.0-dev")
implementation("com.gamebridge:sdk-unity-bridge:0.1.0-dev")
```

네이티브 기본 흐름은 [Compose sample](../android/sample-app)을 참고합니다. Unity의 Activity attach/callback 등록은 `AndroidTransport`가 담당합니다. Native Host가 bridge를 직접 소비한다면 `BridgeFacade.attachHost(activity)`/`detachHost()`와 `setCallback` 수명을 맞춥니다.

실제 FCM은 Host가 FirebaseApp·서비스·채널·권한을 준비합니다. SDK의 Firebase Messaging은 optional compileOnly이므로 사용하는 Host에 의존성과 앱 설정이 필요합니다. 기존 서비스/Activity에서 [forwarding 예제](../android/host-examples/UnityPushForwarding.kt.example)를 통합하고 두 번째 서비스를 중복 등록하지 않습니다.

### iOS Swift Package/XCFramework

Swift source 소비는 [기존 consumer](../ios/consumer-source-check/Package.swift)의 `GameBridgeCore`/`GameBridgeApple`을 참고합니다. binary 소비는 staging의 `Editor/GameBridgeArtifacts~/iOS/GameBridgeNative.xcframework`를 연결하고 module `GameBridgeNative`를 사용합니다. static framework이므로 **Do Not Embed** 대상이며, slice·link 설정은 [기존 iOS hook](../unity/Packages/com.gamebridge.sdk/Editor/IosXcodeBuildHook.cs)과 검증된 소비 예시를 따릅니다.

Host는 window, `UIApplicationDelegate`, `UNUserNotificationCenterDelegate`를 소유합니다. [SwiftUI sample AppDelegate](../ios/SampleApp/GameBridgeSampleApp.swift)처럼 등록 성공/실패·수신/열기 callback을 `ApplePushHostAdapter`에 전달하고 completion handler를 완료합니다. SDK는 Host delegate를 대체하지 않습니다.

Unity의 실제 APNs host 경로는 `NativeDemoIosPush`/`IosPushHostAdapter`를 명시적으로 연결합니다. LOCAL_MOCK은 facade에서 host driver를 사용하지 않고 simulated 경로로 분기합니다. 실제 등록·원격 수신에는 별도 Apple 설정과 실기기 검증이 필요합니다.

## 7. 연동 문제 해결

| 증상 | 확인할 근거 | 조치와 재확인 |
| --- | --- | --- |
| 초기화 `CONFIG_REQUIRED` | mode·URL·LocalMock key 길이·subject·installation UUID. 값 자체는 로그로 출력하지 않음 | Native Demo 런타임 입력과 `GameBridgeConfig.Validate()` 대조. capability와 `GetStatus()` 확인 |
| hook의 Maven/XCFramework missing | Git 소스 설치인지, 완결 staging인지와147 checksum | 올바른 `package.json` 경로를 설치하고 `check-staging.py` 재확인 |
| Android build 성공, 설치/실행 전 중단 | APK 존재와 별도로 ADB exe/PID·runtime/build port·AVD name·serial/양 port | 사용 중인 사용자 서버를 종료하지 않음. 전용 환경에서 소유권 guard를 통과한 뒤 실행. [실제 사례](ENGINEERING_NOTES.md) |
| Player marker/상품/잔액이 오지 않음 | Native Demo 모드, target module, 서버 health·loopback 주소·서버 requestId | Editor Offline/LOCAL_MOCK/실Provider 혼동을 해소. `purchase` marker만 보지 말고 서버 잔액/원장을 확인 |
| 구매 `TIMEOUT`/`VERIFICATION_PENDING` | requestId·session·attempt와 서버 grant/finalization 상태 | 같은 거래 복구·조회로 확인. 멱등키를 다른 body에 재사용하거나 구매 UI를 자동 재오픈하지 않음 |
| `SESSION_EXPIRED` / 로그아웃 경고 | Native 저장소 결속, 서버 세션·갱신 상태. `REVOCATION_UNCONFIRMED` 의미 | 안전한 재인증 또는 연결 회복 후 서버 상태 확인. 옛 refresh token을 강제 복구하지 않음 |
| Push가 전달되지 않음 | installation UUID, 권한/등록 상태, session·allowlist·admin key 설정, 연결 여부 | LOCAL_MOCK은 연결 중 simulated 전달. 실제 Provider는 USER_SETUP으로 분리. 등록/해제와 token 수 재확인 |
| `PERMISSION_DENIED`/`UNSUPPORTED_*` | 해당 모드·플랫폼 capability와 Host adapter | 사용자 선택·플랫폼 미지원·설정 누락을 UI에 설명. 실패를 Mock 성공으로 바꾸지 않음 |
| StoreKit 실패 | iOS Runtime·scheme·local StoreKit 모드·원본 시험 | P05-T03 FAIL과18.6 위험을 유지. LOCAL_MOCK 성공으로 해제하지 않음 |

오류 코드별 의미와 요청/재시도 경계는 [API](API.md), 실 Provider를 선택하는 경우의 준비 순서는 [USER_SETUP](USER_SETUP.md)에 있습니다.
