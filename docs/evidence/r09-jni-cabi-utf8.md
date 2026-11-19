# R09 Android JNI 및 iOS C ABI UTF-8 검증

- Android: source `11dcde97468f718a986afd6ab2543cb45f5aeabb`, tracked-clean, Unity 6000.5.8f1 Android IL2CPP Player 및 전용 Android 36 emulator. `harness/run-unity-android-mock-e2e.py --run-local --utf8-probe ...` exit 0, `artifacts/unity-android-e2e-c26jgz32/result.json`. Unity C#에서 Java/Kotlin으로 `한글 🎮🚀`을 전달한 뒤 AndroidJavaProxy callback이 반환된 후 Unity main-thread에서 동일 messageId를 확인했다. 최초 전체화면 안내는 수동으로 닫았다.
- iOS: source `11dcde9` + 당시 미커밋 test-only XcodeGen target(이후 `8e38d0f`에 커밋). iOS 18.6 전용 Simulator의 `CBridgeTests.testHostPushEventRoutingAndDedup` 1건 PASS·skip 0, `artifacts/r09-ios-20261112203456.xcresult`. `GB_Dispatch`에 원시 한국어/emoji UTF-8 bytes를 넘기고 호출이 반환되자 입력 버퍼를 덮어쓴 뒤, 비동기 C callback에서 복사한 messageId가 동일한지 확인했다. macOS host에서도 같은 XCTest 1건 PASS.
- 새 `harness/run-r09-utf8.py`는 opt-in 후 현재 source의 Android Player 및 새 iOS Simulator XCTest를 모두 다시 실행한다. wrapper 전체 재실행은 별도이며 위 증거를 현재 실행으로 위장하지 않는다.
- Native callback을 넘은 메모리 복사·수명 범위에 한정한다. 실제 기기, 외부 FCM/APNs 수신은 검증하지 않았다.
