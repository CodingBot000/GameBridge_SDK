# P05-T03 iOS 26.5 StoreKitTest 독립 원인 분리

2026-11-13, 시작 HEAD `6c87900e0db9b7dc1464e2a4162a9b6282ae30bf` 위 미커밋 독립 테스트 소스로 `python3 harness/run-storekit-isolation.py --run-local`을 실행했다. 사용자 Simulator·AVD·DB를 사용하거나 변경하지 않았다. 두 신규 Simulator는 테스트 뒤 shutdown했고 삭제하지 않았다. 전체 Strict는 실행하지 않았다.

## 환경과 범위

- Xcode 26.6 (17F113), XcodeGen 2.46.0, Simulator SDK iOS 26.5. StoreKitTest는 Xcode의 iPhoneSimulator SDK `Developer/Library/Frameworks/StoreKitTest.framework`를 사용했다. SDK header에서 기존 iOS 18 deprecated 경고가 있었으며 실패 원인이라고 판단할 근거는 없다.
- 신규 iPhone 16 arm64 Simulator: iOS 18.6 (22G86) `AC65753D-823D-4977-937B-10E364596CC7`, iOS 26.5 (23F77) `9B124F33-C9C5-4019-B489-4A85F948CE43`.
- UIKit 빈 host와 XCTest만 포함하며 GameBridge SDK·Unity·Backend·PostgreSQL을 연결하지 않는다. `SKTestSession(contentsOf:)`에 XCTest bundle 내 파일 URL을 전달해 생성만 검증한다. 기존 통합 앱의 named/URL·main/background 시험을 반복하지 않았다.
- 최소 설정은 기존 형식에서 상품을 한 개로 줄이고 합성 ID를 사용했다. 기존 설정은 `ios/StoreKit/GameBridge.storekit` 원본을 실행 시 복사한다. 기존 파일과 복사본 SHA-256은 둘 다 `4ead467555cf567cdbdfed14c7f2b7790123ee9f91ccda4d7053b001b9def19d`; 최소 파일 SHA-256은 `5c00da718819481831ca86aa3e6250507e236b135dc3b9b46595bbcc2b488b7c`.
- 각 조합은 별도 `xcodebuild test -only-testing:IsolationTests/SessionTests/<test>`로 1회 실행했다. 테스트 실행 제한 60초, 각 xcodebuild 명령 제한 150초, 병렬 테스트 비활성이다. 실제 스토어 연결·구매·지급은 범위 밖이다.

| Runtime | 설정 | xcodebuild 종료 | XCTest | 결과 |
|---|---|---:|---|---|
| 18.6 | 최소 1상품 | 0 | 1건, 실패·skip 0 | PASS |
| 18.6 | 기존 2상품 | 0 | 1건, 실패·skip 0 | PASS |
| 26.5 | 최소 1상품 | 0 | 1건, 실패·skip 0 | PASS |
| 26.5 | 기존 2상품 | 0 | 1건, 실패·skip 0 | PASS |

Runner 전체 exit 0, 산출물 `artifacts/storekit-isolation-04skqp6v/result.json`과 네 `.xcresult`를 로컬에 보존한다. 각 result bundle의 test count를 확인했고 26.5 기존 구성에서는 `SessionTests/testExistingConfiguration()`의 실제 PASS를 추가 대조했다. 원본 빌드 로그와 simulator 데이터는 Git에 넣지 않는다.

## 해석과 다음 조사

이 조건의 **SDK 없는 독립 XCTest에서는 26.5 timeout이 재현되지 않았다**. 따라서 StoreKitTest 26.5 전체 또는 `.storekit` 내용 자체가 반드시 실패한다고 볼 근거는 없다. 다만 기존 통합 시험의 실패 이력 `artifacts/xcode-process-recovery-na8yq85t/result.json`은 26.5에서 `storekit-session-create` 단계 timeout이었고, 이 결과를 지우거나 PASS로 바꾸지 않는다.

이번 독립 시험은 XCTest가 기동한 UIKit host와 test bundle URL을 사용한다. 기존 시험은 `simctl launch`한 SwiftUI recovery 앱, app bundle 설정, SDK 링크와 별도 테스트 실행 순서를 사용하며, `project.yml`에는 run scheme StoreKit 설정이 선언돼 있다. 직접 `simctl launch`에서 그 scheme 설정이 적용됐는지는 확인하지 않았다. Backend는 기존 runner에 있지만 문제 checkpoint는 client 생성 전이며 그 사실만으로 Backend의 영향 유무를 단정할 수 없다. 테스트 host, launch 경로, bundle 위치, scheme 설정 및 초기화 순서가 함께 달라 원인을 어느 하나로 특정할 수 없다.

후속 우선 조사 한 가지: SDK 없이 **XCTest가 아닌 독립 앱의 simctl launch**와 test host 환경을 같은 설정·runtime에서 비교해 launch/test host 차이를 좁힌다. 이전 통합 named/URL 및 스레드 실험을 재실행하지 않는다. `P05-T03`은 FAIL, `ENV-STOREKIT-26`은 OPEN, 실제 Apple sandbox는 WAITING_USER로 유지한다.

## 독립 앱 `simctl launch` 비교 — 2026-11-13

시작 HEAD `b4b4c376742e77d53c5105f93f2d26bd911d2f5b` 위 미커밋 test-only 변경으로 `python3 harness/run-storekit-standalone.py --run-local`을 실행했다. 동일 UIKit IsolationHost를 Xcode 26.6 (17F113)으로 한 번 빌드하고 SDK·Backend·Unity·PostgreSQL 없이 앱 bundle의 기존 2상품 설정 URL을 `SKTestSession(contentsOf:)`에 전달했다. 원본·복사본·빌드된 bundle의 설정 SHA-256은 모두 `4ead467555cf567cdbdfed14c7f2b7790123ee9f91ccda4d7053b001b9def19d`다. build exit 0; XCTest host에 없는 framework를 강제로 추가하거나 우회하지 않았다. Xcode SDK StoreKitTest header에서 deprecated 경고가 있었으나 원인으로 판단하지 않는다.

| Runtime | 전용 iPhone 16 Simulator | launch | 파일 checkpoint | 실제 판정 |
|---|---|---:|---|---|
| iOS 18.6 (22G86) | `E6A5C1EA-FD72-4773-BC41-A847775D784B` | exit 0 | started, 생성 전, 생성 후 | PASS, timeout 없음 |
| iOS 26.5 (23F77) | `F692C5A6-A4AF-4D38-876D-D97A32B437BA` | exit 0 | started, 생성 전만 존재 | FAIL: 생성 중 프로세스 SIGABRT |

초기 runner는 앱 종료 여부를 검사하지 않아 26.5를 75초 checkpoint timeout으로 기록했다 (`artifacts/storekit-standalone-zu6etuhp/result.json`, 전체 exit 1). 이 원본은 보존한다. 그러나 launch PID 87401에 대한 해당 Simulator의 `IsolationHost-2026-11-13-222922.ips` 진단에서 **SIGABRT / abort 6**을 확인했고, terminate도 이미 종료된 프로세스로 보고했다. faulting thread에는 `StoreKitTest:XCTestLibrary` → `__getXCTestConfigurationClass_block_invoke` → `SKTestSession bundleID` → `_configureWithURL:error:` → `initWithContentsOfURL:error:`가 기록됐다. 따라서 단순 세션 대기 timeout이 아니라 생성 도중 프로세스 종료다.

진단 runner에 프로세스 종료와 실제 대기 timeout 구분을 추가한 후 제한적인 26.5 대조 1회: 새 Simulator `77829A4F-665C-4DF6-8344-6E0512BF5895`, build/launch exit 0, 생성 전 checkpoint 후 프로세스 종료 FAIL / 전체 exit 1, `timedOut=false` (`artifacts/storekit-standalone-6ieup1xl/result.json`). PID 88426의 `IsolationHost-2026-11-13-223415.ips`에서도 SIGABRT와 같은 StoreKitTest 함수 경로를 확인했다. 분류 단위 테스트는 1건 PASS/skip 0이다. 세 신규 Simulator는 모두 shutdown했고 삭제하지 않았다. 원본 crash report에는 환경 정보가 포함되므로 Git에 넣지 않는다.

기존 통합 시험 `artifacts/xcode-process-recovery-na8yq85t/result.json`에 기록된 Simulator `481932FB-B2FD-40EC-826E-701A68B94E41`와 `GameBridgeRecoveryHarness-2026-11-13-170037.ips`의 Simulator UUID가 일치한다. 그 기록도 SIGABRT와 같은 `XCTestLibrary`/`SKTestSession` 함수 경로를 보여준다. 기존 runner의 checkpoint timeout 기록을 삭제하지 않되 해당 시도는 앱 조기 종료를 감지하지 못한 **timeout 보고**였음을 정정한다. 이는 SDK가 없는 독립 앱에서도 같은 유형의 종료가 발생한다는 강한 범위 분리 근거이지, Apple 내부 구현 결함이나 특정 수정법의 증명은 아니다.

직전 독립 XCTest는 18.6·26.5 모두 기존 설정 PASS였고, 이번 앱은 18.6 PASS / 26.5 SIGABRT다. 결과는 **XCTest host와 일반 앱 프로세스에서 StoreKitTest의 XCTest 관련 환경 차이**로 조사 범위를 좁힌다. XCTest 프레임워크나 설정 주입으로 이를 우회하지 않았으며, 해당 지원 여부·구체적인 로딩 실패 원인은 아직 미확정이다. 다음에는 Apple의 StoreKitTest 지원 범위와 XCTest host 의존성을 공식 자료 또는 최소 정적 진단으로 확인한다. P05-T03 FAIL / ENV-STOREKIT-26 OPEN과 실제 Provider WAITING_USER는 유지한다.
