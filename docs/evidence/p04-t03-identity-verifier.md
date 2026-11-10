# P04-T03 서버 ID token 검증

- 시각: 2026-11-10 Asia/Seoul. Spring Security/Nimbus의 고정 Google·Apple JWKS endpoint, RS256 제한, issuer·app별 audience·만료·nonce hash 검사. Google discovery와 Apple 공식 JWKS에서 현재 공개 key의 RS256 알고리즘을 확인했다.
- `GAMEBRIDGE_RUN_AUTH_DB_TESTS=true ... ./backend/gradlew -p backend test bootJar --rerun-tasks`: 종료 0. JUnit XML에서 IdentityVerifier 6건, app별 audience 1건, sandbox HTTP 통합 1건, PostgreSQL challenge 경합 1건, rate limiter 1건 등 실행·통과. 전체 21건 중 별도 finalization DB 시험 2건은 이번 실행에서 skip.
- 테스트 전용 메모리 RSA 서명과 test-only decoder로 Google/Apple HTTP 교환, `/me` 표시 이름, 서로 다른 issuer 표기의 동일 계정, 잘못된 signature/audience/nonce/expiry·필수 claim 누락, challenge의 동시 재사용 1회만 성공 및 실패 시 challenge 미소비를 확인. 배포 jar에 test-only verifier와 key fixture가 없음을 별도 확인.
- 격리 Sandbox 서버 HTTP smoke: 사용자 승인 설정으로 IP별 rolling 1분 challenge 30회·교환 10회 허용 후 각각 429, 임의 X-Forwarded-For 무시 확인. 단일 프로세스 메모리 제한이며 다중 서버 전역 제한은 범위 밖이다.
- 한계: 실제 Google/Apple에서 발급한 token, 공식 키 rotation의 실연동 및 실기기 UI는 USER-AUTH-GOOGLE/APPLE 설정 대기다. 자체 서명 fixture 통과는 실제 Provider 검증 성공이 아니다.
