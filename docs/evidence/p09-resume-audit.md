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
