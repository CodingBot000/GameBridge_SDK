# 배치30 Android 최초 실행 장애 분석과 P10 검증

기준2c8e7a79db631e9e679d5c8c9680c58e3f706903,branch handoff/p09-resume-20261113. 기존미추적Demo/cache3경로·기존AVD/Simulator/DB·라이선스/개인파일보존. A~E실제수행범위와실패/미측정/미실행을분리한다.

## A 시작

배치29 설치/Activity응답·emulator Vulkan관측·Backend0 및marker수집범위를실제source와대조한다. 첫성공marker는InitializeAsync완료뒤이므로marker부재를Start미도달로단정하지않는다. process생존/Unity runtime/Scene/Awake/Start/intent/SDK객체/Native초기화/첫HTTP를각판정한다. 배치25 PASS의APK/설정/Scene와비교하되과거PASS를현재로재사용하지않는다. 새실행전필요한진단만test-only로보강하고현재SDK제품은우선변경하지않는다.


## A 원본 대조

[정제비교](p10-batch30-prior-comparison.json): 설치Success/ActivityStatus:ok는확인했지만기존수집은Unity tag의성공/실패계약marker만필터해보존했다. 최초성공marker는InitializeAsync완료뒤라Awake/Start/intent/SDK객체/Native초기화중어디서멈췄는지확정할수없다. Backend health준비확인은있지만첫dev-auth성공/DB사용자·세션·원장없음은각0이며그전native initialize는HTTP를하지않는다.

B25와B29는같은serializedUnityversion6000.5.8f1/arm64IL2CPP/동일Pii scenario바이트·선택build/stripping/graphics/entrypoint설정이며Scene의scriptGUID참조도정상이다. 일부Native라이브러리는바이트가달라전체동일로단정하지않는다. Vulkaninstance create/destroy는부분Native그래픽관측이며완전한Unity초기화/프로세스생존/첫Scene을증명하지않는다. process/PID·ActivityManager/AndroidRuntime/ANR/UI를기존원본에서복원하지못한범위는UNMEASURED로남긴다. 이전성공APK는현재성공으로재사용하지않는다.


## B·C 첫 진단 결과

표준/PII/UTF8 Android test-only scenario의Awake/Start·sceneIndex/focus/pause/intentbool/SDK생성/init전후/예외/첫auth API전marker를추가했고원래성공/실패조건·await순서·제품소스를변경하지않았다. [새GUI APK](p10-batch30-android-build-a.json)는실제Builder/147입력·nonce/크기/hash검증PASS다.

[첫 진단 재현](p10-batch30-diagnostic-a.json)은이전marker timeout을재현(FAIL)했지만앱PID생존·Activityresumed·UnityNativeInitialize/GraphicsOK를확인했다. Awake/Start/SDK생성·HTTP는관측되지않았다. 전체all-buffer logcat/PID/Activity/window/exit-info/UIhierarchy를수집해ignored raw에보존했다. 기존180초판정은그대로이며사후실패관측시간은분리했다.

UI에는실제framework package android의Viewing full screen/To exit swipe/Got it이있었고Native APP_CMD_LOST_FOCUS도있었다. 초기SystemUI-only detector의False와focusfield없는window-query False를각framework-package허용/field부재UNMEASURED로정정하고unit10건PASS로검증했다. 원본관측을덮어쓰지않은별도재분석이다. 이안내가현재차단상태라는증거는있지만정상ack후실행회복을검증하기전에는완전한단일원인/SDKPASS로단정하지않는다.

Qt Emulator가CUA제어표면에노출되지않는한계로사용자에게다음허용재검증의직접ack가능여부또는전용AVD ADB UI입력명시요청을async문의했다. 응답전그조작을강행하지않고,원인별추가재검증은최대1회·새source/APK/AVD조건을유지한다. 이미설치된기존/첫재현AVD는보존하고프로세스만정상종료했다.
