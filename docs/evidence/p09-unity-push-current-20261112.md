# P09 Unity Push 동일 실행 집계

- 소스 `f40f8d5517ef5ec51a667b96cc2bca24e22ce7f2`, 양 Player 실행 중 tracked working tree clean. 기존 미추적 Demo와 캐시는 보존했다.
- `harness/run-unity-push-current.py`를 명시적 opt-in으로 실행해 Android와 iOS Unity LOCAL_MOCK Player 2건 및 현재 소스·필수 결과 marker 검사를 통과했다.
- Android 결과 `artifacts/unity-android-push-0b67f62g/result.json`: Player PASS, network recovery PASS, 로그아웃 후 DB token 0. 빈 테스트 AVD의 최초 전체화면 안내를 수동으로 닫았다.
- iOS 결과 `artifacts/unity-ios-push-ejpifgez/result.json`: Player PASS, network recovery `PASS_LOCAL_TRANSPORT_FAULT`, 로그아웃 후 DB token 0.
- 양쪽에서 중복 억제, foreground/background, 재연결 거부·회복, 이전 세션 합성 callback 폐기 및 사용자 전환을 확인했다. 실제 FCM/APNs, Apple/Google 인증, 실기기와 원격 GitHub Actions 실행은 검증하지 않았다.
- 실행을 마친 테스트용 Simulator와 Android emulator는 shutdown했으며 기기·데이터를 삭제하지 않았다.
