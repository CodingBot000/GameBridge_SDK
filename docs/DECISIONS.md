# 개발 결정 기록

- P00-T01: 제공 문서가 들어 있는 디렉터리를 신규 로컬 Git 저장소로 초기화했다. 원격 저장소는 추가하지 않았다.

- 2026-11-10 사용자 결정 USER-RETRY: 완료 처리 자동 worker는 동시 1개, 5초부터 지수 백오프를 기본으로 한다. local-mock 설정 `GAMEBRIDGE_FINALIZATION_CONCURRENCY`(기본 1), `GAMEBRIDGE_FINALIZATION_INITIAL_BACKOFF_SECONDS`(기본 5), `GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS`(기본 5000)로 반영했다. 같은 DB의 worker는 동일 concurrency 설정이 필요하다. 실제 Provider에는 해당 코드와 검증이 준비된 뒤 적용한다.
- 2026-11-10 사용자 결정 USER-PUSH-RETENTION: 푸시 등록 해제 또는 로그아웃 시 해당 토큰을 즉시 삭제한다. 등록된 다른 사용자의 토큰은 삭제하지 않는다.

- P04-T01: googleid 1.2.1은 Kotlin metadata 2.4로 현재 compiler 2.1에서 빌드되지 않아 Google Maven의 안정 1.1.1로 변경했고 Credential Manager 1.6.0, Kotlin 2.1.20 조합의 AAR·샘플 빌드와 stub 시험을 확인했다. 실제 Google 로그인 검증은 별도다.
