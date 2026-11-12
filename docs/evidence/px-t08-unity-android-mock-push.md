# PX-T08 Unity Android LOCAL_MOCK Push 부분 검증

- 결과: **등록·수신·동일 ID 중복 억제·Unity 메인 스레드·등록 해제/로그아웃 후 이벤트 미관측 PASS**. 전체 Push/Lifecycle E2E 완료를 뜻하지 않는다.
- 소스 `94d2154b9e72636c5b51a86dc961b3f13aee18d4`, 실행 당시 tracked-clean. Unity 6000.5.8f1, Android 36 ARM64 전용 에뮬레이터, Unity IL2CPP 개발 빌드, 별도 local-mock PostgreSQL DB.
- 실행: `python3 harness/run-unity-android-mock-push-e2e.py --run-local --staging <검증된 staging> --serial <전용 emulator> --expected-avd <전용 AVD>`, exit 0. 전용 에뮬레이터의 최초 전체화면 안내는 수동으로 닫았다.
- Backend에서 동일 messageId의 개발 전용 발송 세 번을 요청했고 Unity 이벤트는 메인 스레드에서 한 번 전달됐다. 등록 해제 뒤 서버 발송은 403, 로그아웃 뒤 토큰 row는 0개였고 추가 이벤트는 관측되지 않았다. 연결된 상태의 로컬 SSE 시험이다.
- APK SHA-256 `769e4383ffa8da50728db9a815da9a344854515b2e22468b5e24176252c3f0bb`. 원본 로그·기기 식별자·합성 키·DB·APK는 Git에 포함하지 않는다.
- **NOT_RUN:** 백그라운드/포그라운드, 네트워크 단절·복구, 프로세스 종료·재시작 및 pending, 다른 세션·늦은 callback 주입, iOS Player, 실제 FCM/APNs.
