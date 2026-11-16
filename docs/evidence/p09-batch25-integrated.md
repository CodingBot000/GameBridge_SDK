# P09 잔여 검증·안정화 배치25

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

- Testcontainers **2.0.5**, PostgreSQL **17.6-alpine3.22**, JDBC **42.7.11**, Flyway **11.7.2** 고정. 뒤둘은기존backend해결버전이다. [공식release](https://github.com/testcontainers/testcontainers-java/releases/tag/2.0.5), [PostgreSQL구현](https://github.com/testcontainers/testcontainers-java/blob/2.0.5/modules/postgresql/src/main/java/org/testcontainers/postgresql/PostgreSQLContainer.java), [Gradle init/finalizer](https://docs.gradle.org/current/userguide/init_scripts.html).
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
