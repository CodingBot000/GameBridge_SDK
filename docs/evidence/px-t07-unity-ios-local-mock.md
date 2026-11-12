# PX-T07 Unity iOS Simulator LOCAL_MOCK 검증

**로컬 Mock PASS. 실제 Apple 로그인·App Store 결제·APNs는 NOT_RUN.**

- 검증 소스: `87323334ec51772e1d4521827447f1690e7ff56c`, 실행 당시 tracked-clean.
- 환경: Unity 6000.5.8f1, Xcode 26.6 (17F113), iOS 18.6 Simulator ARM64, Unity IL2CPP 개발 빌드. 실제 iPhone은 미검증.
- 실행: `python3 harness/run-unity-ios-mock-e2e.py --run-local --adhoc --staging <검증된 UPM staging>`; 종료 코드 0. 전용 새 Simulator 및 PostgreSQL DB 사용.
- 서명: 최초 `CODE_SIGNING_ALLOWED=NO` 시도는 로그인 INTERNAL_ERROR로 실패. 성공 시험은 Apple 계정·개인키 없이 Simulator 로컬 ad-hoc 서명을 사용했다. 무서명 성공은 주장하지 않는다.
- UPM staging manifest SHA-256: `d0f88d08e435d2de9b11028f15db9fbbcc526d894aeedeb110cb23c309dfec7e`. iOS Simulator XCFramework binary SHA-256: `f8a1882e9649d33a18bf891b4f6cba226c363301041cc59d43cb95c37d6b748f`. UnityFramework binary SHA-256: `125e3eb7df14c80539c5b13e4ce0f816b6aa1b13361607c3ba4ba0e16f43712c`.
- Unity Editor에서 새 소비 프로젝트를 import하고 Simulator Xcode 프로젝트를 생성했다. Xcode에서 XCFramework 링크 및 GB_ProtocolVersion/SetCallback/Dispatch/Shutdown C ABI 심볼을 확인했다.
- Unity C# → Swift C ABI → 로컬 Backend → PostgreSQL 경로에서 초기화·Mock A 로그인·상품 조회·Mock 구매·서버 잔액 100 증가·로그아웃과 Native diagnostics를 확인했다. 각 API 응답과 diagnostics는 Unity 메인 스레드에서 확인했다. Native callback 자체가 메인 스레드에서 발생했다고 주장하지 않는다.
- 서버 HTTP 200 trace: mock-auth 1, catalog 1, entitlements 2, verify 1, logout 1. DB `wallet_ledger` 1건, delta 100. Unity/Native request ID와 서버 HTTP request ID는 서로 별도로 발급된다.
- 결과 JSON SHA-256: `14aedea87a28adc05f881fee8dbc81b1c96363a167f0f26a25e0fb3097252d08`. 인증키·원본 로그·DB·Simulator 데이터는 Git에 포함하지 않는다.
- 성공 실행은 별도 사용자 UI 조작 없이 수행했다. 앞선 시도에서는 테스트 Simulator의 예상치 못한 알림 권한 팝업을 거부했고, 테스트 앱의 자동 알림 요청을 끈 뒤 재검증했다. iOS 26.5 SKTestSession 문제는 별도이며 이 시험은 StoreKit을 사용하지 않는다.
