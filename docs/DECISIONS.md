# 개발 결정 기록

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
