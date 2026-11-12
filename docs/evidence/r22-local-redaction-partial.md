# R22 합성 민감정보 부분 검증

- Android Unity LOCAL_MOCK Player: source `7156dac`, tracked-clean, `artifacts/unity-android-e2e-m62mfexg/result.json` PASS. 최초 전체화면 안내는 수동으로 닫았다.
- iOS Unity LOCAL_MOCK Simulator Player: source `b2087e1`, tracked-clean, `artifacts/unity-ios-e2e-nz5fz8r5/result.json` PASS.
- 두 test-only consumer는 인증 profile, 구매 결과, Native diagnostics를 직렬화해 그 실행에서 생성한 합성 개발키가 들어 있지 않은지 확인한다. 두 runner는 `GB_MOCK_REDACTION PASS`가 없으면 실패한다.
- 추가 Native LOCAL_MOCK 시험은 새 격리 Backend에서 발급한 synthetic access/refresh token 원문이 Android bridge 응답 및 Swift bridge 결과에 포함되지 않는지 메모리에서 비교했다. Android/Swift 각 1건 PASS/skip 0 (`artifacts/r22-native-7r45s8ui`; 동일 실행의 격리 Backend 로그에 합성 access/refresh token·개발키 및 `mock:<UUID>` push/proof 형태가 없는지도 확인했다. 재현: `python3 harness/run-r22-native-redaction.py --run-local`). 값은 출력하지 않았다.
- 격리 sandbox HTTP/DB와 fake Google verifier 시험 1건에서 합성 구매 증빙·세션 token이 성공/거부 응답과 캡처된 Backend 로그에 노출되지 않음을 확인했다 (`artifacts/r22-proof-0bcej9x1`). 실제 Play 거래는 아니다.
- 독립 managed fixture는 합성 access/refresh token, 구매 증빙, push token 추가 필드가 typed 결과에서 제거되는지 확인했다. Backend MockMvc는 예외 메시지·요청의 합성 secret이 오류 응답 및 ApiErrors 로거에 나타나지 않는지 확인했다. Kotlin/Swift Native의 typed diagnostics와 bridge 합성 시험도 별도로 통과했다.
- 첫 Android 실행은 runner의 marker polling·필터 오류로 FAIL했고 수정 후 재실행했다. 전체 로그·모든 입력 변이·실제 제공자의 credential은 시험 범위 밖이며 R22는 PARTIAL이다. 원본 로그·키·빌드 산출물은 커밋하지 않는다.
- 강화 로그 검사 후 Android/iOS 기본 Player 각각 PASS (`artifacts/unity-android-e2e-j9tb9ven`, `artifacts/unity-ios-e2e-o2mypwsg`), Android/iOS Push Player 동일 실행도 PASS (`artifacts/unity-android-push-918elqj3`, `artifacts/unity-ios-push-anrcrvlm`). raw Unity/server 로그에서 알려진 개발키와 LOCAL_MOCK `mock:<UUID>` token/proof 형태를 검사했다. Android 최초 전체화면 안내는 수동 처리했다. 이 패턴은 범용 비밀정보 탐지기가 아니다.
- 합성 email·전화번호를 Backend 오류/trace, Android/Swift Native diagnostics 입력·예외에 주입한 unit/fake 시험은 Backend 4건·Android 3건·Swift 4건 PASS/skip0. 실제 개인정보 및 Unity raw log의 개인정보 주입 검증은 아니다.
- test-only synthetic Native callback에 허용되지 않은 email·전화번호를 넣어 Android/iOS Unity Player의 공개 PushUpdate 및 원시 Unity 로그에 값이 없는지 확인했다: Android `artifacts/unity-android-e2e-rtm39zwn` source `a42a8b2`, iOS `artifacts/unity-ios-e2e-ehxq_12y` source `6d82338`, 모두 tracked-clean PASS. Android 최초 전체화면 안내는 수동 처리했다. 원격 push나 실제 개인정보는 사용하지 않았으며 자동 strict lane은 미완료다.
