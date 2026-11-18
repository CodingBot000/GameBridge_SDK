# 현재 API 범위

배치34의 최신 검증·제약은 [통합 증거](evidence/p10-batch34-integrated.md)를 따른다. 실제24 HTTP operation의 성공 응답 구조, DTO23개, 새 양플랫폼 Unity LOCAL_MOCK 소비와 선정 JVM API를 확인했다. C ABI 시간은 측정했지만 Task/continuation·Android heap·Unity Scene/Frame 및 전체 Strict는 미완료이며 DEV_RC를 유지한다.


구현과 검증 상태는 [PROGRESS](PROGRESS.md), 세부 실행 결과는 [WORK_LOG](WORK_LOG.md)를 따른다. Native fake와 실제 스토어 검증은 별개다.

- Kotlin/Swift `LocalMockClient`는 로컬 Backend의 인증·상품·구매·복구·잔액과 Mock 푸시 등록을 제공한다. 사용자·앱·서버에 결속된 세션과 구매 단서는 Native 보안 저장소에 남는다.
- Unity `GameBridgeSdk.Create`와 `GameBridgeClient`는 초기화·상태·인증·상점·푸시·config·종료를 제공한다. `GetDiagnostics()`는 C# registry 상태, `GetNativeDiagnosticsAsync()`는 Native의 제한된 typed 이벤트를 반환한다. 독립 managed/fake 시험과 Native 경계 시험, Unity Editor 및 Android/iOS LOCAL_MOCK Player 실행을 확인했다. 실행별 범위와 source는 [배치32 증거](evidence/p10-batch32-integrated.md)를 따른다. 실제 Provider와 실기기 검증은 별도다.
- Android Google/Play Billing 및 iOS Apple/StoreKit Provider는 Native와 Unity bridge에 연결돼 있다. 서버 지급 확인 후 구매 완료를 전달한다. synthetic verifier와 fake Provider를 검증했으며 실제 Google/Apple 계정과 스토어 거래는 별도 미실행이다.
- `XCODE_STOREKIT`은 iOS 18 이상, 명시적 개발 설정 및 소모품 이력 설정이 필요하다. StoreKit의 Xcode 로컬 검증 후 격리된 local-mock fake 서버가 지급한다. 이는 Apple 서버 서명 검증이 아니다. iOS 18.6 local StoreKit과 전용 DB의 응답 유실 복구를 확인했으나 Unity player 및 실제 프로세스 강제 종료는 미검증이다.
- Push host adapter는 권한·등록을 명시적으로 요청한다. 메시지는 `messageId`, `route`, `campaignId`만 소비하고 route는 `home` 또는 `store`만 허용한다. LOCAL_MOCK의 Backend→Android/Swift Native 수신은 전용 DB로 확인했다. LOCAL_MOCK Unity Android/iOS Player의 Push 경로도 확인했다. FCM/APNs 실제 원격 전달은 미검증이다.

서버 `requestId`로 오류를 추적한다. SDK 오류에는 `CONFIG_REQUIRED`, `SESSION_EXPIRED`, `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED`, `BUSY`, `UNSUPPORTED_OPERATION` 등이 있다. Unity `SdkException.NativeCode`는 `auth.signOut`의 `REVOCATION_UNCONFIRMED`만 보존하며, 이는 로컬 세션은 삭제됐지만 서버 revoke가 확인되지 않았다는 뜻이다. 이 경고의 재시작 후 영속 표시와 자동 재시도는 없다.

HTTP API는 [contracts/openapi.yaml](../contracts/openapi.yaml)에 실제 24 method/path를 기술한다. JSON 형식의 YAML 1.2이며 Bridge 메시지용 JSON Schema와 별개다. `python3 harness/check-openapi.py`는 Controller mapping/profile/header 및 Security permitAll·오류 schema와 정적으로 비교한다. DTO 및 endpoint별 오류의 실제 HTTP 응답 전수 대응은 미완료여서 BUG-017은 OPEN이다. OpenAPI 문법 통과는 실제 Provider 통과가 아니다.
