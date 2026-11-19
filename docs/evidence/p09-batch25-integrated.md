# P09 잔여 검증·안정화 배치25

## 최신 상태 — 배치25 수행 종료

A 실제Android Push PASS, B 간헐위험분류/Testcontainers구현·실검증 완료, C 전체Strict1회는57PASS/기존P05기록FAIL1/신규실패·대기0이다. 전체PASS로재작성하지않는다. D에서T01/T03/T05/T06/T08의local완료조건을개별확인해IMPLEMENTED/PASS로변경했고,T02/T04/T07은PARTIAL을유지했다. 아래NOT_RUN/초기실패는당시기록이다. Hosted-only run43889958441 전체SUCCESS(5jobSUCCESS,Unity/ReleaseSKIPPED). 실제Provider·self-hosted·Release완료를뜻하지않는다.


기준 f6915e35f28e06a0d88e053a66883505bc7bc881. local fix/unity-android-mock-e2e-evidence에서 작업하고 handoff/p09-resume-20261113으로 관련 커밋만 FF push한다. A~D 순차 진행, 실제 Provider·main·force·Release·P01/P02/P10 변경 없음.

## A — AVD 연결 조사/보호

읽기 전용 조사: 현재 실행 중인 비전용 emulator 한 개의 요청 console5560과 실제 listen5560/5561 owner PID89772가 일치했다. 해당 AVD는 변경하지 않았다. 최초 adb devices 조회는 daemon 부재로 CLI가 자동 시작을 출력했으며 server kill/restart/초기화는 수행하지 않는다.

배치24의 요청5570·자기 PID93858은 실제 console/ADB 소유 증거가 없었고 해당 serial 조회는 다른 AVD 이름을 반환했다. PID가 살아 있고 인자에 -port가 있다는 사실은 실제 socket 소유와 같지 않다. 당시 최초 bind/포트 경쟁 시점의 증거가 없으므로 OS 차원의 원인은 미확정이다. 실기기/타 AVD로 재현해 충돌시키지 않는다.

`emulator_binding.py`는 ps의 qemu/AVD/요청 port, lsof의 console·ADB 두 port owner를 함께 확인한다. Push runner/CI는 GAMEBRIDGE_PUSH_EMULATOR_PID를 요구하며 매 기기 명령 전 재검증한다. cleanup도 기존 실패를 숨기거나 타 기기에 전송하지 않는다. guard·binding·CI·증거 검사 단위 **16건 PASS/skip0/exit0**. 실제 Player는 아직 NOT_RUN. 원본 조사 자료는 ignored artifacts/batch25에만 보존한다.

다음은 free port와 새 전용 AVD를 준비한 뒤 실제 serial·이름·PID·두 port의 일치 여부를 확인한다. 확인 불가 시 DEFERRED_ENV로 기록하고 B로 이동한다.

## B — StoreKit/DB 계획 차이

NOT_RUN. 배치24 최초 실패와 단독 성공, 동일 코드 범위와 checkpoint/로그 한계를 비교한다. 26.5 재조사나 timeout 증가·성공까지 반복은 하지 않는다. Testcontainers 요구와 현재 별도 PostgreSQL 방식을 비교해 처리 방향을 확정한다.

## C — 하네스/CI 범위/조건부 Strict

NOT_RUN. 기존 미연결4파일6건을 조사하고 Hosted 적합 시 연결한다. 현재 하네스 단위와 새 격리 자체시험9 lane을 실행한다. A 실제 Android Push PASS와 새 전용 전체 환경이 모두 확인돼야 ci-unity-e2e.sh 전체 Strict를 최대1회 실행한다. mapping50은 실제 테스트 수에 합산하지 않는다.

## D — 감사/인계

NOT_RUN. 개별 P09 상태 변경은 실제 근거 및 원장 검사로 판단한다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN/Provider13 WAITING_USER/self-hosted·Release 미검증을 유지한다. 로컬 검증 후 비밀정보·범위 검사, handoff FF push, 변경된 Hosted 테스트가 있고 Unity 변수 안전 확인 가능 시 false 입력 dispatch1회만 수행한다.

### A 실제 실행 완료

source **b55ffe722cfd9bd2663cd3e193343cebb0b4c202**, tracked-clean, Android Push actual exit **0/PASS**, 원본 `artifacts/unity-android-push-l_yu9kmb`. 새 전용 GameBridge_V2_B25_A_PUSH_20261116 / emulator-5582 / PID22235 / console5582·ADB5583 owner 일치. 전체 기기 명령마다 다시 검증했다.

필수 marker7개 모두 존재. mockPush/수신·deduplication/mainThread/background/networkRecovery/reconnectFailure/sessionSwitch PASS, rejectedReconnectAttempts **2**, deviceTokens **0**. 새 앱의 systemui Viewing full screen/Got it을 실제 UI dump로 확인 후1회 클릭했다. UI 보조이며 시스템 상태 우회나 무인CI 입증이 아니다. FCM/APNs/실기기 검증이 아니다.

A는 실제 current-source Player1 PASS로 완료. ENV-P09-AVD local RESOLVED. 최초 OS port 경쟁 시점은 미확정이나, serial·요청 인자와 실제 소유가 같지 않았다는 선행 문제를 PID/양쪽 listen-port 검증으로 차단했다. 처음 실패한 배치24 자료는 보존하며 새 환경에서 통과한 것으로 구분한다. A 전용 프로세스만 종료했고 디스크를 보존했다.

### B StoreKit 비교 결과

| 경로 | 최초(source0b6fb72) | 단독 retry(source4b23529) | 판단 |
|---|---|---|---|
| local DB recovery | a3aicym0:180초 timeout/testExit124, xcresult Info.plist 미완결·부분stdout 폐기 | zk9hcbqp:XCTest1 PASS/skip0/exit0 | 실패 시정지위치미확정. 성공으로원인해소처리불가 |
| process recovery | s3d3ilfe:prepare/store-history 진입후75초 phase timeout | r2r9s3db:prepare/recover 잔액100·서로다른PID/exit0 | Transaction.all/unfinished 어느호출인지당시미분리. 이후checkpoint분리 |

두 runtime source 사이 및 현재까지 SDK runtime 코드 diff는 없다. timeout은늘리지않았다. 네전용DB읽기전용대조: 최초둘 sessions1/purchases0/ledger0/delta0, 성공둘 sessions1/purchases1/ledger1/delta100. Backend 시작은네경우모두확인되지만 StoreKit 개발경로는 LOCAL_MOCK_TRACE 계측대상이아니라 trace0으로요청미발생을추론할수없다. 당시 bootstate/부하로그도없어 cold boot·동시성·SDK원인을확정하지않는다. 현재네device는모두Shutdown이며 이는실패당시상태가아니다.

**미확정 간헐 runtime 위험 유지**: 처음DB timeout과history timeout을동일원인으로묶거나retry PASS로제거하지않는다. 이번B에서StoreKit실행반복/timeout증가/26.5재조사는하지않았다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN 유지.

### B Testcontainers 계획 차이 처리

기존별도Docker PostgreSQL+fresh schema는실제SQL·경쟁·rollback·원장제약·복구를검증했지만 Testcontainers의컨테이너수명관리구현을대체했다고기록하지않는다. 원계획도구요구를충족하도록별도opt-in Gradle init+Python runner를추가했다. 일반backend/SDKclasspath와기존fixture/assertion을바꾸지않는다.

- Testcontainers **2.0.5**, PostgreSQL **17.6-alpine3.22**, JDBC **42.7.11**, Flyway **11.7.2** 고정. 뒤둘은기존backend해결버전이다. [공식release](https://github.com/testcontainers/testcontainers-java/releases/tag/2.0.5), [PostgreSQL구현](https://github.com/testcontainers/testcontainers-java/blob/2.0.5/modules/postgresql/src/main/java/org/testcontainers/postgresql/PostgreSQLContainer.java), [Gradle init](https://docs.gradle.org/current/userguide/init_scripts.html), [task finalizer](https://docs.gradle.org/current/userguide/more_about_tasks.html#sec:finalizer_tasks).
- 새container별임의자격정보/unique run label,127.0.0.1랜덤port강제·실제binding확인,fsync=on,전체프로젝트Flyway+mock migration 적용. 기존5개local fixture는각자의fresh schema/고유row를유지한다. Sandbox2개HTTP fixture는별도empty container에서기존Spring migration/profile 보호를사용한다. 실제Google/Apple호출이아니다.
- mutation은새schema에서만제약을손상하며기존named assertion실패여야한다. 다른실패1건은거부한다. `finalizedBy`로owned container정리후Docker inspect의명시not-found를확인한다. 권한/daemon오류는삭제성공으로기록하지않는다.

실행 `run-purchase-testcontainers.py --run-local`, 원본 `purchase-testcontainers-81ofwf3_`:

| Case | tests | failures | errors | skipped | Gradle exit | 판정 |
|---|---:|---:|---:|---:|---:|---|
| local5개class | 7 | 0 | 0 | 0 | 0 | PASS |
| named ledger mutation | 1 | 1(예상) | 0 | 0 | 1 | 감지PASS |
| normal ledger restoration | 1 | 0 | 0 | 0 | 0 | PASS |
| sandbox synthetic HTTP2개class | 2 | 0 | 0 | 0 | 0 | PASS |

총11 실제test실행(정상10+예상failure1),검사4개,wrapper exit0. 네container모두정리확인. source9c94234+아직미커밋인새harness의초기실행이며commit-source 검증은C에서구분해추가한다.

초기실패도보존: nullable label map compile거부/0 tests(ctkyzc8e),public migration미비로Finalization2실패(q94dolww),실제7testPASS이나Docker소문자not-found 파싱실패로wrapperFAIL(4xqzc9zk). assertion이나격리를완화하지않고migration·파서만보강했다. 관련독립단위5건PASS.

### C 하네스/Hosted 범위 보강

이전미연결4파일6건은StoreKit상태분류fixture,consumer결과JSON/XML,정확한package version임시복사검사로외부도구없이실행된다. 전부inventory에연결했고새binding/TC단위도연결해 **38파일** 전체가일치한다. 전체Python **131건 PASS/skip0/exit0**. backend Hosted는기존서비스DB시험과별도로새Testcontainers경로를실행한다. false입력·Unity비활성조건은유지했다.

Strict는TC를별도required lane으로기록한다. tests11/expectedFailures1,outer검사1과내부검사4를분리하고원본JUnit failure1/Gradle1은유지한다. TC opt-in/환경이없으면DEFERRED_ENV이며기존PostgreSQL결과로대체하지않는다. static mapping50은실제test합계에포함하지않는다.

self-only 실행은필요없는iOSproject/Simulator를생성하지않는다. Native/Editor/StoreKit/전체Strict 성공을뜻하지않으며기존9개필수자체시험은유지한다. 실행source확정후실제결과를이어기록한다.

### C 실제 사전 검증/조건부 전체 실행

source **43d255a39f9efd28e630fad40889cec9d255365d**:

- 전체Python131건 PASS/skip0; 38파일모두Hosted 연결.
- 새전용DB self-check `harness-self-rl7_n0r_`, orchestration `strict-isolated-1wj1cs8b`:9/9 PASS/exit0,tests47(정상44+예상mutation failure3),checks9. 사용하지않는Simulator는생성하지않았다.
- Testcontainers `purchase-testcontainers-86d9mge4`:4case/11실제test(정상10+예상원장failure1),4검사,wrapper0,Gradle0/1/0/0,errors/skip0,네owned container정리확인. 새named mutation 검사도현재commit에서검증했다.

C용fresh PII/PUSH AVD를별도생성했다. PII serial5578/PID36894/ports5578·5579,Push serial5580/PID36901/ports5580·5581의이름·PID·실제양port소유·boot를확인했다. user AVD/ADB server는건드리지않았다. Unity license active 및staging147파일검사통과. A독립Android Push PASS와별도C환경이모두준비돼,다음문서commit후기존ci-unity-e2e.sh전체경로를**1회**실행한다. 18.6 StoreKit을사용하고26.5를재조사하지않는다. 최초전체결과나새실패를숨기지않으며source고정중중간runtime관측은ignored checkpoint에보존후검증종료시정식문서로갱신한다.

### C 전체 Strict1회 결과

source **e46cb6520272334d9816d951274b91bd39133b9b**,tracked-clean. 원본 `verify-all-q_sj2gpu`, orchestration `strict-isolated-r5mw4kpc`, gate `artifacts/batch25/c-full.log`. 전체58lane: **57PASS/기존기록FAIL1/신규FAIL0/대기0**,exit **1**. 실패행은 recorded-unresolved-failures/P05-T03이며이번에26.5를재실행한것이아니다. 전체경로/Strict는최대1회조건대로1회만실행했다.

| 실행별 측정 | 값 | 범위 |
|---|---:|---|
| 상위tests | 226 | self의예상실패3+TC예상실패1포함. 전부제품정상PASS226건이라는뜻이아님 |
| 상위checks | 57 | static mapping alias1포함,고유receipt56. TC내부검사4는별도 |
| samples | 100 | lifecycle stress,tests와분리 |
| players | 4 | 현재Android/iOS PII2+Push2 |
| static mapping | 50 | 실제tests합계에포함하지않음 |

- PII `unity-pii-current-hsboynxv`: Android `unity-android-e2e-drwn26tt`,iOS `unity-ios-e2e-qpw5_qo8`,각ledger1/delta100/PII검사PASS.
- Android Push `unity-android-push-40qhuo7b`:PID36901/ports5580·5581/이름·serial일치,모든markerPASS,reconnect거절2,실제emulator망차단/복구PASS,deviceTokens0.
- iOS Push `unity-ios-push-vqc2s1vc`:모든markerPASS,reconnect거절6,networkRecovery=PASS_LOCAL_TRANSPORT_FAULT,deviceTokens0. 실제OS전체망차단으로기록하지않는다.
- 두Player모두source일치·tracked-clean. 두새Android AVD의초기전체화면안내는각1회실제관측후클릭했다. 시스템상태우회는하지않았으며무인CI성공으로주장하지않는다.
- StoreKit18.6 DB `xcode-storekit-e2e-ke7399o2` actualXCTest1/exit0,process `xcode-process-recovery-belki2xf` 실제재시작복구/exit0 PASS. 최초배치24의간헐위험은원인미확정으로유지한다.
- 현재self9/TC11/Native합성회귀/Editor 및패키징검사도PASS. mock과real Provider를분리하며외부13 WAITING_USER는유지한다.

완료된이번실행전용Simulator/AVD process만종료했고디스크·전용DB·원본증거는보존했다. source고정중관측은ignored checkpoint에보존했고검증종료후정식원장에반영했다.

## D 개별 Task 감사·상태 반영

| Task | 최종 구현/local | 완료 확인·남은 조건 |
|---|---|---|
| P09-T01 | IMPLEMENTED/PASS | required50 ID/entry·fixture잘못된값거부·정상복원·미실행platform제외금지. mapping50은actualtest가아님 |
| P09-T02 | IN_PROGRESS/PARTIAL | core/bridge·duplicate guard mutation·복원·stress100확인. 실제assert총수미측정으로완료승격보류 |
| P09-T03 | IMPLEMENTED/PASS | synthetic auth48·sandbox fake-token401 case1·current PII2Player. realGoogle/Apple은별도13대기 |
| P09-T04 | IMPLEMENTED/PARTIAL | Testcontainers literal요구는실행경로·11case·정확변이감지로충족. 기존SQL/Native회귀유지. 18.6간헐원인미확정위험을추적해localPARTIAL 유지 |
| P09-T05 | IMPLEMENTED/PASS | 현재소유검증Android/iOS Push2+PII2·Native/Host/packaging음성. mock/OS범위·UI보조구분,실제remotePush/기기미검증은별도 |
| P09-T06 | IMPLEMENTED/PASS | 전체Python131·실제Strict58lane·정상/오류/대기0/1/2·측정/소스/증거/소유판정. knownFAIL보존 |
| P09-T07 | IMPLEMENTED/PARTIAL | 38파일모두Hosted연결·TC backend추가·actionlint/localCI경로확인. 현재runner등록0,repository변수0. 실제self-hosted/Release미검증유지 |
| P09-T08 | IMPLEMENTED/PASS | 현재새전용환경9lane/예상negative3/정상복원/독립401실제실행,누락·0건·위조결과차단 |

5개local PASS와3개PARTIAL을개별반영했다. 전체원장64행에서구현/검증집계를자동재계산했다: IMPLEMENTED21/IN_PROGRESS43, localPASS19/FAIL1/PARTIAL44. 외부13 WAITING_USER 및P05-T03 FAIL/ENV-STOREKIT-26 OPEN 유지. 원장편집첫시도는blocker참조를중복행으로오인해쓰기전assert1로중단했고행시작판정으로수정했다. 실제상태반영후verify-progress/문서음성/manifest/diff검사exit0이다.

현재남은P09내부작업은T02 assertion계측·T04 간헐원인의추가관측이다. Testcontainers도구차이·CI미연결4파일·현재AVD연결대기는이번에해소했다. self-hosted는별도전용격리환경및emulator소유/PID를job마다제공하는준비가필요하며이번에등록/활성화하지않는다. 실제Provider/실기기·Release도별도대기다. P01/P02/P10으로전환하지않았다.


## D 원격 Hosted-only 최종 결과

[run43889958441](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43889958441), source **59b98349689171cc8a75d9652f248708645a85c2**, workflow_dispatch, `release_validation=false`, repository변수0/runner등록0확인후한번만요청했다. **workflow SUCCESS**,자동재실행없음.

| Job | 실제 결과 | 범위 |
|---|---|---|
| inventory-contracts | SUCCESS | 38 unittest suite/131건 PASS,FAILED요약0. 로컬에서만실행됐던4파일6건도이번원격실행포함 |
| backend-postgres | SUCCESS | 기존synthetic key/별도PG JUnit13 PASS. 추가owned TC11실제test/검사4/예상원장failure1/복원/cleanup PASS,Gradle0·1·0·0 |
| android-native | SUCCESS | Native fake/transport/offline 및Maven/R8별도consumer |
| swift-ios-simulator | SUCCESS | Swift XCTest17/실패0,synthetic iOS Host의>0·실패/skip0검사통과. Host정확건수미출력 |
| basic-ci | SUCCESS | Hosted4개집계 |
| unity-e2e | SKIPPED | false입력/비활성조건,remote Unity미검증 |
| release-readiness | SKIPPED | Release준비검증·생성·배포미실행 |

원격131과로컬131은이제동일38파일범위다. 실제SQL/Native/XCTest/Player계수는별도이며unit131을제품실행131건으로합산하지않는다. 원본job로그는ignored artifacts/batch25에만보존한다. remoteUnity/실Provider를검증한것으로기록하지않는다.

## 최종 인계·잔여

- **A 완료/PASS**: 실제PID·양port소유와AVD이름을재검증하는새전용환경의Android Push PASS. 선행OS bind/경쟁시점은미확정이며serial만으로판단하지않는다.
- **B 완료(위험분류/구현·검증)**: 최초StoreKit18.6실패는증거한계로원인미확정간헐위험유지. Testcontainers요구차이는기존assertion/격리를유지한별도실행경로로해소.
- **C 수행완료**: unit131/self9/TC11/currentPlayers4와전체Strict1회. Strict는57PASS/기존P05FAIL1/신규실패·대기0,exit1로유지. 전체PASS로재작성하지않는다.
- **D 완료(Hosted-only)**: P09별5개localPASS/3개PARTIAL상태반영·원장/음성검사통과·FF push·원격단일실행SUCCESS. 전체P09/SDK/Release완료선언은아니다.

남은내부작업: T02 actual assertion총수계측,T04 간헐정지구간/기기상태·부하관측. 외부환경작업: 전용self-hosted계정·격리및job별ownedAVD/PID제공/실행,실제Google/Apple/FCM/APNs/실기기검증. P05-T03 FAIL/ENV-STOREKIT-26 OPEN/실Provider13 WAITING_USER유지. 기존사용자AVD/Simulator/개발DB/미추적Demo·cache를삭제하지않았다. main·force·Release·ADB server전체재시작·광범위kill은수행하지않았다. 최초read-only ADB조회에서daemon자동시작된관측은A기록에분리했다.

최종보고문서commit은handoff/p09-resume-20261113으로FF push한다. 자기SHA는Git이력/최종보고에서대조하고이문서에순환기록하지않는다. Hosted source이후코드는변경하지않았다. P01/P02/P10으로전환하지않았다.

## 커밋·실행 source 관계

| Commit | 범위 |
|---|---|
| `b55ffe722cfd9bd2663cd3e193343cebb0b4c202` | fix(harness): [P09-T05] attest emulator process and port ownership |
| `9c942349975c2d4c05deb0d3e8f815c12cc4ab59` | test(harness): [P09-T05] verify owned Android mock push player |
| `1a58915d01df23107c32b917587bca9510098e86` | test(harness): [P09-T04] run purchase invariants in owned Testcontainers |
| `43d255a39f9efd28e630fad40889cec9d255365d` | test(harness): [P09-T06] connect complete unit inventory and container lane |
| `e46cb6520272334d9816d951274b91bd39133b9b` | test(harness): [P09-T08] establish current self-check and strict prerequisites |
| `628a1c221bb41d89622bfd5961810ccd6eecc42e` | test(harness): [P09-T06] record current strict baseline with known StoreKit failure |
| `2b2b6b738f901900ca9c37e5a2dd91571f9c3cc2` | docs(harness): [P09-T06] apply evidence-backed local task states |
| `59b98349689171cc8a75d9652f248708645a85c2` | docs(ci): [P09-T07] record batch25 handoff preflight |

A 실제Android Push는b55ffe7,commit된TC/self9 사전검증은43d255a,전체Strict·4Player는e46cb65,Hosted는59b9834에서실행했다. 이후최종문서만변경했다. 최종문서commit SHA는Git이력/채팅마지막인계에서확인한다.


## 배치26 후속 — assertion 계측 및 Core 리팩토링

[배치26 통합 증거](p09-batch26-integrated.md)와 [구조화 계측](p09-batch26-assertions.json)이 배치25의 T02 미측정 gap을 보강했다. 실제 helper 수/예상 오류 검사/testcase/정적 매핑·공유 scope를 분리하고 정확 duplicate-only mutation·원본 복원도 확인해 T02 local IMPLEMENTED/PASS로 전환한다. 전체 assertion outcomes/일부 JNI scope는 UNMEASURED이며 모든 플랫폼 current Player PASS라는 의미가 아니다.

T04는 StoreKit18.6 controlled 경로 각1회 PASS에도 최초 간헐 원인 미확정으로 PARTIAL, T07은 전용 self-hosted/Release 미검증으로 PARTIAL 유지. T01/T03/T05/T06/T08 기존 localPASS 근거는 유지한다. P10-T01은 두 private Core 개선·새 패키지/API·선정 ABI·계측/Editor/자체시험·독립 C ABI를 검증했으나 새 Android Unity 빌드가 LicensingClient IPC 차단(raw FAIL/exit1, Player NOT_RUN)으로 멈춰 IN_PROGRESS/PARTIAL. 이번 전체 Strict는 실행0/DEFERRED_ENV이고 배치25 Strict/Player 결과는 역사 증거로 보존한다. P05 FAIL/ENV26OPEN/Provider13WAIT·실기기/원격 Unity 미검증 유지.

배치26 최종Hosted sourcec34b419의 [단일run43934095574](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43934095574)은SUCCESS,Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED였다. 원격unit42파일/143건확인. 이는현재Player 미실행/Strict0회 및18.6원인미확정을해결하지않으며위후속상태를유지한다.
