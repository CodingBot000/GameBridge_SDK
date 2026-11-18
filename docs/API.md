# SDK·HTTP·Bridge 계약

공개 Unity 표면은 [GameBridgeClient](../unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs), 설정은 [GameBridgeConfig](../unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeConfig.cs)가 기준입니다. 실제 사용 순서는 [Quick Start](INTEGRATION.md)를 따릅니다.

## Unity 공개 API

| 영역 | 실제 API | 호출자의 책임 |
| --- | --- | --- |
| 생성·수명 | `GameBridgeSdk.Create`, `InitializeAsync`, `ShutdownAsync`, `Dispose` | main thread에서 생성/수명 관리. 활성 facade 하나. 같은 설정 init 공유·다른 설정 거부 |
| 상태 | `GetStatus`, `GetCapabilities`, `GetDiagnostics`, `GetNativeDiagnosticsAsync` | 동기 getter는 snapshot. Native 진단만 비동기 왕복 |
| 인증 | `SignInAsync`, `RestoreSessionAsync`, `SignOutAsync` | LOCAL_MOCK은 MOCK, 실Provider는 설정된 GOOGLE/APPLE. token은 Native 소유 |
| 상점 | `GetProductsAsync`, `PurchaseAsync`, `GetEntitlementsAsync`, `SyncPurchasesAsync` | 논리상품ID 사용, pending과지급 구분, 서버 entitlement로 표시 |
| Push·설정 | `RequestPushPermissionAsync`, `RegisterPushAsync`, `UnregisterPushAsync`, `GetServiceConfigAsync` | 명시적 사용자 동작과 installation UUID, Host adapter 및 mode 확인 |
| 이벤트 | `PurchaseUpdated`, `PushReceived`, `PushOpened`, `PushTokenChanged` | UI 수명에 맞게 구독 해제. 중복/late event와 완료 Task를 분리 |

`SdkCapabilities`의 supported/configured/mode/reason으로 미지원과 미설정을 구분합니다. Push 미설정이 전체 초기화 실패를 뜻하지는 않습니다.

계획서에 있는 이벤트 명칭을 실제 공개 이벤트로 간주하지 않습니다. 위 표는 현재 C# source에 존재하는 표면입니다. raw access/refresh token·구매 증빙·Push token 원문은 공개 result에 포함하지 않습니다.

`PurchaseResult.status`는 `PURCHASED/PENDING/CANCELED/VERIFICATION_PENDING/FAILED`, 지급은 `NOT_GRANTED/GRANTED/ALREADY_GRANTED`, 완료 처리는 `NOT_REQUIRED/PENDING/FINALIZED`로 나눕니다. `PURCHASED`만 보고 코인을 더하지 않습니다. 잔액·revision·거래 식별자처럼 정밀도 손실이 가능한 값은 wire의10진 문자열 규칙을 따릅니다.

## 요청·취소·오류

- `requestId`는 요청, `sdkSessionId`는 SDK 세대, `eventId`는 이벤트 식별자입니다. 응답은 request/session/operation이 맞아야 수락합니다.
- public Task는 한 번 완료합니다. 취소·timeout은 기다림의 종료이며 이미 시작한 결제 취소가 아닙니다. 늦은 거래는 이벤트·복구·서버 조회로 반영합니다.
- 현재 소스의 일반 요청 기본30초·interactive180초·pending100·diagnostic ring200은 구현의 설계값입니다. 성능 보장이나 새 운영 정책으로 제시하지 않습니다.
- `SdkException.Code/Retryable`로 동작을 결정합니다. `NativeCode`는 logout의 `REVOCATION_UNCONFIRMED`만 보존합니다. 로컬 session은 지웠으나 서버 revoke 미확인이라는 뜻이고, 재시작 후 경고 영속화·자동 revoke 재시도는 없습니다.

| 오류·상태 | 대응 |
| --- | --- |
| `CONFIG_REQUIRED`, `INVALID_ARGUMENT` | mode·필수 설정·형식 확인 후 명시적으로 재시도 |
| `NOT_INITIALIZED`, `BUSY`, `ALREADY_INITIALIZED_DIFFERENT_CONFIG` | 호출 순서와 활성 client/UI 작업 수명 확인 |
| `SESSION_EXPIRED`, `AUTH_FAILED`, `AUTH_REPLAY_DETECTED` | Native의 안전한 복원/재인증. 실패를 Mock으로 전환하지 않음 |
| `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED` | 재시도 가능 여부와 기존 거래 상태를 따로 확인 |
| `IDEMPOTENCY_CONFLICT`, `PURCHASE_ACCOUNT_MISMATCH`, `VERIFICATION_FAILED` | 계정·attempt·body·증빙 경계 확인. 새 지급을 강행하지 않음 |
| `PERMISSION_DENIED`, `UNSUPPORTED_PLATFORM/PROVIDER/OPERATION` | Host 권한·capability·모드에 맞게 UI 안내 |
| `MAINTENANCE` | 신규 구매 차단, 기존 검증/복구·로그아웃 경계 유지 |
| `BRIDGE_PROTOCOL_MISMATCH`, `PAYLOAD_TOO_LARGE` | wire 버전·UTF-8·허용 크기/모델을 대조 |

전체 코드 목록은 [error-codes.json](../contracts/error-codes.json), 재현·설정 조치는 [Troubleshooting](INTEGRATION.md#7-연동-문제-해결)을 참고합니다. 무조건적인 자동 구매/로그인 UI 재시도는 구현 계약이 아닙니다.

## 서로 다른 두 계약

| 계약 | 내용 | 근거 |
| --- | --- | --- |
| [Bridge JSON Schema](../contracts/bridge.schema.json) | Unity↔Native request/response/event, UTF-8·session·request·허용 operation | Kotlin/Swift/C# parser·변이 회귀 |
| [HTTP OpenAPI](../contracts/openapi.yaml) | Backend24 operation의 method/path, profile, security/header·DTO·응답 | 소스 binding·DTO23·정상/음성16 및 실제/합성 HTTP 대조 |

OpenAPI는 JSON 형식의 YAML1.2입니다. HTTP `X-Request-Id`는 서버가 생성하며 오류 body의 `requestId`와 연결됩니다. purchase verify에는 `Idempotency-Key`가 필요합니다. Mock은 nonblank/128자 이하, Apple/Google verify는 canonical UUID를 요구합니다. 누락된 필수 header는400 `INVALID_ARGUMENT`입니다.

개발 auth·Xcode fake grant·Push stream은 `local-mock` 전용, 개발 Push send는 `local-mock/sandbox`, 실제 purchase/read/device controller는 `sandbox/production` 경계를 가집니다. Production에는 개발 send를 등록하지 않습니다. `x-source-bindings`와 Controller profile이 근거입니다. 실패·403·503·429의 모든 분기를 실행했다는 의미는 아닙니다.

## LOCAL_MOCK SSE와 Map 응답

SDK 연동자가 실제 소비하는 범위를 현재 Controller와 대조했습니다. 아래는 **사람이 읽는 보강 계약**이며 OpenAPI의 SSE/동적 Map 기계 검증 잔여를 없앴다고 주장하지 않습니다.

| 응답 | 실제 필드·동작 | 소스 |
| --- | --- | --- |
| `GET /v1/catalog` | JSON array. LocalMock: `productId/storeProductId/type` 문자열. Sandbox/Production은 `platform`도 포함. 실제 현지화 가격은 스토어가 제공 | [MockPurchaseController](../backend/src/main/kotlin/com/gamebridge/purchase/MockPurchaseController.kt), [StoreReadController](../backend/src/main/kotlin/com/gamebridge/purchase/StoreReadController.kt) |
| `GET /v1/purchases/{purchaseId}` | 본인·app/environment 범위의 `serverPurchaseId/productId/storeStatus/fulfillmentStatus/finalizationStatus`. 내부 `CLIENT_PENDING`은 응답 `PENDING`으로 변환 | StoreReadController |
| `PUT/DELETE /v1/devices/{installationId}/push-token` | 등록은 `provider/registered/tokenFingerprint`, 해제는 `registered`. 원문 token은 반환하지 않음 | [DeviceRegistrationController](../backend/src/main/kotlin/com/gamebridge/push/DeviceRegistrationController.kt), [MockDevices](../backend/src/main/kotlin/com/gamebridge/push/MockDevices.kt) |
| `POST /v1/dev/push/send` | `accepted` boolean과 `delivery`. LocalMock `SIMULATED`, Sandbox `QUEUED`; 실제 단말 전달 확인이 아님 | [DevPushController](../backend/src/main/kotlin/com/gamebridge/push/DevPushController.kt) |
| `GET /v1/dev/push/stream?installationId=...` | Bearer session과 등록 소유권 필요. `text/event-stream`: `ready`의 data는 `connected`, `push` data는 `messageId/route/campaignId` JSON. campaignId는 null 가능. heartbeat는 comment | [MockPushStreamController](../backend/src/main/kotlin/com/gamebridge/push/MockPushStreamController.kt) |

SSE는 수신/heartbeat마다 session·installation 소유권을 재확인하고, 해제·로그아웃 등으로 소유가 사라지면 완료합니다. 연결 해제 시 listener/heartbeat를 정리하며 미연결 메시지를 저장 재전달하지 않습니다. `route`는 개발 send/SDK 경계에서 `home/store`만 허용합니다. raw token/proof를 payload에 추가하지 않습니다.

24 operation 모두 성공 응답 근거가 있고, 합성 HTTP10시험에서132개의 직렬화 구조를 대조했습니다. 문자열 값은 제거한 구조 검증이라 의미·서명 검증으로 확대하지 않습니다. [HTTP 근거](evidence/p11-batch34-openapi-synthetic.json). **BUG-017은 OPEN**이며 SSE event별 자동 schema 대응·동적 Map의 세부 명세 검사를 Known Limitation으로 남깁니다. 포트폴리오 종료와 독립된 선택적 보강입니다.
