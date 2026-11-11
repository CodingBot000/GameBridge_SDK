# PX-T03 Android Kotlin bridge LOCAL_MOCK 대조 시험

- source: `e770e63` + 당시 미커밋 instrumentation test 및 runner. 결과: `artifacts/android-mock-bridge-e2e-e7bbf_tp/result.json`, 1 test PASS, skip 0.
- 환경: 새 Android 36 ARM64 전용 에뮬레이터, 전용 local-mock PostgreSQL DB, 임시 synthetic 개발키. 기존 AVD·DB는 수정하지 않았다.
- 경로: Android instrumentation → Kotlin `BridgeFacade` → SDK → 격리 local Backend/DB. 초기화, Mock 로그인, 상품 조회, Mock 구매, 서버 잔액 +100, 로그아웃을 확인했다. DB 원장은 1건, 합계 100이다.
- Native callback 로그: `artifacts/android-mock-bridge-e2e-e7bbf_tp/native-requests.log`. 서버 HTTP request ID·상태: 같은 디렉터리 `server.log`의 `LOCAL_MOCK_TRACE`. 두 종류의 ID는 각각 생성되므로 동일한 ID라고 주장하지 않는다.
- 한계: Unity Editor, AndroidJavaProxy/JNI 및 Unity Player는 실행되지 않았다. Google 로그인과 실제 스토어 결제가 아니다.
