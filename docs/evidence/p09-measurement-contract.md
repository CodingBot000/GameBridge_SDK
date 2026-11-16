# P09-T06 simple 측정 단위 계약 — 2026-11-16

기준 HEAD `6c8af7bfa278729dfeddea8c7951872f843c678d` 위 집계 변경을 disposable fixture로 검증했다. 과거 결과 JSON은 변경하지 않았으며 기존 실행 수를 소급해 새 결과로 표시하지 않는다.

## simple lane 분류

| Lane | 이전 tests | 수정된 측정 |
|---|---:|---|
| harness-self, progress, manifest, api-baseline, api-baseline-negative, csharp-compat | marker 성공 1 | tests 0, checks 1 |
| progress-negative, manifest-negative, contract-negative, bridge-mutation, r50-negative, ledger-mutation | marker 성공 1 | tests 0, checks 1 |
| session-replay, push-router-scenarios, push-ownership, android-dependency-negative, ios-xcframework-negative | marker 성공 1 | tests 0, checks 1; 하위 실제 테스트 수는 상위 simple에서 미수집 |
| aggregation-self | unittest 출력 건수 | tests N, checks 1; 실제 Ran N 및 OK·종료 결과 확인 |
| purchase-verifier | 검증 runner가 출력한 synthetic test 건수 | tests N, checks 1; JUnit을 판정한 runner의 count 출력 근거 확인 |
| unity-editor-runtime | Editor 결과 검사기가 출력한 실행 건수 | tests N, checks 1 |
| lifecycle-stress | 100 | tests 0, checks 1, samples 100; liveClients/liveTransports 0 확인 |
| unity-pii-e2e | marker 성공 시 2 | tests 0, checks 1, players 2; 동일 실행 PII validator가 양 플랫폼 증거를 확인한 출력 기준 |
| scenario-coverage (정적 mapping) | tests 0 / checks 1 | 유지: tests 0, checks 1, mappedScenarios 50, executionStatus NOT_RUN |

이 표는 `verify-all.simple` 22개 호출 및 mapping 연결 범위다. 하위 nested producer가 보고하는 단위까지 전부 재분류했다고 주장하지 않는다. 예를 들어 하위 자체시험의 상세 테스트 수는 별도 JSON에 남으며 checker 1회를 제품 test case로 바꾸지 않는다.

## checker-only PASS 근거

`measurement_contract.measured_lane`은 실행 command·exit·캡처 출력과 저장 로그의 일치, marker 존재를 확인한다. `checkerEvidence`는 로그 경로·SHA-256·검증 marker·exit를 저장한다. 상위 aggregator는 로그를 다시 읽어 해시와 marker를 검증하며 checks가 정수 1인지, 실제 기록된 exit가 정수 0인지 확인한다. 단지 `tests=0, checks=1`인 객체는 통과하지 않는다. missing/변조 로그, missing marker, failed exit, 미실행, checks 0, required 누락/skip, errors 양수는 PASS를 거부한다. 이는 해당 실행의 checker 증거 계약이며 외부의 신뢰되지 않은 작성자가 만든 보고서를 인증하는 서명 체계는 아니다.

테스트 측정 simple도 같은 로그 근거와 양수 count를 요구한다. 샘플·Player count는 tests와 별도 필드다. result.json과 summary.md에 tests/checks/samples/players/errors/errorModel/skip을 각각 남긴다. 오류 미측정은 기존 errors null / errorModel checker-exit을 유지하며 독립 XCTest 오류 0 측정을 주장하지 않는다. scenario mapping은 manifest의 tests>0에 의존하지 않고 검증된 checker evidence를 재사용한다.

## 실행한 검증

- `test_measurement_contract.py`: 10건 PASS, unittest exit 0, skip 0. 정상·음성 checker, 증거 변경/누락, samples·players 및 JSON/Markdown 단위 구분 검증. 이 중 unittest 건수 시험은 실제 `test_aggregation.py` subprocess 14건을 실행해 Ran 14를 확인했다.
- `test_aggregation.py`: 별도 14건 PASS, exit 0, skip 0. 정적 mapping 및 누락·실패·skip 방어 유지.
- `test_error_contract.py`: 9건 PASS, exit 0, skip 0. errors 계약 회귀 없음. 외부 명령은 stub인 producer 계약 시험이다.
- `test_self_check_report.py`: 2건 PASS, exit 0, skip 0.
- 위 네 최상위 unittest suite는 총 35건이다. fixture 내부에서 관찰한 subprocess 실행을 제품 테스트 수 증가로 보고하지 않는다. 음성 fixture의 상위 판정은 FAIL/exit 1, 정상 checker는 PASS/exit 0이었다.
- `verify-progress.py`, `check-manifest.py`, Python 문법, actionlint 1.7.12, diff 검사 PASS.

로그는 로컬 `artifacts/p09-measurement-*.log`에만 보존한다. 실제 stress·Unity Player·제품 suite·전체 Strict·DB mutation·원격 Actions·실제 Provider·StoreKit 시험은 실행하지 않았다. CI에 단위시험 연결만 추가했으며 원격 실행은 NOT_RUN이다. P09 PARTIAL, P05-T03 FAIL / ENV-STOREKIT-26 OPEN, Provider WAITING_USER는 유지한다. 다음 P09 한 작업 후보는 nested producer의 checker/Player 측정 단위를 상위로 보존하는 계약 감사·보강이다.

## 배치24 A — nested 단위 (2026-11-16)

Nested JUnit/XCTest는 tests, C# smoke·설정·패키징·StoreKit wrapper·native mock E2E wrapper는 checks, Unity Push wrapper는 players로 분리한다. wrapper 검사 수는 내부 JUnit/XCTest 수의 대용이 아니다. tests/checks/samples/players/failures/errors/skipped/exitCode/errorModel/measurement와 근거를 상위까지 보존하며, 누락 필드를 0으로 채우지 않는다. 자체시험 checker는 tests로 변환하지 않고 판정한다. negative-contract의 실제 Kotlin/Swift test 수 및 ledger mutation 2건은 실제 하위 결과에서 수집한다.

A 단위 25건 PASS, skip 0. 외부 명령 stub fixture는 실제 관측 로그를 생성한다. 제품/DB/Player 실행은 아직 NOT_RUN; 실행 근거 replay 방어는 B에서 보강한다.

## 배치24 B — 실행 연결

현재 orchestrator가 관측한 명령·stdout 로그·실행 ID·시각·HEAD·tracked diff digest를 메모리 registry에 보관한다. simple receipt는 이 관측과 일치해야 한다. nested는 부모가 전달한 새 실행 ID, 부모 실행 시간 안에 생성한 result, stdout에 출력한 해당 artifacts 디렉터리, report hash·source와 자식 로그 경로·시각·hash를 모두 확인한다. 상위 필드도 원본 child와 같아야 한다. 임의 파일의 hash만으로 PASS하지 않는다. 과거 JSON은 조회용이며 다른 실행의 PASS 입력으로 사용할 수 없다. 로컬 파일을 쓸 수 있는 악성 실행 코드에 대한 서명/인증 체계는 아니다.

PASS는 모든 카운트의 정확한 int 타입(문자열·boolean·음수 거부), 명시 단위와 실제 측정, 오류 모델 및 exit를 요구한다. 자기시험 9 lane은 상위에서 각각 required로 집계한다. static 50 mapping은 실행 건수가 아니며 manifest 검사 receipt를 참조하는 별도 매핑 행이다.

전체 Python 113건 통과 후 추가 collector 변조 방어 12건 통과. 최초 시스템 Python의 schema 의존성 error와 이전 출력 기대값 failure는 보존 로그에 있으며 후속 venv 실행으로 해소했다. 실제 제품·DB·Player·Strict는 C에서 검증한다.

## 배치24 통합·후속 방어

[통합 결과](p09-batch24-integrated.md)에 현재 source의 자체시험·실제 Player·Strict와 새 실패를 구분했다. 추가 음성 3건으로 미정 errorModel 수락, 호출 후 command 리스트 변조 수락, timeout 부분 stdout 폐기를 재현하고 수정했다. registry의 command는 deep snapshot으로 고정한다. Markdown은 누락 단위를 MISSING으로 표시하고 failures/exit/measurement도 출력한다. timeout의 부분 PASS 문자열은 성공으로 승격하지 않는다. 새 단위를 포함한 전체 Python 117건 PASS/skip 0; 실제 timeout 재확인 1건 PASS. Strict 원본은 수정하지 않으며 이후에는 영향 검증만 수행한다.

최신 source 5eaf31f에서 전체 Python 119건과 실제 자체시험 9 lane(tests47/checks9), 독립 iOS Push Player 1건을 확인했다. 원래 Strict의 tests213/checks52(매핑 alias 포함)/samples100/players2 및 새 실패·후속 결과는 [배치24](p09-batch24-integrated.md)에 source별로 구분했다. Android Push 재검증은 환경 대기이며 과거 PASS를 사용하지 않는다.
