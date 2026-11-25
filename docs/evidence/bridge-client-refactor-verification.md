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
