# R22 합성 credential·개인정보 비노출 회귀

- 범위는 로컬 fixture와 LOCAL_MOCK이다. 실제 계정 token, 실제 개인정보와 모든 가능한 로그 형식을 검사했다는 뜻이 아니다.
- Backend 오류/trace: 합성 개발키·email·전화번호를 요청과 예외에 주입한 HTTP/로그 unit 4건 PASS. fake Google verifier와 격리 sandbox DB의 성공·거부 응답 및 캡처된 Backend 로그에서 synthetic 구매 증빙·세션 token이 나오지 않는 통합시험 1건 PASS (`artifacts/r22-proof-0bcej9x1`).
- Android/Swift Native: 격리 Backend가 발급한 synthetic access/refresh token 및 개발키가 bridge 결과와 Backend 로그에 없는지 각각 1건 PASS (`artifacts/r22-native-7r45s8ui`). mock push token/구매 proof 형식 로그 검사 포함. Android/Swift diagnostics의 synthetic email·전화번호 및 키 비노출 시험도 PASS했다.
- Unity 결과·로그: synthetic Native callback의 비허용 email·전화번호가 Android/iOS Unity Player 공개 PushUpdate와 원시 Unity 로그에 남지 않는지 두 Player를 같은 실행으로 확인했다 (`artifacts/unity-pii-current-ml8muq1n`); 각 Player tracked-clean, 원장 1건/100. strict `artifacts/verify-all-p09mpzq9`의 `unity-pii-e2e`는 2건 PASS, 전체 strict는 별도 FAIL이다. Android 최초 전체화면 안내는 수동 처리했다.
- 별도 Android/iOS 기본·Push LOCAL_MOCK Player에서 개발키와 `mock:<UUID>` token/proof 형태의 raw Unity/server 로그 비노출을 확인했다. 세부 실행 경로와 초기 실패 이력은 [부분 검증 이력](r22-local-redaction-partial.md)에 있다.
- `GAMEBRIDGE_RUN_UNITY_PII_E2E=true`와 새 전용 AVD·staging/cache 등 환경을 준비하면 `harness/run-scenario.py R22`의 PII suite는 두 Player를 새로 실행한다. 자동화 환경 부재·테스트 미실행은 성공이 아니다. opt-in 진입 wrapper 자체의 실제 호출은 아직 단위 검증만 했고, 기반 두 Player wrapper 및 strict 증거 판정은 실제 실행했다.
