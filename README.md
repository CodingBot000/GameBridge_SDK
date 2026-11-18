# GameBridge SDK
> **명시 승인된 별도 확장 — 사용자 문서37 / feature/social-login-20261119**
> 기존 아래 포트폴리오 판정·CI648은 동결 snapshot이다. 이 브랜치의 새 소셜 인증은 별도 구현·검증 중이며, 옛 DEV_RC로 새 기능을 검증한 것으로 취급하지 않는다. 원격 push/PR/Release는 하지 않는다.

| 새 인증 경로 | 구현 | 로컬 검증 | Native/패키지 | 실제 계정 |
| --- | --- | --- | --- | --- |
| iOS Google | A 구현, 공식GoogleSignIn9.2.0/custom nonce | Swift29·기존JWT/Audience 회귀 PASS | device/sim XCFramework·source/binary 소비 build·UPM147 PASS (Player未실행) | WAITING_USER |
| Android Facebook | B 구현, Meta18.3.0 Classic | Kotlin/Backend HTTP·C# PASS | Maven/R8 소비 PASS | WAITING_USER |
| iOS Facebook | B 구현, Meta18.1.1 Limited/Classic | Swift30·서버 증명 분리 PASS | 공식 검증 binary cache로 Simulator archive PASS; 원격 다운로드 지연 | WAITING_USER |
| Android Apple | C 대기 | NOT_RUN | NOT_RUN | WAITING_USER |

```csharp
await sdk.SignInAsync(AuthProvider.GOOGLE); // 기존Android / 새iOS 경로
await sdk.SignInAsync(AuthProvider.APPLE);  // 기존iOS / C배치Android 웹 경로
await sdk.SignInAsync(AuthProvider.FACEBOOK);
```



Kotlin Android·Swift iOS·C# Unity를 연결하는 **개인 게임 서비스 SDK 포트폴리오**입니다. 인증·구매·Push의 공통 인터페이스, Native Plugin, 서버의 세션·지급 권위, 설치·소비·회귀 검증을 함께 구현했습니다.

**PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS — 포트폴리오 개발 종료.** 전체 SDK 제품화 상태는 별도 BLOCKED_INTERNAL이며 알려진 제한과 실패를 유지합니다.

포트폴리오 최종 판정은 [최종 보고](docs/FINAL_REPORT.md), 실제 지원·미검증 범위는 [호환성](docs/COMPATIBILITY.md)을 따릅니다. 상용 적용 SDK나 정식 출시 결과로 제시하지 않습니다.

## 먼저 볼 자료

1. [Quick Start / Host 통합](docs/INTEGRATION.md) — 패키지 설치, LOCAL_MOCK 실행, 플랫폼별 연결과 오류 진단
2. [설계·Edge Case·문제 해결](docs/ENGINEERING_NOTES.md) — 계층별 소유권, 대표 난제3개, weak client 제한 조사
3. [API 계약](docs/API.md) / [보안 경계](docs/SECURITY.md) — 호출·상태·오류, 세션·증빙·토큰의 권위
4. [버전·호환성·검증 결과](docs/COMPATIBILITY.md) — 환경과 source/checksum, 실제 Player와 CI의 차이

개발 이력 전체가 필요할 때만 [64 Task 원장](docs/PROGRESS.md)과 [WORK_LOG](docs/WORK_LOG.md)를 읽으면 됩니다.

## 구조

```text
Unity C# Public API ─┬─ Android JNI → Kotlin SDK ─┐
                    └─ iOS Swift C ABI → Swift SDK ─┤
Android/iOS 단독 Host → Native SDK ──────────────┤
                                               Backend → PostgreSQL
```

- Unity는 typed API·요청 수명·main-thread 전달을, Native는 OS Provider·HTTP·보안 저장소를 소유합니다.
- Backend는 인증·계정 binding·구매 검증·멱등 지급·token 소유권을 확인합니다. UI callback이 서버 잔액을 대신하지 않습니다.
- Host는 Activity/window·Delegate·Firebase 초기화·알림 권한·사용자 동의와 화면을 소유합니다.

## 공고 요구와 실제 대응

사용자가 제공한 `Recruit2개회사.md`의 W(웹젠)·G(그라비티) 스냅샷을 기준으로 정리했습니다.

| 요구 | 프로젝트가 보여주는 근거 | 범위 |
| --- | --- | --- |
| W/G: SDK·Library·API 설계 | Kotlin/Swift Core, C# 공통 facade, JNI/C ABI, 역할·상태·wire 계약 | [설계와 실제 소스](docs/ENGINEERING_NOTES.md) |
| W: Edge Case와 정밀한 테스트 | 중복/취소/late/session 격리, duplicate guard 변이·복원, 원장 unique·멱등성 | [Edge Case 표](docs/ENGINEERING_NOTES.md#대표-edge-case) |
| W: 데이터 기반 난제 해결 | ADB build/runtime 수명 분리, OS별 source-binding 순서 오류, 전체화면 안내와 reconnect 실패 분리 | [실제 사례3개](docs/ENGINEERING_NOTES.md) |
| W: 기술 스펙·연동 문서화 | Host/SDK/Backend 책임, 실행 가능한 기존 샘플·설치 순서·오류 진단 | [통합 가이드](docs/INTEGRATION.md). 실제 외부 조직 협업 실적으로 바꾸어 말하지 않음 |
| G: Unity·Android·iOS SDK 및 공통 기능 | 공통 인증·상점·Push, Native bridge, LOCAL_MOCK 양 Player 검증 | [기능 범위](docs/FEATURE_MATRIX.md) |
| G: Client–Server·REST | Spring Boot Kotlin/PostgreSQL, HTTP OpenAPI24 operation·DTO23·합성 응답 대조 | [API](docs/API.md) |
| G: 호환성·버전·빌드/배포 체계 | Maven/AAR·static XCFramework·UPM147 checksum, 독립 R8/Swift 소비, 선정 ABI와 신규 Unity 소비 | [호환성](docs/COMPATIBILITY.md). 로컬 DEV_RC이며 공개 배포 운영은 아님 |
| W/G: 언어 이해·엔진·Native Plugin 우대 | Kotlin·Swift·C#, Unity6000.5.8f1, 직접 작성한 JNI/Swift C ABI 연결 | Objective-C/C++·Unreal·Godot·Windows Native를 개발했다고 주장하지 않음 |
| W/G: 실제 플랫폼 기능·Backend 우대 | Google/Apple/Billing/StoreKit/FCM/APNs adapter·실제 호출 코드와 synthetic 경계, Spring Boot | 실제 Provider13건·출시·AWS/GCP/Kubernetes 운영은 미검증/범위 밖 |
| 경력3/7년·상용 개발/출시·대외 협업·해외근무 조건 | 이 프로젝트만으로 증명할 수 없음 | 기존 이력서·출시/경력 증빙 및 본인 확인과 별도로 평가 |

## 확인한 결과

| 확인 범위 | 근거 |
| --- | --- |
| 새 Android/iOS Unity LOCAL_MOCK Player → Native → Backend → 원장 | [Android](docs/evidence/p10-batch34-unity-android.json), [iOS](docs/evidence/p10-batch34-unity-ios.json): 실제 소비·구매·서버 잔액/PII 경계 |
| 원장·취소/중복·session·변이 복원 | [회귀 증거](docs/evidence/p10-batch34-regression.json): Python263, Kotlin10/Swift12, managed418 검사, self9, TC11 등 서로 다른 범위를 구분 |
| 최신 코드 Hosted CI | [44287600414 SUCCESS](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44287600414), code648bb80. Unity/Release는 SKIPPED |
| 패키지·호환성 | [새 패키지147](docs/evidence/p10-batch33-package.json), [선정 JVM4개](docs/evidence/p10-batch34-binary-api.json), device/simulator C ABI4개와 실제 소비 |
| 제한된 실측 | [C ABI](docs/evidence/p10-batch34-cabi-performance.json), [실제 Player/Scene/frame](docs/evidence/p10-batch34-unity-performance.json). weak1 관측·누수 미확정 |

실제 Google/Apple 계정·스토어·FCM/APNs·실기기 PASS와 구분합니다. 전체 Strict0회, P05-T03 StoreKit FAIL/환경 위험, self-hosted 미검증과 weak1은 [Known Limitations](docs/ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)에 공개합니다.

## 사용·검토 시작

로컬 DEV_RC는 `artifacts/portfolio-final/DEV_RC`에 구성하며 생성 바이너리는 Git에 넣지 않습니다. 다른 checkout에서는 [통합 가이드](docs/INTEGRATION.md)의 기존 build/package 명령으로 준비합니다. Git의 `unity/Packages/com.gamebridge.sdk` 소스 설치와 Native 바이너리를 포함한 staging 설치는 다릅니다.

[Native Demo](<unity/Packages/com.gamebridge.sdk/Samples~/Native Demo/README.md>)와 [Offline Demo](<unity/Packages/com.gamebridge.sdk/Samples~/Offline Demo/README.md>)를 재사용합니다. 실제 Provider를 연결하려는 경우에만 [USER_SETUP](docs/USER_SETUP.md)을 사용합니다. 남은 개선 사항은 선택적 backlog이며 포트폴리오 개발을 자동으로 재개하는 조건이 아닙니다.
