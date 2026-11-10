# 현재 API 범위 — 개발 중

이 문서는 구현된 표면을 설명하며 완성된 SDK 계약이 아니다. 자세한 구현 및 실패 이력은 `PROGRESS.md`와 `WORK_LOG.md`를 따른다.

- Kotlin `LocalMockClient` 및 Swift `LocalMockClient`: 로컬 Backend의 `signIn`, `restore`, `products`, `wallet`, `purchase`, `signOut`. 이 API의 구매는 명시적 MOCK 거래다.
- Unity `GameBridgeSdk.Create`와 `GameBridgeClient`: 생성·초기화·상태·진단·종료 표면이 있다. Editor의 offline fake는 독립 smoke로만 확인했다. Android/iOS native bridge는 현재 `sdk.status`, `sdk.shutdown` 외 작업에 `UNSUPPORTED_OPERATION`을 반환한다.
- Android `GoogleAuthProvider`, Swift `AppleAuthProvider`: 실제 인증 API 경계와 fake 시험이 있다. 외부 계정·앱 설정을 한 실제 인증은 아직 실행하지 않았고 Unity/sample 연결도 미완료다.
- Native StoreKit/Play Billing, server verifier와 APNs/FCM sender는 부분 구현이다. 공개 구매 흐름, 서버 지급과 실제 스토어 연결이 끝났다는 뜻이 아니다.
- Push host adapter는 사용자가 명시적으로 권한과 등록을 요청하는 호스트 경계다. 메시지는 `messageId`, `route`, `campaignId`만 소비하고 route는 `home` 또는 `store`만 허용한다. 서버 token 등록과 실제 원격 알림은 미완료다.

서버가 반환하는 `requestId`로 오류를 추적한다. SDK 오류에는 `CONFIG_REQUIRED`, `SESSION_EXPIRED`, `NETWORK_UNAVAILABLE`, `TIMEOUT`, `CANCELED`, `BUSY`, `UNSUPPORTED_OPERATION` 등이 있다. 실제 구현되지 않은 작업은 성공으로 대체하지 않는다. 로그아웃에서 로컬 삭제는 끝났으나 서버 revoke 확인에 실패한 경우 Native 오류에 `REVOCATION_UNCONFIRMED`가 표시된다. 현재 이 경고의 재시작 후 영속 표시와 자동 재시도는 없다.
