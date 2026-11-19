# P08 Native Demo iOS LOCAL_MOCK Simulator Player

- 소스 `083100fe117b856bc4ce198941dcee19ce09d488`, tracked-clean, Unity 6000.5.8f1 iOS 18.6 Simulator ARM64 Player, 로컬 ad-hoc Simulator 서명. SDK staging은 `artifacts/upm-native-sample-fix-20261112`다.
- 새 프로젝트에서 Unity Package Manager Sample API로 staged Offline/Native sample을 import하고 uGUI 2.5.0을 구성했다. test-only probe가 runtime 설정을 입력하고 sample의 초기화·로그인·상품 조회·100코인 mock 구매·로그아웃 버튼 callback을 호출했다.
- `artifacts/unity-ios-e2e-7ryle35b/result.json`: Player PASS, main-thread, 격리 LOCAL_MOCK Backend/PostgreSQL 지급 원장 1건·100코인, 개발키 입력 필드 삭제 및 합성 개발키 결과 비노출 확인.
- 첫 시도 `artifacts/unity-ios-e2e-kd8mlvys`는 sample iOS asmdef의 `GameBridge.Runtime` 직접 참조 누락으로 Unity export CS0246 FAIL, Player NOT_RUN이었다. 참조 수정 및 새 staging 후 위 결과로 재검증했다.
- 실행 후 Simulator는 shutdown만 했다. Package Manager GUI 클릭, 실제 포인터·렌더링, Apple 로그인·스토어 거래·APNs 및 실기기 검증은 아니다. 원본 로그·키·DB·빌드는 커밋하지 않는다.
