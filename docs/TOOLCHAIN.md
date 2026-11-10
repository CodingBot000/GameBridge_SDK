# 도구와 호환성

확인일 2026-11-10. 아래 버전은 설치 또는 공식 호환성 확인 결과이며 전체 조합의 빌드 통과를 뜻하지 않는다.

| 도구 | 확인 결과 | 확인 방법 |
|---|---|---|
| JDK | OpenJDK 21.0.10 | `java -version` |
| Xcode | 26.6 (17F113) | `xcodebuild -version` |
| Swift | 6.3.3 | `swift --version` |
| Android | adb 37.0.1; 플랫폼 34–36 및 37.0, build-tools 34–36 | `adb version`, SDK 디렉터리 목록 |
| Docker | client/server 29.1.3, Compose 2.40.3 | `docker version`, `docker compose version` |
| Unity | 6000.4.0f1, 6000.5.8f1 설치; 라이선스와 모듈 미검증 | Editor 디렉터리 목록 |
| Gradle | 시스템 명령 없음; wrapper 필요 | `gradle --version` 조회 |

후보: Android AGP 8.13.0 및 Gradle 8.13, Android API 36; backend Spring Boot 3.5.16 및 JDK 21. 이는 공식 문서상 호환 후보이며 함께 빌드되기 전에는 확정 조합이 아니다. Kotlin과 PostgreSQL 패치, Unity 버전은 실제 빌드 시 확정한다. 설치된 Unity는 공식 문서상 6.3 LTS가 아니므로 LTS 부재를 기록하고 설치된 버전의 호환성을 확인한다.

출처: [Android AGP 호환성](https://developer.android.com/build/releases/agp-8-13-0-release-notes), [Spring Boot 시스템 요구사항](https://docs.spring.io/spring-boot/3.5/system-requirements.html), [Unity 지원 정책](https://unity.com/releases/unity-6/support).

Android AGP 8.13.0 / Gradle 8.13 / Kotlin 2.1.20 / API 36 / JDK 21 최소 Compose 앱 빌드 성공 (2026-11-10); 기기 실행 및 Unity export 미검증. Backend Spring Boot 3.5.16 / Kotlin 2.1.20 / Gradle 8.13 / JDK 21 최소 빌드 성공.
