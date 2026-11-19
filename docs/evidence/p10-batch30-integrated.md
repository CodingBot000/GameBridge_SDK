# 배치30 Android 최초 실행 진단과 P10 검증

작업 branch `handoff/p09-resume-20261113`, 시작 HEAD `2c8e7a79db631e9e679d5c8c9680c58e3f706903`. 현재 기준은 이 문서이며 이전 UI 입력 대기 문서는 해소된 체크포인트 이력이다. **프로젝트 IN_PROGRESS, P10-T01/T02 PARTIAL**이며 전체 SDK 완료 판정은 기존 **BLOCKED_INTERNAL**을 유지한다.

## A — 마지막 정상 단계와 최초 미확인 단계

[이전 APK·설정 대조](p10-batch30-prior-comparison.json). 배치29는 설치와 Activity `Status: ok`만 확인됐고 PID/Unity 초기화/Scene/Awake/Start는 UNMEASURED였다. 첫 성공 marker가 `InitializeAsync` 뒤에 있어 marker 부재로 Start 미진입을 단정할 수 없었다. Native initialize는 HTTP를 보내지 않으므로 DB0도 진입 위치의 증명이 아니다.

배치25 PASS와 배치29는 Unity6000.5.8f1/arm64 IL2CPP·선택 PlayerSettings·동일 PII scenario/정상 Scene GUID였다. 일부 Native 라이브러리 바이트는 달랐으므로 APK 전체가 같다고 주장하지 않는다. 최초 실패 원본을 보존했다.

## B — 실제 변경 소스와 진단

SDK 제품 변경은 없다. 표준·PII·UTF8 Android 테스트 scenario에 Awake/Start·focus/pause·intent 존재/유효성 bool·SDK 생성·init 호출/반환·auth 직전 marker를 추가했다. await 순서·callback·성공 marker·180초 timeout과 구매/PII/원장 판정은 유지했다.

`android_startup_diagnostics.py`는 동일 소유 guard로 PID, Activity/window, 모든 logcat buffer, exit-info, UI hierarchy와 Backend trace 관측을 기록한다. UI 미수집·focus field 부재는 UNMEASURED, mandatory log/PID 조회 오류는 실패다. package별 crash/ANR와 system native-load 범주를 분리한다. 원본은 ignored artifacts에만 보존한다.

`android_fullscreen_notice.py`는 framework android/SystemUI의 정확한 `Viewing full screen`·단일 enabled `Got it`·유효 bounds만 식별한다. 사용자의 “이 전용 AVD에 한해 ADB UI 입력으로 안내를 닫아줘” 요청 뒤에만 명시 GUI receipt/진단/소유 바인딩 옵션을 추가했다. default 입력0, 다른 앱·권한·설정 변경0이며 실제 ACK는 한 번이었다.

## C — 최초 FAIL과 제한된 추가 검증 PASS

[첫 진단](p10-batch30-diagnostic-a.json): source c3e23d1, 새 GUI APK c0946242, 새 AVD A. 앱 PID4639 생존·Activity resumed·Unity Native engine/graphics 초기화는 확인됐으나 managed entry와 HTTP는 없었다. 실제 전체화면 교육 안내와 Native focus lost를 관측했다. detector의 초기 SystemUI-only 오분류는 framework android도 인식하도록 수정했고 원본/별도 재분석을 보존했다. 180초 timeout FAIL/exit1, 사후 수집까지194.418초다.

[새 APK B](p10-batch30-android-build-b.json)는 build source `c07a264d923ecd05a994563c14a6c1636c10c2fe`, PII scenario SHA `afaf42d3cd055d2c206ae8cfc3b972045c87fc537a85fe74eb02367d51348130`, APK27,076,328bytes/SHA `f8f402fdb8d9a9b5ffc4038c4051d643eeb98e00220424605dec207ebd322b7e`다. 원본 Builder return·147package·nonce/receipt/log·builder/주·보조 source·현재 ancestor 보호경로 diff0를 검사했다.

[추가 E2E](p10-batch30-android-e2e-b.json): source `6f813a79ffe2b8b932a7b562f326613950c7d7fc`, tracked-clean. 새 전용 AVD `GameBridge_V2_B30_START_B_20261118_ACK`, emulator PID99860/serial5594/양port5594·5595, 현재 동일 Unity SDK ADB server98843을 매 호출 전 가드했다. 안내 전 PID4479/Native init/resumed·focus lost·managed marker0이었다. 14.528초에 허용된 안내를1회 닫았고 exit0이었다. 22.937초 snapshot에는 **같은 PID4479**, 안내 소멸·window focus 회복·Awake/Start/intent/SDK init 호출·반환/auth 진입과 첫 HTTP trace가 관측됐다. 이 값은 첫 HTTP의 실제 발생시각이 아닌 최초 snapshot 관측시각이다.

완료 snapshot27.976초, marker34·Backend auth1/catalog1/entitlements2/verify1/logout1·DB 원장1/delta100·PII 검사 PASS/exit0. 이 재현에서는 정상 OS 교육 안내가 managed 진입을 막았고 ACK 뒤 회복했음을 확인했다. UI 원본이 없는 배치29 원인까지 소급 확정하지 않는다. 사용자 ACK가 포함된 LOCAL_MOCK 실행이며 무인 CI·실Google 로그인/스토어 결제 통과가 아니다. controller는 자기 emulator만 종료하고 A/B AVD·설치 앱·DB·원본 로그를 보존했다. 최초 FAIL2개와 신규 PASS는 별개다. 추가 main E2E 횟수 한도를 사용했으므로 세 번째 재실행은 하지 않았다.

## D — 영향 회귀와 미충족 조건

[Core 계측](p10-batch30-core.json), source6f813a7: Kotlin10/helper50, Swift12/helper122, managed checker1/helper418(정상198/예상 오류220), lifecycle100samples/helper316 PASS. duplicate-only 변이의 예상 실패 process134를1회 감지하고 정상probe0·원본 hash 복원·복원418/조건분기419를 확인했다. helper 호출 수는 test 수나 전체 boolean/assertion outcome 수와 다르며, 변이 실패는 예상 음성 process 결과다.

[현재 artifact 검사](p10-batch30-artifact-inspection.json): 79 shipping source SHA·147 staging·선정 Java3 class javap·양iOS slice Cexport4개가 보존 Native artifact와 일치한다. GUI APK source/receipt/hash도 현재 checkout에서 재검사했다. 새로운 Native build나 모든 ABI 검증은 아니다. [iOS 대조](p10-batch30-ios-compatibility.json)는 배치29 actual PASS d543556와 iOS/공통 제품·소비 source diff0이며 신규 iOS Player를 실행한 것으로 쓰지 않는다.

Android Push/Lifecycle **NOT_RUN/DEFERRED_ENV**: 기존 runner는 자동 batch builder 전용이다. 엄격한 GUI receipt 입력 확장은 내부 미구현 작업이며 사용자 인증 대기로 넘기지 않는다. 현재 자동 batch Editor 정상은 확인되지 않았다. main PII scenario의 focus callbacks를 전체 Push/Lifecycle 검증으로 대체하지 않는다.

Android JNI R09 **NOT_RUN/DEFERRED_ENV**: 새 UTF8 전용 GUI APK와 설치 없는 전용 실행 환경이 없다. 이번 PII APK는 UTF8 scenario가 아니고 기존 설치 보존 gate를 우회하거나 전용 AVD ACK 허가를 다른 기기로 확장하지 않았다. 실제 UTF8 roundtrip을 Core/managed helper로 대신하지 않는다.

전체 Strict **0회/DEFERRED_ENV**: 자동 batch Editor 및 전용 무인 실행 선행조건이 확인되지 않아 조건부 실행을 시작하지 않았다. 기존 IPC 실패를 근거 없이 반복하지 않는다. T01 전체 조건이 충족되지 않아 **IN_PROGRESS/PARTIAL**, 따라서 T02 Android session codec/Swift grant decoder 제품 refactor는 보류하고 배치29 후보 정상·음성 tests를 보존한다.

## E — 검사·보존·GitHub 인계

[정제 검증](p10-batch30-verification.json): 전체 Python49모듈/187건, failure/error/skip0 PASS(16.309초), startup12·안내 selector4 포함. 최초 기본 Python의 jsonschema import error1/exit1을 보존했고 기존 schema venv로 성공했다. 표준 scenario compile-only warning0/error0도 확인했다. 원장/API/source/wire/manifest/meta/staging147 PASS. actionlint는 PATH 부재127 및 기존 custom label config 누락1을 보존하고 실제 캐시 binary+명시 동일 runner label config로 exit0을 확인했다. 전체 Native/self9를 관성 반복하지 않았다.

새 push 범위 secret scan exit0/finding0. 이전 이력 포함 scan은 exit1/finding2이며 정확히 b1e3c73 candidate-tests.json18/19의 test-source SHA metadata다. 현재 실제 test SHA와 독립 재계산 일치로 검토했다. raw exit1·원본 이력 보존, ignore/amend/force 없음. 모든 push commit 경로와 blob은 text이며 키/서명/license/원본로그/Library/Temp/APK/Xcode 산출물은 제외했다.

Repository `CodingBot000/GameBridge_SDK` public, 정상 API vars0/runners0·origin handoff ancestor를 확인했다. 모든 code/test commit 후 handoff 동일 branch만 FFpush하고 `release_validation=false` Hosted-only를1회 실행한다. 이 문단의 최초 작성시 배치30 push/dispatch는 NOT_RUN이었다. **실제 FFpush/단일 Hosted SUCCESS는 아래 최종 원격 결과가 최신이다.** main 병합·force·runner 등록·Release·실Provider 호출 없음.

P05-T03 FAIL/ENV-STOREKIT-26 OPEN·18.6간헐 위험·Provider13 WAITING_USER·self-hosted/실기기/Release 미검증을 유지한다. 64Task 집계는 IMPLEMENTED22/IN_PROGRESS42,local PASS20/FAIL1/PARTIAL43 그대로다. 초기 미추적 Demo/캐시3경로와 기존 기기를 보존한다. 현재 B30B GUI Editor만 idle로 남기고 시험 Backend/Player/controller는 종료됐다.

## 다음 재개 지점

1. 자동 batch Editor 정상 경로를 실제 receipt로 확인한다. GUI 정상과 별개다. 같은 IPC 실패를 반복하거나 license/계정/서버를 임의 변경하지 않는다.
2. Push GUI 명시 입력을 추가할 경우 원본 builder/현재 staging147·주/보조 scenario/receipt/source/hash 및 매 ADB 호출의 server/AVD PID·양port 경계를 그대로 유지한다. 기존 CLI 실패 fallback을 만들지 않는다.
3. 새 UTF8 GUI APK·설치 없는 소유 AVD에서 R09, 별도 Push/Lifecycle을 실제 실행한다. 이번 허용한 단일 안내 ACK를 무인 CI 일반 허가로 취급하지 않는다. 기존 실패/성공 AVD 설치를 덮어쓰지 않는다.
4. 자동 실행과 전용 환경이 검증됐을 때만 전체 Strict1회→T01 전체 판정→충족시에만 T02 후보 제품 책임 분리로 진행한다.

## 작업별 로컬 커밋

| SHA | 내용 |
| --- | --- |
| `5ce6a7a628275fbddd56f2a31661f7f2e6f97315` | test(android): [P10-T01] observe startup stages and scoped runtime diagnostics |
| `c3e23d1cc47abf618ca8677cfab8359bb89eaaf4` | test(android): [P10-T01] bind fresh startup APK and precise diagnostic categories |
| `b00ce0d7a326ae4c8630516ecde29adb0d7f3d59` | fix(diagnostics): [P10-T01] recognize framework-owned fullscreen guide evidence |
| `aa0a982bae086b6c8f8b1b288a25295212311ba7` | test(android): [P10-T01] constrain known fullscreen notice selection and preserve observations |
| `87c808c180593e492cf7704599905075d2edd96c` | docs(handoff): [P10-T01] preserve startup evidence and required UI acknowledgement input |
| `c07a264d923ecd05a994563c14a6c1636c10c2fe` | test(android): [P10-T01] acknowledge only explicitly requested owned-device education notice |
| `6f813a79ffe2b8b932a7b562f326613950c7d7fc` | test(android): [P10-T01] bind new APK and explicitly authorized single revalidation |
| `1a311f32559a49a389ec907e2caeca8e06e117c8` | test(android): [P10-T01] record authorized fullscreen recovery E2E |
| `98fca65fd96d2a3b57630d7df8fb985959312af2` | test(core): [P10-T01] record measured regressions and remaining platform gates |

이후 정제문서/CI 결과 커밋과 최종 local/remote HEAD는 아래 인계 기록과 최종 채팅에서 실제 조회한다. 현재 커밋 자체 SHA를 파일 내부에 억지로 기록하지 않는다.

| `a1cc004139193d175f6964cf11be7051f6e5b5f7` | docs(handoff): [P10-T01] reconcile batch30 recovery and verification limits; Hosted 검증 source |


## E 최종 원격 결과와 재개 상태 (2026-11-18)

[Hosted run44115202057](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44115202057), source `a1cc004139193d175f6964cf11be7051f6e5b5f7`, `release_validation=false` 단1회 **SUCCESS**. [정제 원격 증거](p10-batch30-hosted.json): Hosted4개와 basic-ci SUCCESS, Unity/Release SKIPPED. 공식 로그 Python49모듈187건·Swift package37건(후보 auth20 포함)/실패0·synthetic iOS host step/xcresult gate·TC11건/의도변이1·정상복원 확인. quiet host 로그의 정확 testcase 수는 UNMEASURED로 유지하며 Unity iOS 실행으로 바꾸지 않는다. 초기 진행중 `gh run view --job --log` 조회 exit1은 보존했고 완료job의 공식 jobs/logs API 조회 exit0으로 실제 수를 확인했다.

코드/test가 모두 포함된 `a1cc004139193d175f6964cf11be7051f6e5b5f7`을 `2c8e7a7`에서 동일 handoff로 FFpush했고 local/remote 일치를 확인했다. 이후 변경은 결과 문서뿐이며 추가 CI/Unity/self-hosted/Release 실행0이다. 마지막 문서 커밋 후 동일 handoff FFpush와 HEAD/작업트리를 다시 조회한다. 최종 문서 커밋 SHA는 Git 이력과 최종 채팅에서 확인한다.

현재 Android 회복/PII·Core·현재 source/선정 ABI·Python/Hosted는 PASS지만 Push/Lifecycle·R09·자동 batch/Strict는 미완료다. T01/T02 PARTIAL·전체 SDK BLOCKED_INTERNAL은 유지한다. 새 반복 E2E/SDK refactor를 시작하지 않은 채 위 재개 순서와 내부 미구현 작업을 다음 작업 기준으로 남긴다. 기존 실패 원본과 Demo/cache/AVD/DB/라이선스는 그대로 보존했다.


## 배치31 후속

[GUI Push/JNI 확장·현재 증거와 재개](p10-batch31-integrated.md). 새 명시 입력과 independent R09 결과 계약/음성 fixture를 구현했지만 Hub재시작 후4.0.1 새 법적 약관 동의 화면으로 실제 새GUI/APK/Player는미실행이다. 이 배치30의 단일AVD ACK 허용을 확대하지 않았다. iOS구매PII·CABI source동일 범위와 과거iOSPush의Registry변경 gap을 분리했다. T01/T02PARTIAL 및 과거실패/실Provider대기를 유지한다.
