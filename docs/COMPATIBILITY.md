# 호환성 확인 범위 — 개발 중

| 대상 | 확인한 범위 | 미확인 |
|---|---|---|
| Android | Kotlin/JDK 21·JVM 17, API 36 빌드; 새 local Maven 및 소스 없는 R8 release consumer compile | 실제 Google/Play/FCM과 Unity Android Player |
| iOS | Xcode 26.6의 iOS device arm64 및 simulator arm64/x86_64 무서명 static XCFramework, C ABI symbol, 별도 Swift simulator consumer link | 서명된 실기기, 실제 Apple/StoreKit/APNs 및 Unity iOS Player |
| Unity | 설치된 6000.5.8f1 managed reference 기준 C# 조건부·uGUI/Notifications compile; P08 C# consumer source fixture | Editor license ENV-002, 실제 import/export, IL2CPP, scene·device |
| Backend | JDK 21/Spring Boot 3.5.16, 격리 PostgreSQL 17 계열의 synthetic/local DB 시험 | 운영 환경·외부 store 인증·다중 서버 운영 |

P08 source snapshot 비교와 C# consumer compile은 binary ABI 안정성이나 위 버전 외 조합의 호환성 보증이 아니다. 현재 전체 local gate는 미구현·환경 대기와 기록된 StoreKit 실패로 통과하지 않는다.
