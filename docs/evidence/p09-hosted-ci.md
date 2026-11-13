# P09-T07 GitHub Actions hosted CI

## 범위와 사전 검사

- 저장소 `CodingBot000/GameBridge_SDK`, default branch `main`의 `.github/workflows/verify.yml`은 active로 등록됐고 `workflow_dispatch`를 허용했다. handoff workflow는 같은 경로의 더 최신 구성이다.
- repo owner는 개인 User, Actions repository 변수 목록은 0개이며 `GAMEBRIDGE_UNITY_E2E_ENABLED` 조회는 404였다. `unity-e2e` job에 environment scope는 없고 조건은 `workflow_dispatch && vars.GAMEBRIDGE_UNITY_E2E_ENABLED == 'true'`다. 실행 전마다 변수 목록을 확인했고 두 실행에서 Unity self-hosted job은 실제 SKIPPED였다.
- YAML 파싱 및 `test_ci_gate.py` 6건 PASS. actionlint 1.7.7은 구버전 label 목록 때문에 `macos-26`과 custom self-hosted label을 오류 처리했다. actionlint 1.7.12에 custom label을 임시 설정으로 알려주어 exit 0; GitHub의 [hosted runner 공식 문서](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)는 macOS 26 계열을 명시한다. 이 설정은 실제 self-hosted runner 생성이나 사용이 아니다.
- `contents: read`, SHA 고정 actions, PR·dispatch 이벤트, hosted job timeout, basic-ci의 required hosted job 검증, release-readiness의 basic/Unity 조건을 대조했다. 이전 로컬 Unity Player 결과는 원격 CI PASS로 취급하지 않는다.

## 첫 실행

[run 43481632527](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43481632527), source `c977b24f9a662772ff06cd33ad57393375ffb774`, workflow_dispatch, 전체 failure.

| Job | 실제 결과 | 확인 범위 |
|---|---|---|
| inventory-contracts | FAILURE | fresh checkout에 `artifacts/`가 없어 manifest guard unittest FileNotFoundError (3건 중 error 1) |
| backend-postgres | SUCCESS | 격리 PostgreSQL·synthetic JUnit 13건, 실패/skip 0 |
| android-native | SUCCESS | JUnit 45+1+1건, 실패/skip 0; 별도 Maven/R8 consumer |
| swift-ios-simulator | SUCCESS | Swift XCTest 17건, 실패/skip 0; synthetic Simulator host XCTest 1건 이상, 정확한 수는 CI가 출력하지 않음 |
| basic-ci | FAILURE | inventory failure 전파; 나머지 hosted success |
| unity-e2e | SKIPPED | self-hosted job 미실행 |
| release-readiness | FAILURE | basic-ci failure를 먼저 보고함; Unity 결과는 성공 아님 |

확인된 결함은 `harness/test_manifest_execution_guard.py`가 임시 디렉터리 생성 전에 상위 `artifacts/` 존재를 가정한 것이다. `mkdir(exist_ok=True)` 한 줄로 보강했고 원본 데이터는 건드리지 않는다. 새 git clone(artifacts 없음)의 inventory step 전체는 unittest 24 suite 68건 PASS/skip 0이었다. 원본 실패 로그는 로컬 artifacts에만 보존한다.

## 수정 후 원격 재검증

[run 43483388390](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43483388390), source `2af863b573fc0bbcdb83a05756187e96b34358de`, workflow_dispatch. 최초 실패의 확인된 결함을 수정한 뒤 한 차례 재실행했다. 전체 workflow는 release gate 때문에 **failure**다.

| Job | 실제 결과 | 확인 범위 |
|---|---|---|
| inventory-contracts | SUCCESS | schema 포함 unittest 25 suite / 70건; 실패·skip 0 |
| backend-postgres | SUCCESS | synthetic JUnit 13건; 실패·skip 0 |
| android-native | SUCCESS | JUnit 45+1+1건; 실패·skip 0; Maven/R8 consumer 빌드 |
| swift-ios-simulator | SUCCESS | Swift XCTest 17건 실패·skip 0, SwiftPM host consumer; synthetic Simulator host XCTest는 1건 이상·실패/skip 0만 검증, 정확한 수 미출력 |
| basic-ci | SUCCESS | 네 hosted job 성공을 집계 |
| unity-e2e | SKIPPED | 비활성 조건에 따라 self-hosted job은 실행되지 않음 |
| release-readiness | FAILURE | `BASIC_RESULT=success`, `UNITY_RESULT=skipped`, gate가 `DEFERRED_ENV`와 exit 2를 반환해 GitHub job은 failure |

이는 hosted 검증 범위의 성공과 Unity 미실행에 따른 release 대기를 구분한 결과다. 전체 workflow 성공, Unity 원격 Player PASS, 실제 Provider 인증·스토어·원격 푸시 또는 release 승인으로 해석하지 않는다. P05-T03 FAIL / ENV-STOREKIT-26 OPEN, Provider 13개 WAITING_USER, P09 전체 PARTIAL을 유지한다. 원본 job 로그는 로컬 artifacts에만 보존한다. 인계 문서 커밋은 실행 SHA 이후이며 제품·workflow 코드를 변경하지 않는다.
