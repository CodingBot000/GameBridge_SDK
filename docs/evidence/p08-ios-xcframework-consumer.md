# P08-T02 SwiftPM 및 XCFramework 독립 소비 검증

- 소스 `fd4102f`의 iOS Native 제품 경로로 `artifacts/ios-p08-reverify-20261113/GameBridgeNative.xcframework`를 생성했다. 당시 문서 및 test-only source consumer 변경은 미커밋이었다. f1e12b6 이후 iOS Native 제품 파일 차이는 없다.
- `scripts/build-ios.sh --xcframework` exit 0: 서명 없이 device 및 simulator archive를 생성했다. `verify-xcframework.py`는 device arm64, simulator arm64/x86_64 및 각 slice의 C ABI 4개 symbol을 확인했다.
- 별도 `ios/consumer-check/main.swift`를 iOS Simulator arm64 대상으로 XCFramework import·link했으며 `vtool`의 플랫폼이 IOSSIMULATOR임을 확인했다. 이 실행 파일을 Simulator에서 실행한 것은 아니다.
- `scripts/smoke-ios-source-consumer.sh`는 `GameBridgeCore`/`GameBridgeApple`을 SwiftPM package dependency로 사용하는 별도 source consumer를 macOS host에서 빌드·실행했다 (`artifacts/ios-source-consumer.UIxcpt`). 이는 iOS 실기기 실행이 아니다.
- XCFramework Info.plist SHA-256 `d5bf66d1e08ea8be8b8e4c9ca50fea112e5cee031e85c722dd033bb5e0122b22`; 독립 iOS Simulator consumer binary SHA-256 `dbaa22717a5a2ef2a9f55f26de476fa4108557450960029604ee3ec5d952e749`. 서명된 기기·실제 Apple 인증/스토어는 검증하지 않았다. 산출물과 원본 로그는 Git에 포함하지 않는다.
