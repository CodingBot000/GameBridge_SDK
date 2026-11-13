# P09 재개 감사 및 인계

- 시작 브랜치: `fix/unity-android-mock-e2e-evidence`, 시작 HEAD `8cb4003942433087bcc12f9aa83d19c718159f39`.
- 원격 확인: `origin`은 `CodingBot000/GameBridge_SDK`, 기존 원격 작업 브랜치 HEAD `058742df270f42d146843c25cdc2bbfc3ec3b341`. 시작 시 로컬은 그 커밋보다 138개 앞섰고 분기는 없었다. 신규 handoff 브랜치는 최초 조회 시 없었다.
- 미추적 `unity/Demo/`, Python 캐시 및 artifacts는 보존했다. 이 문서의 소스 기준은 시작 HEAD와 P09-T08 미커밋 변경이다. 완료 커밋 SHA는 Git log에서 확인한다.

## P09 원장과 남은 범위

| Task | 원장 상태 | 현재 판단 |
|---|---|---|
| P09-T01 | IN_PROGRESS / PARTIAL | manifest 50개 ID 및 공유 contract 구현. 통합 검증과 전체 완료 기준은 남음 |
| P09-T02 | IN_PROGRESS / PARTIAL | R09 JNI/C ABI 및 R11 Editor 사례는 과거 실행 증거 존재. 전체 장치·현재 소스 재실행 미완료 |
| P09-T03 | IN_PROGRESS / PARTIAL | R22 합성 redaction 증거 존재. 실제 인증과 모든 로그 포괄 검증은 별도 |
| P09-T04 | IN_PROGRESS / PARTIAL | 로컬 DB 및 복구 사례 존재. iOS 26.5 StoreKit 초기화 실패는 미해결 |
| P09-T05 | IN_PROGRESS / PARTIAL | R40 OS denial, R43 synthetic host, R49 신규 소비자 증거 존재. 외부 APNs/FCM과 실제 기기는 미검증 |
| P09-T06 | IN_PROGRESS / PARTIAL | 집계 및 음성 단위 검사가 존재. 현재 소스 전체 strict 통과는 확인되지 않음 |
| P09-T07 | IN_PROGRESS / PARTIAL | workflow 구성과 로컬 대조 존재. GitHub Actions 및 Unity license lane의 이번 실행은 NOT_RUN |
| P09-T08 | IN_PROGRESS / PARTIAL | 이번 manifest 경로 우회 음성 검사를 완료. DB·패키지 등 모든 자체 시험의 현재 소스 통합 재실행은 별도 |

현재 manifest는 50/50을 `IMPLEMENTED`로 표시한다. 이는 시나리오의 assertion 및 기존 증거 매핑 상태이며 이번 실행에서 50개를 모두 통과했다는 의미가 아니다. 과거 원격의 R09/R11/R22/R40/R43/R49 6개 PARTIAL은 현재 manifest에서 모두 IMPLEMENTED로 바뀌었다. 각 한계는 [R09](r09-jni-cabi-utf8.md), [R11](r11-unity-scene-domain-reload.md), [R22](r22-synthetic-redaction.md), [R40](r40-os-and-mock.md), [R43](r43-ios-host-unity-boundary.md), [R49](r49-unity-fresh-consumers.md)에 있다. R40 iOS 거부 선택과 일부 Android 최초 안내는 수동 보조였고, R43은 분리된 합성 host/Player 시험이다. 이들 현재 소스 전체 wrapper 재실행, 실제 플랫폼 provider 및 실제 기기 검증은 완료로 취급하지 않는다.

PX-T01~T17 이력 중 PX-T04/PX-T07의 Android/iOS Unity LOCAL_MOCK Player, PX-T08~T15 Push/Lifecycle·재연결·프로세스 복구와 PX-T16~T17 이벤트 경계 결과는 P09 시나리오 증거에 연결할 수 있다. 초기 라이선스 미설치 등 과거 블로커는 후속 실행으로 대조해야 하며, 해당 Mock 실행은 실제 Google/Apple 로그인·결제, 원격 FCM/APNs나 모든 Scene/OS 경로의 증거가 아니다. 상세는 WORK_LOG와 위 evidence를 따른다.

## P01/P02 전환 조사

`AGENTS.md`는 미완료 작업 중 선행 Task를 선택하도록 적고, `fbd06f1`은 미완료 기능 baseline을 기록했다. 그 뒤 `1b310fb` 등은 모델 계약 재검증, `1051557`/`6e1e95e`는 Backend smoke 판정과 격리 실행, `3d84945`는 Mock 원장 검증을 수행했다. 이 순서와 규칙을 보면 선행 미완료 항목을 선택한 것으로 **추정**되지만, 각 전환이 P09에 직접 필요한 결함 때문이었다는 명시적 근거는 확인되지 않았다. 이번 지시에 따라 P09에 직접 필요한 결함이 아니면 P01/P02 개발로 되돌아가지 않는다.

## 이번 P09-T08 한 단위

`check-manifest.py`는 suite의 Python entry가 절대 경로여도 기존 파일이면 허용했다. 원본을 건드리지 않은 복사 manifest의 외부 실행 파일 경로가 수정 전 exit 0이었다 (`artifacts/p09-manifest-path-0lu14th1`). 수정 후 저장소 밖 경로, `..`, 외부 symlink 및 bash/직접 실행 파일 이탈을 거부한다.

- `python3 harness/check-manifest.py`: PASS (inventory만 검사).
- `python3 harness/check-manifest-negative.py`: PASS; 삭제·잘못된 coverage·timeout과 새 경로 변조 5종 감지.
- 최초 절대 경로 변조본: 수정 후 exit 1, `invalid local entry`.
- `python3 -m unittest discover -s harness -p test_aggregation.py -v`: 13 PASS, 0 skip.
- `python3 -m unittest discover -s harness -p test_ci_gate.py -v`: 6 PASS, 0 skip.
- `python3 scripts/verify-progress.py`, `git diff --check`: PASS.

마지막 전체 strict 결과는 `artifacts/verify-all-n3u_5w60/summary.md`의 소스 `562c75f` + 당시 미커밋 변경, 전체 FAIL이다. 이후 제품 변경이 있어 현재 HEAD의 전체 PASS로 사용할 수 없다. 외부 인증 대상 13개는 WAITING_USER다.

## 다음 한 작업

P09-T08에서 현재 source의 격리 DB를 사용하는 ledger mutation과 정상 원장 suite를 재실행하고, fail-closed 결과·실행 수·원본 복원 및 미실행 항목을 기록한다. iOS 26.5 실패를 덮어쓰지 않는다.

## Push 전 이력 점검

기존 원격 작업 브랜치 `058742df` 이후 139개 커밋을 gitleaks 8.24.2로 검사했으며 탐지 1건은 `2f0c32e`의 redaction 단위 테스트에서 명시한 합성 고정 문자열이다. 패턴 점검에서 개인키·AWS/GitHub token 형태 및 실제 전화번호는 발견되지 않았고 email 형태는 합성 `example.invalid`뿐이다. 전체 이력 경로에서 서명·인증 파일, APK·IPA, XCFramework 바이너리, 캐시·원본 로그 경로는 발견되지 않았다. 스캐너 결과와 생성물은 커밋하지 않았다. 자동 검사가 모든 비밀정보의 부재를 보증하지는 않는다.

기존 원격 이후 전체 diff의 `--check`는 Unity `.meta` 빈 필드 후행 공백 때문에 exit 2다. `.meta`를 제외한 diff 검사와 이번 변경 자체 diff 검사는 PASS다. Unity가 생성한 기존 metadata를 이번 P09 수정에서 재작성하지 않았다. 최종 신규 handoff 브랜치 생성 여부 및 원격 SHA는 대화의 최종 보고에서 확인한다.

## P09-T08 실행 guard 보완 — 2026-11-13

시작 로컬 및 handoff 원격 HEAD `c862f72382f7db3023c5c151afd8d64775c13540`. 각 suite ID에 대한 현재 30개 명령과 모든 인자를 코드의 명시적 allowlist로 검증한다. 새 suite나 인자를 추가할 때 allowlist도 함께 검토해야 한다. `run-scenario.py`는 읽은 동일 manifest 전체를 실행 전에 검증하며 거부 시 suite를 호출하지 않는다.

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s harness -p test_manifest_execution_guard.py -v`: 3건 PASS, 0 skip. 복사 manifest의 8개 경로·인터프리터·옵션 변조, 선택하지 않은 suite 변조, 잘못된 JSON/구조를 거부하고 임시 마커가 생성되지 않았다. 정상 R50은 exit 0.
- `UNITY_EDITOR_PATH=<installed> python3 harness/run-scenario.py R01`: exit 0, Kotlin 10·Swift 12·C# 1 PASS, `artifacts/contracts-y_9ccyrf`. 현재 검증은 host contract이며 Unity Player/실 provider가 아니다.
- `python3 harness/check-manifest.py`, `python3 harness/check-manifest-negative.py`, `python3 scripts/verify-progress.py` 및 CI YAML 파싱 PASS. GitHub Actions 실행은 NOT_RUN.

P09 전체 및 P09-T08은 PARTIAL을 유지한다. 다음 P09-T08 작업은 격리 DB ledger mutation과 정상 suite다. 해당 DB 시험은 이번 범위에서 실행하지 않았다.

## P09-T08 원장 mutation — 2026-11-13

새 전용 PostgreSQL DB와 각각 독립된 두 schema에서 mutation 및 정상 원장 테스트를 실행했다. mutation Gradle exit 1은 의도한 중복 UNIQUE 제약 assertion 실패 1건이며 정상 Gradle exit 0은 1건 PASS/skip 0이다. 최종 하네스 exit 0과 두 JUnit XML·제약 대조는 [원장 mutation 증거](p09-ledger-mutation-20261113.md)에 기록했다. 전체 strict와 외부 provider는 이번에 실행하지 않았으며 P09-T08은 PARTIAL이다.

## P09-T08 통합 자체시험 — 2026-11-13

새 전용 local-mock/sandbox DB에서 9개 lane을 실제 실행해 자체시험 exit 0. 독립 sandbox fake token 401 JUnit, 예상된 계약·원장 mutation 실패, 정상 contract 결과 및 각 lane의 테스트·검사 수는 [통합 자체시험 증거](p09-self-check-20261113.md)에 기록했다. 전체 strict 및 실제 Provider 인증은 실행하지 않았고 P09 전체는 PARTIAL이다.

## P09-T06 Strict 기준선 — 2026-11-13

정적 시나리오 매핑 50개와 실제 실행 테스트 수를 분리한 뒤 소스 `d6bbe7c`에서 격리 strict를 한 차례 실행했다. 전체 FAIL / exit 1, PASS 46·FAIL 1·DEFERRED_ENV 2이며 50개 매핑은 실행 0건의 정적 검사다. 기존 P05-T03 iOS 26.5 실패와 두 Player 환경 대기·실제 Provider WAITING_USER를 유지한다. 49개 lane 및 수집하지 않은 항목은 [strict 기준선](p09-strict-baseline-20261113.md)을 따른다.
