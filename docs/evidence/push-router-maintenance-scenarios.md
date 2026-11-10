# Push router·점검 중 복구 로컬 회귀

2026-11-11 `artifacts/push-router-scenarios-ohmtb_j0`의 Android·Swift unit 및 독립 C# fake는 초기화 전 `PushOpened`를 대기시켰다가 READY 후 한 번 전달했다. 같은 messageId 중복과 `home`/`store` 이외 route를 거부하는 Native router·payload 경계도 확인했다.

양 Native `LocalMockRecoveryTest(s)`는 synthetic HTTP의 응답 유실로 pending 단서를 만든 다음 점검을 켰다. 신규 구매는 `MAINTENANCE`로 차단되고 기존 거래는 같은 idempotency 단서로 복구됐다. 실제 OS 알림, Unity Editor/player와 외부 FCM/APNs는 이 시험에 포함되지 않는다.
