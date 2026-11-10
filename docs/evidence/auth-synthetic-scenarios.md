# 인증 로컬 회귀 증거

2026-11-11 `IdentityVerifierTest` 6건은 합성 서명키로 Google·Apple의 잘못된 서명, 알고리즘, 발급자, audience, 만료와 nonce를 거부했다. `python3 harness/run-auth-verifier.py`는 동일 test class와 비실행·skip·실패를 확인한다.

전용 sandbox DB `gamebridge_ci_f89c70feaa`에서 `AuthFlowDatabaseTest` 1건 및 `AuthHttpIntegrationTest` 1건이 통과했다. 잘못된 nonce 후 challenge가 소비되지 않고 정상 재시도가 가능하며 이후 재사용은 거부된다. 이름이 없는 Apple 최초 인증과 이름이 있는 후속 인증, 다시 이름 없는 인증은 동일 subject 계정을 유지했다. sandbox의 개발 인증 endpoint는 404이고 Mock identity 교환은 401이다. 테스트는 합성 서명키와 테스트 전용 DB를 사용하며 실제 Google/Apple 계정 검증이 아니다.

`artifacts/auth-regression-qp1sjplw/result.json`: 전용 sandbox DB `gamebridge_ci_064dab9080`에서 backend synthetic 6+2건, Android fake 17건, Swift fake 22건 모두 PASS/skip 0. Google·Apple 취소는 `CANCELED`와 저장 세션 없음으로 처리됐다. iOS에서 인증된 작업 10건의 synthetic 401이 refresh 1회를 공유하고 1회 재시도했으며, Android는 동시 10개 작업을 session lock으로 직렬화해 최초 401 한 건 후 refresh 1회로 처리했다. 양 플랫폼 proof 요청은 재시도 시 동일 idempotency key를 사용했다. 실제 기기, Provider token 및 실 네트워크 401 동시성은 포함하지 않는다.
