# GameBridge SDK

![Status](https://img.shields.io/badge/status-development-orange)
![Version](https://img.shields.io/badge/version-0.1.0--dev-blue)
![Platforms](https://img.shields.io/badge/platforms-Unity%20%7C%20Android%20%7C%20iOS-555555)

**Unity 게임에서 Android·iOS 네이티브 기능과 게임 Backend를 하나의 C# 인터페이스로 연결하는 SDK 프로젝트입니다.**

로그인, 상품 조회·인앱 결제, 서버 재화, 푸시 알림과 진단 기능을 다룹니다. Unity C# SDK, Kotlin/Swift 네이티브 브리지, Spring Boot·PostgreSQL Backend로 구성되어 있습니다.

> [!IMPORTANT]
> **현재 버전은 `0.1.0-dev` (개발 중)이며 배포 가능한 상용 SDK가 아닙니다.** 일부 Native·LOCAL_MOCK·Fake 경로만 검증했습니다. Unity Editor import/Player/IL2CPP 전체 통합, 실제 Google·Apple 계정/스토어 결제, FCM/APNs 원격 전달은 검증 완료 상태가 아닙니다. 아래 Quick Start 역시 **Editor용 가상 데이터 예제**이며 실제 구매를 수행하지 않습니다.

**바로가기:** [5분 둘러보기](#quick-start--unity-editor-offline) · [지원 환경](#지원-환경) · [공개-api](docs/API.md) · [통합 가이드](docs/INTEGRATION.md) · [검증 현황](#검증-현황과-제한사항)

## 주요 기능

| 기능 | Unity에서 사용하는 기능 | 구현·검증 범위 |
| --- | --- | --- |
| **Authentication** | 로그인, 세션 복원, 로그아웃 | Editor Fake 및 Native LOCAL_MOCK 경로 확인. 실제 Google/Apple 인증 미검증 |
| **In-App Purchase** | 상품 조회, 구매, 구매 복원 | Mock 원장·중복 지급 방지 일부 검증. 실제 Play Billing/StoreKit 결제 미검증 |
| **Entitlements** | 서버 재화 잔액·구매 권한 조회 | LOCAL_MOCK Backend·PostgreSQL 경로 일부 검증 |
| **Push Notifications** | 알림 권한, 등록·해제, 수신·열기 | Native Mock·가상 수신 일부 확인. 실제 FCM/APNs 및 Unity Player 미검증 |
| **Configuration & Diagnostics** | 서비스 설정, SDK 상태·진단 조회 | Fake·Native 경계 검사; 실제 Unity Player 미검증 |

`LOCAL_MOCK`의 구매·잔액은 개발용 로컬 Backend에서 처리합니다. **Google/Apple Store 결제 또는 서버의 실제 스토어 서명 검증 성공을 의미하지 않습니다.** 기능별 세부 상태는 [기능 매트릭스](docs/FEATURE_MATRIX.md)에서 구분합니다.

## 구조 한눈에 보기

```mermaid
flowchart TB
    U["Unity Game (C#)"] --> F["GameBridgeSdk / GameBridgeClient"]
    F --> A["Android JNI → Kotlin SDK"]
    F --> I["iOS C ABI → Swift SDK"]
    A --> B["GameBridge Backend (Spring Boot)"]
    I --> B
    B --> D["PostgreSQL · 세션 / 구매 원장 / 재화"]
```

게임에서는 C# API를 호출하고, 플랫폼별 기능은 Android/iOS Native 쪽에서 처리합니다. Backend는 개발용 인증 세션과 구매 지급·중복 처리 등을 담당합니다. 실제 인증·결제·푸시 제공자 연동은 플랫폼 설정이 추가로 필요하며 위 그림은 **구성도이지 전체 E2E 통과를 나타내는 그림이 아닙니다.**

## 지원 환경

| 구성 요소 | 현재 개발·확인 기준 | 주의 |
| --- | --- | --- |
| Unity | 패키지 설정: **6000.5** / 관리 코드 컴파일 기준: **6000.5.8f1** | Editor import, 장면 실행, IL2CPP 및 Player 미검증 |
| Android | Kotlin·JNI, API 36 빌드, JDK 21 | Unity Android Player·실제 Google/Play/FCM 미검증 |
| iOS | Swift·C ABI, Xcode 26.6, XCFramework 소비 링크 | Unity iOS Player·실기기 서명·실제 Apple/StoreKit/APNs 미검증 |
| Backend | Spring Boot·JDK 21·PostgreSQL 17 계열 | 로컬/격리 시험 기준, 운영 검증 아님 |

위 버전은 **확인된 개발 조합**이며 최소 지원 버전이나 다른 조합의 호환성 보증이 아닙니다. 자세한 내용은 [호환성](docs/COMPATIBILITY.md)과 [도구 버전](docs/TOOLCHAIN.md)을 확인하세요.

## Quick Start — Unity Editor Offline

**목표:** 외부 계정, 결제 콘솔, Backend 없이 C# SDK의 호출 형태와 가상 로그인·상품 조회를 살펴봅니다.

1. 저장소를 clone하고 Unity **6000.5 계열**로 별도 테스트 프로젝트를 준비합니다.
2. Unity **Window → Package Manager → + → Add package from disk**에서 `unity/Packages/com.gamebridge.sdk/package.json`을 선택합니다. 이 로컬 패키지는 개발 소스이므로 정식 배포 패키지로 간주하면 안 됩니다.
3. Package Manager의 GameBridge SDK **Samples**에서 **Editor Offline Demo**를 Import합니다. UI 샘플에는 `com.unity.ugui`가 필요합니다.
4. 테스트 Scene의 빈 GameObject에 `OfflineDemo` 컴포넌트를 추가하고, 프로젝트 입력 방식에 맞는 EventSystem을 하나 준비합니다.
5. Editor Play로 Home/Store의 가상 로그인·상품 조회·구매 UI를 살펴봅니다.

[Offline Demo 설명·제약](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/README.md) · [실제 샘플 C# 코드](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/OfflineDemo.cs)

동일한 흐름을 직접 작성한다면 다음과 같습니다. `GameBridgeSdk.Create`와 생명주기 API는 Unity 메인 스레드에서 호출하세요.

```csharp
using GameBridge;
using GameBridge.Core;
using UnityEngine;

public sealed class GameBridgeQuickStart : MonoBehaviour
{
    private GameBridgeClient sdk;

    private async void Start()
    {
        try
        {
            // Editor 전용: 실제 로그인·구매·Backend 연결 없음
            var config = new GameBridgeConfig(
                "gamebridge-sample", ProviderMode.EditorOffline, null);

            sdk = GameBridgeSdk.Create(config);
            await sdk.InitializeAsync(config);
            await sdk.SignInAsync(AuthProvider.MOCK);

            var products = await sdk.GetProductsAsync();
            Debug.Log("Mock products: " + products.Count);
        }
        catch (SdkException error)
        {
            Debug.LogError("GameBridge: " + error.Code);
        }
    }

    private void OnDestroy()
    {
        sdk?.Dispose();
    }
}
```

> **실행 검증 주의:** 예제는 저장소의 공개 C# API 및 Offline Demo 소스를 토대로 작성했습니다. 원격 저장소에 기록된 검증은 관리 코드 컴파일까지이며, Unity Editor 라이선스 문제로 실제 Import·Play 실행은 **미검증**입니다.

## Android / iOS Native 연동

Editor Offline과 달리 **Native LOCAL_MOCK / PLATFORM_SANDBOX**는 플랫폼별 산출물 및 Host 설정이 필요합니다.

| 단계 | 확인할 곳 |
| --- | --- |
| 1. Android Maven/AAR 또는 iOS XCFramework 생성 | [통합 가이드 — 패키지 소비](docs/INTEGRATION.md#패키지-소비) |
| 2. Unity UPM staging 준비 및 Native Demo | [Native Demo](unity/Packages/com.gamebridge.sdk/Samples~/Native%20Demo/README.md) |
| 3. Backend 및 테스트 계정·결제·푸시 설정 | [사용자 설정](docs/USER_SETUP.md) |
| 4. API와 결과 상태·에러 처리 | [API 가이드](docs/API.md) |

`LOCAL_MOCK`는 개발 서버 키와 테스트용 Backend를 요구합니다. `PLATFORM_SANDBOX`는 실제 플랫폼 개발자 계정과 별도 설정이 필요합니다. **실제 키·토큰은 소스, Unity 에셋, 로그에 넣지 마세요.** 브리지 연결·로컬 배포 산출물을 만드는 작업과 Unity Player에서 통과한 작업은 별개입니다.

## 개발·검증 명령

로컬 개발 환경에서 사용하는 대표 명령입니다. 필요한 환경변수·전용 DB·산출물 경로는 [사용자 설정](docs/USER_SETUP.md)과 [통합 가이드](docs/INTEGRATION.md)를 먼저 확인하세요.

```bash
# 개발용 Backend: 전용 DB 비밀번호 및 인증·암호화 키 필요
bash scripts/run-demo-backend.sh

# Android Mock SDK 산출물 / iOS 개발용 프로젝트 및 빌드
bash scripts/build-android.sh --mock
bash scripts/generate-ios-project.sh
bash scripts/build-ios.sh --simulator

# 로컬 검사 집계 (PASS / FAIL / 미실행 구분)
bash scripts/verify-all.sh --available
```

생성되는 `artifacts/`는 로컬용이며 공개 Release가 아닙니다. Backend 단위 테스트만으로 DB 통합·Unity Player 테스트까지 실행됐다고 해석하면 안 됩니다.

## 검증 현황과 제한사항

- **확인한 범위:** Kotlin/Swift Native Mock·일부 로컬 Backend/DB, 독립 Android 소비 빌드·iOS XCFramework 링크, Unity C# 관리 코드 컴파일 등.
- **미검증:** Unity Editor import·장면 실행·Android/iOS Player·IL2CPP, 실계정 인증, 실제 스토어 거래, 원격 FCM/APNs.
- **기록된 실패:** iOS 26.5 로컬 StoreKit 상품 조회 시험. iOS 18.6의 일부 별도 시험 PASS가 이를 대체하지 않습니다.
- **전체 판정:** 제품 전체 검증 게이트는 통과한 상태가 아닙니다. 자세한 실패·보류·환경 제약은 [진행 원장](docs/PROGRESS.md)과 [최종 보고](docs/FINAL_REPORT.md)에서 확인하세요.

## 문서 안내

| 문서 | 읽는 목적 |
| --- | --- |
| [API](docs/API.md) | Unity 개발자를 위한 메서드·이벤트·오류 설명 |
| [통합 안내](docs/INTEGRATION.md) | Android/iOS Host, Native 패키징, 인증·구매·푸시 통합 |
| [샘플: Offline Demo](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/README.md) | Backend 없는 Unity Editor Fake 둘러보기 |
| [샘플: Native Demo](unity/Packages/com.gamebridge.sdk/Samples~/Native%20Demo/README.md) | LOCAL_MOCK 및 플랫폼 Sandbox 설정 |
| [호환성](docs/COMPATIBILITY.md) · [기능별 확인](docs/FEATURE_MATRIX.md) | 플랫폼 지원 범위와 미검증 항목 |
| [보안](docs/SECURITY.md) · [사용자 설정](docs/USER_SETUP.md) | 비밀정보·Host 소유권·실연동 준비 |
| [진행 원장](docs/PROGRESS.md) · [작업 기록](docs/WORK_LOG.md) | 개발 내부 진행 및 실제 검증 증거 |
| [변경 이력](docs/CHANGELOG.md) | 개발 버전별 변경 사항 |

본 README는 **처음 방문하는 사람을 위한 안내**입니다. 작업 ID·세부 로그·재현 명령은 링크된 기술 문서에서 유지합니다.
