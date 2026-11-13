# P02-T03 로컬 Mock 원장 검증

2026-11-13, HEAD `6e1e95e`에 미커밋 smoke assertion을 적용한 상태로 새 격리 DB `gamebridge_ci_6a1f22d6f1`에서 `harness/run-backend-smoke-isolated.py --run-local`을 실행했다. Backend local-mock 구매 14개 assertion이 통과했고 별도 복사본에서 기대 잔액을 틀리게 변경한 음성 검사도 실패를 감지했다. 로컬 evidence는 `artifacts/backend-smoke-isolated-hbw5kx_k`다.

두 상품 catalog, 동일 거래 재전송의 단일 지급, 다른 사용자의 거래 재전송 409, 동시 재시도 단일 지급, premium 거래 재요청 및 클라이언트가 보낸 위조 금액·사용자·가격이 지급에 영향을 주지 않는 경로를 확인했다. `wallet_ledger.purchase_id`의 unique 제약과 `entitlements(user_id, product_id)` 기본키를 소스에서 확인했다. 이 결과는 합성 mock 증빙과 테스트 DB에 한정되며 실제 스토어 영수증·외부 결제 검증은 포함하지 않는다.
