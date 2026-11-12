# CI 검증 범위

`.github/workflows/verify.yml`은 PR과 수동 실행에서 다음 결과를 분리한다. 현재 workflow 수정본의 GitHub Actions 실행은 **NOT_RUN**이며 로컬 정적·음성 시험이 원격 성공을 뜻하지 않는다.

- `inventory-contracts`: 진행 원장·manifest·집계와 fail-closed gate 단위 검사.
- `backend-postgres`: GitHub 호스팅 Linux의 전용 PostgreSQL과 Backend fixture. 테스트 전용 자격값이며 외부 서비스 계정이 아니다.
- `android-native`: GitHub 호스팅 Linux의 Android 단위/fake 검사와 별도 Maven/R8 consumer 빌드.
- `swift-ios-simulator`: GitHub 호스팅 macOS의 Swift 단위/fake 및 합성 iOS host callback 시험. 실제 Apple 로그인·APNs는 아니다.
- `basic-ci`: 위 네 job이 모두 실제 성공해야만 성공한다. 이 결과는 SDK Release 준비 완료가 아니다.
- `unity-e2e`: `workflow_dispatch`에서 repository 변수 `GAMEBRIDGE_UNITY_E2E_ENABLED=true`인 경우에만 전용 `self-hosted, macOS, ARM64, gamebridge-unity-e2e` runner에서 실행한다. PR의 신뢰되지 않은 코드를 self-hosted에서 자동 실행하지 않는다. 활성 Unity 라이선스, 격리 새 AVD, 테스트 DB, 최신 staged SDK, 설치된 Editor 실행 파일 `UNITY_EDITOR_PATH`와 `GAMEBRIDGE_UPM_STAGING`, `GAMEBRIDGE_ANDROID_SERIAL`, `GAMEBRIDGE_TEST_AVD_NAME`, 별도 Push 전용 `GAMEBRIDGE_PUSH_ANDROID_SERIAL`, `GAMEBRIDGE_PUSH_TEST_AVD_NAME`이 필요하다. 두 AVD 이름은 `GameBridge_V2_`로 시작하고 서로 다른 기기여야 한다. `GAMEBRIDGE_UNITY_PACKAGE_CACHE`는 정확한 버전의 격리 테스트용 package cache 경로로 필수다. Editor smoke, Offline/Native sample Editor 검사, Android/iOS 실제 Player와 동일 실행의 strict-local suite 중 하나라도 실패·미실행이면 성공하지 않는다. strict 실행은 지정한 `UNITY_EDITOR_PATH`와 같은 staging 안의 Maven/XCFramework를 사용한다. strict orchestration은 `gamebridge-sdk-local-postgres-1` 컨테이너에 새 전용 DB/role을 만들고 테스트 서버를 실행한 뒤 보존하므로 전용 로컬 PostgreSQL과 Docker가 필요하다.
- `release-readiness`: basic-ci와 실제 unity-e2e가 모두 성공하고 모든 필수 회귀 시나리오가 완료되어야 성공한다. Unity job이 skipped이면 `DEFERRED_ENV` 메시지와 비영 종료를 남긴다. GitHub UI의 failed job은 환경 대기와 제품 테스트 실패를 자동으로 구분하지 않으므로 로그를 확인해야 한다.

현재 50개 중 2개 시나리오가 PARTIAL이며 `harness/check-required-coverage.py`는 비영 종료한다. strict-local의 Unity push lane은 명시적인 `GAMEBRIDGE_RUN_UNITY_PUSH_E2E=true`와 전용 환경이 있을 때 두 Player를 새로 실행하고 현재 HEAD·clean 상태·필수 marker를 확인한다. opt-in이나 환경이 없으면 DEFERRED_ENV다. 로컬 전체 gate에서 소스 `e703f43`의 Android/iOS 기본 및 Push LOCAL_MOCK Player, Unity Editor가 각각 PASS했으나 부분 시나리오와 기존 P05-T03 실패로 전체 gate는 FAIL이다 ([증거](evidence/p09-unity-ci-local.md)). Android 최초 전체화면 안내는 수동으로 닫았으며 GitHub Actions 및 실제 원격 푸시는 여전히 NOT_RUN이다. 기존 검증을 삭제하거나 과거 증거로 현재 실행을 대체하지 않는다. 실제 계정, 원격 FCM/APNs, 상용 서명이나 외부 인증키는 사용하지 않는다.

현재 로컬 UPM staging은 `artifacts/upm-stable-meta-20261113`이다. `upm-native-sample-fix-20261112`에는 안정적 asset metadata 추가가 없다. 이전 `upm-offline-sample-current-20261112`에는 iOS Native Demo asmdef 수정이 없다. 이전 `upm-offline-sample-20261112` 후보는 Native payload가 달라 최신 staging으로 사용하지 않는다. 로컬 산출물은 원격 checkout에 자동으로 존재하지 않는다.
