# 개발 결정 기록

과거 결정과 당시 상태를 보존하는 이력이다. 현재 실행·종료 판정은 [FINAL_REPORT](FINAL_REPORT.md)를 따른다. 아래 초기 미구현/미실행 표현을 현재 상태로 재사용하지 않는다.

- P00-T01: 제공 문서가 들어 있는 디렉터리를 신규 로컬 Git 저장소로 초기화했다. 원격 저장소는 추가하지 않았다.

- 2026-11-10 사용자 결정 USER-RETRY: 완료 처리 자동 worker는 동시 1개, 5초부터 지수 백오프를 기본으로 한다. local-mock 설정 `GAMEBRIDGE_FINALIZATION_CONCURRENCY`(기본 1), `GAMEBRIDGE_FINALIZATION_INITIAL_BACKOFF_SECONDS`(기본 5), `GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS`(기본 5000)로 반영했다. 같은 DB의 worker는 동일 concurrency 설정이 필요하다. 실제 Provider에는 해당 코드와 검증이 준비된 뒤 적용한다.
- 2026-11-10 사용자 결정 USER-PUSH-RETENTION: 푸시 등록 해제 또는 로그아웃 시 해당 토큰을 즉시 삭제한다. 등록된 다른 사용자의 토큰은 삭제하지 않는다.

- P04-T01: googleid 1.2.1은 Kotlin metadata 2.4로 현재 compiler 2.1에서 빌드되지 않아 Google Maven의 안정 1.1.1로 변경했고 Credential Manager 1.6.0, Kotlin 2.1.20 조합의 AAR·샘플 빌드와 stub 시험을 확인했다. 실제 Google 로그인 검증은 별도다.

- P04 인증 nonce: Android Google `GetGoogleIdOption.setNonce`와 Apple `ASAuthorizationAppleIDRequest.nonce`에 서버 challenge의 raw nonce를 그대로 전달한다. 서버는 각 Provider가 서명한 nonce claim을 동일한 raw 값과 비교해야 하며, 별도 hash 적용을 임의 가정하지 않는다. 실제 Provider 서명 검증은 P04-T03 미구현이다.

- 2026-11-10 사용자 결정 USER-AUTH-RATE: 단일 서버에서 IP별 인증 challenge는 분당 30회, token 교환은 분당 10회를 기본 제한으로 한다. 설정 `GAMEBRIDGE_AUTH_CHALLENGE_PER_MINUTE`와 `GAMEBRIDGE_AUTH_EXCHANGE_PER_MINUTE`로 반영하고 단일 프로세스 rolling 1분 단위 시험을 수행했다. sandbox HTTP route에서 실제 제한 동작을 확인했다. 다중 서버 전역 제한은 구현하지 않았다.

- P04-T03: 앱별 Google/Apple 공개 audience는 `GAMEBRIDGE_AUTH_AUDIENCES_JSON`으로 공급한다. 빈 설정은 Provider의 CONFIG_REQUIRED이며 샘플 값은 사용자의 실제 설정이 아니다. Google의 두 허용 issuer 표기는 검증 후 같은 canonical issuer로 정규화한다.

- P05-T02: Google Maven의 안정 Play Billing 9.1.0을 사용한다. 이번 범위는 기본 일회성 상품이며 임의 promotional offer 선택은 하지 않는다. 실제 Play 검증은 사용자 설정 후 별도다.

- 2026-11-10 사용자 결정 USER-SESSION-TTL: refresh 토큰의 기본 7일 만료는 최초 로그인부터 고정하며 refresh로 연장하지 않는다.
- 2026-11-10 사용자 결정 USER-VERIFY-CONCURRENCY: 한 기기의 구매 증빙 서버 검증 기본 동시성은 1건이며 설정으로 변경할 수 있다.
- 2026-11-10 사용자 결정 USER-STOREKIT-TEST-PRICE: Xcode 로컬 StoreKit 시험 표시 가격은 coins $0.99, premium $1.99이다. 실제 App Store 상품 가격 정책이 아니다.

- 2026-11-10 USER-PUSH-RETRY: 푸시 일시 장애와 429 기본 재시도는 최대 3회, 5초부터 지수 백오프. Apple APNs 5xx는 플랫폼 지침에 따라 최소 15분 뒤 재시도한다.
- 2026-11-10 USER-DEV-PUSH-RATE: 개발용 push API는 단일 서버에서 관리자 키별 분당 10회로 제한한다.
- 2026-11-10 USER-GOOGLE-EVIDENCE: Google 구매 완료를 확인하면 암호화된 구매 증빙을 즉시 삭제한다. 완료 확인 전에는 재시도에 필요한 증빙을 보존한다.
- 2026-11-10 USER-PUSH-DEDUP: 앱 세션에서 최근 messageId 200개를 기억하고 초과 시 오래된 ID부터 잊는다. 앱 재시작 시 초기화한다.
- 2026-11-10 USER-CONFIG-DEFAULT: 서버 설정을 가져오지 못하고 사용할 수 있는 캐시도 없으면 신규 구매를 차단한다. 기존 검증·복구·로그아웃은 허용한다.
- 2026-11-10 USER-CONFIG-TTL: 서버 점검 설정의 기본 cache 유효기간은 5분으로 한다. 설정 가능하며 만료 후 사용 가능한 새 설정이 없으면 신규 구매를 차단한다.
- 2026-11-10 USER-PUSH-CONCURRENCY: 푸시 발송·재시도 worker의 기본 동시 처리 수는 1건이며 설정 가능하다.
- 2026-11-10 USER-MAINTENANCE-UNSET: 서버 점검 여부가 명시되지 않으면 신규 구매를 차단한다. 명시적으로 정상 상태를 설정해야 신규 구매가 가능하다.

### LOCAL_MOCK 푸시 미연결 시 처리 (2026-11-11)

사용자 결정: 앱이 연결 중일 때만 simulated 푸시를 전달하고 미연결 시 메시지를 버린다. 이 정책은 로컬 개발용이며 FCM/APNs 실제 전달에는 적용하지 않는다. 구현과 E2E 검증은 아직 진행 전이다.

### LOCAL_MOCK 푸시 연결 확인 및 향후 결정 (2026-11-11)

사용자 결정: LOCAL_MOCK 연결의 끊김 확인 간격은 30초다. 이후 개발 중 필요한 결정은 추가 질문 없이 권장안을 선택해 기록하고 진행한다. 이 연결 확인은 실제 FCM/APNs 정책과 무관하다.

### LOCAL_MOCK 푸시 연결 재시도 (2026-11-11)

사용자가 이후 결정의 권장안 선택을 위임했다. Native LOCAL_MOCK 스트림의 일시 연결 실패는 5초부터 지수 백오프하여 최대 60초 간격으로 재연결한다. 등록 해제·로그아웃·SDK 종료 시 즉시 중단한다. 이 설정은 실제 FCM/APNs에 적용하지 않는다.

### Xcode StoreKit 로컬 지급 격리 (2026-11-11)

사용자가 개발 결정의 권장안 선택을 위임했다. Xcode 거래는 StoreKit 클라이언트 검증 뒤 local-mock 전용 개발키로 fake 서버에 제출한다. 서버는 Xcode 서명 검증을 주장하지 않으며 Xcode 사용자·구매 namespace를 일반 Mock과 분리한다. sandbox/production에서는 개발 경로를 제공하지 않는다. 이는 실제 Apple sandbox 검증이 아니다.

### Xcode 테스트 거래 충돌·보관 (2026-11-11)

사용자가 후속 권장안 결정을 위임했다. Xcode 테스트 거래는 Native에 최소 시도 UUID와 후보 식별자만 보관하고 StoreKit 완료 확인 뒤 삭제한다. 개발 서버는 거래 키와 시도 UUID의 일대일 결합을 개발 DB 수명 동안 보존하며 다른 시도가 같은 키를 주장하면 충돌로 거부한다. 증빙 원문은 저장하지 않는다. 실 Apple sandbox/production 정책이 아니다.

### P09 Testcontainers 실행 경로 — 배치25 (2026-11-16)

기존공유개발container의별도DB/fresh schema 검증은유효하지만원계획Testcontainers와같다고취급하지않는다. 배치25 기술선택으로기존구매fixture를그대로실행하는opt-in init script/runner를추가했다. Testcontainers2.0.5,PG17.6-alpine3.22,기존JDBC42.7.11/Flyway11.7.2를고정했다. 일반SDK·backendbuild의의존성/검증정책을바꾸지않는다. 새loopback-only container와소유label만사용·정리하고,기존개발DB는건드리지않는다. 원장변이의정확한예상실패와정상복원·sandbox합성HTTP를모두요구한다. native/self-check의기존전용DB경로는유지하고C Strict에별도TC검증을연결한다. StoreKit간헐위험분류는이선택과분리한다.

## 2026-11-18 — 사용자 문서36: 포트폴리오 개발 종료

목표는 게임 플랫폼 SDK의 설계·구현과 검증 근거를 확인할 수 있는 기술 포트폴리오를 완성하는 것이다. PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS와 기존 SDK BLOCKED_INTERNAL을 별도로 유지한다. 전체 Strict·실Provider13·모든 OS/성능 완료를 포트폴리오 종료의 절대조건으로 두지 않는다. 신규 P0가 확인되지 않고 최종 보고의 기준을 충족하면 개발을 종료한다. 추가 P1/P2와 실서비스 연동은 선택적 backlog이며 명시적 새 요청 없이 재개하지 않는다. weak1은 추가 재현/제품수정0회·원인미확정, BUG-017 OPEN과기존StoreKit실패도보존한다. 이번동결은문서/동일바이너리 RC 정리이며버전·공개API·정책·데이터수명은바꾸지않는다.
