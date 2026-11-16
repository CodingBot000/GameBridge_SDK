# P09-T06 required lane errors 계약 — 2026-11-16

기준 HEAD `c1c121a9b918e5c0d5c17d9dca79523a690603c1`에 집계/producer 변경을 적용해 로컬 fixture만 검사했다. 과거 보고서는 수정하지 않았다.

- JUnit은 tests/failures/errors/skipped를 독립 수집한다. 공통 JUnitCounts는 기존 tuple의 tests/failures/skipped 인덱스를 보존하면서 errors를 별도 보유하고 producer JSON에서는 `errorModel=separate`와 정수 errors를 기록한다. failures에 errors를 다시 합산하지 않는다. run-contracts Kotlin도 동일하다.
- Swift XCTest 텍스트 및 xcresult의 failedTests 합산 경로는 `errorModel=included-in-failures`, `errors=null`로 기록한다. failures가 명시적인 비음수 정수여야 하며 합산 실패가 양수이면 FAIL이다. 이 모델의 errors 누락은 명시적 호환 계약으로만 허용한다. 독립 errors가 제공되면 호환 모델이어도 타입과 0 여부를 검사한다.
- marker/checker는 `errorModel=checker-exit`, errors=null로 오류 미측정을 명시한다. 성공은 실행 exit/marker와 기존 카운트·evidence 조건에 근거하며 독립 XCTest errors=0 측정을 주장하지 않는다. static mapping은 기존 tests 0 / checks 1 계약을 유지한다.
- errors 필드가 누락됐고 명시적 호환 모델도 없으면 PASS 거부. 음수·문자열·boolean·승인 모델 없는 null을 거부한다. required errors 양수는 status PASS/부모 exit 0에도 전체 FAIL/exit 1이다.
- verify-all의 nested_lane은 errors와 errorModel을 원형으로 전달한다. result.json은 정수/null/누락을 보존하고 summary.md는 승인된 미수집을 UNMEASURED, 오류 계약 누락을 MISSING/UNSPECIFIED로 표시한다. 누락을 조용히 0으로 채우지 않는다. Self-check의 하위 contract 검사도 새 계약을 확인한다.

## 실제 실행한 검증

| 검사 | 결과 |
|---|---|
| test_error_contract.py | 9건 PASS, skip 0, unittest exit 0 |
| test_aggregation.py | 14건 PASS, skip 0, unittest exit 0 |
| test_self_check_report.py | 2건 PASS, skip 0, unittest exit 0 |
| 정상 disposable fixture subprocess | tests 1 / failures 0 / errors 0 / skip 0 / runner exit 0 → 전체 PASS, 실제 process exit 0 |
| 오류 disposable fixture subprocess | 같은 PASS-shaped 결과에 errors 1 → 전체 FAIL, 실제 process exit 1 |
| verify-progress.py / check-manifest.py / diff | PASS |
| actionlint 1.7.12 | custom label 설정에서 exit 0 |

오류 계약 단위는 잘못된 errors 타입·누락, 합산 호환의 정상·실패, required 누락/0건/skip, 별도 JUnit errors가 failures에 이중 집계되지 않는지 확인했다. 실제 nested_lane의 disposable result.json/summary.md에 errors 1을 저장하고 전체 exit 1임을 검사했다. producer main 4종(contracts/auth/purchase/push)은 외부 명령을 stub 처리한 계약 시험으로 실제 제품 suite PASS가 아니다. 과거 static mapping 단위도 유지했다. 로그는 로컬 `artifacts/p09-errors-unit.log`, `p09-errors-aggregation.log`, `p09-errors-self.log`에만 보존한다.

전체 Strict·하네스 자체시험 9 lane·Unity Player·DB mutation·원격 Actions·실제 Provider·StoreKit은 이번에 실행하지 않았다. CI에는 새 단위시험을 연결했으나 원격 실행은 NOT_RUN이다. P09 모든 기존 PARTIAL, P05-T03 FAIL / ENV-STOREKIT-26 OPEN / Provider WAITING_USER는 유지한다. 다음 P09 한 작업 후보는 `verify-all.simple`의 marker 호출 수를 실제 테스트 수와 구분하는 측정 계약 보강이다.

## 배치24 보강

Nested 필드와 오류 모델은 원본과 상위에서 동일해야 한다. `failures=0/errors=1/exitCode=0/status=PASS`는 실패다. deferred 상태라도 측정한 실패·오류가 있으면 실패를 우선한다. 새 `test_execution_evidence.py`는 실제 child 및 collector subprocess에서 정상 0·실패 1·환경 대기 2를 확인한다. 전체 Python 113건 및 후속 collector 12건 통과; 제품 검증은 별도다.

배치24 후속: `errorModel`은 separate/included-in-failures/checker-exit 중 하나여야 한다. 미정 모델은 errors=0이어도 거부한다. negative 재현 후 전체 Python 117건 통과. checker/Swift의 errors UNMEASURED를 독립 errors 0으로 바꾸지 않는다. 실제 Strict/새 runtime failure는 통합 evidence에 별도 보존한다.

최신 source 5eaf31f 실제 self-check 9/9 및 Python 119건 통과. Strict source 0b6fb72의 4 FAIL/1 환경 대기는 그대로 보존한다. errors=UNMEASURED인 checker/Swift 행은 독립 errors=0을 측정했다는 의미가 아니다.

배치25:TC JUnit의독립errors0/skipped0,예상failure1을실제명명된assertion과비교하며다른실패/cleanup오류는PASS로처리하지않는다. currentStrict57PASS/knownP05FAIL1과local/Hosted131단위를확인했다. Swift/xcresult합산모델및checker UNMEASURED를독립errors0으로재해석하지않는다. 자세한source관계는[배치25](p09-batch25-integrated.md)에보존했다.
