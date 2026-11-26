# GameBridge SDK

![Status](https://img.shields.io/badge/status-development-orange) ![Version](https://img.shields.io/badge/version-0.1.2--dev-blue) ![Platforms](https://img.shields.io/badge/platforms-Unity%20%7C%20Android%20%7C%20iOS-555555)

**Unity 게임에서 Android·iOS의 인증·결제·푸시 기능을 하나의 C# API로 사용하는 모바일 게임 SDK입니다.** Unity C# SDK와 Kotlin/Swift Native 브리지, Spring Boot·PostgreSQL Backend를 직접 연결해 플랫폼별 구현 차이와 서버 데이터의 책임을 분리했습니다.

> **프로젝트 상태** 개인 개발 포트폴리오입니다. 최신 개발자용 배포본은 [`v0.1.2-dev` Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)입니다.

**바로가기:** [주요 기능](#주요-기능) · [아키텍처](#구조-한눈에-보기) · [기술적 핵심](#기술적-핵심) · [패키지 설치](#개발자용-pre-release-설치) · [Quick Start](#quick-start--unity-editor-offline) · [검증 결과](#검증-현황과-제한사항)

**대표 검증 성과** Android API 34와 iOS 18.6에서 `0.1.1-dev → 0.1.2-dev` 덮어 설치 후 세션과 미완료 구매가 복구됐고, 재동기화 후 각 원장은 1건·100코인이었습니다.

## 주요 기능

| 기능 | Unity에서 사용하는 기능 | 핵심 API / 이벤트 |
| --- | --- | --- |
| **Authentication** | Google·Apple·Facebook 로그인, 세션 복원·로그아웃 | `SignInAsync`, `RestoreSessionAsync`, `SignOutAsync` |
| **In-App Purchase** | Google Play Billing / Apple StoreKit 상품 조회·구매·복원 | `GetProductsAsync`, `PurchaseAsync`, `SyncPurchasesAsync` |
| **Entitlements** | 서버가 관리하는 코인 잔액·프리미엄 권한 | `GetEntitlementsAsync`, `PurchaseUpdated` |
| **Push Notifications** | FCM / APNs 등록·해제, 수신·열기 이벤트 | `RegisterPushAsync`, `PushReceived`, `PushOpened` |
| **Config & Diagnostics** | 점검 설정·캐시, SDK 상태·기능·진단 조회 | `GetServiceConfigAsync`, `GetStatus`, `GetDiagnostics` |

### 지원 로그인

| 제공자 | Android | iOS |
| --- | --- | --- |
| **Google** | Credential Manager · 이전 실계정 AVD 증거 | GoogleSignIn 9.2.0 · 이전 실계정 Simulator 증거 |
| **Apple** | 웹 OAuth · Custom Tabs | AuthenticationServices |
| **Facebook** | Meta Classic Login | Meta Limited / Classic Login |
| **Mock** | 개발용 `LOCAL_MOCK` | 개발용 `LOCAL_MOCK` |

로그인 공급자의 원본 토큰과 인증 증빙은 Native·Backend에서 처리하고, Unity에는 사용자/세션 결과만 전달합니다. [인증·Host 설정](docs/USER_SETUP.md) · [C# API 전체](docs/API.md)

## 구조 한눈에 보기

```mermaid
flowchart TB
    U["Unity Game · GameBridgeClient (C#)"]
    A["Android · JNI / Kotlin SDK"]
    I["iOS · C ABI / Swift SDK"]
    PA["Google · Apple · Meta / Billing / FCM"]
    PI["Google · Apple · Meta / StoreKit / APNs"]
    B["GameBridge Backend · Spring Boot"]
    D[("PostgreSQL · Session / Purchase Ledger / Entitlement")]
    U --> A
    U --> I
    A --> PA
    I --> PI
    A --> B
    I --> B
    B --> D
```

**클라이언트는 인증·구매 요청을 전달하고, Backend는 세션 발급과 재화 지급의 최종 권한을 갖습니다.** 구매 UI의 성공 메시지만으로 재화를 지급하지 않고 서버 원장과 권한 조회 결과를 사용합니다.

## 기술적 핵심

- **플랫폼 경계를 넘는 비동기 SDK:** Unity C# 공통 API와 Android JNI·iOS C ABI를 연결했습니다. `requestId`·세션 세대·메인 스레드 디스패치로 중복 완료, 타임아웃, 취소, 늦은 콜백을 관리합니다.
- **인증·세션 보안:** Provider 증명과 nonce challenge를 Backend에서 검증하고, Native 보안 저장소(Android Keystore / iOS Keychain)를 사용합니다. Unity 이벤트·로그에는 인증 토큰 원문을 노출하지 않도록 경계를 분리했습니다.
- **멱등 구매·재화 관리:** PostgreSQL 거래 유일성 제약과 멱등 원장으로 중복 지급을 방어하고, 구매 결과·서버 지급·재화 조회 및 응답 유실 후 복구를 별개 상태로 다룹니다.
- **Unity iOS 연동 문제 해결:** Google OAuth의 AppController·UnityScene URL 경로를 분리해 처리하고, Meta 동적 Framework 4개의 Host 앱 Embed·서명 문제를 수정했습니다. Export 후처리의 반복 적용과 충돌 방지도 검증했습니다.
- **SDK 버전 관리·패키징:** Maven/AAR·R8, XCFramework·Swift 소비, UPM의 버전 정합성과 체크섬을 검사하고 기존 SDK 업데이트 시 선정 API·ABI 및 세션·미완료 구매 복구를 검증했습니다.

**0.1.2-dev 리팩토링** Android `BridgeFacade`는 공급자별 오류와 세션 소유권을 유지하며 Store 수명주기와 FCM 토큰 획득을 공통화했습니다. Unity `GameBridgeClient`는 상태 모델과 진단·Capability JSON 변환을 분리하고 초기화·종료·이벤트 수명주기를 기존 Facade에 유지했습니다. [리팩토링 상세와 검증 근거](docs/evidence/bridge-client-refactor-verification.md)

구현과 장애 분석은 [설계·Edge Case·문제 해결](docs/ENGINEERING_NOTES.md)과 [보안·데이터 소유권](docs/SECURITY.md)을 참고하세요.

## 개발자용 Pre-release 설치

[GitHub Pre-release v0.1.2-dev](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)에서 패키지를 다운로드할 수 있습니다. Release 자산 6개를 같은 디렉터리에 받은 뒤 `shasum -a 256 -c SHA256SUMS`로 확인합니다.

| 대상 | 설치 방법 |
| --- | --- |
| **Unity** | Package Manager → **Add package from tarball**에서 `com.gamebridge.sdk-0.1.2-dev.tgz`를 선택합니다. Native Maven과 XCFramework를 포함하며 최소 Unity 버전은 6000.5입니다. |
| **Android** | `GameBridge-Maven-0.1.2-dev.zip`을 풀고 Gradle 저장소에 `maven-repo`, `google()`, `mavenCentral()`을 추가한 뒤 `com.gamebridge:sdk-android:0.1.2-dev`를 사용합니다. |
| **iOS** | `GameBridgeNative-0.1.2-dev.xcframework.zip`을 풀고 Xcode 앱 대상에 `GameBridgeNative.xcframework`를 링크한 뒤 **Do Not Embed**를 선택합니다. |

GameBridge는 포트폴리오 평가와 비상업적 테스트에 사용할 수 있습니다. [Native 통합 및 Host 설정](docs/INTEGRATION.md) · [GameBridge 라이선스](LICENSE) · [외부 의존성 고지](THIRD_PARTY_NOTICES)

## Quick Start — Unity Editor Offline

외부 계정·개발 서버 없이 SDK 인터페이스를 살펴볼 수 있는 **Unity Editor 전용 메모리 Fake** 예제입니다.

1. Unity **6000.5 계열** 프로젝트에서 위의 TGZ를 추가합니다. 소스 checkout은 Package Manager의 **Add package from disk**에서 [`package.json`](unity/Packages/com.gamebridge.sdk/package.json)을 선택할 수 있습니다.
2. 패키지 **Samples → Editor Offline Demo**를 Import합니다. UI에는 `com.unity.ugui`가 필요합니다.
3. Scene의 GameObject에 `OfflineDemo`를 붙이고 호환되는 EventSystem을 준비합니다.
4. Editor Play에서 로그인·상품 목록·가상 구매 흐름을 확인합니다.

공통 C# API 호출 형태:

```csharp
// Unity 메인 스레드의 비동기 호출 지점에서 사용
var config = new GameBridgeConfig("gamebridge-sample", ProviderMode.EditorOffline, null);
var sdk = GameBridgeSdk.Create(config);
await sdk.InitializeAsync(config);
await sdk.SignInAsync(AuthProvider.MOCK);
var products = await sdk.GetProductsAsync();
sdk.Dispose();
```

[실행 가능한 Offline Demo](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/README.md) · [소스](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/OfflineDemo.cs)

### Native / 플랫폼 Sandbox 연동

Android/iOS Player는 별도 Native 패키지·Host·Backend 설정을 사용합니다. 플랫폼 인증 설정을 완료한 뒤에도 동일한 Unity API로 호출합니다.

```csharp
var user = await sdk.SignInAsync(AuthProvider.GOOGLE);
var session = await sdk.RestoreSessionAsync();
await sdk.SignOutAsync();
```

[Native Demo](unity/Packages/com.gamebridge.sdk/Samples~/Native%20Demo/README.md) · [Native 통합 및 빌드 절차](docs/INTEGRATION.md) · [설정](docs/USER_SETUP.md)

## 검증 현황과 제한사항

| 검증 영역 | 확인한 결과 | 근거 |
| --- | --- | --- |
| **SDK 업데이트** | Android API 34·iOS 18.6에서 `0.1.1-dev → 0.1.2-dev` 덮어 설치, 세션·구매 복구 및 플랫폼별 원장 1건·100코인 | [업데이트 검증](docs/evidence/bridge-client-refactor-verification.md#이전-공개-버전에서-업데이트) |
| **Unity·OS 호환성** | 0.1.2-dev는 Unity 6000.5.8f1의 Android API 34 AVD와 iOS 18.6 Simulator에서 실행 검증 | [버전별 근거](docs/COMPATIBILITY.md) |
| **패키징·계약** | 0.1.2-dev Maven·XCFramework·UPM, SHA-256, C# 공개 메타데이터, 선정 JVM 5개 클래스와 JNI·C ABI 5개 심볼 비교 | [API·ABI 근거](docs/evidence/bridge-client-refactor-verification.md#변경과-호환성) |
| **후속 Player 회귀** | 양 플랫폼 합성 PII 및 로그아웃 후 복원·종료, iOS LOCAL_MOCK Push 통과 | [실행 근거](docs/evidence/bridge-client-refactor-verification.md#2026-11-26-후속-실제-player-검증) |
| **Google 실계정** | 이전 Android API 34 AVD·iOS 18.6 Simulator에서 로그인·복원·취소·로그아웃을 확인했습니다. 0.1.2-dev 재검증은 미실행입니다. | [Android](docs/evidence/android-google-live-20261125.md) · [iOS](docs/IOS_GOOGLE_OAUTH_VERIFICATION.md) |
| **Unity iOS 콜백·Export 복구** | PBX·콜백 검사 157개, 네 쓰기 지점의 중단 복구, Host 편집 보존, Framework Embed·서명 | [PR #11](https://github.com/CodingBot000/GameBridge_SDK/pull/11) |
| **Hosted CI** | PR #18 HEAD `46988f8`의 기본 5개 성공. Unity E2E 및 Release Readiness SKIPPED | [CI 실행](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45812418546) |

`EDITOR_OFFLINE`은 메모리 Fake, `LOCAL_MOCK`은 로컬 Native·Backend 개발 경로입니다. 가상 구매는 실제 스토어 거래가 아닙니다. 실제 Google 토큰 갱신/replay, Apple·Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs, 실기기, Unity 6000.4 및 전체 Strict/Hosted Unity E2E·Release 검증은 미완료이며 기존 StoreKit 26.5 실패도 유지합니다. [검증 범위](docs/FEATURE_MATRIX.md) · [알려진 제한](docs/ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)

**0.1.2-dev 검증 환경** Unity 6000.5.8f1 · Android API 34 AVD(빌드 API 36, JDK 21) · iOS 18.6 Simulator(Xcode 26.6) · Spring Boot/PostgreSQL. Android API 30·36 및 iOS 26.5 LOCAL_MOCK은 [이전 Batch B](docs/evidence/batch-b48-compatibility.md)의 실행 기록입니다.

## 문서 안내

| 문서 | 내용 |
| --- | --- |
| [API](docs/API.md) · [통합 가이드](docs/INTEGRATION.md) | C# API·오류·이벤트, Native 패키징과 Host 설정 |
| [설계·문제 해결](docs/ENGINEERING_NOTES.md) · [보안](docs/SECURITY.md) | 브리지 경계·Edge Case·원장·토큰 소유권 |
| [Android Google](docs/evidence/android-google-live-20261125.md) · [iOS Google](docs/IOS_GOOGLE_OAUTH_VERIFICATION.md) | 실제 인증·세션 수명주기 검증 |
| [진행 기록](docs/PROGRESS.md) · [변경 이력](docs/CHANGELOG.md) | 시점별 테스트 근거와 개발 이력 |
| [호환성](docs/COMPATIBILITY.md) · [사용자 설정](docs/USER_SETUP.md) | 검증한 조합·플랫폼 연동 준비 |
| [기능 매트릭스](docs/FEATURE_MATRIX.md) · [최종 보고](docs/FINAL_REPORT.md) | 실제 검증 범위와 완료 판정 |

이 저장소는 개인 기술 포트폴리오이며, 상용 게임 출시나 외부 고객 운영 실적을 의미하지 않습니다.
