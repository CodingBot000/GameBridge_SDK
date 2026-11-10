# R12 독립 .NET 수명주기 회귀

`tests/LifecycleStress/Program.cs`는 EditorOffline fake를 사용해 warm-up 5회와 본 시험 100회에서 초기화 중 push 1건을 실제 registry에 넣고, 종료 후 push queue 0 및 pending 요청 0을 확인한다. 모든 회차를 끝낸 뒤 강제 GC로 client·transport weak reference가 남지 않는지도 확인한다.

`artifacts/lifecycle-stress.B1S3dz/result.json`: source HEAD `88a8388` 및 당시 미커밋 시험 변경, 본 시험 100회, live client/transport 각각 0, p50 0.1832ms·p95 0.3072ms. 이 수치는 독립 .NET fake이며 Unity Editor, 실제 기기, 장시간 profiling 결과가 아니다. 테스트가 모든 미래 실행에서 메모리 누수가 없음을 증명하지 않는다.
