# 배치34 통합 검증과 잔여 조건

시작 source3313c847e77c17be5130451b091196db8eee0383. 전체 SDK는 BLOCKED_INTERNAL이며 배치34 모든 완료조건을 충족한 상태는 아니다.

| 영역 | 실제 결과 | 판정과 남은 조건 |
| --- | --- | --- |
| A OpenAPI | 순서/중복/누락·DTO23 및 request binding 검사, OpenAPI16시험/문법PASS. LOCAL32관측+합성Sandbox/Local10시험·132구조,24operation 모두200근거 | PARTIAL. SSE 전체event payload/동적Map 세부계약 및 모든 오류분기 도달성을 증명하지 않아 BUG-017 OPEN |
| B 감사 | 64개 각각 완료기준/충족/미충족/외부·환경/권장상태 검토 | P00-T03만 최소프로젝트 조건으로 정정.25구현/39진행, local23PASS/1FAIL/40PARTIAL. 기준별 근거 미완결 항목은 감사 JSON에 구체적으로 기록 |
| C 성능 | 새iOS18.6 Simulator/실제배포framework C ABI initialize/status/shutdown 각warmup20+100,120session/360callback | T03 PARTIAL. harness outstanding0이며 SDK 내부pending이나continuation 누수없음을 뜻하지 않음. AndroidJNIheap·Taskcancel NOT_RUN. 새UnityPlayer 반복/Scene100·frame1000 및 runtimeProfiler관측은 후속구간 참조 |
| D 호환성 | batch32↔33 JVM public4class 동일. batch33동일Native소스/147package의 신규Android/iOS Unity import/build/Player 각PASS | 독립소비 검사PASS, T03의존으로T04 전체PARTIAL. 첫Android port충돌/dirty guard실패는원본보존 |
| E/F Strict | 실제required58lane 추출,20종E1조건 판정·E2 identity비교 및6시험 | E1 실제DEFERRED_ENV/2. E2 자원생성·전wrapper실관측배선未완성, 실제전체Strict0회 NOT_RUN |
| G 문서/RC | 주요9문서 현재사실반영, 기존패키지를 재사용한새DEV_RC source/manifest 검토 | 정식Release아님. 실Provider13/기존StoreKit위험·self-hosted 대기 유지 |
| H 회귀/Hosted | 초기Python261→추가계측코드263 PASS, OpenAPI16/문법,Core/managed/자체시험/TC 및 양Player 증거 | 최종 source/Hosted/원격HEAD는 후속결과를 따른다 |

## 실제 결과의 범위

- HTTP의 누락 Idempotency-Key가 generic500이던 내부 결함을400 INVALID_ARGUMENT로 수정했다. MockMvc와 실제HTTP로 확인했으며 Provider 설정 없이 호출했다.
- 합성HTTP의 최초동일DB profile혼합은 제품DB소유guard가 거부했다. 별도DB로분리한 뒤 검증기의literal route우선 매칭 오류를 고쳐 최종10시험0failure/error/skip. 원본실패로그는 artifacts에 보존했다.
- 문자열을 전부 redacted로 바꾼 응답구조만 capture한다. 토큰/proof/키·요청body/원문응답문자열을 정제JSON에 저장하지 않는다. 값의 의미·실Provider서명 검증 성공과구분한다.
- iOS C ABI p50/p95/max와 peakRSS는 p10-batch34-cabi-performance.json. process high-water RSS증가를누수로판정하지 않는다. 기존SwiftCore100측정을 C ABI로재명명하지 않았다.
- 새Unity iOS는24marker/원장1·100, Android는별도실제JNI/PII경로다. 두쪽모두명시적CLI batch/Simulator·AVD이며GUI/실기기/실스토어로표현하지않는다. 각자생성기기·서버만종료하고디스크/DB원본보존.

## 증거

- p11-batch34-openapi-http.json, p11-batch34-openapi-synthetic.json
- p11-batch34-task-audit.json
- p10-batch34-cabi-performance.json
- p10-batch34-binary-api.json, p10-batch34-unity-android.json, p10-batch34-unity-ios.json
- p10-batch34-preflight.json

## 다음 실제 구현

1. SSE event와동적Map의세부명세, 오류별실행대응 보강으로BUG-017의잔여판정.
2. Android JNI/heap, iOS Task/continuation 수명 및 Unity weak client1 잔존의 메모리 root/CPU blocking 분석. 현재CABI/harness카운트를대체증거로쓰지않는다.
3. E1의license·AVD/secret/TC/소유계획 실관측과E2자원생성·전lane소유전파 완성 후에만 전체Strict최대1회.
4. P11 감사JSON의각Task별 미충족근거를 실제시험으로 닫는다. P05FAIL·StoreKit26OPEN·18.6간헐위험·Provider13WAIT·self-hosted미검증은별도로유지.

## 최종 로컬 회귀

최종Python262/17.004초/exit0. OpenAPI16·문법0, HTTPcapture+오류MockMvc4시험0, 합성HTTP10시험0/132구조. Core는Kotlin10/50helper,Swift12/122helper,managed418/복원418·분기419,duplicate mutation감지 및100 lifecycle sample/316helper이다. self9는최신고정6b8d884에서47test(정상44/예상음성3)/checks9/exit0. TC는11실행(정상10/예상변이1)·정상복원exit0/자기container정리검증. 다른범위의test/check/helper/sample/Player 수를합산하지않는다. code/test가바뀌지않은범위만이전source근거를유지했다. 상세p10-batch34-regression.json.

## Unity Player 후속 실측

새전용 iOS18.6 Unity6000.5.8f1 Player에서120회반복(20warmup/100측정),Native진단의메인스레드왕복/임시Scene생성·해제/SDK종료를측정했다. p50/p95는init66.493/66.669ms,Native진단왕복66.821/67.313ms,Scene66.527/66.717ms. frame1000개 p50/p95 33.333/33.456ms(max49.754ms). 이값은Simulator/Player프레임스케줄링포함 왕복이며순수Native실행시간·CPU blocking이아니다. UnityruntimeProfiler메모리및forcedGC후weak client1,완료후pending0을관측했다. 잔존1의원인/누수여부는미확정이고0으로바꾸지않았다. 첫app초기화시간·Task/continuation·Androidheap이남아T03/T04 PARTIAL유지. rawsample미보관으로수치계약은summary타입/범위/count검사이며percentile재계산은NOT_CHECKED다. p10-batch34-unity-performance.json참조.

추가계측후최종Python263/16.708초 PASS,변경영향GUI/cache14시험및성능summary6시험 PASS. 새최신source를고정하고Hosted1회와동일source의self/TC/Core결과를후속기록한다.

## 최종 동일source 및 원격 결과

[Hosted44287600414](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44287600414), source648bb807baeab4e83b037856a9ae04f84e8a2154,release_validation=false dispatch1회 SUCCESS. inventory/Backend/Android/Swift-iOS/basic SUCCESS,Unity/Release SKIPPED. Ubuntu공식inventory job134744193895에서Python60모듈263시험·OpenAPI문법/정상·순서반전·중복·request body누락 fixture통과를확인했다. 최초배치33 이식성실패를새source에서검증했다. 합성HTTP10/MockMvc4의전부를Hosted가실행했다고주장하지않는다. Hosted는선정cohort,로컬은별도실행범위다.

같은648bb80에서localCore(Kotlin10/Swift12/managed418+변이복원),self9/47test/check9,TC11/예상변이1·정상복원·container정리도각PASS. 원본은core-assertions-v3o3wh48,harness-self-cn8tm4r9,purchase-testcontainers-27qjah_h. 최종Python263은06f7120 code에서실행했고이후648은문서차이뿐이며Ubuntu도263으로일치한다. CI이후code/test/workflow변경0,최종결과문서만후속커밋한다.

현재원장64/25 IMPLEMENTED·39 IN_PROGRESS/local23PASS·1FAIL·40PARTIAL,외부13WAITING_USER. P00-T03만개별완료기준으로승격했다. P10-T03/T04·P11 PARTIAL,BUG-017 OPEN,Strict E1/E2/E3는부분구현이며전체Strict0회. 기존P05FAIL/StoreKit26OPEN·18.6간헐위험·실Provider/self-hosted미검증을유지한다.

GitHub CLI의일시적연결실패때connected read로원격3313c84를확인했고,복구후freshfetch/ancestor검사·648bb80 FFpush·local/remote동일·정상vars0뒤새CI를요청했다. 재실행·force·main변경·runner등록·Release생성0. 기존Demo/cache와이번Gradle생성backend/.kotlin도비추적상태로보존했다.

최종문서commit SHA와local/remote HEAD는Git이력에서조회한다. 마지막인계는코드648bb80과의diff가문서/정제evidence뿐임을확인한뒤동일handoff로FFpush한다.

## 작업별 커밋

| SHA | 작업 |
| --- | --- |
| ec4a036 | fix(http): [P11-T01] validate DTO and HTTP contracts and classify missing headers |
| 24de83a | docs(audit): [P11-T01] assess all task criteria and reconcile minimum project evidence |
| ee36070 | docs(progress): [P11-T01] reconcile counts after individual task closure |
| 950f816 | test(performance): [P10-T03] measure packaged C ABI callbacks on owned simulator |
| f6934ac | test(compatibility): [P10-T04] verify selected JVM surfaces and fresh Unity iOS consumer |
| fd7a55f | feat(harness): [P11-T04] evaluate strict prerequisites and validate owned identities |
| 45c8e9d | test(android): [P10-T04] verify fresh owned consumer after endpoint availability returns |
| 41eabe1 | test(openapi): [P11-T01] validate synthetic profile responses without retaining secrets |
| 6b8d884 | docs(integration): [P11-T03] reconcile batch34 evidence and scoped dev candidate readiness |
| 8f3685f | docs(validation): [P11-T04] record frozen local regression and dev candidate evidence |
| 06f7120 | test(performance): [P10-T03] measure actual Player lifecycle scenes frames and memory |
| 648bb80 | docs(performance): [P11-T03] record Player observations and freeze Hosted validation source |
