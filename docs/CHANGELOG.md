# 변경 이력

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
