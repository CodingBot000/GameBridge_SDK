# GameBridge 공통 API 계약

개발 중인 계약이다. 현재 이 문서가 API 구현 또는 실서비스 검증을 의미하지 않는다.

- 초기화, 상태 및 capability 조회, 종료.
- 인증: 명시적 provider 로그인, 로그아웃, 세션 복원.
- 상점: 상품 조회, 구매, entitlement 조회, 앱 복귀 또는 사용자 복원 사유에 따른 구매 동기화.
- 푸시: 권한 요청, 명시적 등록 및 해제. 등록 결과는 토큰이 아닌 fingerprint를 제공한다.
- 서비스 설정과 진단 snapshot 조회.

공개 요청은 성공·오류·취소·timeout 중 하나로 종료하며 같은 요청을 두 번 완료하지 않는다. Native가 세션을 소유하고 Unity 공개 결과에는 자격증명, 토큰, 거래 증명을 노출하지 않는다. 예상 가능한 오류는 `error-codes.json`의 코드를 사용한다. Mock은 명시된 모드에서만 실행하며 Sandbox 실패 시 Mock으로 전환하지 않는다.

`coinBalance`, `revision`, `priceMicros`, 플랫폼 거래 ID 등 64비트 정수는 십진 문자열이다. 시간은 UTC ISO 8601이다. nullable 필드와 누락 필드는 구별한다. 알 수 없는 enum은 조용히 성공 상태로 해석하지 않는다. 제품 가격 표시는 스토어에서 받은 localized price를 사용하며, 구매 지급 여부는 서버 entitlement를 따른다. 상세 필드·동시성·이벤트 계약은 [개발계획 5장](../docs/DEVELOPMENT_PLAN.md)을 따른다.

현재 Mock token fingerprint wire 표현은 SHA-256 앞 6바이트의 소문자 16진수 12자이며, 메모리 Fake는 `mock-fingerprint`로 표시한다. 원본 token을 공개 결과에 넣지 않는다. 다른 Provider 구현도 이 형식으로 정규화해야 한다.
