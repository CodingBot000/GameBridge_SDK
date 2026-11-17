# 배치31 GUI 검증 경로 확장과 P10 판정

작업 branch `handoff/p09-resume-20261113`, 시작 HEAD `089f1a8a7978dbdc5396f0c20f6ca864622d1cf0`. **GUI Push/JNI 입력 구현·fixture 검증 완료, 실제 GUI 빌드/Player 미실행. P10-T01/T02 PARTIAL, 전체 SDK BLOCKED_INTERNAL 유지.** 새 Hub 약관 동의가 필요한 단계만 보류하고 독립 검증·커밋·Git 인계를 진행했다. 사용자에게 개발 중단을 요청받은 상태나 배치 전체 완료가 아니다.

## A — 이전 결과와 승인 범위

[배치30](p10-batch30-integrated.md)의 Android 구매·PII E2E PASS는 새 AVD 정상 전체화면 교육 안내를 사용자의 명시 요청으로1회 닫은 실행이다. 이 허용을 다른 AVD로 확대하지 않았다. 과거 timeout FAIL들과 신규 PASS를 모두 보존한다. 이번 새 실제 ACK는0, 새 실제 기기 실행도0이다.

## B — Push GUI 입력 경로

`prepare-unity-gui-android.py --variant push`가 기존 Push scenario·LateCallbackProbe·link.xml을 복사하고 원본 BuildMockPlayer와 test-only GUI 메뉴를 재사용한다. 새 nonce/config를 생성하고 package/cache를 준비한다. 기존 standard/pii/utf8 경로도 유지한다.

`gui_verification.py`는 Push variant와 보조 소스를 기존 엄격 검증에 포함한다. runId/source ancestor·보호경로 diff0·소유 project·Unity6000.5.8f1·원본 Builder/adapter/scenario hash·147staging/checksum·exact package versions·receipt/APK freshness/hash/size·로그 nonce를 검사한다.

Push E2E에 명시 GUI project/receipt·ADB executable·emulator/server PID 입력을 추가했다. 검증 실패는 ADB·Backend·batch 전에 거부한다. 유효 GUI 입력은 기존 Backend/Proxy/Player/DB 본문으로 들어가며 batch build를 실행하지 않는다. CLI 실패를 GUI 성공으로 fallback하지 않는다. GUI ADB는 매 호출 전 동일 SDK server/AVD PID·양port 소유를 가드한다. 기존 등록/해제/logout·중복 제거·main thread·background/foreground·망 차단/복구·reconnect 거절·세션 전환·token0 검사 조건은 유지했다. 선택적 startup 진단은 입력 없이 UI/PID/focus/log을 수집한다.

`run-unity-push-current.py`도 명시 GUI 입력을 전달한다. 기본값은 여전히 양플랫폼 fresh 실행이며, 명시 `--platform android` 또는 `ios`는 해당 실행만 판정하고 상대 플랫폼을 실행했다고 출력하지 않는다.

## C — R09 독립 판정

R09 wrapper의 명시 GUI 경로는 기존 UTF8 consumer와 `--utf8-probe`를 사용하고 strict receipt·소유 binding을 전달한다. Android 결과는 현재 source/tracked-clean·실제 Player/원장 검사에 더해 utf8Probe=true와 전용 `GB_UTF8_JNI_ROUNDTRIP PASS` marker를 요구한다. 일반 구매 marker만으로 R09 PASS가 될 수 없다.

`--platform android|ios|both`를 지원하며 기본 both 성공은 두 실제 경로가 모두 PASS일 때뿐이다. Android 실패 뒤에도 명시된 iOS는 독립 판정한다. iOS는 새로 만든 자기 Simulator만 shutdown하고 삭제하지 않는다. 새 summary는 testcase 수와 오류를 검증해 저장한다. 이번 구현의 단위시험은 실제 JNI/C ABI 실행 증거가 아니다.

새 음성 fixture에서 xcresult가 배열일 때 AttributeError로 결과 저장이 중단되는 하네스 결함(error1/exit1)을 재현했다. object/integer count 검증을 추가해 FAIL/IOS_RESULT_UNAVAILABLE를 기록하고 cleanup을 유지하도록 수정했다. 원본 실패 로그를 보존했다.

## D — 실제 빌드·기기 검증 차단

새 Push project `artifacts/unity-android-mock.Vo5TLO/GameBridgeGuiAndroidB31Push`, UTF8 project `artifacts/unity-android-mock.lb7A7f/GameBridgeGuiAndroidB31Utf8`를 source8aadcf4에서 준비했다. [config·nonce·source hash](p10-batch31-prepared.json)를 검사했고 원본 Builder·147SDK·정확한 Notifications2.5.0/Newtonsoft3.2.2를 사용한다. **PREPARED_NOT_BUILT**이며 GUI 컴파일/APK/Player는 NOT_RUN이다.

Hub3.22.6 파일 선택창은 정확한 경로 입력/자동완성/AX 편집 메뉴를 사용해도 수락 대신 초기화했다. 선택창을 정상 Quit한 뒤 재시작에서 **Hub4.0.1과 새 Unity Hub Software License Terms**가 표시됐다. 에이전트가 update/install 명령을 요청하지 않았으며 재시작 후 버전 변경을 관측했다. 새 약관은 CUA 정책의 `Confirmation Required at Action time — Accepts a legally binding agreement`에 해당해 동의하지 않고 사용자 직접 확인·동의 또는 명시적 허용을 요청했다. 이후 읽기 전용 재확인에서도 약관 화면이 남았고 아직 허용 응답이 없다. CLI/설정/라이선스 파일 조작으로 이 단계를 우회하지 않았다.

공식 unity-cli의 `projects add`로 위 두 project를 각각 등록했다(exit0). Editor launch 옵션은 사용하지 않았고 GUI 실행 성공으로 해석하지 않는다. 동의 후에는 Hub 검색으로 선택할 수 있어 파일 선택창 재시도를 피할 수 있다.

5037 포트 read-only 조회의 현재 listener는0이다. 이는 이전 server PID98843을 다시 사용할 수 있다는 뜻이 아니다. 새 APK·새 AVD를 실행하기 전 실제 동일 SDK server·AVD명/serial/PID/양port 소유를 다시 입증해야 한다. 이번 ADB client/device 명령·server start/kill·새 AVD 생성/기동/설치·새 guide ACK는0이다. 기존 성공/실패 AVD와 설치 앱은 그대로 보존했다.

Strict는0회/DEFERRED_ENV다. 자동 batch Editor의 실제 정상 receipt 및 필수 환경이 확인되지 않았고 새 GUI 빌드도 차단됐다. GUI/fixture 성공을 Strict나 Release PASS로 바꾸지 않는다.

## E — P10 완료 조건

| 조건 | 이번 판정 |
| --- | --- |
| API/wire·선정 ABI·현재79 shipping source/147staging | PASS, 보존 artifact 현재 재대조; 새 Native build 아님 |
| Core 전후·duplicate 감지/정상 복원 | 독립 로컬 PASS |
| Android 구매·PII | 배치30 실제 PASS와 제품·scenario 동일 범위 유지; 이번 재실행0 |
| iOS 구매·PII | 배치29 실제 PASS d543556와 보호 source diff0; 이번 재실행0 |
| Android Push/Lifecycle·JNI | 새 GUI 입력 구현/fixture PASS, 실제 빌드·Player NOT_RUN/환경 대기 |
| iOS 독립 C ABI | 배치26 actual XCTest1 PASS d86ccc2와 보호 source diff0; 신규 실행0 |
| 현재 iOS Unity Push/Lifecycle | 미검증. 배치25 e46cb65 PASS 뒤 RequestRegistry.cs 변경1개가 남아 그대로 승계 불가 |
| 전체 Strict | 0회/DEFERRED_ENV; 자동 batch 정상 미확인 |

[iOS source 대조](p10-batch31-ios-compatibility.json). 과거 iOS Push PASS를 현재 refactor 이후의 성공으로 오기록하지 않는다. T01 전체 조건이 충족되지 않아 **IN_PROGRESS/PARTIAL**이며 E1 GoogleAuthProvider codec/binding 분리와 E2 AppleHttpProofSink decode/HTTP 분리는 **NOT_RUN_PREREQUISITE**다. 배치29 후보 Kotlin18/Swift20 정상·음성 tests와 session/grant/finalization 불변식은 보존했다. 새 제품 API·권한·기본 정책·지급/finish 순서 변경은 없다.

## F — 독립 통합 검증과 인계

[정제 검증](p10-batch31-verification.json): 최종 Python203건/51모듈, failure/error/skip0 PASS(17.370초). GUI38건은 여기에 포함된다. 잘못된 receipt/variant·누락/변조 보조 소스·APK bytes·package/cache·stale 결과/source·유효 GUI의 Backend 도달/batch0·invalid GUI의 ADB/Backend전 거부·각 플랫폼 독립 결과를 검증했다. 기존202PASS와 새 malformed-summary 재현error1/수정 후203PASS는 다른 실행이다. 코드 수정 없이 full Python을 반복하지 않았다.

[Core](p10-batch31-core.json): Kotlin10/helper50·Swift12/helper122, managed checker/helper418(정상198/예상오류220), lifecycle100samples/helper316, duplicate-only process134 예상실패1 감지·정상probe0·원본 SHA 복원·복원418/분기419 PASS. 실행 시 harness/test/doc 미커밋 변경이 있었고 SDK shipping79 SHA는 동일임을 별도로 확인했다. helper/test/check/sample/예상 음성 process를 합산하거나 실제 Player assertion 수로 쓰지 않는다.

[선정 artifact 재검사](p10-batch31-artifact-inspection.json): Java3 class public javap·양iOSslice Cexport4개·현재79 shipping SHA와 staging147 일치. 원장/API·wire/manifest/metadata/actionlint PASS. 전체 Native/self9는 관련 dispatcher/measurement gate가 변하지 않아 로컬에서 관성 반복하지 않았고 새 wrapper 입력·음성/독립 판정 fixture로 검증했다.

새 push 범위 gitleaks exit0/finding0. 이전 이력 포함 scan은 정확한 b1e3c73 source-SHA metadata 오탐2건/실제 exit1을 보존한다. ignore/amend/이력 삭제 없이 기존 검토 근거를 유지한다. 키·토큰·서명·license·원본 로그/DB·Unity/Xcode/Android 빌드 산출물은 올리지 않는다. 기존 Demo/cache3경로를 보존한다.

이 문단 작성시 새 handoff push/Hosted는 아직 NOT_RUN이다. 모든 code/test commit 후 FFpush하고 정상 API의 repo public/Unity vars0를 재확인해 false Hosted-only를1회 실행한다. 수락/최종 결과는 아래 후속 기록을 따른다. main/force/runner등록/Release/실Provider 호출은 하지 않는다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN·18.6간헐 위험·Provider13 WAITING_USER·self-hosted/실기기/Release 미검증을 유지한다.

## 재개할 정확한 지점

1. 현재 열린 Hub4.0.1의 새 약관을 사용자가 직접 처리하거나 행동 시점 명시 허용을 제공한다. 허용 전 동의·계정/라이선스 변경을 하지 않는다.
2. Hub에서 등록된 GameBridgeGuiAndroidB31Push를 검색해 Unity6000.5.8f1로 연다. 실제 컴파일 뒤 test-only Switch Android Target→Build Android Mock를 실행하고 nonce/receipt/147/APK/source를 검사한다. 그다음 UTF8 project도 같은 절차로 별도 생성한다. 준비 source8aadcf4는 후속 harness/doc commit의 ancestor이며 보호 SDK/빌더/scenario diff0 조건을 다시 확인한다.
3. Push/JNI 각각 새 AVD와 현재 server/실행파일·PID·serial·양port 소유를 입증한다. 기존 설치를 덮지 않는다. Push wrapper는 `--platform android --gui-project ... --gui-build-receipt ... --expected-adb-server-pid ... --adb ...`, R09도 `--platform android --gui-project ... --gui-build-receipt ... --expected-emulator-pid ... --expected-adb-server-pid ... --adb ... --startup-diagnostics`를 명시한다. 원래 opt-in/staging/serial/AVD 환경값도 필요하다.
4. 새 guide가 실제 나타나면 원본/정제 관측을 남기고 해당 AVD 정상 안내에 대한 새 허용만 요청한다. 배치30 ACK는 적용하지 않는다. 기존 성공/원본 실패·판정시간/성공조건을 유지한다.
5. 현재 iOS Push/Lifecycle 영향 검증도 남았다. 이를 완료하지 않고 T01/T02를 완료로 바꾸지 않는다. 자동 batch/Strict 조건을 별도로 확인하고 충족 시에만 Strict 최대1회→T01 재판정→충족시에만 E1/E2 제품 분리로 진행한다.

## 작업별 커밋

| SHA | 변경 |
| --- | --- |
| `8aadcf44bf6bd42dddb634ef8bedcba04ac87120` | test(unity): [P10-T01] add explicit GUI push and independent JNI evidence paths |
| `3a472661562dc39b426b48851e99f85578f7f090` | test(harness): [P10-T01] verify GUI dispatch and preserve scoped platform gaps |
| `4b64d3701b4099036334dfb12293c050cb18f6f4` | fix(harness): [P10-T01] retain independent failure evidence for malformed xcresult summaries |

최종 문서/CI 커밋 및 local/remote HEAD는 후속 기록과 최종 채팅에서 실제 조회한다.
