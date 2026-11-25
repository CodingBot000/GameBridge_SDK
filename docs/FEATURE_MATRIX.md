# 기능별 구현·검증 현황

> **기준:** 2026-11-25, SDK `0.1.1-dev` / Bridge v1, PR #14 병합 `949d4e0` 및 후속 Android Google 증거. **구현, 합성 시험, LOCAL_MOCK Player, 실제 계정 로그인은 별도 판정**입니다.

## 실제 확인한 기능

| 기능 | 공개 API·구성 | 확인된 범위 | 아직 확인하지 않은 범위 |
| --- | --- | --- | --- |
| 초기화·세션 | `GameBridgeSdk`, `SignInAsync`, `RestoreSessionAsync`, `SignOutAsync` | Android/iOS Native·Unity Google 실제 로그인·복원·취소·로그아웃 PASS; Android 취소 후 재시도 성공 | 양 플랫폼 Apple/Facebook 실계정, 실제 토큰 갱신/replay, iOS Native 취소 후 재로그인 성공 및 실기기 |
| 상품·구매·재화 | `GetProductsAsync`, `PurchaseAsync`, `GetEntitlementsAsync`, `SyncPurchasesAsync` | LOCAL_MOCK Player→Backend→PostgreSQL 원장 **플랫폼별 1건/100코인**; 기존 멱등·복원 테스트 | 실제 Google Play/Apple Sandbox 거래, 일부 StoreKit 문제 |
| 푸시 | `RequestPushPermissionAsync`, `RegisterPushAsync`, `UnregisterPushAsync`, `PushReceived/Opened` | Host adapter·Native/Mock 등록·수신·중복 억제의 선정 기존 시험 | FCM/APNs 실제 원격 전달·실기기 |
| 설정·진단 | `GetServiceConfigAsync`, `GetStatus`, `GetCapabilities`, `GetDiagnostics` | Native·Fake/HTTP·선정 Player 진단, 정제 검사 | 운영 수준의 전체 장애·PII 감사 |
| 샘플·패키지 | NativeDemo/OfflineDemo, Android Maven/AAR, iOS static XCFramework, Unity UPM | 0.1.1-dev 패키지·checksum·R8·Swift 소비·선정 API/ABI, 양 플랫폼 LOCAL_MOCK 버전 교체 및 복구 | 공개 배포, Unity 6000.4, 기타 조합 및 실기기 |

## 플랫폼별 소셜 인증

| Provider | Android | iOS | 실제 계정 검증 |
| --- | --- | --- | --- |
| Google | Credential Manager·Backend ID Token 검증 | GoogleSignIn **9.2.0**, custom nonce 및 자동 Export 콜백 | Android API 34 AVD / iOS 18.6 Simulator **Native·Unity 실계정 로그인/복원/취소/로그아웃 PASS** |
| Apple | 웹 OAuth·Custom Tabs·서버 code 교환 구현·보안 테스트 PASS | 기존 AuthenticationServices 구현 | 두 플랫폼 모두 **WAITING_USER** |
| Facebook | Meta **18.3.0** Classic, Backend token debug 검증 구현 | Meta **18.1.1** Limited/Classic·JWT 검증 분리 구현 | 두 플랫폼 모두 **WAITING_USER** |
| 개발용 Mock | LOCAL_MOCK Player PASS | LOCAL_MOCK Player PASS | 실계정 Provider와 무관 |

iOS Google 최신 실계정 증거는 [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md)와 [정제 JSON](evidence/ios-google-oauth-verification.json)의 `lifecycle20261123`입니다. Native·Unity 복원에서 신규 challenge/세션 0건, 로그아웃은 각각 해당 시험 세션만 폐기했습니다. 취소 후 재시도 UI 진입은 양쪽에서 확인했으나 Native 재시도 로그인 성공은 관측하지 못했습니다. Unity는 두 차례 인증창 timeout 후 새 요청으로 로그인 성공을 확인했습니다. 다른 Provider의 LOCAL_MOCK·합성·빌드 결과를 실제 계정 PASS로 해석하지 않습니다.

Android Google은 API 34 AVD Native·Unity에서 취소 후 재로그인 성공, 앱 재실행 후 신규 인증 요청/세션 없이 복원, 동일 identity의 독립 세션 2개 모두 폐기, C# URL 이벤트 0건 및 시험 프로세스 로그 민감 패턴 미검출을 확인했습니다. [Android Google 검증](evidence/android-google-live-20261125.md). 실제 토큰 갱신·재사용은 미실행입니다.

## 현재 통합 회귀 증거

| 영역 | 결과 및 근거 |
| --- | --- |
| Android Unity LOCAL_MOCK | PR #4 병합 소스 `36ca836`의 후속 로컬 검증 **PASS**, 33개 marker·구매 원장 1건/100코인. PR #5는 Android 코드를 변경하거나 재실행하지 않음 |
| iOS Unity LOCAL_MOCK | Meta Embed 수정 소스의 새 Simulator Player **PASS**, 23개 marker·원장 1건/100코인·로그아웃 후 활성 세션 0건. [실행·빌드 증거](IOS_META_EMBED_FIX.md), [정제 JSON](evidence/ios-meta-embed-fix.json) |
| Hosted CI | [PR #14 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45578953794)에서 기본 5개 Job **SUCCESS**, Unity E2E·Release Readiness **SKIPPED**. 실계정·Player는 별도 로컬 실행 |
| iOS 의존성 | `FBAEMKit`, `FBSDKCoreKit_Basics`, `FBSDKCoreKit`, `FBSDKLoginKit` Host 앱 Embed·서명 복구 확인. [변경 기록](IOS_META_EMBED_FIX.md) |
| iOS Google 세션 수명 | [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md): 실제 로그인·복원·취소·로그아웃 PASS; Swift 합성 10개·Backend 합성 HTTP 2개 PASS (refresh rotation/replay 등); 실계정 SDK-token refresh/replay NOT_RUN |
| Unity iOS 자동 콜백 | [PR #8](https://github.com/CodingBot000/GameBridge_SDK/pull/8): 71개 PBX/URL 검사·새 Export·빌드·서명 PASS. 합성 warm URL Native ABI 1회/C# 이벤트 0건; 실제 로그인 ABI 진입 0건, cold URL 직접 주입 NOT_RUN |

## 범위와 남은 위험

- **포트폴리오:** `PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS`. **전체 SDK 제품화:** 기존 `BLOCKED_INTERNAL` 판정과 64개 Task 원장을 유지합니다. [최종 보고](FINAL_REPORT.md) 참조.
- 양 플랫폼 Apple/Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs 및 실기기는 남아 있습니다. Android/iOS Google 실제 SDK-token refresh/replay, iOS cold Scene URL 직접 주입과 Native 취소 후 재로그인 성공은 미확인입니다.
- 기존 iOS 26.5 StoreKit 로컬 상품 조회 FAIL, 전체 Strict 미실행, weak client 원인 미확정은 그대로 남아 있습니다. [알려진 제한](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업).
- 과거 DEV_RC와 [기존 동결 검증](COMPATIBILITY.md#이전-포트폴리오-dev_rc-검증-기록)은 당시 소스의 증거이며, 새로운 소셜 Provider의 실연동 결과가 아닙니다.

구현 책임과 코드 위치는 [설계·문제 해결](ENGINEERING_NOTES.md), 소비자 설정은 [통합 안내](INTEGRATION.md), 실제 소셜 계정 연동 준비는 [사용자 설정](USER_SETUP.md)을 참고하세요.

## Batch B 0.1.1-dev 추가 근거

Android API 34·iOS 18.6에서 0.1.0-dev → 0.1.1-dev 실제 버전 교체 후 세션·미완료 구매 복구 및 원장 각 1건/100코인 유지. Android API 30·36 및 iOS 26.5 LOCAL_MOCK도 확인했습니다. Unity 6000.4는 DEFERRED_ENV이며 이번 후속 개발 범위에서 제외합니다. [Batch A](evidence/batch-a47-dev-compatibility.md) · [Batch B](evidence/batch-b48-compatibility.md) · [Android Google 검증](evidence/android-google-live-20261125.md).
