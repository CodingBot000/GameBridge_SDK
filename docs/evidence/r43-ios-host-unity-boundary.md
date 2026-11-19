# R43 iOS Host delegate 및 Unity 전달 경계

- Swift host: source `1f3d3a4` + 당시 진행 문서 변경, iOS 18.6 전용 Simulator `GameBridgePushTests/PushHostTests.testSyntheticHostCallbacksAndCompletion` 1건 PASS, 실패·skip 0 (`artifacts/r43-ios-20261112204204.xcresult`). 기존 `UNUserNotificationCenter` delegate 보존과 host completion 호출을 synthetic callback으로 확인했다.
- Unity Player: source `1f3d3a4b8919afae928b96af46a444cbdc048343`, tracked-clean, Unity 6000.5.8f1 iOS 18.6 Simulator ARM64에서 `harness/run-unity-ios-mock-e2e.py --run-local --adhoc --host-callback-probe ...` exit 0 (`artifacts/unity-ios-e2e-f7bwumjl/result.json`). Synthetic `iOSNotificationPushTrigger`를 Unity `IosPushHostAdapter`에 주입해 Swift C ABI를 거쳐 Unity `PushReceived`로 돌아오는 단일 전달·중복 억제·main-thread를 확인했다. 테스트 전용 linker 보존 설정을 사용했다.
- 두 시험은 분리된 합성 입력이다. Swift host delegate의 보존·completion과 Unity host callback 경계를 함께 다루지만 실 APNs 원격 전달이나 실제 단말의 host 구성 전체를 증명하지 않는다.
- `harness/run-r43-host.py`는 opt-in 후 현재 source의 새 Unity Player와 새 host Simulator XCTest를 각각 실행하고 성공·마커·skip을 확인한다. wrapper 자체의 전체 재실행은 별도다.
