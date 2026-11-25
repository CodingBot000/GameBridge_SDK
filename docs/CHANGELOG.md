# 변경 이력

> 개발 버전 `0.1.0-dev`의 변경 기록입니다. **병합됐다는 사실과 실제 Provider·Release 검증 완료는 다릅니다.** 최초 포트폴리오 DEV_RC의 동결 근거는 보존하고, 이후 승인된 확장을 아래에 별도로 기록합니다.

## 0.1.1-dev 개발자용 후보

- SDK 버전 메타데이터를 맞추고 Android 및 iOS Simulator의 호환성을 검사했다. Android API 34와 iOS 18.6에서 이전 SDK 위에 후보를 설치해 세션과 미완료 구매를 복구했다. [Batch A](evidence/batch-a47-dev-compatibility.md) · [Batch B](evidence/batch-b48-compatibility.md).

## 2026-11-20~25 — iOS Google 인증 및 포트폴리오 문서 개편

- [PR #7](https://github.com/CodingBot000/GameBridge_SDK/pull/7): Native/Unity iOS 실제 Google 로그인 기록, 독립 Native Host, 로컬 HTTPS sandbox, Google AppController 자동 콜백 Export 추가. 최초 실제 Unity 인증은 수동 콜백 연결 빌드에서 수행했으며 새 Export 검증과 구분.
- [PR #8](https://github.com/CodingBot000/GameBridge_SDK/pull/8): UnityScene warm/cold URL 처리 보완. 실제 계정 로그인·복원·UI 취소·로그아웃 PASS (Native/Unity); 합성 warm URL ABI 1회/C# 이벤트 0건, cold URL 직접 주입 NOT_RUN. 실계정 refresh/replay 미실행, 합성 Swift 10건·Backend HTTP 2건 통과. [iOS Google 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md).
- [PR #9](https://github.com/CodingBot000/GameBridge_SDK/pull/9): README를 공통 API·아키텍처·대표 검증 성과 중심으로 개편한 문서 변경. [PR #8 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45153886562) 및 [PR #9 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45174047873) 기본 5개 Job SUCCESS, Unity E2E/Release SKIPPED.
- [PR #10](https://github.com/CodingBot000/GameBridge_SDK/pull/10): iOS Apple 로그아웃 후 Provider 선택 기록을 정리하고, 기존 Keychain 세션이 없다고 확인한 경우에만 다른 앱의 낡은 Apple 선택 기록을 정리한다. 인증 수명 회귀를 기본 PR CI에 연결한다.
- [PR #11](https://github.com/CodingBot000/GameBridge_SDK/pull/11): iOS Export는 쓰기 전 입력을 검증하고, 쓰기 중단 뒤 같은 폴더에서 복구한다. 복구 계획과 충돌한 Host 수정은 보존한다.

아래는 각 단계의 당시 기록이며 최신 판정은 [기능 매트릭스](FEATURE_MATRIX.md)를 따릅니다.

## 2026-11-20 — 소셜 인증 확장 및 Unity iOS Host 패키징 통합

- [PR #4](https://github.com/CodingBot000/GameBridge_SDK/pull/4): iOS Google, Android/iOS Facebook, Android Apple 웹 인증 구현. Backend Provider 증명 분리·기존 session/구매 원장 재사용·Native/Unity 라우팅 확장. 당시 실제 계정 OAuth는 **WAITING_USER**.
- [PR #5](https://github.com/CodingBot000/GameBridge_SDK/pull/5): Unity iOS Export Hook에서 Meta 18.1.1 동적 의존성을 Host App에 Embed·서명하도록 수정; 반복 적용 멱등성 검사 및 iOS Player 사전 검사 추가. 원인과 [iOS E2E PASS](IOS_META_EMBED_FIX.md) 기록.
- Android Unity LOCAL_MOCK은 PR #4 병합 소스에서 로컬 PASS(33 marker, 지급 1건/100코인); PR #5에서는 Android 변경·재실행하지 않음. iOS Unity LOCAL_MOCK은 수정 소스에서 로컬 PASS(23 marker, 지급 1건/100코인, 로그아웃 후 활성 세션 0).
- [PR #5 Hosted CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44538602965)의 필수 5개 Job SUCCESS; Unity E2E/Release SKIPPED. `main` Merge commit `18e22af8800626a50364350f3ff56b596d00cf39`. 이 단계에서는 공식 SDK/플랫폼 실계정 테스트·실스토어 거래·원격 푸시를 실행하지 않았다.

## 이전 개발 이력 (작성 당시 원문)

> 문서37의 최신 소셜 확장 상태·검증은 [SOCIAL_AUTH_HANDOFF](SOCIAL_AUTH_HANDOFF.md)를 따른다. 아래 이전 포트폴리오 snapshot과 실Provider 검증을 구분한다.


## 0.1.0-dev — 포트폴리오 동결 후보

정식 릴리스나 여러 버전의 마이그레이션 실적은 없습니다. 실제 환경·source·ABI와 Host 확인 원칙은 [COMPATIBILITY](COMPATIBILITY.md)를 따릅니다.

- Kotlin Android·Swift iOS·C# Unity SDK, JNI/Swift C ABI, Native HTTP·세션/보안 저장소·Provider adapter를 구현했습니다.
- Backend의 identity/session·purchase binding·원장/멱등 지급·finalization·Push 소유권을 연결하고 LOCAL_MOCK과 synthetic 경계를 검증했습니다.
- Maven/AAR·static XCFramework·UPM147 checksum, 독립 R8/Swift 소비와 새 양 Unity LOCAL_MOCK Player를 확인했습니다. 기존의 “Unity import/Player 미실행” 설명을 현재 증거에 맞게 정리했습니다.
- Core와 Google session codec/Apple grant decode 책임을 정리하고 원래 baseline 및 Native 전이 guard·회귀/변이·정상 복원을 유지했습니다.
- HTTP OpenAPI24 operation·DTO23/실제 응답 구조 검사와 순서 의존성 회귀를 추가했습니다. 누락 필수 header가500이던 오류는400 INVALID_ARGUMENT로 수정했습니다. BUG-017의 세부 SSE/Map 검사 잔여는 OPEN입니다.
- C ABI와 실제 Player lifecycle·Scene/frame·runtime 메모리를 관측했습니다. weak client1의 원인/누수 여부는 미확정이며 성능 향상률을 주장하지 않습니다.
- 포트폴리오 최종화는 문서·제한 조사·동일 바이너리의 로컬 DEV_RC 정리입니다. 제품/하네스/계약 코드는 마지막 Hosted 검증 code648bb80 이후 변경하지 않습니다.

실제 Provider13 WAITING_USER, P05-T03/StoreKit 환경 위험, 전체 Strict·self-hosted/Release 및 미실행 profiling은 [최종 보고](FINAL_REPORT.md)에 명시합니다.

## 문서37 소셜 확장 B

SOC-B: Meta Android18.3.0/iOS18.1.1 Native adapter, explicit Facebook proof types, server debug/OIDC verification, Native account-session reuse, Host callback integration, forward V10 migration 및 부정 테스트 추가. 실계정 미실행.

## 문서37 SOC-C / 확장 종료

Android Apple Custom Tabs/App Links, 서버 Services ID/ES256/code exchange/form_post callback, verifier-bound one-use completion, V11 migration 추가. 기존 proofType 생략 HTTP 호환을 명시 null 기본 처리로 보장. 공통 challenge 대기 중 shutdown 시 UI를 열지 않도록 Android/iOS 수명 경계를 보강하고 회귀 검증했다. Live Provider/새UnityPlayer/원격배포 없이 A/B/C 로컬 구현·검증을 종료한다.
