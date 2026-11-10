# P05-T02 Google Play Billing adapter — 부분 검증

- 시각: 2026-11-10 Asia/Seoul. Google Play Billing 9.1.0, Android SDK 36, AGP 8.13, Kotlin 2.1.20.
- `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug`: 종료 0. JUnit XML의 Billing fake gateway/sink 시험 7건·실패0·skip0. pending·계정 불일치·수량 2 미지급, proof fingerprint 불일치, verifier/동시성 미설정 시 구매 UI 차단, 늦은 검증 중 계정 전환, 무관한 callback 라우팅을 확인했다.
- `:sample-app:assembleDebug`: 종료 0. 소스 검사에서 Android client의 consume/acknowledge 호출 없음. 샘플은 아직 LOCAL_MOCK이며 실제 스토어 UI는 연결되지 않았다.
- 미완료: 기기별 proof 검증 동시성 사용자 선택, 서버 binding 및 실제 Play Developer API proof verifier/sink, 계정 변경·재시작 전체 복구, Unity/샘플 통합, Play Console 테스트 상품·계정과 실제 기기 구매. Fake sink의 성공은 실제 Play 결제나 서버 검증의 증거가 아니다.
