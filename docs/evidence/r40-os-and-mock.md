# R40 실제 OS 및 Mock 알림 권한 거부 회귀

- `GAMEBRIDGE_RUN_OS_PERMISSION_E2E=true ... python3 harness/run-r40-permission-optin.py`를 소스 `ef9405b6e688e0b424f1294363ff8d0fdc8c3fbb`에서 실행해 세 경로가 각각 PASS했다. 양 OS Player 결과는 tracked-clean이다.
- Android: `artifacts/unity-android-permission-ube13ah7`. Android 36 전용 AVD의 실제 OS 알림 창을 명시적인 denial resource ID로 자동 두 번 선택해 첫 DENIED, 등록 `PERMISSION_DENIED`, 재요청 DENIED를 확인했다. test-only Firebase Messaging dependency만 사용했으며 Firebase 프로젝트·계정·원격 발송은 없다.
- iOS: `artifacts/unity-ios-permission-hk912uou`. iOS 18.6 Simulator의 실제 OS 알림 창에서 도구로 **허용 안 함**을 선택해 첫 DENIED, 등록 `PERMISSION_DENIED`, 재요청 DENIED를 확인했다. 이 GUI 선택은 외부 도구 조작이며 무인 CI 통과가 아니다. GUI 입력이 없으면 runner는 환경 대기로 끝난다.
- Mock: `scripts/smoke-unity-mock-permission.sh`는 synthetic DENIED 주입 후 실제 EditorOffline 등록의 `PERMISSION_DENIED`와 재요청 DENIED를 standalone managed test에서 확인했다. 실제 OS 시험과 합산하지 않는다.
- 초반 Android 자동 runner의 버튼 ID 미일치에 따른 INTERRUPTED와 그 이전 Firebase dependency 부재 실패는 [Android 부분 이력](r40-android-os-permission-partial.md)에 보존한다. [iOS 부분 이력](r40-ios-os-permission-partial.md)도 별도다.
- 재현에는 빈 전용 Android AVD, staged SDK/cache 및 iOS Simulator GUI denial 처리가 필요하다. 실제 FCM/APNs, 실제 계정과 실기기는 검증하지 않았다. 원본 로그·빌드·키는 Git에 포함하지 않는다.
