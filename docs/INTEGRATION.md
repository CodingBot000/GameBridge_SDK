# 통합 안내 — 개발 중

## 앱과 인증 정보의 소유권

Host가 Android Activity 및 Firebase 초기화, iOS window와 AppDelegate/notification delegate를 소유한다. SDK에 화면·delegate를 전달하며 SDK가 Host delegate를 교체하지 않는다. 인증 토큰, 스토어 증빙 및 push 토큰을 Unity 이벤트, 로그 또는 `PlayerPrefs`에 기록하지 않는다. 각 플랫폼의 실제 앱 등록, 인증키, 콘솔 설정은 `USER_SETUP.md`를 따른다.

앱이 알림 권한과 등록을 명시적으로 요청해야 한다. Android의 `AndroidPushHostAdapter`를 쓰는 Host는 Firebase Messaging 의존성과 앱 설정을 별도로 제공하고 기존 `FirebaseMessagingService`에서 callback을 전달한다. `android/host-examples`는 예시이며 자동 활성화되지 않는다. iOS의 `ApplePushHostAdapter`에는 Host의 등록 성공/실패 및 수신/열기 callback을 전달한다. 현재 adapter와 서버 사이의 실제 토큰 등록은 미구현이다.

## 구매 및 계정

신규 서버 세션은 인증 challenge로 확인한 앱 범위에 연결된다. 범위가 없는 기존 세션은 구매 binding을 받기 전에 재인증해야 하며 자동 변경·삭제하지 않는다. Apple/Google account binding은 Native 내부 값이다. 검증된 거래만 서버에서 지급하며 Apple finish는 서버의 지속된 지급 확인 뒤에만 수행해야 한다. 서버 verifier·실제 스토어·Native 조립은 아직 완성되지 않았다.

## 패키지 소비

Android Maven 소비 예시는 `android/consumer-check`에 있으며 소스 프로젝트 참조 없이 로컬 coordinate를 사용한다. Firebase Messaging은 optional `compileOnly`이므로 FCM을 사용하는 Host가 별도로 의존성을 넣어야 한다. iOS XCFramework는 device/simulator slice를 무서명으로 생성하고 별도 Swift consumer link를 확인했으나, 실기기 서명·Unity linkage는 미확인이다.

Unity Android/iOS export hook과 staging script가 있으나 Unity Editor 라이선스 부재로 import 및 실제 export를 검증하지 못했다. 완성된 배포 패키지라고 가정하지 않는다. `scripts/package-sdk.sh`는 기존 output을 덮어쓰지 않으며 필요한 Native 산출물이 없으면 실패한다.
