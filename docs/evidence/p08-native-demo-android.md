# P08 Native Demo Android LOCAL_MOCK Player

- 소스 `68a315f14bb17e84beb469e91435244f17c6c7f7`, tracked-clean, Unity 6000.5.8f1 Android 개발 Player와 전용 Android 36 AVD. SDK staging은 `artifacts/upm-offline-sample-current-20261112`다.
- staged `Native Demo` sample과 uGUI 2.5.0을 새 프로젝트에 복사했다. test-only probe가 runtime 설정을 입력하고 실제 sample의 초기화·로그인·상품 조회·100코인 mock 구매·로그아웃 버튼 callback을 호출했다.
- `artifacts/unity-android-e2e-j7ir0wt8/result.json`: Player PASS, 격리 LOCAL_MOCK Backend/PostgreSQL 지급 원장 1건·100코인, 개발키 입력 필드 삭제와 합성 개발키 결과 비노출 확인.
- 최초 전체화면 안내는 수동으로 닫았고 AVD는 실행 후 shutdown만 했다. Package Manager UI import, 화면 포인터·렌더링, iOS Native Demo Player, 실제 Play 거래·인증 및 실기기 검증은 아니다. 원본 로그·APK·키·DB는 커밋하지 않는다.
