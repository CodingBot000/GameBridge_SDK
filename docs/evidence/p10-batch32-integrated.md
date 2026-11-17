# 배치32 대형 통합 개발과 검증

인계 branch `handoff/p09-resume-20261113`, 시작 `3639a1d3de15698553bb6c29ad51f0864e01a883`. [source별 정제 검증](p10-batch32-verification.json)이 실행 범위와 한계를 담는다. **T01·T02 구현/로컬 PASS, T03·T04·P11 PARTIAL, 전체 SDK BLOCKED_INTERNAL**이다. 자동 batch 회복과 실제 headless Player를 GUI·Strict·Release 성공으로 바꾸지 않는다.

## A~J 상태

| 항목 | 이번 결과 | 남은 범위 |
| --- | --- | --- |
| A 기준/환경 | 기존HEAD/remote·미추적보존·현재SDK/147/cache/API 확인. Hub4 정상Projects·GUI실제Builder. 자동Editor direct/cli nonce 진단도 실제PASS | Mac CUA 잠금, 실Provider/Release 환경 |
| B 남은 플랫폼 | 현재Core의 새Android Push/UTF8 JNI·새iOS Unity Push/Lifecycle 실제PASS, 실패 원본과source구분 | 실기기·FCM/APNs는 미검증 |
| C T01 판정 | 원본79file Core guard/공개API·Core회귀·변이복원·추가Player gap 해소/self9 근거로 명시 제품조건 PASS | 전체 Strict/SDK Release는 별도 |
| D Native 제품 | 격리후보 두개 실제구현/회귀/패키징 후 T01PASS 뒤 정식두commit. 현재Native회귀·post-change 구매PII 양플랫폼 PASS | 실제 Provider13건 |
| E 측정 | warmup20+100/실제monotonic p50·p95·max·pending/live0·HTTP멱등/409·원장1/100 | 사전계측, Native memory/UI jank/Unity startup 미측정 |
| F 패키징 | 후보와handoff 각각새Maven/AAR/R8·양sliceXCFramework·Swift source/binary·147checksum·선정ABI. 새handoff package실제CLI 소비 | T03미완료로T04전체PARTIAL, 모든ABI·실기기보증아님 |
| G P11 사전감사 | 64Task/증거path/기능문서감사·오래된검증/110checksum표기정정·구현/Mock/실제Provider분리 | OpenAPI계약파일부재(BUG-017), P11전체미완료 |
| H 통합검증 | Python237·Native47/43·Core10/12/418/변이·self9·TC11/변이1·API/wire/선정ABI·실제Player | 전체Strict0/전용전체orchestration未완비 |
| I GitHub | 모든코드·테스트정리후같은handoff FF인계/단일false Hosted계획 | 실제push/run결과는하단후속기록으로갱신 |
| J 인계 | 진행/로그/사용자설정/기능표/보고서·본source별증거갱신 | SDK전체완료/Release선언없음 |

## 실제 플랫폼 결과와 실패 구분

- [Android GUI Push APK](p10-batch32-push-build.json)27,074,492bytes/SHA97a2e42a…, [UTF8 APK](p10-batch32-utf8-build.json)27,073,808bytes/SHA0a4a8b1b…: source8aadcf4의원본Builder·Unity6000.5.8f1·147SDK/cache/주·보조scenario/nonce/log/APK증명PASS. 빌드각check1/test0·Player0과분리했다.
- Push A 및UTF8 A는wrapper새ACK옵션연결누락으로argparse2/실제설치·Player0이었다. source연결/기기전 parser preflight를수정했고기존AVD/자료를보존했다.
- [Push B](p10-batch32-android-push-b.json)는initialize/login/등록·수신중복/mainthread/BG-FG까지실제통과뒤network90.023초/InvalidOperationException으로FAIL. noReconnect marker와코드상90초분기가일치하나예외메시지미출력부분은추론으로구분했다. 중복legacy GUI증명과고정fault대기를보강하되실제명령직전동일강도PID/AVD/양port/server/exe guard·앱90초·원래성공조건을유지했다.
- [Push C](p10-batch32-android-push-c.json), source1ec45b9: 같은APK/SDK의새소유기기에서6필수marker,중복/mainthread/BG-FG/망차단복구/reconnect거절/session/latecallback·최종DBtoken0 PASS. B실패를삭제하지않았고복합하네스수정중어느하나만단독원인이라고단정하지않았다.
- [Android JNI R09](p10-batch32-android-jni.json), sourceb6bd767: 새기기에서전용UTF8 marker/Nativecallback와전체LOCAL_MOCK 구매·Backend·원장1/100 PASS. 일반구매marker만으로JNI를통과시키지않았다.
- [iOS GUI export](p10-batch32-ios-push-export.json)는sourcebf10f53의3076파일/147SDK/원본Builder/트리·PBX/주·보조source를검증했다. [현재 iOS Unity Push](p10-batch32-ios-push.json), source01892c8: 새Simulator/DB의6marker와token0·소유UUID/name/Shutdown확인PASS. 망차단은TCP proxy범위이며OS전체단절·APNs아니다.

### Native 변경 후 새 패키지

정식Native sourceff2d0d5를handoff에서새로빌드한staging147/SHA d11a2b063b488f3a80b75eb9afa30f262c47fccbe3f6a947d7da1f80bcf04959를사용했다. 원래동작하던retained package80669…의Player성공을새Native소스성공으로재활용하지않았다.

Mac잠금이CUA에관측돼수동해제를요청했으며에이전트가잠금을풀거나약관/보안설정을변경하지않았다. 그동안새로운Hub환경의독립direct/cli batch진단이각실제nonce메서드·receiptPASS였다. 이정상원래자동Builder경로를명시선택해후속소비를실행했으며GUIreceipt로위장하지않았다.

초기foreground -L hostname문법은SDK가bind전 거부(기기0)해지원되는localhost기본tcp:5037로정정했다. 그후batch종료가runtimeADB를종료해APK생성뒤설치전 guard가중단(기존기준무시0)했다. [단일분리검증](p10-batch32-build-adb-isolation.json)에서build5038과runtime5037을분리하니같은SDK runtimePID가유지됐고,명시옵션과busy/invalid/다른exe/소유process만정리하는4음성·정상unit을추가했다. 기존daemon을kill/restart하지않고portfree시직접foreground bind한자기server만관리했다. 근거: [공식ADB명령행](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/docs/user/adb.1.md), [환경 endpoint 우선순위의공식구현](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/client/commandline.cpp).

[창표시 후속실패](p10-batch32-post-native-android-failure.json)는Awake뒤Start/SDK/HTTP전에EXIT_SELF0·timeout이었다. 이를NativeAuth원인으로단정하지않았다. 같은코드/설정/CPU2/RAM2GB/이미지/시간제한에서창표시만headless로바꾼[새Android후속](p10-batch32-post-native-android.json), source5bc3cd0은원본CLI Builder·현재Native/package·PII/Native/Backend·원장1/100 PASS였다. [새iOS후속](p10-batch32-post-native-ios.json), sourcedaf3cd9도같은새package의CLI export/Xcode ad-hoc·새18.6Simulator·24marker·원장1/100 PASS,자기기기만shutdown했다. 모든원본실패/기기/DB/로그를보존했다.

## P10-T01와 T02 제품 판정

[T01 판정](p10-batch32-t01-decision.md)은계획의명시제품조건과추가전체Strict/Release를구분했다. 원본Core기준은그대로이며닫힌source4485b2f에서엄격Native/관리표면/wire79file검사를통과했다. 변경전후동일418cohort와새실제Player gap을해소해IMPLEMENTED/PASS로정리했다. 전체SDK완료판정은아니다.

[Native 전후](p10-batch32-native-refactor.md): 별도local candidate/p10-t02-batch32-20261118,제품e6e1de7/fc3da2f,현재보존HEAD21b5f71. T01대기중에는handoff통합/push하지않았고,closing후같은제품bytes를정식5ef87e5/ff2d0d5로각반영했다. 후보는비교이력으로보존하며미통합제품변경은없고원격branch를만들지않았다.

GoogleStoredSession codec/binding은encode/decode/필드·config검증만분리했고profile/save·refresh single-flight/401·cancel/tombstone/offline logout/network전 거부를유지했다. Apple grant decoder는JSON/허용두status/모델생성만분리해attemptID/auth계정/멱등키/late result/downstream acceptGrant/finish/journal을유지했다. 새publicAPI/baseclass/DI·실Provider교체·retention/가격/동시성/재시도정책변경은없다. 기존18→20/20→23와현재넓은Native47/43·fresh소비·post-source실제모의구매PII양플랫폼통과로T02도IMPLEMENTED/로컬PASS다. 실제Provider13건은미검증이다.

CI는원본Corebaseline을덮지않고닫힌Git source에원검사를적용한뒤,승인된Native4경로의정확pre/posthash·추가파일집합과나머지Core/Native/wire byte불변·Cexports를검사한다. 허용파일이라는이유로다른변경을통과시키지않는다. privateCore/wire/export드리프트·경로/내용/원기준hash/없는closingref를거부하는8unit과기존Coreunit을유지한다.

## 수치·테스트·패키지 범위

| 종류 | 실제 확인 | 해석 한계 |
| --- | --- | --- |
| Python | 최종237건/57모듈 failure/error/skip0,25.101초 | 이전229건은CLI소유guard/isolation추가전source |
| Native baseline/후보/정식 | 기존Kotlin18/Swift20 → 각각20/23. 별도후보와현재handoff 넓은Native47/43 각PASS | 주입gateway/HTTP/스토어Fake; 실제OAuth/스토어아님 |
| Core | Kotlin10/helper50,Swift12/helper122,managed418(198정상/220예상오류),복원418/분기419 | test/helper/check를합산하지않음 |
| duplicate-only | 예상process134실패1감지,정상probe0·원본hash불변/정상복원 | 제품testfailure1로변환하지않음 |
| lifecycle | 100samples/helper316·managed객체잔존0 | helper316은시간값아님 |
| self9 | T01판정전과Native/새staging후각9필수PASS,각test47(44정상/3예상negative),checks9 | null/checker errors는모두0으로채우지않음 |
| Testcontainers | 실행11(정상10/의도변이1),변이exit1·정상복원0/격리container정리 | 실제store sandbox아닌synthetic fixture |
| GUI Builder | Android2/ iOSexport1,각check1/test0/Player0 | actualPlayer결과와분리 |
| 실제Player | T01현재Core:AndroidJNI1PASS/PushB1FAIL→C1PASS/iOSPush1PASS. Native변경후Android1FAIL→headless1PASS/iOS1PASS | argv/daemon/binding전 중단은Player실행0,이전배치구매PII/CABI를새실행으로더하지않음 |

[성능](p10-batch32-performance.md)은warmup20을뺀100sample별실제monotonic p50/p95/max와0잔존·800정상응답/100cancel·duplicate/late각100을기록했다. Backend는catalog/동일멱등/409각100(+warmup20)·원장1/100이다. 최초driver의문자열수량오독aggregateFAIL과그때managedPASS를보존하고Backend만새DB에서수정재측정했다. Native/UI/실기기/Unity startup·속도향상·99.9안정성주장없음. T02정식완료전사전계측으로T03전체PARTIAL이다.

[후보패키지](p10-batch32-candidate-package.json)와[신규handoff패키지](p10-batch32-handoff-package.json)는각자실제새source의Maven/AAR/sample/R8·devicearm64/simulatorarm64+x86_64 XCFramework·Swift source와SimulatorSDK binaryimport·147checksum·지정3Java/Cexport4양slice를검증했다. GoogleAuthProvider공개bytecode는compiler synthetic private accessor를제외해동일했다. 후보artifact를handoff신규build로부르지않고모든ABI호환보증도하지않는다. 새handoff패키지실제CLI소비까지확인했지만T03선행/전체Task한계로T04전체PARTIAL이다.

## P11 사전 감사와 미완료

[사전감사](p11-batch32-preaudit.json):64Task/증거path대조·제품TODO표식0,이것이기능완성증거는아니다. README/START_HERE/FEATURE_MATRIX/COMPATIBILITY의계획전용소개·Unity미검증/이전 ENV-002·staging110을현재실측/147로정정했다. 계획된contracts/openapi.yaml은부재(BUG-017)이며실제Controller/docsAPI/Bridge schemas와구분한다. P11전체Task완료로올리지않는다.

P05-T03 FAIL/ENV-STOREKIT-26 OPEN,18.6간헐위험,실Provider13 WAITING_USER,실기기·self-hosted/Release미검증을유지한다. 자동tinyEditor회복은확인했지만기존 fullStrict의전체 wrapper build/runtime ADB·PID소유전파와OS/StoreKit전용컨텍스트가완비·preflight되지않아**전체Strict0/NOT_RUN·DEFERRED_ENV/내부orchestration준비대기(DEP-STRICT-OWNED-ENV)**다. 원래required suite/recorded P05FAIL을삭제/optional로바꾸거나GUI/개별CLI PASS를전체Strict로변환하지않았다.

## Git·CI 인계

이문서초기작성시새remote push/CI는NOT_RUN이다. 최종코드/테스트/실제수정/현재소스검증을모두정리한뒤동일handoffFFpush·repo/비활성Unity변수정상API를확인하고false Hosted-only를1회만실행한다. 배치31의UUID후속수정도현재코드에포함됐다. 실제run결과/최종HEAD는후속기록을따른다. main/force/runner등록/Release·실Provider호출없음. 기존Demo/캐시·사용자프로젝트/기기/DB/라이선스·원본실패는보존했다.

## 다음 실제 작업의 우선순위

1. 전체 Strict 원래orchestrator의전체 lane소유binding/buildendpoint전파·OS/StoreKit컨텍스트preflight를완비하고최대1회현source전체검증. 기존P05FAIL을별도처리한다.
2. Native memory/실제UI·scene전환·실기기프로파일링과T03/T04남은조건. 현재fake/loopback수치와구분한다.
3. Controller와동기화한기계OpenAPI계약문서·P11최종감사(64Task/정확source/생성물/오류코드).
4. USER_SETUP의실Provider13건과StoreKit26.5/18.6위험·전용self-hosted/Release를실제별도검증. MacGUI는수동unlock후필요한시각검증만수행한다.

## 작업별 handoff 커밋

| SHA | 작업 |
| --- | --- |
| `bf10f5330d67dc553e0a06b02e3c5b87e709490a` | test(unity): [P10-T01] validate explicit iOS Push GUI exports and owned cleanup |
| `0d36d9360b7a4da09fa1e9432bdd72374aeb2512` | test(android): [P10-T01] scope explicitly enabled notice acknowledgement for Push regression |
| `48dc7de36d1cd22d411c57b80b9e3917f27a9315` | fix(harness): [P10-T01] forward scoped Push notice option through current-run wrapper |
| `ee2f91013582c6ff3119b9476ed91e90b29bcff8` | fix(harness): [P10-T01] avoid duplicate GUI device proofs within Push recovery windows |
| `b6bd767935fbf09e663660ca4de74a6fba442289` | fix(harness): [P10-T01] preflight GUI notice options in both platform wrappers |
| `1ec45b98d583ca0f0065786017eeec5cee2b0614` | test(android): [P10-T01] record current GUI UTF8 JNI Player success |
| `8a69c00775234ab88e452ddba218c219cdc9d0ee` | test(android): [P10-T01] retain failed run and verified current Push recovery |
| `01892c8e347431a076a85f3530d4b98eec22512f` | test(ios): [P10-T01] bind current Push GUI export to explicit Player verification |
| `4793bc4c1e12258351bc1d168a87e89ebd6144df` | test(performance): [P10-T03] add scoped monotonic managed and local Backend measurements |
| `eff5d5a44a9d8dcb182a94381dab76c82714ade0` | fix(performance): [P10-T03] validate decimal wallet quantities and retain partial measurements |
| `4485b2fec8db8f06ee9405ed4a87de434782d0a1` | docs(core): [P10-T01] close product regression criteria with explicit release limitations |
| `5ef87e59a67889909757afd251ccc02fca3fb240` | refactor(auth): [P10-T02] integrate validated Google stored-session codec after Core closure |
| `ff2d0d5aa864b42ad048faf4dea713e851deaa95` | refactor(purchase): [P10-T02] integrate Apple grant decoder with immutable Core transition checks |
| `b0dcd118deef8c7fc5210aad9a1997f207bb8c4e` | test(integration): [P10-T04] verify fresh Native packages and scoped CLI consumer fallback path |
| `981b5bb95f725726882f190808200252b8630fae` | test(android): [P10-T02] bind automatic consumers to an attested local ADB endpoint |
| `37df6f3c6b455f6e3d4c71722cb7a68dbca87933` | docs(validation): [P10-T02] preserve rejected ADB foreground setup before device creation |
| `0d6df8ff0399c8db1c9da5a83448ceee2055cdb1` | fix(harness): [P10-T02] isolate batch build ADB lifecycle from guarded runtime devices |
| `5bc3cd0565173b980217705b3db0b18f58710047` | test(android): [P10-T02] preserve post-change startup failure before SDK entry |
| `daf3cd97a3811da6f235ff21e4e901a539373773` | test(android): [P10-T02] verify fresh post-refactor Native purchase and PII in headless consumer |

이후증거/CI결과문서commit과최종local/remote SHA는하단인계기록과최종채팅에서실제조회한다.


## 최종 로컬 검증/scan 인계 준비

최종현재코드의Python237/57모듈이모두최종Hosted에연결됐고,Native47/43·선정API/원본Core종결+정확Native전이·manifest/metadata/actionlint/147checksum이통과했다. 변경후양플랫폼CLI E2E가완료돼Mac잠금은필수제품검증의진행차단이아니며선택GUI시각작업만미실행이다. 신규push범위gitleaks exit0/탐지0,이전이력포함scan은정확한b1e3c73 source-hash metadata2건/실제exit1이다. 실제현재Kotlin/Swift test SHA256을독립재계산해검토했고ignore/이력삭제/기준완화없다. 전체push commit/blob에키/서명/개인파일/원본log·DB·license/Library·Temp/APK/IPA/Xcode산출물없음을확인했다.

Repository CodingBot000/GameBridge_SDK public/vars0/runners0의정상API응답과origin handoffancestor관계를확인했다. 이후코드/테스트변경없이고정한source를동일handoffFFpush후false Hosted1회로검증한다. 실제최종run/문서커밋/HEAD는아래최종원격기록으로갱신한다.
