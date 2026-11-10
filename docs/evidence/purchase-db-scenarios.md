# 구매 원장 synthetic DB 회귀

2026-11-11 전용 local DB `gamebridge_ci_1faba5873f_local` 및 sandbox DB `gamebridge_ci_1faba5873f_sandbox`에서 `python3 harness/run-purchase-db-scenarios.py`가 종료 0이었다. 상세 로그는 `artifacts/purchase-db-scenarios-18xuxp_k`에 있다.

Synthetic Apple 검증 결과를 사용한 10개 동시 검증은 구매·원장 한 건과 코인 100을 남겼다. 다른 idempotency key로 같은 거래를 재요청해도 지급은 한 번이며, 같은 key로 다른 거래를 제출하면 HTTP 409와 잔액 불변을 확인했다. 다른 사용자 증빙 재사용은 거부됐다. 테스트 전용 schema에 ledger 제약 실패를 주입했을 때 구매·원장·idempotency 상태가 모두 rollback됐다.

이는 격리 DB·test verifier 결과이며 실제 Apple 서명, 스토어 거래, Unity player의 통과를 뜻하지 않는다. 실행은 별도 local/sandbox DB URL 및 명시적 test opt-in을 요구한다.

후속 회귀 `artifacts/purchase-db-scenarios-0_5gs2l8`는 전용 DB `gamebridge_ci_c36863b21d_local` / `_sandbox`에서 잘못된 bundle·상품·스토어 환경, 취소/철회 및 2개 수량의 synthetic 검증 결과를 HTTP에서 거부하고 기존 잔액·원장이 증가하지 않음을 확인했다. `artifacts/purchase-verifier-2l6nsxv4`의 5건은 Apple/Google verifier의 synthetic 상태 검사와 실제 Apple server library가 테스트용 비신뢰 ES256 JWS를 거부하는 경계를 포함한다. 유효한 실제 Apple 서명이나 실제 스토어 응답 검증은 포함하지 않는다.

`artifacts/purchase-db-scenarios-cye0z6z8`는 전용 local/sandbox DB에서 Google consume 및 acknowledge 각각의 synthetic 일시 실패 후 durable job 대기, worker 인스턴스 재생성과 재시도 성공을 확인했다. 확인 직후 암호화된 증빙 삭제, 기존 코인 원장 및 비소모성 entitlement의 불변도 확인했다. 실제 Play API는 호출하지 않았다.
