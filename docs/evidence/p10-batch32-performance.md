# P10-T03 사전 계측 — 배치32

[원본 source/환경/한계·정제 수치](p10-batch32-performance.json). Release .NET 8.0.21 Arm64의 EDITOR_OFFLINE 및 실제 localhost JVM/HTTP/PostgreSQL 범위다. 각 계열 warmup20을 제외한 sample100의 monotonic 실측이다. Task 전체 PASS나 성능 개선을 주장하지 않는다. 기존 lifecycle100/316helper는 별도 실행 범위이며 시간값으로 바꾸지 않았다.

| 계열 | samples | p50 ms | p95 ms | max ms |
| --- | --- | --- | --- | --- |
| Managed createInitialize | 100 | 0.076750 | 0.108958 | 0.528292 |
| Managed callbackProductQuery | 100 | 0.064250 | 0.088833 | 0.413792 |
| Managed shutdownDispose | 100 | 0.025042 | 0.032083 | 0.050042 |
| Managed registryEightInflightDuplicateCancelLate | 100 | 0.276583 | 0.356291 | 1.342542 |
| Backend catalogLoopback | 100 | 3.380542 | 5.244958 | 6.168000 |
| Backend idempotentVerifyLoopback | 100 | 5.472375 | 6.552833 | 7.725541 |
| Backend conflictingVerifyLoopback | 100 | 2.962459 | 4.034583 | 4.417583 |

Managed의 pending/client/transport 잔존0, 정상응답800·예상cancel100·duplicate/late ignored각100이다. Backend는각100측정(+warmup20)의catalog/같은멱등키/409충돌을검사하고새DB의원장1·delta100을확인했다. 409와cancel은예상음성 workload이며제품실패test수가아니다. Unity startup·Native memory·실제UI jank·실기기/실제Provider는NOT_RUN. 첫Backend driver의JSON문자열수량오독으로 aggregateFAIL이었고managed는그실행에서PASS였다. 같은managed측정은반복하지않고수정된Backend만별도새DB에서실측했다.
