# 수명주기 측정 — 2026-11-11

- 기준: `e689dd7` + 측정 코드 미커밋 변경. macOS Darwin 25.5 arm64, .NET 8.0.21, Release, **독립 EditorOffline fake**.
- `scripts/stress-csharp-lifecycle.sh`: warm-up 5회 후 100회 각각 client 생성 → 초기화 → fake 상품 조회 → shutdown, p50 **0.1467ms**, p95 **0.2125ms**. 각 회차 shutdown 및 pending 0 확인. client Dispose 시간은 포함하지 않았다. 결과 `artifacts/lifecycle-stress.zrf6NN/result.json`.
- 첫 실행은 생성 시간을 측정에 포함하지 않아 별도 이력으로 남겼고 위 수치로 대체하지 않는다 (`artifacts/lifecycle-stress.5nblL2`).
- 이 수치는 Unity Editor/player, JNI/IL2CPP, 실제 스토어·네트워크 지연, 메모리 누수 또는 실기기 성능을 나타내지 않는다. 해당 profile 및 scene 전환 측정은 NOT_RUN이다.
