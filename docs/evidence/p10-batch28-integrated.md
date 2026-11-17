# 배치28 P10-T01 완료 및 P10-T02 조건부 실제 구현

기준3955e4ea3454f0fbbd6fa09b79fd1e306faaec39,branch handoff/p09-resume-20261113. 기존미추적Demo/cache3경로보존. 최초문서의사용자Editor정상실행확인에대해사용자가이번대화에서정상실행확인을에이전트에위임했다. 따라서새전용project의공식direct smoke1회로실제receipt/marker/exit를확인한다. 라이선스/계정/기존프로세스조작없음.

## A 시작

Hub/CLI/Editor/Client버전read-only대조후 `run-unity-editor-smoke.py --run-local --mode direct`1회. 실패시원본보존·DEFERRED_ENV유지하며Player반복없음. 성공시에만BcurrentPlayer→Strict1회→T01판정,그완료시에만C1/C2제품변경으로진행한다.

## B~E

NOT_RUN. 기존P05FAIL/ENV26OPEN/18.6간헐위험/Provider13WAIT/self-hosted미검증을유지한다. 미실행/실패/Mock와실플랫폼증거를구분한다.


## A 결과 — 자동 batch와 Hub 일반 실행 분리

사용자는 선행조건 확인을 에이전트에 위임했다. 자동 direct는새project `unity-editor-smoke-w2bupii_`에서1회실행,source3955e4e,210.05초/outertimeout124/diagnosticexit2·PROCESS_TIMEOUT이다. receiptCorrelated=false/marker0,compilerCS오류0,실행Client로그의mutex획득실패관측. 실제Editor child 반환값은UNMEASURED다. 원본은ignored artifacts에보존하고[정제결과](p10-batch28-editor.json)에실행/버전/범위를기록했다.

별도로 위임된 **Hub 일반 GUI 실행**은 CUA에서새전용artifact project만디스크에서추가해1회열었다. Unity6000.5.8f1 실제Scene/Hierarchy(Main Camera/Directional Light)/Project/Inspector정상화면을확인했다(**PASS_UI_SCOPE**). 계정/라이선스설정·Cloud연결·기존사용자project를변경하지않았고검증용Editor창은열어둔다. 이것은앞선batchreceipt성공이나Player/SDK시험성공이아니다. 추가direct/CLI자동smoke를반복하지않는다.

버전은Hub3.22.6/CLI1.0.0-beta.13/Editor6000.5.8f1/HubClient1.18.3+d7ffd15. EditorClient bundle CFBundleVersion1.2.0과실제Client product version1.18.1+9fbee8e를분리했다. 정상GUI가있으므로Unity전체실행불가라고단정하지않으며,자동batch경로의channel/mutex문제원인은미확정이다.

GUI상태바에서Multiple ADB server instances 및다른SDK의ADB인스턴스종료경고를실제관측했다. 에이전트ADB kill/start/네트워크/기기설치명령은없지만Unity시작자동동작이므로ADB전체상태불변을주장하지않는다. 대상SDK/프로세스/기기영향은미확정이며새블로커ENV-UNITY-ADB-STARTUP로기록한다. 화면원본/다른사용자project목록·개인정보는공개commit하지않는다.

A자동receipt조건은미충족/DEFERRED_ENV이므로지시대로BPlayer·R09플랫폼영향검사미실행,전체Strict0/DEFERRED_ENV,P10-T01PARTIAL유지. C1(Android세션codec/binding)·C2(Swiftgrantdecoder)는T01완료전이어서제품변경/후보별신규회귀미실행이다. 기존배치27감사·설계는유효하나구현완료로표시하지않는다.

## D 독립 검증 진행

Python149건PASS/skip0,원장/manifest50/meta/두API-source-wire baseline/staging147/actionlint/diffPASS. Core/Native/cohort418·mutation/self9는고정source에서이어확인한다. 실제Editor/Player환경대기를독립fake PASS로대체하지않는다. 현재제품/하네스/테스트/workflow변경0이며코드변경조건의추가Hosteddispatch는계획하지않는다.


### D Core·Native·호환성 결과

source **4d58d132859aa0990ced6a1b7fa67652030eb5a3**의Core collector `core-assertions-7b_9fhgq` exit0/PASS. Kotlin10test/helper50(37normal+13expected),Swift12/122(112+10),managed0test/check1/helper418(198+220),복원418,조건분기419(추가OFF0/ON1). duplicate-only 정상0/변이nonzero·예상negative1/원본hash동일·정상전체복원확인. lifecycle100samples/helper316(15+300+1),liveClients0/liveTransports0. assertion outcomes/래퍼밖/JNI실제Player범위는UNMEASURED다. Editorinclude없음.

같은shippingcode/전후79hash일치에서Native선택회귀 `artifacts/batch28/native` Android42JUnit/Swift38XCTest 모두exit0·실패skip0(추가진행문서만미커밋). 실제OS인증UI/결제·FCM/APNs/권한·Player는아니다. C1/C2새설계case를실행/구현한것으로표시하지않는다.

`artifacts/batch28/artifact-inspection.json`은기존dc45a2fNative산출물의현재source79hash/UPMmanifest·checksum147/javap3class/Cexport4개양slice를재검사해동일확인했다. 새빌드/새현재Player성공은아니다. 제품API/wire/source변경0이며P10-T01baseline은덮어쓰지않았다.

GUI후ADB읽기전용후속에서는5037에adb PID68316 listener가있음을관측했다. 사전owner/종료대상/기기영향은여전히미측정이며lsof/ps외ADB명령은실행하지않았다. 이관측만으로원래server가복원됐다고주장하지않는다.
