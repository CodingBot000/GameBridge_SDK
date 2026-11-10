# Core·Bridge synthetic 회귀

2026-11-11 `artifacts/contracts-p2sh2c22/result.json`: Kotlin 7건, Swift 7건, 독립 C# registry/facade fake 1 suite PASS, skip 0. 초기화 전 API 거부를 세 언어에서 확인하고 같은 config 동시 초기화, 다른 config 거부 후 기존 초기화 성공, 잘못된 JSON 및 필수 requestId 누락 거부를 검사했다.

C# fake에서는 중복 callback 뒤 완료 횟수 1·무시 횟수 증가, 다른 SDK session 이벤트 무시, cancel/shutdown 경쟁 100회의 단일 완료 및 pending 0을 확인했다. `harness/check-bridge-mutation.py`는 새 격리 사본에서 중복 응답 guard 제거를 감지했다. 이 증거는 독립 managed/Native unit 시험이며 Unity Editor, JNI/IL2CPP, 실제 스토어 검증이 아니다.

후속 `artifacts/contracts-aoe84z1m/result.json`: Kotlin 10건·Swift 11건·C# fake 1 suite PASS. timeout된 C# 요청의 늦은 응답은 무시되고 별도 검증 구매 이벤트는 전달됐다. Swift C ABI는 음수 길이, 최대치를 넘는 길이 및 null pointer를 읽기 전에 거부하고 이후 정상 요청을 처리했다. Android dispatcher의 과대 payload 거부도 확인했다. 실제 Unity JNI 호출은 포함하지 않는다.
