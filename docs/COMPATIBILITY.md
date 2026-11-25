# 버전·호환성·검증 범위

> 최신 0.1.1-dev 검증을 먼저 정리하고, 이전 소셜 확장과 DEV_RC의 역사적 검증을 보존합니다. 서로 다른 소스의 증거를 합쳐 한 번의 테스트 PASS로 표시하지 않습니다.

## 현재 통합 상태 — 0.1.1-dev (2026-11-25)

| 영역 | 확인된 범위 | 근거·제한 |
| --- | --- | --- |
| SDK 소스·버전 | 패키지 소스 026716f, PR #13 병합 35cddc1, PR #14 통합 949d4e0; SDK 0.1.1-dev / Bridge v1 | Batch B 패키지 바이트는 Batch A와 동일; 로컬 후보, 공개 Release 없음 |
| 패키징 | Maven 3개 모듈, XCFramework, UPM; SHA-256 및 source manifest | [Batch A](evidence/batch-a47-dev-compatibility.md); 배포 권리·프로젝트 라이선스 별도 결정 필요 |
| 선정 API/ABI | 기존 C# 소비자, JVM 클래스 4개 공개 서명, iOS 3 slice의 C ABI 심볼 5개 비교 PASS | 전체 Kotlin metadata·API 호환 보증 아님 |
| 버전 교체 | Android API 34·iOS 18.6에서 0.1.0-dev → 0.1.1-dev, 앱/DB 보존, 세션·미완료 구매 복구, 각 원장 1건/100코인 | [Batch A](evidence/batch-a47-dev-compatibility.md) · [Batch B](evidence/batch-b48-compatibility.md); LOCAL_MOCK |
| Unity·OS | Unity 6000.5.8f1, Android API 30·34·36 AVD, iOS 18.6·26.5 Simulator | 6000.4 DEFERRED_ENV 및 후속 범위 제외; UPM 최소 6000.5 유지 |
| Google 실계정 | Android API 34 AVD / iOS 18.6 Simulator Native·Unity 로그인·취소·복원·로그아웃 PASS | [Android Google 검증](evidence/android-google-live-20261125.md) · [iOS Google 검증](IOS_GOOGLE_OAUTH_VERIFICATION.md); 실제 refresh/replay·실기기 미실행, iOS Native 취소 후 재로그인 성공 미확인 |
| Hosted CI | [PR #14 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45578953794) 기본 5개 SUCCESS | Unity E2E·Release Readiness SKIPPED; Player 및 실계정은 로컬 |

StoreKit 26.5 기존 FAIL 및 전체 Strict 제한은 유지합니다. iOS 26.5 LOCAL_MOCK 성공은 실제 StoreKit 거래 성공이 아닙니다.

## 이전 소셜 확장 통합 상태 (2026-11-23 검증, PR #9 문서 개편 포함)

| 구분 | 확인한 내용 | 근거·제한 |
| --- | --- | --- |
| 코드 | PR #4·#5 소셜/Embed 확장, [PR #7](https://github.com/CodingBot000/GameBridge_SDK/pull/7)·[PR #8](https://github.com/CodingBot000/GameBridge_SDK/pull/8) iOS Google 인증/콜백 통합 (SDK 병합 SHA `09db0706f0e53693d9fd44df290d9da4c49aba6b`); [PR #9](https://github.com/CodingBot000/GameBridge_SDK/pull/9) README 문서 개편 병합 `761be81e89995720dfa7713be62310ac13e06fc3` | 개발용 `0.1.0-dev`, Release 아님 |
| Android Unity LOCAL_MOCK | PR #4 병합 소스 `36ca836` 로컬 Player PASS, marker 33개, DB 원장 1건/100코인 | 문서41 로컬 검증; PR #5에서 Android 수정·재실행 없음 |
| iOS Unity LOCAL_MOCK | Meta Embed 수정 소스에서 새 Unity 6000.5.8f1 / iOS 18.6 Simulator Player PASS, marker 23개, 원장 1건/100코인, 활성 세션 0 | [실행 결과](IOS_META_EMBED_FIX.md) / [정제 증거](evidence/ios-meta-embed-fix.json). 수정된 Hook·runner의 검증 해시를 최종 commit과 대조 |
| iOS UPM — 2026-11-20 Meta Embed 단계 | 소셜 확장·Meta Embed 수정 포함 로컬 staging 147개 checksum PASS, manifest SHA-256 `997fd8dea785aafa859c7ddb319492a101583bc6b59978e799ff3c8952a8bf36` | 당시 산출물; 현재 Google 콜백 후속 stage와 구분. [패키지 안내](INTEGRATION.md#1-패키지-준비) |
| Hosted CI | [PR #8 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45153886562) (code `c3dd91e`) 및 [PR #9 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45174047873) (README 변경) 기본 5개 Job SUCCESS | Unity E2E·Release Readiness SKIPPED; 실제 Player 검증은 로컬 |
| 외부 Provider | iOS Google Native·Unity iOS 18.6 Simulator 실제 계정 로그인·앱 재시작 후 복원·Google UI 취소·로그아웃 및 해당 Backend 세션 폐기 PASS; Backend challenge·Identity·세션 결속 확인 | [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md). 실계정 refresh/replay, Native 취소 후 재로그인 성공, cold Scene URL 직접 주입, Android Google·양 플랫폼 Apple/Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs 및 실기기 미완료 |
| iOS Google 후속 패키징 | Unity 6000.5.8f1, Xcode 26.6 (17F113), iOS 18.6 Simulator; GoogleSignIn 9.2.0 / Meta 18.1.1; 자동 Export·71개 콜백/PBX 검사 및 서명 PASS | 수정 staging manifest SHA-256 `b318a58bb2bd50b78ba068e5794482198069a5b055ae30388e559e0b417b2f0b`. [실행별 증거](evidence/ios-google-oauth-verification.json); 이전 147개 checksum 수치를 새 stage에 소급 적용하지 않음 |

**최신 Unity LOCAL_MOCK PASS는 소셜 인증 실계정 동작을 검증한 결과가 아닙니다.** 배포 지원 OS 범위·상용 안정성을 보증하지 않으며, 원래의 StoreKit 로컬 실패 및 Strict 미완료는 여전히 [알려진 제한](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)으로 남아 있습니다.

## 이전 포트폴리오 DEV_RC 검증 기록

> 다음 버전·소스 SHA·DEV_RC checksum/Hosted 실행 표는 **문서36 당시 포트폴리오 후보**의 근거입니다. 위 소셜 확장 및 iOS Google 후속 stage와 혼동하지 마세요.

**SDK0.1.0-dev / Bridge protocol1 / 로컬 DEV_RC.** 아래는 실제 확인한 조합이며 모든 단말·OS·Unity 버전을 지원한다는 보증이 아닙니다. [최종 보고](FINAL_REPORT.md)는 포트폴리오 종료와 SDK 제품화 상태를 따로 판정합니다.

## 패키지와 source

| 항목 | 확정한 기준 |
| --- | --- |
| Native/UPM 바이너리 build source | `a83561a31c6b34fafcc85988b419fff20c7e059f` |
| 최종 기능·하네스 검증 code | `648bb807baeab4e83b037856a9ae04f84e8a2154` |
| 두 source 사이 Native/UPM 관계 | Android·iOS·Unity shipping source diff0. Backend의 누락 HTTP header400 수정은 별도이며 Backend binary는 UPM에 포함하지 않음 |
| 패키지 manifest | SDK147파일, SHA256SUMS hash `6fc4cb4b8a6765ce6526c988c0df2b43d19e4a35cf7263cd276181a775751fba` |
| 배포 상태 | 로컬 후보 `artifacts/portfolio-final/DEV_RC`. 공개 Maven/UPM registry·GitHub Release·스토어 배포 없음 |

[패키지 빌드 증거](evidence/p10-batch33-package.json), [RC source/checksum](evidence/portfolio-finalization.json). 이 환경에서는 `python3 harness/check-staging.py artifacts/portfolio-final/DEV_RC/upm`으로 내부147 checksum을 확인할 수 있습니다. 외부 checkout의 재생성 명령은 [INTEGRATION](INTEGRATION.md)에 있습니다. 기존 빌드를 날짜 변경 목적으로 반복하지 않습니다.

## 플랫폼별 실제 범위

| 대상 | 확인한 환경·결과 | 경계 |
| --- | --- | --- |
| Android | AGP8.13.0/Gradle8.13/Kotlin2.1.20, JDK21·JVM17, min26/compile·target36. Maven3모듈·AAR/JAR/POM, 독립 unsigned R8 소비. Unity Player는 API34 arm64 Google APIs AVD에서 LOCAL_MOCK JNI·구매·서버잔액·PII 확인 | min/target SDK는 실제 실행한 OS 버전과 다름. 실기기·Google/Play/FCM 실연동 미검증 |
| iOS | Xcode26.6(17F113)/Swift6.3.3. static XCFramework device arm64·simulator arm64/x86_64, Swift source consumer와 simulator module/binary 소비. iOS18.6(22G86) arm64 Simulator의 새 Unity Player·C ABI 확인 | device archive는 signed iPhone 실행이 아님. x86_64 slice가 있어도 해당 Player 실행을 뜻하지 않음. 실제 Apple/StoreKit/APNs 별도 |
| Unity |6000.5.8f1. 새 Android/iOS 소비 프로젝트의 UPM import·CLI build/export·실제 LOCAL_MOCK Player. 이전 GUI Builder/영수증·Push/UTF8 결과도 각 source별 보존 | 다른 Unity 버전·모든 Scene/Domain Reload 조합·상용 앱을 검증한 것은 아님 |
| Backend | Kotlin2.1.20/Spring Boot3.5.16/JDK21, PostgreSQL17.6-alpine3.22의 격리 DB/Testcontainers. 세션·멱등 원장·synthetic verifier/HTTP 검증 | 외부 Provider 서명·운영 DB·다중 서버·클라우드 운영 성과는 미검증 |
| Unity package 의존성 | Newtonsoft JSON3.2.2, Mobile Notifications2.5.0. Native Demo UI는UGUI2.5.0 사용 | package.json의 Unity6000.5 요구가 여러 설치 버전의 실제 호환 시험을 대신하지 않음 |

[새 Android](evidence/p10-batch34-unity-android.json), [새 iOS](evidence/p10-batch34-unity-ios.json), [실제 Player 계측](evidence/p10-batch34-unity-performance.json). 샘플 UI의 프로그램 방식 초기화·구매 callback과 사용자의 실제 포인터/화면 렌더링 검증은 구분합니다.

## 호환성 검사의 의미

- Kotlin 선정 JVM public 표면4개(`SdkCoordinator`, `BridgeProtocol`, `BridgeFacade`, `GoogleAuthProvider`)가 전후 Maven에서 동일했습니다. [비교 hash](evidence/p10-batch34-binary-api.json). 모든 Kotlin metadata ABI를 검사한 것은 아닙니다.
- Swift C ABI는 `GB_ProtocolVersion/GB_SetCallback/GB_Dispatch/GB_Shutdown`4개를 slice별 확인했습니다. 새 packaged C ABI callback·session 교체 실측은 [별도 증거](evidence/p10-batch34-cabi-performance.json)입니다.
- 기존 coordinate 기반 Android R8 소비, Swift source/binary 소비를 보존하고 새 Unity 양 소비를 수행했습니다. 같은 Native source임을 확인했으며 옛 Player 결과를 새 패키지 실행으로 재사용하지 않았습니다.
- public API/wire baseline과 승인된 Native refactor 전이는 [baseline](../contracts/baseline), [source guard](../harness/check-feature-refactor-transition.py)로 검사합니다. source·binary·설치·실행 결과는 서로 대체하지 않습니다.

## 검증 결과 요약

| 구분 | 실제 기록 | 해석 |
| --- | --- | --- |
| Python |263 tests, local 및 Ubuntu inventory PASS | 서로 다른 source의 실행 수를 합산하지 않음 |
| Core·managed | Kotlin10/Swift12, managed418 검사, duplicate 변이 감지·정상 복원 | helper/assertion은 독립 시험 수가 아님 |
| Self-check |9 lane/47test(정상44·예상 음성3)/check9 PASS | 전체 Strict 아님 |
| Testcontainers |11실행 중 정상10·예상 변이1, 정상 복원·자기 container 정리 | 실제 스토어 sandbox 거래 아님 |
| HTTP |24 operation 성공 근거, DTO23, LOCAL32관측·합성10시험/132구조·오류 MockMvc4 | SSE/Map 세부와 모든 오류 분기의 완전 검증 아님 |
| 성능 | managed·Backend·Swift Core·C ABI·실제 Unity Player/Scene/frame | paired 전후 실험이 아니므로 향상률 없음. weak1은 미확정 |
| Hosted | [44287600414 SUCCESS](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44287600414), code648bb80 | inventory/Backend/Android/Swift-iOS/basic PASS. Unity/Release SKIPPED |

수치·명령·source의 상세는 [회귀](evidence/p10-batch34-regression.json), [Hosted](evidence/p10-batch34-hosted.json)에 있습니다. 최종화의 문서 변경은 이 코드와 분리하며 새 제품/하네스 코드가 없으면 CI를 반복하지 않습니다.

## 버전 변경 시 Host 확인 원칙

개발자용 0.1.0-dev 및 0.1.1-dev 사이의 실제 LOCAL_MOCK 버전 교체를 Android/iOS에서 검증했습니다. 공개 배포 및 정식 제품 버전 간 마이그레이션 실적은 없습니다. 후속 배포 시 다음을 확인합니다.

1. `VERSION`, Maven coordinate, UPM `package.json`, Native version 표면과 manifest/checksum을 함께 대조합니다. wire protocol 버전은 SDK 버전과 별개입니다.
2. 공개 API·필수 모델·error/async 의미, min OS/Unity·의존성, Host Activity/Delegate와 build hook 변경을 비교합니다.
3. 기존 consumer source compile, 선정 JVM/C ABI·slice·R8, 새 UPM import/export/Player의 필요한 범위를 다시 검증합니다.
4. 저장된 session/pending 단서의 환경·계정 결속과 재인증 조건을 확인합니다. 새 형식에 맞추려고 기존 데이터를 임의 삭제/이전하지 않습니다.

0.x-dev에 대해 무조건적인 하위 호환을 약속하지 않습니다. 실제 확인한 표면과 위험·설치 변경을 [CHANGELOG](CHANGELOG.md)에 기록합니다. StoreKit26 FAIL/18.6 위험·전체 Strict·실 Provider·self-hosted 등 Known Limitations는 [ENGINEERING_NOTES](ENGINEERING_NOTES.md#알려진-제한과-선택적-후속-작업)에서 관리합니다.

## Batch B 대표 Unity·OS 조합

Unity 6000.5.8f1에서 Android 30·34·36과 iOS 26.5 LOCAL_MOCK Player를 검증했다. iOS 18.6은 동일 패키지의 이전 버전 교체 시험을 근거로 한다. Unity 6000.4.0f1은 모바일 모듈과 고정된 샘플 시험 의존성이 없어 DEFERRED_ENV이며 후속 개발 범위에서 제외한다. UPM 최소 Unity 6000.5 유지. [대표 조합과 범위](evidence/batch-b48-compatibility.md).
