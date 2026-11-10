# Core·Bridge synthetic 회귀

2026-11-11 `artifacts/contracts-p2sh2c22/result.json`: Kotlin 7건, Swift 7건, 독립 C# registry/facade fake 1 suite PASS, skip 0. 초기화 전 API 거부를 세 언어에서 확인하고 같은 config 동시 초기화, 다른 config 거부 후 기존 초기화 성공, 잘못된 JSON 및 필수 requestId 누락 거부를 검사했다.

C# fake에서는 중복 callback 뒤 완료 횟수 1·무시 횟수 증가, 다른 SDK session 이벤트 무시, cancel/shutdown 경쟁 100회의 단일 완료 및 pending 0을 확인했다. `harness/check-bridge-mutation.py`는 새 격리 사본에서 중복 응답 guard 제거를 감지했다. 이 증거는 독립 managed/Native unit 시험이며 Unity Editor, JNI/IL2CPP, 실제 스토어 검증이 아니다.
