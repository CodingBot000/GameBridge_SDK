# 기능별 구현·검증 현황

> **기준:** [PR #4 — 소셜 인증 확장](https://github.com/CodingBot000/GameBridge_SDK/pull/4)과 [PR #5 — iOS Meta Embed 수정](https://github.com/CodingBot000/GameBridge_SDK/pull/5)을 `main`에 통합한 개발용 SDK `0.1.0-dev`. **코드 구현, Fake 테스트, Unity LOCAL_MOCK Player 실행, 실제 Provider 로그인은 서로 다른 판정**입니다.

## 실제 확인한 기능

| 기능 | 공개 API·구성 | 확인된 범위 | 아직 확인하지 않은 범위 |
| --- | --- | --- | --- |
| 초기화·세션 | `GameBridgeSdk`, `SignInAsync`, `RestoreSessionAsync`, `SignOutAsync` | Android/iOS Unity LOCAL_MOCK Player, Native·Backend 세션/회귀 | 실제 Google·Apple·Facebook OAuth 세션 |
| 상품·구매·재화 | `GetProductsAsync`, `PurchaseAsync`, `GetEntitlementsAsync`, `SyncPurchasesAsync` | LOCAL_MOCK Player→Backend→PostgreSQL 원장 **플랫폼별 1건/100코인**; 기존 멱등·복원 테스트 | 실제 Google Play/Apple Sandbox 거래, 일부 StoreKit 문제 |
| 푸시 | `RequestPushPermissionAsync`, `RegisterPushAsync`, `UnregisterPushAsync`, `PushReceived/Opened` | Host adapter·Native/Mock 등록·수신·중복 억제의 선정 기존 시험 | FCM/APNs 실제 원격 전달·실기기 |
| 설정·진단 | `GetServiceConfigAsync`, `GetStatus`, `GetCapabilities`, `GetDiagnostics` | Native·Fake/HTTP·선정 Player 진단, 정제 검사 | 운영 수준의 전체 장애·PII 감사 |
| 샘플·패키지 | NativeDemo/OfflineDemo, Android Maven/AAR, iOS static XCFramework, Unity UPM | R8·Swift 소비 빌드, 새 UPM **147개 checksum**, 양 플랫폼 LOCAL_MOCK Player | 상용 배포/다수 Unity·OS 조합/실계정 Host UI |

## 플랫폼별 소셜 인증

| Provider | Android | iOS | 실제 계정 검증 |
| --- | --- | --- | --- |
| Google | 기존 Credential Manager·Backend ID Token 검증 구현 | GoogleSignIn **9.2.0**, custom nonce 구현·Fake/계약 PASS | 두 플랫폼 모두 **WAITING_USER** |
| Apple | 웹 OAuth·Custom Tabs·서버 code 교환 구현·보안 테스트 PASS | 기존 AuthenticationServices 구현 | 두 플랫폼 모두 **WAITING_USER** |
| Facebook | Meta **18.3.0** Classic, Backend token debug 검증 구현 | Meta **18.1.1** Limited/Classic·JWT 검증 분리 구현 | 두 플랫폼 모두 **WAITING_USER** |
| 개발용 Mock | LOCAL_MOCK Player PASS | LOCAL_MOCK Player PASS | 실계정 Provider와 무관 |

**신규 소셜 확장 4개 경로(iOS Google, Android/iOS Facebook, Android Apple)의 Native·Backend·Bridge 코드는 구현했지만 실제 계정 로그인 UI/브라우저 복귀·세션 발급을 검증한 결과는 없습니다.** Android/iOS Unity Player PASS는 `AuthProvider.MOCK` 기반 호출 경로를 검증한 것입니다.

## 현재 통합 회귀 증거

| 영역 | 결과 및 근거 |
| --- | --- |
| Android Unity LOCAL_MOCK | PR #4 병합 소스 `36ca836`의 후속 로컬 검증 **PASS**, 33개 marker·구매 원장 1건/100코인. PR #5는 Android 코드를 변경하거나 재실행하지 않음 |
| iOS Unity LOCAL_MOCK | Meta Embed 수정 소스의 새 Simulator Player **PASS**, 23개 marker·원장 1건/100코인·로그아웃 후 활성 세션 0건. [실행·빌드 증거](IOS_META_EMBED_FIX.md), [정제 JSON](evidence/ios-meta-embed-fix.json) |
| Hosted CI | [PR #5 Run 44538602965](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44538602965): Inventory/Backend/Android/Swift/Basic **SUCCESS**. Unity E2E·Release Readiness **SKIPPED** |
| iOS 의존성 | `FBAEMKit`, `FBSDKCoreKit_Basics`, `FBSDKCoreKit`, `FBSDKLoginKit` Host 앱 Embed·서명 복구 확인. [변경 기록](IOS_META_EMBED_FIX.md) |

## 범위와 남은 위험

- **포트폴리오:** `PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS`. **전체 SDK 제품화:** 기존 `BLOCKED_INTERNAL` 판정과 64개 Task 원장을 유지합니다. [최종 보고](FINAL_REPORT.md) 참조.
- 실제 OAuth·실기기 Android App Link·Google Play/Apple Sandbox 실결제·FCM/APNs 원격 전달은 미검증입니다.
- 기존 iOS 26.5 StoreKit 로컬 상품 조회 FAIL, 전체 Strict 미실행, weak client 원인 미확정은 그대로 남아 있습니다. [알려진 제한](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업).
- 과거 DEV_RC와 [기존 동결 검증](COMPATIBILITY.md#이전-포트폴리오-dev_rc-검증-기록)은 당시 소스의 증거이며, 새로운 소셜 Provider의 실연동 결과가 아닙니다.

구현 책임과 코드 위치는 [설계·문제 해결](ENGINEERING_NOTES.md), 소비자 설정은 [통합 안내](INTEGRATION.md), 실제 소셜 계정 연동 준비는 [사용자 설정](USER_SETUP.md)을 참고하세요.
