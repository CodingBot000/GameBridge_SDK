# GameBridge SDK — Codex 상세 개발계획서

- 문서 버전: 1.0 / 작성 기준: 2026-11-10
- 목적: 웹젠 SDK 앱 개발자·그라비티 플랫폼서비스 클라이언트 개발자 공고에 대응하는, 재사용 가능한 게임 서비스 SDK 포트폴리오
- 실행 대상: 사용자가 선택한 Codex Terra Medium. 특정 모델의 완주 성능을 보증하는 문서가 아니라, 판단 부담을 줄인 작업 계약이다.
- 구현 순서: **기능 개발 → 패키징·샘플 → 하네스 → 리팩토링 → 누락 감사·사용자 인계**
- 자동 실행 범위: P00~P11. 계정/콘솔/실키/서명/외부 실연동 확인은 사용자 설정 후 수행한다.
- 현재 상태: 계획만 작성됨. 소스 작성·빌드·테스트·커밋 수행 사실 없음.

## 0. 반드시 지킬 실행 계약

### 0.1 멈추지 않는 개발의 의미

계획 설명으로 끝내지 말고 실제 파일을 작성하고 명령을 실행한다. 각 Task를 마치면 문서를 갱신하고 로컬 커밋을 남긴 뒤 다음 Task를 즉시 수행한다. 단계 종료는 사용자 승인 요청 지점이 아니다. 명확한 기본 선택이 본문에 있으면 그대로 사용한다. 사소한 선택 때문에 질문하지 않는다.

한 플랫폼의 실행환경이나 계정이 없으면 그 플랫폼의 소스·설정·문서·실행 스크립트를 가능한 데까지 작성하고 독립 작업을 계속한다. 인증이 없다는 이유로 인증 Provider 자체를 구현하지 않거나 전체 개발을 멈추지 않는다. 반대로 빈 구현을 작성하고 전체 완료라고 보고하지 않는다.

단, 사용량/컨텍스트/세션/권한/안전 제약은 우회하지 않는다. 불가피한 세션 종료 직전에는 현재 Task, 마지막 실행 명령, 작업 트리 상태, 재개할 다음 행동을 기록한다. 이 경우 상태는 `INTERRUPTED`이지 `COMPLETE`가 아니다.

### 0.2 완료의 두 단계

**개발 인계 완료 `LOCAL_READY_EXTERNAL_PENDING`**: 계획된 코드·샘플·패키징·하네스·리팩토링이 구현되고, 필수 로컬 검증이 실제로 통과했으며, 외부 인증이 필요한 검증만 명시적으로 남은 상태다. 이것이 첫 무인 개발 세션의 목표다.

**외부 검증 완료 `SANDBOX_VERIFIED`**: 사용자가 콘솔·서명·실키를 설정한 다음 Android/iOS 실기기 로그인, 테스트 결제, 원격 푸시와 Unity 실연동을 확인한 상태다. 첫 단계와 같지 않다. 두 상태 모두 상용 운영 준비 완료를 뜻하지 않는다. 환불 서버 알림/전체 보안 심사/스토어 심사/운영 SLA는 이번 범위 밖이다.

필수 로컬 검증이 환경 때문에 실행되지 않으면 `IMPLEMENTED_ENV_PENDING`; 내부 실패·미구현이 남으면 `BLOCKED_INTERNAL`; 실제 작업 미종료는 `IN_PROGRESS`다. 실기기 부재를 인증 대기로 숨기지 않는다.

### 0.3 기록 없이는 작업 완료가 아니다

다음 사건마다 `PROGRESS.md`와 `WORK_LOG.md`를 갱신한다: Task 시작, 의미 있는 구현 결과, 검증 실행 결과, 블로커 발견, 커밋 직전, Phase 종료, 세션 종료. 커밋에 코드만 있고 두 상태 문서가 없으면 완료 절차를 충족하지 않은 것이다.

`WORK_LOG.md`에는 원인 추측 대신 실제 명령·종료 코드·관측 결과를 기록한다. 예상 명령은 계획에, 실제 명령은 로그에 쓴다. 코드 리뷰만 했다면 `REVIEW_ONLY`로 표시한다. 테스트 실행 수가 0인데 테스트 성공이라고 쓰지 않는다. 이전 실패는 삭제하지 않고 후속 수정과 연결한다.

### 0.4 범위 변경 권한

파일명·내부 타입명·호환되는 의존성 패치 버전은 필요한 경우 조정하고 `docs/DECISIONS.md`에 이유를 기록한다. 결제 불변식·플랫폼 범위·공개 API 의미·인증 대기 정책은 임의 축소하지 않는다. 이 문서의 작업을 다른 설계 문서로 대체하거나 더 큰 프레임워크 개발로 확장하지 않는다.

## 1. 목표 산출물과 제외 범위

### 1.1 이번 실행에서 만드는 것

| 산출물 | 내용 | 완료 증거 |
|---|---|---|
| Kotlin Android SDK | Core, Google 인증, Play Billing, FCM, 서버 통신, Unity Bridge | AAR/Maven 산출물, 단독 앱 및 Unity 소비 빌드 |
| Swift iOS SDK | Core, Apple 인증, StoreKit 2, APNs Host 연동, 서버 통신, C ABI | Swift Package 소스, static XCFramework, 소비 빌드 |
| Unity SDK | 공통 C# API, Android/iOS transport, Editor Mock, 이벤트, 오류, 설치 도구 | UPM 패키지, Demo, 실제/대기 상태를 구분한 검증 |
| Backend | Kotlin Spring Boot, 인증 검증, 세션, 구매 원장·지급, 토큰 등록, 개발용 푸시 전송 | Docker Compose, PostgreSQL migration, API·트랜잭션 검증 |
| 샘플 | Android Compose, iOS SwiftUI, Unity 버튼 기반 실습 장면 | SDK public API만 사용하는 소비자 |
| 후반 품질 체계 | 계약 테스트, 실패 주입, 회귀, CI 설정, 호환성·재현성 확인 | 실행 증거와 실패하는 부정 시험 |
| 문서 | 설치, API, 상태/오류, 변경 내역, 사용자 설정, 최종 누락 목록 | 깨끗한 환경에서 따라 할 수 있는 명령 |

### 1.2 기능 범위 고정

인증은 Android Google·iOS Apple·개발 전용 Mock 계정이다. 로그인/로그아웃/세션 복원/갱신을 포함한다. 계정 연결·이메일 가입·다른 플랫폼의 인증 제공자 확장은 제외한다.

결제는 `coins_100` 소모성 상품과 `premium_unlock` 비소모성 상품이다. 실제 스토어 상품 ID는 설정에서 매핑한다. 구독, 프로모션, 다중 수량 구매, 게임 내 코인 소비, 환불 자동화는 제외한다. 다중 수량이 들어오면 지원하지 않음을 명확히 반환하며 1개로 임의 계산하지 않는다.

푸시는 Android FCM·iOS APNs를 지원한다. 권한/토큰 등록·갱신·해제, 전경 수신, 클릭·콜드스타트 라우팅을 구현한다. 운영용 캠페인 관리·예약 발송·분석 대시보드는 제외한다.

추가 범위는 진단 로그, 설정/점검 모드, `home`/`store` 두 경로의 알림 라우팅, 호환성 자료까지로 제한한다. 범용 Deep Link 라우터·Universal Links/Android App Links 도메인 검증은 이번 범위가 아니다.

Windows/C++·Unreal·Godot·웹 관리자·멀티플레이 게임·Kubernetes·Kafka·Redis·상용 클라우드 구축은 제외한다. 본인 이름의 실제 사업자 서비스나 회사 내부 SDK로 오인되게 표현하지 않는다.

### 1.3 언어와 구조

Android와 Backend는 Kotlin, iOS는 Swift, Unity는 C#이다. C ABI는 호출 규약이지 C++ 플랫폼 개발을 추가하라는 뜻이 아니다. Swift `@_cdecl` export를 우선한다. Unity/Apple/Google 의존성 내부의 C/Objective-C/C++와 엔진 생성 코드는 자체 개발 언어 제약과 구분한다.

SDK에는 Hilt를 넣지 않는다. 생성자 주입·Factory·Provider interface만으로 조립한다. 앱이 DI 컨테이너나 특정 MVVM 프레임워크를 도입하지 않아도 설치할 수 있어야 한다. Kotlin Multiplatform을 새로 도입하지 않는다.

## 2. 저장소·문서·상태 모델

### 2.1 최종 디렉터리

```text
AGENTS.md
START_HERE.md
README.md
VERSION
Makefile
contracts/
  public-api.md
  error-codes.json
  bridge.schema.json
  models.schema.json
  openapi.yaml
  fixtures/
android/
  gradlew, gradle/wrapper/, gradle/libs.versions.toml
  sdk-core/                 # Kotlin 공통 모델·클라이언트·계약, Android 의존 최소화
  sdk-android/              # Keystore, Google, Billing, FCM, lifecycle
  sdk-unity-bridge/         # Kotlin JNI facade; Unity 클래스에 직접 링크하지 않음
  sdk-testing/              # Fake/fixtures. 배포 기본 경로에 포함하지 않음
  sample-app/              # Compose
  settings.gradle.kts
  build.gradle.kts
ios/
  Package.swift
  Sources/GameBridgeCore/
  Sources/GameBridgeApple/
  Sources/GameBridgeTesting/
  UnityBridge/              # Swift C export, package core와 별도 target
  SampleApp/                # SwiftUI 및 명시적 AppDelegate forwarding
  Framework/                # archive용 project 또는 재현 가능한 project spec
  StoreKit/GameBridge.storekit
  Tests/
unity/
  Packages/com.gamebridge.sdk/
    package.json, Runtime/, Editor/, Tests/, Samples~/, Plugins/
  Demo/Assets/, Packages/, ProjectSettings/
backend/
  gradlew, gradle/wrapper/, build.gradle.kts
  src/main/kotlin/.../{auth,session,catalog,purchase,wallet,push,config}/
  src/main/resources/db/migration/
  src/main/resources/application*.yaml
  src/test/
  Dockerfile
infra/compose.yaml
scripts/
  doctor.sh, build-android.sh, build-ios.sh, build-unity.sh
  run-demo-backend.sh, smoke-local.sh, package-sdk.sh
  verify-progress.py, verify-all.sh, verify-external.sh
  verify-release.sh, export-final-report.py
harness/                    # P09에서 작성. 초기에 프레임워크부터 만들지 않음
  scenarios/, fixtures/, regression-manifest.json
config/*.example.*
docs/
  DEVELOPMENT_PLAN.md, PROGRESS.md, WORK_LOG.md, USER_SETUP.md, FINAL_REPORT.md
  DECISIONS.md, TOOLCHAIN.md, ENVIRONMENT.md
  API.md, INTEGRATION.md, SECURITY.md, COMPATIBILITY.md, CHANGELOG.md
  evidence/                 # 비밀정보 제거한 소규모 결과만 추적
artifacts/                  # 원시 로그·빌드·로컬 Maven repo·릴리스 staging, 기본 gitignore
```

파일 구조의 모든 하위 파일을 초반에 빈 파일로 생성하지 않는다. 각 Task에서 실제 구현과 함께 추가한다. 빈 README로 기능 완성을 대신하지 않는다.

### 2.2 상태 문서의 필드와 판정

`PROGRESS.md`는 작업 목록의 단일 원장이다. `WORK_LOG.md`는 시간순 증거 기록이다. 원장의 행을 삭제하지 않는다.

| 축 | 허용 값 | 의미 |
|---|---|---|
| 구현 | NOT_STARTED / IN_PROGRESS / IMPLEMENTED / BLOCKED | IMPLEMENTED는 의미 있는 코드·설정·산출물 작성 완료 |
| 로컬 검증 | NOT_RUN / PASS / FAIL / PARTIAL / DEFERRED_ENV / REVIEW_ONLY | 해당 Task의 로컬 완료 조건 기준 |
| 실연동 검증 | N/A / WAITING_USER / PASS / FAIL / DEFERRED_ENV | Mock·서명 없는 빌드로 PASS 불가 |
| 블로커 | 없음 / USER-xxx / ENV-xxx / BUG-xxx / DEP-xxx | 유형과 해소 조건을 별도 표로 기록 |

실연동이 필요한 Task라도 코드+로컬 검증이 끝났으면 `IMPLEMENTED / PASS / WAITING_USER`가 가능하다. 이 행을 실연동까지 완료된 행으로 계산하지 않는다. 테스트가 실패하면 구현 열만 IMPLEMENTED일 수 있고 로컬 검증은 FAIL이다.

**Task 완료율, 로컬 검증 통과율, 실연동 통과율을 별도로 표시한다.** 분모에서 대기 항목을 임의 삭제해 100%를 만들지 않는다. 같은 도구 부재는 하나의 ENV 항목으로 묶고 영향 Task를 나열한다.

### 2.3 커밋과 문서 갱신 절차

```text
Task 선택
→ PROGRESS: IN_PROGRESS, 다음 행동 기록
→ 구현
→ 가능한 최소 빌드/smoke 실행
→ PROGRESS: 구현/검증/실연동/증거/블로커 갱신
→ WORK_LOG: 실제 명령과 결과 추가
→ verify-progress 실행 (P00에서 작성한 단순 문서 일관성 검사)
→ git diff --check 및 변경 파일 검토
→ 해당 소스·상태 문서·정제된 증거만 stage
→ feat|fix|test|refactor|docs(scope): [TaskID] 요약 으로 로컬 commit
→ 결과 확인, 다음 Task
```

현재 커밋 자신의 SHA를 같은 커밋 문서에 넣는 순환 문제를 만들지 않는다. 진행 원장에는 Task ID를 사용하고 최종 보고 생성 시 `git log --all --grep='[TaskID]' --fixed-strings` 등으로 실제 이력을 조회한다. 최종 문서 커밋 자체의 SHA는 그 이후 Git 이력에서 확인하면 된다.

문서 검사 도구는 Task 누락/중복, 불법 상태 값, PASS의 증거 누락, IMPLEMENTED의 로그 누락, WAITING_USER의 설정 항목 누락을 검사한다. 이것은 초기 진행 기록 장치이며, P09의 제품 검증 하네스를 앞당겨 만드는 작업이 아니다.

## 3. 실행환경·버전·구성 기본값

### 3.1 의존성 선택 절차

버전은 추측해서 최신 번호를 쓰지 않는다. P00에서 현재 설치 도구와 공식 호환성 문서를 확인하고 **실제로 함께 빌드되는 조합 하나**를 고정한다. `TOOLCHAIN.md`에 정확한 버전, 출처, 선택 이유, 설치 여부, 검증 결과를 남긴다. 버전 범위 `+`, 무조건 latest, SNAPSHOT, alpha/beta는 사용하지 않는다.

| 항목 | 설계 기본값 | 확인 사항 |
|---|---|---|
| Android minSdk | 26 | 포트폴리오의 선택이며 회사 지원 범위라는 주장이 아님 |
| Android compile/target | 사용 가능한 안정 SDK 및 선택한 Unity와 호환 조합 | 스토어 제출 정책과 실제 빌드 가능성을 확인, 숫자 추측 금지 |
| Kotlin/JDK/AGP/Gradle | Android는 Unity export와 함께 확인, Backend는 독립 wrapper | Android JVM target 기본 17, Backend JDK 기본 21; 불일치 시 명시 조정 |
| iOS deployment | 16.0 | Swift/StoreKit/엔진의 실제 지원 조합으로 확인 |
| Xcode/Swift | 로컬 안정 설치본 | simulator/device build, concurrency 경고 기록 |
| Unity | 설치된 Unity 6 LTS 안정판 우선 | 없으면 현재 공식 지원 LTS를 선택해 기록; 특정 Swift project type을 필수 전제하지 않음 |
| Spring Boot | JDK/Kotlin과 맞는 지원 중인 안정 버전 | BOM으로 Spring 의존성을 관리 |
| PostgreSQL | 17 계열 안정 패치 기본 | Docker image tag/digest를 고정, 기존 개인 DB 연결 금지 |
| JSON | Kotlin kotlinx.serialization, Swift Codable, C# Unity 지원 Newtonsoft JSON | IL2CPP와 stripping 확인; System.Text.Json을 무조건 도입하지 않음 |

Unity 문서의 최신 버전 예제가 로컬 LTS에서 동일하게 동작한다고 가정하지 않는다. iOS는 **Swift로 빌드한 static XCFramework + C export**를 기준으로 해 새 Swift Xcode project type에 종속되지 않는다. C ABI export는 실제 Xcode/Unity 조합에서 초기에 증명한다. [S01][S02]

### 3.2 실행 모드 — 느슨한 fallback 금지

| 모드 | Provider | Backend | 사용 목적 |
|---|---|---|---|
| EDITOR_OFFLINE | C# Fake | 불필요 | Unity Editor UI·API·콜백 데모 |
| LOCAL_MOCK | Kotlin/Swift Fake 또는 C# Fake | 로컬 mock profile + PostgreSQL | API·로그인·구매 원장·중복 방지·재실행 |
| XCODE_STOREKIT | 실제 StoreKit + 로컬 .storekit | 격리된 development 검증 경로 | Apple 계정 설정 전 로컬 거래 동작 |
| PLATFORM_SANDBOX | Google/Apple/FCM/APNs 실제 Provider | sandbox profile | 사용자 설정 후 실연동 |

실서비스/샌드박스에서 Google 로그인 실패를 Mock 로그인으로 바꾸지 않는다. 선택한 모드와 Provider를 UI·진단 정보에 항상 표시한다. 개발 서버의 Mock identity/proof는 sandbox/production 프로필에서 수락하지 않는다.

개발용 fake proof를 수락하는 서버는 loopback에만 노출하는 것이 기본이다. Docker container 내부 bind는 실행에 맞게 하되 host port mapping을 `127.0.0.1`로 제한한다. 실기기 개발을 위해 LAN bind를 바꿀 때는 별도 명시 설정과 development key가 필요하며, 임의 public tunnel·외부 배포는 하지 않는다.

### 3.3 초기화 설정 모델

`appId`, `environment`, `providerMode`, `backendBaseUrl`, `clientInstanceId`, `requestTimeoutMs`, `googleServerClientId`(공개 식별자), `diagnosticsEnabled`를 구분한다. `appId`는 허용된 서버 설정 키일 뿐 인증 비밀키가 아니다. product ID, bundle ID, package name은 서버 허용 목록과 대조한다.

서비스 계정 JSON, Apple .p8, signing private key, DB 비밀번호, 운영 JWT/암호키는 SDK·Unity ScriptableObject·Git에 넣지 않는다. client secret이 필요한 서버 호출은 Backend에서만 한다. OAuth client ID/Firebase client config가 모두 비밀키인 것처럼 취급하지는 않되, 실제 프로젝트 설정은 샘플과 분리해 `.gitignore`한다.

비밀값은 `.env.local`/사용자 환경 변수/로컬 파일 경로에서 읽는다. 예제 파일에는 변수명과 가짜 값만 둔다. 설정 누락은 `CONFIG_REQUIRED`와 누락 키 이름을 반환하며 실제 값은 로그에 쓰지 않는다.

### 3.4 환경이 없을 때

Unity 라이선스·Xcode 선택·기기 신뢰·Android USB 디버깅·Docker 미실행은 USER/ENV 항목으로 남긴다. 자동 로그인·유료 가입·인증서 발급·비밀키 생성/삭제·계정 설정 변경은 하지 않는다. 프로젝트 로컬 의존성 설치와 이미 허용된 공식 package download는 가능하되 관리자 권한이나 시스템 전역 설치는 임의 수행하지 않는다.

Unity가 없으면 C# 소스·asmdef·package.json·샘플 생성 코드·테스트 코드를 작성한다. Editor 실행이나 IL2CPP 성공을 주장하지 않는다. Xcode가 없으면 Swift 코드를 가능한 범위까지 작성하되 `swift test`만으로 UIKit/StoreKit 빌드가 검증되었다고 쓰지 않는다. Docker가 없으면 PostgreSQL 통합 검증은 대기이며 H2로 대체해 같은 결과라고 하지 않는다.

## 4. 아키텍처·책임 분리

```text
Unity Demo ── C# GameBridge Public API ── Platform Adapter
                                            │
                    Android JNI ────────────┼──────────── iOS C ABI
                        │                   │                  │
                 Kotlin Native SDK         │           Swift Native SDK
                        │                   │                  │
                   Google/Billing/FCM       │         Apple/StoreKit/APNs Host
                        └────────────── Backend API ───────────┘
                                              │
                             Verifier → Purchase Service → PostgreSQL
```

**Native 대상에서 인증·결제·세션·백엔드 호출은 Native SDK가 소유한다.** C#은 API facade·요청 식별·메인스레드 이벤트 전달·화면만 담당한다. Unity에 세션 토큰을 복사해서 C#과 Native 양쪽이 갱신하지 않는다. Editor Adapter는 데모를 위해 같은 계약의 별도 Fake 또는 로컬 Backend 클라이언트를 사용한다.

제품 핵심 동작의 상태 권위는 Native coordinator다. C#은 Native 상태를 mirror하며, 아직 Native 결과가 없는 요청의 대기/취소 상태만 별도로 관리한다. C# 화면 상태를 근거로 Native 구매 상태를 임의 전환하지 않는다. SDK Core는 설정·상태·오류·Provider interface·Backend client 계약을 가진다. Android/iOS 구현체는 OS API·보안 저장소·생명주기를 담당한다. Backend가 계정·구매 지급·코인 잔액의 최종 권위다. 클라이언트 UI의 “구매 성공” 콜백만으로 재화를 더하지 않는다.

정적 `GameBridge` facade를 제공해도 내부 구현은 인스턴스 기반으로 만든다. 테스트에서 clock, transport, storage, providers, scheduler를 대체할 수 있게 하되, 범용 DI framework나 자체 플러그인 시스템을 만들지는 않는다.

## 5. 공개 API·모델·오류 계약

### 5.1 공통 API

아래는 의미를 고정하는 계약이다. 각 언어 관용구에 맞게 Kotlin `suspend`, Swift `async throws`, C# `Task<T>`를 사용한다. 예상 가능한 실패는 공통 `SdkError`로 변환한다. 로직마다 임의 문자열 오류를 새로 만들지 않는다.

```csharp
Task<InitResult> InitializeAsync(GameBridgeConfig config, CancellationToken ct = default);
SdkStatus GetStatus();
SdkCapabilities GetCapabilities();
Task<UserProfile> SignInAsync(AuthProvider provider, CancellationToken ct = default);
Task SignOutAsync(CancellationToken ct = default);
Task<SessionSnapshot> RestoreSessionAsync(CancellationToken ct = default);
Task<IReadOnlyList<StoreProduct>> GetProductsAsync(CancellationToken ct = default);
Task<PurchaseResult> PurchaseAsync(string productId, CancellationToken ct = default);
Task<EntitlementSnapshot> GetEntitlementsAsync(CancellationToken ct = default);
Task<PurchaseSyncResult> SyncPurchasesAsync(SyncReason reason, CancellationToken ct = default);
Task<PushPermission> RequestPushPermissionAsync(CancellationToken ct = default);
Task<PushRegistration> RegisterPushAsync(CancellationToken ct = default);
Task UnregisterPushAsync(CancellationToken ct = default);
Task<ServiceConfig> GetServiceConfigAsync(CancellationToken ct = default);
DiagnosticsSnapshot GetDiagnostics();
Task ShutdownAsync();
```

`GameBridge.Auth.*`, `GameBridge.Store.*`, `GameBridge.Push.*` 하위 facade로 노출해도 위 의미를 유지한다. 동기 getter `GetStatus`, `GetCapabilities`, `GetDiagnostics`는 최근 Native 응답/이벤트를 반영한 캐시 snapshot을 즉시 반환한다. Native 왕복을 기다리려고 Unity 메인스레드에서 `.Wait()`/`.Result`를 호출하지 않는다. 초기화 결과에 최초 snapshot을 포함하고, 내부 비동기 갱신 요청으로 cache를 업데이트하며 snapshot 시각을 표시한다. `UserProfile`에는 서버 user ID와 표시 이름·provider만 제공한다. access/refresh token, Apple authorization code, 원본 ID token, purchase proof, push token 원문을 Unity public result로 전달하지 않는다. push 결과에는 provider·등록 상태·마스킹된 fingerprint만 제공한다.

`SdkCapabilities`에는 각 기능의 `supported`, `configured`, `mode`, `reason`이 있다. 미설정 푸시 때문에 SDK 전체 초기화를 실패시키지 않는다. 단, 선택한 서버 기반 모드에 필수인 URL 자체가 잘못되면 초기화를 실패시킨다. Editor의 실제 Google/Apple 구매는 `UNSUPPORTED_PLATFORM`이며 Fake 지원과 구별한다.

`SyncReason`은 `APP_RESUME`와 `USER_RESTORE`를 구분한다. iOS `AppStore.sync()`는 사용자 복원 동작에서만 호출한다. 일반 앱 복귀마다 인증 UI를 유발하는 복원 API를 호출하지 않는다. [S09]

### 5.2 주요 데이터 모델

| 모델 | 필수 필드·규칙 |
|---|---|
| SdkStatus | state, sdkVersion, platform, mode, initializedAt, capabilities |
| UserProfile | userId(UUID 문자열), displayName(nullable), provider. email을 계정 primary key로 쓰지 않음 |
| SessionSnapshot | signedIn, user(nullable), expiresAt(nullable), sessionRestored. 토큰 원문 금지 |
| StoreProduct | productId(논리 ID), storeProductId, type(CONSUMABLE/NON_CONSUMABLE), title, localizedPrice, currencyCode, priceMicros(nullable 정수 문자열) |
| PurchaseResult | attemptId, productId, status, serverPurchaseId(nullable), fulfillmentStatus, finalizationStatus, error(nullable) |
| EntitlementSnapshot | userId, premiumEnabled, coinBalance(정수 문자열), revision(정수 문자열), updatedAt |
| PurchaseSyncResult | examinedCount, recoveredCount, deferredCount, failureCount, entitlements |
| PushRegistration | provider, registered, permission, tokenFingerprint(nullable), updatedAt |
| ServiceConfig | revision, maintenanceEnabled, message, expiresAt, source(NETWORK/CACHE/DEFAULT) |
| SdkError | code, message(비밀정보 없음), retryable, requestId, nativeCode(nullable), details(허용 목록만) |

JSON 숫자로 표현하면 언어/파서에 따라 정밀도가 달라질 수 있는 transaction ID·micro price·64-bit balance/revision은 **10진 문자열**로 교환한다. Kotlin/Swift/C# 내부에서는 범위 검사 후 정수로 다룬다. 가격 표시는 스토어의 localized price를 사용하며 Backend가 원화 문자열을 조립하지 않는다.

`PurchaseResult.status`: `PURCHASED`, `PENDING`, `CANCELED`, `VERIFICATION_PENDING`, `FAILED`. `PURCHASED`라도 UI는 서버 entitlement snapshot으로만 지급을 표시한다. `fulfillmentStatus`: `NOT_GRANTED`, `GRANTED`, `ALREADY_GRANTED`; `finalizationStatus`: `NOT_REQUIRED`, `PENDING`, `FINALIZED`. Google/Apple 스토어 거래·서버 지급·스토어 완료 처리라는 세 상태를 한 boolean으로 합치지 않는다.

### 5.3 이벤트

`AuthStateChanged`, `PurchaseUpdated`, `EntitlementsChanged`, `PushTokenChanged`(fingerprint), `PushReceived`, `PushOpened`, `ConfigurationChanged`, `DiagnosticWarning`을 공통 이벤트로 정의한다. 이벤트는 `eventId`, `type`, `occurredAt`, `sdkSessionId`, `payload`, 가능한 경우 `relatedRequestId`를 가진다.

public Task의 완료는 request ID마다 최대 한 번이다. 그러나 나중에 도착한 스토어 구매 완료는 원래 Task를 두 번째 완료시키지 않고 `PurchaseUpdated` 이벤트와 서버 조회로 반영한다. `Shutdown` 이후 이전 sdkSessionId의 이벤트를 새 세션으로 전달하지 않는다.

### 5.4 오류 코드

`NOT_INITIALIZED`, `ALREADY_INITIALIZED_DIFFERENT_CONFIG`, `INVALID_ARGUMENT`, `UNSUPPORTED_PLATFORM`, `UNSUPPORTED_PROVIDER`, `UNSUPPORTED_OPERATION`, `CONFIG_REQUIRED`, `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED`, `BUSY`, `SESSION_EXPIRED`, `AUTH_FAILED`, `AUTH_REPLAY_DETECTED`, `PRODUCT_NOT_FOUND`, `STORE_UNAVAILABLE`, `PURCHASE_FAILED`, `VERIFICATION_FAILED`, `PURCHASE_ACCOUNT_MISMATCH`, `IDEMPOTENCY_CONFLICT`, `PERMISSION_DENIED`, `MAINTENANCE`, `BRIDGE_PROTOCOL_MISMATCH`, `PAYLOAD_TOO_LARGE`, `INTERNAL_ERROR`를 기본으로 사용한다.

사용자 취소는 예측 가능한 정상 분기다. `PENDING` 거래를 오류로 변환하지 않는다. 재시도 가능한 오류도 구매 UI 재오픈을 자동 수행하지 않는다. 예외의 원문·JWT·영수증·HTTP Authorization을 메시지에 포함하지 않는다.

### 5.5 초기화·동시성

`UNINITIALIZED → INITIALIZING → READY → SHUTTING_DOWN → SHUTDOWN`을 기본으로 한다. 실패 시 재시도 가능한 초기화 상태를 명시한다. 같은 설정의 동시 init은 같은 작업에 합류하고, 다른 설정은 오류다. init 도중 일반 API는 `NOT_INITIALIZED`로 실패한다. Shutdown은 중복 호출 가능하다.

로그인 UI·결제 UI는 각각 동시에 1개만 허용하고 두 UI의 상호 배제도 공통 UI gate로 처리한다. 백그라운드 조회는 계속 가능하다. Mutex/actor/lock을 사용해 read-modify-write를 보호한다. OS UI 호출은 메인스레드, 네트워크/DB는 UI 스레드 밖에서 수행한다.

초기값으로 일반 요청 timeout 30초, 사용자 상호작용 timeout 180초, queue 상한 100, 진단 ring buffer 200개를 둔다. 이는 측정 사실이 아니라 조정 가능한 설계값이다. TIMEOUT/Cancellation은 호출자의 대기 종료이며 이미 시작된 스토어 거래 취소를 뜻하지 않는다. 거래 복구 경로는 살아 있어야 한다.

## 6. Unity ↔ Native Bridge 상세 계약

### 6.1 Envelope

UTF-8 JSON을 사용하고, 외부 공개 API와 내부 wire protocol 버전을 분리한다. 최대 입력 크기는 기본 256 KiB, 초과 시 명시 오류다.

```json
{
  "protocolVersion": 1,
  "sdkSessionId": "uuid",
  "kind": "request",
  "requestId": "uuid",
  "operation": "store.purchase",
  "payload": { "productId": "coins_100" }
}
```

```json
{
  "protocolVersion": 1,
  "sdkSessionId": "uuid",
  "kind": "response",
  "requestId": "same-uuid",
  "operation": "store.purchase",
  "ok": true,
  "result": {
    "attemptId": "uuid",
    "productId": "coins_100",
    "status": "PENDING",
    "serverPurchaseId": null,
    "fulfillmentStatus": "NOT_GRANTED",
    "finalizationStatus": "NOT_REQUIRED",
    "error": null
  },
  "error": null
}
```

이벤트는 `kind=event`, `eventId` 필수, `requestId`는 nullable다. 실패 응답은 `ok=false`, `result=null`, `error` 필수다. 알 수 없는 필드는 호환을 위해 무시하되 필수 필드·type·protocolVersion·길이는 검증한다. operation allowlist 밖의 문자열로 reflection 호출을 하지 않는다.

operation 목록은 `sdk.initialize`, `sdk.status`, `sdk.capabilities`, `auth.signIn`, `auth.signOut`, `auth.restore`, `store.products`, `store.purchase`, `store.entitlements`, `store.sync`, `push.permission`, `push.register`, `push.unregister`, `config.get`, `diagnostics.get`, `sdk.shutdown`다. host 전용 `host.pushToken`, `host.pushReceived`, `host.pushOpened`, `host.lifecycle`은 public 게임 API와 분리한다.

### 6.2 Android

Kotlin `BridgeFacade`에 `attachHost(activity)`, `setCallback(callback)`, `dispatch(json)`, `detachHost()`를 제공한다. C#은 `AndroidJavaClass`/`AndroidJavaObject`로 호출한다. callback은 Kotlin으로 작성한 JVM interface의 `onMessage(String)` 하나이고 C# `AndroidJavaProxy`가 구현한다. Kotlin static 진입에는 필요한 경우 `@JvmStatic`을 사용한다.

BridgeFacade는 Unity 클래스를 import하지 않는다. C#이 Unity current Activity를 얻어 전달하며 SDK는 Activity를 장기 강한 참조로 보관하지 않는다. 기본 SDK는 application context를 사용하고 UI 호출 직전에 유효 Activity를 확인한다. Activity recreation 때 재부착한다.

C# callback proxy는 강한 참조로 보관하고 종료 시 해제한다. Native callback thread에서 Unity 객체에 접근하지 않는다. 문자열을 queue에 넣고 Unity Update dispatcher에서 결과 완료·이벤트를 전달한다. consumer ProGuard/R8 rules와 C# preservation rules를 함께 제공해 release 빌드에서 callback이 제거되지 않게 한다. [S03]

### 6.3 iOS: Swift만으로 export

Swift bridge에 아래 의미의 C ABI 함수를 제공한다. 실제 pointer 타입·int width·calling convention은 C#과 1:1로 맞춘다.

```text
GB_ProtocolVersion() -> Int32
GB_SetCallback(callback: C function pointer?)
GB_Dispatch(bytes: pointer-to-UInt8, length: Int32)
GB_Shutdown()
callback(bytes: pointer-to-UInt8, length: Int32) -> void
```

`@_cdecl` 및 `@convention(c)`를 사용한다. export 함수는 async/Swift String/Swift struct/throwing ABI를 직접 노출하지 않고 내부 Task로 넘긴다. C#은 `DllImport("__Internal")`, static delegate, `AOT.MonoPInvokeCallback`, 적절한 unmanaged calling convention을 쓴다. delegate를 static 참조로 유지한다. [S01][S02]

**메모리 소유권**: C#에서 전달한 bytes는 GB_Dispatch가 반환하기 전에 Swift가 복사한다. Native→C# callback 버퍼는 callback 호출 동안만 유효하며 C#이 즉시 managed byte[]/string으로 복사한다. 포인터를 Unity queue에 저장하지 않는다. 길이를 음수/상한 초과로 받을 때 즉시 거부한다. 반환 String 자동 마샬링 대신 명시적 UTF-8+length를 사용한다. 한글·emoji·null/empty·다중바이트 경계 테스트를 추가한다.

`nm` 등으로 실제 C symbol을 확인하고, **static** XCFramework가 UnityFramework 쪽에 링크되는지 검증한다. dynamic XCFramework를 만들면서 아무 확인 없이 `__Internal`을 쓰지 않는다. Swift runtime link·device/simulator slice·dead stripping 설정을 Xcode build log와 함께 확인한다.

### 6.4 Unity 요청 관리자

request registry는 `requestId → TaskCompletionSource`로 만들고 등록 후 Native를 호출한다. 응답을 받으면 원자적으로 제거한 요청만 완료한다. `RunContinuationsAsynchronously` 사용 가능 여부를 선택 런타임에서 확인한다. 이벤트와 continuation이 Unity 메인스레드에서 안전하게 사용되도록 dispatcher 계약을 문서화한다.

중복 callback, timeout 뒤 늦은 callback, 이전 session callback, 없는 request ID는 예외로 앱을 죽이지 않고 진단 카운터로 기록한다. 비동기 결과가 구매 이벤트인 경우 재조회 흐름은 유지한다. scene 변경 때 dispatcher는 하나만 유지하고 중복 생성하지 않는다. Domain reload 비활성 Editor에서도 static 상태가 초기화되도록 reset hook을 둔다.

모든 public Task는 성공/실패/취소/timeout 중 하나로 종료되어야 한다. 종료 시 pending registry와 event 구독을 해제하고 Native 종료를 호출한다. 네트워크 요청 하나를 취소했다고 전체 SDK를 종료하지 않는다.

## 7. Backend·인증·세션

### 7.1 서버 구성

단일 Spring Boot 애플리케이션에 Spring Web, Validation, Security, JDBC, Flyway, PostgreSQL driver를 사용한다. JPA와 JDBC를 동시에 도입하지 않는다. 기본은 `JdbcTemplate` 또는 선택 버전의 `JdbcClient` + 명시적 SQL이다. HTTP/스토어 검증 중 긴 DB transaction을 유지하지 않는다.

`local-mock`, `sandbox`, `production` 프로필을 나눈다. production 프로필은 방어적 설정 검증용이며 이번 계획에서 public 운영 배포는 하지 않는다. 개발 API·Mock verifier는 local-mock에서만 Bean/route로 등록한다. 시작 시 모든 Provider 설정이 없다고 서버 전체를 종료하지 말고 활성화한 Provider의 필수 설정만 검사한다. 선택 기능이 disabled인지 misconfigured인지 readiness에 구분한다.

### 7.2 Endpoint 계약

| Endpoint | 인증 | 입력·결과 요약 |
|---|---|---|
| GET /health | 없음 | 상세 비밀정보 없는 health |
| POST /v1/auth/challenges | 없음, rate limit | provider/appId → challengeId·nonce·expiresAt |
| POST /v1/auth/exchange | 없음, rate limit | challengeId·provider·idToken·필요 시 authorizationCode → 세션 |
| POST /v1/auth/refresh | refresh token | rotation된 세션 |
| POST /v1/auth/logout | access 또는 refresh | 현재 session 폐기, 재호출 멱등 |
| GET /v1/me | access | 사용자 정보·구매 account binding 정보 |
| GET /v1/catalog | access | 논리 상품·store ID·재화 지급 정의; 실제 가격 권위는 스토어 |
| POST /v1/purchases/verify | access + Idempotency-Key | platform·productId·purchaseToken 또는 signedTransaction·attemptId |
| GET /v1/purchases/{id} | access, 소유권 | 현재 검증/지급/완료처리 상태 |
| GET /v1/entitlements | access | 코인·premium·revision |
| PUT /v1/devices/{installationId}/push-token | access | provider·platform·token·appId·environment |
| DELETE /v1/devices/{installationId}/push-token | access, 소유권 | 현재 사용자 연결 해제 |
| GET /v1/config | 제한된 공개 읽기 | maintenance/message/revision/TTL |
| POST /v1/dev/auth | local-mock + development key | 고정 test subject로 Mock session |
| POST /v1/dev/push/send | local/sandbox + 별도 admin key + allowlist | 자신의 테스트 설치 대상으로만 전송 |

오류 body는 `code`, `message`, `requestId`, `retryable`를 일관되게 사용한다. 400 입력 오류, 401 인증 없음/만료, 403 소유권 위반, 409 계정/멱등 충돌, 429 제한, 503 일시적 외부 장애를 구분한다. 소유하지 않은 purchase id는 존재 여부 노출을 최소화한다. `Idempotency-Key`는 동일 사용자·작업·요청 body hash에 묶고 다른 body 재사용은 409다.

### 7.3 데이터 모델과 제약

모든 주요 시간은 UTC instant, ID는 UUID, 통화/재화는 부동소수점 금지다. migration은 반복 실행 가능해야 하며 적용된 migration을 덮어쓰지 않는다.

| 테이블 | 핵심 필드·제약 |
|---|---|
| users | id, display_name, created_at |
| auth_identities | user_id, provider, issuer, subject, audience/app scope; UNIQUE(provider, issuer, subject, app_scope) |
| auth_challenges | id, provider, nonce_hash, app_id, expires_at, used_at; 성공 교환 시 원자적 소비 |
| sessions | id, user_id, access_hash, refresh_hash, expires_at, refresh_expires_at, revoked_at, family_id |
| session_refresh_history | consumed_refresh_hash, family_id, consumed_at; 회전 재사용 탐지 |
| products | app_id, logical_id, platform, store_id, type, grant_amount; UNIQUE(app_id, platform, store_id) |
| purchases | id, app_id, environment, platform, proof_key_hash, user_id, product_id, store_state, fulfillment_state, finalization_state, evidence_encrypted, created_at |
| wallet_ledger | id, purchase_id UNIQUE, user_id, delta, reason, created_at |
| entitlements | user_id, product_id, active, source_purchase_id; UNIQUE(user_id, product_id) |
| store_finalization_jobs | purchase_id UNIQUE, action, attempt_count, next_attempt_at, status, last_error |
| idempotency_records | user_id, operation, key, body_hash, purchase_id/response, state; UNIQUE(user_id, operation, key) |
| device_tokens | app_id, environment, platform, installation_id, user_id(nullable), token_encrypted, token_hash, updated_at |

purchase 식별자는 Android purchaseToken, Apple transactionId 기준으로 플랫폼/app/environment와 함께 unique 처리한다. Apple consumable의 서로 다른 거래를 originalTransactionId만으로 합치지 않는다. token 원문은 공개 로그에 남기지 않고, 재시도에 필요하면 서버 측 암호화해서 저장한다. 샘플 암호화 master key는 로컬 환경에서 공급하고 Git 밖에 둔다.

개발용 데이터는 고정 test namespace와 별도 DB를 쓴다. 사용자의 기존 서비스 DB를 재사용하거나 삭제하지 않는다. 테스트 teardown은 테스트가 만든 리소스에만 제한한다.

### 7.4 인증 Provider

Android는 Credential Manager의 Sign in with Google을 사용한다. 서버 client ID·nonce·활성 Activity가 필요하다. UI 취소, 계정 없음, 재인증, 비활성 Activity, 네트워크 오류를 구분한다. ID token은 Backend에만 전달하고 로그/Unity payload에 노출하지 않는다. [S04]

iOS는 AuthenticationServices를 사용한다. controller/delegate/presentation anchor를 인증 동안 유지하고 `@MainActor`에서 표시한다. Apple이 이름/email을 매번 제공한다고 가정하지 않는다. 고유 식별은 검증된 subject다. 앱 복귀/credential revoked 상태를 처리하고 필요 시 서버 세션을 폐기한다.

Backend는 공식/검증된 JWT 라이브러리로 signature·허용 algorithm·issuer·audience·expiration·nonce를 검증한다. JWT payload를 Base64 decode한 것만으로 인증 성공을 만들지 않는다. 공개키 fetch/cache는 timeout을 두고, 키 로테이션 시 재확인하되 검증 실패를 무시하지 않는다. [S05][S06]

`challengeId`는 짧은 TTL(기본 5분), provider와 app에 묶고 한 번만 사용한다. native에는 raw nonce를 공급하고 provider별 요청/claim 변환을 명시적으로 구현한다. Apple/Google에 동일한 nonce hashing 규칙을 임의 적용하지 않는다. 공식 SDK가 기대하는 요청 값과 검증할 claim이 일치하는지를 fixture로 확인한다.

### 7.5 세션의 단순화된 기본안

자체 JWT 발급 체계를 새로 만들지 않고 **고엔트로피 opaque access/refresh token + DB hash**로 구현한다. 서버가 사용자·세션을 조회하는 구조로 범위를 줄인다. 기본 access TTL 15분, refresh TTL 7일은 프로젝트 설계값이며 설정으로 변경한다. 표준 암호난수와 SHA-256 token hash를 사용한다.

refresh는 transaction과 row lock으로 회전시키고 이전 refresh 재사용 시 session family를 폐기한다. Native는 동시에 여러 refresh를 시작하지 않고 single-flight로 합친다. refresh 응답이 유실되어 새 토큰을 받지 못한 경우에는 안전하게 재로그인을 요구한다. 무제한 grace window나 예전 token 자동 부활은 만들지 않는다.

Android는 Android Keystore 기반 키로 민감정보를 암호화해 app-private storage에 저장한다. 새로 deprecated 저장 API를 도입하기 전에 상태를 확인한다. iOS는 Keychain을 사용하고 device-only 정책을 기본으로 검토한다. Unity PlayerPrefs에 토큰을 넣지 않는다. 로그아웃 시 로컬 토큰·진단의 민감정보·푸시 사용자 연결을 해제한다. 네트워크가 없으면 로컬 로그아웃은 우선 완료하되 서버 revoke 실패와 보류 상태를 표시한다.

## 8. 결제·검증·지급·복구

### 8.1 절대로 깨지면 안 되는 불변식

1. **서버가 검증한 PURCHASED 거래만 지급한다.** PENDING·취소·검증 실패는 지급하지 않는다.
2. 같은 플랫폼 거래는 여러 callback/동시 HTTP 요청/프로세스 재시작에도 최대 한 번 지급한다.
3. 지급 기록·원장·entitlement 변경은 하나의 DB transaction에서 원자적으로 반영한다.
4. 스토어 완료 처리는 지급 commit 이후다. 완료 처리 실패가 재지급을 유발하지 않는다.
5. 거래 소유권은 검증된 구매 account binding 및 최초 서버 사용자와 일치해야 한다. 다른 계정에 재사용하면 거부한다.
6. 사용자의 Task 취소나 timeout은 결제 취소 보장이 아니다. 앱 재실행에서 미완료 거래를 복구한다.
7. 실제 모드의 실패를 Fake success로 대체하지 않는다. [S07][S08]

### 8.2 Android Play Billing

product 조회, BillingClient 연결·재연결, launchBillingFlow, 구매 callback, queryPurchasesAsync 기반 복구를 구현한다. 항상 현재 store ProductDetails로 결제를 시작하고 논리 ID와 store ID를 검증한다. 초기 범위는 one-time product 두 개, 수량 1이다.

purchase 전에 로그인된 사용자에 대한 서버 발급 account binding 값을 `obfuscatedAccountId`로 전달한다. raw email/user name을 넣지 않는다. Backend가 검증 응답의 account binding을 일치 검사한다. 로그인 사용자가 도중 바뀌어도 거래를 새 사용자에게 붙이지 않는다.

PENDING은 저장/표시하되 검증·지급하지 않는다. PURCHASED가 확인되면 token을 서버에 전송하고 반환된 entitlement snapshot을 읽는다. 기존 소유 비소모성/서비스 단절/취소/상품 없음/중복 클릭을 분기한다.

**Google acknowledge/consume의 주체는 Backend 하나로 고정**한다. SDK 클라이언트에서 서버와 동시에 consume하지 않는다. 서버 지급 commit 뒤 consumable은 consume, non-consumable은 acknowledge한다. 선택한 Developer API의 실제 상태와 응답을 사용한다. 이미 처리됐다는 응답은 저장된 지급 상태 및 스토어 재확인을 근거로 멱등하게 정리한다. [S07][S08]

### 8.3 iOS StoreKit 2

Product 조회, purchase 결과(success verified/unverified, pending, userCancelled), `Transaction.updates` 수신, unfinished/current entitlements 조회, 사용자 복원을 구현한다. transaction listener는 초기화 시 하나만 만들고 종료 시 취소한다. raw transaction proof는 서버에만 보낸다.

purchase 옵션에 서버 user에 대응하는 `appAccountToken` UUID를 넣고 Backend 검증과 일치시킨다. 클라이언트 StoreKit verification 성공과 Backend 지급 성공을 구분한다. 신뢰할 수 없는 거래를 finish하거나 지급하지 않는다.

Backend가 지급을 durable하게 완료한 응답을 받은 뒤 해당 transaction의 `finish()`를 호출한다. 응답 유실/앱 종료로 finish되지 않으면 다음 실행에서 검증을 재요청하고 ALREADY_GRANTED를 받은 뒤 finish한다. 비소모성 복원과 소모성 서버 잔액 복원을 혼동하지 않는다. 과거 consumable 잔액의 권위는 서버 원장이다. [S09][S10]

### 8.4 검증 Provider와 로컬 환경 구분

Backend interface: `PurchaseVerifier.verify(proof, expectedApp, expectedUserBinding) → VerifiedPurchase`. Fake verifier, Google verifier, Apple verifier를 분리한다. verify 결과는 store transaction key, product ID, quantity, state, account binding, app/environment, revocation 정보 등을 포함한다.

Google verifier는 서버 자격증명으로 Play Developer API를 호출하며 token·package·product·구매상태·소유권을 확인한다. orderId를 멱등키로 사용하지 않는다. Apple verifier는 공식 App Store Server Java Library의 서명 검증/Server API를 활용하고 app/environment·bundle/product·transaction·account binding·revocation을 검사한다. 온라인 조회가 필요한 경로와 로컬 JWS 검증 경로를 구분한다. [S07][S11]

Xcode `.storekit` 거래는 실제 App Store가 서명한 거래와 다르다. 따라서 실제 Apple Server API 검증 성공으로 기록하지 않는다. 로컬 StoreKit 시험은 **명시적인 XCODE_STOREKIT development 경로**로만 매핑하고 서버의 local-mock 데이터와 분리된 namespace에서 지급 흐름을 확인한다. sandbox/production에서는 이 증빙을 무조건 거부한다. 로컬 JWS 검증이 구현되지 않았다면 “StoreKit 로컬 client 검증 + fake 서버 지급”이라고 정확히 적는다. [S12]

### 8.5 서버 처리 순서

```text
입력/세션 검증 → idempotency key 기존 처리 확인
→ 서버가 Provider로 proof 검증 (DB transaction 밖)
→ 검증된 거래 key와 account binding 확인
→ DB transaction 시작
  1) purchases unique key로 기존 거래 조회/insert
  2) 기존 user가 다르면 충돌; 이미 지급됐으면 재지급 없음
  3) 신규 거래이면 wallet_ledger UNIQUE(purchase_id) 또는 entitlement upsert
  4) fulfillment=GRANTED 및 revision 갱신
  5) Google finalization job 생성; Apple은 client finish 대기 상태
  6) idempotency 결과 기록
→ commit
→ Google finalization 시도 또는 worker에 위임
→ entitlement와 처리 상태 반환
```

동시 insert unique 충돌을 transaction 전체 실패로 방치하지 않는다. PostgreSQL `INSERT ... ON CONFLICT` 또는 충돌 후 새 transaction 조회로 재진입해 기존 결과를 읽는다. wallet balance는 원장 합계 또는 잠금/원자 update된 별도 balance로 일관되게 계산한다. 초기 범위는 원장 합계가 단순하다.

finalization worker는 같은 PostgreSQL의 작업 테이블을 사용한다. retry count/next_attempt_at/last_error를 두고 백오프한다. 별도 Kafka/Redis를 도입하지 않는다. 검증 API가 외부 네트워크 때문에 실패하면 `VERIFICATION_PENDING`으로 남기고 클라이언트가 재시도할 수 있게 한다. purchase/fulfillment/finalization 상태를 진단에서 추적한다.

### 8.6 복구·제한사항

앱 시작/복귀/사용자 복원에서 진행 중 거래를 확인한다. 복구 작업은 single-flight이며 과도한 조회를 막는다. Native 저장소에 attemptId·product·사용자 binding·필요한 재확인 단서를 저장하되 token 원문을 평문으로 저장하지 않는다.

스토어에서 이미 consume/finish된 거래를 클라이언트가 다시 조회할 수 있다고 가정하지 않는다. 서버 지급이 완료됐다면 `GET /entitlements`로 복구한다. 로그인 계정을 바꾸면 과거 거래를 새 계정에 귀속시키지 않는다.

환불/취소 서버 알림·Google RTDN·Apple Server Notifications 운영은 이번 실행에서 제외한다. `current entitlements`나 검증 응답에서 관측한 revoked 상태는 반영하되 모든 환불을 자동 추적한다고 주장하지 않는다. 자동 refund API 호출도 하지 않는다. 이 제한은 SECURITY/FINAL_REPORT에 반드시 적는다.

## 9. 푸시·Host 통합·점검 모드

### 9.1 Android FCM

Firebase configuration은 Host가 소유한다. SDK가 기존 FirebaseApp을 재초기화하거나 host 설정을 덮어쓰지 않는다. 샘플은 config가 있으면 실제 adapter를 조립하고, 없으면 명시적 mock 모드로 빌드한다. google-services plugin 적용과 처리 task가 config 없는 mock build를 깨지 않게 분기한다.

기본은 explicit `registerPush` 후에만 등록하고 초기화 시 권한 dialog를 자동 표시하지 않는다. Android 알림 권한, channel, foreground, background notification 클릭을 처리한다. FCM callback `onNewToken`/`onMessageReceived`를 SDK로 전달하는 host forwarding API를 제공한다. 샘플용 service 구현을 제공하되 기존 host service와 충돌하지 않도록 문서화한다. token 갱신·사용자 변경·로그아웃 후 연결 제거를 구현한다. [S13]

### 9.2 Swift SDK의 APNs host 계약

Swift SDK는 `UNUserNotificationCenter` 권한 조회/요청과 payload 정규화·등록 API를 제공한다. Host의 AppDelegate/NotificationCenter delegate를 몰래 교체하거나 method swizzling하지 않는다. Host가 `didRegisterForRemoteNotifications`, 등록 실패, 수신/응답 callback을 SDK에 전달한다. 샘플 SwiftUI 앱은 `UIApplicationDelegateAdaptor`로 연결한다.

APNs token은 매 launch에 시스템에서 얻어 서버로 전달한다. 오래 저장한 token을 현재 유효 token이라고 가정하지 않는다. notification display permission과 APNs registration 상태를 하나의 boolean으로 합치지 않는다. 동의 상태를 존중하며 보이는 알림의 권한 거부와 네트워크 등록 실패를 구분한다. [S14]

### 9.3 Unity iOS에서 Swift-only 제약을 유지하는 방법

C ABI만으로는 Unity Host의 AppDelegate callback이 자동으로 Swift SDK에 전달되지 않는다. 이 연결을 빠뜨리지 않는다. **기본 선택은 Unity 공식 Mobile Notifications 패키지의 C# host adapter**다. 선택한 package 버전의 APNs registration/device token/remote received/last responded API를 사용해 C#에서 host 이벤트를 받고 Swift Bridge의 host 전용 operation으로 전달한다. [S15]

이 adapter는 `UNITY_IOS`에서만 동작하고 Native Swift sample에는 필요 없다. Native SDK의 서버 등록·이벤트 정규화 로직을 재사용한다. 공식 패키지 내부 Native 코드 사용과 우리가 Objective-C/C++를 새로 작성하는 것은 다르다. 새로운 Unity Swift project type이나 임의 UnityAppController subclass를 필수 조건으로 만들지 않는다.

SDK와 Unity notification 패키지가 같은 권한 dialog/remote registration을 중복 요청하지 않도록 **host-managed push 모드**를 정한다. Unity에서만 host가 OS registration을 소유하고 SDK는 전달받은 token/event를 처리한다. Native sample에서는 Swift SDK와 AppDelegate forwarding이 소유한다. 전경 수신 이벤트 구독이 알림 표시 방식에 미치는 영향은 선택 package 문서를 확인해 명시한다.

### 9.4 백엔드 전송과 토큰 저장

Android FCM은 Firebase Admin Java SDK, iOS APNs는 검증된 HTTP/2 client/JDK HttpClient와 토큰 기반 인증으로 구현한다. JWT 서명은 검증된 라이브러리를 사용하고 .p8는 서버에만 둔다. APNs의 sandbox/production endpoint, topic(bundle ID), token type을 구분한다. FCM token과 APNs token을 같은 provider로 저장하지 않는다. [S16][S17]

잘못되거나 폐기된 token 응답은 비활성화하고, 429/일시 장애는 제한된 재시도·백오프를 적용한다. 개발용 전송 API는 별도 admin key·development/sandbox 프로필·자신의 등록된 테스트 설치 allowlist로 제한한다. URL/대상 token을 임의 주입해서 외부 발송할 수 없게 한다. 요청 body 제한과 rate limit을 둔다.

push 클릭 payload는 `messageId`, `route`, `campaignId` 정도의 허용 목록만 소비한다. 허용 route는 `home`, `store`. arbitrary URL 실행·스크립트 실행·임의 scene 이름 로딩은 금지한다. 콜드스타트에서는 SDK READY까지 큐에 보관하고 messageId 기준 중복 제거 후 한 번 전달한다. notification 전달은 OS/네트워크 영향을 받으므로 반드시 전달된다고 보장하지 않는다.

### 9.5 진단·설정

진단에는 sdkVersion, protocolVersion, platform, mode, active provider, requestId, duration, error code, pending count, late/duplicate callback count, 최근 정제 이벤트가 포함된다. 원본 토큰·영수증·Authorization·개인정보는 제외한다. ring buffer 200개, export 상한과 redaction을 적용한다. 메인스레드에서 대량 disk write를 하지 않는다.

GET /config는 maintenance 플래그·message·revision·TTL을 제공한다. 정상 cache가 있으면 offline에서도 사용하고, 없으면 safe default를 사용한다. 점검 모드에서 새 purchase 시작을 막되, **이미 진행된 거래 검증/지급/복구·로그아웃은 막지 않는다.** 원격 코드를 실행하는 기능으로 확대하지 않는다.

## 10. 배포·패키징·소비자 검증

### 10.1 Android: AAR만 복사해서 끝내지 않는다

AAR 직접 파일에는 전이 의존성을 자동 해결하는 Maven metadata가 함께 전달되지 않는다. `sdk-core`, `sdk-android`, `sdk-unity-bridge`를 **Maven publication + POM**으로 `artifacts/maven-repo`에 발행한다. Kotlin stdlib, coroutines, serialization, Credential Manager, Billing, Firebase 등의 의존성이 소비자 build에서 해결되는지 확인한다. 임의 fat AAR로 제3자 라이브러리를 전부 재포장하지 않는다. [S18]

Unity 개발 소비 경로는 exported Gradle project에 local Maven repository와 gamebridge coordinate를 추가하는 **멱등 build hook**이다. 사용자의 기존 repositories/dependencies를 덮어쓰지 말고 표식 블록을 넣고 두 번 적용해도 중복되지 않게 한다. repository 경로를 개발자 Mac 절대 경로로 고정하지 않는다. release staging에는 repo를 동봉해 상대 경로로 참조하게 한다.

consumer ProGuard rules, manifest merger, minSdk 충돌, AndroidX/Kotlin metadata, duplicate class를 검증한다. SDK library manifest에 앱 label/icon/launcher Activity를 넣지 않는다. sample의 exported/service/permission 설정을 SDK에 무조건 전파하지 않는다.

### 10.2 iOS: source와 binary 두 경로

Swift Package source 소비를 지원하고, Unity용 **static GameBridge XCFramework**를 생성한다. device arm64와 사용 가능한 simulator slice를 archive해 bundle로 묶는다. source-only의 존재를 XCFramework 생성 성공으로 기록하지 않는다. [S19]

프레임워크 target은 필요한 Core/Apple/UnityBridge 구현이 링크되는지 확인한다. `SKIP_INSTALL=NO`, distribution/library evolution 등 설정은 선택 toolchain에서 적합성을 확인한다. 코드 서명 없는 simulator build와 device generic archive 가능한 범위를 활용하되 실제 device 실행은 별도다. third-party 의존성과 리소스/PrivacyInfo.xcprivacy가 필요한지 조사하고 README에 명시한다. 근거 없이 개인정보 미수집 선언을 생성하지 않는다.

Unity postprocess hook으로 UnityFramework target의 link flags/framework search paths/Swift settings를 멱등하게 적용한다. `Unity-iPhone` target에만 추가하고 끝내지 않는다. exported project regeneration 후에도 동작해야 한다.

### 10.3 UPM 패키지

`com.gamebridge.sdk`의 package.json, runtime/editor/test asmdef, platform include constraints, stable .meta GUID, Samples~, README, CHANGELOG를 포함한다. 기본 Runtime에서 `UnityEditor`를 참조하지 않는다. Android/iOS/Editor 조건부 컴파일을 사용해 다른 플랫폼에서 native import가 실행되지 않게 한다.

개발 시 local UPM path + 로컬 native artifact bootstrap을 사용한다. 배포 가능한 zip/tgz는 필요한 자체 Native 산출물·Maven metadata·의존성 설명·checksum을 포함한다. 서드파티 대형 바이너리·private key·빌드 캐시를 Git에 넣지 않는다.

**Git URL 설치만으로 Native 바이너리가 저절로 생기지 않는다.** 소스 저장소 URL 소비를 제공하면 사전 artifact build/설치 단계가 필요함을 명시한다. 바이너리 완결 패키지는 별도 staging 산출물이다. 테스트하지 않은 원격 Git URL·Release 링크를 README에 실제 설치 가능 링크처럼 쓰지 않는다. [S20]

### 10.4 새 소비자 프로젝트

기존 Demo가 SDK 소스를 직접 참조해 우연히 성공한 것인지 확인하기 위해 독립된 disposable consumer를 생성한다. Android는 Maven coordinate, iOS는 source package와 binary 경로, Unity는 staging UPM으로 소비한다. 로컬 빌드 성공과 실행 성공을 별도로 기록한다.

Unity consumer는 clean import → mock demo → Android export/build → iOS export/build 순으로 가능한 범위를 검증한다. signing/license/device 부족은 DEFERRED_ENV/WAITING_USER다. 패키지에 필요한 파일이 누락돼 빌드 실패한 것은 환경 탓이 아니라 내부 버그다.

## 11. 샘플 앱의 구체적 동작

UI는 기능 검증용이며 게임 콘텐츠를 만들지 않는다. Android Compose·iOS SwiftUI·Unity UI에서 같은 화면 구조를 유지한다.

| 화면/영역 | 요소·동작 |
|---|---|
| 상단 상태 | SDK/bridge 버전, 모드, 플랫폼, Provider configured 여부, 로그인 사용자 |
| 초기화 | Initialize, Shutdown, 진단 export; 미초기화 버튼의 명시 오류 |
| 인증 | Google/Apple 또는 Mock 로그인, 로그아웃, 세션 복원 |
| 상점 | 상품 두 개, store localized price, 구매, 진행/보류/검증대기/실패 표시 |
| 내 재화 | 서버 코인 잔액, premium 상태, refresh, 사용자 복원 |
| 알림 | 권한, 등록 상태, 테스트 수신/클릭 기록, token fingerprint |
| 설정 | 점검 모드 조회, 캐시 출처, config revision |
| 진단 | requestId/error, 최근 이벤트, 중복 callback 카운터; 원문 비밀정보 없음 |

로그인 없이 구매하면 로그인 필요를 표시한다. 구매 버튼 중복 클릭은 UI 및 SDK에서 방어한다. background→foreground 뒤 세션/거래/토큰 상태를 재확인한다. scene 전환은 데모에서 2개 scene 또는 동일 수준의 화면 이동으로 재현한다. 여러 비동기 결과가 도착해도 해제된 화면을 업데이트하지 않는다.

Editor Offline은 배너로 Fake임을 명확히 표시한다. LOCAL_MOCK은 서버/DB를 통과하는 통합 데모다. 이 둘을 같은 “실연동”으로 표현하지 않는다. 실서비스 config가 없을 때 unavailable 표시만 하고 나머지 mock 기능은 사용 가능하게 한다.


## 12. 순차 실행 Task 명세

총 **64개 Task**, 12개 Phase다. 아래 작업은 전부 자동 개발 대상이며, 외부 계정이 필요한 실연동 확인만 사용자에게 넘긴다. 의존 Task의 코드가 작성되었지만 실연동이 대기인 경우 Mock/계약을 사용해 후속 코드 개발을 계속한다. 내부 contract 자체가 미정이거나 깨져 있으면 DEP 블로커를 기록하고 독립 작업부터 진행한다.

각 Task의 공통 마지막 행동은 **원장·작업 로그 갱신 → diff 검토 → Task ID를 포함한 로컬 커밋 → 다음 Task**다. 다음 Phase 승인을 요청하지 않는다. 아래 검증은 최소 기준이며 P09 전에는 대형 하네스보다 실제 기능 연결을 우선한다.

### P00 — 준비·환경·진행 기록

#### P00-T01 — 저장소 보존·작업 원장 초기화

- 의존: 없음. 참조: 0~2장.
- 구현: 기존 git status/branch/history와 파일을 조사한다. 기존 사용자 변경을 별도로 기록하고 덮어쓰지 않는다. 현재 저장소에서 작업하거나 깨끗한 경우에만 전용 로컬 브랜치를 만든다. 빈 저장소라면 git init은 가능하지만 remote·push는 만들지 않는다. 제공된 PROGRESS/WORK_LOG 양식을 보존하고 세션 시작 정보를 기록한다. 기존 AGENTS가 있으면 충돌을 분석해 병합한다.
- 완료 확인: 현재 디렉터리와 실제 Git root가 일치하고 기존 파일이 보존됐는지 확인한다. 모든 계획 Task ID가 진행 원장에 한 번씩 존재해야 한다. Git identity가 없으면 USER-GIT에 기록하고 이후 코드 개발을 계속한다.
- 산출물: `AGENTS.md, docs/PROGRESS.md, docs/WORK_LOG.md, docs/DECISIONS.md`.

#### P00-T02 — 도구·라이선스·버전 조합 확정

- 의존: P00-T01. 참조: 3장.
- 구현: java -version, xcodebuild -version, swift --version, adb version, docker version, docker compose version, 설치된 Unity 경로/ProjectVersion, Android SDK·Gradle 호환성을 조사한다. 현재 설치된 안정 조합을 우선하고 정확한 dependency 버전을 선택한다. 설치하지 않은 도구를 설치됐다고 기록하지 않는다. 사용자 소유 외부 계정이나 저장된 비밀키를 무단 탐색하지 않는다.
- 완료 확인: TOOLCHAIN에 실제 버전/출처/확인 명령이 있고 ENVIRONMENT에 가능·불가 검증이 구분되어 있어야 한다. 버전 미확정 항목은 이유와 후속 Task를 남긴다. 라이선스/로그인이 필요한 도구는 대기로 분류한다.
- 산출물: `docs/TOOLCHAIN.md, docs/ENVIRONMENT.md, docs/USER_SETUP.md`.

#### P00-T03 — 빌드 가능한 최소 프로젝트 구성

- 의존: P00-T02. 참조: 2~4장.
- 구현: Android/Backend 독립 Gradle wrapper, Kotlin source sets, iOS Package와 Xcode sample/framework target, Unity package·Demo 기본 프로젝트, Compose/PostgreSQL 구성을 만든다. Unity .meta는 가능한 경우 Editor로 생성하고 안정 GUID를 유지한다. 자체 로직이 없는 feature를 빈 성공 구현으로 등록하지 않는다. placeholder package/bundle ID와 VERSION=0.1.0-dev를 사용한다.
- 완료 확인: 가능한 도구에서 빈 앱/라이브러리/Backend 기본 빌드를 실행한다. 실제 원격 wrapper 다운로드가 막히면 문제를 기록하고 가짜 wrapper JAR를 만들지 않는다. Unity 프로젝트가 없으면 생성 script를 제공하고 미실행 상태로 남긴다.
- 산출물: `android/, ios/, unity/, backend/, infra/compose.yaml, VERSION, .gitignore`.

#### P00-T04 — 진행 문서 검사·기본 명령 진입점

- 의존: P00-T03. 참조: 2.3장, 13장.
- 구현: Python 표준 라이브러리로 verify-progress.py를 작성한다. 계획 Task ID/원장 행/상태값/증거·설정 참조의 일관성만 검사한다. doctor.sh와 Makefile, 각 플랫폼 build script의 실제 호출 경로를 만든다. 아직 없는 기능 검증은 NOT_IMPLEMENTED로 실패/대기 처리하며 echo PASS를 쓰지 않는다.
- 완료 확인: 정상 원장은 통과하고 Task 행 누락·증거 없는 PASS·잘못된 상태는 임시 복사본에서 실패해야 한다. 원본 문서를 망가뜨린 채 남기지 않는다. 도구 부재와 명령 실패의 종료 코드가 구분되는지 확인한다.
- 산출물: `scripts/verify-progress.py, scripts/doctor.sh, scripts/build-*.sh, Makefile`.

#### P00-T05 — 모드·비밀정보·설정 격리

- 의존: P00-T03. 참조: 3.2~3.4장.
- 구현: EDITOR_OFFLINE/LOCAL_MOCK/XCODE_STOREKIT/PLATFORM_SANDBOX 설정과 예제 파일을 만든다. .env.local, 실키, provisioning, 실제 google-services 설정, build artifacts를 ignore한다. mock build는 실키 없이 선택 가능하도록 한다. production/sandbox에서 development profile을 묵시적으로 활성화하지 않는다.
- 완료 확인: 설정이 전혀 없어도 명시적 mock 앱/서버 빌드가 가능해야 한다. real provider 선택 시 누락 key 이름이 CONFIG_REQUIRED로 나타나고 mock으로 fallback하지 않아야 한다. git diff에 비밀값이 없는지 확인한다.
- 산출물: `config/*.example.*, .gitignore, 각 플랫폼 config loader, backend profile config`.

### P01 — 공통 계약·Core·Fake

#### P01-T01 — 공통 모델·오류·상태 schema

- 의존: P00-T05. 참조: 5장.
- 구현: public-api.md, models schema, error-code registry를 작성하고 Kotlin/Swift/C# DTO를 수동 구현한다. 실제 모델은 계약의 단일 의미를 유지하고 nullable·64-bit 문자열·enum unknown 처리·timestamp 규칙을 정한다. 언어 간 codegen framework를 만들지 않는다.
- 완료 확인: 동일 JSON fixture의 product/purchase/error/profile을 각 가능한 언어에서 decode/encode한다. 한글·emoji·null·큰 정수 문자열이 보존돼야 한다. 필수 필드 누락을 성공으로 해석하지 않는다.
- 산출물: `contracts/models.schema.json, contracts/error-codes.json, contracts/public-api.md, 각 플랫폼 DTO`.

#### P01-T02 — Bridge wire protocol·공용 fixture

- 의존: P01-T01. 참조: 6.1장.
- 구현: request/response/event schema와 operation allowlist를 확정한다. 성공/실패/pending/unsupported/구버전/잘못된 길이 fixture를 작성한다. requestId·sdkSessionId·eventId를 분리한다. 외부 URL이나 operation 문자열을 reflection target으로 사용하지 않는다.
- 완료 확인: schema validation과 최소 parser smoke로 정상/비정상 fixture를 구분한다. ok=false인데 error가 없거나 requestId가 다른 결과는 거부/격리해야 한다.
- 산출물: `contracts/bridge.schema.json, contracts/fixtures/bridge/, BridgeEnvelope DTO`.

#### P01-T03 — SDK 상태기계·Provider interface

- 의존: P01-T01, P01-T02. 참조: 4장, 5.5장.
- 구현: Kotlin/Swift core와 C# facade에 초기화/종료/동일 설정 재초기화 상태를 구현한다. Auth/Store/Push/Transport/Storage/Clock interface를 만든다. 필요한 concrete 조립 지점만 Factory로 두고 framework를 만들지 않는다. capability의 supported/configured/mode를 구분한다.
- 완료 확인: 초기화 전 API 오류, 동일 설정 중복 init, 다른 설정 init 거부, shutdown 중복, shutdown 후 새 초기화에 대해 가능한 최소 smoke를 수행한다. 상호 배제 상태가 데이터 race로 깨지지 않는지 코드와 실행으로 확인한다.
- 산출물: `SDK Core state machine, Provider interfaces, configuration factory`.

#### P01-T04 — 결정적인 Fake Provider

- 의존: P01-T03. 참조: 3.2장, 5장.
- 구현: Kotlin/Swift/C# FakeAuth/FakeStore/FakePush를 구현한다. success/cancel/pending/network fail/duplicate/late 결과를 명시 scenario로 선택한다. 임의 확률로 실패하지 않게 고정 seed/clock을 제공한다. Fake transaction에 mock: namespace를 붙이고 real provider와 타입·조립을 분리한다.
- 완료 확인: 계정/스토어 없이 login→products→purchase→entitlement→push event 흐름이 실행되어야 한다. 같은 Fake transaction을 재처리해도 재지급되지 않는 최소 동작을 확인한다. 표시된 모드는 반드시 Fake다.
- 산출물: `android/sdk-testing/, ios/Sources/GameBridgeTesting/, Unity Editor Fake adapters`.

#### P01-T05 — Native HTTP·저장소·세션 소유권 기반

- 의존: P01-T03. 참조: 4장, 7.5장.
- 구현: Native에 Backend client와 secure storage interface/구현을 추가한다. Android Keystore·iOS Keychain을 사용하고 Editor는 test-only memory/file storage를 사용한다. 공통 timeout·error mapping·requestId·token redaction을 구현한다. Unity Native 경로에서는 C#이 토큰을 저장하거나 갱신하지 않는다.
- 완료 확인: mock transport로 200/401/timeout/invalid JSON을 확인한다. 샘플 로컬 storage에 token 평문이 없는지 확인한다. 개발 HTTP 예외는 debug/local로만 제한하고 TLS 검증을 비활성화하지 않는다.
- 산출물: `Native BackendClient, SecureTokenStore, SessionStore, EditorBackendClient`.

### P02 — Backend 로컬 통합

#### P02-T01 — Backend·PostgreSQL·migration 기동

- 의존: P00-T03, P01-T01. 참조: 7.1~7.3장.
- 구현: Flyway 초기 migration과 schema를 구현한다. local-mock DB·health endpoint·requestId filter·입력 검증·공통 error handler를 만든다. 운영 DB나 기본 공개 포트로 임의 연결하지 않는다. Docker volume과 테스트 DB의 수명 정책을 문서화한다.
- 완료 확인: 로컬 compose 기동, migration, health, 두 번째 시작 시 migration idempotency를 확인한다. PostgreSQL이 없으면 실행 대기로 기록하며 H2 통과로 대체하지 않는다.
- 산출물: `backend server bootstrap, db/migration, infra/compose.yaml, scripts/run-demo-backend.sh`.

#### P02-T02 — Mock 사용자·opaque 세션·갱신

- 의존: P02-T01, P01-T05. 참조: 7.2~7.5장.
- 구현: 개발 전용 auth endpoint와 opaque access/refresh 발급·hash 저장·만료·rotation·logout을 구현한다. 기본 사용자 A/B를 고정 subject로 구분한다. Spring Security filter에서 세션을 확인하고 개발 endpoint는 local-mock에만 등록한다.
- 완료 확인: curl/script로 login→me→refresh→old-refresh 재사용 거부→logout을 실행한다. 두 사용자 데이터가 섞이지 않아야 한다. sandbox 프로필에서 dev/auth가 404 또는 명시 차단인지 확인한다.
- 산출물: `backend/auth, backend/session, security config, dev auth seed`.

#### P02-T03 — 상품·재화·구매 원장 서비스

- 의존: P02-T02. 참조: 7.3장, 8.1~8.5장.
- 구현: 두 논리 상품의 store mapping과 catalog/entitlements API를 구현한다. Mock verifier로 검증된 거래를 구매 서비스에 전달하고 원장·premium 변경을 transaction으로 처리한다. client price/userId/amount를 지급 근거로 쓰지 않는다.
- 완료 확인: 같은 거래를 두 번 검증 요청해 coin 100만 지급되는지 확인한다. 다른 사용자 재전송은 409이고 원장 변화가 없어야 한다. premium 재요청도 한 entitlement로 유지돼야 한다.
- 산출물: `backend/catalog, backend/purchase, backend/wallet, migration/seed`.

#### P02-T04 — purchase 재시도·finalization queue

- 의존: P02-T03. 참조: 8.5장.
- 구현: idempotency records와 finalization job worker를 구현한다. 외부 호출은 DB transaction 밖에서 수행한다. Fake finalizer가 실패 후 성공하도록 만들어 durable retry를 구현한다. 입력 Idempotency-Key와 provider transaction unique 제약을 둘 다 사용한다.
- 완료 확인: 동일 key+다른 body 거부, 서로 다른 key+같은 거래의 한 번 지급, worker 재시작 후 처리 재개, 이미 지급된 거래의 finalization 재시도에서 원장 불변을 확인한다.
- 산출물: `IdempotencyService, PurchaseFinalizationWorker, finalization tables`.

#### P02-T05 — device token·config·개발 푸시 API

- 의존: P02-T02. 참조: 9장.
- 구현: installation/provider/app/environment별 token upsert와 소유권 해제, local push sender, config 조회 API를 만든다. 원문 token은 마스킹/암호화하고 다른 사용자가 임의 installation을 해제하지 못하게 한다. 개발 send API에 별도 key와 allowlist를 둔다.
- 완료 확인: token 회전과 로그아웃 연결 해제, 다른 사용자 삭제 거부, unauthenticated send 거부, config cache metadata를 확인한다. 네트워크로 실제 외부 푸시는 보내지 않는다.
- 산출물: `backend/push, backend/config, dev push sender`.

#### P02-T06 — 로컬 Backend 통합 smoke 명령

- 의존: P02-T03, P02-T04, P02-T05. 참조: 13장.
- 구현: scripts/smoke-local.sh 또는 표준 라이브러리 Python helper로 사용자 A/B·상품·중복 구매·세션·token·config 시나리오를 자동 실행한다. 실행마다 고유 test namespace를 사용하고 결과 요약을 남긴다. P09처럼 범용 하네스를 만들지 않고 핵심 흐름만 확인한다.
- 완료 확인: 서버·DB를 통과한 명령의 exit code와 실제 assert 수를 기록한다. 틀린 기대 잔액을 임시로 주면 실패해야 한다. 서버가 없다고 PASS하지 않는다.
- 산출물: `scripts/smoke-local.sh, 정제된 backend smoke evidence`.

### P03 — Native·Unity Bridge 수직 연결

#### P03-T01 — Kotlin SDK의 LOCAL_MOCK 수직 연결

- 의존: P01-T04, P01-T05, P02-T06. 참조: 4~8장, 11장.
- 구현: Kotlin Core에 Fake provider와 실제 Backend transport를 조립한다. Compose sample에서 초기화·Mock 로그인·상품·구매·잔액을 SDK public API로만 사용한다. localhost/device 주소 차이는 config로 해결하고 global cleartext 설정을 넣지 않는다.
- 완료 확인: Android sample mock build, 가능한 emulator/device에서 localhost backend를 통한 한 흐름을 확인한다. 실행이 불가하면 빌드와 runtime을 구분한다. UI가 DB 금액 대신 자체 카운터를 더하지 않아야 한다.
- 산출물: `android/sdk-android, sample-app, sample debug network config`.

#### P03-T02 — Swift SDK의 LOCAL_MOCK 수직 연결

- 의존: P01-T04, P01-T05, P02-T06. 참조: 4~8장, 11장.
- 구현: Swift Core/Apple module 조립과 SwiftUI sample을 구현한다. Keychain과 async/await를 연결한다. ViewModel의 main-actor 경계를 정하고 server transport를 사용한다. sample AppDelegate를 명시적으로 유지한다.
- 완료 확인: 지원되는 Xcode에서 simulator build와 가능한 실행을 확인한다. Mock login→purchase→server balance까지 확인하고 저장/재시작 흐름을 기록한다. 순수 Swift package test만으로 UIKit 동작 PASS를 기록하지 않는다.
- 산출물: `ios/Sources/, ios/SampleApp/, scheme/project config`.

#### P03-T03 — Android JNI 왕복 transport

- 의존: P03-T01, P01-T02. 참조: 6.2장.
- 구현: Kotlin BridgeFacade와 callback interface, C# AndroidJavaProxy transport를 구현한다. host Activity attach/detach, string dispatch, strong callback reference, queue, R8 rules를 넣는다. Unity 클래스에 대한 Kotlin compile dependency를 만들지 않는다.
- 완료 확인: Unity Android export/build가 가능하면 sdk.status 및 지연 echo/인증 요청을 왕복한다. 아직 release package 전이면 임시 local Maven 소비로 확인한다. Native standalone 성공만으로 JNI 성공이라고 쓰지 않는다.
- 산출물: `android/sdk-unity-bridge, Unity AndroidTransport, consumer rules`.

#### P03-T04 — Swift C ABI 왕복 transport

- 의존: P03-T02, P01-T02. 참조: 6.3장.
- 구현: Swift @_cdecl 함수와 C callback을 구현한다. C# IntPtr/length wrapper·static AOT delegate·UTF-8 즉시 복사를 만든다. static framework build·nm export 검증·Unity iOS postprocess의 최소 link를 구성한다. 새 Objective-C/C++ 파일을 만들지 않는다.
- 완료 확인: 가능한 Xcode archive와 exported symbol 확인을 수행한다. Unity iOS 빌드가 가능하면 sdk.status 및 한글 callback을 왕복한다. device/simulator/engine 검증 범위를 별도로 기록한다.
- 산출물: `ios/UnityBridge, ios/Framework, Unity iOSTransport, minimal iOS build hook`.

#### P03-T05 — Unity facade·dispatcher·request registry

- 의존: P03-T03, P03-T04. 참조: 5장, 6.4장.
- 구현: public facade, 플랫폼 factory, TaskCompletionSource registry, 메인스레드 queue, 이벤트 구독, cancellation/timeout, singleton lifecycle를 구현한다. Editor에서는 Native 호출 없이 Fake adapter를 사용한다. native transport 구현이 환경 대기여도 C# 코드는 계속 구현한다.
- 완료 확인: Editor mock에서 init→login→purchase→shutdown을 실행하고 duplicate/late callback으로 Task가 두 번 끝나지 않는지 확인한다. scene 전환·Domain Reload 설정에 관계없이 dispatcher가 중복되지 않아야 한다.
- 산출물: `Unity Runtime/Core, Auth, Store, Push, Platforms, asmdef/link.xml`.

#### P03-T06 — Unity 최소 Demo·Native 경로 분기

- 의존: P03-T05. 참조: 11장.
- 구현: 기능 버튼과 상태/오류 표시 UI를 만든다. 고급 게임 art/assets는 도입하지 않는다. API가 SDK facade만 사용하도록 한다. Editor Offline과 Native LOCAL_MOCK 배너를 표시하고 platform support/configuration 상태를 노출한다.
- 완료 확인: Editor에서 사용자가 순서대로 클릭 가능한 최소 scene을 확인한다. Android/iOS native smoke는 가능한 환경에서 실행하고 부재는 대기로 기록한다. UI만 돌아가면 전체 Native 연동 완료라고 쓰지 않는다.
- 산출물: `unity/Demo, Samples~ 기본 예제, 초기 Unity evidence`.

### P04 — 실제 인증 코드와 세션

#### P04-T01 — 실제 Android Google 로그인 adapter

- 의존: P03-T01, P03-T03. 참조: 7.4장.
- 구현: Credential Manager와 Google ID token 결과를 구현한다. nonce challenge, client ID, main Activity, 사용자 취소/계정 없음/중복 UI 호출을 처리한다. 설정 없으면 해당 provider만 CONFIG_REQUIRED다. Mock과 실제 adapter를 동일 codepath에서 구분 없이 섞지 않는다.
- 완료 확인: 실키 없이 컴파일·mock credential adapter 테스트가 가능해야 한다. 실제 로그인 UI/서버 검증은 USER-AUTH-GOOGLE에 남긴다. 설정 key를 채우면 동작할 실제 호출 코드가 존재해야 한다.
- 산출물: `GoogleAuthProvider.kt, Android dependency/config, auth sample UI`.
- 실연동 대기 연결: `USER-AUTH-GOOGLE`. 로컬 구현/검증과 별도로 기록한다.

#### P04-T02 — 실제 iOS Apple 로그인 adapter

- 의존: P03-T02, P03-T04. 참조: 7.4장.
- 구현: AuthenticationServices controller/delegate/presentation anchor, nonce, identityToken 전달, first-login 이름 처리, cancellation, revoked credential 처리를 구현한다. Swift controller의 생명주기를 유지하고 UI는 main actor에서 실행한다.
- 완료 확인: code-signing 없는 범위의 build와 provider fake callback 확인을 수행한다. Sign in with Apple capability·계정 실기기 검증은 사용자 대기로 남긴다. 미설정 entitlement를 정상 로그인처럼 처리하지 않는다.
- 산출물: `AppleAuthProvider.swift, Swift sample auth wiring, entitlement template`.
- 실연동 대기 연결: `USER-AUTH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P04-T03 — 서버 실제 identity 검증·nonce 재사용 방어

- 의존: P04-T01, P04-T02, P02-T02. 참조: 7.4장.
- 구현: Google/Apple token verifier를 구현한다. JWKS/공식 라이브러리, issuer/audience/exp/nonce 검증, challenge 원자 소비, subject-based identity mapping을 넣는다. token algorithm을 문서/실제 verifier에 맞게 제한하고 decode만으로 통과시키지 않는다.
- 완료 확인: local test key 또는 verifier stub으로 정상/잘못된 aud/만료/재사용/키조회 실패를 확인한다. 자체 서명 fixture 통과는 Google/Apple 실제 서명 검증 PASS와 구분한다. 외부 인증 결과를 조작해 만들지 않는다.
- 산출물: `GoogleIdentityVerifier, AppleIdentityVerifier, ChallengeService, auth migrations`.
- 실연동 대기 연결: `USER-AUTH-GOOGLE, USER-AUTH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P04-T04 — 세션 복원·single-flight 갱신·로그아웃

- 의존: P04-T03, P01-T05. 참조: 7.5장.
- 구현: Native refresh coordinator를 구현하고 동시에 여러 API가 401을 받아도 한 번만 갱신한다. 재인증 필요/오프라인/만료를 구분한다. 계정 변경 시 현재 구매 owner binding·푸시 association을 일관되게 바꾼다. 안전하지 않은 이전 token 복구를 하지 않는다.
- 완료 확인: 로컬 서버로 동시 만료 요청, refresh rotation, 저장소 재읽기, 오프라인 로그아웃을 확인한다. C#에 token이 반환되거나 PlayerPrefs에 저장되지 않는지 확인한다.
- 산출물: `Native SessionCoordinator, logout integration, docs/SECURITY.md 초안`.

#### P04-T05 — 인증 Native·Unity 소비자 통합

- 의존: P04-T01, P04-T02, P04-T04, P03-T06. 참조: 5장, 11장.
- 구현: 세 샘플에 provider 선택·로그인·로그아웃·restore 결과를 연결한다. 플랫폼에 없는 제공자는 명시적으로 unavailable 처리한다. Unity Native 경로에서 인증 토큰 없이 user snapshot만 전달하는지 확인한다.
- 완료 확인: Mock 전 흐름은 로컬에서 확인하고 실제 provider의 UI·토큰 교환은 설정 후 실행할 단계와 명령으로 남긴다. Android Kotlin 및 Swift standalone 앱과 Unity 경로를 별도로 추적한다.
- 산출물: `세 샘플의 auth panel, integration guide, auth validation matrix`.
- 실연동 대기 연결: `USER-AUTH-GOOGLE, USER-AUTH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

### P05 — 실제 결제 코드·검증·지급·복구

#### P05-T01 — 구매 상태·account binding 계약

- 의존: P02-T03, P04-T04. 참조: 5.2장, 8장.
- 구현: store state/fulfillment/finalization을 분리한 상태기계를 Native와 server에 구현한다. appAccountToken/obfuscated account binding을 서버에서 안정적으로 제공한다. 로그인 바뀜·중복 UI·취소·보류·앱 종료를 모델링한다.
- 완료 확인: 최소 상태 전이 smoke로 pending에서 grant 불가, granted 재진입 시 재지급 불가, account mismatch 거부를 확인한다. 단순 boolean purchased로 되돌리지 않는다.
- 산출물: `PurchaseCoordinator, account binding fields/API, state transition documentation`.

#### P05-T02 — 실제 Google Play Billing adapter

- 의존: P05-T01, P03-T01. 참조: 8.2장.
- 구현: BillingClient connection·상품 조회·구매 UI·purchase updates·pending·복구 query·account binding을 구현한다. consume/acknowledge는 서버 소유이므로 클라이언트에서 자동 실행하지 않는다. 실결제 profile과 Mock을 분리한다.
- 완료 확인: 컴파일과 fake BillingClient 경계 smoke를 수행한다. Play Console/internal testing 설치가 없으면 실제 구매는 사용자 대기다. item unavailable를 성공으로 무시하지 않는다.
- 산출물: `GooglePlayBillingProvider.kt, product map, store UI`.
- 실연동 대기 연결: `USER-BILLING-GOOGLE`. 로컬 구현/검증과 별도로 기록한다.

#### P05-T03 — StoreKit 2·로컬 .storekit 시나리오

- 의존: P05-T01, P03-T02. 참조: 8.3~8.4장.
- 구현: StoreKit Product/purchase/Transaction.updates/unfinished/current entitlements/finish와 USER_RESTORE를 구현한다. 두 상품의 .storekit 파일과 scheme 연결을 작성한다. 로컬 Xcode 거래는 development-only verifier 경로로 명시 분리한다.
- 완료 확인: 가능한 Xcode simulator에서 purchase/cancel/pending/finish의 로컬 흐름을 확인한다. 로컬 StoreKit만 통과하면 실 App Store 검증은 WAITING_USER로 남긴다. AppStore.sync를 앱 시작마다 호출하지 않는다.
- 산출물: `StoreKitBillingProvider.swift, GameBridge.storekit, test scheme`.
- 실연동 대기 연결: `USER-BILLING-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P05-T04 — 실제 Google·Apple 구매 검증 서버

- 의존: P05-T02, P05-T03, P02-T04. 참조: 8.4장.
- 구현: 공식 Google Developer API client와 Apple server library를 연결한다. app/package/bundle/product/environment/account/거래 상태·revocation 검증을 넣는다. 외부 credential은 lazy/configured provider에만 필요하도록 조립한다. 네트워크 실패와 위조 증빙을 구분한다.
- 완료 확인: 가짜 HTTP 응답/서명 fixture로 mapping과 거부 경로를 검증한다. unknown product, wrong account, wrong environment, forged proof는 grant 없이 끝나야 한다. 실제 서명/스토어 조회는 사용자 대기로 남긴다.
- 산출물: `GooglePurchaseVerifier, ApplePurchaseVerifier, provider configuration`.
- 실연동 대기 연결: `USER-BILLING-GOOGLE, USER-BILLING-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P05-T05 — 지급 원자성·동시성·서버 finalizer 연결

- 의존: P05-T04, P02-T04. 참조: 8.5장.
- 구현: 검증된 응답만 PurchaseService에 연결하고 unique collision을 안전하게 재조회한다. Google server consume/acknowledge를 durable job에 붙인다. 재시작 후 job 복구와 finalization status 조회를 구현한다. 고의 지연은 development fixture에서만 허용한다.
- 완료 확인: 로컬 DB에서 동시 중복 요청 10개에 원장 1개, 응답 유실 후 재요청에도 원장 1개, finalizer 실패 후 재시도에도 금액 불변을 확인한다. 원인과 SQL 결과를 증거로 남긴다.
- 산출물: `PurchaseService, GoogleFinalizer, JobWorker, concurrency smoke evidence`.

#### P05-T06 — Native 복구·store finish·timeout 이후 처리

- 의존: P05-T05, P05-T02, P05-T03. 참조: 8.3장, 8.6장.
- 구현: 앱 복귀와 재시작에서 미완료 거래를 처리한다. 서버 지급 성공 뒤 Apple finish, Google은 서버 finalization 상태를 따른다. timeout으로 끝난 public Task는 재완료하지 않고 이벤트/재조회로 상태를 복구한다. 구매 당시 user binding을 보존한다.
- 완료 확인: Fake/로컬 StoreKit에서 지급 후 응답 유실, finish 전 종료, 재시작, 계정 변경을 시뮬레이션한다. 원래 Task 종료 횟수와 실제 지급 횟수를 따로 확인한다.
- 산출물: `Native PurchaseRecovery, durable pending metadata, lifecycle hooks`.

#### P05-T07 — Unity·Native 상점 완성

- 의존: P05-T06, P03-T06. 참조: 11장.
- 구현: 두 상품 조회·localized price·구매·pending·verification pending·entitlement refresh·restore를 세 샘플에 연결한다. UI가 사라져도 거래 coordinator를 유지한다. 결제 완료 토스트만 있고 잔액 상태가 없는 샘플로 끝내지 않는다.
- 완료 확인: LOCAL_MOCK에서 두 상품 전체 흐름과 서버 잔액/entitlement를 확인한다. 실제 스토어 product query·purchase·restore는 Android/iOS 각각 USER_SETUP에 실행 순서를 남긴다.
- 산출물: `세 샘플의 store panels, purchase status UI, billing evidence`.
- 실연동 대기 연결: `USER-BILLING-GOOGLE, USER-BILLING-APPLE`. 로컬 구현/검증과 별도로 기록한다.

### P06 — 푸시와 생명주기

#### P06-T01 — 실제 FCM 등록·수신·권한 adapter

- 의존: P02-T05, P04-T04. 참조: 9.1장.
- 구현: Firebase host-owned init, notification permission/channel, token refresh, message forwarding과 click intent 전달을 구현한다. SDK sample service와 host 기존 service 통합 방식을 분리한다. 실 config 없는 mock build가 계속 성공해야 한다.
- 완료 확인: compile·mock token rotate·message mapping·permission denied를 확인한다. google-services.json 부재가 mock build를 깨지 않는지 확인한다. 실제 token 발급/원격 수신은 사용자 대기다.
- 산출물: `AndroidPushProvider, host service adapter, manifest/config templates`.
- 실연동 대기 연결: `USER-PUSH-GOOGLE`. 로컬 구현/검증과 별도로 기록한다.

#### P06-T02 — Swift APNs 등록·Host forwarding

- 의존: P02-T05, P04-T04. 참조: 9.2장.
- 구현: 권한 조회·명시적 요청, remote registration success/failure, notification received/opened 전달을 구현한다. SwiftUI SampleApp AppDelegate에서 forwarding을 연결하고 SDK가 host delegate를 덮어쓰지 않게 한다.
- 완료 확인: 로컬 payload 주입 및 가능한 알림 권한 UI를 확인한다. 토큰 발급이 없는 경우 실제 APNs 등록으로 기록하지 않는다. delegate completion handler를 누락하지 않는지 확인한다.
- 산출물: `ApplePushProvider, PushHostAdapter, SampleApp AppDelegate`.
- 실연동 대기 연결: `USER-PUSH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P06-T03 — Unity iOS Push Host Adapter

- 의존: P06-T02, P03-T05. 참조: 9.3장.
- 구현: 고정한 Mobile Notifications 패키지 API로 token·remote event·last opened notification을 받아 Swift bridge host operation에 전달한다. host-managed 모드로 권한/등록 중복을 막는다. C# 조건부 compilation과 package dependency를 설정한다.
- 완료 확인: Editor/Android에서 iOS 전용 코드가 compile error를 만들지 않아야 한다. iOS export에서 package 연결을 확인하고 실원격 동작은 대기로 남긴다. fake event 주입으로 route 파이프라인은 확인한다.
- 산출물: `Unity iOSPushHostAdapter, asmdef/package.json, host operation mapping`.
- 실연동 대기 연결: `USER-PUSH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P06-T04 — Backend FCM·APNs 실제 sender

- 의존: P06-T01, P06-T02, P02-T05. 참조: 9.4장.
- 구현: Firebase Admin sender와 APNs HTTP/2 token-auth sender를 구현한다. credential lazy init, environment/topic, invalid-token disable, retry/rate limit을 넣는다. dev send endpoint의 admin key와 대상 allowlist를 유지한다.
- 완료 확인: mock HTTP/transport로 성공·invalid token·429·timeout을 확인한다. production profile에서 개발 발송 endpoint가 비활성인지 확인한다. 실제 발송 성공을 credential 없이 주장하지 않는다.
- 산출물: `FcmPushSender, ApnsPushSender, token lifecycle/error mapping`.
- 실연동 대기 연결: `USER-PUSH-GOOGLE, USER-PUSH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

#### P06-T05 — 수명주기·콜드스타트·클릭 라우팅

- 의존: P06-T03, P06-T04, P05-T06. 참조: 9.4장, 11장.
- 구현: home/store allowlist, 초기화 전 메시지 queue, messageId 중복 제거, foreground/background/cold-start 상태를 연결한다. 계정 변경·logout에서 token association을 정리한다. OS 제한을 회피하는 background service를 새로 만들지 않는다.
- 완료 확인: 로컬 event 주입으로 초기화 전/후, scene 변경, 같은 messageId 중복을 확인한다. 실제 notification tap과 강제종료 이후 동작은 실제 OS 조건에서 별도로 검증해야 한다.
- 산출물: `PushRouter, lifecycle coordinator, Unity/native UI handling`.
- 실연동 대기 연결: `USER-PUSH-GOOGLE, USER-PUSH-APPLE`. 로컬 구현/검증과 별도로 기록한다.

### P07 — 기능·샘플·문서 완결

#### P07-T01 — 진단·redaction·점검 설정 완성

- 의존: P06-T05. 참조: 9.5장.
- 구현: 정제 ring buffer와 diagnostics export를 구현한다. config TTL/cache/default/maintenance를 연결하고 점검 중 신규 구매만 차단한다. 기존 거래 검증·복구·로그아웃은 계속 허용한다. 원문 event payload를 무조건 로깅하지 않는다.
- 완료 확인: 민감 토큰 모양의 입력이 로그에 남지 않는지 확인한다. config offline cache와 maintenance 중 recovery 허용을 확인한다. 측정하지 않은 성능 수치를 문서에 넣지 않는다.
- 산출물: `Diagnostics, Redactor, ConfigRepository, sample settings panel`.

#### P07-T02 — 세 샘플 전체 사용자 흐름 연결

- 의존: P07-T01, P05-T07. 참조: 11장.
- 구현: 로그인·상점·재화·알림·설정·진단을 세 샘플에서 완결한다. disabled 버튼의 이유와 대기 상태를 표시한다. Unity 두 화면 전환과 native background/foreground를 시연할 경로를 제공한다.
- 완료 확인: 사용자가 README 순서대로 LOCAL_MOCK을 실행할 수 있는지 직접 따라한다. 기능마다 source mode와 상태를 확인하고 UI의 실제 서비스 주장/가짜 리뷰/가짜 성과 수치를 제거한다.
- 산출물: `완결된 Android/iOS/Unity samples, demo walkthrough`.

#### P07-T03 — 연동 문서·오류·소유권 가이드

- 의존: P07-T02. 참조: 5~10장.
- 구현: README, API.md, INTEGRATION.md, SECURITY.md 초안을 작성한다. UI main thread, token ownership, store finalization, host delegate forwarding, config/permission, transitive dependencies, 지원 제외 기능을 명시한다.
- 완료 확인: 문서의 모든 예제 API가 실제 source와 일치하고 임의 클래스명/미구현 함수가 없는지 확인한다. 없는 release URL·완료되지 않은 real test를 성공 사례로 넣지 않는다.
- 산출물: `README.md, docs/API.md, docs/INTEGRATION.md, docs/SECURITY.md`.

#### P07-T04 — 구현 누락 1차 점검

- 의존: P07-T03. 참조: 0장, 1장.
- 구현: 계약의 모든 public operation과 provider에 실제 호출 경로가 있는지 매핑한다. TODO/FIXME/NotImplementedException/fatalError/고정 success를 검색하고 명시적인 excluded/unsupported 외의 누락을 수정한다. 사용자 설정 대기와 코드 미구현을 분리한다.
- 완료 확인: 기능→public API→Native/Server 구현→sample 사용 경로의 traceability 표를 만든다. 발견한 미구현은 BUG/PX Task로 기록하고 독립 개발을 진행한 뒤 반드시 재검토한다.
- 산출물: `docs/FEATURE_MATRIX.md, docs/PROGRESS.md 누락 표`.

### P08 — 패키징·기능 기준점

#### P08-T01 — Android Maven 산출물·소비 build

- 의존: P07-T04. 참조: 10.1장.
- 구현: 각 라이브러리를 AAR+POM+metadata로 로컬 Maven repo에 publish한다. dependency scope와 consumer R8 rules를 정리한다. 별도 native consumer app에서 source project dependency 없이 coordinate로 가져온다.
- 완료 확인: 깨끗한 소비 build에서 전이 의존성·manifest·R8 release build를 확인한다. AAR만 복사해 unresolved class가 발생하면 해결 전 PASS하지 않는다.
- 산출물: `Maven publish config, artifacts/maven-repo, scripts/build-android.sh, consumer evidence`.

#### P08-T02 — Swift Package·static XCFramework 산출물

- 의존: P07-T04, P03-T04. 참조: 10.2장.
- 구현: source package 소비와 device/simulator archive→XCFramework script를 완성한다. 필요한 symbols/resources/link settings를 확인한다. 생성 파일을 수동 binary 편집하지 않는다.
- 완료 확인: source consumer build, XCFramework slice·symbol·별도 consumer link를 실제 확인한다. signing 없는 archive와 signed device 실행을 구분한다. 환경이 없어 archive를 못 했으면 산출물이 생성됐다고 기록하지 않는다.
- 산출물: `scripts/build-ios.sh, Package.swift, framework config, binary evidence`.

#### P08-T03 — UPM staging·멱등 build hook

- 의존: P08-T01, P08-T02. 참조: 10.3장.
- 구현: UPM Runtime/Editor/Plugins/metadata와 Android local Maven hook·iOS link hook을 완성한다. staging package에 자체 native artifact와 필요한 install metadata를 넣는다. hook을 재실행해도 중복되지 않게 한다. 없는 artifact는 친절한 setup error로 실패한다.
- 완료 확인: Editor import, asmdef/platform 조건, hook 두 번 실행, .meta 안정성, checksum을 확인한다. Git source install과 바이너리 완결 staging install을 README에서 구분한다.
- 산출물: `scripts/package-sdk.sh, UPM Editor installer/hooks, artifacts/dist`.

#### P08-T04 — 신규 Unity 프로젝트 재설치 검증

- 의존: P08-T03. 참조: 10.4장.
- 구현: Demo와 다른 disposable Unity 프로젝트를 생성하고 staging UPM만 설치한다. bootstrap 문서 그대로 Native 설정과 mock scene을 가져온다. 기존 workspace 절대 경로나 직접 소스 참조를 제거한다.
- 완료 확인: clean Editor import→mock scene→Android export/build→iOS export/build를 가능한 범위에서 실행한다. Unity/target module/license 부재는 ENV로 기록한다. 패키지 파일 누락은 BUG로 분류한다.
- 산출물: `clean consumer generation script, docs/evidence/consumer-install.md`.

#### P08-T05 — 기능 개발 기준점 고정

- 의존: P08-T04. 참조: 0장, 12장.
- 구현: 기능 구현·샘플·배포 상태와 남은 사용자/환경 블로커를 정리한다. 현재 public API와 protocol을 파일 snapshot으로 저장한다. baseline Git commit을 기록하고 이후에 P09 하네스를 붙인다. 공개 v1.0 release는 생성하지 않는다.
- 완료 확인: P00~P08 모든 행을 확인하고 NOT_STARTED를 묵시적으로 누락하지 않는다. 내부 미구현을 사용자 인증 부족이라고 쓰지 않는다. 가능한 build/smoke baseline 결과와 API snapshot이 존재해야 한다.
- 산출물: `docs/evidence/feature-baseline.md, contracts/baseline/, PROGRESS checkpoint`.

### P09 — 후반 하네스·회귀·CI

#### P09-T01 — 후반 하네스 manifest·공통 contract test

- 의존: P08-T05. 참조: 14장.
- 구현: 이 시점에 harness/scenarios와 검증 manifest를 만든다. 플랫폼·level·mode·required·expected·evidence를 명시하고 schema/API fixture를 Kotlin/Swift/C#에서 실행한다. 초기 문서 검사와 제품 검증 하네스를 구분한다.
- 완료 확인: 모든 required 시나리오에 ID와 실행 entry가 있고 잘못된 fixture에서 실패해야 한다. 도구가 없는 platform을 자동 제외해 전체 green으로 만들지 않는다.
- 산출물: `harness/regression-manifest.json, shared fixtures, contract tests`.

#### P09-T02 — Core·Bridge 회귀·실패 주입

- 의존: P09-T01. 참조: 14장 R01~R12.
- 구현: init race, duplicate/late callback, timeout, session reset, invalid UTF-8/JSON, unknown operation, scene lifecycle, pending map cleanup을 테스트한다. deterministic scheduler/clock을 사용하고 sleep에 의존하는 flaky test를 줄인다.
- 완료 확인: 의도적으로 duplicate completion guard를 제거한 임시 mutation에서 해당 검증이 실패하는지 확인하고 복원한다. PASS/FAIL/assert count를 기록한다.
- 산출물: `Kotlin/Swift/Unity Core and Bridge tests, fault injector`.

#### P09-T03 — 인증·세션·개발모드 차단 회귀

- 의존: P09-T01. 참조: 14장 R13~R22.
- 구현: issuer/aud/exp/nonce/replay, simultaneous refresh, rotation reuse, logout offline, secure storage redaction, sandbox dev-auth 거부를 테스트한다. 외부 token real test는 독립 suite로 유지한다.
- 완료 확인: 로컬 fixture suite를 실제 실행하고 fake token을 sandbox에 제출했을 때 거부되는지 확인한다. 실제 Google/Apple 테스트는 미설정이면 WAITING_USER다.
- 산출물: `Backend auth tests, native session tests, profile security tests`.

#### P09-T04 — 구매·DB 동시성·복구 회귀

- 의존: P09-T01. 참조: 14장 R23~R39.
- 구현: Testcontainers PostgreSQL로 동시 중복, 서로 다른 key, user mismatch, transaction rollback, pending→purchased, finalization retry, 응답유실, app restart, finish ordering, revoked 상태를 검증한다. 코인 지급은 원장 SQL로 확인한다.
- 완료 확인: 원장 unique/지급 순서를 임시로 손상한 음성 검증에서 실패하는지 확인한다. Docker 부재는 DEFERRED_ENV이며 통합 suite zero-test 성공을 허용하지 않는다.
- 산출물: `Backend purchase integration tests, native recovery tests, DB evidence`.

#### P09-T05 — Push·Lifecycle·패키징 회귀

- 의존: P09-T01. 참조: 14장 R40~R50.
- 구현: token rotate/logout/re-register, delegate 보존, permission denied, cold-start route dedupe, malicious route 차단, maintenance recovery, dependency resolution, iOS symbol/link, new consumer install을 suite로 만든다.
- 완료 확인: mock event는 fake test로 표시하고 실제 OS notification와 구분한다. 필요한 binary를 임시 staging에서 제거했을 때 packaging 검증이 실패해야 한다.
- 산출물: `Push tests, package checks, clean consumer smoke suite`.

#### P09-T06 — 검증 집계·진행 원장 강제 검사

- 의존: P09-T02, P09-T03, P09-T04, P09-T05. 참조: 13~14장.
- 구현: verify-all과 결과 JSON/Markdown 집계를 구현한다. per suite exit code, counts, mode, environment, commit, evidence를 저장한다. required suite 누락/skip/실패와 external 대기를 별도 exit status로 처리한다. 진짜 검증 없이 상태를 PASS로 바꾸지 않는다.
- 완료 확인: PASS, 실패 한 개, required skip, 외부 설정 대기 네 경우를 각각 확인한다. --strict-local에서는 required local skip을 성공으로 돌려주면 안 된다.
- 산출물: `scripts/verify-all.sh, result collector, docs/evidence/verification-summary.md`.

#### P09-T07 — CI 설정·플랫폼 lane 분리

- 의존: P09-T06. 참조: 14.3장.
- 구현: GitHub Actions에서 Linux backend+contract+Android, macOS iOS, 별도 Unity license lane을 구성한다. 외부 credential 없는 PR에서는 real tests를 실행하지 않는다. fork에 secret을 노출하지 않는다. concurrency 취소·캐시 key·timeout을 설정한다.
- 완료 확인: workflow static validation과 가능한 로컬 대응 명령을 확인한다. push 권한을 사용하지 않으므로 원격 Actions 성공을 만들어내지 않는다. Unity lane 미실행은 aggregate에서 명시적으로 대기여야 한다.
- 산출물: `.github/workflows/, CI docs, local workflow evidence`.

#### P09-T08 — Fail-closed 하네스 자체 시험

- 의존: P09-T07. 참조: 14.4장.
- 구현: 문서 누락, 실패 테스트, required suite 제거, native artifact 누락, fake token real profile 주입을 disposable workspace/fixtures로 시험한다. 제품 소스를 고의 손상한 상태로 최종 브랜치에 남기지 않는다. 검사기 우회 플래그로 green을 만들지 않는다.
- 완료 확인: 각 부정 시험이 실제 nonzero인지 기록한다. 원상 복구 후 정상 suite를 재실행한다. 감지 못한 사례는 하네스 버그로 수정하고 재확인한다.
- 산출물: `harness self-check, negative-test evidence, repaired verification`.

### P10 — 검증 기반 리팩토링

#### P10-T01 — 검증 기준 유지하며 Core·Bridge 리팩토링

- 의존: P09-T08. 참조: 6장, 15장.
- 구현: 기능 baseline public API를 유지하고 registry/dispatcher/native transport 책임을 정리한다. 주입·thread ownership·lifecycle cleanup을 단순화한다. 한 번에 전체 플랫폼을 갈아엎지 않고 작은 변경마다 관련 suite를 실행한다.
- 완료 확인: baseline contract diff와 관련 회귀 tests가 통과해야 한다. 성능 개선을 이유로 취소/late event semantics를 바꾸지 않는다. 변경 전후 commit과 결과를 남긴다.
- 산출물: `Refactored Core/Bridge, API compatibility evidence`.

#### P10-T02 — 인증·결제·푸시 책임과 보안 정리

- 의존: P10-T01. 참조: 7~9장, 15장.
- 구현: 모든 서비스를 공통 base class로 과도하게 합치지 않는다. 상태기계·서버 검증·저장소·OS UI의 책임을 분리하고 임시 중복과 dead code를 제거한다. actual provider 구현을 Fake로 치환해 테스트를 쉽게 만들지 않는다.
- 완료 확인: security/purchase/push 관련 suite와 LOCAL_MOCK E2E를 재실행한다. transaction/idempotency/finalization 순서가 유지되는지 확인한다.
- 산출물: `Refactored feature services, security regression evidence`.

#### P10-T03 — 측정 기반 수명주기·메모리·응답 확인

- 의존: P10-T02. 참조: 15장.
- 구현: 동일 환경에서 초기화/콜백 왕복·반복 초기화/종료·scene 교체를 측정한다. native/UI profiling 도구가 있으면 누수와 main-thread blocking을 확인한다. 백엔드 단순 부하/중복 요청도 로컬에서만 수행한다.
- 완료 확인: 기기/OS/build/mode/sample count와 p50/p95 또는 관측값을 기록한다. 실행하지 못한 profiling은 NOT_RUN이다. 측정 없는 99.9% 안정성이나 대규모 운영 성과를 만들지 않는다.
- 산출물: `docs/evidence/performance.md, lifecycle stress results`.

#### P10-T04 — 리팩토링 후 재패키징·호환성 재검증

- 의존: P10-T03. 참조: 10장, 15장.
- 구현: 모든 native artifact/UPM staging을 현재 source에서 다시 만든다. source SHA와 VERSION/checksum을 맞추고 old consumer API fixture를 compile한다. 새 consumer 설치를 다시 수행한다.
- 완료 확인: 리팩토링 전 artifact를 재사용해 통과시키지 않는다. API source compatibility, Android artifact 소비, Swift module/binary 소비, Unity build를 실제 수행 범위별로 표시한다. 모든 Unity/OS 버전 호환을 주장하지 않는다.
- 산출물: `최종 artifacts/dist, COMPATIBILITY.md, package rebuild evidence`.

### P11 — 최종 감사·사용자 인계

#### P11-T01 — 전체 Task·TODO·계약 누락 최종 감사

- 의존: P10-T04. 참조: 0~2장, 16장.
- 구현: 모든 원장 행·기능 matrix·소스 TODO·실행 증거를 대조한다. 내부 미구현/FAIL은 수정하고 가능한 독립 검증을 다시 실행한다. 여전히 해결 못 한 것은 BUG로 남기고 상태를 BLOCKED_INTERNAL로 한다. 인증 대기에 필요한 코드가 실제 있는지 점검한다.
- 완료 확인: 계획 Task 총수와 원장 총수가 같아야 한다. 구현/로컬/실연동 수치가 각각 계산돼야 한다. 증거 경로가 존재하고 실제 명령 결과와 맞아야 한다.
- 산출물: `Audited PROGRESS/FEATURE_MATRIX, outstanding BUG list`.

#### P11-T02 — 사용자 설정·실연동 재개 runbook 완성

- 의존: P11-T01. 참조: 17장, USER_SETUP.md.
- 구현: Google/Apple/Unity/Git/기기 설정을 빠짐없이 정리한다. 각 항목에 사용자가 해야 할 일, 비밀파일 위치, 연결한 코드, configuration check, 실제 실행 command, 기대 결과, 실패 진단을 채운다. P00에서 발견한 환경에 맞게 명령을 구체화한다.
- 완료 확인: verify-external --check-config는 비밀값을 출력하지 않고 readiness만 확인한다. 실키 없는 상태로 실제 로그인/결제를 시도하지 않는다. 외부 readiness pass와 live test pass를 혼동하지 않는다.
- 산출물: `docs/USER_SETUP.md, scripts/verify-external.sh, credential readiness docs`.

#### P11-T03 — 최종 문서·release candidate 로컬 패키지

- 의존: P11-T02. 참조: 16장.
- 구현: README·API·Integration·Security·Changelog·Compatibility·FINAL_REPORT를 실제 결과에 맞춰 작성한다. 최종 source SHA 기반 manifest와 checksum을 만들고 로컬 패키지만 보관한다. 공개 Release/스토어 업로드/자동 push는 하지 않는다.
- 완료 확인: source/version/checksum/설치 절차가 일치하고 실제 생성하지 못한 artifact를 포함됐다고 쓰지 않아야 한다. 외부 대기이면 release-candidate 또는 dev 상태로 표시한다.
- 산출물: `docs/FINAL_REPORT.md, release manifest, checksums, 완성 문서`.

#### P11-T04 — 마지막 검증·커밋·인계

- 의존: P11-T03. 참조: 0.2장, 16장.
- 구현: verify-progress, strict local suite, git diff --check와 secret-aware 검토를 실행한다. 실제 commit history를 final report에 기록하고 마지막 문서 커밋을 남긴다. git status에서 사용자 원본 변경과 자신의 잔여 변경을 구분한다. 자동 개발 결과를 근거 있는 최종 상태로 보고한다.
- 완료 확인: 미검증을 PASS로 바꾸지 않고 완료/미완료/사용자 대기/환경 대기/내부 실패를 각각 나열한다. 다음 행동은 USER_SETUP의 첫 미완료 항목 또는 재개 Task여야 한다. 단계 승인 질문으로 끝내지 않는다.
- 산출물: `최종 docs/PROGRESS.md, WORK_LOG.md, FINAL_REPORT.md, 로컬 Git 커밋`.

## 13. 명령 인터페이스·실행 증거 규칙

### 13.1 Codex가 구현할 명령

아래 명령은 **계획된 인터페이스**다. 아직 존재하거나 실행됐다는 뜻이 아니다. P00에서 진입점을 만들고 해당 기능 Task에서 실제 구현을 채운다. 설명만 출력하고 성공 종료하는 script는 금지한다. root에서 실행 가능하게 만들고 OS/tool 미설치 시 원인을 출력한다.

| 명령 | 실제 수행해야 할 일 | 도입 시점 |
|---|---|---|
| `bash scripts/doctor.sh` | toolchain/프로젝트 경로/버전/권한·환경 가용성을 조사 | P00 |
| `python3 scripts/verify-progress.py` | Task/진행 원장/증거/로그/USER_SETUP 일관성 검사 | P00 |
| `bash scripts/build-android.sh --mock` | Gradle native SDK·mock sample assemble | P00→P03 |
| `bash scripts/build-ios.sh --simulator` | Xcode iOS simulator SDK/sample build, 가능한 테스트 | P00→P03 |
| `bash scripts/build-unity.sh --editor-smoke` | 선택 Unity로 프로젝트 import·mock smoke 실행 | P03 |
| `bash scripts/run-demo-backend.sh` | 별도 dev DB와 local-mock 서버 기동 및 health | P02 |
| `bash scripts/smoke-local.sh` | Backend Mock 흐름의 실제 HTTP/DB 검증 | P02 |
| `bash scripts/package-sdk.sh --local` | Android Maven repo·static XCFramework·UPM staging·checksum | P08 |
| `bash scripts/verify-all.sh --strict-local` | required local suite 전부 집계 | P09 |
| `bash scripts/verify-all.sh --available` | 실행 가능한 suite를 모두 실행하되 미실행을 그대로 보고 | P09 |
| `bash scripts/verify-release.sh` | package completeness·version·새 소비 build·API baseline | P09~P10 |
| `bash scripts/verify-external.sh --check-config` | 비밀값을 표시하지 않는 외부 설정 readiness 검사 | P11 |
| `bash scripts/verify-external.sh --platform android` | 설정 후 Android real test 실행/수동 체크 진입 | 사용자 설정 후 |
| `bash scripts/verify-external.sh --platform ios` | 설정 후 iOS real test 실행/수동 체크 진입 | 사용자 설정 후 |
| `python3 scripts/export-final-report.py` | 원장·evidence·Git 이력을 집계, 결과 초안 생성 | P11 |

버전별 실제 Gradle task명·Xcode scheme·Unity executeMethod가 바뀌면 script 내부와 TOOLCHAIN에 기록한다. 단순히 `./gradlew test`가 모든 플랫폼 검증을 수행한다고 가정하지 않는다. 예시 기본 명령은 `cd backend && ./gradlew test`, `cd android && ./gradlew :sample-app:assembleMockDebug`, `xcodebuild -scheme ... -destination ... test`, `Unity -batchmode ... -runTests ...`지만 **실제 생성한 variant/scheme/editor 경로에 맞게 확정**한다.

### 13.2 종료 코드와 집계

- `0`: 해당 명령이 담당하는 검증이 실제 수행되어 통과했다.
- `1`: assertion/build/test 실패 또는 내부 잘못된 상태다.
- `2`: tool/license/credential/device가 없어 필수 검증을 수행하지 못했다.
- 사용법 오류는 별도 비영(예: 64)로 표현할 수 있으나 summary에는 ERROR로 기록한다.

`--strict-local`은 required local suite가 하나라도 미실행이면 0을 반환하지 않는다. `--available`이 가능한 검증을 끝냈더라도 summary에 필수 미실행이 있으면 전체 준비 완료로 승격하지 않는다. external 대기는 strict-local 필수 목록에서 별도로 관리한다. `--check-config` 통과는 실제 외부 기능 통과가 아니다.

복수 suite를 계속 실행하려면 각 종료 코드를 명시적으로 수집하고 마지막에 집계한다. 실패를 무조건 `|| true`로 숨기는 방식은 금지한다. timeout·실행 수 0·runner crash·artifact 누락도 감지한다. GitHub에서 skip된 job만 보고 전체 SDK 검증 성공이라고 쓰지 않는다.

### 13.3 증거 파일

`docs/evidence/<phase>-<task>-<check>.md`에는 source SHA 또는 worktree 식별, OS/tool 버전, mode/provider, 명령, 시간, exit code, 실행/통과/실패/skip 수, 핵심 관측값, 한계가 있어야 한다. 대용량 raw log는 `artifacts/`에 두고 중요한 결과를 정제하여 추적한다.

테스트를 실행한 working tree와 커밋이 다르면 `base HEAD + working diff`를 표시한다. 최종 배포 evidence는 source commit 기준으로 다시 만든다. 지금 쓰는 evidence 자기 파일의 변경을 포함한 commit hash를 알아야 한다는 무한 재검증 요구를 만들지 않는다. 제품 소스와 빌드 입력이 동일한지 확인하면 된다.

실키·토큰·purchaseToken·JWS·APNs token·서비스 계정 내용은 원시 로그에서도 최소화한다. 공개 evidence에는 식별자 hash/fingerprint만 남긴다. 기존 기밀 로그를 단순 복사해 Git에 넣지 않는다.

## 14. 후반 하네스의 필수 시나리오

### 14.1 필수 로컬 검증 묶음

계약/진행 기록, Backend PostgreSQL 통합, Android SDK build+unit tests, iOS simulator build+XCTest, Unity Editor tests, 패키지 completeness 및 가능한 clean consumer build를 required local suite로 설정한다. Native 기기 실행·실제 provider는 외부/기기 suite로 별도 분리한다. iOS/Unity 도구가 없으면 해당 로컬 검증은 DEFERRED_ENV이며 전체 상태를 `LOCAL_READY_EXTERNAL_PENDING`으로 올리지 않는다.

최소 시나리오는 아래 50개다. 하나의 test가 여러 항목을 검증할 수는 있지만 각 ID와 assertion의 대응을 manifest에 명시한다. 코드 coverage 비율만으로 완료를 판단하지 않는다.

| ID | 시나리오 | 기대 결과 | 주 검증 위치 |
|---|---|---|---|
| R01 | 초기화 전 API 호출 | NOT_INITIALIZED, crash 없음 | 3언어 Core |
| R02 | 같은 config 동시 init | 단일 초기화/일관된 결과 | Core |
| R03 | 다른 config 재초기화 | 명시 오류, 기존 상태 보존 | Core |
| R04 | callback 중복 | Task 완료 1회 | Unity registry |
| R05 | timeout 후 callback | Task 재완료 없음, 거래 이벤트는 보존 | Bridge/Store |
| R06 | 다른 sdkSessionId event | 현재 세션에 전달하지 않음 | Bridge |
| R07 | malformed JSON/필수값 누락 | 명시 오류, 앱 생존 | 공통 parser |
| R08 | 과대 payload/음수 길이 | 길이 검증으로 거부 | Native Bridge |
| R09 | 한글/emoji/UTF-8 복사 | 문자열 동일, 해제 메모리 참조 없음 | C ABI/JNI |
| R10 | cancellation/shutdown race | pending task 누락/중복 완료 없음 | Core |
| R11 | scene 전환/Domain Reload | dispatcher 1개, 구독 누수 없음 | Unity |
| R12 | 100회 init/shutdown 반복 | registry/queue가 정리되고 무한 증가 없음 | Local stress |
| R13 | 잘못된 token signature/algorithm | 인증 거부 | Backend |
| R14 | wrong issuer/audience/expired | 인증 거부 | Backend |
| R15 | nonce mismatch/재사용 | 인증 거부, challenge 처리 일관 | Backend |
| R16 | Google/Apple 사용자 취소 | 정상 취소 모델, 로그인되지 않음 | Provider fake |
| R17 | 최초 로그인 profile 일부 누락 | subject로 계정 유지 | Auth |
| R18 | 10개 동시 401 | Native refresh single-flight | Session |
| R19 | 이전 refresh token 재사용 | family revoke/재로그인 | Backend |
| R20 | offline logout | 로컬 토큰 제거, 서버 pending 명시 | Native |
| R21 | sandbox에서 mock identity | 거부, dev endpoint 비활성 | Backend profile |
| R22 | 로그/Unity result 민감정보 | 원문 token/secret 없음 | Redaction |
| R23 | 같은 거래 동시 10회 verify | 원장 1개·코인 100 | PostgreSQL |
| R24 | 다른 idempotency key·같은 거래 | 지급 1회 | PostgreSQL |
| R25 | 같은 key·다른 body | 409, 추가 지급 없음 | Backend |
| R26 | 다른 user가 proof 재사용 | account mismatch, 지급 없음 | Backend |
| R27 | PENDING 거래 | grant/consume/finish 없음 | Store/Backend |
| R28 | PENDING→PURCHASED | 검증 후 1회 지급 | Store |
| R29 | 위조 proof/wrong app·product | 검증 실패, 지급 없음 | Verifier |
| R30 | store environment 불일치 | 거부 | Verifier |
| R31 | DB transaction 중간 실패 | purchase/원장 상태 원자성 | PostgreSQL |
| R32 | 지급 commit 후 응답 유실 | 재요청에 기존 결과, 재지급 없음 | Backend+client |
| R33 | Google consume/ack 실패 | durable retry, 원장 불변 | Worker |
| R34 | Apple finish 전 앱 종료 | 재실행 후 기존 지급 확인·finish | StoreKit/Fake |
| R35 | 서버 검증 실패/timeout | finish/consume 금지, retry 상태 | Native/Server |
| R36 | 비소모성 복원 | entitlement 복구, 중복 생성 없음 | Store |
| R37 | 소모성 과거 잔액 복원 | 서버 원장 기준, 구매 기록 재지급 없음 | Backend/client |
| R38 | 구매 중 로그인 계정 변경 | 구매 당시 binding 보호 | Coordinator |
| R39 | revoked/multi-quantity 관측 | 정책대로 거부/지원 제외, 임의 지급 없음 | Verifier |
| R40 | push 권한 거부 | 등록/표시 상태 명시, crash 없음 | Native |
| R41 | token rotate | 새 token 등록·오래된 association 정리 | Push/Server |
| R42 | logout·다른 user login | token 소유 연결 정확히 이동 | Push/Server |
| R43 | APNs host delegate 연동 | 기존 delegate 보존·completion 호출 | Swift/Unity host |
| R44 | 초기화 전 push click | READY 후 1회 전달 | Router |
| R45 | 중복 messageId/잘못된 route | 중복 제거/allowlist 차단 | Router |
| R46 | 점검 모드에서 거래 복구 | 신규 구매 차단, 기존 처리 허용 | Config/Store |
| R47 | Android dependency 누락 | 소비 build 실패 감지 | Packaging |
| R48 | iOS C symbol/slice 누락 | 링크 전 검사 또는 build 실패 감지 | Packaging |
| R49 | 신규 Unity consumer 설치 | Demo 소스 직접 참조 없이 import/build | Packaging |
| R50 | 필수 suite 미실행/증거 누락 | 전체 완료 판정 금지 | Harness self-test |

기능상의 안전 규칙은 P09까지 미뤄도 된다는 뜻이 아니다. P09에서는 이미 구현한 기능에 대해 **실패를 재현하고 회귀를 지속 검출하는 자동화**를 본격 추가한다.

### 14.2 외부 실연동 시나리오

Google/Apple 실제 로그인+서버 token 검증, 세션 재실행, Play 테스트 결제+서버 조회+consume/ack, Apple Sandbox 결제+JWS 검증+finish+복원, FCM/APNs 원격 수신·클릭, Unity Android/iOS Native bridge 실제 실행을 별도 EXT ID로 만든다. 테스트 계정/상품/서명 준비 후 실행하며 실제 금전 결제나 운영 발송은 하지 않는다.

Local StoreKit·FCM payload 주입·mock server JWS 응답은 외부 suite 대체가 아니다. Android emulator와 실기기, iOS simulator와 실기기, Native sample과 Unity sample의 증거를 따로 남긴다.

### 14.3 CI 구성

- Linux lane: 문서/계약, Backend unit+PostgreSQL integration, Android unit/lint/build, secret-aware 검사.
- macOS lane: iOS simulator build/test, framework archive 가능한 범위. signing secret 없는 PR에서도 가능한 작업은 실행한다.
- Unity lane: Editor tests·target build를 별도 구성하고 license/installation prerequisites를 명시한다. 지원하지 않는 환경에서 성공한 척하는 placeholder job은 만들지 않는다.
- 최종 gate: required lane의 실제 결과를 집계한다. job 자체가 실행되지 않은 상태와 테스트 성공을 구분한다.

원격 push/Actions 실행은 이번 기본 권한에 없다. workflow 파일이 작성됐다는 사실과 GitHub에서 실행됐다는 사실을 분리한다. 로컬 `act`가 있더라도 macOS runner·Unity license를 완전히 대신한다고 주장하지 않는다. 외부 PR에 secret이 전달되지 않게 하고 외부 입력을 shell command에 그대로 붙이지 않는다.

### 14.4 하네스가 실패를 잡는지 확인

실패 테스트를 하나 넣고 test job이 실패하는지, required suite를 누락하고 summary가 완료를 거부하는지, 원장 PASS 증거를 제거하고 문서 검사가 실패하는지 확인한다. temporary fixture/disposable workspace를 사용하고 마지막에 복원한다. 고의 실패를 영구 main 소스에 남겨 빌드를 깨지 않는다.

`tests passed` 로그만 검사하는 문자열 판별 대신 test report·exit code·실행 수를 조합한다. baseline snapshot을 무조건 자동 갱신해 모든 회귀를 합격시키지 않는다. 기대 결과 변경에는 이유와 변경 내역을 기록한다.

## 15. 리팩토링 순서와 허용 기준

리팩토링은 P09의 실행 가능한 회귀 기준을 만든 뒤 시작한다. 변경 단위는 작은 책임 단위이며 서로 다른 플랫폼 전체를 한 번에 재작성하지 않는다.

첫째, Core/Bridge의 thread·request registry·memory ownership·lifecycle를 정리한다. 둘째, Auth/Store/Push의 Provider adapter와 business coordinator를 분리한다. 셋째, sample이 SDK 내부 타입이나 secret에 의존하는 부분을 제거한다. 넷째, 동일 조건에서 최소 측정으로 메모리/지연을 확인하고 필요한 개선만 한다. 마지막으로 artifact를 전부 재생성하고 새 소비 프로젝트로 확인한다.

공개 API 이름만 같은 것이 호환성은 아니다. 결과 enum 의미, 오류 code, 이벤트 발생 조건, callback thread, 취소 semantics, 설정 기본값도 비교한다. pre-1.0에서 불가피하게 바꿔야 한다면 계획/계약/샘플/마이그레이션 노트와 버전을 같이 변경한다. 하위 호환성을 지키지 못했다면 그대로 기록한다.

JVM source/API compatibility, AAR transitive dependency 호환, Swift source/module/binary compatibility, Unity C# source와 IL2CPP linkage는 서로 다르다. 한 종류만 검사하고 모두 보장했다고 쓰지 않는다. 서로 다른 Unity 안정 버전이 설치되어 있다면 추가 소비 build를 실행하되, 미설치 버전 지원을 임의 약속하지 않는다.

성능 수치는 source SHA, build type, device/OS, warm-up, sample count, 측정 코드와 함께 기록한다. Fake latency와 실제 store latency를 비교해 SDK 개선이라고 주장하지 않는다. 실제 기기 profiling이 없으면 가능한 로컬 stress 결과와 한계를 쓴다.

## 16. 최종 완료 판정과 보고서

### 16.1 첫 개발 실행의 종료 체크

P00~P11의 모든 Task를 IMPLEMENTED 또는 근거 있는 BLOCKED로 분류하고, 기록을 비워 둔 채 종료하지 않는다. 사용자 설정만 필요한 항목은 **연결할 실제 코드가 이미 존재하는지** 검토한다. 외부 verifier가 TODO이면 WAITING_USER가 아니라 내부 미구현이다.

Task마다 최소 소스 경로·검증 결과·증거 또는 미실행 이유가 있어야 한다. 패키지에는 current source로 만든 바이너리와 manifest가 있어야 하며, 환경 때문에 만들지 못하면 그 artifact를 미생성으로 표시한다. 새 소비 검증 없는 상태를 배포 검증 완료로 쓰지 않는다.

모든 자동 수행 가능 작업이 끝나면 마지막 보고서와 로컬 커밋을 작성한다. 실패가 남았는데 “요청하신 개발을 모두 완료했습니다”라고 보고하지 않는다. 단계별로 사용자를 기다릴 필요는 없지만 실제 오류·권한 제약을 은폐할 권한은 없다.

### 16.2 최종 상태 계산

```text
내부 미구현/실패/계약 누락 존재       → BLOCKED_INTERNAL
필수 로컬 검증 환경 미충족 존재     → IMPLEMENTED_ENV_PENDING
코드·필수 로컬 검증 완료 + 외부대기  → LOCAL_READY_EXTERNAL_PENDING
외부 Sandbox 시나리오도 실제 통과   → SANDBOX_VERIFIED
단순 세션 종료, 할 일 남음           → INTERRUPTED
```

중복 지급·위조 토큰 허용 등 보안상 실패가 존재하면 환경 대기보다 내부 실패를 우선한다. 최종 상태가 좋아 보이도록 검증 suite를 optional로 바꾸지 않는다.

### 16.3 FINAL_REPORT 필수 내용

구현 완료/로컬 검증 완료/미구현/사용자 설정 대기/환경 대기/실패/범위 제외를 분리한다. 각 내용에는 Task ID와 증거를 연결한다. 실제 도구 버전과 실제 실행 명령, 실행된 테스트 수, skipped 사유, generated artifact 경로·checksum·source SHA, 주요 commit 이력, 설계 변경, 보안/운영 한계, 다음 사용자 행동을 포함한다.

포트폴리오 문구는 `구현`, `로컬 검증`, `Sandbox 검증`, `운영 경험`을 혼동하지 않는다. 실제 사용자 규모·게임팀 도입·상용 운영·빌드 개선 수치가 없으면 지어내지 않는다. “SDK 개발·Native Bridge·결제 멱등 처리·재현 가능한 검증” 중 실제로 입증한 것만 README에 쓴다.

마지막 git status의 남은 변경이 사용자의 원래 변경이면 그대로 보존했다는 사실을 적는다. 작업 도중 만든 변경이 남았다면 이유를 적는다. identity 부재로 commit하지 못했다면 커밋 완료라고 쓰지 않는다.

## 17. 사용자가 인증을 마친 뒤의 마무리 절차

`USER_SETUP.md` 순서대로 실제 package/bundle ID·OAuth client ID·개발자 계정·상품·푸시·서명 설정을 적용한다. secret은 Git 밖의 local 파일/환경 변수에서 공급한다. 설정 없는 기능만 선택적으로 enable하며 서로 다른 앱/테스트 환경의 ID를 섞지 않는다.

사용자 준비 후 `verify-external --check-config`로 누락값·파일 존재·ID 정합성만 확인한다. 이후 Android/iOS Native sample의 실제 인증 → 실제 테스트 결제 → 원격 푸시를 확인하고, 그 다음 Unity Android/iOS에서 동일 기능을 확인한다. 문제 범위를 Native와 Bridge로 분리하기 위한 순서다.

실연동 실패 시 새 BUG 항목을 만들고 수정→관련 로컬 회귀→외부 재검증→문서/커밋을 수행한다. 그 전에 완료된 모든 작업을 처음부터 다시 만들지 않는다. 콘솔 설정을 바꿨다는 사용자 설명만으로 실제 기능 PASS를 기록하지 않는다. 실제 실행 결과가 필요하다.

구독·환불 서버 알림·Windows 같은 새 기능은 별도 다음 버전 계획으로 남긴다. 외부 검증 마무리를 새 기능 개발로 끝없이 확장하지 않는다.

## 18. 공식 기술 근거와 재확인 목록

아래 문서는 본 계획의 플랫폼 제약을 확인한 출처다. 조사 기준일은 2026-11-10이다. **선택한 실제 SDK/엔진 버전의 문서와 컴파일 결과가 우선**하며 최신 문서의 예제를 로컬 버전에 그대로 적용하지 않는다. Task 구조·상태명·기본 timeout·상품·DB 구조는 이 프로젝트의 설계 선택이다.

- [S01] Unity, iOS native plug-in/C linkage/Swift export: https://docs.unity.com/en-us/engine/7000.0/manual/platform-specific/iphone/ios-developing/plugins-for-ios/ios-native-plugin-create — Swift `@_cdecl` 예시를 확인하는 참고이며 Unity 7 alpha 도입 지시가 아님. 실제 LTS에서 C ABI/link를 별도 검증한다.
- [S02] Unity, native callback delegates: https://docs.unity3d.com/6000.0/Documentation/Manual/ios-native-plugin-call-back.html
- [S03] Unity, AndroidJavaProxy API: https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AndroidJavaProxy.html — 실행 시 선택 버전의 API와 callback signature를 재확인한다.
- [S04] Android, Credential Manager Sign in with Google: https://developer.android.com/identity/sign-in/credential-manager-siwg
- [S05] Google, ID token server verification: https://developers.google.com/identity/gsi/web/guides/verify-google-id-token — token 검증 원칙 참고. Web cookie/CSRF 예제를 Native 흐름에 그대로 복사하지 않는다.
- [S06] Apple, Verifying a user: https://developer.apple.com/documentation/signinwithapple/verifying-a-user
- [S07] Android, Play Billing security/verification: https://developer.android.com/google/play/billing/security
- [S08] Android, Play Billing integration: https://developer.android.com/google/play/billing/integrate
- [S09] Apple, AppStore.sync: https://developer.apple.com/documentation/storekit/appstore/sync()
- [S10] Apple, Transaction.finish: https://developer.apple.com/documentation/storekit/transaction/finish()
- [S11] Apple, App Store Server Java Library: https://github.com/apple/app-store-server-library-java
- [S12] Apple, Xcode와 Sandbox testing 구분: https://developer.apple.com/documentation/storekit/testing-at-all-stages-of-development-with-xcode-and-the-sandbox
- [S13] Firebase, Android FCM setup/token lifecycle: https://firebase.google.com/docs/cloud-messaging/android/get-started
- [S14] Apple, APNs registration: https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns
- [S15] Unity Mobile Notifications, iOS host APIs: https://docs.unity3d.com/Packages/com.unity.mobile.notifications@2.4/manual/iOS.html — 패키지 버전은 실제 호환 조합에서 고정한다.
- [S16] Firebase Admin SDK setup: https://firebase.google.com/docs/admin/setup
- [S17] Apple, APNs token authentication: https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns
- [S18] Android library/Maven dependencies: https://developer.android.com/studio/projects/android-library
- [S19] Apple, XCFramework bundle: https://developer.apple.com/documentation/xcode/creating-a-multi-platform-binary-framework-bundle
- [S20] Unity UPM Git dependencies: https://docs.unity3d.com/6000.3/Documentation/Manual/upm-git.html
- [S21] OpenAI, AGENTS.md instructions discovery/size: https://developers.openai.com/codex/guides/agents-md/
- [S22] OpenAI, iterative development workflow: https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex

문서에 붙어 있는 URL은 자격증명이 아니다. 브라우저에 로그인되어 있다고 자동으로 외부 계정 설정을 변경할 권한이 생기지 않는다. 이 계획은 외부 인증을 사용자가 마지막에 처리한다는 경계를 유지한다.
