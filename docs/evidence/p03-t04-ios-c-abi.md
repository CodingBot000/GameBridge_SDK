# P03-T04 Swift C ABI 검증 요약

- 시각: 2026-11-10 Asia/Seoul. 기준 소스: `c8c3522` 및 P03-T04 작업 트리 변경.
- `swift test --package-path ios`: 종료 0, XCTest 13건 중 12 통과·1 skip. C ABI 테스트에서 호출자 UTF-8 입력 버퍼 복사와 callback 응답의 request ID를 확인. Backend opt-in 시험은 이번 실행에서 skip.
- Xcode 26.6 `xcodebuild archive`: 서명 없이 generic iOS device와 iOS Simulator static framework 각각 성공. 두 archive에서 XCFramework 생성 성공. Swift-only framework의 umbrella header/module map 경고가 기록됨.
- XCFramework 검사: device arm64 및 simulator arm64/x86_64 static ar slice 확인. 양쪽에 `GB_ProtocolVersion`, `GB_SetCallback`, `GB_Dispatch`, `GB_Shutdown` symbol 존재. device binary의 외부 `GameBridgeCore` 참조 0건.
- 미검증: Unity C# 컴파일, UnityFramework 링크, 실제 Simulator/기기에서 C#↔Swift 왕복, Swift runtime 링크 및 stripping. status/shutdown 이외 요청은 명시적 미지원이다. 이것은 완성된 배포 패키지 증거가 아니다.
