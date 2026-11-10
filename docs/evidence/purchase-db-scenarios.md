# 구매 원장 synthetic DB 회귀

2026-11-11 전용 local DB `gamebridge_ci_1faba5873f_local` 및 sandbox DB `gamebridge_ci_1faba5873f_sandbox`에서 `python3 harness/run-purchase-db-scenarios.py`가 종료 0이었다. 상세 로그는 `artifacts/purchase-db-scenarios-18xuxp_k`에 있다.

Synthetic Apple 검증 결과를 사용한 10개 동시 검증은 구매·원장 한 건과 코인 100을 남겼다. 다른 idempotency key로 같은 거래를 재요청해도 지급은 한 번이며, 같은 key로 다른 거래를 제출하면 HTTP 409와 잔액 불변을 확인했다. 다른 사용자 증빙 재사용은 거부됐다. 테스트 전용 schema에 ledger 제약 실패를 주입했을 때 구매·원장·idempotency 상태가 모두 rollback됐다.

이는 격리 DB·test verifier 결과이며 실제 Apple 서명, 스토어 거래, Unity player의 통과를 뜻하지 않는다. 실행은 별도 local/sandbox DB URL 및 명시적 test opt-in을 요구한다.
