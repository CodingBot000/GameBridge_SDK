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
