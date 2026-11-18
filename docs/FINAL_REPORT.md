# GameBridge SDK 개발 보고서

배치34의 최신 검증·제약은 [통합 증거](evidence/p10-batch34-integrated.md)를 따른다. 실제24 HTTP operation의 성공 응답 구조, DTO23개, 새 양플랫폼 Unity LOCAL_MOCK 소비와 선정 JVM API를 확인했다. C ABI와 실제 Unity Scene/Frame·runtime 메모리를 측정했고 weak client1개 잔존을 관측했다. 원인·누수 여부는 미확정이다. Task/continuation·Android heap·CPU blocking 및 전체 Strict는 미완료이며 DEV_RC를 유지한다.


## 최신 인계 — 배치32 (2026-11-18)

**P10-T01·T02 구현/로컬 PASS, P10-T03·T04·P11 PARTIAL, 전체 SDK BLOCKED_INTERNAL 유지.** [배치32 A~J·source별 결과·커밋·남은 실제 작업](evidence/p10-batch32-integrated.md), [정제 검증](evidence/p10-batch32-verification.json)이 현재 기준이다.

새 Android GUI Push/UTF8 APK와 iOS GUI Push export를 생성한 뒤 새 기기의 실제 LOCAL_MOCK Push/Lifecycle·JNI·late callback·token0을 검증했다. 기존 Core 기준과 현재 회귀/변이복원·추가 Player gap을 대조해 계획의 T01 제품 조건을 종결했다. 전체 Strict/Release 상태를 바꾼 것은 아니다.

격리 로컬 후보에서 Google 저장 session codec과 Apple grant decode를 실제 구현·전후18→20/20→23 및 넓은47/43·fresh패키징으로 검증한 뒤 같은 bytes를 handoff의 정식5ef87e5/ff2d0d5로 각각 반영했다. 원본 Core baseline을 덮지 않고 닫힌 Core Git tree와 승인 Native4파일의 정확한 전후hash를 연결해 검사한다. 현재 source의 새 Maven/AAR/R8·무서명 양slice XCFramework·Swift source/binary·147checksum, 변경 후 새package Android/iOS 구매PII·Backend·원장1/100도 명시 CLI batch로 실제 PASS했다. Mac 잠금을 해제하거나 GUI 결과로 위장하지 않았다.

현재 Python237/57모듈, Native47/43, Core10/12·managed418·duplicate 감지/복원·lifecycle100/316, 필수self9·TC11/의도변이1을 검증했다. 최초 wrapper/fixture/문자열수량/서버수명·post Android 창환경 실패를 보존하고 실제 수정·대조와 연결했다. [사전계측](evidence/p10-batch32-performance.md)은 warmup20+100·실제monotonic p50/p95/max·잔존0 및 loopback멱등/409를 기록하며, Native memory/UI jank/Unity startup·실제Provider나 성능 향상을 주장하지 않는다.

자동 Editor의 direct/cli 정상은 회복했지만 원래 fullStrict의 전체기기/서버수명·필수OS/StoreKit컨텍스트 전이가 완비되지 않아 전체Strict0/NOT_RUN·DEFERRED_ENV/내부설정대기를 유지한다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN·18.6간헐위험·Provider13 WAITING_USER·self-hosted/실기기·Release미검증을 보존했다. P11 사전감사에서 64Task/증거와 문서의110→147·Unity미검증표기를 정정했고 기계OpenAPI파일부재는 BUG-017로 남겼다. [Hosted run44165459795](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44165459795), source2017771d355cb56865f44ef1ddf9e4faad78442d,false단1회SUCCESS: Hosted4+basic성공,Unity/ReleaseSKIPPED. 공식Python237/Swift40·신규KotlinCodec/TC11·변이복원확인. 코드변경은모두이source에포함됐고이후문서변경뿐이다. 동일handoffFFpush/최종localremote문서HEAD는마지막Git/채팅인계에서조회한다.


## 최신 인계 — 배치31 (2026-11-18)

**GUI Push/JNI 입력 구현·fixture 검증 완료, 실제 GUI 빌드/Player는 NOT_RUN/DEFERRED_ENV. P10-T01/T02 PARTIAL·전체 SDK BLOCKED_INTERNAL 유지.** [배치31 통합결과·정확한 재개 지점·커밋](evidence/p10-batch31-integrated.md),[정제 검증](evidence/p10-batch31-verification.json)이 최신 기준이다.

Push GUI preparer/strict receipt·기존 Backend/Proxy/DB 검사 연결과 R09 UTF8 GUI 전달·각 플랫폼 독립 결과/정확한 실패 저장을 구현했다. 최종 Python204/51모듈·GUI39 포함, CoreKotlin10/Swift12·managed418·duplicate 감지/복원·lifecycle100samples·API/wire/선정 ABI/staging147 PASS. malformed iOS summary의 새 음성 오류를 재현·수정한 뒤203건으로 복구했다. fixture 통과를 실제 JNI/Player 통과로 쓰지 않는다.

Hub3.22.6 파일선택 실패 뒤 정상 재시작에서4.0.1 새 Software License Terms가 나타나 약관 동의를 보류하고 사용자 직접 처리/명시 허용을 요청했다. 새동의·우회·license조작·실제APK/AVD/ACK/UnityPlayer 실행0. 후속 독립 iOS C ABI는 새18.6 Simulator에서1건 실제PASS(a812cdd)했고 최초destination70/시험0 실패를 보존했다. 공식 CLI로 두 소유 프로젝트 등록만 완료했고 source/nonce/hash를 보존했다. iOS구매PII/CABI 과거PASS와 source동일 범위는 유지하되, 과거iOSPush는Registry 변경이 있어 현재 검증으로 승계하지 않는다. Strict0, E1/E2 제품 refactor 진입0이다.

[Hosted run44126492891](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44126492891), source5af3aff,false 단1회SUCCESS: Hosted4/basic성공,Unity/ReleaseSKIPPED. 공식Python203/Swift37/TC11·의도변이1확인. 이후 UUID수정2commit은원격CI미검증이며최종로컬204·실제CABI1로검증했다. 최종HEAD전체 Hosted검증으로표시하지않는다. handoff FFpush/최종SHA는마지막 Git인계에서조회한다. P05FAIL/ENV26OPEN·18.6위험/Provider13WAIT·self-hosted/Release 미검증과 기존 Demo/cache/기기/DB/실패원본을 보존한다.


## 최신 인계 — 배치30 (2026-11-18)

**Android LOCAL_MOCK E2E PASS, P10-T01/T02 PARTIAL. 전체 SDK 판정 BLOCKED_INTERNAL 유지.** [통합 결과·재개 지점·커밋](evidence/p10-batch30-integrated.md)과[정제검증](evidence/p10-batch30-verification.json)이 최신 기준이다. 아래 배치29 Android FAIL과 UI 입력 대기는 당시 이력으로 보존한다.

새 AVD 첫 진단에서는 Native 초기화/Activity·PID까지만 확인됐고 정상 전체화면 안내가 managed 진입을 막았다. 사용자 명시 요청 후 새 APK·새 전용 AVD에서 정확한 안내를1회 닫자 같은 PID에서 Awake/Start·SDK 초기화와 Backend 구매/원장1·100코인·PII 검사가 PASS했다. 실Provider나 무인 Strict PASS는 아니다. 첫 실패 원본은 보존했고 배치29의 미수집 UI 원인까지 소급 확정하지 않는다.

Python187/49모듈, Core Kotlin10/Swift12·managed418·duplicate 변이 감지/원본 복원·lifecycle100samples, API/source/147staging/선정 ABI 확인 PASS. iOS는 배치29 PASS와 보호 source diff0 대조이며 신규 실행0이다. Push/Lifecycle·JNI R09와 자동 batch/Strict는 미완료이며 T02 제품 codec/decoder refactor는 진입하지 않았다. P05 FAIL/ENV26OPEN·18.6간헐 위험·실Provider13WAIT·self-hosted/Release 미검증 유지.

[Hosted run44115202057](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44115202057), source a1cc004139193d175f6964cf11be7051f6e5b5f7,false 단1회 SUCCESS: Hosted4+basic 성공,Unity/Release SKIPPED. 공식 Python187/Swift37/TC11·의도변이1·정상복원 확인. handoff FFpush 및 당시 local/remote SHA 일치 확인,이후 결과 문서만 변경했다. 최종 문서 HEAD와 작업트리는 마지막 Git/채팅 인계에서 조회한다. 기존 Demo/캐시·모든 AVD/DB/로그/라이선스 보존, main/force/Release/runner등록 없음.


## 최신 인계 — 배치29 (2026-11-17)

**P10-T01/T02 PARTIAL, 로컬 Android 실행 FAIL 잔여.** [GUI·플랫폼·작업별source/commit 통합결과](evidence/p10-batch29-integrated.md)와[정제검증](evidence/p10-batch29-verification.json)을현재기준으로본다. 이전중단문서와아래이전배치는시각별이력이다.

실제GUI메뉴의C#컴파일·nonce/소유project/version/Unity객체7조건을확인했고기존Builder그대로AndroidAPK(27,072,192bytes)와iOS Xcodeexport(3,076files)를생성했다. batch자동화PASS와구분한다. iOS는현재GUIexport를명시입력검증해Xcode ad-hoc Simulator build/C ABI4symbol·PII/인증·구매/Backendtrace·원장1/delta100 PASS,새소유Simulator만shutdown/데이터보존했다.

Android는GUIAPK/source/hash·현재ADBserver/동일SDK·새전용AVD/PID/양port를검사해설치/launch성공후180초Playermarker timeoutFAIL이었다. 새DB users/sessions/purchases/ledger 각0,원인미확정·Qt CUA표면한계도단정하지않는다. 원본보존·동일실행재시도없음. 전체Strict/남은Push·Lifecycle/R09조합미완료로T01PARTIAL,따라서T02제품codec/decoder는변경하지않았다. 독립후보test Kotlin18/Swift20(신규3+2)와GUI입력/ADB가드·음성계약을구현·검증했다.

영향최종Python47모듈/171건PASS,SDK shipping/API/wire변경0·기존baseline보존. 전체Native/self9/managed418를관성재실행하지않았고이전증거로만표시했다. [Hosted run44096116650](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44096116650),source3fd95f459355d5abdab98ff9c622a7bd5675d0d1,false1회SUCCESS:Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED,공식Python171/Swift37/TC11·의도변이1확인. 원격Unity/실기기/Provider13/Release미검증,P05FAIL/ENV26OPEN/StoreKit18.6간헐위험유지.

현재전용iOS GUI만idle,관련testSimulator/AVD는정지/원본데이터보존했다. handoff에만FFpush,main/force/Release/runner등록/실Provider호출없음. 다음작업은Android첫managed marker미도달의새진단근거·안전한UI/ADB/기기소유조건확인부터다. T01전체조건충족후에만T02제품변경으로진입한다. 최종local/remote문서HEAD는Git/채팅마지막인계에서조회한다.


## 최신 인계 — 배치28 (2026-11-17)

**P10-T01·T02 PARTIAL / 자동 검증 환경 대기.** 사용자가위임한정상실행확인에서새전용project를Hub로열어Unity6000.5.8f1 Scene/Hierarchy/Inspector정상GUI를확인했다. 별도direct자동smoke1회는210초outertimeout124/검증2·receipt없음이었고정상자동receipt는미확인이다. [Editor정제관측](evidence/p10-batch28-editor.json)과[통합결과·커밋](evidence/p10-batch28-integrated.md)에두scope를구분했다.

지시에따라B현재Player/R09플랫폼영향·전체Strict(0회)/C1Android세션codec·C2Swiftgrantdecoder제품변경은진행하지않았다. 독립D에서는Python149,CoreKotlin10/Swift12(helpers50/122)·managed418,Native42/38,self9(47test/의도negative3/check9),mutation복원·lifecycle100samples/live0·API/wire/선정ABI재대조PASS. 과거Player/Strict를현재로바꾸지않는다.

GUI상태바에는다른SDK의ADBserver종료경고가있었고후속read-only5037listener는Unity내장SDK adb였다. 에이전트ADB명령은없으나사전owner/종료대상/기기영향은미확정으로보존했다. 검증GUI Editor는artifact전용project로열어두었다. 기존사용자project/계정/라이선스설정·개인파일을삭제/변경하지않았다.

이번제품/harness/test/workflow/baseline코드변경0이므로추가Hosted dispatch0/NOT_RUN. 배치27Hosted SUCCESS는역사증거다. P05FAIL/ENV26OPEN/18.6간헐위험/실Provider13WAIT/self-hosted·실기기·Release미검증유지. 재개는GUI/자동차이확인·자동receipt→ADB/기기격리→currentPlayer/Strict→T01판정→C1/C2순서다. [PROGRESS](PROGRESS.md)와[USER_SETUP](USER_SETUP.md)에다음행동을남겼다.


## 최신 인계 — 배치27 (2026-11-17)

**IN_PROGRESS / P10-T01·T02 PARTIAL.** [통합 결과·작업별커밋](evidence/p10-batch27-integrated.md),[정제 IPC 관측](evidence/p10-batch27-ipc.json),[독립회귀](evidence/p10-batch27-regressions.json),[T02 감사·설계](evidence/p10-auth-purchase-push-batch27.md)가현재기준이다. 이하이전배치는각실행당시기록이다.

A 실제새Editor 비교는direct210초/124와CLI180초/6 모두메서드미도달로DEFERRED_ENV,추가수정0/복구없음. IPC protocol거부/mutex획득실패/channel부재를관측했으나정확한전체원인은미확정이다. 계정/라이선스/Hub·사용자프로세스는조작하지않았다. B현재Player NOT_RUN/CStrict호출0·DEFERRED_ENV로T01PARTIAL유지. D는선행차단에따라제품변경없이Native책임경계·후보2·기존회귀/추가설계까지REVIEW_ONLY로완료했다.

E Python149/진단6,KotlinCore10·SwiftCore12/managed418,NativeAndroid42·Swift38,self9(47test/의도negative3/check9),mutation감지/원본복원·lifecycle100samples/live0가독립PASS. test/helper/check/sample/실제Player는서로구분한다. public API/wire·79shipping source변경0,보존artifact/checksum147/선정javap·C ABI재대조PASS이며새Player/build보증은아니다.

[Hosted44057317769](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44057317769),source50cd34c2f3c97eca36708d4a2ed377da392247d7,false입력1회SUCCESS. Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED,공식Python43파일149건확인. P05FAIL/ENV26OPEN/18.6간헐위험/실Provider13WAIT/실기기·전용self-hosted/Release미검증유지. 전체64Task 집계는IMPLEMENTED22/IN_PROGRESS42,localPASS20/FAIL1/PARTIAL43다.

재개는USER_SETUP의IPC환경확인및실제Editor smokePASS→currentPlayer→별도Strict→T01판정→T02후보별제한변경순서다. 기존Demo/cache/기기·DB·라이선스/개인파일을보존했다. handoff에만FFpush,main/force/Release없음. 최종local/remote문서HEAD는Git/채팅마지막인계에서조회한다.


## 최신 인계 — 배치26 (2026-11-17)

**프로젝트 IN_PROGRESS / P10-T01 PARTIAL.** [배치26 통합 결과·R01~R12·작업별 커밋](evidence/p09-batch26-integrated.md), [리팩토링 전후](evidence/p10-core-bridge-batch26.md), [구조화 계측](evidence/p09-batch26-assertions.json)을 현재 기준으로 본다. 이하 기존 보고서는 각 실행 당시의 역사 기록이다.

A 실제 assertion helper 계측·duplicate-only 변이와 정상 복원 완료로 P09-T02 local PASS. Kotlin10tests/50helpers,Swift12/122,managed0tests/check1/418(전후동일),Editor2/32,stress100samples/316helpers를 구분했다. 래퍼 밖/전체 assertion outcome 및 JNI 계수는 UNMEASURED다. B controlled18.6 StoreKit 두 경로 각1회PASS에도 최초 간헐원인미확정이므로 T04 PARTIAL 유지.

C shipping 수정은 RequestRegistry.cs 한파일의 event header 중복3→private1·pending owner removal중복2→private1이다. public/internal API·wire/native source·선정 javap/Cexport 표면 변경없음. 현재source의 새Native/XCFramework/UPM147checksum·Python143·cohort418·Editor·self9 및 독립 iOS Simulator C ABI1PASS를 확인했다. 현재 Android Unity 빌드는 LicensingClient IPC 연결실패로 raw FAIL/exit1,APK/Player NOT_RUN. 이번 전체Strict 호출0/DEFERRED_ENV이며 T01 IN_PROGRESS/PARTIAL을 유지한다. 이전 Player/Strict를 현재실행으로 치환하지 않는다.

D [Hosted run43934095574](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43934095574),sourcec34b419e3a2c719e5d615362f179b38f59b1a241,release_validation=false 단1회 SUCCESS. Hosted4+basic SUCCESS,Unity/Release SKIPPED;unit42파일143건 확인. 전용 runner/실기기/실Provider13/Release는 미검증이며 P05-T03FAIL·ENV26OPEN·T07PARTIAL을 유지한다. 전체64Task는IMPLEMENTED22/IN_PROGRESS42,localPASS20/FAIL1/PARTIAL43이다.

재개는 [USER_SETUP](USER_SETUP.md)의 ENV-UNITY-LICENSE-IPC 실제 Editor 통신 복구→current staging/source와 소유 기기 확인→미실행 영향 Player 회귀 순서다. local/remote최종문서HEAD는Git이력과채팅마지막인계에서확인한다. handoff/p09-resume-20261113에만FFpush하며main/force/Release/runner등록/실자격증명호출은없다. 기존Demo·cache·사용자기기·DB와모든실패원본은보존한다.


## 판정

**BLOCKED_INTERNAL.** P00–P11의 모든 계획 Task를 원장에 등록했으며 개발과 로컬 검증을 진행했다. Unity Android 및 iOS Simulator LOCAL_MOCK 전체 흐름은 검증했으나 전체 제품, 실제 기기와 실제 스토어·푸시 서비스는 검증되지 않았고 내부 미완료도 남았다. 이 문서는 상용 배포 승인이나 sandbox 검증 완료를 뜻하지 않는다. 자세한 Task별 상태와 증거는 [PROGRESS](PROGRESS.md), 실행 이력은 [WORK_LOG](WORK_LOG.md)에 있다.

P11 감사 당시 64개 Task 중 IMPLEMENTED 2개, 나머지는 진행 또는 미착수였다. 실연동 대상 13개 중 PASS는 0개다. 회귀 manifest의 50개 시나리오는 R12·R50 및 인증·구매 synthetic 회귀를 포함해 50개 IMPLEMENTED, 0개 PARTIAL로 local/fake 시나리오 증거가 기록됐다. 이는 전체 strict나 실제 제공자 검증 통과가 아니다. 이후 원장 갱신에 따른 최신 집계는 PROGRESS가 기준이다.

## 확인한 범위

- Android Kotlin, iOS Swift 및 Unity C# 경계의 계약·fake 테스트와 일부 local-mock HTTP/PostgreSQL 시험을 실행했다. 인증, 구매 중복 지급 방지 및 응답 유실 복구, 푸시 토큰 등록·삭제의 제한된 경로를 확인했다. 실제 제공자 테스트와 구분한다.
- Android emulator Keystore와 iOS simulator Keychain의 인스턴스 재생성 복구를 확인했지만 Unity Android emulator와 iOS Simulator의 LOCAL_MOCK 프로세스 재시작 구매 복구도 확인했다. 실제 기기 복구는 미검증이다.
- Android Maven 산출물의 독립 R8 소비 빌드, iOS static XCFramework의 simulator Swift 소비 링크, UPM staging checksum을 확인했다. 이후 Unity 6000.5.8f1 신규 소비 프로젝트 import·Android IL2CPP APK 및 local-mock Player 전체 경로는 전용 에뮬레이터에서 PASS했다 ([증거](evidence/px-t04-unity-android-local-mock.md)). Unity iOS Simulator의 LOCAL_MOCK 전체 흐름도 확인했으며 실제 스토어는 미검증이다.
- 최신 로컬 Unity gate는 소스 `562c75f`에서 PII·Push 양 플랫폼 Player, Editor, 50개 시나리오 coverage 및 실행 suite가 PASS했으나 `artifacts/verify-all-n3u_5w60/summary.md`의 기존 P05-T03 FAIL 때문에 전체 FAIL이다 ([증거](evidence/p09-unity-ci-local.md)). 두 Android 최초 안내와 R40 iOS OS 거부는 수동 도구 조작이 포함됐다. GitHub Actions 및 실제 제공자는 실행하지 않았다.
- 리팩토링은 하네스 이후 진행했다. baseline API 소스 비교와 별도 C# consumer 컴파일을 확인했으나 바이너리 ABI 및 Unity 실행을 보장하지 않는다. 독립 .NET fake 수명주기 100회 측정 p50 0.1467ms, p95 0.2125ms는 Unity나 기기 성능 수치가 아니다.

Offline Demo는 별도 staged UPM의 Package Manager Sample API import 후 새 테스트 프로젝트의 Unity Editor Play에서 fake 로그인·상품·구매 callback을 확인했다 ([증거](evidence/p08-offline-sample-editor.md)). Native Demo는 양 플랫폼별 신규 프로젝트에서 Sample API import 후 Android/iOS LOCAL_MOCK Player의 설정·모의 구매 callback을 확인했다 ([Android](evidence/p08-native-demo-android.md), [iOS](evidence/p08-native-demo-ios.md)). iOS 첫 export는 sample asmdef 누락으로 실패했으며 수정 후 통과했다. Package Manager GUI 클릭, 실제 포인터·화면 렌더링은 별도다.

## 남은 내부 작업과 실패

| 항목 | 상태 및 영향 |
|---|---|
| BUG-013 | XCODE_STOREKIT 격리 fake 서버 지급 및 Native/Unity bridge를 구현했다. iOS 18.6 상품 조회와 일회성 synthetic 지급·finish를 확인했으나, 추가 시험에서 동일 미완료 거래의 JWS가 바뀌어 중복 지급 위험을 발견했다. 완료 후 연속 구매의 고정 필드는 한 시험에서 구분됐지만 재시작 복구의 유일성은 미확인이다. iOS 18 이상과 host 소모품 이력 설정, 거래 후보 단일성 및 durable attempt를 요구하도록 보강했다. local DB 응답 유실과 Keychain 인스턴스 재생성 복구는 통과했으며 전용 iOS 18.6 simulator 앱 재시작 시험에서 journal 재생성 실패를 재현한 뒤 중복 거래 방지 수정으로 재시험 PASS (`artifacts/xcode-process-recovery-f_w2fsya`). 실제 기기·Unity 실행은 미검증이다. iOS 26.5 StoreKit 시험은 Code 3으로 실패했다. |
| BUG-014 | LOCAL_MOCK Unity Android emulator·iOS Simulator 전달 및 lifecycle을 확인했다. 실제 기기·FCM/APNs와 iOS OS 전체 네트워크 차단은 미검증이다. |
| BUG-015 | Native 진단 ring의 Unity 비동기 조회는 Android 및 iOS Simulator LOCAL_MOCK Player에서 확인했다. 다른 모드와 실제 기기는 미검증이다. |
| BUG-009 | LOCAL_MOCK Unity Android emulator와 iOS Simulator에서 응답 유실 후 프로세스 재시작 복구를 확인했다. 실제 스토어 및 실기기 복구는 남았다. |
| P09 | local/fake 50개 시나리오 증거 기록, R12 독립 fake·R50 하네스 음성 및 인증·구매 synthetic 회귀 구현; Unity Editor scene/domain reload 시험과 양 플랫폼 LOCAL_MOCK Player를 별도로 실행했다. 이전 로컬 전체 gate의 Editor 및 Push 양 Player는 PASS했지만 전체 gate는 실패였다. R40 iOS 실제 OS 거부는 GUI 도구 보조가 필요했다. |

## 환경 및 사용자 설정

과거 Unity 라이선스 오류(ENV-002)는 활성화 후 해소됐고 Android local-mock Player는 통과했다. 계획된 6.3 LTS 확인(ENV-001), 실제 기기 및 나머지 Unity 시나리오는 별도다. iOS 26.5 simulator의 StoreKit local 시험은 실패(ENV-STOREKIT-26)했다. 이후 별도 앱 재시험도 SKTestSession 생성에서 timeout (`artifacts/xcode-process-recovery-p8qyld6o`)이었으며 동일 계측의 iOS 18.6 대조는 PASS였다. 이후 test-only URL initializer도 iOS 26.5에서 세션 생성 단계 timeout (`artifacts/xcode-process-recovery-97a0wg1_`), 같은 URL 경로의 iOS 18.6 대조는 PASS (`artifacts/xcode-process-recovery-xbadp2tm`)였다. 두 실패의 동일 원인은 미확정이다. 이후 test-only background URL 대조는 iOS 26.5에서 세션 생성 단계 timeout (`artifacts/xcode-process-recovery-na8yq85t`)이었고, 동일 경로 및 기본 named의 iOS 18.6 대조는 각각 PASS였다. Apple 내부 원인은 확인되지 않았다. 실제 Google/Apple 인증, 스토어, FCM/APNs의 계정·앱 등록·서명 및 기기 준비는 [USER_SETUP](USER_SETUP.md)에 정리했다. `bash scripts/verify-external.sh --check-config`는 설정 형태만 확인하며 실연동 테스트가 아니다.

## 로컬 산출물

[산출물 manifest](evidence/p11-artifact-manifest.json)는 실제 파일별 SHA-256과 크기를 기록한다. 산출물은 Git에 포함되지 않는 로컬 개발 결과이며 공개 release가 아니다. P10 빌드는 `d02b8ed`와 당시 미커밋 P10-T04 변경을 사용했고 해당 변경은 `3bf8d0a`에 커밋됐다. 깨끗한 checkout에서 재현한 빌드라고 주장하지 않는다.

| 산출물 | 경로 | 확인 범위 |
|---|---|---|
| Android Maven | `artifacts/maven-p10-20261111-b` | 별도 소비자 R8 build |
| iOS XCFramework | `artifacts/ios-package-p10-20261111-a/GameBridgeNative.xcframework` | simulator Swift link, device C ABI symbol |
| Unity UPM staging | `artifacts/upm-staging-p10-20261111-a` | checksum 및 build hook 시험; Unity import 미실행 |

진단 연결 이후 `52f60f7` 소스 기준 새 산출물은 `artifacts/maven-diag-20261111`, `artifacts/ios-diag-20261111/GameBridgeNative.xcframework`, `artifacts/upm-diag-20261111`에 생성했다. Android R8 consumer 빌드와 UPM checksum은 통과했고 Unity import는 실행하지 않았다. 파일별 해시는 [새 manifest](evidence/diagnostics-artifact-manifest.json)에 있다.

현재 소스 `10e2a3c` 기준 재생성 산출물은 `artifacts/maven-current-20261111`, `artifacts/ios-current-20261111/GameBridgeNative.xcframework`, `artifacts/upm-current-20261111`이다. Android R8 consumer 빌드, iOS simulator Swift link·device symbol, UPM checksum을 확인했다. Unity import 및 실제 기기 실행은 미검증이다. [현재 산출물 해시](evidence/current-artifact-manifest.json)를 참조한다.

최신 재생성 산출물은 `artifacts/maven-final-20261111`, `artifacts/ios-final-20261111/GameBridgeNative.xcframework`, `artifacts/upm-final-20261111`이며 source `6a3fea5`에서 빌드했다. Android R8 consumer, iOS simulator Swift link와 device symbol, UPM 체크섬을 확인했다. [최신 해시 목록](evidence/final-artifact-manifest.json)을 참조한다. Unity import·실기기 검증은 미실행이다.

XCFramework arch·C ABI 선검사를 적용해 다시 staging한 최신 UPM은 `artifacts/upm-validated-20261111`이며 [파일별 해시](evidence/validated-upm-manifest.json)가 있다. Unity import는 미실행이다.

최신 제품 소스 `2bc9d77`에서 Android Maven `artifacts/maven-2bc9d77`, iOS XCFramework `artifacts/ios-2bc9d77/GameBridgeNative.xcframework`, UPM staging `artifacts/upm-2bc9d77`을 재생성했다. Android R8 consumer, iOS arch별 C ABI 및 UPM checksum은 통과했다. [산출물 해시](evidence/artifacts-2bc9d77.json); Unity import 및 실기기는 미실행이다.

최신 iOS 수정 반영본은 source `e9b64fb`의 `artifacts/ios-e9b64fb/GameBridgeNative.xcframework`, `artifacts/upm-e9b64fb`이며 [파일별 SHA-256](evidence/artifacts-e9b64fb.json)을 기록했다. Android 트리는 `2bc9d77` 이후 변경이 없어 해당 Maven R8 consumer 산출물을 재사용했다. iOS arch별 C ABI, arm64 simulator 독립 Swift consumer link 및 UPM checksum은 통과했고 Unity import·실기기는 미실행이다.

## 주요 이력과 재개

P09 하네스는 `e0afb97`, `196ae97`, `7770943`, `02005a4`, `864d2b6`, `35f1912`, `a93cf52` 등에 기록됐다. P10 리팩토링·호환성은 `36db140`, `e689dd7`, `d02b8ed`, `3bf8d0a`, P11 감사·설정 점검은 `31b683c`, `35bf2bd`에 기록됐다. 이후 문서 커밋은 `git log`에서 확인한다.

다음 개발은 BUG-013과 P09 미완성 시나리오를 해결하고 BUG-014·015 실제 Unity 검증을 진행하며 각 범위의 검증을 추가하는 것이다. 사용자 설정이 준비되면 USER_SETUP의 해당 항목에서 실제 플랫폼 검증을 별도로 실행한다. 자동 push, 공개 배포와 스토어 업로드는 수행하지 않았다.


## 후속 변경 — Unity Android LOCAL_MOCK E2E 재검증 준비

후속 브랜치에서 PX-T04 Unity Android Player 검증 Runner, PX-T05 Native-only 실행 환경 가변화, PX-T06 공개용 증거 Exporter 및 오프라인 검사 코드를 추가했다. 이 변경은 기존 P00~P11 전체 완료 또는 실연동 완료를 의미하지 않는다. 그 후속 브랜치 작업 당시 변경된 Runner의 Unity 실행·Android 기기 시험 및 GitHub Actions는 **NOT_RUN**이었다. 이후 로컬 Unity Player 검증은 위에 별도 기록했으며 GitHub Actions는 여전히 NOT_RUN이다.

기존 PX-T03 Kotlin Bridge → 로컬 Backend 1건/100코인 시험은 별도의 이전 실행 결과다. 변경된 코드를 clean checkout에서 재실행한 성공 근거 없이 그 결과를 새로운 코드의 PASS로 이전하지 않는다. 실제 실연동 대상 13건의 WAITING_USER 및 프로젝트 BLOCKED_INTERNAL 판정은 유지한다.

당시 2026-11-12 Android Maven·iOS XCFramework·UPM staging은 `f1e12b6` 제품 소스로 새로 생성했다. UPM 110개 파일 checksum, Android 독립 R8 consumer, iOS arch/C ABI 및 0.1.0-dev 버전을 확인했다. Unity Android Player E2E는 source `c58b4a6`의 clean tracked tree와 동일한 staged Unity SDK 소스로 실행해 PASS했으며 첫 전체화면 안내는 수동으로 닫았다. 해당 Android 실행 당시 실제 Google 로그인·스토어 및 Unity iOS는 NOT_RUN이었다. 이후 iOS LOCAL_MOCK 결과는 다음 항목에 기록한다.

2026-11-12 Unity iOS 18.6 Simulator ARM64에서 Unity C# → Swift C ABI → LOCAL_MOCK Backend/PostgreSQL 전체 흐름이 PASS했다 ([증거](evidence/px-t07-unity-ios-local-mock.md)). 무서명 실행은 로그인에서 실패했고 성공 실행은 로컬 ad-hoc Simulator 서명을 사용했다. 실제 Apple 로그인·스토어 결제·APNs 및 실기기는 미검증이다.

2026-11-12 Unity Android emulator 및 iOS Simulator에서 LOCAL_MOCK Push 등록·수신·중복 억제·main-thread·background/foreground·연결 복구·A→B 세션 전환 및 별도 process 종료/pending 복구를 검증했다 ([Android](evidence/px-t08-unity-android-mock-push.md), [iOS](evidence/px-t12-unity-ios-mock-push.md)). 늦은 이전-session callback은 test-only 합성 주입이며 iOS 연결 단절은 test-only TCP proxy로 재현했다. 실제 FCM/APNs, 실제 기기 및 실제 원격 지연 callback은 NOT_RUN이다. Android/iOS 인증·구매 LOCAL_MOCK Player 회귀도 별도 source에서 각각 PASS했다.


배치33 연속 작업 결과는 [통합 증거](evidence/p10-batch33-integrated.md)를 따른다. 새 Native 패키지·독립 소비와 Swift Simulator Core 계측은 확인했으나 전체 Strict, OpenAPI의 HTTP 전수 대응, Native/Unity 성능 전체 및 P11 완료는 아직 PARTIAL이다. 기존 P05 실패·StoreKit 환경 위험·실 Provider 13건 대기는 유지한다.

배치33 최종 원격: [44269328731](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44269328731), source deb907414706b132f4e1976e77bcc72524bb2587, FAILURE. Backend·Android·Swift/iOS Simulator 성공, inventory의 OpenAPI 파일열거순서 차이로 basic도 실패. 후속84e1026에서 수정했고 로컬Python248/자체시험9/TC11 통과, 수정코드는 원격 미검증이다. 추가CI0회. 배치33 A~H는 부분 완료이며 남은 실제 구현·검증은 통합 증거의 다음 순서를 따른다.
