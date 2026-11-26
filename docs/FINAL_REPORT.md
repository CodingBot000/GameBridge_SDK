# GameBridge 포트폴리오 최종 보고

> 아래 원래의 종료 판정과 64개 Task 집계는 **문서36 당시 포트폴리오 스냅샷**으로 보존합니다. 이후 사용자 승인으로 별도 소셜 로그인 확장·iOS 패키징 보완을 진행했습니다. 과거 수치·FAIL/WAITING_USER를 소급 변경하지 않습니다.

## 현재 포트폴리오 종료 판정 — 2026-11-26

**포트폴리오 `PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS`. 리팩토링 `REFACTORING_VERIFIED_FOR_REVIEW`.** SDK 0.1.2-dev / Bridge v1. 전체 SDK 제품화의 판정은 `BLOCKED_INTERNAL`이며 기존 64개 Task 원장을 유지합니다.

| 영역 | 확인한 결과 |
| --- | --- |
| 공개 배포 | [v0.1.2-dev Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)의 Unity UPM·Android Maven·iOS XCFramework와 검증 파일 3개를 공개했습니다. 비로그인 다운로드로 SHA-256, 매니페스트, 검증 후보와의 바이트 일치를 확인했습니다. |
| 리팩토링 | Android Store 수명주기·FCM 토큰 획득 공통화, Unity 상태 모델·진단·Capability Decoder 분리. C# 공개 메타데이터와 선정 JVM/JNI·iOS C ABI 비교를 통과했습니다. |
| 실제 Player | Android API 34와 iOS 18.6에서 0.1.1-dev → 0.1.2-dev 덮어 설치 후 세션과 미완료 구매 복구, 각 원장 1건·100코인. 합성 PII 2건, iOS LOCAL_MOCK Push 1건, 로그아웃 후 복원 차단·종료 2건 성공. [실행 근거](evidence/bridge-client-refactor-verification.md) |
| Hosted CI | PR #18 HEAD `46988f8`의 기본 5개 성공. Unity E2E와 Release Readiness SKIPPED. [CI 실행](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45812418546) |

0.1.2-dev의 Google 실계정 재검증은 미실행입니다. 기존 실계정 증거는 아래 기록을 따릅니다. StoreKit 26.5 FAIL, 전체 Strict 및 weak client 원인 미확정과 실제 원격 Push·스토어·실기기 제한이 남아 있습니다. [기능 매트릭스](FEATURE_MATRIX.md) · [알려진 제한](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)

## 0.1.1-dev 포트폴리오 판정 — 2026-11-25

**포트폴리오: PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS.** SDK 0.1.1-dev / Bridge v1. PR #13·#14 통합 및 Android Google 후속 실계정 검증을 완료했다. SDK 제품화는 기존 BLOCKED_INTERNAL을 유지한다.

| 후속 작업 | 결과 |
| --- | --- |
| 개발자용 배포 | [v0.1.1-dev Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.1-dev) 공개. Maven·XCFramework·UPM 및 SHA-256·소스 매니페스트·Release Notes를 배포하고 다운로드 검증을 완료했다. |
| 버전 교체 | Android API 34·iOS 18.6, 앱/DB 보존, 세션·미완료 구매 복구, 원장 각 1건/100코인; 선정 API/ABI 비교 PASS |
| Unity·OS | Unity 6000.5.8f1, Android API 30·34·36 및 iOS 18.6·26.5 LOCAL_MOCK 검증; Unity 6000.4 DEFERRED_ENV 및 후속 범위 제외 |
| Google | Android API 34 AVD·iOS 18.6 Simulator Native/Unity 실제 로그인·취소·복원·로그아웃 및 세션 폐기 PASS |
| Hosted CI | [PR #14 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45578953794) 기본 5개 SUCCESS, Unity E2E/Release SKIPPED |

근거: [Batch A](evidence/batch-a47-dev-compatibility.md) · [Batch B](evidence/batch-b48-compatibility.md) · [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md). Android 취소 후 재로그인 성공은 확인했으나 iOS Native의 해당 성공, 양 플랫폼 실제 refresh/replay, 실기기 및 다른 실제 Provider/스토어/원격 Push는 미검증이다. 기존 StoreKit 26.5 FAIL, 전체 Strict 제한, weak client 원인 미확정 및 역사적 64 Task 원장을 보존한다. 신규 기능 및 호환성 확대는 이번 범위에서 종료한다.

## 후속 iOS Google 실계정 검증 및 README 통합

- **SDK 통합:** [PR #7](https://github.com/CodingBot000/GameBridge_SDK/pull/7)·[PR #8](https://github.com/CodingBot000/GameBridge_SDK/pull/8) 병합, 최신 SDK 변경 기준 `09db0706f0e53693d9fd44df290d9da4c49aba6b`. iOS Google Native·Unity iOS 18.6 Simulator 실제 계정 로그인·앱 재시작 후 복원·Google UI 취소·로그아웃 및 해당 Backend 세션 폐기 PASS. 자동 콜백을 사용한 Unity Player에서도 실제 로그인 PASS. [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md) / [정제 증거](evidence/ios-google-oauth-verification.json).
- **검증 경계:** 합성 warm 콜백 ABI 1회/C# 이벤트 0건, 실제 OAuth ABI 진입 0건. cold URL 직접 주입, 실계정 refresh/replay, Native 취소 후 재로그인 성공 및 실기기는 미확인. Unity 두 timeout 기록과 최초 Native 실패를 유지한다.
- **문서·CI:** [PR #9](https://github.com/CodingBot000/GameBridge_SDK/pull/9) 병합 `761be81e89995720dfa7713be62310ac13e06fc3`; [PR #8 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45153886562) 및 [PR #9 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45174047873) 기본 5개 Job SUCCESS, Unity E2E·Release SKIPPED. 기존 LOCAL_MOCK, 실패·제한 및 64 Task 기록은 소급 변경하지 않는다.
- **판정:** `PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS` 유지, 전체 SDK 제품화는 기존 `BLOCKED_INTERNAL` 유지. 나머지 Provider/스토어/푸시 검증 상태는 [기능 매트릭스](FEATURE_MATRIX.md)를 따른다.

## 이후 통합·검증 추록 (2026-11-20)

- **GitHub 통합:** [소셜 로그인 확장 PR #4](https://github.com/CodingBot000/GameBridge_SDK/pull/4), [iOS Meta Embed 수정 PR #5](https://github.com/CodingBot000/GameBridge_SDK/pull/5)가 모두 `main`에 병합됨. 최종 Merge commit `18e22af8800626a50364350f3ff56b596d00cf39`.
- **Android:** PR #4 병합 소스 `36ca836`에서 Unity LOCAL_MOCK Player → Native JNI → Backend → PostgreSQL **PASS**(marker 33개, 원장 1건/100코인). PR #5에서 Android 소스 변경이나 재실행 없음.
- **iOS:** Meta 의존성 Host App Embed 수정 후 새 Unity LOCAL_MOCK Player → Swift C ABI → Backend → PostgreSQL **PASS**(marker 23개, 원장 1건/100코인, 로그아웃 후 활성 세션 0). [원인·실행 기록](IOS_META_EMBED_FIX.md) / [정제된 증거](evidence/ios-meta-embed-fix.json).
- **당시 Hosted CI:** [Run 44538602965](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44538602965) 기본 5개 Job SUCCESS, Unity E2E/Release SKIPPED. 실제 Player 검증은 로컬에서 수행.
- **당시 결론:** 포트폴리오 `PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS` 유지. SDK 전체 제품화 원장은 별도 `BLOCKED_INTERNAL` 유지. **실계정 소셜 OAuth, 실제 스토어 거래, 원격 푸시는 미검증**이며 상용 Release 없음.

최신 기능별 판정은 [기능 매트릭스](FEATURE_MATRIX.md), 패키지/소스 구분은 [호환성](COMPATIBILITY.md), 실계정 시험 준비는 [사용자 설정](USER_SETUP.md)을 참고하세요.

## 문서36 당시 종료 판정 및 기록 (원본)

**포트폴리오: PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS — 개발 종료.**

**전체 SDK 제품화: BLOCKED_INTERNAL.** 기존64 Task는 구현25/진행39, 로컬PASS23/FAIL1/PARTIAL40, 실제 Provider13건 WAITING_USER다. 두 판정을 합치거나 미완료 행을 삭제하지 않았다.

## 무엇을 완성했는가

Kotlin Android·Swift iOS·C# Unity 공통 SDK, Android JNI/iOS Swift C ABI, Native 인증·스토어·Push adapter, Spring Boot/PostgreSQL Backend와 로컬 패키지·검증 체계를 구현한 개인 포트폴리오다. 상용 적용·출시·실제 고객 지원 실적으로 제시하지 않는다.

제공 공고 W(웹젠)의 SDK/Library·Edge Case·데이터 기반 문제 해결·기술 문서화 요구와, G(그라비티)의 Unity/Native 공통 SDK·REST·빌드/버전·호환성 업무에 대응한다. [설계·Edge Case·문제 해결](ENGINEERING_NOTES.md)에서 요구별 소스·문서를 찾을 수 있다. 경력3/7년·상용 플랫폼·출시·대외 협업·해외근무 조건은 기존 이력서·본인 증빙과 별도다.

| 결과물 | 검토 위치 |
| --- | --- |
| 프로젝트 목적·공고 대응·빠른 증거 | [README](../README.md) |
| 설치·초기화·LOCAL_MOCK 로그인/구매·서버 잔액·Push·종료 | [INTEGRATION](INTEGRATION.md)와 기존 Native/Offline Demo |
| 계층·비밀정보·상태 소유권, Edge Case, 문제 해결3사례 | [ENGINEERING_NOTES](ENGINEERING_NOTES.md), [SECURITY](SECURITY.md) |
| 공개 API·비동기/오류·HTTP/Bridge·SSE/Map 계약 | [API](API.md) |
| 패키지/version/source/checksum·선정 ABI·소비 범위 | [COMPATIBILITY](COMPATIBILITY.md), [CHANGELOG](CHANGELOG.md) |
| 실제 Provider를 선택할 때의 로컬 준비 | [USER_SETUP](USER_SETUP.md) |
| 개발 원장과 실패 원본 추적 | [PROGRESS](PROGRESS.md), [WORK_LOG](WORK_LOG.md), 각 evidence와 Git 이력 |

## 개발 종료 기준 판정

| 사용자 기준 | 판정·근거 |
| --- | --- |
| 핵심 LOCAL_MOCK 실제 실행 | 새 [Android](evidence/p10-batch34-unity-android.json)/[iOS](evidence/p10-batch34-unity-ios.json) Player→Native→Backend→원장 PASS |
| Android/iOS/Unity 연동 구조 | 실제 JNI·C ABI·UPM 소비와 현재 소스·소유권 문서 대응 |
| 구매 지급·세션 핵심 불변식 | 원장1건/100코인, TC 변이·복원, session/late/duplicate 및 managed/Core 회귀 증거 |
| 심각한 P0 결함 확인 여부 | 검토한 범위에서 신규 P0 확인 없음. weak1은 원인·누수 미확정으로 공개 |
| 패키지/source 연관성 | Native build a83561a와 현재 shipping source diff0, SDK147 checksum·선정 ABI·새 양 소비 |
| 공개 API/Edge Case 근거 | [회귀](evidence/p10-batch34-regression.json) 및 [대표 입력/기대/관측](ENGINEERING_NOTES.md#대표-edge-case) |
| 코드와 맞는 통합 가이드 | 실제 constructor·public API·Host 예제·scripts·Controllers 대조, 문서 정합성 검토 |
| 대표 문제 해결 사례 | ADB 수명/port 분리, OpenAPI 순서 이식성, 전체화면 안내와 reconnect 실패 분리. 미확정 원인은 단정하지 않음 |
| 미검증·실패 공개 | 아래 제한과 원장의 FAIL/PARTIAL/WAITING_USER 유지 |

위 기준으로 **포트폴리오 개발 종료를 권고하고 이번 개발을 종료한다.** 새 P1/P2 개선점이나 실제 Provider 연동을 자동 다음 필수 배치로 넘기지 않는다. 새 P0가 재현되거나 핵심 증거가 무효임이 확인되면 그 근거로 별도 PORTFOLIO_BLOCKED 판정을 재검토한다.

## 확정한 실행 근거

마지막 제품·하네스·계약 코드는 `648bb807baeab4e83b037856a9ae04f84e8a2154`다. [Hosted44287600414](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44287600414)는 SUCCESS, inventory/Backend/Android/Swift-iOS/basic PASS이며 Unity/Release는 SKIPPED다. Ubuntu에서 OpenAPI 정상/순서 반전과 Python263을 확인했다.

같은 code의 Core는 Kotlin10/Swift12, managed418 검사·변이·복원, self9 lane/47test(정상44·예상음성3), TC11(정상10·예상변이1)·복원·자기 container 정리를 통과했다. HTTP24 operation의 성공 근거와 DTO23, LOCAL32관측·합성10시험/132구조·오류 MockMvc4를 따로 기록했다. test/helper/check/sample/Player 수를 합산하지 않는다. 정확한 source·실행 범위는 [회귀](evidence/p10-batch34-regression.json), [Hosted](evidence/p10-batch34-hosted.json)를 따른다.

이번 최종화는 문서·기존 자료/소스 검토·동일 산출물 RC 정리다. 제품/하네스/계약 코드를 바꾸지 않아 CI·Player·전체 회귀를 날짜 갱신 목적으로 반복하지 않았다. 새 문서의 API-name/링크/예제 문법·source diff와 패키지 checksum을 필요한 범위에서 검토했다. 최종 문서 commit은 Git 이력과 인계 메시지에서 확인한다.

## 제한된 위험 처리

- **weak client1:** 기존120cycle 자료와 cleanup 소스를 검토했다. active/driver·transport current/Message/queue·pending/cancel 등록 정리 경로가 있다. 계측 async 프레임이 끝나기 전 GC/weak count를 읽으므로 테스트 참조·await/런타임 root 가설을 분리했다. root chain·증가 곡선·clean-stack 대조는 없어 누수 여부를 확정하지 않는다. 추가 재현0/제품 수정0으로 제한 조사를 종료한다. [조사](ENGINEERING_NOTES.md#제한-조사--weak-client1개).
- **BUG-017:** 중요 HTTP 사용 범위의 SSE/Map 필드를 현재 소스와 대조해 API 문서에 보강했다. 기계 schema와 자동 검사 잔여는 OPEN으로 남긴다. 포트폴리오 종료를 막는 필수 신규 개발로 전환하지 않는다.
- **전체 Strict:**58 required lane·원래 P05 기록 실패를 유지한다. E2 생성/전 wrapper 소유권 배선 미완료이므로 전체 실행0회, 마지막 preflight는 DEFERRED_ENV/2다. 안전 기준을 낮추지 않았다.
- **기존 실패·외부 대기:** P05-T03 FAIL, ENV-STOREKIT-26 OPEN, iOS18.6 간헐 위험, 실 Provider13 WAITING_USER, 실기기/self-hosted/Release 미검증을 유지한다.
- **추가 profiling:** Android JNI heap·iOS continuation·Unity CPU blocking/첫 app 초기화는 NOT_RUN이다. 현재 실측은 환경별 관측이며 성능 향상률·상용 안정성을 주장하지 않는다.

## 최종 로컬 후보와 선택적 backlog

최종 로컬 경로는 `artifacts/portfolio-final/DEV_RC`이며 Native 재빌드 없이 검증된 UPM/Maven/XCFramework와 현재 문서를 묶는다. SDK0.1.0-dev·build source·검증 code·내부147 checksum·상위 문서 checksum·제한을 manifest에 분리한다. 생성 바이너리는 Git에 넣지 않고 공개 Release/registry/스토어 배포를 하지 않는다.

Unreal/Godot/Windows Native·C++ 포팅, Kubernetes/AWS/GCP 운영, 실 Google/Apple/결제/FCM/APNs와 정식 출시는 이번 개발에서 제외한다. 선택적 제품화가 필요할 때만 [backlog](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)와 USER_SETUP을 사용한다. 포트폴리오의 현재 SDK·Native Plugin·REST·문서화·문제 해결 증거를 해당 경험으로 확대하지 않는다.

## 후속 0.1.1-dev 개발자용 후보

선정 API/ABI와 Android·iOS의 LOCAL_MOCK 버전 교체를 확인했다. Unity 6000.5.8f1의 대표 OS 실행은 [Batch B 검증 기록](evidence/batch-b48-compatibility.md)에 있다. Android Google 실계정은 후속 검증에서 PASS했다 ([Android Google 검증](evidence/android-google-live-20261125.md)). StoreKit·Strict 제한은 각 기존 원장에 남아 있다.
