# 배치30 정상 OS 안내 ACK 입력 대기

배치30 전체 완료가 아니다. 현재필수입력은새전용AndroidAVD의정상Viewing full screen/Got it안내를어떻게ACK할지다. 실제안내를수집했지만Qt emulator는CUA앱표면에없다. CUA지침상다른기술의UI입력은사용자의명시요청없이어시스턴트가대체하지않는다. async질문에대한사용자직접ACK가능여부또는전용AVD한정ADB UI입력명시요청을기다린다. 침묵/시간경과를허가로취급하지않는다.

## 이미 수행한 사실

- 첫진단source c3e23d1,GUI APKsource5ce6a7a/size27076304/SHA c09462427fd8c7c0de2b38dc8185cfa92e862d7261aabb5906fbd5112042b3a8.
- 새AVD GameBridge_V2_B30_START_A_20261117_c094,PID94221/serial5592/ports5592·5593와기존UnitySDK ADBserver93103소유가드통과.
- 설치/Activity시작·실제앱PID4639생존·Activityresumed·UnityNativeengine/graphics확인. Scene/Awake/Start/intent/SDK/API/init/callback/HTTP는아직확인되지않았다.
- 실제UI XML에framework android의Viewing full screen/To exit swipe/Got it안내가있고Nativefocuslost관측. 초기SystemUI-only detector가놓친부분은원본보존·별도재분석/수정했다. ack후회복전완전한SDK원인확정/성공주장없음.
- 첫재현은180초marker timeoutFAIL,사후failure capture까지194.418초. Raw `artifacts/unity-android-e2e-pe_0tdqo/`,metadata `[p10-batch30-diagnostic-a.json]` 참조. 자기emulator종료/AVD·DB·로그보존,기존B29 AVD/앱보존.
- startup진단10/순수guide식별4·전체Python185/49모듈PASS,표준scenario compile-only warning0/error0. GUI builder1회실제PASS,source/staging147/API/wire/metadata/progress검사PASS.
- iOS SDK/공통소비소스는기존actualPASS d543556와보호경로diff0이며이번재실행하지않았다.
- Push/JNI/CoreNative전체/self9/Strict·T02제품refactor는조건미충족으로NOT_RUN. T01/T02PARTIAL/P05FAIL/StoreKit18.6위험/Provider13WAIT유지.

## 입력 후 이어갈 단계

1. 기존종료된AVD/설치앱을무작정재실행/삭제하지않는다. 새근거(실제OS안내와Nativefocus)/진단수정이확보됐으므로허용된추가재검증은최대1회다.
2. 사용자ACK방법이명시되면새source commit·새GUI 소비project/APK(원본Builder·147/source/scenario/nonce·hash검사)·새전용AVD/양port와현재serverPID/실행경로를다시입증한다. 과거PID숫자는재사용하지않는다.
3. `android_fullscreen_notice.known_guide_button`은android/SystemUI의정확한교육안내/단일enabled Got it/bounds만식별한다. 함수는아직실제UI입력을하지않았다. ADB UI입력이명시요청된경우에만이전용기기동일가드로정상ACK를수행하고tap/전후XML·focus/조기marker·DB를기록한다. 권한/계정/보안설정조작은없다.
4. 추가실제E2E가PASS하면지시된AndroidPush/Lifecycle·R09·Kotlin/Swift/managed+duplicate변이·API/ABI/현재소스관계를검증한다. iOS는무조건재실행하지않는다. 자동batch/전용환경확인전Strict강행없음.
5. T01완료시에만T02제품후보2를구현,아니면PARTIAL. 최종코드/test가정해진뒤E secret/PII/FF검사·handoff push·변수비활성정상응답후falseHosted1회·최종보고한다.

현재이번배치push0/Hosteddispatch0이다. 추가실제검증에따라코드가더변경될수있어‘모든code/test commit후단1회’원격CI는아직시작하지않았다. 원격tracking은2c8e7a7,local은이후commit이며재개시fetch로확인한다. 기존b1e3c73 source-hash metadata오탐2건검토근거는이전문서에보존한다.
