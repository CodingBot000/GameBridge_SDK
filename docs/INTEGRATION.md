# 통합 안내 — 개발 중

## 앱과 인증 정보의 소유권

Host가 Android Activity 및 Firebase 초기화, iOS window와 AppDelegate/notification delegate를 소유한다. SDK에 화면·delegate를 전달하며 SDK가 Host delegate를 교체하지 않는다. 인증 토큰, 스토어 증빙 및 push 토큰을 Unity 이벤트, 로그 또는 `PlayerPrefs`에 기록하지 않는다. 각 플랫폼의 실제 앱 등록, 인증키, 콘솔 설정은 `USER_SETUP.md`를 따른다.

앱이 알림 권한과 등록을 명시적으로 요청해야 한다. Android의 `AndroidPushHostAdapter`를 쓰는 Host는 Firebase Messaging 의존성과 앱 설정을 별도로 제공하고 기존 `FirebaseMessagingService`에서 callback을 전달한다. `android/host-examples`는 예시이며 자동 활성화되지 않는다. iOS의 `ApplePushHostAdapter`에는 Host의 등록 성공/실패 및 수신/열기 callback을 전달한다. 현재 adapter와 서버 사이의 실제 토큰 등록은 미구현이다.

## 구매 및 계정

신규 서버 세션은 인증 challenge로 확인한 앱 범위에 연결된다. 범위가 없는 기존 세션은 구매 binding을 받기 전에 재인증해야 하며 자동 변경·삭제하지 않는다. Apple/Google account binding은 Native 내부 값이다. 검증된 거래만 서버에서 지급하며 Apple finish는 서버의 지속된 지급 확인 뒤에만 수행해야 한다. 서버 verifier와 Native 내부 runtime은 synthetic fixture로 연결 검증했으나 공개 sample/Unity 조립과 실제 스토어 검증은 아직 완성되지 않았다.

## 패키지 소비

Android Maven 소비 예시는 `android/consumer-check`에 있으며 소스 프로젝트 참조 없이 로컬 coordinate를 사용한다. Firebase Messaging은 optional `compileOnly`이므로 FCM을 사용하는 Host가 별도로 의존성을 넣어야 한다. iOS XCFramework는 device/simulator slice를 무서명으로 생성하고 별도 Swift consumer link를 확인했으나, 실기기 서명·Unity linkage는 미확인이다.

Unity Android/iOS export hook과 staging script가 있으나 Unity Editor 라이선스 부재로 import 및 실제 export를 검증하지 못했다. 완성된 배포 패키지라고 가정하지 않는다. `scripts/package-sdk.sh`는 기존 output을 덮어쓰지 않으며 필요한 Native 산출물이 없으면 실패한다.

Unity iOS의 Mobile Notifications 2.5.0 host adapter는 명시적으로 권한을 요청하고 foreground remote callback과 마지막 알림 열기를 정규화한다. 해당 Unity API 구독 시 foreground 시스템 알림의 기본 표시는 억제된다. 현재 Swift bridge host operation은 UNSUPPORTED로 남아 있어 토큰/이벤트의 전체 전달은 동작하지 않는다.

### Unity Android LOCAL_MOCK (부분 연결)

개발 서버를 명시적으로 `local-mock` profile로 실행하고 Android host가 접근할 수 있는 개발 서버 주소를 설정한다. `new GameBridgeConfig(appId, ProviderMode.LocalMock, backendUrl, timeoutMs, developmentKey, mockSubject)`로 메모리에서만 개발키와 `A` 또는 `B`를 전달한다. 이 키는 로컬 개발 서버 전용이며 소스·Unity 에셋·로그에 저장하지 않는다. Android emulator의 host loopback은 `10.0.2.2`를 사용하고, 개발 전용 cleartext 허용은 host 앱에서 해당 주소에 한정해 설정한다. 토큰과 구매 증빙은 Native에 남는다. 인증·상품 조회·Mock 구매·서버 잔액 경로는 연결됐지만 구매 sync와 push, 실제 스토어 브리지는 아직 미연결이다. config 조회는 서버 설정과 유효 cache를 구분한다. 이 경로는 Native JVM→로컬 Backend/DB로만 검증했으며 Unity JNI 실행은 ENV-002로 미검증이다.

Unity iOS LOCAL_MOCK도 동일한 명시 설정을 Swift C ABI로 전달하며 Native Keychain 별도 항목을 사용한다. C ABI 초기화·session 분리와 Swift handler→로컬 서버/DB는 각각 검증했다. 둘을 합친 Unity iOS 실행, 실제 Apple 계정/StoreKit, 구매 sync·push 브리지는 미연결이다. config 조회의 서버/유효 cache 경계는 synthetic 시험으로 확인했다. iOS simulator의 HTTP 개발 서버 허용은 host의 개발 전용 네트워크 보안 설정이 필요하다.

Android PLATFORM_SANDBOX 인증 bridge는 Native GoogleAuthProvider와 Credential Manager를 사용한다. Google OAuth 서버 client ID는 `GameBridgeConfig` 7인자 생성자에 전달한다. 계정 토큰은 Native 내부에 남고 Mock fallback은 없다. fake 경계와 compile만 확인했으며 실제 Google·Unity JNI 검증은 남았다.

iOS PLATFORM_SANDBOX 인증 bridge는 활성 key window를 Native AppleAuthProvider에 전달하고 Keychain을 별도 보관한다. fake 인증 경계와 simulator framework compile만 확인했으며 Apple 계정과 Unity iOS 실동작은 USER-AUTH-APPLE 준비 후 별도 확인해야 한다.

Android Unity sandbox의 Google Play bridge는 host가 명시한 두 상품 ID로 Native Billing facade를 구성한다. 구매 UI의 성공 응답은 검증 대기로 표시하며, 서버 지급 확인 후 `PurchaseUpdated` 이벤트와 서버 entitlement 조회를 사용한다. fake provider·이벤트 session 격리 및 복구 집계만 확인했으며 실제 Play·Unity JNI 및 복구 중복 요청의 완전한 single-flight는 미검증 또는 미완료다.

iOS Unity sandbox는 Native StoreKit 상품·구매·서버 잔액을 연결하고 서버 확인 및 finish 후에만 완료 결과를 반환한다. 거래 업데이트와 미완료 복구의 검증된 결과는 session·계정 세대가 일치할 때 구매 이벤트로 전달한다. 이 경로는 fake 결과와 simulator compile만 확인했으며 실제 StoreKit listener, 사용자 복원 및 Unity iOS는 미검증이다. 복구 사유 분기는 fake 시험으로 확인했다.
