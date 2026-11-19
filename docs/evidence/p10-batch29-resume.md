# 배치29 사용자 요청 안전 중단 — 재개 체크포인트

> 이 문서는 중단 당시의 고정 이력이다. 사용자 재개 후 iOS GUI export/실제E2E 및 Hosted가 수행됐다. **현재 상태/다음 작업은 [배치29 최종결과](p10-batch29-integrated.md)와 PROGRESS를 따른다.** 아래 push0/CI0/NOT_RUN은 중단 당시 상태다.

2026-11-17 Asia/Seoul. **사용자 요청으로 중단했으며 배치 완료가 아니다.** 추가 실행·push·CI는 재개 지시 전 수행하지 않는다.

## 현재 보존 상태

- branch `handoff/p09-resume-20261113`, 시작 `7fe7c4ad3aab56302ec6b988b9d1b747ebe9cf94`.
- 이번 로컬 커밋은 아직 push하지 않았다. 원격 마지막 확인/로컬 tracking ref는 시작 HEAD다. 재개 후 네트워크가 복구되면 fetch해서 실제 이력을 다시 확인한다.
- 진행 중 GUI build·Player·Backend 시험·Gradle/Swift testcase는 없다. Android 전용 emulator PID80979 및 controller는 종료됐고 AVD/DB/원본 로그는 보존했다.
- 현재 새 소비 프로젝트 **GameBridgeGuiAndroidB29**의 GUI Editor PID79170은 열린 채 idle이다. 새 세션에서는 PID·소유 경로·실제 창을 재확인하며 숫자/AX index를 그대로 재사용하지 않는다.
- 기존 미추적 `harness/__pycache__/`, `scripts/__pycache__/`, `unity/Demo/` 보존. main/fix 브랜치·사용자 프로젝트·기존 기기/DB/라이선스 삭제 없음.

## 실제 완료된 검증

1. **A GUI 메서드 PASS**: `dcc0b4c`의 test-only 메뉴 `GameBridge Verification/Run GUI Probe`. nonce7bbe2cf1b06d4612be219d88ac488fb2,실제 C# assembly/버전/소유project/scriptSHA 및 Unity 객체 생성·Transform·정리7조건/receipt/marker1회 확인. batch PASS나 Player PASS가 아니다. 최초 `GetInstanceID` CS0619 실패와 수정1회 보존.
2. **B Android APK GUI build PASS**: source `7263444dbf2262e7eae1539616ae7b0946d8cec9`,기존 BuildMockPlayer 그대로 호출,147개패키지파일 검증,27072192 bytes,SHA256 `dd09b532c842ee60116e57785e5b7add25f40a7f7d0deab486872e16c4b628e4`.
3. **C Android 실제 E2E FAIL**: source `7520cbc27d9cfb9e04e98d5fd36ebb74328fba72`,GUI APK 명시입력검증·이름/serial/PID/5590·5591 양port·기존Unity ADBserver79436/동일실행파일 guard·installSuccess·ActivityStatus:ok. 이후180초내완료marker없음 `UNITY_PLAYER_RESULT_TIMEOUT`. 새DB users/sessions/purchases/ledger 각0. UI원인은미확정이며성공으로재작성하지않는다.
4. **D 독립후보 tests PASS**: Kotlin GoogleAuthProviderTest18건(신규3)/failure,error,skip0,Swift AppleAuthProviderTests20건(신규2)/failure,skip0. storedbinding·잘못된credentials·저장실패순서/grant 정상·malformed·다른account·logout후늦은grant거부. Kotlin첫SDK미지정실패(테스트0)는원본보존후해당subprocess ANDROID_HOME 지정으로만재검증했다. 제품codec/decoder 변경0,T01/T02 PARTIAL.
5. GUI 계약 단위19건(Probe5/Android7/ADB3/iOS4),기존cache2건·binding5건 등 영향단위 PASS. **Python전체/Native전체/self9/Strict 재실행은 아직 안 했다.** 과거149·42/38·self9를현재실행으로표시하지않는다.

## 고정 경로

- A private GUI project: `artifacts/unity-editor-smoke-w2bupii_/project` (이전probeEditor는 정상Quit).
- Android 소비GUI project: `artifacts/unity-android-mock.34sD3a/GameBridgeGuiAndroidB29`.
- APK: `artifacts/unity-android-mock.34sD3a/gamebridge-gui-mock.apk`.
- Android GUI receipt 경로: `artifacts/batch29/android-gui-receipt.txt`,project 경로: `artifacts/batch29/android-gui-project.txt`.
- C E2E raw: `artifacts/unity-android-e2e-eb3lua0b/`,controller/raw: `artifacts/batch29/android-*`,emulator log: `artifacts/batch29/emulator.log`.
- 새 전용AVD: `GameBridge_V2_B29_GUI_PII_20261117_85e0`,데이터 보존/정지. **기존controller를그대로재실행하지 않는다**(로그존재/설치된app보존guard). 재시도는실패원인의새근거·새전용AVD/새로그·최신소유증명이있을때만.
- staging: `artifacts/batch26/upm-current`(현재SDK/147checksum일치),cache: `artifacts/unity-ios-mock.8xjMY7/project/Library/PackageCache`(Notifications2.5.0/Newtonsoft3.2.2).
- 5037은실행당시UnitySDK adb 소유. 재개시lsof/read-only경로부터다시확인하고기존서버kill/start나타SDKadb접근을하지않는다.

## 다음 독립 작업 — iOS GUI export (아직 미실행)

`GuiIosExport.cs`,GUI iOS 준비도구·export tree/receipt 입력계약·iOSE2E 명시입력·음성4단위를중단커밋에보존한다. Python syntax/19개GUI단위는통과했으나 **이 iOS C# helper 실제GUI컴파일/export/Simulator build·실행은 NOT_RUN**이다. 실패가있으면계층/로그를구분하고근거없이반복하지않는다.

재개지시후현재Git/Editor/소유경로·staging/API를확인하고:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 harness/prepare-unity-gui-ios.py --prepare \
  --staging artifacts/batch26/upm-current \
  --package-cache artifacts/unity-ios-mock.8xjMY7/project/Library/PackageCache --variant pii
```

이명령은새project만준비하고Editor/batch를시작하지않는다. 출력된전용 `GameBridgeGuiIosB29` project만Hub에서열고기존Android전용GUI와동일경로동시Editor실행을피한다. `GameBridge Verification/Switch iOS Target` → 실제컴파일확인 → `Export iOS Mock`. 메뉴가안보이면실제project의 `Logs/Editor.log`에서CS오류를확인한다(default 전역Editor.log와구분). 새장시간batch는하지않는다.

실제export receipt가생성되면 `gui_verification.load_ios_export`로source/nonce/147package/builder/scenario/PBX·exporttreehash·원본로그를검증한다. 그뒤에만:

```sh
python3 harness/run-unity-ios-mock-e2e.py --run-local --adhoc \
  --staging artifacts/batch26/upm-current --pii-probe \
  --gui-project <실제새project절대경로> --gui-export-receipt <실제receipt절대경로>
```

이경로는원래Xcode/C ABI·새Simulator/Backend/DB·auth/purchase/wallet/PII 검사본문을유지한다. Apple계정/인증서/실Provider시험은아니다. 새실행결과·생성Simulator의정확한UUID/소유를확인하고기존기기를조작하지않는다.

## 나머지 배치29 종료 작업

- Android현재timeout의원인·UI제어표면한계를미확정으로보존,새근거없는반복없음.
- GUI Player 성공과batch Strict 미실행을분리,T01필수조건이남으면PARTIAL. T02제품은진입하지않고현재독립tests의검증범위를유지.
- 신규iOS계약단위를Hosted inventory에연결(중단커밋에포함). 영향하네스코드가변경돼E에서전체Python을최종1회검증하는것은타당하나149/fullNative/self9를관성적으로반복하지않는다.
- 현재모든코드/tests를commit후secret/생성물/PII·remote/upstream/FF 이력검사,repo Unity변수비활성정상응답확인후Hosted-only false 단1회. **현재 dispatch0/push0이며아직원격미검증**.
- P05-T03FAIL/ENV-STOREKIT-26OPEN/18.6간헐위험/Provider13WAIT/self-hosted미검증보존. main/force/Release/실Provider호출/runner등록금지.
- PROGRESS/WORK_LOG·USER_SETUP·batch28/29 evidence 갱신후작업별commit/handoff FF인계·최종보고. 이번중단은최종배치완료보고가아니다.


## 중단 시점 비밀정보 검사 상태

네트워크사용을막은 `go run module@version` 호출은Go의module deprecation lookup이차단돼실행불가였다. 이어캐시된gitleaks v8.24.2 source를GOPROXY=off/GOSUMDB=off/GOTOOLCHAIN=local로실행해이번6commit전체를검사했고exit1/finding2였다.

두finding은모두 `b1e3c738fa9a0c17ec2d7eed99da16672ef9faa0`의 `docs/evidence/p10-batch29-candidate-tests.json` 18/19행(generic-api-key)이다. 실제값을해당Kotlin/Swift test파일의SHA256과독립계산·대조해일치확인했다. 인증키/토큰이아닌**테스트source파일hash metadata**의오탐이다. SHA필드를path→hash map에서path/sha256객체배열로정리했으며기존commit을amend/rewrite/ignore하지않았다. rawscan exit1을0으로표시하지않는다.

재개 후push전전체범위검사에서이두개가다시나오면위commit/file/line과실제sourcehash일치근거로검토하고,새finding은별도로조사한다. 원본redacted report는 `artifacts/batch29/pause-secret-report.json`이다. 이번push0/CI0은유지한다.
