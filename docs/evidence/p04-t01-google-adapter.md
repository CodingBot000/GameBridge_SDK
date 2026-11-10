# P04-T01 Android Google adapter 검증 요약

- 시각: 2026-11-10 Asia/Seoul. Android SDK 36, AGP 8.13, Kotlin 2.1.20, Credential Manager 1.6.0 및 Google ID 1.1.1.
- `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug`: 종료 0. JUnit XML 4건·실패 0·skip 0: stub gateway/backend로 nonce 전달, 설정 누락, user 불일치, 호출자 취소, 동시 로그인 BUSY 및 Native 저장 경로를 확인. 실제 Credential Manager 화면은 실행하지 않았다.
- `:sample-app:assembleDebug`: 종료 0. 이 샘플은 현재 LOCAL_MOCK 화면이며 실제 Google 로그인 연결을 뜻하지 않는다.
- 의존성 1.2.1은 Kotlin metadata 2.4 불일치로 빌드 실패한 뒤 1.1.1로 조정했다. 처음에 테스트 하나가 JUnit에 감지되지 않은 문제와 재시험은 WORK_LOG에 기록했다.
- 미완료: Backend 실제 challenge/exchange·서명 및 nonce 검증, Native 샘플과 Unity 로그인 연결, 공통 UI gate, 실제 Google 계정/서버·기기 검증. 외부 설정은 USER_SETUP의 USER-AUTH-GOOGLE 참조.
