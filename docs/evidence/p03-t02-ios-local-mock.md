# P03-T02 iOS LOCAL_MOCK 검증 요약

- 시각: 2026-11-10 Asia/Seoul. 기준 소스: 커밋 `8df473c`와 P03-T02 작업 트리 변경. 해당 커밋은 Git 이력의 Task ID로 찾는다.
- 환경: Xcode 26.6, Swift 6.3.3, XcodeGen 2.46.0, iOS 26.5 Simulator, local-mock Backend와 전용 PostgreSQL 17.6. 외부 계정·실결제 미사용.
- macOS `swift test`: opt-in local-mock 수직 시험 포함 XCTest 12건 통과, 실패 0. 서버 로그인·상품·중복 Mock 구매·서버 잔액·메모리 저장소 복원·로그아웃을 확인.
- XcodeBuildMCP Debug Simulator 빌드·설치·실행 성공. UI smoke 1건 통과, 실패 0·skip 0: Mock 로그인·상품 조회·구매 후 `GRANTED / PENDING`, 앱 재시작 후 Keychain 세션 복원, 로그아웃 완료 표시 확인. 앞선 UI 자동화·target 설정 실패는 WORK_LOG에 보존.
- Release Simulator 빌드 성공. Debug Info.plist의 loopback 도메인 예외를 확인하고 Release Info.plist에는 ATS 예외가 없음을 검사.
- 한계: 실제 Apple 로그인·StoreKit/App Store 결제·APNs·실기기·Unity bridge와 모든 오류/경합 경로는 미검증. 테스트의 local-mock 성공은 외부 Sandbox 성공이 아니다.
