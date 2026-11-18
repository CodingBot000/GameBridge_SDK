# 호환성 확인 범위 — 개발 중

배치34의 최신 검증·제약은 [통합 증거](evidence/p10-batch34-integrated.md)를 따른다. 실제24 HTTP operation의 성공 응답 구조, DTO23개, 새 양플랫폼 Unity LOCAL_MOCK 소비와 선정 JVM API를 확인했다. C ABI 시간은 측정했지만 Task/continuation·Android heap·Unity Scene/Frame 및 전체 Strict는 미완료이며 DEV_RC를 유지한다.


현재 기준은 [배치32 source/산출물별 기록](evidence/p10-batch32-integrated.md)이다. 빌드·실행·소스 검사·기존 증거의 source 동일성을 구분한다. 다음 표는 모든 버전·ABI·실기기 지원 보증이 아니다.

| 대상 | 확인한 범위 | 미확인·한계 |
| --- | --- | --- |
| Android | JDK21.0.10/JVM17·compile/target API36·min26, 새 Maven/AAR/sample 및 소스 없는 R8 release 소비 빌드. Unity6000.5.8f1 현재 Core의 GUI APK/새 emulator LOCAL_MOCK Push·JNI/구매PII 근거 | 실제 Google/Play/FCM·실기기 미검증. Native T02 변경 뒤 새 package CLI 구매PII는 PASS, 별도 GUI 시각검증은 Mac잠금으로 미실행 |
| iOS | Xcode26.6(17F113)/Swift6.3.3, device arm64·simulator arm64/x86_64 무서명 static XCFramework/4 Cexports·새 Swift source 소비와 simulatorSDK binary module typecheck. 현재 Core의 Unity Simulator Push/Lifecycle 및 독립CABI/기존구매PII 근거 | 실제 Apple/StoreKit/APNs·서명 실기기 미검증. iOS Push 망차단은 로컬 TCP proxy 범위이며 OS전체차단이 아님. post-T02 새 package CLI 구매PII PASS, 별도 GUI 시각검증 미실행 |
| Unity | 6000.5.8f1 실제 GUI C# 메뉴 컴파일·원본 Android/iOS Builder와 source/nonce/147SDK/hash/receipt 검사·새 LOCAL_MOCK Player 실행 | 다른 설치버전6000.4/미설치6.3지원 미검증. 자동 batch Editor direct/cli 정상과 새CLI Builder는확인. 전체Strict·self-hosted/Release는미검증. Native memory/UI jank/startup 프로파일링 NOT_RUN |
| Backend | JDK21/Spring Boot3.5.16, 격리PostgreSQL17 계열·synthetic/LOCAL_MOCK 원장/소유권/멱등·loopback 실측 | 운영·외부store인증·다중서버 미검증. 실제 검증 수/expected mutation은 개별 증거로 구분 |

P08 public API snapshot, 닫힌 Core source, 정확히 승인된 Native4파일 전이 검사는 별도 경계다. [원본 Core 제품 판정](evidence/p10-batch32-t01-decision.md) 후의 Native 변경은 원본 baseline을 덮어쓰지 않고 고정된 전후hash·나머지Core/Native/wire 불변으로 검사한다. 선정 Java 표면/C ABI·소비 빌드를 모든 binary ABI 호환성으로 확대하지 않는다.

P05-T03 StoreKit26.5 FAIL/ENV-STOREKIT-26 OPEN, 18.6 간헐 위험, Provider13 WAITING_USER와 기존 내부/문서 gap을 유지한다. 전체 SDK와 local/Release gate를 통과한 것으로 표시하지 않는다. 생성된 artifact/source/checksum은 [진행 원장](PROGRESS.md), [사용자 설정](USER_SETUP.md) 및 최신 source별 증거를 따른다.


배치33 연속 작업 결과는 [통합 증거](evidence/p10-batch33-integrated.md)를 따른다. 새 Native 패키지·독립 소비와 Swift Simulator Core 계측은 확인했으나 전체 Strict, OpenAPI의 HTTP 전수 대응, Native/Unity 성능 전체 및 P11 완료는 아직 PARTIAL이다. 기존 P05 실패·StoreKit 환경 위험·실 Provider 13건 대기는 유지한다.
