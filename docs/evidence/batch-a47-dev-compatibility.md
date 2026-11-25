# Batch A 개발자용 패키징과 호환성

비교 기준은 PR #10·#11 병합이 끝난 main `3d9d5b8e6e906c78affd4d53444c544b762afe30`에서 새로 빌드한 `0.1.0-dev`다. 후보는 해당 소스에서 SDK 버전을 `0.1.1-dev`로 올린 개발자용 패키지다. Bridge Protocol은 v1이다. `VERSION`이 Maven과 패키징 버전의 기준이며, Unity Android Export는 설치된 UPM의 버전으로 Maven 좌표를 선택한다. Swift·Kotlin·C#의 버전 표기는 기존 소스 전이 검사로 대조한다. Apple 프레임워크 번들의 숫자 버전은 `0.1.1`, SDK 버전 메타데이터는 `0.1.1-dev`다.

| 검증 | 결과 |
| --- | --- |
| C# | 기존 LegacyConsumer가 후보 소스로 빌드되어 실행됨 |
| Android JVM | `SdkCoordinator`, `BridgeProtocol`, `BridgeFacade`, `GoogleAuthProvider`의 javap public 서명과 JVM descriptor 일치. 모든 Kotlin 메타데이터 비교는 범위 밖 |
| iOS C ABI | device arm64, Simulator arm64/x86_64에서 모든 GB 공개 심볼 5개 일치 |
| Android 소비 | 두 Maven 버전으로 독립 Release R8 소비자 빌드 성공. 후보 Unity Android Export 반복 훅 성공. 새 Android Player 실행은 미실행 |
| 패키지 교체 | 동일 bundle ID의 Unity iOS 18.6 Simulator 앱에서 이전 SDK가 이번 로컬 Backend에 연결하고 구매 응답 유실을 재현. 앱과 DB를 지우지 않고 후보 앱을 덮어 설치한 뒤 세션 복원과 미완료 구매 복구 성공. 원장은 1건, 순증 100코인으로 유지 |
| 음성 | 빠진 Android/iOS 산출물, 혼합 SDK 버전, 기존 출력 경로를 패키징에서 거부. 후보 Maven의 복제본에서 전이 core JAR 제거 후 독립 소비자 빌드가 실패하는지 확인 |
| 회귀 | Swift 버전·Bridge·복구·갱신 9개, Android Gradle 훅, iOS PBX/URL 검사 157개 및 계약·전이 가드 통과 |

로컬 교체 시험에서는 LOCAL_MOCK 세션과 모의 구매를 사용했다. 기존 StoreKit 26.5 실패, Strict 및 외부 Provider 미검증 기록이 계속 적용된다. 사용한 환경은 Xcode 26.6, iOS 18.6 Simulator, Unity 6000.5.8f1, JDK 21 및 Android SDK 36이다. 로컬에는 iOS 26.5 Simulator, Android API 26/30/31/33/34/36 이미지, Unity 6000.4.0f1도 설치되어 있다.

배포용 후보 묶음에는 프로젝트 산출물인 Maven 3개 모듈, GameBridgeNative XCFramework, UPM 패키지를 넣는다. UPM/SwiftPM/Maven이 해석하는 외부 SDK는 소비 시 원래 공급처에서 받는다. AAR에 추가 vendor JAR이 없음을 확인했고, 보관용 ZIP/TGZ에는 완성 Player나 외부 프레임워크를 넣지 않는다. 후보에서 서명 키, 개인키 패턴, 로컬 OAuth 설정과 계정 파일을 점검했다. 외부 의존성 조건은 원 배포처를 따른다. 프로젝트에 저장소 전체 라이선스 파일이 없어 공개 재배포 권리 판단은 공개 전에 별도로 확인해야 한다. [GoogleSignIn 라이선스](https://github.com/google/GoogleSignIn-iOS/blob/9.2.0/LICENSE) · [Meta 라이선스](https://github.com/facebook/facebook-ios-sdk/blob/v18.1.1/LICENSE)

재현은 `scripts/build-android.sh --mock`, `scripts/build-ios.sh --xcframework`, `scripts/package-sdk.sh`를 각 소스에 적용한 뒤 기존 `harness/run-unity-ios-mock-restart-e2e.py --previous-app`에 비교 앱과 후보 staging을 전달한다. 비교 앱은 기존 `tests/UnityIosRestartConsumer` 시나리오를 사용해 만든다. 아카이브의 source manifest에 소스 커밋과 내용 체크섬을 기록한다.
