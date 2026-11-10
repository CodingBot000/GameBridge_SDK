# 기능 호출 경로 1차 조사 — 개발 중

2026-11-10 소스 기준. `PARTIAL`은 열거된 일부 경로만 존재한다. 단위/fake 시험, local-mock 실행과 실제 플랫폼 검증은 서로 대체하지 않는다. 최종 P11 감사가 아니다.

| 기능/Unity 공개 표면 | Editor offline | Android/iOS native bridge | Native sample / Backend | 현재 판정 |
|---|---|---|---|---|
| 초기화 `InitializeAsync` | fake 초기화 구현, 독립 .NET smoke | `sdk.initialize` 미연결, 명시적 UNSUPPORTED | Native local-mock sample은 자체 초기화 | PARTIAL |
| 상태/종료 `GetStatus`, `ShutdownAsync` | fake 및 상태기계 | status/shutdown 제한 처리 | Native sample은 독립 소유 | PARTIAL; Unity Editor/IL2CPP 미실행 |
| 로그인·복원·로그아웃 | fake 동작 | auth operation 미연결 | Android/iOS local-mock 실제 로컬 Backend 시험; Google/Apple 경계는 fake 시험 | PARTIAL; 실제 인증 미실행 |
| 상품 조회·구매·잔액·복구 | fake 두 상품과 모의 원장 | store operation 미연결 | Native local-mock 구매/잔액 시험. 실 store gateway, server verifier/grant/finalizer는 부분 구현 | PARTIAL; 실스토어 미실행 |
| push 권한·등록·해제 | fake 상태 | push operation/Unity host adapter 미연결 | FCM/APNs host와 단발 sender 부분 구현. local-mock token 등록/삭제 확인 | PARTIAL; 실제 원격 미실행 |
| 설정 `GetServiceConfigAsync` | fake default | config operation 미연결 | Backend 기본값 route; cache/maintenance 제어 미구현 | PARTIAL |
| 진단 `GetDiagnostics` | C# registry snapshot | Native ring 및 facade 연결 미완료 | Android/iOS typed ring unit 시험만 존재 | PARTIAL |
| host push/lifecycle | 미완료 | operation 미연결 | Native payload allowlist unit 확인, queue/dedup 미구현 | PARTIAL |

구매 서버는 Apple synthetic verifier→DB grant 동시 시험, Google verifier 및 finalizer fake 시험이 있다. provider 설정·공개 verify endpoint·durable Google finalization·Native sink가 이어지지 않아 실거래 지급 경로는 미완성이다. iOS StoreKit local 상품 조회는 simulator 시험에서 실패했다. Unity staged package의 import 및 Android/iOS export는 라이선스·모듈 제약으로 미검증이다.

초기 검색에서 대상 소스에 `TODO`, `FIXME`, `NotImplementedException`, `fatalError(` 표기는 발견되지 않았지만, 위의 호출 경로 누락은 실제 미구현이다. 이 표는 코드 변경에 따라 계속 갱신한다.
