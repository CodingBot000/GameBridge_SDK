# 개발 결정 기록

- P00-T01: 제공 문서가 들어 있는 디렉터리를 신규 로컬 Git 저장소로 초기화했다. 원격 저장소는 추가하지 않았다.

- 2026-11-10 사용자 결정 USER-RETRY: 완료 처리 자동 worker는 동시 1개, 5초부터 지수 백오프를 기본으로 한다. local-mock 설정 `GAMEBRIDGE_FINALIZATION_CONCURRENCY`(기본 1), `GAMEBRIDGE_FINALIZATION_INITIAL_BACKOFF_SECONDS`(기본 5), `GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS`(기본 5000)로 반영했다. 같은 DB의 worker는 동일 concurrency 설정이 필요하다. 실제 Provider에는 해당 코드와 검증이 준비된 뒤 적용한다.
- 2026-11-10 사용자 결정 USER-PUSH-RETENTION: 푸시 등록 해제 또는 로그아웃 시 해당 토큰을 즉시 삭제한다. 등록된 다른 사용자의 토큰은 삭제하지 않는다.

- P04-T01: googleid 1.2.1은 Kotlin metadata 2.4로 현재 compiler 2.1에서 빌드되지 않아 Google Maven의 안정 1.1.1로 변경했고 Credential Manager 1.6.0, Kotlin 2.1.20 조합의 AAR·샘플 빌드와 stub 시험을 확인했다. 실제 Google 로그인 검증은 별도다.

- P04 인증 nonce: Android Google `GetGoogleIdOption.setNonce`와 Apple `ASAuthorizationAppleIDRequest.nonce`에 서버 challenge의 raw nonce를 그대로 전달한다. 서버는 각 Provider가 서명한 nonce claim을 동일한 raw 값과 비교해야 하며, 별도 hash 적용을 임의 가정하지 않는다. 실제 Provider 서명 검증은 P04-T03 미구현이다.

- 2026-11-10 사용자 결정 USER-AUTH-RATE: 단일 서버에서 IP별 인증 challenge는 분당 30회, token 교환은 분당 10회를 기본 제한으로 한다. 설정 `GAMEBRIDGE_AUTH_CHALLENGE_PER_MINUTE`와 `GAMEBRIDGE_AUTH_EXCHANGE_PER_MINUTE`로 반영하고 단일 프로세스 rolling 1분 단위 시험을 수행했다. HTTP route 연동 및 다중 서버 전역 제한은 별도 미검증이다.
