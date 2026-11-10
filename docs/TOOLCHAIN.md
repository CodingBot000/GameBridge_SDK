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

Unity 6000.5.8f1에 포함된 .NET SDK 8.0.318로 Unity managed assembly 대상 C# 독립 컴파일을 수행할 수 있다. 이는 Unity Editor import나 IL2CPP 검증이 아니다. 첫 실행 시 .NET이 개발용 HTTPS 인증서를 자동 설치했다고 출력했으며 신뢰 명령은 실행하지 않았다. 이후 검사에서 인증서 생성을 비활성화한다.

Unity JSON 후보 `com.unity.nuget.newtonsoft-json` 3.2.2는 Unity 공식 registry metadata와 패키지 DLL로 독립 .NET 컴파일·smoke를 확인했다. Unity Editor import 및 IL2CPP 호환성은 미검증이다. 출처: https://packages.unity.com/com.unity.nuget.newtonsoft-json

Android Google adapter: androidx.credentials 및 credentials-play-services-auth 1.6.0, googleid 1.1.1. googleid 1.2.1은 Kotlin metadata 2.4로 기존 Kotlin 2.1.20과 빌드 실패하여 제외했다. 출처: Google Maven metadata 및 https://developer.android.com/identity/sign-in/credential-manager-siwg-implementation.

Google Play Billing candidate: `com.android.billingclient:billing:9.1.0`. Google Maven metadata와 공식 9.1.0 release notes를 확인했고 Android AAR 및 Mock sample 빌드, fake boundary 시험을 수행했다. 실제 Play Console·기기 테스트는 미실행이다. 출처: https://developer.android.com/google/play/billing/release-notes 및 https://developer.android.com/google/play/billing/deprecation-faq.
