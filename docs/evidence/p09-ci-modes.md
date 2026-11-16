# P09-T07 CI 실행 모드 분리 — 2026-11-16

기준 HEAD `1f6beea7a90d0edc2ea12a076515a7f6c3c02a22`. `workflow_dispatch.inputs.release_validation`은 boolean 기본 false다. Unity는 dispatch·입력 true·기존 repository 변수 true의 세 조건을 요구하며, release-readiness는 명시적 release dispatch에서만 실행된다. PR과 기본 dispatch에서는 두 job이 skipped되고 hosted 결과만 workflow에 반영된다.

기존 `ci-unity-e2e.sh`의 strict 호출과 비영 전파, `ci-release-gate.sh`의 basic·Unity·coverage 차단은 변경하지 않았다. 현재 구조에서 Player PASS 뒤 strict FAIL이면 Unity job이 실패하고 Release는 비영 종료한다. Player/Strict 독립 증거 인터페이스는 아직 미구현이다.

`test_workflow_modes.py` 2건과 `test_ci_gate.py` 7건 PASS/skip 0. 후자는 미실행·실패 Unity, strict 실패 전파, coverage 실패·누락 및 성공 fixture를 확인한다. actionlint 1.7.12와 custom self-hosted label 설정 exit 0. 이들은 로컬 정적·격리 시험이며 실제 GitHub Actions 결과는 아니다.

GitHub 원격 HEAD 조회 및 repository 변수 조회는 각각 12초 timeout이었다. 따라서 원격 안전 조건을 재확인하지 못했고 hosted-only dispatch는 NOT_RUN이다. 기존 hosted 결과와 P05-T03 FAIL / ENV-STOREKIT-26 OPEN, Provider WAITING_USER 및 P09 PARTIAL을 유지한다. 원격 연결 복구 후 HEAD·변수를 확인하고 fast-forward push한 다음 Unity 비활성 조건에서 hosted-only dispatch를 실행한다.
