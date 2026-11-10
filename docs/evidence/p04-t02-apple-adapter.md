# P04-T02 Apple adapter 검증 요약

- 시각: 2026-11-10 Asia/Seoul. Xcode 26.6, iOS 26.5 Simulator, Swift 6.3.3. Apple 계정이나 실제 credential은 사용하지 않았다.
- `swift test --package-path ios`: 종료 0, XCTest 16건 중 15 통과·local Backend opt-in 1 skip. Apple fake gateway/backend 시험 3건에서 server raw nonce 전달, 취소·동시 호출 BUSY, profile 불일치 거부, revoked 상태의 로컬 삭제와 서버 revoke 실패 분리를 확인.
- XcodeBuildMCP Debug `build_sim`: 성공, 경고·오류 0. UIKit/AuthenticationServices gateway를 Simulator target에서 컴파일했다. 서명 entitlement 예제는 앱 bundle에 포함되지 않는 것을 확인했다.
- 미완료: Backend 실제 challenge/exchange·Apple 서명/nonce 검증, Native sample/Unity 실 Provider UI, 공통 결제 UI gate, 실제 Apple 계정·서명·기기 시험. 사용자 설정은 USER_SETUP의 USER-AUTH-APPLE 참조.
