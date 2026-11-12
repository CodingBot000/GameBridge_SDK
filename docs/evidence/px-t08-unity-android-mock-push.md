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

## 강제 종료 및 pending 복구 추가 시험

- 소스 `c15550d8efa614914ed8350a3167c0da93bf45eb`, tracked-clean. `harness/run-unity-android-mock-restart-e2e.py --run-local` 전용 Android 36 에뮬레이터 실행 exit 0, `artifacts/unity-android-restart-r3p6hl0d/result.json` PASS.
- 테스트 전용 loopback proxy가 서버의 최초 구매 검증 성공 응답을 503으로 바꾼 뒤 서버 원장 1건·100코인을 확인했다. Unity 앱을 force-stop하고 서로 다른 프로세스로 재실행해 세션 복원, pending 1회 복구, 두 번째 sync의 pending 0건, 원장 불변과 Unity 메인 스레드를 확인했다. 단순 background 전환과 별도 시험이다.
- APK SHA-256 `56af04cd869115f80907f7009b67c20c6dfa4273d9d1edc798f33ebf8448c13c`. 전용 AVD의 최초 전체화면 안내는 수동으로 닫았다. 실제 Play Billing 거래 또는 오프라인 원격 푸시를 뜻하지 않는다.
- 세션 변경·늦은 callback 주입, 재연결 실패 검증과 iOS Player, 실제 FCM/APNs는 별도 미완료다.

## A→B 세션 전환 추가 시험

- 소스 `817de08732c3534e156fbb8cf3d4f9ae05724b60`, tracked-clean. 확장된 동일 Runner의 새 전용 Android 36 AVD 실행 exit 0, `artifacts/unity-android-push-h9oyrtjy/result.json` PASS.
- A 로그아웃 후 Unity SDK를 종료하고 B로 재초기화해 같은 설치를 등록했다. 이전 A 사용자 발송은 403으로 거부됐고 B 사용자의 Mock 이벤트는 메인 스레드에서 한 번 전달됐다. 테스트 중 이전 메시지의 재유입은 관측되지 않았다. 등록 해제·로그아웃 후 DB token row는 0개다.
- 기본 등록/중복, background/foreground, 오프라인 미전달·재연결 후 수신도 새 코드에서 다시 통과했다. 전용 AVD의 첫 전체화면 안내는 수동으로 닫았다. APK SHA-256 `c6de2d9341c17e727570c4ae3be9f6fbb44c380338fa7e2dd8ec6ad3d5979995`.
- 임의 지연 Native callback과 재연결 실패의 명시적 주입, iOS Player 및 실제 FCM/APNs는 이 시험으로 증명하지 않는다.

## 재연결 실패 주입 추가 시험

- 소스 `ea5e17fcc726f9944ec5e7348d8c26cd8dd473ec`, tracked-clean. 새 전용 Android 에뮬레이터에서 Runner exit 0 (`artifacts/unity-android-push-n3lvsnkx/result.json`).
- 전용 AVD의 Wi-Fi/data 차단·복원 외에도 test-only loopback proxy가 SDK 재연결 시도를 2회 거부했고, 이후 연결 복원과 새 Mock 푸시 수신이 통과했다. background/foreground, 중복·세션 전환·등록 해제도 같은 실행에서 통과했다. 첫 전체화면 안내는 수동으로 닫았다.
- APK SHA-256 `76a5e5f123cea694cc1153a193e01e82cefd620e771f88b6da57312eb7a6121d`. 실제 FCM, 임의 지연 Native callback 주입은 아니다. 강제 종료/pending은 위 PX-T10 별도 실행에서 확인했다.

## 기존 인증·구매 회귀

소스 `8afe5d07551d639d6510af7b736f60dec0b475cc`, tracked-clean에서 기존 Unity Android LOCAL_MOCK 인증·구매 전체 Runner를 새 전용 AVD·DB로 재실행해 exit 0, `artifacts/unity-android-e2e-7001epc_/result.json` PASS. exact-version embedded Unity package cache를 사용했고 첫 전체화면 안내는 수동으로 닫았다. Google 로그인·Play 실결제는 미실행이다.

## 지연된 이전 세션 callback 합성 주입

- 소스 `d2146add76095b7c74b333796732893331659dce`, tracked-clean. 새 전용 Android 36 에뮬레이터의 확장 Push Runner exit 0 (`artifacts/unity-android-push-3n9bo6qw/result.json`).
- 실제 Unity Player에서 B 세션 활성 후 A 세션 이벤트를 **테스트 코드가 합성해** Android transport callback 메서드/큐에 주입했다. Unity ignored counter 증가와 구독자 미전달을 확인했다. 이 주입은 실제 JNI 또는 FCM이 늦게 callback한 사례는 아니다. timeout 후 늦은 응답과 dispose 후 메시지는 별도 managed 단위 시험으로 확인했다.
- 같은 실행에서 background/foreground·실제 AVD 연결 차단/복원·test proxy 재연결 거부 2회·복구·중복 제거·session 전환도 통과했다. 최초 전체화면 안내는 수동으로 닫았다. 테스트 probe 반영 APK SHA-256 `05ef751b06e50044120b27361b0cbb17055bfc57f81c873c13df8d24d3858162`.
