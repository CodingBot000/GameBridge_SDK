# Android 및 iOS 패키지 음성 검증

2026-11-11 `artifacts/android-dependency-negative-2v90vblk`에서 새 소비 프로젝트와 별도 Maven 사본의 정상 R8 release build가 성공했다. 그 사본에서만 전이 의존성 `sdk-core` JAR을 삭제하자 Gradle offline 재빌드가 해당 파일 누락 오류로 실패했다. 실제 source Maven 저장소는 수정하지 않았다.

`artifacts/ios-xcframework-negative-os4u5n1z`에서는 실제 로컬 XCFramework의 device arm64·simulator arm64/x86_64와 각 architecture의 C ABI symbol 네 개를 먼저 확인했다. 새 복사본에서 simulator binary를 제거한 경우와 device binary를 일부 symbol만 포함한 테스트 archive로 대체한 경우 모두 `scripts/verify-xcframework.py`가 staging 전에 거부했다. 원본 XCFramework는 변경하지 않았다.

이 시험은 로컬 소비 build와 정적 산출물 검사이며 Unity Editor import/export나 서명된 기기 실행을 뜻하지 않는다.
