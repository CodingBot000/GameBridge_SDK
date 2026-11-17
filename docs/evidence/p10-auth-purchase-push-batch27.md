# P10-T02 조건부 책임 경계 감사 — 배치27

**REVIEW_ONLY. 제품 리팩토링 NOT_RUN.** A의 실제 Editor smoke 두 경로가 모두 DEFERRED_ENV이고 B/C 완료 조건이 충족되지 않았다. P10-T01은 PARTIAL이며 P10-T02 제품 변경을 시작하지 않는다. 이 감사는 기존 P10-T02 IN_PROGRESS/PARTIAL을 완료로 바꾸지 않는다. 기준 cf276b7, 제품 source 변경0. P10-T01 baseline 파일은 보존하며 T02용 새 제품 baseline을 덮어쓰거나 확정하지 않았다.

## 실제 호출·소유 경계

| 영역 | 기존 호출 경로 / 책임 | 보존할 불변식·관측 한계 |
|---|---|---|
| Android 인증 | GoogleAuthProvider.signIn → backend.challenge → AndroidGoogleGateway.get(호스트 Activity, main thread) → backend.exchange/profile → TokenStore. restore/withAuthenticatedSession이 sessionLock, uiGate는 OS UI 배타 실행 | nonce 전달·프로필 소유 일치·native token만 저장. restore와 operation401의 profile 확인/저장 순서가 다르므로 flow를 무리하게 합치지 않는다 |
| iOS 인증 | AppleAuthProvider(MainActor) → AppleCredentialGateway(OS UI/credential state)·AppleAuthBackend(HTTP). refreshFlight UUID/Task와 generation이 재진입·로그아웃 후 결과를 제어 | 공유 refresh·durable refresh_pending·generation 재확인·logout 먼저 local clear. Android Mutex와 형식 통일하지 않는다 |
| Android 구매 | GoogleStoreSession/GooglePlayStore → Billing provider → GooglePurchaseAccountSource(auth.withAuthenticatedSession, backend binding) → GoogleHttpProofSink → Backend grant → provider의 finalization | account binding·proof fingerprint·동일 attempt id의401 retry·서버 원장 권위. consume/ack 순서·동시1/재시도정책 변경 없음 |
| iOS 구매 | AppleStoreRuntime → StoreKitBillingProvider → ApplePurchaseAccountSource(generation-scoped cache)·AppleHttpProofSink → acceptAppleGrant → finish/didFinish | UI는uiGate, 검증은Native, 지급은Backend. transaction/journal·account/transaction 비교·grant 후finish 순서 유지. 실제 StoreKit/기기는 이번 감사로 검증되지 않는다 |
| Push | AndroidPushHostAdapter/ApplePushHostAdapter는 OS 권한·토큰·host callback forwarding, Google/ApplePushRegistration은 authenticated Backend 등록/해제, PushRouter는 allowlist/dedup | raw token은Native에 한정, Unity에는fingerprint만. 설치ID·session 소유, 해제 즉시 서버token삭제 정책과200개session dedup 유지. 실제FCM/APNs/OS권한은미검증 |
| 전송·오류·비밀정보 | BackendClient는 configured origin/경로·dev-key mode·idempotency allowlist/redirect거부·bounded response·코드 allowlist. TokenStore는 encrypted-at-rest 구현으로 위임 | development key를sandbox/production에 전송하지 않는다. BackendResponse/credential/session/proof description은redacted. 이 검토는 전체 보안감사·실서비스 인증 성공이 아니다 |

검토 파일은 Kotlin GoogleAuthProvider/GoogleHttpProofSink/GooglePurchaseAccountSource/GooglePushRegistration/AndroidPushHostAdapter 및 Swift AppleAuthProvider/AppleHttpProofSink/ApplePurchaseAccountSource/StoreKitBillingProvider/ApplePushRegistration/ApplePushHostAdapter,양 BackendClient와PurchaseCoordinator다. Native token·receipt를Unity로 옮기거나Provider를Mock으로 바꾸는 설계는 채택하지 않는다.

## 후속 후보 — 최대2개, 아직 선정 구현하지 않음

### 후보1: Android 저장 세션의 codec/검증과 인증 orchestration 분리

GoogleAuthProvider의 signIn/restore/withAuthenticatedSession에 StoredGoogleSession 생성·encode/save 및 validate/binding 규칙이 반복된다. 구성-bound session decode/encode·필드 검증을 작은 내부 책임으로 분리하는 가치가 있다. 새 공개 API/base class/DI framework는 필요 없다. backend refresh 실행·tombstone write·profile 확인·저장 시점과sessionLock/uiGate는 기존 orchestration에 남긴다.

특히 restore는 rotated session 저장 후 profile, operation401은 profile 확인 후 저장한다. 두 flow 전체를 하나의 refresh 메서드로 합치는 것은 현재 의미 변경 위험이 있어 제외한다. 실패시 clear와refresh_pending 보존을 임의로 같게 만들지 않는다.

기존 근거: GoogleAuthProviderTest의 nonce/native session, missing config/profile mismatch, cancellation, concurrent restores rotate once/offline logout, lost refresh, ten401single refresh, repeated401once, proof attempt-id 유지, refresh profile mismatch tombstone 사례. 현재소스 재실행 결과는 배치27 통합문서에 따로 기록한다.

추가 회귀 설계(NOT_RUN): (a) appId/mode/backend/provider 각binding 불일치의 정확 SESSION_EXPIRED, (b) malformed canonical user UUID/expiry/empty token의 기존오류, (c) storage save 실패시 기존profile호출·tombstone/clear순서, (d) cancellation/401두번째실패에서old refresh 재사용0·operation 재시도1, (e) signIn/restore/operation401 각 저장 bytes·호출순서 baseline 비교. 기존error/flow를변경하는 새정책검사는추가하지않는다.

### 후보2: Swift proof sink의 grant 응답 decode와 authenticated HTTP 분리

AppleHttpProofSink.verify의 로컬 Output Decodable·fulfillmentStatus검사·ServerGrant변환이 attempt 생성 및 auth/HTTP closure 안에 섞여 있다. GoogleHttpProofSink는 parseGoogleGrant가 이미 분리돼 있으므로 Android를같이리팩토링할이유는약하다. Swift 응답 decoder만 작은 내부 함수로 추출하는 후보가 있다.

attemptId는auth closure 밖에서1회생성,proof/account precheck·server endpoint·dev key mode·main actor 및후속acceptAppleGrant/finish는현재위치에남긴다. decoder에새product/account정책을넣어downstream검사순서를바꾸지않는다. StoreKit finish/Google ack·consume·Backend지급트랜잭션은범위밖이다.

기존 근거: AppleAuthProviderTests.testAppleProofSinkRequiresDurableServerGrant/testAppleProofRetryKeepsIdempotencyKey,StoreKitBillingProviderTests의account/transaction/grant/finish음성,PurchaseCoordinatorTests의중복grant·finalization 전제. 추가설계(NOT_RUN): GRANTED/ALREADY_GRANTED 각각 동일모델,malformed UUID/누락field/거부status의 BRIDGE_PROTOCOL_MISMATCH,허용unknownfield 유지,decode실패시finish0,durablegrant후finish1,401retry같은attempt/동일body,logout generation변경시late grant적용0.

## 수정 제외와 재개 조건

Push의 OS host forwarding/Backend registration/router는 이미 책임이 분리돼 있다. 실제 혼재·중복 근거가 약해 세번째 후보로 늘리지 않는다. timeout/cancel/retry/retention/동시성·스토어 finalization 정책은이미승인된값을유지한다.

C에서 current Player·전체Strict 및P10-T01완료판정이충족된뒤에만후보별(최대2) 별도baseline→정상/음성test→작은제품변경→같은회귀/API·보안/원장대조→독립commit으로재개한다. 이번에는후보감사/설계까지완료했으며T02제품변경0·추가설계case미실행·성능개선미측정이다.
