# PX-T08 Unity Android LOCAL_MOCK Push 부분 검증

- 결과: **등록·수신·동일 ID 중복 억제·Unity 메인 스레드·등록 해제/로그아웃 후 이벤트 미관측 PASS**. 전체 Push/Lifecycle E2E 완료를 뜻하지 않는다.
- 소스 `94d2154b9e72636c5b51a86dc961b3f13aee18d4`, 실행 당시 tracked-clean. Unity 6000.5.8f1, Android 36 ARM64 전용 에뮬레이터, Unity IL2CPP 개발 빌드, 별도 local-mock PostgreSQL DB.
- 실행: `python3 harness/run-unity-android-mock-push-e2e.py --run-local --staging <검증된 staging> --serial <전용 emulator> --expected-avd <전용 AVD>`, exit 0. 전용 에뮬레이터의 최초 전체화면 안내는 수동으로 닫았다.
- Backend에서 동일 messageId의 개발 전용 발송 세 번을 요청했고 Unity 이벤트는 메인 스레드에서 한 번 전달됐다. 등록 해제 뒤 서버 발송은 403, 로그아웃 뒤 토큰 row는 0개였고 추가 이벤트는 관측되지 않았다. 연결된 상태의 로컬 SSE 시험이다.
- APK SHA-256 `769e4383ffa8da50728db9a815da9a344854515b2e22468b5e24176252c3f0bb`. 원본 로그·기기 식별자·합성 키·DB·APK는 Git에 포함하지 않는다.
- **초기 시험에서 NOT_RUN:** 백그라운드/포그라운드, 네트워크 단절·복구, 프로세스 종료·재시작 및 pending, 다른 세션·늦은 callback 주입, iOS Player, 실제 FCM/APNs. 후속 시험 결과는 아래에 별도로 기록한다.

## 백그라운드 및 네트워크 복구 추가 시험

- 소스 `ab17d9ecc88e78debb06ab0b6435b8e7cd02ed90`, tracked-clean. 동일 Runner 수정본의 새 전용 Android 36 에뮬레이터 실행 exit 0, `artifacts/unity-android-push-a82dcn48/result.json` PASS.
- 실제 HOME→앱 재개에서 Unity pause/resume callback 및 메인 스레드 확인. 전용 에뮬레이터의 Wi-Fi/data를 차단해 host 접속 실패를 확인한 뒤 Mock 메시지를 발송하고 연결 복구 후 기존 메시지가 전달되지 않음을 확인했다. 이후 연결된 상태에서 새 메시지가 Unity에 전달됐다.
- 재시험의 APK SHA-256 `3a05e5d7894a3fafec1b75b436ee4c9bfba34ca66efbbb0e889e68e070770b86`. 전용 에뮬레이터 최초 전체화면 안내는 수동으로 닫았다.
- 프로세스 강제 종료·재시작 및 pending, 세션 변경·늦은 callback 주입, iOS Player, 실제 원격 FCM/APNs는 여전히 NOT_RUN이다.
