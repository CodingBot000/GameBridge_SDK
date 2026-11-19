# P08-T01 Android Maven 독립 소비 검증

- 소스 `fd4102f`의 Android Native 제품 경로를 사용해 `artifacts/maven-p08-reverify-20261113`에 새 publication을 만들었다. 당시 문서 및 test-only 독립 소비자 변경은 미커밋이었다. f1e12b6 이후 Android Native 제품 파일 차이는 없다.
- publication은 `sdk-android` 및 `sdk-unity-bridge` AAR, 순수 JVM `sdk-core` JAR과 각 POM/Gradle module metadata로 구성된다. sdk-android POM의 sdk-core 및 인증·Billing runtime 전이 의존성을 확인했다. 세 모듈 모두 AAR이라고 주장하지 않는다.
- `scripts/build-android.sh --mock` exit 0; 별도 `scripts/smoke-android-maven-consumer.sh`는 기존 build/.gradle을 복사하지 않은 새 소비 프로젝트에서 Maven 좌표만으로 R8 minify된 unsigned release APK 및 mapping을 생성했다 (`artifacts/android-maven-consumer.cNk7BG`). source project dependency는 사용하지 않았다.
- APK merged manifest의 BILLING/INTERNET 권한 및 consumer activity를 확인했다. Android SDK XML 버전 경고가 있었지만 build는 성공했다. unsigned APK의 실제 기기 실행, Firebase/Google 실제 인증·원격 서비스 검증은 이 시험에 포함되지 않는다.
- SHA-256: sdk-core JAR `258b9cc960231a094ac51eca52829bd401dc2dc257c98fbee5687d028a367085`; sdk-android AAR `c7190cc584de5d35dbfd79d4b533ceb085b0f9beaa2ac1299939db3160338073`; sdk-unity-bridge AAR `2e913bc11bc6a34395c5d242565f241761383d6663a2362fa87e379b9744bda8`. 산출물과 원본 로그는 Git에 포함하지 않는다.

## 2026-11-13 설정 진단 변경 후 재검증

- Android 제품 변경은 `fb48371`에 포함됐다. 빌드 당시 그 제품 변경은 미커밋이었고 이후 현재 Android 제품 경로는 동일하다. `artifacts/maven-config-diagnostic-20261113`을 개발키·Google credential 환경 변수 없이 새로 publish했다.
- `artifacts/android-maven-consumer.IjHXTq`의 새 격리 프로젝트에서 Maven 좌표만으로 unsigned R8 release APK·mapping 및 merged manifest를 확인했다. 실제 기기/Google 인증은 별도다.
- SHA-256: core JAR `c8c4700c000d49e5f7b0f53d1ff24b1fd8fcb9298cb9b5e520e46be223625d8f`; Android AAR `2c20a17c3f22305b52469e017f4fe28da2a5751da0ec050b7923892d3768c8db`; Unity bridge AAR `2acbbc013316a6363b89cd1c0412461fb313c5d4ae2aef54587a7e61dd777860`. SDK XML 버전 경고가 있었다.
