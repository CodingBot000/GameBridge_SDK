# GameBridge SDK 개발 보고서

## 판정

**BLOCKED_INTERNAL.** P00–P11의 모든 계획 Task를 원장에 등록했으며 개발과 로컬 검증을 진행했다. Unity Android 및 iOS Simulator LOCAL_MOCK 전체 흐름은 검증했으나 전체 제품, 실제 기기와 실제 스토어·푸시 서비스는 검증되지 않았고 내부 미완료도 남았다. 이 문서는 상용 배포 승인이나 sandbox 검증 완료를 뜻하지 않는다. 자세한 Task별 상태와 증거는 [PROGRESS](PROGRESS.md), 실행 이력은 [WORK_LOG](WORK_LOG.md)에 있다.

P11 감사 당시 64개 Task 중 IMPLEMENTED 2개, 나머지는 진행 또는 미착수였다. 실연동 대상 13개 중 PASS는 0개다. 회귀 manifest의 50개 시나리오는 R12·R50 및 인증·구매 synthetic 회귀를 포함해 49개 IMPLEMENTED, 1개 PARTIAL로 전체 통과가 아니다. 이후 원장 갱신에 따른 최신 집계는 PROGRESS가 기준이다.

## 확인한 범위

- Android Kotlin, iOS Swift 및 Unity C# 경계의 계약·fake 테스트와 일부 local-mock HTTP/PostgreSQL 시험을 실행했다. 인증, 구매 중복 지급 방지 및 응답 유실 복구, 푸시 토큰 등록·삭제의 제한된 경로를 확인했다. 실제 제공자 테스트와 구분한다.
- Android emulator Keystore와 iOS simulator Keychain의 인스턴스 재생성 복구를 확인했지만 Unity Android emulator와 iOS Simulator의 LOCAL_MOCK 프로세스 재시작 구매 복구도 확인했다. 실제 기기 복구는 미검증이다.
- Android Maven 산출물의 독립 R8 소비 빌드, iOS static XCFramework의 simulator Swift 소비 링크, UPM staging checksum을 확인했다. 이후 Unity 6000.5.8f1 신규 소비 프로젝트 import·Android IL2CPP APK 및 local-mock Player 전체 경로는 전용 에뮬레이터에서 PASS했다 ([증거](evidence/px-t04-unity-android-local-mock.md)). Unity iOS Simulator의 LOCAL_MOCK 전체 흐름도 확인했으며 실제 스토어는 미검증이다.
- 회귀 하네스의 누락·변이 음성 시험과 로컬 Unity gate를 실행했다. 소스 `e703f43`의 기본 Android/iOS Player, Push 양 플랫폼 및 Unity Editor는 PASS했지만 `artifacts/verify-all-4r3l36i6/summary.md` 전체는 당시 R22/R40 PARTIAL과 기존 P05-T03 FAIL로 FAIL이다 ([증거](evidence/p09-unity-ci-local.md)). 두 Android 최초 안내는 수동으로 닫았다. GitHub Actions 및 실제 제공자는 실행하지 않았다.
- 리팩토링은 하네스 이후 진행했다. baseline API 소스 비교와 별도 C# consumer 컴파일을 확인했으나 바이너리 ABI 및 Unity 실행을 보장하지 않는다. 독립 .NET fake 수명주기 100회 측정 p50 0.1467ms, p95 0.2125ms는 Unity나 기기 성능 수치가 아니다.

Offline Demo는 별도 staged UPM의 Package Manager Sample API import 후 새 테스트 프로젝트의 Unity Editor Play에서 fake 로그인·상품·구매 callback을 확인했다 ([증거](evidence/p08-offline-sample-editor.md)). Native Demo는 양 플랫폼별 신규 프로젝트에서 Sample API import 후 Android/iOS LOCAL_MOCK Player의 설정·모의 구매 callback을 확인했다 ([Android](evidence/p08-native-demo-android.md), [iOS](evidence/p08-native-demo-ios.md)). iOS 첫 export는 sample asmdef 누락으로 실패했으며 수정 후 통과했다. Package Manager GUI 클릭, 실제 포인터·화면 렌더링은 별도다.

## 남은 내부 작업과 실패

| 항목 | 상태 및 영향 |
|---|---|
| BUG-013 | XCODE_STOREKIT 격리 fake 서버 지급 및 Native/Unity bridge를 구현했다. iOS 18.6 상품 조회와 일회성 synthetic 지급·finish를 확인했으나, 추가 시험에서 동일 미완료 거래의 JWS가 바뀌어 중복 지급 위험을 발견했다. 완료 후 연속 구매의 고정 필드는 한 시험에서 구분됐지만 재시작 복구의 유일성은 미확인이다. iOS 18 이상과 host 소모품 이력 설정, 거래 후보 단일성 및 durable attempt를 요구하도록 보강했다. local DB 응답 유실과 Keychain 인스턴스 재생성 복구는 통과했으며 전용 iOS 18.6 simulator 앱 재시작 시험에서 journal 재생성 실패를 재현한 뒤 중복 거래 방지 수정으로 재시험 PASS (`artifacts/xcode-process-recovery-f_w2fsya`). 실제 기기·Unity 실행은 미검증이다. iOS 26.5 StoreKit 시험은 Code 3으로 실패했다. |
| BUG-014 | LOCAL_MOCK Unity Android emulator·iOS Simulator 전달 및 lifecycle을 확인했다. 실제 기기·FCM/APNs와 iOS OS 전체 네트워크 차단은 미검증이다. |
| BUG-015 | Native 진단 ring의 Unity 비동기 조회는 Android 및 iOS Simulator LOCAL_MOCK Player에서 확인했다. 다른 모드와 실제 기기는 미검증이다. |
| BUG-009 | LOCAL_MOCK Unity Android emulator와 iOS Simulator에서 응답 유실 후 프로세스 재시작 복구를 확인했다. 실제 스토어 및 실기기 복구는 남았다. |
| P09 | 현재 R40 1개 부분 검증, R12 독립 fake·R50 하네스 음성 및 인증·구매 synthetic 회귀 구현; Unity Editor scene/domain reload 시험과 양 플랫폼 LOCAL_MOCK Player를 별도로 실행했다. 최신 로컬 strict의 Editor 및 Push 양 Player는 PASS했지만 전체 gate는 실패다. |

## 환경 및 사용자 설정

과거 Unity 라이선스 오류(ENV-002)는 활성화 후 해소됐고 Android local-mock Player는 통과했다. 계획된 6.3 LTS 확인(ENV-001), 실제 기기 및 나머지 Unity 시나리오는 별도다. iOS 26.5 simulator의 StoreKit local 시험은 실패(ENV-STOREKIT-26)했다. 이후 별도 앱 재시험도 SKTestSession 생성에서 timeout (`artifacts/xcode-process-recovery-p8qyld6o`)이었으며 동일 계측의 iOS 18.6 대조는 PASS였다. 실제 Google/Apple 인증, 스토어, FCM/APNs의 계정·앱 등록·서명 및 기기 준비는 [USER_SETUP](USER_SETUP.md)에 정리했다. `bash scripts/verify-external.sh --check-config`는 설정 형태만 확인하며 실연동 테스트가 아니다.

## 로컬 산출물

[산출물 manifest](evidence/p11-artifact-manifest.json)는 실제 파일별 SHA-256과 크기를 기록한다. 산출물은 Git에 포함되지 않는 로컬 개발 결과이며 공개 release가 아니다. P10 빌드는 `d02b8ed`와 당시 미커밋 P10-T04 변경을 사용했고 해당 변경은 `3bf8d0a`에 커밋됐다. 깨끗한 checkout에서 재현한 빌드라고 주장하지 않는다.

| 산출물 | 경로 | 확인 범위 |
|---|---|---|
| Android Maven | `artifacts/maven-p10-20261111-b` | 별도 소비자 R8 build |
| iOS XCFramework | `artifacts/ios-package-p10-20261111-a/GameBridgeNative.xcframework` | simulator Swift link, device C ABI symbol |
| Unity UPM staging | `artifacts/upm-staging-p10-20261111-a` | checksum 및 build hook 시험; Unity import 미실행 |

진단 연결 이후 `52f60f7` 소스 기준 새 산출물은 `artifacts/maven-diag-20261111`, `artifacts/ios-diag-20261111/GameBridgeNative.xcframework`, `artifacts/upm-diag-20261111`에 생성했다. Android R8 consumer 빌드와 UPM checksum은 통과했고 Unity import는 실행하지 않았다. 파일별 해시는 [새 manifest](evidence/diagnostics-artifact-manifest.json)에 있다.

현재 소스 `10e2a3c` 기준 재생성 산출물은 `artifacts/maven-current-20261111`, `artifacts/ios-current-20261111/GameBridgeNative.xcframework`, `artifacts/upm-current-20261111`이다. Android R8 consumer 빌드, iOS simulator Swift link·device symbol, UPM checksum을 확인했다. Unity import 및 실제 기기 실행은 미검증이다. [현재 산출물 해시](evidence/current-artifact-manifest.json)를 참조한다.

최신 재생성 산출물은 `artifacts/maven-final-20261111`, `artifacts/ios-final-20261111/GameBridgeNative.xcframework`, `artifacts/upm-final-20261111`이며 source `6a3fea5`에서 빌드했다. Android R8 consumer, iOS simulator Swift link와 device symbol, UPM 체크섬을 확인했다. [최신 해시 목록](evidence/final-artifact-manifest.json)을 참조한다. Unity import·실기기 검증은 미실행이다.

XCFramework arch·C ABI 선검사를 적용해 다시 staging한 최신 UPM은 `artifacts/upm-validated-20261111`이며 [파일별 해시](evidence/validated-upm-manifest.json)가 있다. Unity import는 미실행이다.

최신 제품 소스 `2bc9d77`에서 Android Maven `artifacts/maven-2bc9d77`, iOS XCFramework `artifacts/ios-2bc9d77/GameBridgeNative.xcframework`, UPM staging `artifacts/upm-2bc9d77`을 재생성했다. Android R8 consumer, iOS arch별 C ABI 및 UPM checksum은 통과했다. [산출물 해시](evidence/artifacts-2bc9d77.json); Unity import 및 실기기는 미실행이다.

최신 iOS 수정 반영본은 source `e9b64fb`의 `artifacts/ios-e9b64fb/GameBridgeNative.xcframework`, `artifacts/upm-e9b64fb`이며 [파일별 SHA-256](evidence/artifacts-e9b64fb.json)을 기록했다. Android 트리는 `2bc9d77` 이후 변경이 없어 해당 Maven R8 consumer 산출물을 재사용했다. iOS arch별 C ABI, arm64 simulator 독립 Swift consumer link 및 UPM checksum은 통과했고 Unity import·실기기는 미실행이다.

## 주요 이력과 재개

P09 하네스는 `e0afb97`, `196ae97`, `7770943`, `02005a4`, `864d2b6`, `35f1912`, `a93cf52` 등에 기록됐다. P10 리팩토링·호환성은 `36db140`, `e689dd7`, `d02b8ed`, `3bf8d0a`, P11 감사·설정 점검은 `31b683c`, `35bf2bd`에 기록됐다. 이후 문서 커밋은 `git log`에서 확인한다.

다음 개발은 BUG-013과 P09 미완성 시나리오를 해결하고 BUG-014·015 실제 Unity 검증을 진행하며 각 범위의 검증을 추가하는 것이다. 사용자 설정이 준비되면 USER_SETUP의 해당 항목에서 실제 플랫폼 검증을 별도로 실행한다. 자동 push, 공개 배포와 스토어 업로드는 수행하지 않았다.


## 후속 변경 — Unity Android LOCAL_MOCK E2E 재검증 준비

후속 브랜치에서 PX-T04 Unity Android Player 검증 Runner, PX-T05 Native-only 실행 환경 가변화, PX-T06 공개용 증거 Exporter 및 오프라인 검사 코드를 추가했다. 이 변경은 기존 P00~P11 전체 완료 또는 실연동 완료를 의미하지 않는다. 그 후속 브랜치 작업 당시 변경된 Runner의 Unity 실행·Android 기기 시험 및 GitHub Actions는 **NOT_RUN**이었다. 이후 로컬 Unity Player 검증은 위에 별도 기록했으며 GitHub Actions는 여전히 NOT_RUN이다.

기존 PX-T03 Kotlin Bridge → 로컬 Backend 1건/100코인 시험은 별도의 이전 실행 결과다. 변경된 코드를 clean checkout에서 재실행한 성공 근거 없이 그 결과를 새로운 코드의 PASS로 이전하지 않는다. 실제 실연동 대상 13건의 WAITING_USER 및 프로젝트 BLOCKED_INTERNAL 판정은 유지한다.

당시 2026-11-12 Android Maven·iOS XCFramework·UPM staging은 `f1e12b6` 제품 소스로 새로 생성했다. UPM 110개 파일 checksum, Android 독립 R8 consumer, iOS arch/C ABI 및 0.1.0-dev 버전을 확인했다. Unity Android Player E2E는 source `c58b4a6`의 clean tracked tree와 동일한 staged Unity SDK 소스로 실행해 PASS했으며 첫 전체화면 안내는 수동으로 닫았다. 해당 Android 실행 당시 실제 Google 로그인·스토어 및 Unity iOS는 NOT_RUN이었다. 이후 iOS LOCAL_MOCK 결과는 다음 항목에 기록한다.

2026-11-12 Unity iOS 18.6 Simulator ARM64에서 Unity C# → Swift C ABI → LOCAL_MOCK Backend/PostgreSQL 전체 흐름이 PASS했다 ([증거](evidence/px-t07-unity-ios-local-mock.md)). 무서명 실행은 로그인에서 실패했고 성공 실행은 로컬 ad-hoc Simulator 서명을 사용했다. 실제 Apple 로그인·스토어 결제·APNs 및 실기기는 미검증이다.

2026-11-12 Unity Android emulator 및 iOS Simulator에서 LOCAL_MOCK Push 등록·수신·중복 억제·main-thread·background/foreground·연결 복구·A→B 세션 전환 및 별도 process 종료/pending 복구를 검증했다 ([Android](evidence/px-t08-unity-android-mock-push.md), [iOS](evidence/px-t12-unity-ios-mock-push.md)). 늦은 이전-session callback은 test-only 합성 주입이며 iOS 연결 단절은 test-only TCP proxy로 재현했다. 실제 FCM/APNs, 실제 기기 및 실제 원격 지연 callback은 NOT_RUN이다. Android/iOS 인증·구매 LOCAL_MOCK Player 회귀도 별도 source에서 각각 PASS했다.
