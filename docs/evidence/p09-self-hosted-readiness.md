# P09-T07 Unity self-hosted CI 사전 점검 — 2026-11-14

시작 HEAD `2a771c6c9b31c6d85abbe3f2220b5ef253c25371`, handoff 원격과 일치. 이번 검토는 읽기 전용 준비 확인과 로컬 gate 단위시험이다. Runner 설치/등록, repository 변수 변경, workflow dispatch, AVD/Simulator/DB 생성 및 E2E 재실행은 하지 않았다.

## 변경 전 판정표와 최소 분리 제안

현재 `ci-unity-e2e.sh`는 Editor·export·PII를 검사한 뒤 `run-strict-local-isolated.py`를 호출하고 그 종료 코드를 그대로 반환한다. Push Player는 strict 내부에서 실행된다. `verify-all.py`는 원장에 로컬 FAIL인 Task가 하나라도 있으면 `recorded-unresolved-failures` required FAIL lane을 추가한다. 현재 P05-T03이 해당하며 과거 소스 `5d716bd`의 Player PASS/전체 strict FAIL 결과가 이 경로를 실제 확인했다. 따라서 현재 Unity job success는 Unity Player만의 상태가 아니라 strict 전체 성공까지 의미한다.

| Hosted | Unity Player | Strict | 제안한 독립 Release 판정 |
|---|---|---|---|
| PASS | NOT_RUN / SKIP | 어떤 상태든 | 미통과(대기) |
| PASS | PASS | FAIL | FAIL |
| PASS | PASS | PASS | 현재 실행 증거·필수 완료 조건도 충족할 때만 PASS |
| FAIL / SKIP / 누락 | 어떤 상태든 | 어떤 상태든 | PASS 금지 |
| PASS | FAIL / SKIP / 누락 증거 | 어떤 상태든 | PASS 금지 |
| PASS | PASS | SKIP / 누락 / 0건 / 무효 증거 | PASS 금지 |

**제안이며 이번에 runtime gate에 적용하지 않았다.** 최소 후속 변경은 다음과 같다.

1. 같은 HEAD·run identity·PII nonce를 가진 구조화된 결과에 `unityPlayer`와 `strict`를 각각 저장한다. Player 판정은 strict가 생성한 양 플랫폼 Push 결과와 앞서 실행한 PII 결과의 fresh 증거를 사용하고, strict가 Player까지 도달하지 못하면 NOT_RUN이다. 출력 marker나 과거 증거만으로 PASS하지 않는다.
2. Strict 호출과 nonzero 전파를 유지한다. 결과 JSON/정제 summary를 실패 시에도 수집해 Actions에서 두 상태를 보여준다. `continue-on-error`로 job 성공을 만들지 않는다.
3. Release gate는 hosted status, 독립 Player 증거, strict의 실제 exit/summary·required lane 상태·실행 SHA, 필수 증거 누락·skip과 기존 미해결 실패, 계획의 추가 완료 조건을 모두 확인한다. `UNITY_RESULT=success`만 신뢰하는 기존 인터페이스를 그대로 두고 strict를 분리하면 안 된다. 정적 scenario mapping 50개는 실제 50개 실행을 대신하지 않는다.

현재 `ci-release-gate.sh`는 basic/Unity job 상태와 정적 coverage 검사에 의존한다. 안전성은 Unity job 안에 strict가 포함된 데서 나온다. Unity 실패를 모두 exit 2로 표시하는 현행 메시지는 내부 strict FAIL과 환경 대기를 독립적으로 설명하지 못한다. 따라서 분리 구현 후에는 strict FAIL을 Release FAIL로 명확히 전달하고, 위 표의 음성·정상 단위시험을 먼저 추가해야 한다.

## 준비 상태

| 항목 | 확인 결과 | 실행 준비 판단 |
|---|---|---|
| GitHub runner/label | API 등록 runner 0개, `gamebridge-unity-e2e` 없음 | 미준비 |
| Repository 변수 | 목록 0개, Unity opt-in 비활성 | 실행 비활성 유지 |
| OS·계정 | 로컬 macOS ARM64, 현재 개발 계정은 admin 그룹 | 전용 계정·격리 경계 미확인 |
| 개인 인증키·업무 파일 접근 차단 | 전용 VM/계정·권한 제한 증거 없음, 키 내용은 읽지 않음 | 충분한 격리로 판단 불가 |
| Unity | 현재 개발 계정 라이선스 active, 6000.5.8f1 Android/iOS 모듈 | 로컬 조건만 확인, runner 계정은 미검증 |
| UPM staging | 기존 147개 checksum PASS, 배포 product 경로는 5d716bd 이후 diff 0 | runner checkout/HEAD 검증·재생성 경로 필요 |
| PackageCache | Notifications 2.5.0, Newtonsoft 3.2.2 각각 exact 일치 1개 | 로컬 cache 확인, 전용 runner 공급 미준비 |
| Android AVD | 보존된 서로 다른 PII/PUSH 전용 AVD 2개 존재, 연결 기기 없음 | 과거 설치 데이터가 있어 fresh CI 기기로 자동 간주하지 않음 |
| iOS Simulator | booted 기기 없음, 기존 runner는 실행마다 신규 test simulator 생성 | 원격 전용 생성·수명 관리 미검증 |
| PostgreSQL | 기존 loopback 개발 컨테이너 실행 중; script는 새 DB/role 생성 | 기존 컨테이너는 전용 runner 격리의 증거가 아님 |
| 무인 실행 | 과거 두 신규 AVD 최초 전체화면 안내 수동 확인 | 무인 원격 PASS와 구분, 재현 가능한 준비 절차 필요 |

**현재 실행 가능 여부: DEFERRED_ENV.** 별도 격리된 macOS ARM64 실행 계정/VM, 개인 credential·업무 파일·개발 Docker/Simulator에 대한 접근 제한, 신뢰한 ref만 수동 선택하는 실행 정책, 전용 exact 도구·패키지/산출물과 fresh AVD 2개·전용 Simulator/DB·role, 수동 안내 처리 및 정리 정책을 확인한 뒤 runner 등록·활성화를 별도 수행해야 한다. `workflow_dispatch` 제한만으로 공개 저장소 self-hosted의 격리가 입증되지는 않는다. 개인 개발 환경에 runner를 연결해 준비 완료로 처리하지 않는다.

P05-T03 FAIL, ENV-STOREKIT-26 OPEN, 실제 Provider WAITING_USER와 P09 PARTIAL을 유지한다. 로컬 Player PASS는 원격 Unity CI PASS가 아니다.

## 로컬 검증

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s harness -p test_ci_gate.py -v`: 7건 PASS, 실패·skip 0. 기존 test는 결합 script의 strict 실패 전파 및 미실행/실패 Unity 차단을 확인하고, 추가 test는 정상 coverage fixture에서만 성공하며 checker 실패·누락은 비영 종료임을 확인한다. 실제 Unity·Strict·원격 workflow를 실행하지 않는 disposable stub 시험이다. 제안한 독립 `unityPlayer`/`strict` 증거 인터페이스는 아직 구현/실행하지 않았다. `scripts/verify-progress.py` 및 `git diff --check`도 PASS다.
