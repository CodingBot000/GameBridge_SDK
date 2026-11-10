# GameBridge SDK 개발 보고서

## 판정

**BLOCKED_INTERNAL.** P00–P11의 모든 계획 Task를 원장에 등록했으며 개발과 로컬 검증을 진행했다. 전체 제품, Unity 통합 및 실제 스토어·푸시 서비스는 검증되지 않았고 내부 미구현도 남았다. 이 문서는 상용 배포 승인이나 sandbox 검증 완료를 뜻하지 않는다. 자세한 Task별 상태와 증거는 [PROGRESS](PROGRESS.md), 실행 이력은 [WORK_LOG](WORK_LOG.md)에 있다.

P11 감사 당시 64개 Task 중 IMPLEMENTED 2개, 나머지는 진행 또는 미착수였다. 실연동 대상 13개 중 PASS는 0개다. 회귀 manifest의 50개 시나리오는 47개 PARTIAL, 3개 NOT_IMPLEMENTED로 전체 통과가 아니다. 이후 원장 갱신에 따른 최신 집계는 PROGRESS가 기준이다.

## 확인한 범위

- Android Kotlin, iOS Swift 및 Unity C# 경계의 계약·fake 테스트와 일부 local-mock HTTP/PostgreSQL 시험을 실행했다. 인증, 구매 중복 지급 방지 및 응답 유실 복구, 푸시 토큰 등록·삭제의 제한된 경로를 확인했다. 실제 제공자 테스트와 구분한다.
- Android emulator Keystore와 iOS simulator Keychain의 인스턴스 재생성 복구를 확인했지만 실제 기기 프로세스 종료·Unity player 복구는 확인하지 않았다.
- Android Maven 산출물의 독립 R8 소비 빌드, iOS static XCFramework의 simulator Swift 소비 링크, UPM staging checksum을 확인했다. Unity 신규 프로젝트 import 및 IL2CPP는 실행하지 않았다.
- 회귀 하네스가 누락된 증거, 시나리오 및 중복 콜백 guard 제거를 감지하는 부정 시험을 실행했다. push 전달 미구현과 미완성 시나리오 때문에 전체 검증은 통과하지 않았다. 마지막 strict 집계는 `artifacts/verify-all-g_lqddbb/summary.md`에 있으며 일부 opt-in 환경은 미실행이었다. CI 설정은 로컬 점검만 했으며 원격 실행하지 않았다.
- 리팩토링은 하네스 이후 진행했다. baseline API 소스 비교와 별도 C# consumer 컴파일을 확인했으나 바이너리 ABI 및 Unity 실행을 보장하지 않는다. 독립 .NET fake 수명주기 100회 측정 p50 0.1467ms, p95 0.2125ms는 Unity나 기기 성능 수치가 아니다.

## 남은 내부 작업과 실패

| 항목 | 상태 및 영향 |
|---|---|
| BUG-013 | XCODE_STOREKIT의 서버 지급 및 Unity 전체 경로 미구현. simulator StoreKit 시험도 Code 3으로 실패했다. |
| BUG-014 | LOCAL_MOCK 개발 push 응답은 SIMULATED이나 Backend에서 client까지 전달하는 경로가 미구현이다. |
| BUG-015 | Native 진단 ring의 전체 snapshot이 Unity 공개 경계에 연결되지 않았다. |
| BUG-009 | 응답 유실 복구의 실제 기기 프로세스 재시작 및 Unity player 검증이 남았다. |
| P09 | 3개 시나리오 미구현, 나머지 부분 검증; Unity lane 미구현. strict 전체 gate는 성공이 아니다. |

## 환경 및 사용자 설정

Unity Editor 라이선스 오류(ENV-002)와 계획된 버전 확인(ENV-001)으로 Unity import/player 검증이 보류됐다. iOS 26.5 simulator의 StoreKit local 시험은 실패(ENV-STOREKIT-26)했다. 실제 Google/Apple 인증, 스토어, FCM/APNs의 계정·앱 등록·서명 및 기기 준비는 [USER_SETUP](USER_SETUP.md)에 정리했다. `bash scripts/verify-external.sh --check-config`는 설정 형태만 확인하며 실연동 테스트가 아니다.

## 로컬 산출물

[산출물 manifest](evidence/p11-artifact-manifest.json)는 실제 파일별 SHA-256과 크기를 기록한다. 산출물은 Git에 포함되지 않는 로컬 개발 결과이며 공개 release가 아니다. P10 빌드는 `d02b8ed`와 당시 미커밋 P10-T04 변경을 사용했고 해당 변경은 `3bf8d0a`에 커밋됐다. 깨끗한 checkout에서 재현한 빌드라고 주장하지 않는다.

| 산출물 | 경로 | 확인 범위 |
|---|---|---|
| Android Maven | `artifacts/maven-p10-20261111-b` | 별도 소비자 R8 build |
| iOS XCFramework | `artifacts/ios-package-p10-20261111-a/GameBridgeNative.xcframework` | simulator Swift link, device C ABI symbol |
| Unity UPM staging | `artifacts/upm-staging-p10-20261111-a` | checksum 및 build hook 시험; Unity import 미실행 |

## 주요 이력과 재개

P09 하네스는 `e0afb97`, `196ae97`, `7770943`, `02005a4`, `864d2b6`, `35f1912`, `a93cf52` 등에 기록됐다. P10 리팩토링·호환성은 `36db140`, `e689dd7`, `d02b8ed`, `3bf8d0a`, P11 감사·설정 점검은 `31b683c`, `35bf2bd`에 기록됐다. 이후 문서 커밋은 `git log`에서 확인한다.

다음 개발은 BUG-013, BUG-014, BUG-015와 P09 미완성 시나리오를 해결하고 각 범위의 검증을 추가하는 것이다. 사용자 설정이 준비되면 USER_SETUP의 해당 항목에서 실제 플랫폼 검증을 별도로 실행한다. 자동 push, 공개 배포와 스토어 업로드는 수행하지 않았다.
