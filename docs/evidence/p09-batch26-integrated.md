# 배치26 P09 잔여 정리 / P10 Core·Bridge

기준6d200b064b5cd8ea5ebca76bf3b58c1bd0086e6d. 명시handoff/p09-resume-20261113 local branch를같은HEAD에서생성해사용한다. 기존fix/main이력·사용자미추적Demo/cache는보존한다.

## A — 실제 assertion 계측

shipping runtime/API는아직변경하지않았다. Kotlin4개Core·Bridge test class의JUnit lifecycle scope와test-only wrapper,Swift4개XCTest subclass/helper,C#registry-smoke의Check/Expect·caller site counter를추가했다. 원래assertion에위임하고값·메시지·file/line·예외판정을약화하지않는다. 같은test에서발생한async호출은lock으로세며겹치는testscope는계측오류로거부한다.

실측초기검증: Kotlin10test/helper50,Swift12test/helper122,C#managed0tests/check1/helper391. XCTest/JUnit testcase수와assertion수는별개다. 기본 framework가제공하지않는assertion pass/fail 세부결과는UNMEASURED다. 직접parse성공·adhoc throw 등래퍼밖implicit failure signal도UNMEASURED로남긴다. Source static-call-site 총수는UNMEASURED이고manifest의declared assertion list는STATIC_MAPPING_NOT_EXECUTIONS로보존한다.

통합초기원본 `core-assertions-cfcx9l9a`, Editor포함 `core-assertions-va33f7nf`: 실제테스트/검사와동적helper호출을구조화했다. stress는5warmup+100samples에서helper316(warmup15/sample300/final1)을실측했다. samples를tests로치환하지않는다. UnityDomainReload Enabled/Disabled2test는각16helper=32를NUnit위임호출에서측정했다.

Mutation초기trace는unknown-ID응답에서먼저실패했다. 이제정상duplicate-only probe0후같은probe를disposable mutated source에서실행해nonzero/RequestRegistry.HandleMessage의NullReferenceException을검사한다. 원본hash전후동일및fullmanaged원본다시391호출/0종료확인. 변이중부분assertion은별도기록하며process실패1을assertion실패1로사용하지않는다.

Python계약5건포함전체136건PASS/skip0,기존API baseline/progress/manifest/diff통과. 입력파일spec경로오참조는ios/Framework/project.yml로정정했고CBridge Xcode test target에도helper를포함했다. 마지막collector는실행이지정한results.xml만읽고freshness를검사한다. 새commit소스에서조건분기ON/OFF와동일cohort를다시실행해P10변경전baseline을고정한다.

R01~R12의report는native shared-test scope와managed선택label/site를구분한다. shared testcase의N회전체를각R의정확한N회로합산하지않는다. JNI Player assertion과미실행범위는UNMEASURED/NOT_RUN을분리한다. A source결과와D현재Native/Unity실행은각각추가한다.

## B — StoreKit18.6 제한 진단

NOT_RUN. 최초실패/정상source·설정·boot/health/checkpoint·경과시간관측을검토하며26.5재조사/timeout증가/성공까지반복하지않는다. 미확정위험은PARTIAL유지.

## C — P10-T01 첫 리팩토링

NOT_RUN. A baseline확정후API/ABI/wire/소스snapshot을기록하고실제중복책임을작게분리한다. 자체동작을Fake로바꾸지않는다. NativeSDK/실행의영향경계를명시한다.

## D — 통합·Hosted·인계

NOT_RUN. 현재Core 변경을빌드해새staging/checksum·실제Native/Unity LOCAL_MOCK 및조건부Strict최대1회검증한다. Hosted false입력1회만실행하고main/force/Release/self-hosted등록활성화는하지않는다. P05FAIL/ENV26OPEN/Provider13WAIT/기기·원격Unity미검증을유지한다.

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
