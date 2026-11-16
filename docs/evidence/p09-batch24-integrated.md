# P09 하네스 통합 보강 배치24 — 2026-11-16

## 범위·소스

기준 8eec64a1b95af8930d69680e4534a533bf04cb51. A `2af4d7a`는 nested 단위 보존, B `94dad65af2e45bdc67468ec0579fd9df4e5dd073`는 부모 호출과 실행 증거 연결·fail-closed 보강이다. 로컬 브랜치 fix/unity-android-mock-e2e-evidence에서 관련 커밋만 원격 handoff/p09-resume-20261113으로 전진시킨다.

## 단위·정적 확인

`PYTHONDONTWRITEBYTECODE=1 artifacts/p01-schema-venv/bin/python -m unittest discover -s harness -p 'test_*.py' -v`: 34 suite 파일, 114건 PASS, skip 0, exit 0. aggregation 14/errors 9/measurement 10/nested 4/execution 12/self-report 2를 포함한다. measurement 안의 실제 aggregation subprocess 14건은 최상위 114건에 추가해 제품 테스트로 합산하지 않는다.

최초 112건에서는 시스템 Python jsonschema 부재 error 1 및 이전 Markdown 기대값 failure 1, 이후 수정·기존 schema venv에서 113건 PASS, 마지막 collector 케이스 추가 후 114건 PASS였다. 이 이력을 삭제하지 않는다.

collector 정상·오류·환경대기 fixture는 실제 collector subprocess에서 각각 exit 0/1/2다. missing/duplicate/zero/문자열·bool·음수/오류 1/원본 결과 변조/로그 누락·변조/같은 SHA 과거 결과/source·digest·실행 ID mismatch/부모·자식 불일치/deferred·skip 승격은 PASS하지 않는다. 이는 하네스 fixture이며 실제 Player·DB 검증과 구분한다.

`verify-progress.py`, `check-manifest.py`, `check-unity-meta.py`, `check-api-baseline.py`, actionlint 1.7.12 및 diff 검사 exit 0. manifest 50 mapping, baseline INCOMPLETE를 유지한다.

## P09-T08 직접 통합 실행

명령: `GAMEBRIDGE_UPM_STAGING=<기존 staging> python3 harness/run-strict-local-isolated.py --run-local --self-check`. source 94dad65 및 미커밋 진행 문서 2개 상태(제품/하네스 코드는 해당 commit 그대로). 신규 전용 local/sandbox DB와 role, 합성 인증만 사용. 원본 `artifacts/harness-self-cvmhknn5/result.json`, orchestration `artifacts/strict-isolated-pf5d4dpu`는 로컬 보존, 공개하지 않는다.

| Lane | 판정 | 실제 tests | checks | 예상 실패 | skipped | exit |
|---|---|---:|---:|---:|---:|---:|
| progress-negative | PASS | 0 | 1 | 0 | 0 | 0 |
| manifest-negative | PASS | 0 | 1 | 0 | 0 | 0 |
| package-negative | PASS | 0 | 1 | 0 | 0 | 0 |
| contract-negative | PASS | 22 | 1 | 2 | 0 | 0 |
| bridge-mutation | PASS | 0 | 1 | 0 | 0 | 0 |
| ledger-mutation | PASS | 2 | 1 | 1 | 0 | 0 |
| failed-and-zero-test | PASS | 0 | 1 | 0 | 0 | 0 |
| sandbox-fake-token | PASS | 1 | 1 | 0 | 0 | 0 |
| normal-contracts | PASS | 22 | 1 | 0 | 0 | 0 |

9/9 PASS, exit 0. tests 47는 정상 44 + 의도된 failure 3이며 모두 정상 제품 테스트 PASS 47건이라는 뜻이 아니다. checks 9는 각 lane 판정 호출이며 하위 assertion 총수가 아니다. samples 0/players 0. JUnit 독립 errors 0, Swift 합산·checker errors UNMEASURED. 예상 mutation nonzero 및 복원 성공을 구분한다.

## 현재 Player·Strict

NOT_RUN — 위 기록을 로컬 커밋한 뒤 ci-unity-e2e.sh에서 실행할 예정. 과거 Player 결과를 이번 근거로 사용하지 않는다. staging 147 checksum 통과·exact PackageCache 존재·Unity license active만 준비 확인했다. 사용자 AVD 4개와 booted iOS 기기는 보존하고 기존 GameBridge 전용 AVD 2개를 별도 포트에 기동했다.

## 원격·남은 상태

Hosted-only 새 실행은 NOT_RUN. repository 변수 총 0개(활성 Unity 변수 없음), 원격 handoff 기준 HEAD 8eec64a 확인. 이후 작업 D에서 commit scan·fast-forward push·false 입력 dispatch 1회를 수행한다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN/실 Provider WAITING_USER/Unity self-hosted 미검증을 유지한다.

### C 준비 시도 1 — 환경 대기

source a6a14da30a96e77348a445b1daf657c69e396a19 tracked-clean. Editor 2 tests, Offline sample flow 1 test·GUID reimport, Android/iOS hook repeat PASS. ci-unity-e2e.sh는 기존 AVD의 설치 앱을 보호해 `TEST_APP_ALREADY_INSTALLED_PRESERVE_EXISTING`/exit 2. 새 Player/Strict는 NOT_RUN이다. `artifacts/unity-pii-current-ocq0awkp`·`unity-android-e2e-jefckpl8`은 이 차단의 원본이며 이전 PASS로 대체하지 않는다. 기존 앱을 삭제/덮어쓰지 않고 새로운 전용 AVD를 준비한다.
