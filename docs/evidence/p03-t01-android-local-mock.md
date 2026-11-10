# P03-T01 Android LOCAL_MOCK 검증 요약

- 시각: 2026-11-10 Asia/Seoul. 소스: 기준 커밋 `ec32a5b` 이후 P03-T01 작업 트리 변경; 이 파일을 포함한 커밋은 Git 이력의 Task ID로 찾는다.
- 환경: 로컬 Android 36 arm64 전용 AVD, Debug APK, Kotlin SDK, 로컬 PostgreSQL 17.6 및 `local-mock` Backend. 외부 계정·실결제는 사용하지 않았다.
- `:sample-app:assembleDebug`: 종료 0. Android native library strip 경고 관측.
- Kotlin JVM opt-in Backend 통합 시험: 종료 0, 테스트 1건, 실패 0, skip 0. 로그인·상품·중복 재요청·서버 잔액·메모리 저장소 복원·로그아웃 확인.
- 전용 AVD: 설치와 Activity 실행, Mock 로그인, 상품 조회, Mock coins 구매, 서버 잔액 900→1000 및 `GRANTED / PENDING` 확인. 앱 재시작 후 Keystore 세션 복원과 동일 잔액 조회, 로그아웃 후 SDK session preference 제거 확인. 개발키·토큰 원문은 기록하지 않았다.
- 한계: 실제 Play/Google 인증·결제·finalization, Unity transport, 실기기, 전체 오류·복구·보안 검증은 미실행. 자동화 입력을 화면 준비 전에 시도해 실패한 사례와 재시도는 WORK_LOG에 남겼다.
