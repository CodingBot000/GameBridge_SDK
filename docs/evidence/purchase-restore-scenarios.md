# 구매 복구·복원·계정 결속 로컬 회귀

`artifacts/purchase-regression-hnncaxbh/result.json`은 전용 local/sandbox DB `gamebridge_ci_248eb1b40b_local` / `_sandbox`에서 local DB 7건, sandbox HTTP 2건, Android fake 18건, Swift fake 16건, Android·Swift local Backend 각각 2건, Xcode local StoreKit/DB 1건을 모두 PASS/skip 0으로 기록한다.

양 Native local-mock은 소모성 거래의 서버 잔액과 비소모성 entitlement를 새 client 인스턴스에서 복원하고 과거 거래를 같은 attempt로 재검증해도 추가 지급되지 않았다. synthetic Apple DB에서는 같은 비소모성 거래의 재요청 후 entitlement가 한 건이었다. Xcode local/DB 시험은 서버 commit 후 응답을 유실시키고 Keychain 인스턴스를 다시 생성해 같은 attempt로 복구·finish하면서 잔액 100을 유지했다.

Android Play fake는 검증 도중 계정이 바뀌면 이전 거래의 이벤트를 전달하지 않았고 Swift grant 검사 및 synthetic 서버는 사용자·binding 불일치를 거부했다. 이 시험은 실제 프로세스 강제 종료, 실제 스토어 거래, Unity player나 실제 기기 복원을 대체하지 않는다.
