# 배치27 Unity IPC 복구 및 P10 조건부 진입

기준 cf276b7ca8e5dc92c6bbd13306c8fc0a869d0faf,branch handoff/p09-resume-20261113. 기존 미추적 Demo/cache3경로와 사용자 기기·DB·인증/라이선스 파일을 보존한다.

## A 시작

공식 Editor/Client/Hub/CLI 로그를 read-only로 대조한다. 원본 로그와 자격값은 ignored artifacts/batch27에만 보존하며 공개 문서에는 제한된 관측만 기록한다. 새 전용 project의 CLI/direct Editor smoke 각1회,근거 있는 수정 최대2회. 라이선스/계정/Hub설정 수정 및 사용자 프로세스 종료는 금지한다. 실제 Editor PASS 전 B Player를 강행하지 않는다.

## B~E

아직 NOT_RUN. P10-T01 실제 current Player와 Strict가 완료되지 않으면 PARTIAL 유지하며 P10-T02는 책임 경계 감사·후보·회귀 설계만 수행한다. 기존 P05FAIL/ENV26OPEN/Provider13WAIT/StoreKit18.6 위험/self-hosted미검증을 유지한다.

- 배치27 A 최종검증/블로커: CLI새project비교1회는timeout180초/actualCLIexit6/181.47초,validator exit2,receipt/marker없음,CS compile오류0/IPC부재5회. direct1회는timeout210초/124/210.05초였다. 실제Editor smokePASS가없어A DEFERRED_ENV,복구미완료다. 확인된관측층은protocol505/Clientglobalmutex거부와Editorchannel부재이며누가mutex를유지하는지까지확정하지않는다. 공식명령옵션에서안전한수정근거가없어추가수정시도0/최대2,Hub/라이선스/계정/전체프로세스조작없이대기로전환한다. B현재Player NOT_RUN,C전체Strict호출0/DEFERRED_ENV,T01PARTIAL유지. D는제품변경없이경계감사·최대2후보·회귀설계를수행하고E독립검증/CI/FF인계를계속한다.


## A 최종 관측·판정

실제 비교 source **cf276b7ca8e5dc92c6bbd13306c8fc0a869d0faf**. CLI1.0.0-beta.13,license status active/exit0. 새 빈 전용project 두 개에 같은 Editor method를 작성해 batch mode/version 확인→새 receipt write→marker 출력까지 요구했다. SDK API/구매/Player 성공을고정반환하는Mock이아닌Editor초기화도달검사(tests0/check1)다.

| 경로 | 실제 실행 | 결과 |
|---|---|---|
| 공식6000.5.8f1 직접실행 | `-batchmode -quit -projectPath ... -executeMethod Batch27EditorSmoke.Run -logFile ...` | 210.05초/timeout124,validator2,receipt/marker없음,compile CS오류0,DEFERRED_ENV |
| Unity CLI run | 별도새project/같은executeMethod/logFile,CLI timeout180초 | 181.47초/CLI6,validator2,receipt/marker없음,compile CS오류0,DEFERRED_ENV |

원본은 artifacts/batch27/smoke-direct 및smoke-cli에만보존한다. 공개[정제JSON](p10-batch27-ipc.json)은PID/exit/시간·범주만기록하며원본payload/자격값/라이선스/개인경로를싣지않는다. 옵션은[Unity6000.5 공식참조](https://docs.unity.com/en-us/engine/6000.5/manual/unity-editor/command-line-arguments/editor)의실행방식을사용했다. 라이선스확인생략옵션은없다.

공식Client/Hub/CLI로그와기존batch26Editorlog를read-only대조했다. batch26시각의기존HubClient가CLI LocalIPC1.19.0-rc.3 handshake를505 UnsupportedProtocol로거부했고,별도CLIClient가1.19.0-rc.3로시작한뒤pipe종료를기록했다. Editor-bundled1.18.1 Client는여러PID에서globalmutex획득실패였다. 현재direct Client에도같은mutex획득실패,두경로Editor에는channel부재·재연결timeout이있었다. Hub의license/entitlement응답및active상태는Editor메서드실행증명이아니다.

**확인된장애층은IPC protocol거부·mutex획득실패·Editorchannel부재다. 정확한mutex소유자/전체인과관계는미확정이며복구하지못했다.** 정상HubClient의socket열림은read-only관측했지만그사실만으로mutex소유를단정하지않는다. 단순named-pipe/로그문구를바꾸거나라이선스파일조작으로우회하지않았다.

각비교1회/추가수정시도0(허용최대2). 공식옵션에서이관측을해결할안전한스크립트수정근거가없었고Hub/계정/Client서비스조작은범위밖이므로추측성재시도하지않았다. own전용process session만timeout정리,기존Hub/Client/타Editor/사용자기기종료없음. A DEFERRED_ENV. B현재Player NOT_RUN,CfullStrict0/DEFERRED_ENV,P10-T01PARTIAL유지.

### 재현 도구·판정 계약

harness/run-unity-editor-smoke.py는명시--run-local/--mode로매번새artifact project를만들며원래Editor licensing경로를그대로사용한다. nonce-correlated receipt·marker1회·process0이모두있어야PASS,active/initialized문구·부분결과·nonzero·timeout·foreign/duplicate receipt는PASS가아니다. compile실패는FAIL로분리하고공개관측에는IPC오류개수/버전만포함한다. 계정/라이선스조작·자동retry·사용자project입력은없다.

새계약6단위PASS/skip0및실제실패log의read-only판정DEFERRED_ENV확인. 이새도구로Editor를다시실행하지않았으며실제비교는보존된artifact wrapper의명령이었다. 도구unitPASS를실제EditorPASS로표시하지않는다. 환경복구후각경로1회검증용명령은USER_SETUP에기록했다.

## B 준비 inspection과 실행 미실행

기존batch26 UPM147checksum/currentSDKsource및Notifications2.5.0/Newtonsoft3.2.2 exactCache일치. 기존artifact source는dc45a2f이며이후shipping code는같다. 새Player를위해과거staging을검증없이사용하지않았다. 현재A차단이므로AVD/Simulator/Player/Player용DB는만들지않았으며기존batch25PlayerPASS를현재로바꾸지않는다. Native/API/선정ABI검사는E의독립결과로따로기록한다.

## D 선행조건 차단과 독립 감사

[인증·구매·푸시책임감사](p10-auth-purchase-push-batch27.md)에실제호출/소유경계·기존testcase·추가회귀설계를정리했다. Android세션codec/검증과Swiftgrant응답decoder두후보,제품변경0/설계caseNOT_RUN/성능개선미측정이다. Push는이미host/등록/router가분리돼형식적수정을제외했다. P10-T01PARTIAL이므로T02제품리팩토링진입조건을우회하지않는다.

## E 진행

전체Python149건PASS/skip0,신규진단6건Hosted연결. 원장/manifest/meta/API/source/wire/actionlint/diffPASS. 고정source에서Native/managed·mutation·self9및API/선정ABI를검증한뒤명시handoff FFpush/false Hosted-only1회로인계한다. 실제Provider13WAIT/P05FAIL/ENV26OPEN/18.6위험/self-hosted/Release미검증유지.


## E 고정 소스 독립 회귀

source **ffed5c2e83c1b02ec1f68edb590a918e9556174c**의 Core collector는 tracked-clean에서 실행해 `core-assertions-_jnkfd1a` PASS/exit0. Kotlin10test/helper50(37+13),Swift12/122(112+10),managed0test/check1/helper418(198+220),복원418,분기419(추가OFF0/ON1)이다. duplicate-only 정상probe helper2/exit0→변이부분helper1/process134(의도negative1)→원본hash동일·정상전체418/exit0. assertion outcomes/래퍼밖/JNI scope는UNMEASURED이며framework test수와helper수는별개다.

lifecycle `lifecycle-stress.IDb0Hp`: 5warmup/100samples에서helper316(15+300+1),liveClients0/liveTransports0. 이는managed fake 관측이며Unity/native memory 또는성능개선증명이아니다. `--include-editor`는사용하지않아이번Editor 회귀는NOT_RUN,과거2test/32helper를현재로복사하지않는다.

이어같은shipping code의 Native fake/session/store/push 선택회귀 `artifacts/batch27/native`에서 Android42JUnit/failure0/error0/skip0/exit0,Swift38XCTest/failure0/skip0/exit0. 기록중미커밋변경은진행문서뿐이며79shipping hash를전후실측확인했다. 실제Google/Apple로그인·StoreKit/PlayStore결제·FCM/APNs·OS권한시험은아니다. 새T02설계case를이기존test42/38로대체하지않는다.

ABI/source re-inspection은 `artifacts/batch27/artifact-inspection.json`: 기존dc45a2f산출물의79shippinghash·UPMmanifest/checksum147현재일치,Nativejavap3class표면및nm C-export4개양slice이전비교와동일. 새Nativebuild/현재Player성공으로주장하지않는다. 보존staging이현재SDKsource와일치함을확인한B준비inspection의연장이다. public/internal API/wire baseline파일변경없음.
