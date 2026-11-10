# P04-T03 서버 ID token 검증 — 부분 증거

- 시각: 2026-11-10 Asia/Seoul. Spring Security/Nimbus decoder, RS256 제한. Google discovery와 Apple 공식 JWKS에서 현재 공개 key의 RS256 알고리즘을 확인했다.
- `./backend/gradlew -p backend test`: 종료 0. 메모리 RSA 테스트키로 서명한 fixture를 사용한 IdentityVerifier 3건·실패 0·skip 0: 서명, issuer, audience, expiration, nonce hash, 잘못된 algorithm/서명 및 JWKS network 오류 분기를 검증했다. Google의 두 허용 issuer를 같은 canonical issuer로 정규화한다.
- 사용자 승인 IP별 rolling 1분 제한 challenge 30회·교환 10회에 대해 단위 시험 1건 통과. process 메모리 기반이며 여러 서버를 통합한 제한이 아니다.
- 미완료: DB challenge 발급·원자적 소비, app별 audience 설정·HTTP exchange 연결, HTTP rate-limit 통합, 실제 Google/Apple 발급 token 및 키 회전 시험. 자체 서명 fixture 통과는 실제 Provider 검증 성공이 아니다.
