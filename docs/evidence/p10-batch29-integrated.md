# 배치29 Unity GUI 빌드 경로 검증과 P10 재개

**사용자 요청으로 안전 중단. 배치 미완료.** [재개 체크포인트](p10-batch29-resume.md)를먼저읽는다. A GUI메서드·B APK빌드PASS,C Android실행timeoutFAIL,D 독립후보testsPASS. iOS export/Player·최종E CI/FFpush는아직미실행이다.

기준7fe7c4ad3aab56302ec6b988b9d1b747ebe9cf94,branch handoff/p09-resume-20261113. A~E 실제수행범위를source/nonce/기기·산출물/검사종류와함께기록한다. GUI와batch,빌드와실행,현재와과거증거를분리한다. 기존미추적Demo/cache·사용자project/기기/DB·라이선스보존. P05FAIL/StoreKit18.6위험/Provider13WAIT유지.

## A 시작

기존전용GUI project에test-onlyEditor menu를추가하고실제컴파일/UnityEngine메서드/nonce·소유project·버전검사를수행한다. 장시간batch재시도없음. 단순파일PASS는허용하지않는다. B~E아직NOT_RUN.


## 사용자 요청 안전 중단 시점

[정제GUI probe](p10-batch29-gui-probe.json)와[Android GUI APK](p10-batch29-android-build.json)는실제생성·메서드/파일검증PASS다. Android[실제E2E 결과](p10-batch29-android-e2e.json)는install/launch후marker timeoutFAIL을보존했다. 소유AVD/PID/양port 및5037동일SDK/server guard를사용했으며타기기/서버조작·실패빌드fallback은없었다. 원본AVD/DB/로그보존,자기emulator만종료했다.

[후보계약tests](p10-batch29-candidate-tests.json): Kotlin18/Swift20 PASS(신규3+2). codec/decoder제품변경0이며T01/T02 PARTIAL이다. GUI19개영향단위와cache2/binding5등을검증했으나기존전체149/fullNative/self9/Strict를현재실행으로표시하지않는다.

iOS GUI test-only helper/준비·receipt/exporttree·명시E2E입력·음성4건은코드로보존하되실제Unity컴파일/export/Xcode/Simulator실행NOT_RUN이다. 현재Android소비GUI는idle로열려있고진행중빌드/Player/Backend작업은없다. 네트워크중단예정사용자요청에따라새네트워크/Hosted/push를시작하지않았다(각0회). 재개지시후[정확한명령·남은순서](p10-batch29-resume.md)로계속한다.
