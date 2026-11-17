# 배치29 Unity GUI 빌드 경로 검증과 P10 재개

## 현재 결과 — 재개 후 E 인계 준비

사용자중단요청은재개지시로해제됐다. 아래초기NOT_RUN/중단표시는시각별이력이며현재판정과구분한다.

| 구간 | 실제 결과 | 한계 |
|---|---|---|
| A GUI Editor 메뉴 | PASS,실제컴파일/메서드·nonce/project/version·Unity객체7조건·receipt/로그 | batch자동화PASS아님;최초CS0619수정실패기록보존 |
| B Android GUI APK | PASS,27072192bytes/SHA dd09b532c842ee60116e57785e5b7add25f40a7f7d0deab486872e16c4b628e4 | 기존BuildMockPlayer그대로,Player실행과별개 |
| C Android LOCAL_MOCK | FAIL/UNITY_PLAYER_RESULT_TIMEOUT,설치Success/ActivityStatus:ok후180초완료marker없음 | 새DB users/sessions/purchases/ledger모두0,원인미확정,UI원인단정없음 |
| B iOS GUI export | PASS,3076files/treeSHA fd7c2c6bd7f800d6a13fb9cdf6317f430e5ffc9f86aa812eb1ac702bb24e5a85 | 실제Xcode project생성,기존BuildMockIosPlayer그대로 |
| C iOS LOCAL_MOCK | PASS,Xcode ad-hoc Simulator build/C ABI4symbol/24marker·PII/Backend·원장1/delta100 | 실제Apple/스토어/APNs·실기기시험아님 |
| D P10-T01 | IN_PROGRESS/PARTIAL | Android실행FAIL·전체플랫폼/Strict미완료,GUI성공으로우회없음 |
| D P10-T02 | IN_PROGRESS/PARTIAL,제품변경0 | 독립후보test Kotlin18/Swift20 PASS(신규3+2),코드리팩토링진입없음 |
| E 영향회귀 | Python171/47module PASS/skip0,GUI22+관련단위포함 | 이전169PASS후새가드/aux변경으로최종171재검증;fullNative/self9/418미재실행 |
| E Hosted | 아직NOT_RUN/dispatch0 | 모든소스commit후비활성변수정상응답확인·false단1회예정 |

[구조화된전체범위](p10-batch29-verification.json)에source와검사종류를기록했다. GUI/batch,build/export/Player,현재/과거,실제실패/예상negative/미실행을합산하지않는다.

### 현재 source와 실제 실행 연결

- A GUI probe `dcc0b4c`,Android GUI build `7263444` 및실행 `7520cbc`,iOS GUI export `953a5a5` 및E2E `d543556`. source head가다른경우source ancestor와보호SDK/Builder/scenario 경로diff0·현재복사본/manifest·실제artifacthash를명시검증했다.
- iOS Helper의실제C#컴파일/GUI메뉴/원본Builderreturn·package147/nonce/log·PBX/exporttree SHA PASS. Xcode/Simulator는source d543556 tracked-clean에서실행했고서버권위wallet delta100/원장1을확인했다. 실제생성기기8D737ECF-CD32-4069-A64D-30D3D5176210는새DBsuffix와name대조뒤해당UUID만shutdown,데이터보존.
- Android는새AVD GameBridge_V2_B29_GUI_PII_20261117_85e0/PID80979/serial5590/console5590·ADB5591양port를확인했다. 기존5037 serverPID79436·Unity SDK실행파일을모든ADB호출전가드했고다른SDK/client·다른serial·server kill/start는차단했다. 종료는controller자기Popen emulator만,DB/AVD/APK/원본log보존. CUA가Qt emulator를앱표면으로노출하지않아UI관측/조작이불가능했던한계는확정원인이아니다. 현재timeout원인미확정,동일실행재시도없음.
- 검증용Android GUI는정상Quit했고현재iOS 소비GUI project만idle로열려있다. 기존사용자project/기기/DB/라이선스를삭제하지않았다. batch28의과거다른SDK ADB종료경고대상은여전히미확정이며이번소유검증으로과거영향을추정하지않는다.

### 하네스 입력 계약과 회귀

명시GUI receipt옵션만새경로를선택한다. 기본CLI가실패한뒤성공처리하는fallback은없다. nonce/source/project/version/script·Builder/scenario·보조PII/link파일·147package/manifest/정확cache·실제APK hash/size 또는exporttree/PBX·원본Builder로그를검사한다. 잘못된GUI APK입력은ADB/Backend전에거부한다. 원래auth/purchase/PII/Backend원장·marker/callback검사본문은유지했다.

실제Android/iOS는원래검사입력을사용했지만종료전검토에서renamed adb client dispatch가빠질수있는경로와보조PII파일대조누락을찾아guard/음성unit을보강했다. 제품코드나원래성공조건을약화하지않았고동일실제플랫폼실행은불필요하게반복하지않았다. 최종Python171 PASS,초기169 PASS도별도이력이다.

Core/managed418·Native전체·self9·batch Strict는이번SDK제품변경이없어관성재실행하지않았다. 이전출처는그대로유지한다. 현재API/source/wire baseline·metadata/manifest/actionlint/diff PASS,147현재staging은실제GUI두빌드에서검증했다. Native SDK/C#shipping source변경0,baseline덮어쓰기없음. iOS현재UnityFramework4개C ABI실제symbol검사PASS를모든binary ABI재검증으로확대하지않는다.

### 후보독립tests 및 신규/잔여 실패

Kotlin18/Swift20건은새test source hash로확인했다. 신규Kotlin3건은저장app/mode/backend/providerbinding·잘못된credentials의network전거부와profile후save실패순서,Swift2건은GRANTED/ALREADY_GRANTED/unknownfield유지·malformed grant/다른account·logout후지연HTTPgrant CANCELED를검증한다. 기존single-flight/tombstone/offline logout/idempotency retry/finalization규칙을수정하지않았다. 플랫폼Store finish 자체를새로실행했다고주장하지않는다.

최초GUI probe GetInstanceID CS0619(test-only)와Kotlin SDK경로미지정(테스트0)실패는원본보존후각근거있는수정/환경명시로검증했다. Android실제Playertimeout은미해결FAIL이다. P05-T03FAIL/ENV-STOREKIT-26OPEN,StoreKit18.6간헐원인미확정,Provider13WAITING_USER/self-hosted·실기기·Release미검증을유지한다.


## 작업중이력 (중단/재개 전후 상태 포함)

**사용자 요청으로 안전 중단. 배치 미완료.** [재개 체크포인트](p10-batch29-resume.md)를먼저읽는다. A GUI메서드·B APK빌드PASS,C Android실행timeoutFAIL,D 독립후보testsPASS. iOS export/Player·최종E CI/FFpush는아직미실행이다.

기준7fe7c4ad3aab56302ec6b988b9d1b747ebe9cf94,branch handoff/p09-resume-20261113. A~E 실제수행범위를source/nonce/기기·산출물/검사종류와함께기록한다. GUI와batch,빌드와실행,현재와과거증거를분리한다. 기존미추적Demo/cache·사용자project/기기/DB·라이선스보존. P05FAIL/StoreKit18.6위험/Provider13WAIT유지.

## A 시작

기존전용GUI project에test-onlyEditor menu를추가하고실제컴파일/UnityEngine메서드/nonce·소유project·버전검사를수행한다. 장시간batch재시도없음. 단순파일PASS는허용하지않는다. B~E아직NOT_RUN.


## 사용자 요청 안전 중단 시점

[정제GUI probe](p10-batch29-gui-probe.json)와[Android GUI APK](p10-batch29-android-build.json)는실제생성·메서드/파일검증PASS다. Android[실제E2E 결과](p10-batch29-android-e2e.json)는install/launch후marker timeoutFAIL을보존했다. 소유AVD/PID/양port 및5037동일SDK/server guard를사용했으며타기기/서버조작·실패빌드fallback은없었다. 원본AVD/DB/로그보존,자기emulator만종료했다.

[후보계약tests](p10-batch29-candidate-tests.json): Kotlin18/Swift20 PASS(신규3+2). codec/decoder제품변경0이며T01/T02 PARTIAL이다. GUI19개영향단위와cache2/binding5등을검증했으나기존전체149/fullNative/self9/Strict를현재실행으로표시하지않는다.

iOS GUI test-only helper/준비·receipt/exporttree·명시E2E입력·음성4건은코드로보존하되실제Unity컴파일/export/Xcode/Simulator실행NOT_RUN이다. 현재Android소비GUI는idle로열려있고진행중빌드/Player/Backend작업은없다. 네트워크중단예정사용자요청에따라새네트워크/Hosted/push를시작하지않았다(각0회). 재개지시후[정확한명령·남은순서](p10-batch29-resume.md)로계속한다.
