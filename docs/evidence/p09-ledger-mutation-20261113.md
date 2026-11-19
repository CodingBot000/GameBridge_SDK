# P09-T08 격리 DB 원장 mutation 검증

시작 소스 HEAD `37061d9c7f52fb4cc88fd2be607602e350f30e9b`에 미커밋 하네스 보강을 적용해 2026-11-13 실행했다. 기존 로컬 Docker PostgreSQL의 loopback `127.0.0.1:54329`에 새 role/DB `gamebridge_ci_54affdf462`를 생성하고 local-mock marker를 넣었다. 테스트는 매번 새 무작위 schema를 생성한다. 기존 DB·schema는 변경하지 않았으며 새 DB·role·schema도 삭제하지 않고 보존했다.

`GAMEBRIDGE_RUN_DB_TESTS=true` 및 전용 DB 설정으로 `python3 harness/check-ledger-mutation.py` 실행 결과 **exit 0**. 하네스 내부의 두 Gradle 실행은 `backend/gradlew -p backend test --rerun-tasks --tests com.gamebridge.purchase.LedgerInvariantDatabaseTest`다.

| 실행 | Gradle 종료 | JUnit | 제약 및 결과 |
|---|---:|---|---|
| mutation | 1 (예상 실패) | tests 1, failures 1, errors 0, skipped 0 | 신규 `gb_ledger_invariant_93b32ebcf60f49ed9ad8438b93b46cf8`에서 `wallet_ledger_purchase_id_key` 제거. 중복 insert가 성공하자 `DataIntegrityViolationException`을 기대한 assertion이 실패 |
| 정상 대조 | 0 | tests 1, failures 0, errors 0, skipped 0 | 별도 신규 `gb_ledger_invariant_b0a86827754944719fbca5606f012e75`에서 동일 UNIQUE 제약 존재, 중복 insert 거부 |

두 schema의 제약 개수는 PostgreSQL catalog에서 각각 0과 1로 별도 확인했다. `artifacts/ledger-mutation-1mys19ze/mutation.junit.xml`과 `normal.junit.xml`은 별개로 보존됐으며 각 Gradle 원본 로그는 같은 로컬 artifact 디렉터리에만 둔다. 원본 로그·DB·임시 암호는 Git에 포함하지 않는다.

하네스는 이제 이전 XML 재사용을 거부하고 testcase명, 실제 실행 수, errors/skip, 정확한 중복 제약 실패 메시지와 각 Gradle 종료 코드를 확인한다. 이 판정의 별도 단위 시험은 1건 PASS, skip 0이다. 이 결과는 P09-T08의 원장 mutation 한 단위이며 전체 strict, 실제 결제 provider 또는 iOS 26.5 StoreKit 결과가 아니다.
