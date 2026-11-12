# CI 검증 범위

`.github/workflows/verify.yml`은 PR과 수동 실행에서 다음 결과를 분리한다. 현재 workflow 수정본의 GitHub Actions 실행은 **NOT_RUN**이며 로컬 정적·음성 시험이 원격 성공을 뜻하지 않는다.

- `inventory-contracts`: 진행 원장·manifest·집계와 fail-closed gate 단위 검사.
- `backend-postgres`: GitHub 호스팅 Linux의 전용 PostgreSQL과 Backend fixture. 테스트 전용 자격값이며 외부 서비스 계정이 아니다.
- `android-native`: GitHub 호스팅 Linux의 Android 단위/fake 검사와 별도 Maven/R8 consumer 빌드.
- `swift-ios-simulator`: GitHub 호스팅 macOS의 Swift 단위/fake 및 합성 iOS host callback 시험. 실제 Apple 로그인·APNs는 아니다.
- `basic-ci`: 위 네 job이 모두 실제 성공해야만 성공한다. 이 결과는 SDK Release 준비 완료가 아니다.
- `unity-e2e`: `workflow_dispatch`에서 repository 변수 `GAMEBRIDGE_UNITY_E2E_ENABLED=true`인 경우에만 전용 `self-hosted, macOS, ARM64, gamebridge-unity-e2e` runner에서 실행한다. PR의 신뢰되지 않은 코드를 self-hosted에서 자동 실행하지 않는다. 활성 Unity 라이선스, 격리 새 AVD, 테스트 DB, 최신 staged SDK와 `GAMEBRIDGE_UPM_STAGING`, `GAMEBRIDGE_ANDROID_SERIAL`, `GAMEBRIDGE_TEST_AVD_NAME`이 필요하다. 선택적으로 `GAMEBRIDGE_UNITY_PACKAGE_CACHE`를 지정한다. Editor smoke, Android/iOS 실제 Player와 동일 실행의 strict-local suite 중 하나라도 실패·미실행이면 성공하지 않는다.
- `release-readiness`: basic-ci와 실제 unity-e2e가 모두 성공하고 모든 필수 회귀 시나리오가 완료되어야 성공한다. Unity job이 skipped이면 `DEFERRED_ENV` 메시지와 비영 종료를 남긴다. GitHub UI의 failed job은 환경 대기와 제품 테스트 실패를 자동으로 구분하지 않으므로 로그를 확인해야 한다.

현재 50개 중 6개 시나리오가 PARTIAL이며 `harness/check-required-coverage.py`는 비영 종료한다. 또한 strict-local의 Unity push lane은 현재 실행 결과 연결이 완성되지 않아 DEFERRED_ENV를 반환한다. 기존 검증을 삭제하거나 과거 증거로 현재 실행을 대체하지 않는다. 실제 계정, 원격 FCM/APNs, 상용 서명이나 외부 인증키는 사용하지 않는다.
