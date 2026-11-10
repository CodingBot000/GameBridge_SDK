# P05-T06 Mock 복구 검증 요약

- Android 36 전용 emulator: `KeystoreNamespaceTest#pendingPurchaseSurvivesNewKeystoreInstancesAndDoesNotDoubleGrant`, 1건 통과. 독립 Keystore namespace 재생성 후 local Mock PostgreSQL의 기존 거래를 복구하고 코인이 한 번만 증가했다.
- iOS 26.5 전용 simulator: `MockRecoveryDeviceTests/testKeychainInstancesRecoverCommittedMockPurchaseOnce`, 1건 통과, skip 0. ad-hoc simulator 서명과 독립 Keychain service를 사용했다.
- 두 시험은 서버 지급 commit의 응답을 버리는 상황을 모사하고 새 Native client/store 인스턴스에서 동일 거래를 재검증한다. 테스트 전용 Mock 계정의 DB 데이터는 보존했다.
- 실제 기기에서 프로세스를 강제 종료한 재시작, Unity Player/JNI/IL2CPP, 실제 Google/Apple 거래는 실행하지 않았다.
