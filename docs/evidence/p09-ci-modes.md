# P09-T07 CI 실행 모드 분리 — 2026-11-16

기준 HEAD `1f6beea7a90d0edc2ea12a076515a7f6c3c02a22`. `workflow_dispatch.inputs.release_validation`은 boolean 기본 false다. Unity는 dispatch·입력 true·기존 repository 변수 true의 세 조건을 요구하며, release-readiness는 명시적 release dispatch에서만 실행된다. PR과 기본 dispatch에서는 두 job이 skipped되고 hosted 결과만 workflow에 반영된다.

기존 `ci-unity-e2e.sh`의 strict 호출과 비영 전파, `ci-release-gate.sh`의 basic·Unity·coverage 차단은 변경하지 않았다. 현재 구조에서 Player PASS 뒤 strict FAIL이면 Unity job이 실패하고 Release는 비영 종료한다. Player/Strict 독립 증거 인터페이스는 아직 미구현이다.

`test_workflow_modes.py` 2건과 `test_ci_gate.py` 7건 PASS/skip 0. 후자는 미실행·실패 Unity, strict 실패 전파, coverage 실패·누락 및 성공 fixture를 확인한다. actionlint 1.7.12와 custom self-hosted label 설정 exit 0. 이들은 로컬 정적·격리 시험이며 실제 GitHub Actions 결과는 아니다.

GitHub 원격 HEAD 조회 및 repository 변수 조회는 각각 12초 timeout이었다. 따라서 원격 안전 조건을 재확인하지 못했고 hosted-only dispatch는 NOT_RUN이다. 기존 hosted 결과와 P05-T03 FAIL / ENV-STOREKIT-26 OPEN, Provider WAITING_USER 및 P09 PARTIAL을 유지한다. 원격 연결 복구 후 HEAD·변수를 확인하고 fast-forward push한 다음 Unity 비활성 조건에서 hosted-only dispatch를 실행한다.

## Hosted-only 원격 실행 — 2026-11-16

이전 timeout·Push 미완료 기록은 당시 상태로 보존한다. 이후 `f8d644e83dd8219578c19c4d1330e9846e35a35b`가 handoff 브랜치에 fast-forward push됐고, 이번 시작 시 로컬·원격 SHA가 해당 값과 일치했다. GitHub 변수 목록 API는 성공(총 0개)해 `GAMEBRIDGE_UNITY_E2E_ENABLED` 미설정을 확인했다. 조회 오류나 timeout을 미설정으로 간주하지 않았다.

`gh workflow run verify.yml --repo CodingBot000/GameBridge_SDK --ref handoff/p09-resume-20261113 -f release_validation=false`를 **딱 1회** 실행했다. [Run 43840984922](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43840984922), 실제 실행 SHA `f8d644e83dd8219578c19c4d1330e9846e35a35b`, event `workflow_dispatch`, 전체 **SUCCESS**.

| Job | 최종 결과 |
|---|---|
| inventory-contracts | SUCCESS |
| backend-postgres | SUCCESS |
| android-native | SUCCESS |
| swift-ios-simulator | SUCCESS |
| basic-ci | SUCCESS |
| unity-e2e | SKIPPED |
| release-readiness | SKIPPED |

이는 Hosted-only 모드의 정상 결과다. Unity·Release 검증은 실행되지 않았으므로 Release PASS나 원격 Unity PASS가 아니다. 코드·workflow·변수·runner를 변경하지 않았고 원격 재실행도 하지 않았다. P05-T03 FAIL / ENV-STOREKIT-26 OPEN, Provider WAITING_USER, P09 전체 PARTIAL은 유지한다. 이후 인계 커밋은 이 결과의 문서 변경이며 원격 실행 소스 SHA는 위 값을 따른다.

## 배치24 Hosted-only 재검증 — 2026-11-16

source8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18, [run43862394352](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43862394352). false 입력 단일 dispatch, repo Unity 변수 미설정. Hosted4+basic-ci SUCCESS, Unity/Release SKIPPED, workflow SUCCESS. 원격 하네스 단위113건 통과. self-hosted·remote Player·Release 검증으로 취급하지 않는다. local Strict 실패와 환경 대기는 [배치24 evidence](p09-batch24-integrated.md)에 별도로 유지했다.

## 배치25 Hosted-only 확인

source59b98349689171cc8a75d9652f248708645a85c2,[run43889958441](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43889958441),false입력1회만요청. Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED,workflowSUCCESS. inventory모든38파일/131건과backend TC11(negative1/normal복원)확인. self-hosted등록/활성변수변경/Release실행은없다. actual localStrict57PASS/knownP05FAIL1은[배치25](p09-batch25-integrated.md)에source별분리했다.

Unity self-hosted 경로는 GAMEBRIDGE_PUSH_EMULATOR_PID를job별전용emulator에서유도해제공해야한다. 정적인PID설정만으로소유를주장하지않고이름·console/ADB양port owner를매명령전재검증한다. 이번에는준비hook/전용계정격리의원격실행을검증하지않았으므로T07PARTIAL을유지한다.
