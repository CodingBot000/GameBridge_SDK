# 선택적 실서비스 연동 준비

포트폴리오 개발 종료 후 **실제 Provider 연동을 선택할 때만** 사용하는 절차입니다. 설정 준비와 실연동 PASS는 별개이며 현재13개 Task의 WAITING_USER를 유지합니다. 로컬 실행은 [Quick Start](INTEGRATION.md), 증명된 결과는 [COMPATIBILITY](COMPATIBILITY.md)가 기준입니다.

## 준비·권한 경계

| ID | 코드/로컬 준비 | 사용자가 할 일 | 현재 실연동 |
| --- | --- | --- | --- |
| USER-GIT | 실제 identity로 commit/FF 인계 및 Hosted 기록 존재 | 이미 설정된 계정/identity 유지 | 포트폴리오 Git 인계와 Provider 인증은 별개 |
| USER-UNITY |6000.5.8f1·모듈·새 양 Player 실제 검증 | 자기 환경의 Editor·module·license 준비, 약관/로그인 직접 처리 | 전용 self-hosted/Release는 미검증 |
| USER-DEVICE | Android API34 AVD/iOS18.6 Simulator, 무서명 archive·ad-hoc Simulator | 실제 단말·앱 ID·서명·capability·기기 신뢰 | 실기기 미검증 |
| USER-BACKEND | local/synthetic profile·DB·HTTP·verifier/sender 코드 | sandbox URL·별도 DB/role·secret 범위와 Provider 권한 준비 | 운영/외부 연결 미검증 |
| USER-AUTH-GOOGLE | Credential Manager/nonce·서버 verifier·fake 경계 | OAuth client ID·audience·package·서명 fingerprint·테스트 계정 | WAITING_USER |
| USER-AUTH-APPLE | AuthenticationServices·nonce·서버 verifier·fake 경계 | Bundle/App ID·Sign in with Apple capability·audience·서명·계정 | WAITING_USER |
| USER-BILLING-GOOGLE | Play Billing·검증/Google finalizer·synthetic 회귀 | 앱/internal testing·일회성 두 상품·테스터·서버 서비스 계정 권한 | WAITING_USER |
| USER-BILLING-APPLE | StoreKit2·검증/finish·Xcode 로컬 일부 | App Store 상품·Sandbox tester·Bundle/환경·검증 신뢰 설정 | WAITING_USER, P05-T03 FAIL 별도 유지 |
| USER-PUSH-GOOGLE | FCM adapter/sender·fake HTTP | Firebase 프로젝트/앱·Host 초기화·google-services 설정·서버 권한 | WAITING_USER |
| USER-PUSH-APPLE | APNs adapter/sender·Host forwarding·fake HTTP | Push capability·aps-environment·topic/Team/Key·서버 .p8·실기기 | WAITING_USER |

실제 key·서명·계정 정보를 생성하거나 ChatGPT로 전송할 필요가 없습니다. 사용자가 자기 로컬 secret 파일/환경에서 설정합니다. Codex는 계정 로그인·약관 동의·키 발급/삭제를 대신하지 않습니다. 실서비스 시험은 별도로 명시 승인된 범위에서만 실행합니다.

## 현재 구현의 실제 설정 이름

아래는 [verify-external-config.py](../scripts/verify-external-config.py)와 현재 Backend loader가 사용하는 이름입니다. 과거 계획 변수명을 새 설정 이름으로 혼동하지 않습니다.

| 변수 | 앱별 JSON/파일 형태 | 연결 |
| --- | --- | --- |
| `GAMEBRIDGE_AUTH_AUDIENCES_JSON` | appId→GOOGLE/APPLE의 비어 있지 않은 문자열 배열 | OAuth/Apple audience와 서버 identity 검증 |
| `GAMEBRIDGE_GOOGLE_PURCHASE_CONFIG_JSON` | appId→packageName·productIds 문자열 배열·credentialPath | Google purchase/finalizer |
| `GAMEBRIDGE_APPLE_PURCHASE_CONFIG_JSON` | appId→bundleId·productIds 배열·rootCertificatePaths 파일 배열 | Apple server library 검증 |
| `GAMEBRIDGE_FCM_CONFIG_JSON` | appId→projectId·credentialPath | Firebase Admin 발송 |
| `GAMEBRIDGE_APNS_CONFIG_JSON` | appId→teamId·keyId·topic·privateKeyPath | APNs token-auth 발송 |
| `SERVER_PURCHASE_ENCRYPTION_KEY` | Base64 decode32 bytes | 서버 구매 증빙 암호화 |
| `SERVER_TOKEN_ENCRYPTION_KEY` | Base64 decode32 bytes | 서버 Push token 암호화 |

값은 예제 repository의 실제 서비스 credential이 아닙니다. 파일은 서버 로컬의 읽기 가능한 경로로 공급하며 SDK/UPM/Host 앱에 서버 credential을 내장하지 않습니다. 기존 DB 비밀번호·암호화키를 재실행 때 임의로 바꾸지 않습니다.

```sh
bash scripts/verify-external.sh --check-config
```

값을 출력하거나 Provider에 요청하지 않는 존재/기본 자료형 검사입니다. 마지막 실제 실행은7항목 모두 `MISSING_OR_INVALID`, exit2였습니다. 올바른 JSON과 파일이 있어도 identity·권한·앱 등록·상품·서명·네트워크·실제 기능 PASS가 되지는 않습니다. 배열 대신 문자열 등 잘못된 자료형은 성공으로 처리하지 않습니다.

## 실제 연동을 선택할 때의 순서

1. **도구·Host:** 기존 앱과 분리한 sandbox 앱/단말을 선택하고 app/package/bundle ID·서명·capability를 맞춥니다. Unity는 staged Native package와 같은 설치 조건을 사용합니다.
2. **Backend:** production과 다른 sandbox DB/role/URL·암호화키·최소 Provider 권한을 로컬에서 준비합니다. profile 표식 충돌은 기존 데이터를 지워 해결하지 않습니다.
3. **인증:** Google server client ID와 서버 audience, Apple bundle/audience/nonce를 맞춥니다. 실제 로그인→서버 검증→복원·갱신→취소·logout을 Native 앱과 Unity에서 각각 확인합니다. 토큰 원문은 기록하지 않습니다.
4. **스토어:** `coins_100/premium_unlock` 논리 ID를 실제 테스트 product ID에 매핑합니다. 가격은 스토어 localized price를 표시합니다. 정상/pending/cancel/재시작·복구/계정 불일치/지급 후 응답 유실과 서버 원장·완료 처리를 확인합니다. 실제 Google consume/ack는 서버 소유입니다.
5. **FCM/APNs:** Host의 기존 service/Activity 또는 Delegate/completion을 연결합니다. 권한 거부·token 회전·명시적 등록/해제·foreground/열기·logout 후 소유 해제를 확인하고, 원격 전달은 실제 단말에서 별도로 확인합니다.
6. **증거:** 사용한 source/package/checksum/OS·mode, 요청별 익명 requestId·status·원장 결과를 정제해 기록합니다. 준비 상태와 실제 PASS를 별도로 바꿉니다.

개발 send는 admin key·allowlist가 있어야 하고 LOCAL_MOCK의 `SIMULATED`/Sandbox의 `QUEUED`는 단말 전달 성공이 아닙니다. Xcode 로컬 StoreKit은 별도 개발 모드이며 실제 Apple 서버 증빙 검증을 대신하지 않습니다. iOS26.5 실패·18.6 간헐 위험은 [Known Limitations](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)에 남겨 두었습니다.

## 안전한 재실행 도구

[Android 소비 runner](../harness/run-unity-android-mock-e2e.py)는 staging과 명시한 전용 serial/AVD/PID·ADB 실행파일 및 build/runtime endpoint를 검증합니다. [iOS 소비 runner](../harness/run-unity-ios-mock-e2e.py)는 새 소비 프로젝트·Simulator·DB를 사용합니다. 실제 검증 명령·결과는 [배치34 증거](evidence/p10-batch34-integrated.md)에 있습니다. 자신의 환경에서 소유권과 조건을 확인하지 않은 채 과거 PID/UUID를 복사해 실행하지 않습니다.

원래 Strict는58개 required lane과 recorded P05 실패를 보존합니다. [preflight](../harness/strict-preflight.py)의 E2 생성/전 wrapper 소유권 계약이 아직 미완성이므로 전체 실행0회입니다. self-check9개 PASS를 전체 Strict로 해석하지 않습니다. self-hosted 등록·Unity opt-in·Release 준비는 이 포트폴리오 종료 작업에서 수행하지 않습니다.

과거 설정 지시는 Git의 이전 `USER_SETUP.md`와 WORK_LOG에 보존했습니다. 이후 작업은 명시적으로 실서비스 연동을 선택한 경우에만 진행하며, 위 목록을 자동 필수 배치로 전환하지 않습니다.
