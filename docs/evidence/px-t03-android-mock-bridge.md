# PX-T03 Android Kotlin bridge LOCAL_MOCK 대조 시험

- source: `e770e63` + 당시 미커밋 instrumentation test 및 runner. 결과: `artifacts/android-mock-bridge-e2e-e7bbf_tp/result.json`, 1 test PASS, skip 0.
- 환경: 새 Android 36 ARM64 전용 에뮬레이터, 전용 local-mock PostgreSQL DB, 임시 synthetic 개발키. 기존 AVD·DB는 수정하지 않았다.
- 경로: Android instrumentation → Kotlin `BridgeFacade` → SDK → 격리 local Backend/DB. 초기화, Mock 로그인, 상품 조회, Mock 구매, 서버 잔액 +100, 로그아웃을 확인했다. DB 원장은 1건, 합계 100이다.
- Native callback 로그: `artifacts/android-mock-bridge-e2e-e7bbf_tp/native-requests.log`. 서버 HTTP request ID·상태: 같은 디렉터리 `server.log`의 `LOCAL_MOCK_TRACE`. 두 종류의 ID는 각각 생성되므로 동일한 ID라고 주장하지 않는다.
- 한계: Unity Editor, AndroidJavaProxy/JNI 및 Unity Player는 실행되지 않았다. Google 로그인과 실제 스토어 결제가 아니다.


## 후속 검수 주석

기존 기록의 출발점은 e770e63 및 당시 미커밋 테스트/Runner 변경으로, 깨끗한 checkout의 동일 소스 재현은 아니다. 해당 기록의 1건 PASS를 새 변경 브랜치나 Unity Android Player 검증의 성공으로 이전하지 않는다. 후속 PX-T05 Runner는 설정 경로를 가변화했으나 실제 재실행은 NOT_RUN이며, 새 clean-checkout 결과가 통과했을 때만 PX-T06 Exporter로 별도의 공개 증거를 만든다.
