# 변경 이력

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
