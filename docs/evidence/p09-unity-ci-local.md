# P09 Unity CI gate 로컬 검증

- 소스 `e703f43c646331ac4979ca2ff52811df85bc141a`, staging `artifacts/upm-native-sample-fix-20261112`. 네 Player 결과 모두 해당 HEAD 및 tracked-clean이다. strict 전체의 `sourceDirty: true`는 보존 중인 기존 미추적 Demo/캐시가 포함된 `git status` 기준이다.
- `scripts/ci-unity-e2e.sh`를 활성 Unity Editor, 전용 baseline/push AVD 2개, 격리 PostgreSQL DB 및 iOS Simulator에서 실행했다. Editor 소비자 2건과 staged sample Editor 1건, Android/iOS 기본 LOCAL_MOCK Player와 Android/iOS Push LOCAL_MOCK Player가 각각 PASS했다.
- strict `artifacts/verify-all-4r3l36i6/summary.md`: `unity-editor-runtime` PASS 2건, `push/unity-player-notifications` PASS 2건. 전체는 R22/R40 시나리오 PARTIAL과 기록된 P05-T03 FAIL 때문에 **FAIL / exit 1**이다. 외부 제공자 13개는 WAITING_USER다.
- 기본 Player: `artifacts/unity-android-e2e-jnmyjg_y`, `artifacts/unity-ios-e2e-h0qfk2lx`; Push Player: `artifacts/unity-android-push-_yyei7g7`, `artifacts/unity-ios-push-jmoaub1q`. 두 Android AVD의 최초 전체화면 안내는 수동으로 닫았다.
- 첫 gate 시도는 Unity ADB 재시작 직후 초기 기기 조회로 DEFERRED_ENV였다. 재검색 대기 수정 후 앱이 설치되지 않은 동일 전용 AVD를 재사용해 위 결과를 얻었다.
- 실행 후 이 시험의 AVD 2개와 Simulator 3개는 shutdown만 했고 데이터는 보존했다. GitHub Actions, 실제 Google/Apple 인증·스토어·FCM/APNs, 실기기 및 완전 무인 CI 실행은 검증하지 않았다. 원본 로그·키·DB·빌드는 커밋하지 않는다.
