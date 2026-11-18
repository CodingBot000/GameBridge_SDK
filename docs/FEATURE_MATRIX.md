# 구현·호출 경로와 실제 범위

> 문서37의 최신 소셜 확장 상태·검증은 [SOCIAL_AUTH_HANDOFF](SOCIAL_AUTH_HANDOFF.md)를 따른다. 아래 이전 포트폴리오 snapshot과 실Provider 검증을 구분한다.


이 표는 기능을 찾기 위한 현재 지도입니다. 기존64 Task의 별도 상태는 [PROGRESS](PROGRESS.md), 포트폴리오 종료 판정은 [FINAL_REPORT](FINAL_REPORT.md)를 따릅니다.

| 기능 | 공개 진입점·실제 구현 | 확인한 범위 | 남은 범위 |
| --- | --- | --- | --- |
| 초기화·종료·상태 | `GameBridgeSdk`/`GameBridgeClient`, Native coordinator·BridgeFacade/Swift C ABI | Core/managed·실제 양 Player·C ABI·Player100cycle | first app init·CPU blocking·weak1 root 미확정 |
| 로그인·세션 | `SignInAsync/RestoreSessionAsync/SignOutAsync`, Native HTTP/storage·Backend session/identity | LOCAL_MOCK Player·test key/synthetic·refresh/session 회귀 | 실 Google/Apple와 모든 세션/실기기 조합 |
| 상점·지급·복구 | `GetProductsAsync/PurchaseAsync/GetEntitlementsAsync/SyncPurchasesAsync`, Native store adapters·Backend verifier/원장/finalizer | local 구매/잔액·원장1/100·TC 변이복원·LOCAL_MOCK 복구 증거 | 실스토어·StoreKit 기존 실패/환경 위험·일부 복구 조건 |
| Push 권한·등록·해제 | facade Push API, AndroidPushHostAdapter/IosPushHostAdapter·Native backend registration | mocked 권한·simulated 등록/삭제·OS 조건별 기존 시험 | 실 token·FCM/APNs·실기기 |
| Push 수신·열기 | `PushReceived/PushOpened/PushTokenChanged`, Native/host forwarding·PushRouter | LOCAL_MOCK 양 Player의 dedupe/main thread/session·연결 복구 | 실제 notification tap·remote·모든 OS/lifecycle |
| 설정·진단·PII | `GetServiceConfigAsync/GetDiagnostics/GetNativeDiagnosticsAsync`, cache/maintenance/typed ring·정제 오류 | Native/fake/HTTP·Player PII/진단 | 실제 운영 보안 심사·모든 장애 시나리오 |
| 샘플·설치 | NativeDemo/OfflineDemo, Compose/SwiftUI sample, Gradle/Xcode hook | 새 양 Unity 소비·Native sample build·프로그램 방식 demo callback | 실제 사용자 포인터/렌더링·상용 UX 검증 |
| 패키지·API·계약 | Maven/AAR/XCFramework/UPM, public API/Bridge schema/HTTP OpenAPI |147 checksum·선정JVM4/C ABI4·R8/Swift·OpenAPI24 성공 구조 | 모든 ABI/Unity/OS·SSE/Map 세부 기계 검사 |

주요 소스 연결은 [ENGINEERING_NOTES](ENGINEERING_NOTES.md), 재현 명령과 source별 증거는 [COMPATIBILITY](COMPATIBILITY.md)에 모았습니다. 과거 GUI/CLI/Player/StoreKit/Provider의 범위를 한 개의 PASS로 합치지 않습니다. 이 표로 원장의 PARTIAL/FAIL을 일괄 승격하지 않습니다.

## 문서37 소셜 확장 B

Android Facebook Classic / iOS Facebook Limited·Classic: IMPLEMENTED, Fake/Contract PASS, 실제 로그인 WAITING_USER. 기존 Android Google/iOS Apple/LOCAL_MOCK 유지.

## 문서37 최종 플랫폼 지원 (기존 동결 표보다 우선)

| 경로 | 구현/Fake·계약 | Native/패키지 | 실제 계정 |
| --- | --- | --- | --- |
| iOS Google9.2.0 | IMPLEMENTED/PASS | device/sim XCF·binary consumer·UPM PASS | WAITING_USER |
| Android Facebook18.3.0 | IMPLEMENTED/PASS | Maven·Meta포함R8 consumer PASS | WAITING_USER |
| iOS Facebook18.1.1 | IMPLEMENTED/PASS | device/sim XCF·binary consumer PASS (공식 local SDK cache) | WAITING_USER |
| Android Apple 웹 | IMPLEMENTED/PASS | Android Native/JNI·Maven/R8·UPM PASS | WAITING_USER |

새 Unity Player와 실기기 OAuth UI/복귀 시험 NOT_RUN. Meta 기본원격SPM download DEFERRED_ENV, 공식 SHA/codesign 검증 cache만 사용. 기존64 Task·포트폴리오 동결 snapshot은 이 확장의 실연동 근거가 아니다.
