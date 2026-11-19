# P10-T01 제품 완료 조건 판정 — 배치32

**IMPLEMENTED / 로컬 PASS / N/A.** 전체 SDK 및 Release 완료 판정과 다르다. 기준은 DEVELOPMENT_PLAN P10-T01의 명시 완료 문구인 “baseline contract diff와 관련 회귀 tests가 통과해야 한다”, 취소/late event 의미 보존, 변경 전후 commit/결과 보존이다. 배치32 C는 이 제품 조건과 추가 전체 Strict/Release 조건을 구분하도록 명시했다. 기존 baseline/required suite/실패 행을 삭제하거나 optional로 바꾸지 않았다.

## 제품 변경과 동등성

배치26의 baseline6d200b0·동일418cohort에서 RequestRegistry private event header3곳을TryReadEventEnvelope로,원자적pending removal2곳을RemoveOwned로모았다. public/internal/protected 선언·wire·Native 인터페이스는 유지했다. 실제 post source dc45a2f와변경전후418=198normal+220expected-error·Kotlin10/Swift12/지정ABI·새package147/당시Editor2근거는 [전후기록](p10-core-bridge-batch26.md)에보존한다. Native coordinator의플랫폼별Mutex/actor는이유를기록하고변경하지않았다.

배치32 Native제품통합직전까지 해당Core source 및Native/wire가dc45후보와동일함을기존check-core-refactor-surface.py(79file scope)와P08API기준으로PASS했다. 원본contracts/baseline/p10-core-batch26.json은수정하지않는다. 현재 [Core실측](p10-batch32-core.json)은Kotlin10/helper50,Swift12/helper122,managed418·복원418/branch419,duplicate-only변이134감지/정상probe0·원본SHA불변,lifecycle100samples/helper316·잔존0을확인했다. helper/test/check/Player는분리한다.

## 남아 있던 실제 관련 경로

- Android 구매·PII: 배치30source6f813a7 실제PASS/원장1·100. 배치32시점제품source/consumer보호경로동일이며과거timeoutFAIL은보존한다.
- iOS 구매·PII: 배치29sourced543556 실제PASS/원장1·100. 같은보호source범위유효,새실행으로바꾸지않았다.
- [Android UTF8 JNI](p10-batch32-android-jni.json): 배치32새소유AVD·현재GUIAPK에서전용marker/Nativecallback·Backend/원장1·100 PASS.
- [Android Push/Lifecycle](p10-batch32-android-push-c.json): 같은SDK/기존 APK의새C기기에서6필수marker/소유session·중복/mainthread·BG/FG·망차단복구/reconnect거절·latecallback·token0 PASS. B의network90초FAIL와wrapper진입오류들은별도로보존했다.
- [현재 iOS Unity Push/Lifecycle](p10-batch32-ios-push.json): source01892c8 새GUIexport·Xcode/Simulator/DB의6marker와token0·자기기기종료PASS. 이전e46 source를새Registry성공으로재사용하지않았다.
- iOS C ABI: 배치31sourcea812cdd의실제UTF8/synthetic host XCTest1 PASS와제품/CABI source동일. UnityPlayer/실APNs와구분한다.
- [현재 self9](p10-batch32-self-nine.json): 새격리DB/role에서9필수negative/정상복구검사PASS/exit0. expected nonzero를실제감지하고원상복구했다. P09-T08의로컬기능의존을확인했다.

## 추가 전체 검증의 제한

전체Strict는자동batch Editor의정상실행·전용환경이확인되지않아0/DEFERRED_ENV를유지한다. 기존P05-T03 FAIL/ENV-STOREKIT-26 OPEN·18.6간헐위험·Provider13 WAITING_USER·self-hosted/실기기/Release미검증을유지한다. GUI/개별Player PASS를Strict PASS로변환하지않는다. 이추가Release제약으로완료된Core제품변경을무한대기시키지않되SDK전체완료로도확장하지않는다.

## 후속 Native phase 경계

이판정commit을T01 closing source로고정한다. P10-T02의승인된Google session codec/Apple grant decoder는별도local후보(e6e1de7/fc3da2f,현재후보21b5f71)에서18→20/20→23 및넓은47/43·freshpackage/소비자/지정ABI를검증했다. 이제명시조건충족에따라동일제품bytes를handoff에후보별별도commit으로통합할수있다.

기존Core검사기는닫힌T01 Git source에그대로적용한다. 후속현재source는Core·wire·나머지Native파일불변,허용된4개Native파일의정확한전후hash/파일집합을별도전이기준으로검사한다. 원본Core baseline을덮어쓰거나Native드리프트를포괄허용하지않는다. 원격CI는모든후속code/test/실측수정이끝난최종source에서1회만진행한다.
