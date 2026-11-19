# P08 실제 Unity export hook 반복 검증

- `artifacts/upm-stable-meta-20261113`의 staged SDK를 격리 소비 프로젝트에 설치했다. Native payload는 f1e12b6 검증 staging과 81개 파일 byte 동일하다.
- Android: `scripts/smoke-unity-android-hook-repeat.sh`, `artifacts/unity-android-mock.mri8OM/hook-markers.log`. Unity 6000.5.8f1의 실제 Android Gradle export에서 자동 post-generate hook 이후 같은 hook을 두 번 더 실행하고 `settings.gradle`, `unityLibrary/build.gradle`과 복사된 Maven 전체 파일 hash가 변하지 않음을 확인했다.
- iOS: `scripts/smoke-unity-ios-hook-repeat.sh`, `artifacts/unity-ios-mock.ztGwKd/hook-markers.log`. 실제 Unity iOS Xcode export 후 postprocess hook을 두 번 더 실행하고 PBX 및 복사된 XCFramework 전체 파일 hash가 변하지 않음을 확인했다.
- 두 시험은 격리 Unity export hook의 반복 실행 검사다. 서명·실기기·실제 스토어는 포함하지 않으며 APK/Simulator Player는 [소비자 설치 증거](consumer-install.md)에서 별도로 확인한다.
- 결과 marker만 보존하며 생성된 Gradle/Xcode export, Native 바이너리 및 원본 로그는 Git에 포함하지 않는다.
