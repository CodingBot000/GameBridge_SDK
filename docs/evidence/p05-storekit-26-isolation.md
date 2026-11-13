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

## XCTest 구매·pending 비교 — 2026-11-14

시작 HEAD `824fa4d340e3659f09af5824971f3d805de2abab` 위에 test-only checkpoint와 상품 ID 관측을 미커밋 상태로 적용하고 기존 `GameBridgeStoreKit` scheme을 사용했다. 비교에 사용한 `XcodeStoreKitPurchaseTests.swift`의 SHA-256은 `ff11d10179bffdbe9f395a76f8c23879f038be291ca7b6e84feae8473d2294b5`다. 실행 시 `sourceTrackedDirty=true`는 test-only 변경과 진행 문서 때문이며 제품 Provider는 변경하지 않았다. Xcode 26.6 (17F113), 새 iPhone 16 Simulator에서 각 XCTest를 순차 실행하고 `.xcresult`를 보존했다. `SKTestSession`은 XCTest 내부에서 생성하며 실제 Apple sandbox와 외부 결제는 사용하지 않고 Backend는 `URLProtocol` fake 응답이다.

| Runtime | XCTest | xcodebuild | XCTest 결과 | 마지막 단계 |
|---|---|---:|---|---|
| 26.5 (23F77) | testLocalVerifiedPurchaseReceivesFakeGrantAndFinishes | 65 | 1건 실패, skip 0 | session·store start 후 직접 상품 조회 빈 목록, 원래 구매에서 `PRODUCT_NOT_FOUND` |
| 26.5 (23F77) | testAskToBuyPendingNeverRequestsGrant | 65 | 1건 실패, skip 0 | session·store start 후 직접 상품 조회 빈 목록, 원래 구매에서 `PRODUCT_NOT_FOUND` |
| 18.6 (22G86) | testLocalVerifiedPurchaseReceivesFakeGrantAndFinishes | 0 | 1건 PASS, skip 0 | fake grant, unfinished 0, 재구매·복구 complete |
| 18.6 (22G86) | testAskToBuyPendingNeverRequestsGrant | 0 | 1건 PASS, skip 0 | pending, fake grant 미호출, complete |

결과 `artifacts/storekit-xctest-comparison-jryw7wv_/result.json` 및 각 `.xcresult`는 로컬에 보존했다. Runner는 26.5 실패로 exit 1이다. 26.5의 두 건은 XCTest에서 포착된 `SdkFailure(PRODUCT_NOT_FOUND)`이며 timeout이나 session SIGABRT는 아니다. 구매, fake grant·finish 또는 pending 후속에 도달하지 못했으므로 해당 단계는 PASS가 아니다. 18.6 최종 checkpoint의 빈 `productIDs`는 후속 checkpoint의 기본값으로 실제 조회 결과를 뜻하지 않는다. 26.5의 `purchase-and-grant-before` / `purchase-before`에 기록된 빈 배열만 직접 조회 실측값이다. Runner의 이후 출력은 다른 단계에서 `null`을 기록해 혼동을 막도록 보정했다.

첫 실행 `artifacts/storekit-xctest-comparison-l5tx8137`에서는 추가한 `store.products()`가 두 상품을 모두 요구해 26.5가 추가 전제에서 실패했다. 원래 구매 경로와 분리하기 위해 추가 전제를 제거하고 직접 조회 ID만 관측하도록 좁혀 제한적으로 재비교했다. 두 시도 모두 18.6 구매·pending PASS, 26.5 상품 미조회 FAIL이었다. 총 4대의 신규 Simulator는 shutdown하고 보존했다. 원본 로그·Xcode 생성물·Simulator 데이터는 커밋하지 않는다.

26.5 XCTest에서는 독립 세션 생성에 이어 GameBridge XCTest의 session 생성과 store start에도 도달하지만 이번 상품 조회 이후 실패했다. 기존 `GameBridgeStoreKit` scheme은 LaunchAction에 StoreKit 설정을 선언하고 생성된 TestAction에는 같은 명시 참조가 보이지 않는다. session과 scheme의 상호작용 또는 26.5 runtime 차이 중 무엇이 빈 결과에 기여했는지는 미확정이며 SDK 제품 결함이나 Apple 내부 원인으로 단정하지 않는다. 일반 앱 SIGABRT의 기존 기록을 지우지 않고 P05-T03 FAIL / ENV-STOREKIT-26 OPEN / 실제 Apple sandbox WAITING_USER를 유지한다. 다음 후보는 XCTest TestAction에서 StoreKit configuration 활성 상태를 보호 우회 없이 독립 확인하는 것이다.

## SDK 없는 XCTest 상품 조회 비교 — 2026-11-14

[Apple TN3185](https://developer.apple.com/documentation/technotes/tn3185-troubleshooting-in-app-purchases-availability-in-xcode)는 Xcode 로컬 StoreKit에서 상품 미조회 시 활성 configuration의 product ID와 Load Products 오류 시뮬레이션을 확인하도록 안내한다. 현재 `GameBridge.storekit`의 ID는 `coins_100`, `premium_unlock`이며 독립 XCTest와 기존 GameBridge XCTest의 조회 ID와 일치한다. 설정 JSON에는 Load Products failure를 나타내는 명시적 failure/error 키가 없으나, 이 사실만으로 각 테스트 프로세스의 실제 활성 설정 상태까지 확인한 것은 아니다.

`ios/Framework/project.yml`을 바탕으로 새로 생성한 `GameBridgeStoreKit.xcscheme`을 XML로 대조했다. LaunchAction의 StoreKit 참조는 `../../../StoreKit/GameBridge.storekit`이며 TestAction은 `GameBridgeSample.app`을 host로, `GameBridgeStoreKitTests.xctest`를 테스트 대상으로 지정한다. TestAction에 별도 StoreKit 참조는 없지만, 이것만으로 잘못된 설정이나 미지원 속성이 필요하다고 판단하지 않았다. 직전 GameBridge 테스트 빌드의 `.xctest/GameBridge.storekit` 사본과 원본은 SHA-256이 같았다.

시작 HEAD `49a25469e351661c8ed52225e879427bc1ea28a1` 위 미커밋 test-only 코드를 적용해 `python3 harness/run-storekit-isolation-products.py --run-local`을 실행했다. `SessionTests.swift` SHA-256 `405c8de805a50a376c254ed24465982d7b71dcfcf1d6fb676e0714f91d8288e4`, 기존 설정 원본과 독립 프로젝트 복사본 SHA-256 `4ead467555cf567cdbdfed14c7f2b7790123ee9f91ccda4d7053b001b9def19d`. `sourceTrackedDirty=true`는 test-only 코드와 진행 문서 변경이다. SDK·Unity·Backend·PostgreSQL을 연결하지 않았고 구매·지급·finish·pending은 실행하지 않았다.

| 새 iPhone 16 Simulator | 세션 생성 | `Product.products(for:)` 반환 ID | XCTest / 종료 |
|---|---|---|---|
| iOS 26.5 (23F77), `732DC58D-D198-49A8-A2B3-9D28EEAB7331` | PASS | `[]` — 두 상품 미조회 | 1건 실패·skip 0, xcodebuild 65 |
| iOS 18.6 (22G86), `DA2D5013-6AAD-4548-A0C1-73DC8EFBB84E` | PASS | `coins_100`, `premium_unlock` | 1건 PASS·skip 0, xcodebuild 0 |

독립 runner 전체 exit 1; 정제된 결과와 두 xcresult 위치는 `artifacts/storekit-isolation-products-dwknj5y4/result.json`. 26.5 assertion은 예외 없이 반환된 빈 집합과 기대 ID 집합이 달랐다는 실패다. 이전 GameBridge `.xcresult`의 26.5 두 시험은 그 빈 조회 이후 구매 경로가 `SdkFailure(PRODUCT_NOT_FOUND)`를 던졌다. 이전의 일반 앱 `SIGABRT`는 별도 실행 경로이며 이번에 재실행하지 않았다. 새 Simulator 둘은 shutdown했고 삭제하지 않았다. 실제 Apple sandbox 계정·credential이나 원격 결제는 사용하지 않았다. StoreKit의 내부 네트워크 경로는 별도로 캡처하지 않아 외부 요청 발생 여부까지 단정하지 않는다.

**결론:** 같은 기존 설정과 SDK 없는 XCTest에서도 18.6은 두 상품을 반환하고 26.5는 빈 목록을 반환해 런타임별 차이가 재현됐다. 이는 GameBridge SDK의 상품 mapping 코드만으로 설명되지 않는다는 근거다. 그러나 실제 활성 configuration이나 Xcode/StoreKitTest와 runtime의 상호작용은 아직 확인되지 않아 Apple 내부 결함이나 특정 scheme 수정으로 단정하지 않는다. 다음 한 작업은 새 격리 테스트에서 공식 지원되는 설정 활성화 경로와 실제 활성 configuration을 확인하는 것이다. `P05-T03 FAIL`, `ENV-STOREKIT-26 OPEN`, 실제 Apple sandbox `WAITING_USER` 및 P09 PARTIAL을 유지한다. 원본 로그·`.xcresult`·Simulator 데이터는 Git에 포함하지 않는다.
