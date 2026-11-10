# P09-T03 R20 오프라인 로그아웃

- `android/sdk-android/src/test/kotlin/com/gamebridge/android/auth/GoogleAuthProviderTest.kt`, `concurrent restores rotate once and offline logout clears local session`: synthetic backend revoke 실패에서 `NETWORK_UNAVAILABLE`과 `REVOCATION_UNCONFIRMED`, 저장 token 제거를 확인한다.
- `ios/Tests/GameBridgeCoreTests/AppleAuthProviderTests.swift`, `testConcurrentRestoreSharesRefreshAndOfflineLogoutClearsLocally`: 동일 오류와 Keychain 대역 저장소의 token 제거를 확인한다.
- 두 테스트는 `harness/run-auth-regression.py`에서 실행한다. `artifacts/verify-all-2cnr0y99/summary.md`의 Android 17건 및 Swift 22건 synthetic auth suite가 통과했다.
- 실제 네트워크 차단 기기, 실제 인증 제공자 및 Unity player 검증을 뜻하지 않는다. 서버 revoke는 확인되지 않은 상태로 보고한다.
