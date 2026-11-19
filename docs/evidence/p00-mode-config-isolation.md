# P00-T05 모드·설정·비밀정보 격리 검증

- `config/gamebridge.example.json`과 각 플랫폼 설정은 EDITOR_OFFLINE/LOCAL_MOCK/XCODE_STOREKIT/PLATFORM_SANDBOX를 명시적으로 구분한다. Backend `EnvironmentPolicyTest`는 profile 누락·혼합을 거부한다. 실제 sandbox에서 개발 인증 endpoint 비활성과 synthetic mock identity 거부는 기존 격리 HTTP/DB 회귀에서 확인했다.
- 개발키·Google credential 관련 환경 변수를 제거한 Backend bootJar 및 Android mock publication/R8 consumer build가 성공했다 (`artifacts/config-diagnostic-backend-build.log`, `artifacts/config-diagnostic-android-build.log`). 서버 실기동이나 실제 provider 인증이 아니다.
- Android Google client ID 누락은 Native `CONFIG_REQUIRED` 및 `googleServerClientId` key 이름으로 반환하고 gateway/challenge 전에 중단한다. Unity Android/iOS sandbox capability는 빠진 설정 key 이름만 표시한다. Android provider fake 15건·bridge fake 5건, Swift Apple bridge fake 3건, Kotlin/Swift config 각 2건 및 C# managed facade 검사 PASS/skip0.
- 실제 Unity sandbox 설정 경계: Android `artifacts/unity-sandbox-config-android-yklqwymu` (source `3d30cc1`)와 iOS `artifacts/unity-sandbox-config-ios-c9m2245o` (source `8d2da0e`)는 각각 tracked-clean PASS. 누락 key capability와 `CONFIG_REQUIRED`/no-fallback을 확인했으며 `example.invalid`만 사용했다. Android 최초 전체화면 안내는 수동으로 닫았다. 실제 Google/Apple 계정·스토어·실서버는 호출하지 않았다.
- `.env` 변형, Unity `.ulf`, 서명 파일과 APK/AAB/IPA의 synthetic 파일명 ignore 시험 2건 PASS; `.env.example`은 추적 가능하다. 실제 비밀 파일의 내용을 읽지 않았다. scoped 변경 diff의 흔한 credential 패턴은 발견되지 않았으며 이는 전체 저장소 또는 모든 비밀 형식의 보증이 아니다.
- 실제 provider 자격·entitlement·원격 sandbox 및 실기기 검증은 USER_SETUP의 별도 WAITING_USER다. 로컬 설정 분리 PASS가 실제 제공자 동작 PASS를 뜻하지 않는다.
