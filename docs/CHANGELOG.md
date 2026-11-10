# 변경 이력

## 0.1.0-dev — 개발 중

- Android Kotlin·iOS Swift SDK와 Unity C# bridge, 로컬 Mock 및 실제 Provider 연결 경로를 구현했다. 실제 계정과 스토어, 기기 검증은 별도다.
- Backend에 인증 세션, 거래 검증·원장 멱등성, 구매 완료 재시도, 푸시 토큰 관리와 로컬 개발 경로를 추가했다.
- Xcode 로컬 StoreKit과 전용 개발 서버에서 응답 유실 및 Keychain 인스턴스 재생성 복구를 검증했다. 별도 프로세스 재시작 시험에서 journal 재생성 실패를 재현해 수정하고 로컬 재시험했다.
- Android Maven, iOS XCFramework, Unity UPM staging과 독립 소비·무결성 검사를 추가했다. Unity Editor import 및 player 검증은 미실행이다.
- 50개 회귀 시나리오 manifest, 격리 DB와 simulator 시험, 누락 검출 및 strict-local gate를 추가했다. 부분 검증과 실패가 남아 전체 통과 상태가 아니다.
- Unity 수명주기와 Native 인증의 동시 401 refresh 경로를 보강하고 synthetic 회귀를 추가했다. 실제 플랫폼 검증 범위는 [PROGRESS](PROGRESS.md)와 [FINAL_REPORT](FINAL_REPORT.md)를 따른다.
