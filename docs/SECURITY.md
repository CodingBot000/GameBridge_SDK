# 보안과 데이터 소유권

현재 구현·검증의 경계이며 상용 보안 심사 결과는 아닙니다. 구조·소스는 [ENGINEERING_NOTES](ENGINEERING_NOTES.md), 설정 절차는 [USER_SETUP](USER_SETUP.md)을 따릅니다.

## Host·Unity·Native·Backend

| 데이터/권위 | 처리·보관 계층 | 공개 경계 |
| --- | --- | --- |
| OS 계정 UI·알림 권한·Activity/window·Delegate | Host가 제공, Native/명시적 host adapter가 호출 | SDK 초기화가 임의로 권한 창을 열지 않음 |
| ID token·access/refresh token·세션 복원 | Native HTTP/세션 coordinator. Android Keystore 기반 암호화 저장소·iOS device-only Keychain | Unity에는 user/session snapshot만 전달. PlayerPrefs·로그에 token 원문을 저장하지 않음 |
| 스토어 증빙·pending attempt·account binding | Native 복구 단서, Backend verifier/암호화 저장·원장 | C# 결과·이벤트에 raw proof를 넣지 않음 |
| Push token | Host/Native 등록→Backend의 환경·installation·session 결속 암호화 저장 | 공개 결과는 fingerprint/등록 상태. raw token을 이벤트로 노출하지 않음 |
| 구매 지급·재화/entitlement | Backend 검증·transaction·unique/멱등 원장 | UI callback/클라이언트 price·amount가 지급 권위가 아님 |

[RequestRegistry](../unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs)는 session/request/operation을 검증하고 Task 중복 완료를 막습니다. Native callback bytes는 즉시 복사해 main thread에서 처리합니다. 세션 종료 뒤 이전 callback을 새 client에 넘기지 않습니다.

## 환경과 개발 경로

- LOCAL_MOCK을 명시적으로 선택합니다. Google/Apple 실패나 설정 누락을 Mock 성공으로 바꾸지 않습니다.
- DB의 profile 표식이 다르면 migration 전 거부합니다. 기존 DB의 소유권을 임의로 추정하지 않고, 시험은 새 전용 role/DB로 격리합니다.
- 개발 auth/Xcode fake grant/Push stream은 local-mock에 한정하고, 개발 send는 local-mock/sandbox의 별도 admin key·allowlist·session 소유권을 확인합니다. production에는 개발 send가 없습니다.
- 로컬 HTTP 소비자의 개발 예외와 production TLS를 구분합니다. 자동 Android test consumer의 cleartext 허용 manifest는 배포용이 아닙니다.
- 자격증명·서명·개인 파일·DB·raw log·빌드 출력은 Git이나 최종 공개 문서에 넣지 않습니다. shape checker는 값·파일 내용·Provider 권한을 검증하지 않습니다.

## 세션·지급·삭제의 현재 계약

서버는 Google/Apple identity의 issuer/audience/만료/nonce·서명 검증, challenge 원자 소비와 identity/session transaction을 갖습니다. test key/synthetic/LOCAL_MOCK 외에 Android/iOS Google Native·Unity의 실제 계정 로그인, 동일 identity 재사용 및 독립 세션 발급·폐기를 신뢰된 로컬 HTTPS Sandbox에서 확인했습니다. Android 시험에서 C# URL 이벤트 0건 및 시험 프로세스 로그의 JWT·OAuth 코드/토큰·Bearer 패턴 미검출을 확인했습니다. [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md). 실제 계정 SDK-token refresh/replay는 미실행이고 해당 회귀는 합성 시험입니다.

Native 저장 session은 app ID·모드·Backend에 결속됩니다. refresh 이전에 token 없는 `refresh_pending` 표식으로 원자 교체하므로 응답 유실 후 옛 refresh token을 강제 재사용하지 않습니다. 기본7일 만료는 최초 발급부터 고정이라는 기존 결정이며 새 정책을 추가하지 않았습니다. 이전 형식 session은 자동 이전/삭제하지 않고 재인증합니다.

로그아웃은 로컬 session을 먼저 지웁니다. 서버 revoke 미확인 시 `REVOCATION_UNCONFIRMED`를 표시하지만 이 경고의 재시작 후 영속화·자동 재시도는 없습니다.

구매는 검증·지급·스토어 완료를 구분합니다. Apple finish는 서버 지급 확인 후이며 Google 완료 처리는 서버 finalizer가 소유합니다. Google 증빙은 완료 확인 전 암호화 보존, 완료 후 삭제라는 기존 결정입니다. 해제/logout의 Push token은 해당 session 범위에서 삭제하며 다른 사용자 token을 삭제하지 않습니다. 정책 출처는 [DECISIONS](DECISIONS.md)입니다.

## 로그와 제한

형식이 맞는 requestId·허용 operation·정제된 상태를 사용해 추적합니다. HTTP 공통 오류는 sanitized message와 requestId를 반환합니다. PII callback·server trace·synthetic 응답의 문자열 제거와 예외 원문 비노출을 [실제 증거](evidence/p11-batch34-openapi-synthetic.json) 및 [오류 시험](../backend/src/test/kotlin/com/gamebridge/config/HttpInfrastructureTest.kt)으로 확인했습니다.

Android 12 실기기 v0.1.2-dev Unity 합성 이메일·전화번호와 시험 자격정보 패턴을 공개 콜백, 앱 PID 및 Backend 로그에서 검사했고, Google 실계정 시험 로그의 민감 패턴과 Unity 원본 URL 이벤트도 0건을 확인했습니다. [실기기 검증](evidence/android-physical-followup-20261127.md).

양 플랫폼 Apple/Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs 및 iOS 실기기·추가 Android 조합·키 rotation·운영 보안 심사는 미검증입니다. Android/iOS Google 실계정 token refresh/replay 및 iOS cold Scene URL 직접 주입도 미실행입니다. RTDN/Apple Server Notifications 운영, 환불 자동화·SLA는 범위 밖입니다. 로컬 StoreKit의 개발 서버 지급은 Apple JWS 서버 검증이 아니며 P05-T03의 실패/환경 위험을 유지합니다. 전체 Strict가 통과했다는 주장도 하지 않습니다.
