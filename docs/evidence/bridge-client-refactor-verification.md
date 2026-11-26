# BridgeFacade와 GameBridgeClient 리팩토링 검증

공개 `v0.1.1-dev`와 로컬 후보 `0.1.2-dev`의 Bridge Protocol은 v1이다. 기준 main은 `6ff2cafa1c54863720ffccd17c2164c30a119bfd`이며 공개 태그는 `e8f2f55c47798cd99afaea1a81e03a01a39d1121`이다. 태그, Release ID·공개 시각, 6개 공개 자산의 크기와 SHA-256을 작업 전후 대조했다.

## 변경과 호환성

Android Google과 Apple/Facebook adapter의 Store 생명주기 구현을 공유하고, Store 인스턴스·상품 매핑·Host·구독·공급자 정리는 각 adapter의 기존 경계에 남겼다. Store 생성 직후 즉시 시작하는 이벤트 수집과 매 접근의 Host attach, 구독 취소 후 close 순서를 fixture로 검증했다. FCM 토큰 획득은 Firebase의 선택 의존성, 권한, 콜백, 취소와 timeout까지 공유한다. Google의 `FIREBASE_HOST` 상세 및 동기 LinkageError 변환과 Social의 기존 예외 전파를 유지했다. Backend 등록 HTTP 호출은 각각의 기존 공급자 client가 수행한다.

Unity의 상태 모델은 같은 `GameBridge.Runtime` assembly의 별도 파일에 있다. 내부 Decoder는 diagnostics와 capability의 필수 필드, strict type과 enum, null 또는 생략 구분, 시간대와 읽기 전용 snapshot을 보존한다. 초기화·종료·요청 세대와 Host 이벤트는 Facade에 남아 있다. [전이 기록](../../contracts/bridge-client-refactor-transition.json)

| 검증 | 결과 |
| --- | --- |
| Android JVM | 후보 Core 35개 중 격리 HTTP 환경을 요구하는 7개 skip·실패 0, Native 47개와 Bridge 17개 skip·실패 0. Store/FCM 특성 및 기존 구매 이벤트·Host Push 시험 포함 |
| Unity 관리 코드 | Android/iOS/Editor/기타 조건부 C# 컴파일, 진단·capability 및 소셜 소비자, Registry/Offline 418 assertion, 수명주기 stress와 iOS Host queue PASS |
| API/ABI | C# 기준과 후보 공개 reflection 결과 383줄 동일. 공개 Maven과 후보의 선정 JVM 클래스 5개 public descriptor 대조, BridgeFacade/BridgeCallback JNI, iOS device arm64 및 simulator arm64/x86_64 5개 GB 심볼과 header 동일 |
| 전이 및 wire | 기준의 원본 소셜/로그아웃/P08/P10 guard와 새 승인 전이 PASS. 신규 양성·음성 8개, 기존 소셜 6개와 Native 전이 8개, Unity GUID, Bridge schema 2개 및 OpenAPI PASS |
| 패키지 | Maven 및 독립 R8 소비 빌드, XCFramework 및 UPM staging 168개, 원본 라이선스와 배포용 checksum 검증. 누락 Maven 전이 JAR, iOS Simulator slice·device ABI 음성 시험 PASS |
| Unity Editor | 6000.5.8f1의 독립 프로젝트에서 Offline/Native 샘플 Import, Offline EditMode 1개 및 재Import GUID 검사 PASS |

Maven·XCFramework·UPM 패키지 소스는 추적 파일이 깨끗한 `7b6430e8afccedb8084e1382a7ab1ec85838fed8`이다. SDK 제품 소스를 수정하지 않는 테스트 fixture 변경 후 실제 Player 소스는 `f42276f595f090b4d8bf94a0f3b145cda8bb3abd`였다. 두 소스의 shipping 입력 diff는 0이다. 후보 staging 매니페스트 SHA-256은 `441cfe72df4b23a55a4474b6cdaa0a7fd32273de191d7b5270d541cd60f6d15b`이다.

| 로컬 아카이브 | SHA-256 |
| --- | --- |
| com.gamebridge.sdk-0.1.2-dev.tgz | `4e1bf57f619a0a11ab2c9ec287b70fed33de620ff7065d32309260564d9060b4` |
| GameBridge-Maven-0.1.2-dev.zip | `ed6c50c9e102414381d4d4f2b5d02f94e342d3fd1e9a428273f6bc9e1cbffe27` |
| GameBridgeNative-0.1.2-dev.xcframework.zip | `2c8b5cf64987c008c67de601ad423aa9d675400a826aa8871ad90553bcb03666` |

## 이전 공개 버전에서 업데이트

두 실행은 같은 staging, Unity 6000.5.8f1, 별도 LOCAL_MOCK DB·role을 사용했다. 시작 앱은 Batch A/B의 공개본과 동일한 SDK 파일을 앱에 탑재한 기존 소비 증거다. 각 앱의 첫 구매 원장 commit 후 proxy가 응답을 한 번 유실했다. 앱·DB 데이터를 유지하며 후보를 덮어 설치한 뒤, 기존 세션과 미완료 구매를 복구했다. 두 번째 동기화의 회수 건수 0과 로그아웃을 확인했고, 각 DB의 순증은 원장 한 건·100코인이었다.

| 실행 | 이전 앱 → 후보 앱 | 결과 |
| --- | --- | --- |
| Android API 34 전용 AVD | 같은 application ID·SHA-256 서명, build 2 → 3. `run-unity-android-mock-restart-e2e.py --previous-apk --candidate-apk` | install -r, 다른 프로세스, 세션·구매 복구, 재동기화·로그아웃 PASS |
| iOS 18.6 전용 Simulator | 같은 bundle ID, build 0 → 1. `run-unity-ios-mock-restart-e2e.py --previous-app` | 새 Xcode Simulator 앱의 signing 검증 및 Meta 동적 framework 4개, 덮어 설치·세션·구매 복구·로그아웃 PASS |

과거 StoreKit 26.5 실패, 전체 Strict, 약한 참조 client 원인 미확정과 플랫폼 실계정의 기존 판정은 각 기존 근거를 따른다. 이 후보 Google 계정 재인증과 실제 Apple/Facebook·FCM/APNs·스토어 거래는 NOT_RUN이다.

두 업데이트 DB를 읽기 전용으로 집계한 결과, 각각 세션 1개, 폐기 1개, 활성 0개였다. 기존 업데이트 fixture는 로그아웃까지만 확인했다. 로그아웃 후 복원 불가와 명시적 shutdown을 단언하는 fixture를 추가했다.

## 추가 Player 검증과 인계 조건

- Android 합성 PII는 APK 빌드 후 `BACKEND_HEALTH_TIMEOUT`, iOS는 Export·Xcode 빌드 후 `SIMULATOR_INSTALL_FAILED`로 첫 실행에서 Player 검증에 도달하지 못했다. 일반 LOCAL_MOCK 업데이트에서 시험 자격값이 로그에 없는 것과 합성 PII fixture 결과는 구분한다.
- 추가 Android 업데이트 빌드는 소유 ADB 확인의 `lsof` 시간제한에 두 차례 걸렸고 새 AVD 부팅도 제한시간을 넘겼다. 기존 업데이트 성공과 보강 단계의 재실행은 각각 기록한다.
- GitHub PR의 동일 HEAD 기본 CI 및 추가 Player 결과를 확인한 뒤 최종 완료를 판정한다.
- Android의 `Version.CURRENT`는 Kotlin 상수다. 이미 이 값을 인라인한 소비자 바이트코드는 재컴파일 전까지 빌드 당시의 버전 문자열을 가질 수 있다.

## 2026-11-26 후속 실제 Player 검증

미완료 시험 다섯 개를 전용 Android API 34 AVD와 iOS 18.6 Simulator에서 순차 실행했다. 후보는 Unity 6000.5.8f1과 로컬 SDK `0.1.2-dev`이며, 다섯 실행의 staging 매니페스트 SHA-256은 위 기록과 일치한다. 합성 PII와 Push 시험은 선행 빌드 증거의 바이너리와 소스를 대조한 뒤 runtime부터 재개했다. 종료 시험은 같은 후보를 탑재한 독립 Player에서 실행했다. 앞서 통과한 덮어 설치·구매 복구 결과는 기존 실행을 근거로 삼았다.

| 시험 | 실제로 관측한 결과 |
| --- | --- |
| Android 합성 PII | `GB_PII_PROBE PASS`, `GB_MOCK_REDACTION PASS` 각 1회, 전체 Unity marker 34개. Backend 검증과 원장 1건·100코인 PASS |
| iOS 합성 PII | `GB_PII_PROBE PASS`, `GB_MOCK_REDACTION PASS` 각 1회, 전체 Unity marker 24개. Backend 검증과 원장 1건·100코인 PASS |
| iOS LOCAL_MOCK Push | `GB_PUSH_RESULT PASS LOCAL_MOCK`. 중복 제거, 백그라운드·포그라운드 전환, 로컬 전송 단절 후 재연결, 등록 해제·로그아웃과 세션 교체 뒤 늦은 콜백 차단 PASS. 재연결 거부 관측 6회, 종료 시 device token 0개 |
| Android 로그아웃 후 복원·종료 | `GB_RF50_LOGGED_IN_SESSION PASS`, `GB_RF50_LOGGED_OUT_RESTORE_BLOCKED PASS`, `GB_RF50_LOGOUT_SHUTDOWN PASS`. `SHUTDOWN` 및 대기 요청 0개. 격리 DB 세션 1개·폐기 1개·활성 0개 |
| iOS 로그아웃 후 복원·종료 | Android와 같은 세 marker PASS. `SHUTDOWN` 및 대기 요청 0개. 격리 DB 세션 1개·폐기 1개·활성 0개 |

아래 경로는 로컬 `artifacts/refactor50/` 기준이다. 각 결과에 기록된 checkout은 tracked-clean이었다. 합성 PII와 Push에 사용한 Player 소스는 `f42276f595f090b4d8bf94a0f3b145cda8bb3abd`, 종료 시험 소스는 `a7c02733b958c99e5c6513d6dce04159107eaa7a`다. 두 소스와 PR 후보의 SDK·Backend·wire 계약 파일을 대조했다. 위 판정은 로컬 실제 실행 결과와 marker 로그를 근거로 한다.

| 시험 | 원본 결과 파일 | 원본 SHA-256 |
| --- | --- | --- |
| Android 합성 PII | `pii-android/artifacts/unity-android-e2e-_nf2ouus/result.json` | `ef02ecac47fb437caae1659616c35b3c05ec8000f0e9a7078201f8981fed63db` |
| iOS 합성 PII | `pii-ios/artifacts/unity-ios-e2e-2fl56ph1/result.json` | `ff0c8062bc5e0711ba23fd10964d1b582e98a4f4546f77a5c16f06695ec8ea73` |
| iOS Push | `push-ios/artifacts/unity-ios-push-crz5_na8/result.json` | `4860a73fe423394d88c364e3d2f04751be57a4a8728b4ccbcb837d9e11377cf9` |
| Android 복원·종료 | `resume50/focused-logout-android/result.json` | `22de8752d82dde587df565a974b9f16bde58c1a085f622c1373b1c0908e5e9a4` |
| iOS 복원·종료 | `resume50/focused-logout-ios/result.json` | `405df6bccb26e4769b7e33790bc63fbc0be8e643777fe57af42a3b53ffc44229` |

합성 PII의 marker는 각 실행 디렉터리의 `unity-test-markers.log`, iOS Push는 `unity-push-markers.log`, 복원·종료는 `markers.log`에 있다. 원본 경로와 판정은 `resume50/verification.json`에 모았다. 위 후속 결과는 초기 Android Backend health timeout, iOS Simulator 설치 실패, Android 소유권 조회 및 AVD 부팅 시간 초과 이후의 성공 기록이다.

## 리뷰 판정

문서50 §11의 로컬 필수 항목은 실제 Player·업데이트 증거, 선정 API/ABI 대조, 전이 가드 및 패키지 검증으로 충족했다. 문서 변경 전 PR HEAD `bc3d81ba45b7b5e6982143d626cb8d7ce4d1934f`의 기본 CI는 5개 모두 성공했다. [문서 변경 전 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45654121957)

`REFACTORING_VERIFIED_FOR_REVIEW` 확정 조건은 PR #18의 현재 HEAD에서 `inventory-contracts`, `backend-postgres`, `android-native`, `swift-ios-simulator`, `basic-ci`가 모두 성공하는 것이다. 확정 판정과 CI 실행 링크는 PR 설명에서 확인할 수 있다. 후보의 실제 계정 인증, 원격 Push, 스토어 거래는 미실행이며 기존 StoreKit 26.5 실패와 전체 Strict 제한은 위 기록을 따른다. [PR #18 및 현재 검사](https://github.com/CodingBot000/GameBridge_SDK/pull/18/checks)
