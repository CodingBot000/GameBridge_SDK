# GameBridge SDK — 마지막 사용자 설정 및 실연동 인계

> 초기 양식이다. 현재는 코드도 아직 구현 전이다. 아래 상태가 대기라고 해서 기능 구현이 준비되었다는 뜻은 아니다. Codex는 개발 중 연결 코드·실제 경로·명령을 채우고, 사용자는 마지막에 계정/콘솔/서명을 처리한다.

## 1. 역할 경계

Codex는 실제 Provider 호출 코드, 설정 로더, 오류 처리, Mock, 빌드 설정, 검증 스크립트까지 작성한다. 사용자는 계정 로그인, 개발자 프로그램 가입/약관, 앱 등록, OAuth/스토어/푸시 권한, 인증서와 실제 key 제공, 실기기 인증·스토어 UI를 처리한다.

외부 설정 부족은 전체 개발 중단 사유가 아니다. 코드 미구현은 사용자 설정 대기로 숨기지 않는다. 실제 key 값을 채팅·README·WORK_LOG에 기록하지 않는다. 사용자 로컬 secret 파일이나 환경 변수로만 전달한다. Codex는 private key를 SDK에 내장하거나 임의 발급·삭제·공개하지 않는다.

## 2. 준비 상태 원장

| 설정 ID | 준비 대상 | 코드 준비 | 설정 준비 | 실연동 검증 | 코드/실행 증거 |
|---|---|---|---|---|---|
| USER-GIT | 로컬 Git identity | NOT_STARTED | NOT_CHECKED | N/A | - |
| USER-UNITY | Unity 설치·라이선스·target modules | NOT_STARTED | NOT_CHECKED | NOT_RUN | - |
| USER-DEVICE | Xcode·Android 도구·실기기·서명 | NOT_STARTED | NOT_CHECKED | NOT_RUN | - |
| USER-BACKEND | 로컬 서버·DB·개발/샌드박스 네트워크 | NOT_STARTED | NOT_CHECKED | NOT_RUN | - |
| USER-AUTH-GOOGLE | Android Google 인증 | NOT_STARTED | WAITING_USER | NOT_RUN | - |
| USER-AUTH-APPLE | iOS Apple 인증 | NOT_STARTED | WAITING_USER | NOT_RUN | - |
| USER-BILLING-GOOGLE | Play 테스트 결제·검증 | NOT_STARTED | WAITING_USER | NOT_RUN | - |
| USER-BILLING-APPLE | Apple Sandbox 결제·검증 | NOT_STARTED | WAITING_USER | NOT_RUN | - |
| USER-PUSH-GOOGLE | Android FCM 원격 전송 | NOT_STARTED | WAITING_USER | NOT_RUN | - |
| USER-PUSH-APPLE | iOS APNs 원격 전송 | NOT_STARTED | WAITING_USER | NOT_RUN | - |

코드 준비는 NOT_STARTED / IMPLEMENTED / BLOCKED, 설정 준비는 NOT_CHECKED / WAITING_USER / READY, 실연동 검증은 NOT_RUN / PASS / FAIL / DEFERRED_ENV를 쓴다. 설정 READY와 실연동 PASS는 별개다.

## 3. 마지막 설정 순서

Git identity·도구/라이선스 → 앱 package/bundle ID·서명 → Backend 접근·환경 → Google/Apple 인증 → 테스트 상품·결제 검증 → FCM/APNs → Native sample 실연동 → Unity 실연동 → 최종 원장/보고서 갱신 순서다. 이미 준비된 항목은 다시 만들지 않는다.

본 문서의 변수명은 **계획된 표준 이름**이다. Codex가 구현 중 실제 이름·경로를 바꿨다면 본문을 반드시 같이 갱신한다. `verify-external --check-config`는 값 자체를 출력하지 않고 존재/형식/상호 일치만 확인한다.

## USER-GIT — 로컬 커밋 identity

사용자가 현재 저장소에 사용할 author 이름/email을 확인한다. Codex는 기존 설정을 사용하되, 없으면 가짜 identity를 전역/로컬에 임의로 만들지 않는다. identity가 없더라도 개발은 계속하고 누락 commit을 기록한다.

확인 명령: `git config user.name`, `git config user.email`, `git status --short`. 원격 GitHub 로그인은 로컬 commit의 전제 조건이 아니다. 이번 작업에서는 push를 자동 수행하지 않는다.

설정 후: 미커밋 변경의 Task 기록과 diff를 대조하고 가능한 논리 단위로 commit한다. 파일 간 의존성 때문에 안전한 분리가 불가능하면 그 이유와 실제 구성대로 기록한다. 과거 시점의 commit을 수행했던 것처럼 조작하지 않는다.

## USER-UNITY — Unity 환경

사용자 할 일: 선택한 Unity LTS Editor와 Android/iOS build support, 필요한 라이선스를 준비한다. 2026-11-10 확인: 설치된 6000.5.8f1 Editor는 프로젝트 생성 시 라이선스 확인에 실패하여 종료 198을 반환했다 (ENV-002). 라이선스 활성화와 계정 로그인은 사용자가 수행한다. Codex가 license secret을 가져오거나 약관을 대신 수락하지 않는다.

설정: `UNITY_EDITOR_PATH`를 실제 실행파일로 지정한다. 정확한 버전은 TOOLCHAIN/ProjectVersion과 일치시킨다. 다른 Unity major/minor를 자동으로 설치해 기존 project를 올리지 않는다.

실행 예정: `bash scripts/doctor.sh`, `bash scripts/build-unity.sh --editor-smoke`. 성공 조건: Editor import, C# compilation, 실제 테스트 수 > 0, Mock demo 및 platform-independent tests 통과. license 오류는 ENV, compiler 오류는 BUG다.

후속: Android/iOS export와 native link 검증을 실행한다. Editor 성공만으로 IL2CPP·device 실행을 통과 처리하지 않는다.

## USER-DEVICE — 앱 식별자·서명·실기기

Android: package/application ID를 결정하고 USB debugging 또는 emulator를 준비한다. 디버그 키 fingerprint와 Play App Signing fingerprint를 구분한다. OS 보안/기기 신뢰 확인은 사용자가 한다.

iOS: Xcode 선택·라이선스 동의·개발자 팀·Bundle ID·프로비저닝·실기기 Developer Mode/신뢰를 준비한다. Team ID 및 `.xcconfig`는 사용자 설정으로 공급한다. 샘플 개인 팀 서명으로 가능한 범위와 실제 Sign in with Apple/APNs/IAP에 필요한 capability를 구분한다.

Unity와 Native sample이 다른 package/bundle ID면 **각각** 외부 앱 등록/인증/푸시/상품 설정이 필요할 수 있다. 하나의 설정을 다른 앱에 무조건 재사용하지 않는다. 같은 ID를 사용한다면 동시 설치가 안 되는 영향과 서명 일치를 문서화한다.

Codex가 채울 항목: 최종 native sample ID, Unity sample ID, target OS, scheme, keystore 위치(값 아님), code signing 방식, device 목록의 비식별 요약. 실제 단말 식별자를 공개 문서에 불필요하게 남기지 않는다.

## USER-BACKEND — 로컬 서버와 샌드박스 접근

사용자 할 일: Docker/Compose 실행과 개발 DB를 준비한다. 기본은 개인 서비스와 분리된 로컬 PostgreSQL이다. 실기기에서 서버가 필요하면 개발 LAN/사용자 관리 HTTPS endpoint를 명시적으로 선택한다. Codex가 공인 tunnel이나 유료 cloud를 임의 생성하지 않는다.

계획 설정:

```text
GAMEBRIDGE_PROFILE=local-mock 또는 sandbox
DATABASE_URL=사용자 로컬 연결
DATABASE_USERNAME=로컬 전용
DATABASE_PASSWORD=비밀값
SERVER_TOKEN_ENCRYPTION_KEY=비밀값
DEVELOPMENT_ADMIN_KEY=개발용 비밀값
GAMEBRIDGE_BACKEND_BASE_URL=기기에서 접근 가능한 주소
```

local-mock 기본 host port는 loopback이다. 실기기 접근을 위해 LAN으로 노출할 경우 fake identity/proof 수락 서버가 공개되지 않게 제한한다. sandbox는 real Provider와 별도 DB/schema/config를 사용한다. `allowAllTLS`, certificate trust 무시, 운영 cleartext 허용은 해결책이 아니다.

현재 준비: `GAMEBRIDGE_DB_PASSWORD`와 local-mock 인증 시험용 `GAMEBRIDGE_DEV_AUTH_KEY`(32자 이상, 비밀값)를 로컬 환경에 설정한 뒤 `bash scripts/run-demo-backend.sh`로 local-mock 서버와 전용 DB를 기동할 수 있다. 최초 기동 시 적용한 DB 비밀번호와 이후 실행 값은 같아야 한다. 기동·health와 migration 재시작만 로컬에서 확인했으며 local-mock A/B 로그인·세션 회전 및 logout의 제한된 smoke는 `python3 scripts/smoke-auth-local.py`로 확인했으나, 속도 제한·Native 연동·실제 인증·구매·푸시 전체 smoke는 아직 구현되지 않았다. 전용 volume 수명은 `infra/README.md`를 따른다.

확인 순서: doctor → server start → health → smoke-local → 기기 통신. 기대 결과: 로컬 원장 smoke 통과, 비밀값 미출력, profile 격리. 설정이 맞아도 실제 Google/Apple 검증이 통과했다는 뜻은 아니다.

## USER-AUTH-GOOGLE — Android Google 로그인

사용자 할 일: Google Cloud/OAuth 설정에서 실제 앱 package와 signing certificate fingerprint를 등록하고 서버용 client ID 및 필요한 동의 화면/테스트 사용자 설정을 준비한다. Native sample과 Unity 앱의 ID·서명이 다르면 각각 대응한다. Credential Manager에서 사용하는 ID의 종류와 Backend가 기대하는 audience를 일치시킨다.

클라이언트 공개 설정: `GOOGLE_SERVER_CLIENT_ID`. 서버 설정: `GOOGLE_ALLOWED_AUDIENCES` 및 app allowlist. client ID는 공개 식별자지만 client secret은 앱에 넣지 않는다. Native ID token 검증에 불필요한 서비스 계정 비밀키를 억지로 요구하지 않는다.

Codex 준비물: GoogleAuthProvider, nonce challenge, server verifier, error mapping, UI, config 검사. TODO 또는 “여기에 OAuth 구현”만 남아 있으면 코드 준비 IMPLEMENTED가 아니다.

실제 검증: Android Native sample에서 Google 로그인→서버 `/me`→재실행 세션 복원→로그아웃. 이후 Unity Android에서 같은 흐름. 취소·audience 불일치·네트워크 실패도 확인한다.

성공 증거: 검증된 provider subject와 서버 user의 비식별 대응, token 원문 없는 결과, 실제 환경/빌드/시각. Mock token이나 자체 서명 token 통과는 실제 Google 인증 증거가 아니다.

## USER-AUTH-APPLE — iOS Apple 로그인

사용자 할 일: 실제 Apple 개발자 팀과 App ID의 Sign in with Apple capability, signing/provisioning, 테스트할 Apple 계정을 준비한다. Native sample·Unity 앱의 bundle ID가 다르면 audience/앱 설정을 각각 확인한다.

설정: `APPLE_ALLOWED_AUDIENCES`, 각 bundle ID, Team ID. 네이티브 identityToken 공개키 검증과 authorization-code exchange/client-secret이 필요한 서버 기능을 구분한다. 구현이 후자를 사용하는 경우에만 해당 private key/key ID/team ID를 서버에 추가한다. 사용하지 않는 비밀키를 필수 요구하지 않는다.

Codex 준비물: AuthenticationServices provider, presentation anchor, nonce, server verifier, credential state 처리, Unity snapshot 변환. Apple 이름/email이 한 번만 올 수 있는 경우에 대비해야 한다.

실제 검증: Native Swift sample 로그인→서버 user 생성/재로그인 동일 계정→취소/복원/로그아웃. 이어 Unity iOS에서 확인한다. Apple token 원문을 출력하지 않는다. capability 부족과 서버 audience mismatch를 구분해 기록한다.

## USER-BILLING-GOOGLE — Play 테스트 결제

사용자 할 일: Play Console에 앱·one-time product 두 개·테스트 가능한 트랙/테스터를 설정한다. Play가 요구하는 상품·앱·정책/가입 상태는 현재 콘솔 기준으로 확인한다. 실제 금전 결제 대신 공식 테스트 계정/테스트 결제 경로를 사용한다. 스토어 업로드는 사용자가 수행한다.

논리 상품: `coins_100`(consumable), `premium_unlock`(non-consumable). 실제 store product ID가 다르면 config mapping을 수정한다. 가격은 store product details에서 읽으며 client hard-coded price를 구매 검증에 쓰지 않는다.

서버 자격증명: 필요한 범위의 Google Play Developer API 접근 권한과 credential 파일 경로. 계획 변수는 `GOOGLE_APPLICATION_CREDENTIALS` 또는 기능별 별도 credential path, `GOOGLE_PLAY_PACKAGE_ALLOWLIST`, product mapping이다. FCM 권한이 있다고 Play API 권한도 있다고 가정하지 않는다. 최소 권한 원칙으로 필요한 앱 접근을 설정한다.

Codex 준비물: Play Billing provider, real server verifier, purchase binding, 원장 transaction, finalization worker, server consume/acknowledge. 앱에서 consume해서 서버 지급 확인을 건너뛰지 않는다.

실제 시나리오: 상품 조회 → 소모성 구매 → 서버 원장 1개/코인 +100 → consume → 재구매 → 비소모성 구매/ack → 재설치 또는 재로그인 복원 → 구매 중 취소/보류 → 네트워크 단절 후 복구 → duplicate verification. 각 원장 변화가 예상과 같아야 한다.

최소 증거: 실제 store 응답을 비밀정보 제거한 상태·purchase fingerprint·server purchase ID·ledger count·finalization status. 주문 ID만으로 중복을 판단하지 않는다. Play Store 설치 조건이 안 맞으면 환경/설정 대기로 남긴다.

## USER-BILLING-APPLE — Apple Sandbox 결제

사용자 할 일: App Store Connect 앱, 두 IAP 상품, Sandbox tester, 필요한 계약/계정/상품 상태를 준비한다. 실제 App Store 테스트에 사용하는 bundle ID와 상품 mapping을 맞춘다. Xcode scheme의 `.storekit` 선택을 실제 Sandbox 시험 시 어떻게 해제/전환하는지 확인한다.

서버 검증 설정: `APPLE_BUNDLE_ID`, `APPLE_STORE_ENVIRONMENT=Sandbox`, Apple 공개 root certificate 경로. App Store Server API 호출 경로에 필요한 경우 `APPLE_STORE_KEY_ID`, `APPLE_STORE_ISSUER_ID`, `APPLE_STORE_PRIVATE_KEY_PATH`를 서버에 둔다. 서명된 transaction JWS 검증과 서버 API 자격증명을 혼동하지 않는다. production용 appAppleId 요구 여부는 선택 라이브러리/환경에 맞춰 확인한다.

Codex 준비물: StoreKit 2 provider, signed data 검증, appAccountToken 일치 확인, 지급 후 finish, unfinished 복구, restore. 초기 Xcode 로컬 시험은 이미 구현되어 있어야 하나 실제 Sandbox 통과와는 별개다.

실제 시나리오: Sandbox 상품 조회 → 소모성 구매 → 서버 검증/원장/finish → 반복 구매 → 비소모성 구매/복원 → 결제 중 종료 후 복구 → duplicate verify → 계정 mismatch 거부. 실제 사용자 금전 결제를 수행하지 않는다.

**주의:** `.storekit` 로컬 성공은 App Store 서명·서버 검증 성공이 아니다. `XCODE_STOREKIT`과 `PLATFORM_SANDBOX`의 mode/provider/evidence를 반드시 구분한다. [공식 설명](https://developer.apple.com/documentation/storekit/testing-at-all-stages-of-development-with-xcode-and-the-sandbox)

## USER-PUSH-GOOGLE — FCM

사용자 할 일: Firebase project에 실제 Android package를 등록하고 host 앱용 client configuration을 준비한다. `google-services.json`은 해당 sample/Unity host 설정 경로에 제공한다. 서버 Firebase Admin 자격증명과 메시지 발송 권한을 준비한다.

설정: `FIREBASE_PROJECT_ID`, 적절한 server credential path, 실제 host config file. FCM 설정 때문에 Google identity 로그인이나 Play Billing 설정이 자동 완료되지는 않는다. 프로젝트와 앱 매핑을 각각 확인한다.

Codex 준비물: host-owned Firebase init, explicit registration, permission/channel, token rotation, foreground/background/click, Backend sender, 개발 발송 API 보호. 기존 host FirebaseMessagingService가 있으면 forwarding 방식으로 통합한다.

실제 검증: Native Android 앱에서 token fingerprint 확인→허용된 자신의 test installation에 전송→foreground 수신→background notification 표시/클릭→재실행→로그아웃/다른 사용자 연결. 이후 Unity Android에서 동일하게 확인한다. 로컬 payload 주입은 원격 FCM 성공이 아니다.

## USER-PUSH-APPLE — APNs

사용자 할 일: 실제 App ID Push capability, provisioning/aps-environment, APNs 인증 key와 Team ID/Key ID를 준비한다. development/sandbox와 production APNs 환경·token이 일치해야 한다. .p8 key는 서버에만 둔다.

계획 변수: `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_PRIVATE_KEY_PATH`, `APNS_TOPIC`, `APNS_ENVIRONMENT`. 앱 bundle ID와 topic의 불일치는 진단한다. Apple Sign in 또는 IAP용 key가 자동으로 APNs에도 유효하다고 가정하지 않는다.

Codex 준비물: Swift host forwarding, token registration, 서버 HTTP/2 sender, invalid token 처리, Unity Mobile Notifications host adapter, click queue. host delegate를 몰래 교체하지 않는다.

실제 검증: Native Swift 앱에서 권한/등록 → token fingerprint → 원격 APNs 전송 → foreground/background/click → cold-start route. 이어 Unity iOS에서 host-managed registration 및 동일 흐름. 로컬 알림이나 simulator payload injection을 실제 APNs 전송으로 기록하지 않는다.

## 4. 설정 후 검증 원장

| EXT ID | 실연동 체크 | Native 결과 | Unity 결과 | 증거 | 잔여 문제 |
|---|---|---|---|---|---|
| EXT-01 | Google 로그인+서버 검증 | NOT_RUN | NOT_RUN | - | - |
| EXT-02 | Apple 로그인+서버 검증 | NOT_RUN | NOT_RUN | - | - |
| EXT-03 | Play 소모성·비소모성+서버 완료처리 | NOT_RUN | NOT_RUN | - | - |
| EXT-04 | Apple Sandbox 구매·복원·finish | NOT_RUN | NOT_RUN | - | - |
| EXT-05 | FCM 원격 등록·수신·클릭 | NOT_RUN | NOT_RUN | - | - |
| EXT-06 | APNs 원격 등록·수신·클릭 | NOT_RUN | NOT_RUN | - | - |
| EXT-07 | 계정 변경·만료·앱 재실행 복구 | NOT_RUN | NOT_RUN | - | - |
| EXT-08 | 실제 단말 생명주기·Bridge callbacks | NOT_RUN | NOT_RUN | - | - |

외부 검증을 수행한 사람, 기기/OS, 빌드, 실행 시각, 결과와 실패 증거를 기록한다. 사용자 스크린샷/로그에 근거한 확인이라면 그 근거를 명시한다. 실행 도구가 직접 확인하지 않은 일을 직접 실행했다고 쓰지 않는다.

## 5. 사용자 설정 완료 후 Codex 재개 지시문

```text
USER_SETUP.md의 실제 설정 준비 상태를 확인하고 verify-external --check-config를 실행해.
비밀값은 출력하지 말고, 코드 준비된 항목부터 Native sample → Unity sample 순으로 외부 Sandbox 검증을 진행해.
실기기 UI 등 내가 직접 조작해야 하는 부분만 정확히 분리해.
실연동에서 발견한 버그를 수정하고 관련 회귀 검증·문서 갱신·로컬 커밋을 수행해.
기존 완료 기능을 처음부터 다시 만들거나 새 기능으로 범위를 넓히지 마.
실행하지 못한 검증은 대기로 유지하고 PROGRESS와 FINAL_REPORT를 실제 결과에 맞게 갱신해.
```
