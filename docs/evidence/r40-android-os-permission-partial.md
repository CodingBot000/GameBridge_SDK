# R40 Android OS 알림 권한 거부 — 부분 검증

- Unity 6000.5.8f1 Android IL2CPP 개발 Player, 전용 Android 36 ARM64 emulator. 테스트 시 source `1fa6c0d` 및 당시 미커밋 test-only `tests/UnityAndroidPermissionConsumer` 소스를 사용했다. 검증 코드는 후속 로컬 커밋에 포함된다.
- test-only Firebase Messaging 26.0.1 의존성을 제공했으나 Firebase 프로젝트·계정·자격증명·원격 전송은 사용하지 않았다. 실제 OS 알림 dialog를 두 번 수동 거부했다.
- Unity SDK의 첫 권한 요청은 DENIED, 등록 요청은 PERMISSION_DENIED로 차단, 두 번째 요청은 DENIED였다. `GB_PERMISSION_RESULT PASS ANDROID_OS_DENIED`를 확인했다. 로컬 마커: `artifacts/r40-android-os-denial-20261112/markers.log`.
- 테스트 APK SHA-256 `b5bf927fade13886332199d87bd2990ae142bfd29d415cc3dcc88f0af7e53dcf`. APK·원본 로그·AVD는 Git에 포함하지 않는다. 전용 AVD의 최초 전체화면 안내 및 권한 dialog는 수동으로 조작했다.
- 선행 두 번의 시도는 Firebase runtime dependency가 없어 등록 단계가 CONFIG_REQUIRED였으므로 권한별 차단 PASS가 아니었다.
- **R40 전체 상태 PARTIAL:** 이 Android 시험 당시 iOS OS 및 Mock 거부는 미검증이었다. 이후 [iOS Simulator 부분 검증](r40-ios-os-permission-partial.md)과 독립 managed Mock 거부 시험을 확인했다. OS 시험의 무인 재현 및 전체 시나리오 집계는 남았다. 실제 FCM/APNs 원격 전달이나 실기기 검증을 뜻하지 않는다.
