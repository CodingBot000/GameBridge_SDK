# Unity C# API 안내

> GameBridge SDK `0.1.0-dev`의 **현재 공개 소스 기준**입니다. 아래 메서드가 존재한다는 사실과 실제 Unity Player/스토어에서 동작이 검증되었다는 사실은 다릅니다. 검증 상태는 [기능 매트릭스](FEATURE_MATRIX.md), [진행 원장](PROGRESS.md)을 확인하세요.

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
| `PlatformSandbox` | Android Google/Play 또는 iOS Apple/StoreKit Sandbox 경로 | 플랫폼 계정·Host 설정이 필요. 실제 통합 검증 미완료 |

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
| `SignInAsync(AuthProvider.MOCK / GOOGLE / APPLE)` | 해당 모드·플랫폼의 로그인 요청 |
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
- **Platform Sandbox:** Provider 연결 코드·synthetic 시험 ≠ 실제 Google/Apple 로그인·스토어·원격 푸시 성공.
- **Xcode StoreKit:** iOS 18.6 일부 통과, iOS 26.5 별도 로컬 실패가 기록됨.

구현·검증 결과의 최신 공식 근거는 [PROGRESS](PROGRESS.md), [WORK_LOG](WORK_LOG.md), [FINAL_REPORT](FINAL_REPORT.md)에서 확인하세요.
