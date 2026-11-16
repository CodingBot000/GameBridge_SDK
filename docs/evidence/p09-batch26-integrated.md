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
