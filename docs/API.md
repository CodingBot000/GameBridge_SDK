# Unity C# API 안내

> GameBridge SDK `0.1.1-dev`의 **현재 공개 소스 기준**입니다. 아래 메서드가 존재한다는 사실과 실제 Unity Player/스토어에서 동작이 검증되었다는 사실은 다릅니다. 검증 상태는 [기능 매트릭스](FEATURE_MATRIX.md), [진행 원장](PROGRESS.md)을 확인하세요.

> 양 플랫폼 GOOGLE/APPLE/FACEBOOK은 Native로 분기하며 원본 증명은 Unity에 노출하지 않습니다. Android API 34 AVD와 iOS 18.6 Simulator의 Native·Unity Google 실제 로그인·복원·UI 취소·로그아웃 및 서버 세션 폐기를 확인했습니다. Android 취소 후 재로그인 성공은 확인했으나 iOS Native의 해당 성공은 미확인입니다. 실제 갱신/replay와 다른 Provider는 별도 판정입니다. [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md)

[README로 돌아가기](../README.md) · [통합 가이드](INTEGRATION.md) · [샘플 코드](../unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/OfflineDemo.cs)

## 기본 사용 순서

1. `GameBridgeConfig`를 생성합니다.
2. Unity 메인 스레드에서 `GameBridgeSdk.Create(config)`로 클라이언트를 만들고 `InitializeAsync(config)`를 호출합니다.
3. 로그인·상품·구매·재화·알림 등의 비동기 API를 사용합니다.
4. 더 이상 사용하지 않으면 `ShutdownAsync()` 또는 `Dispose()`로 정리합니다.

`GameBridgeSdk.Create`는 활성 인스턴스를 하나만 허용하며, 별도 `GameObject`를 수동 생성할 필요가 없습니다. 초기화 모드는 생성한 플랫폼에 맞아야 합니다. 자세한 호출 예제는 [README Quick Start](../README.md#quick-start--unity-editor-offline)를 확인하세요.

## 실행 모드

| `ProviderMode` | 용도 | 중요한 제한 |
| --- | --- | --- |
| `EditorOffline` | Unity Editor의 메모리 Fake | 실제 Backend·스토어·계정과 연결되지 않으며 Player에서 사용 불가 |
| `LocalMock` | Android/iOS Native ↔ 로컬 Backend 개발 경로 | 개발키·테스트 Backend 필요. 가상 로그인/구매이며 실제 스토어가 아님 |
| `XcodeStoreKit` | iOS의 Xcode 로컬 StoreKit 시험 | iOS 18 이상 및 별도 개발 설정 필요. 실제 Apple 서명 검증 아님 |
| `PlatformSandbox` | Android/iOS Google·Apple·Facebook 및 플랫폼 스토어 Sandbox 경로 | 선택한 Provider 계정·Host·Backend 설정 필요; Android/iOS Google 실제 AVD/Simulator 검증은 별도 확인, 전체 실연동 완료 아님 |

`GameBridgeConfig`는 앱 식별자, 모드, Backend 주소, 요청 시간 제한 등을 받습니다. `LocalMock` 및 `XcodeStoreKit`에서는 개발키·Mock 사용자(`A` 또는 `B`)를 별도로 요구합니다. 개발키는 로그·Unity Asset·`PlayerPrefs`에 보관하지 마세요.

## 메서드 빠른 참조

### 초기화·상태

| 메서드 | 역할 |
| --- | --- |
| `GameBridgeSdk.Create(config)` | `GameBridgeClient` 생성 (동시 활성 클라이언트 제한) |
| `InitializeAsync(config)` | 네이티브 전송 계층 초기화 |
| `GetStatus()` / `GetCapabilities()` | SDK 상태 및 현재 모드에서의 지원 기능 조회 |
| `GetDiagnostics()` | C# 요청 상태·무시한 메시지 수 등 진단 |
| `GetNativeDiagnosticsAsync()` | 제한된 Native 진단 이벤트 목록 조회 |
| `ShutdownAsync()` / `Dispose()` | SDK 종료·자원 정리 |

### 인증·구매·재화

| 메서드 | 역할 |
| --- | --- |
| `SignInAsync(AuthProvider.MOCK / GOOGLE / APPLE / FACEBOOK)` | 해당 모드·플랫폼의 로그인 요청 |
| `RestoreSessionAsync()` | 세션 복원 |
| `SignOutAsync()` | 로그아웃 |
| `GetProductsAsync()` | 상품 목록 조회 |
| `PurchaseAsync(productId)` | 구매 시작 및 결과 수신 |
| `GetEntitlementsAsync()` | 서버가 인식한 재화·권한 조회 |
| `SyncPurchasesAsync(reason)` | 구매 동기화·복원 요청 |

구매 호출의 응답 또는 이벤트를 곧바로 **재화 지급 성공으로 간주하면 안 됩니다.** 실제 지급은 서버 검증·원장 처리 이후의 권한·잔액으로 판단합니다. 개발용 Mock 검증과 실제 스토어 검증은 서로 대체할 수 없습니다.

### 푸시·서비스 설정

| 메서드 / 이벤트 | 역할 |
| --- | --- |
| `RequestPushPermissionAsync()` | 명시적인 알림 권한 요청 |
| `RegisterPushAsync()` / `UnregisterPushAsync()` | 푸시 등록·해제 |
| `GetServiceConfigAsync()` | 서버 설정 조회 |
| `PurchaseUpdated` | 구매 상태 변경 알림 |
| `PushReceived` / `PushOpened` | 푸시 수신·열기 알림 |
| `PushTokenChanged` | 푸시 토큰 변경 알림 |

Host가 Android Firebase 서비스·Activity 또는 iOS 알림 delegate를 소유합니다. SDK가 Host의 delegate를 임의 교체하지 않습니다. 푸시 callback 전달·권한 설정은 [통합 안내](INTEGRATION.md)와 [사용자 설정](USER_SETUP.md)을 따릅니다. LOCAL_MOCK의 `SIMULATED` 푸시는 실제 FCM/APNs 전송이 아닙니다.

## 오류 처리

공개 API는 `SdkException`과 오류 코드(`Code`)를 사용합니다. 예를 들면 `CONFIG_REQUIRED`, `SESSION_EXPIRED`, `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED`, `BUSY`, `UNSUPPORTED_OPERATION`이 있습니다.

`SdkException.NativeCode`는 `auth.signOut`의 `REVOCATION_UNCONFIRMED` 경우에만 별도로 보존합니다. 이는 로컬 세션은 삭제했지만 서버 revoke를 확인하지 못했다는 경고이며, 재시작 후 영속 경고·자동 재시도는 구현되어 있지 않습니다.

```csharp
try
{
    var products = await sdk.GetProductsAsync();
}
catch (SdkException error)
{
    Debug.LogWarning("GameBridge error: " + error.Code);
}
```

## 검증 상태를 읽는 법

- **Editor Offline:** Fake/독립 관리 코드 시험 ≠ Unity Editor 실제 Play 검증.
- **LOCAL_MOCK:** Native·Backend 로컬 시험 ≠ Unity Android/iOS Player 전체 통과.
- **Platform Sandbox:** Provider 연결 코드·합성 시험과 실제 계정·스토어·푸시 실행은 별개입니다. [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md)에서 실제 인증과 합성 refresh/replay의 범위를 확인하세요.
- **Xcode StoreKit:** iOS 18.6 일부 통과, iOS 26.5 별도 로컬 실패가 기록됨.

구현·검증 결과의 최신 공식 근거는 [PROGRESS](PROGRESS.md), [WORK_LOG](WORK_LOG.md), [FINAL_REPORT](FINAL_REPORT.md)에서 확인하세요.

## SDK·HTTP·Bridge 세부 계약

> 문서37의 소셜 확장 구현 이력은 [SOCIAL_AUTH_HANDOFF](SOCIAL_AUTH_HANDOFF.md), 현재 검증 범위는 [기능 매트릭스](FEATURE_MATRIX.md)를 따릅니다. 아래 이전 포트폴리오 snapshot과 후속 Provider 시험을 구분합니다.


공개 Unity 표면은 [GameBridgeClient](../unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs), 설정은 [GameBridgeConfig](../unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeConfig.cs)가 기준입니다. 실제 사용 순서는 [Quick Start](INTEGRATION.md)를 따릅니다.

## Unity 공개 API

| 영역 | 실제 API | 호출자의 책임 |
| --- | --- | --- |
| 생성·수명 | `GameBridgeSdk.Create`, `InitializeAsync`, `ShutdownAsync`, `Dispose` | main thread에서 생성/수명 관리. 활성 facade 하나. 같은 설정 init 공유·다른 설정 거부 |
| 상태 | `GetStatus`, `GetCapabilities`, `GetDiagnostics`, `GetNativeDiagnosticsAsync` | 동기 getter는 snapshot. Native 진단만 비동기 왕복 |
| 인증 | `SignInAsync`, `RestoreSessionAsync`, `SignOutAsync` | LOCAL_MOCK은 MOCK, 실Provider는 설정된 GOOGLE/APPLE/FACEBOOK. token은 Native 소유 |
| 상점 | `GetProductsAsync`, `PurchaseAsync`, `GetEntitlementsAsync`, `SyncPurchasesAsync` | 논리상품ID 사용, pending과지급 구분, 서버 entitlement로 표시 |
| Push·설정 | `RequestPushPermissionAsync`, `RegisterPushAsync`, `UnregisterPushAsync`, `GetServiceConfigAsync` | 명시적 사용자 동작과 installation UUID, Host adapter 및 mode 확인 |
| 이벤트 | `PurchaseUpdated`, `PushReceived`, `PushOpened`, `PushTokenChanged` | UI 수명에 맞게 구독 해제. 중복/late event와 완료 Task를 분리 |

`SdkCapabilities`의 supported/configured/mode/reason으로 미지원과 미설정을 구분합니다. Push 미설정이 전체 초기화 실패를 뜻하지는 않습니다.

계획서에 있는 이벤트 명칭을 실제 공개 이벤트로 간주하지 않습니다. 위 표는 현재 C# source에 존재하는 표면입니다. raw access/refresh token·구매 증빙·Push token 원문은 공개 result에 포함하지 않습니다.

`PurchaseResult.status`는 `PURCHASED/PENDING/CANCELED/VERIFICATION_PENDING/FAILED`, 지급은 `NOT_GRANTED/GRANTED/ALREADY_GRANTED`, 완료 처리는 `NOT_REQUIRED/PENDING/FINALIZED`로 나눕니다. `PURCHASED`만 보고 코인을 더하지 않습니다. 잔액·revision·거래 식별자처럼 정밀도 손실이 가능한 값은 wire의10진 문자열 규칙을 따릅니다.

## 요청·취소·오류

- `requestId`는 요청, `sdkSessionId`는 SDK 세대, `eventId`는 이벤트 식별자입니다. 응답은 request/session/operation이 맞아야 수락합니다.
- public Task는 한 번 완료합니다. 취소·timeout은 기다림의 종료이며 이미 시작한 결제 취소가 아닙니다. 늦은 거래는 이벤트·복구·서버 조회로 반영합니다.
- 현재 소스의 일반 요청 기본30초·interactive180초·pending100·diagnostic ring200은 구현의 설계값입니다. 성능 보장이나 새 운영 정책으로 제시하지 않습니다.
- `SdkException.Code/Retryable`로 동작을 결정합니다. `NativeCode`는 logout의 `REVOCATION_UNCONFIRMED`만 보존합니다. 로컬 session은 지웠으나 서버 revoke 미확인이라는 뜻이고, 재시작 후 경고 영속화·자동 revoke 재시도는 없습니다.

| 오류·상태 | 대응 |
| --- | --- |
| `CONFIG_REQUIRED`, `INVALID_ARGUMENT` | mode·필수 설정·형식 확인 후 명시적으로 재시도 |
| `NOT_INITIALIZED`, `BUSY`, `ALREADY_INITIALIZED_DIFFERENT_CONFIG` | 호출 순서와 활성 client/UI 작업 수명 확인 |
| `SESSION_EXPIRED`, `AUTH_FAILED`, `AUTH_REPLAY_DETECTED` | Native의 안전한 복원/재인증. 실패를 Mock으로 전환하지 않음 |
| `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED` | 재시도 가능 여부와 기존 거래 상태를 따로 확인 |
| `IDEMPOTENCY_CONFLICT`, `PURCHASE_ACCOUNT_MISMATCH`, `VERIFICATION_FAILED` | 계정·attempt·body·증빙 경계 확인. 새 지급을 강행하지 않음 |
| `PERMISSION_DENIED`, `UNSUPPORTED_PLATFORM/PROVIDER/OPERATION` | Host 권한·capability·모드에 맞게 UI 안내 |
| `MAINTENANCE` | 신규 구매 차단, 기존 검증/복구·로그아웃 경계 유지 |
| `BRIDGE_PROTOCOL_MISMATCH`, `PAYLOAD_TOO_LARGE` | wire 버전·UTF-8·허용 크기/모델을 대조 |

전체 코드 목록은 [error-codes.json](../contracts/error-codes.json), 재현·설정 조치는 [Troubleshooting](INTEGRATION.md#7-연동-문제-해결)을 참고합니다. 무조건적인 자동 구매/로그인 UI 재시도는 구현 계약이 아닙니다.

## 서로 다른 두 계약

| 계약 | 내용 | 근거 |
| --- | --- | --- |
| [Bridge JSON Schema](../contracts/bridge.schema.json) | Unity↔Native request/response/event, UTF-8·session·request·허용 operation | Kotlin/Swift/C# parser·변이 회귀 |
| [HTTP OpenAPI](../contracts/openapi.yaml) | Backend24 operation의 method/path, profile, security/header·DTO·응답 | 소스 binding·DTO23·정상/음성16 및 실제/합성 HTTP 대조 |

OpenAPI는 JSON 형식의 YAML1.2입니다. HTTP `X-Request-Id`는 서버가 생성하며 오류 body의 `requestId`와 연결됩니다. purchase verify에는 `Idempotency-Key`가 필요합니다. Mock은 nonblank/128자 이하, Apple/Google verify는 canonical UUID를 요구합니다. 누락된 필수 header는400 `INVALID_ARGUMENT`입니다.

개발 auth·Xcode fake grant·Push stream은 `local-mock` 전용, 개발 Push send는 `local-mock/sandbox`, 실제 purchase/read/device controller는 `sandbox/production` 경계를 가집니다. Production에는 개발 send를 등록하지 않습니다. `x-source-bindings`와 Controller profile이 근거입니다. 실패·403·503·429의 모든 분기를 실행했다는 의미는 아닙니다.

## LOCAL_MOCK SSE와 Map 응답

SDK 연동자가 실제 소비하는 범위를 현재 Controller와 대조했습니다. 아래는 **사람이 읽는 보강 계약**이며 OpenAPI의 SSE/동적 Map 기계 검증 잔여를 없앴다고 주장하지 않습니다.

| 응답 | 실제 필드·동작 | 소스 |
| --- | --- | --- |
| `GET /v1/catalog` | JSON array. LocalMock: `productId/storeProductId/type` 문자열. Sandbox/Production은 `platform`도 포함. 실제 현지화 가격은 스토어가 제공 | [MockPurchaseController](../backend/src/main/kotlin/com/gamebridge/purchase/MockPurchaseController.kt), [StoreReadController](../backend/src/main/kotlin/com/gamebridge/purchase/StoreReadController.kt) |
| `GET /v1/purchases/{purchaseId}` | 본인·app/environment 범위의 `serverPurchaseId/productId/storeStatus/fulfillmentStatus/finalizationStatus`. 내부 `CLIENT_PENDING`은 응답 `PENDING`으로 변환 | StoreReadController |
| `PUT/DELETE /v1/devices/{installationId}/push-token` | 등록은 `provider/registered/tokenFingerprint`, 해제는 `registered`. 원문 token은 반환하지 않음 | [DeviceRegistrationController](../backend/src/main/kotlin/com/gamebridge/push/DeviceRegistrationController.kt), [MockDevices](../backend/src/main/kotlin/com/gamebridge/push/MockDevices.kt) |
| `POST /v1/dev/push/send` | `accepted` boolean과 `delivery`. LocalMock `SIMULATED`, Sandbox `QUEUED`; 실제 단말 전달 확인이 아님 | [DevPushController](../backend/src/main/kotlin/com/gamebridge/push/DevPushController.kt) |
| `GET /v1/dev/push/stream?installationId=...` | Bearer session과 등록 소유권 필요. `text/event-stream`: `ready`의 data는 `connected`, `push` data는 `messageId/route/campaignId` JSON. campaignId는 null 가능. heartbeat는 comment | [MockPushStreamController](../backend/src/main/kotlin/com/gamebridge/push/MockPushStreamController.kt) |

SSE는 수신/heartbeat마다 session·installation 소유권을 재확인하고, 해제·로그아웃 등으로 소유가 사라지면 완료합니다. 연결 해제 시 listener/heartbeat를 정리하며 미연결 메시지를 저장 재전달하지 않습니다. `route`는 개발 send/SDK 경계에서 `home/store`만 허용합니다. raw token/proof를 payload에 추가하지 않습니다.

24 operation 모두 성공 응답 근거가 있고, 합성 HTTP10시험에서132개의 직렬화 구조를 대조했습니다. 문자열 값은 제거한 구조 검증이라 의미·서명 검증으로 확대하지 않습니다. [HTTP 근거](evidence/p11-batch34-openapi-synthetic.json). **BUG-017은 OPEN**이며 SSE event별 자동 schema 대응·동적 Map의 세부 명세 검사를 Known Limitation으로 남깁니다. 포트폴리오 종료와 독립된 선택적 보강입니다.

## 별도 소셜 확장 A

새iOS Google은기존GOOGLE enum/legacy challenge·exchange(idToken)를유지하며nonce 검증도그대로사용한다. Native provider 저장은iOS Google전용Keychain service와app/mode/Backend/client-ID 결속을사용한다. Native Store/Push는access-token/userId만담은내부세션protocol로기존서버의계정/원장권위를재사용한다. Apple 공개API/Keychain 상태와섞지않는다.

GB_HandleAuthURL은Host native URL callback용추가C ABI이며원래4개함수는그대로다. rawURL은Unitypublic callback/result로전달하지않는다. 새경로검증은README 확장표와social-login evidence를따르며이전CI648의검증으로승격하지않는다.

## 문서37 소셜 확장 B

FACEBOOK enum3 추가. /v1/auth/challenges의 proofType, /v1/auth/exchange의 명시 proofType+accessToken을 추가하며 기존 GOOGLE/APPLE idToken 호출은 그대로다. Facebook Classic과 Limited는 별도 검증하고 UserProfile 외 원본 증명은 Unity에 노출하지 않는다.

## 문서37 최종 소셜 계약

Unity AuthProvider의 기존 MOCK0/GOOGLE1/APPLE2를 유지하고 FACEBOOK3을 추가했다. 기존 Google/Apple `/v1/auth/challenges`·`/v1/auth/exchange`에서 proofType 생략/null은 ID_TOKEN으로 명시 해석한다. Jackson Kotlin 기본 인자 처리에 의존하지 않는다. Facebook은 명시 FACEBOOK_ACCESS_TOKEN/accessToken 또는 FACEBOOK_LIMITED_ID_TOKEN/idToken만 허용한다. code를 idToken으로 받지 않는다. issuer/subject/app scope로 기존 세션과 원장에 결속하고 이메일 자동 병합/구매 이전은 하지 않는다.

신규 sandbox/production API (무인증 시작/복귀이므로 state·verifier가 권한 증명이며 기존 rate/body 제한 적용):

| POST | 입력 | 성공 응답 |
| --- | --- | --- |
| /v1/auth/apple-web/start | appId, verifierChallenge (Native S256/base64url43) | flowId, authorizationUrl, returnUri, expiresAt; no-store |
| /v1/auth/apple-web/callback | application/x-www-form-urlencoded state+code 또는 error; user는 identity 근거로 사용하지 않음 | 303 Location: 등록HTTPS return?handle=opaque; no-store/no-referrer, body 없음 |
| /v1/auth/apple-web/complete | appId, flowId, handle, verifier | status COMPLETE + 기존SessionTokens 또는 CANCELED/FAILED + session:null; no-store |

코드·키·provider token과 SDK access/refresh는 Native/Backend만 다룬다. session 응답은 Native가 기존 `/v1/me`로 재확인해 보안 저장소에 저장한다. 공개 Unity 결과는 UserProfile뿐이다. 이전 C ABI4개와 C# API를 유지하고 iOS GB_HandleAuthURL, Android onSocialActivityResult/onSocialRedirect의 Native 전용 Host forwarding을 추가했다. JSON Schema의 UserProfile.provider는 기존부터 string이라 enum 축소/이전 fixture 변경이 필요 없다. HTTP DTO/form/redirect 계약은 [OpenAPI](../contracts/openapi.yaml), 증명 정책은 [social-auth](../contracts/social-auth.md)를 따른다.
