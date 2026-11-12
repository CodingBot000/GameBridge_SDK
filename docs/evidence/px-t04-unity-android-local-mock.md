# GameBridge LOCAL_MOCK 검증 증거 — Unity Android Player

**상태: 로컬 Mock PASS. Google 로그인·실제 스토어 결제 NOT_RUN.**

| 검증 항목 | 결과 |
|---|---|
| 실행 경로 | Unity Player → Kotlin Bridge → LOCAL_MOCK Backend/PostgreSQL |
| 소스 SHA | `c58b4a68083f772988819c408ca3f5481cdcb3e5` |
| 추적 파일 변경 | 없음 |
| DB 지급 원장 | 1건, 100코인 |
| Unity Android Player | PASS |
| 실제 Provider·스토어 | NOT_RUN |
| result.json SHA-256 | `a32d054b832d060ce4aafff4d123fb2f63c6f9348dc8edc0e4c38570a6fd9e1a` |
| APK SHA-256 | `0b10dcc0796f7225b566ba78079a2bd79eabd7c1363d912a9ba77b51dace5949` |
| Unity 마커 수 | 21 |
| Backend HTTP 200 trace | 1 mock-auth, 1 catalog, 2 entitlements, 1 verify, 1 logout |

Runner는 지정된 Unity/Native 결과, Backend trace, 로컬 DB 원장을 검사한 뒤 PASS를 기록한다.
Native request ID와 Backend HTTP request ID는 별개이다.

원본 로그·실기기 식별자·개발 키·로컬 DB·APK는 Git에 포함하지 않는다.
이 요약은 Unity iOS 또는 실제 Google/Apple/FCM/APNs 연동 완료의 증거가 아니다.

검증일은 2026-11-12다. 실행은 `python3 harness/run-unity-android-mock-e2e.py --run-local --staging <검증된 staging> --serial <전용 emulator> --expected-avd <전용 AVD>`였으며 종료 코드 0이다. Unity Editor 6000.5.8f1, Android 36 ARM64 에뮬레이터, Unity Android IL2CPP 개발 빌드, 전용 로컬 PostgreSQL을 사용했다. 전용 AVD의 첫 전체화면 안내는 수동으로 닫았다. UPM staging은 110개 파일 체크섬을 검사했고 Unity 소스 일치 및 staging manifest SHA-256은 `d0f88d08e435d2de9b11028f15db9fbbcc526d894aeedeb110cb23c309dfec7e`다.
