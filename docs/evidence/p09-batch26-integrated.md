# 배치26 P09 잔여 정리 / P10 Core·Bridge

최신 상태는 아래 **A~D 로컬 결과 및 완료 판정** 참조. 앞부분은 작업 중 source별 이력이며 초기 NOT_RUN은 최종 상태가 아니다.

기준6d200b064b5cd8ea5ebca76bf3b58c1bd0086e6d. 명시handoff/p09-resume-20261113 local branch를같은HEAD에서생성해사용한다. 기존fix/main이력·사용자미추적Demo/cache는보존한다.

## A — 실제 assertion 계측

shipping runtime/API는아직변경하지않았다. Kotlin4개Core·Bridge test class의JUnit lifecycle scope와test-only wrapper,Swift4개XCTest subclass/helper,C#registry-smoke의Check/Expect·caller site counter를추가했다. 원래assertion에위임하고값·메시지·file/line·예외판정을약화하지않는다. 같은test에서발생한async호출은lock으로세며겹치는testscope는계측오류로거부한다.

실측초기검증: Kotlin10test/helper50,Swift12test/helper122,C#managed0tests/check1/helper391. XCTest/JUnit testcase수와assertion수는별개다. 기본 framework가제공하지않는assertion pass/fail 세부결과는UNMEASURED다. 직접parse성공·adhoc throw 등래퍼밖implicit failure signal도UNMEASURED로남긴다. Source static-call-site 총수는UNMEASURED이고manifest의declared assertion list는STATIC_MAPPING_NOT_EXECUTIONS로보존한다.

통합초기원본 `core-assertions-cfcx9l9a`, Editor포함 `core-assertions-va33f7nf`: 실제테스트/검사와동적helper호출을구조화했다. stress는5warmup+100samples에서helper316(warmup15/sample300/final1)을실측했다. samples를tests로치환하지않는다. UnityDomainReload Enabled/Disabled2test는각16helper=32를NUnit위임호출에서측정했다.

Mutation초기trace는unknown-ID응답에서먼저실패했다. 이제정상duplicate-only probe0후같은probe를disposable mutated source에서실행해nonzero/RequestRegistry.HandleMessage의NullReferenceException을검사한다. 원본hash전후동일및fullmanaged원본다시391호출/0종료확인. 변이중부분assertion은별도기록하며process실패1을assertion실패1로사용하지않는다.

Python계약5건포함전체136건PASS/skip0,기존API baseline/progress/manifest/diff통과. 입력파일spec경로오참조는ios/Framework/project.yml로정정했고CBridge Xcode test target에도helper를포함했다. 마지막collector는실행이지정한results.xml만읽고freshness를검사한다. 새commit소스에서조건분기ON/OFF와동일cohort를다시실행해P10변경전baseline을고정한다.

R01~R12의report는native shared-test scope와managed선택label/site를구분한다. shared testcase의N회전체를각R의정확한N회로합산하지않는다. JNI Player assertion과미실행범위는UNMEASURED/NOT_RUN을분리한다. A source결과와D현재Native/Unity실행은각각추가한다.

## B — StoreKit18.6 제한 진단

초기 체크포인트: NOT_RUN. 최초실패/정상source·설정·boot/health/checkpoint·경과시간관측을검토하며26.5재조사/timeout증가/성공까지반복하지않는다. 미확정위험은PARTIAL유지.

## C — P10-T01 첫 리팩토링

초기 체크포인트: NOT_RUN. A baseline확정후API/ABI/wire/소스snapshot을기록하고실제중복책임을작게분리한다. 자체동작을Fake로바꾸지않는다. NativeSDK/실행의영향경계를명시한다.

## D — 통합·Hosted·인계

초기 체크포인트: NOT_RUN. 현재Core 변경을빌드해새staging/checksum·실제Native/Unity LOCAL_MOCK 및조건부Strict최대1회검증한다. Hosted false입력1회만실행하고main/force/Release/self-hosted등록활성화는하지않는다. P05FAIL/ENV26OPEN/Provider13WAIT/기기·원격Unity미검증을유지한다.

### A 확정 baseline

source **b6fd5379c8ec31b110904754e744325bd39d61c9**,tracked-clean,`core-assertions-2u0cmwrq` actual exit0/PASS. framework test는Kotlin10/Swift12/UnityEditor2이며managed는tests0/checks1이다. helper invocation은각각50/122/32,managed391. 정상복원은별도391,조건분기OFF는0실행/ON은1실행추가로392(테스트-onlysynthetic config)이다. 동일선언소스라도미진입branch는세지않는다.

R12는warmup15/sample300/final1=316실제호출,samples100을tests로치환하지않는다. duplicate-only정상probe는helper2/exit0,guard제거disposable probe는부분helper1후정확한duplicate응답에서NullReference/nonzero를보였다. 실패process1과assertion실패수는같지않다. 원본SHA동일·정상전체smoke391재실행을확인했다.

shared native testcase의전체N회를R별정확N회로중복배분하지않으며managed는실행label/site선택값을보여준다. declared manifest list는STATIC_MAPPING이다. 래퍼밖implicit signal/전체assertion outcomes·정확한소스callsite총수및이ledger에서미실행JNI probe범위는UNMEASURED/NOT_RUN으로구분했다. 이범위를0이나testcase수로채우지않는다. P10전후동일cohort비교의기준이다.

### B 관측 설계/대조

0b6fb72/4b23529/e46cb65의GameBridge.storekit bytes/SHA동일,shipping SDK runtime도변경없다. 현재Xcode26.6(17F113)과CLI의nonparallel옵션을직접확인했다. 최초실패의정확한Xcode/boot상태·정지시간자료는보존되지않아같았다고임의보충하지않는다. 배치25가비교한Backend준비·session1/매입/원장0대성공1/1/100자료도유효하나단독PASS로RootCause를결정하지않는다.

새test-only관측: ProcessInfo.systemUptime API전후checkpoint,JSON timeline/XCTest attachment,configuration SHA,Xcode version,새owned Simulator의상태와Backend health/test구간경과시간. payload/자격값은수집하지않는다. Python진단3단위PASS,Swiftparse0.

구분가능한조건은boot비용·test실행구간의분리관측이다. --diagnose는새18.6기기를명시boot관측한뒤동일180초XCTest제한으로nonparallel·새DerivedData에서DB recovery를1회실행한다. process는기존명시boot및75초phase제한에API전후trace만더해1회실행한다. 두조건은진단용이며default SDK구매/finish/recovery순서·assertion을바꾸지않는다. 성공해도최초간헐위험을해소했다고주장하지않는다.

### B 제한 실행/위험 분류 완료

source5bca33f:DB `xcode-storekit-e2e-s3e8c47b` actualXCTest1/skip0/exit0,新owned18.6명시boot/nonparallel/새DerivedData. backend-ready8.75s,boot-ready30.92s,teststart32.22s/return67.96s. source와실제.app/PlugIns/testbundle의configurationSHA4ead467555cf567cdbdfed14c7f2b7790123ee9f91ccda4d7053b001b9def19d일치. 첫app-root검색0개를성공으로단정하지않고경로를정정해확인했다.

공식xcresulttool attachment export로15단계timeline수집:첫store.start약5.94s,purchase1.39s,recovery.start1.09s,final.start0.35s. 실제trace원본은owned result의api-attachments에만보존한다.

process `xcode-process-recovery-8qg9cxnf`은같은code及진행문서변경상태에서fresh18.6/새DB/기존phase75초로1회PASS/exit0. prepare/recover PID변경·잔액100확인. API trace에서Transaction.all prepare3.93s/recover0.92s,unfinished0.18s/0.005s. boot/health/launch단계를따로기록했다.

두controlled경로모두증상이재현되지않았다. 정상동작관측은이전정지의원인증명이아니다. 초기boot/version/부분로그한계·SDK/환경가설미확정위험을유지하고이번B조사를종료한다. timeout증가·동일조건반복·26.5재조사는없다. P09-T04 PARTIAL/P05FAIL/ENV26OPEN유지.

### C1 event header 분리

변경전/후matrix+기존cohort418helper/exit0동일. 공통header검증3곳→private1곳,body와callback의미유지.API/Native source/C-export/wire baselinePASS.[상세비교](p10-core-bridge-batch26.md). 후속ownership분리를별도검증/commit한다.

### C2 pending ownership 분리

Finish/finally의동일owner removal을한private경계로모으고lock범위·완료알림순서·ignored구분을유지했다. 전후cohort418동일/exit0,정상duplicate0/변이nonzero,baseline검사PASS. [실제변경비교](p10-core-bridge-batch26.md). D에서현재소스의빌드·Native/Unity·ABI·최종회귀를수행한다.

### D 현재 소스 검증 준비

전체Python143건PASS/skip0,신규4파일도Hosted에연결.API/source/wire/progress/actionlint/diff검사통과. consumerEditor실행은이제checksum뿐아니라실제checkout SDK source일치를요구한다. old147파일staging은새private실행코드와달라실제exit1로거부됐고Unity를실행하지않았다. 현재sourcecommit후Maven/XCFramework/UPM을신규경로에생성한다. 이전산출물을현재제품수정의플랫폼증거로사용하지않는다.

### D 새 산출물 및 post baseline

source dc45a2f tracked-clean의새NativeMaven/Android/R8·XCFramework양slice build0,새UPM147checksum통과. javap3종Nativeclass publicsurface·GB_*4exports양slice동일.[비교원본](p10-core-bridge-batch26.md). postledger core-assertions-zn69jotl:Kotlin10/50·Swift12/122·managed418/restore418/branch419·stress316·Unity2/32 및정확duplicate변이복원PASS. 추가NativebridgeJUnit1/실패skip0. 이후source는검증증거문서만추가되며새stage는current SDKsource와일치한다. fresh self9/actualJNI·C ABI/조건부Strict결과를추가한다.


## A~D 로컬 결과 및 완료 판정 (Hosted 대기)

- **A 완료**: 측정 가능한 실제 helper invocation과 test/expected-error-check/static declaration을 분리하고 duplicate-only 변이 감지·정상 복원을 확인했다. 배치26 명시 완료 조건에 따라 P09-T02 IMPLEMENTED/PASS. 실제 assertion outcomes와 래퍼 밖 implicit signal·JNI 계수는 UNMEASURED다.
- **B 완료(제한 진단·위험 분류)**: 각 controlled 경로 1회 PASS했지만 최초 간헐 현상은 재현되지 않았다. 원인 미확정이며 P09-T04 PARTIAL 유지. 26.5 재조사·timeout 증가·성공까지 반복 없음.
- **C 첫 범위 구현·회귀 확인 / 전체 PARTIAL**: RequestRegistry.cs의 event 공통 header와 pending owner 제거 두 private 책임을 분리했다. public API/wire/native source·선정 binary 표면 보존, 동일 managed418 cohort·mutation·Editor 통과. 현재 Android/iOS Unity Player 전체 회귀가 끝나지 않아 P10-T01 IN_PROGRESS/PARTIAL.
- **D 부분 수행**: Python143, fresh Kotlin/Swift·managed·Editor·stress·mutation·API/선정 ABI 및 self9 완료. 독립 iOS Simulator C ABI XCTest1 PASS. 실제 Android Player 빌드는 LicensingClient IPC 차단으로 raw FAIL/exit1, APK/Player NOT_RUN. 전체 Strict는 실행0/DEFERRED_ENV. Hosted-only는 다음 단일 실행으로 확인한다.

### R01~R12 측정 원장

공개 가능한 구조화 결과는 [p09-batch26-assertions.json](p09-batch26-assertions.json). source dc45a2f, 동일 shipping code의 후속 d86ccc2에서 self/C ABI를 실행했다. 아래 native 수는 **해당 전체 공유 testcase**의 helper 수다. R01/R02/R03 등의 수를 합산해 per-R assertion 총수로 사용하지 않는다. `—`는 이 선택 범위의 attribution 없음이며 실제 실행0이라는 뜻이 아니다. managed 수는 동적 실행 label/site의 선택값이며 전체 smoke418과 같다고 주장하지 않는다.

| R | Kotlin 공유 testcase helper | Swift 공유 testcase helper | Managed 선택 label/site helper | 추가 실제 범위 |
|---|---:|---:|---:|---|
| R01 | 8 | 1 | 1 | — |
| R02 | 8 | 6 | 3 | — |
| R03 | 8 | 6 | 2 | — |
| R04 | — | — | 1 | duplicate-only 변이: 정상 exit0 / 변이 nonzero / 복원418 |
| R05 | — | — | 4 | — |
| R06 | — | — | 2 | — |
| R07 | 11 | 15 | 2 | — |
| R08 | 6 | 5 | UNMEASURED | — |
| R09 | — | 6 | UNMEASURED | 독립 iOS Simulator C ABI1 PASS; Android JNI Player NOT_RUN |
| R10 | 2 | 1 | 200 | — |
| R11 | — | — | UNMEASURED | Unity Editor 2 tests ×16=32 helpers |
| R12 | — | — | UNMEASURED | 5 warmup/100 samples, helpers15+300+1=316 |

framework test pass/fail은 Kotlin10/0, Swift12/0, UnityEditor2/0이고 skip0이다. managed는 tests0/check1, 정상 helper198/expected-error helper220=418이며 프로세스0. expected-error helper는 예상된 예외 거부 조건을 검사하는 호출로 failed test220건이 아니다. K50=37+13/S122=112+10. 같은 native testcase가 여러 R을 다룰 수 있다. 정적 manifest 선언은 STATIC_MAPPING_NOT_EXECUTIONS, 정확한 소스 callsite 총수와 assertion 결과 pass/fail은 UNMEASURED다. 스트레스는 tests0/check1/samples100이며 helpers316을 테스트316건으로 치환하지 않는다.

분기 control은 동일 선언소스에서 OFF0회/ON1회 추가(418→419)를 보여준다. duplicate-only 정상 helper2/exit0, 변이 부분 helper1/nonzero·NullReferenceException을 별도로 보존했다. 원본 hash 불변과 전체 managed418/exit0 복원을 검사했으며 실패 process1을 assertion failure1로 변환하지 않았다.

### 현재 실제 플랫폼 실행과 Strict 환경 한계

self `harness-self-5b5bz9vm`: source d86ccc2,9/9 PASS,tests47(정상44+의도negative3)/checks9/예상 외 failures0/exit0. self-only라 불필요 Simulator 생성 없음.

독립 C ABI `artifacts/batch26/r09-ios-independent`: 같은 source, 새 owned iOS18.6, `testHostPushEventRoutingAndDedup` XCTest1 PASS/failure0/skip0/exit0,35.92초. xcresult의 실제 deviceId와 생성한 전용 기기가 일치한다. 종료 시 이미 Shutdown이었으며 shutdown 명령149 응답 뒤 read-only 상태 확인으로 디스크 보존을 확인했다. macOS의 UTF8 testcase와 다른 실제 Simulator testcase이므로 이를 모든 R09 사례 완료로 바꾸지 않는다.

Android `unity-android-e2e-0tikbq7v`: current staging/source 확인 후 fresh 전용 AVD에서 빌드를 시작했으나 새 Unity Editor가 LicenseClient IPC channel 부재와60초 재연결 실패를8분 이상 반복했다. CLI `license status` active/exit0과 실제 Editor 통신은 다른 관측이다. APK 생성 전이므로 Player0/NOT_RUN. 현재 project/PID 소유를 확인하고 Editor만 종료했으며 raw `RESULT FAIL UNITY_IMPORT_OR_ANDROID_BUILD_FAILED`와 wrapper exit1을 보존했다. SDK assertion failure나 PASS로 해석하지 않는다. root R09 runner는 Android 실패 뒤 iOS를 호출하지 않았으므로 위 C ABI는 별도 신규 실행이다. 런타임 문제의 정확한 원인은 미확정이다.

full용 AVD 두 개도 PID·console/ADB port·serial·이름·boot READY까지 확인했지만 Unity runtime 준비 조건은 충족하지 못했다. `c-run-request.json`/`c-full.log`가 없으며 전체 `ci-unity-e2e.sh` 호출0/Strict DEFERRED_ENV. 준비 controller만 중단해 finally에서 소유 emulator를 종료했고 모든 AVD/Simulator 디스크와 DB/로그·기존 사용자 기기를 보존했다. 이번 실행에서는 Player UI/네트워크 조작 단계에 도달하지 않아 안내 UI 보조도 발생하지 않았다. 배치25 Strict57PASS/기존P05FAIL1은 역사 증거이며 이번 source의 Strict 결과가 아니다. 새 제품 testcase 실패0을 증명한 전체 Strict가 있다고 주장하지 않는다.

현재 Player·Strict 재개 절차는 [USER_SETUP](../USER_SETUP.md)의 배치26 환경 항목과 current staging/source 검사 및 기존 owned device gate를 따른다. 이전 산출물을 재활용해 PASS 처리하지 않는다. 실제 OAuth/스토어/FCM/APNs·실기기는 미검증, Provider13 WAITING_USER/P05-T03 FAIL/ENV-STOREKIT-26 OPEN/self-hosted·Release 미검증은 유지한다.
