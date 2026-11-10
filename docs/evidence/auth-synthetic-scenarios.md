# 인증 로컬 회귀 증거

2026-11-11 `IdentityVerifierTest` 6건은 합성 서명키로 Google·Apple의 잘못된 서명, 알고리즘, 발급자, audience, 만료와 nonce를 거부했다. `python3 harness/run-auth-verifier.py`는 동일 test class와 비실행·skip·실패를 확인한다.

전용 sandbox DB `gamebridge_ci_f89c70feaa`에서 `AuthFlowDatabaseTest` 1건 및 `AuthHttpIntegrationTest` 1건이 통과했다. 잘못된 nonce 후 challenge가 소비되지 않고 정상 재시도가 가능하며 이후 재사용은 거부된다. 이름이 없는 Apple 최초 인증과 이름이 있는 후속 인증, 다시 이름 없는 인증은 동일 subject 계정을 유지했다. sandbox의 개발 인증 endpoint는 404이고 Mock identity 교환은 401이다. 테스트는 합성 서명키와 테스트 전용 DB를 사용하며 실제 Google/Apple 계정 검증이 아니다.
