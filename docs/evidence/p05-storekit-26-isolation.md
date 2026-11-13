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
