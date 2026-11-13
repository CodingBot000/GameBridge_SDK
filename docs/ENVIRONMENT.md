# 실행 환경

2026-11-10 조사: Java, Xcode, Swift, adb, Android SDK, Docker 엔진 및 Compose가 명령 실행에 응답했다. Unity Editor 두 버전은 설치 경로만 확인했다. 라이선스, Android/iOS 모듈, 실기기, 서명과 실제 앱 빌드는 확인하지 않았다. 시스템 Gradle은 없으며 프로젝트별 wrapper가 필요하다. 전체 조합의 빌드 및 플랫폼 검증은 아직 실행하지 않았다.

## 2026-11-13 재확인

- Unity 6000.5.8f1의 라이선스 활성, Android/iOS 모듈 및 Editor·Android emulator/iOS Simulator LOCAL_MOCK 실행을 확인했다. Unity 6.3 LTS는 설치·검증하지 않았고 ENV-001에 남는다.
- Android Maven의 unsigned R8 독립 소비 빌드와 iOS 무서명 XCFramework device/simulator slice·별도 Simulator 링크를 확인했다. 서명된 실기기 실행과 실제 스토어 검증은 아니다.
- iOS 18.6 local StoreKit 복구는 통과했으나 iOS 26.5에서는 test-only SKTestSession 생성이 timeout으로 실패했다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN을 유지한다.
- 실제 Google/Apple 인증·스토어·FCM/APNs와 실기기는 사용자 설정 후 별도 검증이다. GitHub Actions는 실행하지 않았다. 세부 버전·명령은 [TOOLCHAIN](TOOLCHAIN.md), 테스트 근거는 [PROGRESS](PROGRESS.md)와 [WORK_LOG](WORK_LOG.md)를 따른다.
