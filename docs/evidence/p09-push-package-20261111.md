# P09 Push·패키징 회귀 — 2026-11-11

- 기준: `02005a4` + 이 작업의 harness 변경. 실제 FCM/APNs 발송은 수행하지 않았다.
- `harness/run-push-regression.py`: Backend fake 10, sandbox fake HTTP 1, Android fake 5, Swift fake 8, iOS synthetic simulator 1, staging checksum 1, package negative 1 통과. 결과 `artifacts/push-regression-33t3bvsw/result.json`.
- LOCAL_MOCK Backend→client delivery E2E는 NOT_IMPLEMENTED, Unity Player 알림은 DEFERRED_ENV여서 runner 전체 exit 1이다. 실제 원격 알림 성공으로 계산하지 않는다.
- `harness/check-package-negative.py`는 새 fake fixture에서 Android/iOS binary 누락과 기존 output 보존을 확인했다. 기존 산출물은 변경하지 않았다.
- iOS host 시험은 ad-hoc simulator 서명·synthetic callback 1건이며 실기기/원격 APNs가 아니다. Unity import/export/IL2CPP는 ENV-002 대기다.
