# P09 하네스 통합 보강 배치24 — 2026-11-16

> 후속현재판정은 [배치25](p09-batch25-integrated.md)를참조한다. 배치24의Android환경대기는새owned Push실행으로해소했고,TC요구/기존CI미연결도후속구현했다. 아래배치24실패·부분·대기및retry성공은당시원본으로보존한다.


## 최신 상태 — 배치24 종료

A/B 구현·방어 보강 완료. C는 전체 Strict 원본 FAIL을 보존한 **PARTIAL**이다. Android Push 재검증은 ENV-P09-AVD 대기다. 최신 코드 source **5eaf31f59f0d187a24bffb5007543744359ca076**: Python 119 PASS/skip 0, P09-T08 9/9 PASS, 독립 iOS Push Player PASS. 아래 NOT_RUN·중간 실패 기록은 당시 이력이며 후속 검증으로 덮어쓰지 않는다. D Hosted-only run 43862394352 전체 SUCCESS(5 job SUCCESS, Unity·Release SKIPPED). 원격 검증 source는 8c8fc62이며 최종 결과 문서만 이후 추가한다.


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

### C Strict 실행 1회 결과

source **0b6fb7250e6f9edb2c93ba477ac06a5060b1769a**, tracked-clean. `ci-unity-e2e.sh`로 fresh 전용 AVD와 기존 staging/cache를 사용했다. 원본 `artifacts/verify-all-5ffhc5v8/result.json`, orchestration `strict-isolated-9udgzbhv`, gate log `p09-batch24-c-player-strict-fresh.log`. 전체 exit **1**, 57 lane 중 **52 PASS / 4 FAIL / 1 DEFERRED_ENV**. 기존 P05 원장 하나만으로 실패한 결과가 아니다.

- 현재 self-check `harness-self-f7gzdby0`: 9/9 PASS.
- 실제 측정 tests **213**(예상 mutation failure 3 포함), checks **52**(manifest/static mapping alias 1개 포함, 고유 receipt 51개), samples **100**, 검증된 Players **2**. 미실행·시간 초과 lane은 테스트 성공 건수로 추가하지 않았다.
- PII: `unity-pii-current-nx2g3_gq`; Android `unity-android-e2e-ebq2fh_4`, iOS `unity-ios-e2e-kxqg9zui`. 모두 source 일치·tracked-clean·piiProbe true·원장 1건/증가 100. 새 Android 최초 systemui 전체화면 안내를 확인하고 Got it을 한 번 눌렀다. 무인 CI 검증으로 간주하지 않는다.
- Auth 6+3+17+22=48 실제 test PASS. Purchase DB/Native/응답 유실 7+2+18+16+3+3=49 PASS. Push Backend 10/sandbox 1/Android 5/Swift 9/iOS Host XCTest 1 PASS.

| 실패/대기 lane | 실제 관측 | 후속 |
|---|---|---|
| purchase/xcode-storekit-local-db-recovery | iOS 18.6, `xcode-storekit-e2e-a3aicym0`, testExitCode 124/180초 timeout, xcresult 미완결·건수 미확정 | 부분 stdout 보존 보강 후 영향 lane 재검증 |
| purchase/xcode-storekit-process-recovery | `xcode-process-recovery-s3d3ilfe`, prepare/store-history timeout | history 두 API 단계 식별 및 영향 lane 재검증 |
| push/unity-player-notifications | `unity-android-push-0weeo3hz` TIMEOUT_GB_PUSH_READY. 실패 후 UI dump에서 systemui Viewing full screen/Got it 확인. iOS Push는 gate가 앞에서 종료돼 NOT_RUN | 앱·AVD 보존, fresh AVD와 명시 UI 보조로 영향 gate만 재실행 |
| unity-editor-runtime | `unity-consumer.781hN7`, CLI process timeout 300초/exit 6, 테스트 판정 없음 → DEFERRED_ENV/exit 2 | preflight 2건 PASS와 구분, 단독 영향 재검증 |
| recorded-unresolved-failures | P05-T03 기존 FAIL 유지 | 26.5를 이번에 재실행/해소한 것으로 취급하지 않음 |

새 두 StoreKit 실패는 26.5 기록과 다른 18.6 관측이며 원인은 아직 확정되지 않았다. 관련 StoreKit runner/RecoveryHarness는 이전 5d716bd 이후 선택 경로 git diff가 없음을 확인했다. 이 사실만으로 환경 원인을 확정하지 않는다. 완료된 이번 실행 전용 PII·StoreKit·Process Simulator는 shutdown했고 디스크·DB·실패 결과는 보존했다. 사용자 iPhone 17 Pro는 변경하지 않았다.

### C 후속 검증/진단 source

`4508b9a`에서 미정 오류 모델·mutable command snapshot·timeout 부분 로그 공백을 보강했다. 관련 새 음성 3건은 수정 전 실패를 재현했고 수정 후 전체 Python 117건 PASS/skip 0. Strict 전체를 재실행한 것으로 취급하지 않는다. 같은 source의 단독 Editor 재검증 `unity-consumer.nsFJLu`는 실제 2건 PASS/exit 0. 최초 timeout은 보존한다.

다음 source는 test-only StoreKit stage 로그와 Transaction.all/unfinished checkpoint를 추가한다. SDK 동작이나 성공 판정 기준·timeout은 바꾸지 않는다. 그 뒤 격리 StoreKit 두 lane을 각각 한 번, 새 전용 AVD의 Push gate를 영향 재검증한다.

### StoreKit 영향 재검증

- `run-xcode-storekit-e2e.py --run-local`: source 4b23529251392bdcc26cdbc2616b574cf93f3063, `xcode-storekit-e2e-zk9hcbqp`, exit 0, 실제 XCTest 1 PASS/skip 0, testExitCode 0, timedOut false.
- `run-xcode-process-recovery.py --run-local`: 같은 source 및 진행 문서 변경(제품·하네스 코드는 동일), `xcode-process-recovery-r2r9s3db`, exit 0. prepare/recover의 잔액 모두 100, PID가 달라 실제 프로세스 종료·복구를 확인했다. 실제 XCTest 건수가 아닌 process recovery 검사 1회다.

새 격리 DB·role·Simulator에서 각 한 번씩 재검증했다. 완료된 이번 전용 Simulator를 종료하고 보존했다. SDK 동작이나 timeout을 변경하지 않았으므로 최초 실패 원인은 미확정/간헐 위험으로 남기며, 원래 Strict report를 통과 결과로 재작성하지 않는다.

### Android Push retry 환경 보류

새 AVD helper는 예상 serial5570에서 다른 AVD 이름을 받아 `Wrong dedicated AVD`/exit 1로 gate 실행 전에 중단했다. UI·설치·네트워크 명령은 보내지 않았다. retry AVD의 자기 PID는 살아 있었지만 해당 serial/online AVD와 연결되지 않았고 원인은 확정하지 못했다. 검증한 자기 PID만 종료했고 디스크를 보존했다. 다른 기기·ADB server를 재시작/초기화하지 않는다.

**ENV-P09-AVD OPEN / Android Push 영향 재검증 DEFERRED_ENV**. 기존 실제 READY timeout FAIL을 지우지 않는다. 원격/과거 Android Player 근거를 현재 PASS로 재사용하지 않는다. 기기 명령마다 serial·전용 이름을 다시 확인하고 cleanup이 기존 실패를 환경 대기로 덮지 않도록 보강했다. serial 재배정·범위 없는 명령 거부 단위 포함 전체 Python 119건 PASS. iOS Push는 독립 실행한다.

### C 마지막 현재 source 검증

- source 5eaf31f59f0d187a24bffb5007543744359ca076, 코드 커밋 후 Python **119건 PASS/skip 0/exit 0**, progress/manifest/Unity metadata/API baseline/actionlint/diff exit 0.
- self-check `harness-self-whqw6w9q`, orchestration `strict-isolated-35ibhosh`: **9/9 PASS/exit 0**, tests 47(정상 44+예상 mutation failure 3), checks 9/samples 0/players 0. sandbox 지정 401 case 1건과 정상 복원을 포함한다.
- 독립 iOS Unity Push `unity-ios-push-5wsdfn1e`: **Player 1 PASS/exit 0**, source 일치·tracked-clean, mockPush/deduplication/mainThread/background/reconnectFailure/sessionSwitch PASS, rejectedReconnectAttempts 6, deviceTokens 0. networkRecovery는 **PASS_LOCAL_TRANSPORT_FAULT**로 실제 OS 네트워크 전환과 구분한다. FCM/APNs 실제 전송이 아니다.

Strict source 0b6fb72와 최신 source 사이의 변경은 오류 모델/관측 snapshot/timeout 진단/Markdown/기기 명령 소유 재확인·test-only stage 로그 및 증거 문서다. 실제 SDK 동작·signing·Provider는 변경하지 않았다. 전체 Strict는 한 번만 수행했으며 후속 119 단위·9 lane·Editor·StoreKit·iOS Push는 영향 재검증이다. 원래 Strict 결과를 최신 전체 PASS로 재작성하지 않는다. 상위 tests/checks 합계는 실행별 측정 단위이며 고유 제품 케이스/모든 내부 assertion 총수가 아니다. static 50 mapping은 실제 테스트 합계에 포함하지 않는다.

## 커밋·실행 source 관계

| Commit | 범위 |
|---|---|
| `2af4d7ae86b3daeda1924d62dc64219d748a3f87` | fix(harness): [P09-T06] preserve nested measurement units |
| `94dad65af2e45bdc67468ec0579fd9df4e5dd073` | fix(harness): [P09-T06] bind nested evidence to observed executions |
| `a6a14da30a96e77348a445b1daf657c69e396a19` | test(harness): [P09-T08] record integrated self-check before strict |
| `0b6fb7250e6f9edb2c93ba477ac06a5060b1769a` | docs(harness): [P09-T06] record preserved AVD preflight deferral |
| `30f55dd2564859798bd2764dcfa707c91a9c3f92` | test(harness): [P09-T06] preserve strict results and new runtime failures |
| `4508b9a856df8fa62b1979e6cb2104d856e58fb5` | fix(harness): [P09-T06] freeze observations and retain timeout diagnostics |
| `4b23529251392bdcc26cdbc2616b574cf93f3063` | test(harness): [P09-T06] record editor retry and trace StoreKit stages |
| `5a50a3bc2d947058cf3143bcedf21b1630b47d78` | test(harness): [P09-T04] record isolated StoreKit recovery retries |
| `5eaf31f59f0d187a24bffb5007543744359ca076` | fix(harness): [P09-T05] revalidate device identity before commands |
| `631396365d0d57486330624596ed1092b126b575` | docs(harness): [P09-T06] audit integrated validation and remaining waits |
| `8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18` | docs(ci): [P09-T07] record handoff push preflight |

실제 전체 Strict는 0b6fb72, 후속 Editor는 4508b9a, StoreKit 두 retry는 4b23529, 최종 local119/self9/iOS Push는 5eaf31f, Hosted 실행은 8c8fc62다. 5eaf31f 이후 Hosted source까지는 문서만 변경했다. 이 뒤 최종 결과 문서 커밋 SHA는 자기 참조로 넣지 않고 Git 이력과 최종 인계에서 보고한다.

## D Hosted-only 최종 결과

[GitHub Actions run 43862394352](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43862394352), source **8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18**, event workflow_dispatch, `release_validation=false`. repo 변수 총0으로 Unity 활성 변수 미설정을 확인했다. 한 번만 요청했고 재실행하지 않았다. **workflow SUCCESS**.

| Job | 실제 최종 결과 | 범위 |
|---|---|---|
| inventory-contracts | SUCCESS | 32 unittest suite/113건 PASS, 새 하네스 단위 연결 확인 |
| backend-postgres | SUCCESS | synthetic key·격리 PostgreSQL, JUnit13/실패·skip0 |
| android-native | SUCCESS | JUnit45+1+1/실패·skip0 및 Maven/R8 clean consumer |
| swift-ios-simulator | SUCCESS | Swift XCTest17/실패0, synthetic iOS host >0·실패/skip0 검사 통과. Host 정확 건수는 출력되지 않음 |
| basic-ci | SUCCESS | 네 Hosted 결과 집계 |
| unity-e2e | SKIPPED | 요청한 false 입력·비활성 조건. remote Unity 검증 미실행 |
| release-readiness | SKIPPED | Release 검증/생성·배포 미실행 |

로컬 단위119는36파일, 원격113은32파일 범위다. 기존 `test_storekit_standalone_classification.py`, `test_unity_consumer_e2e.py`, `test_unity_consumer_result.py`, `test_unity_ios_push_cache.py`의6건은 로컬에서만 실행했다. 이번에 추가/수정한 하네스 단위는 전부 Hosted에 연결했다. 113을 제품/Player 테스트 건수로 취급하지 않는다. 원본 job 로그는 ignored artifacts에만 보존하고 공개하지 않는다.

## 최종 판정·다음 재개점

- **A 완료**: nested tests/checks/samples/players 및 오류·실행 필드 보존, 실제 JUnit/XCTest와 checker/Player 구분, self-check 호환 치환 제거.
- **B 완료**: 실행 관측/source/run/log/parent-child 연결, 타입·누락·중복·0건·오류·재사용·변조·status/exit 불일치 fail-closed. 정상/실패/대기 실제 collector process0/1/2 확인. 새 관측 snapshot·오류 모델 공백도 음성 재현 후 보강.
- **C PARTIAL**: 현재 local119/self9/iOS Push 및 영향 Editor/StoreKit retry PASS. 원래 Strict52PASS/4FAIL/1대기/exit1 보존. Android Push current retry는 **ENV-P09-AVD** 대기. StoreKit 최초 timeout의 간헐 원인은 미확정이며 기존26.5 FAIL과도 별도다.
- **D 완료(Hosted-only)**: FF push와 단일 false-input run SUCCESS. self-hosted/remote Unity/Release 증명은 아니다.

다음 내부 작업: CI 미연결 기존4파일6건의 연결 검토, T04 Testcontainers 계획 차이 정리 및 StoreKit 간헐 증거 보강. 다음 환경 작업: 독점 전용 ADB/AVD 연결·실제 이름 일치를 확보한 뒤 `run-unity-push-current.py`를 current tracked-clean source에서 실행한다. serial 번호만 보고 기기를 조작하지 않는다. self-hosted 격리 준비·실 Provider 자격/실기기 검증은 별도 대기다. 이번에는 P01/P02/P10으로 이동하지 않았다.

P09-T01/T03/T06/T08의 local 상태 변경 근거는 [완료 조건 감사](p09-completion-gap-audit.md)에 제시했다. 원장 상태를 일괄 PASS로 변경하지 않았고 P05-T03 FAIL·ENV-STOREKIT-26 OPEN·Provider WAITING_USER13을 유지한다.

최종 push는 handoff/p09-resume-20261113에 docs만 추가하는 FF다. 최종 문서 commit의 자기 SHA는 Git 이력/채팅 최종 보고에서 대조한다. 원격 실행은8c8fc62에서 완료됐으며 이후 코드 변경은 없다. 기존 미추적 Demo·Python cache, ignored artifacts·DB·AVD·Simulator 디스크를 삭제하지 않았다.

## 배치25 진행

잔여 환경·검증·상태 감사의 후속은 [배치25 evidence](p09-batch25-integrated.md)에 기록한다. 배치24의 실패·미실행·후속 성공은 수정하지 않는다.

### 배치25 후속현재상태

A current-owned Android Push PASS, current Strict57PASS/knownP05FAIL1/신규실패·대기0. P09-T01/T03/T05/T06/T08의local PASS를실제반영했다. T02 assert계측/T04 간헐위험/T07 self-hosted는PARTIAL로유지한다. source·개별상태·후속Hosted는[배치25](p09-batch25-integrated.md)에기록한다. 기존배치24문제관측은삭제하지않는다.
