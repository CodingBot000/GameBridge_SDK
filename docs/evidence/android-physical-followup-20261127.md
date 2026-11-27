# Android 실기기 추가 검증

2026-11-27 KST에 삼성 SM-G975N, Android 12(API 31), arm64-v8a에서 실행했다. USB ADB와 에뮬레이터 플래그 0을 확인했다. SDK는 v0.1.2-dev이며 버전 교체의 시작 앱은 v0.1.1-dev다. [이전 실기기 기본 검증](android-physical-local-mock-20261127.md)

| 항목 | 실행 경로 | 결과 |
| --- | --- | --- |
| 이전 버전 위 덮어 설치 | Unity Player, LOCAL_MOCK | **PASS.** 앱 데이터 유지, 기존 세션과 미완료 구매 복구, 로그아웃 뒤 복원 차단. 지급 원장 1건·100코인. |
| 로그의 개인정보 노출 검사 | Unity Android 콜백, 앱 PID logcat, 시험 Backend 로그 | **PASS.** 합성 이메일·전화번호가 공개 콜백 결과와 검사한 로그에 노출되지 않았다. 시험 자격값·토큰 패턴도 0건이다. |
| 모의 푸시 | Unity Player, LOCAL_MOCK SSE | **PASS.** 등록·수신, 중복 억제, 복귀, 재연결, 등록 해제와 세션 교체 후 이전 이벤트 차단. 종료 시 푸시 토큰 0개. |
| Google 실계정 로그인 | Native·Unity, HTTPS PLATFORM_SANDBOX | **Native·Unity PASS.** 실계정 로그인, 취소, 재시작 복원, 로그아웃과 복원 차단을 확인했다. |

## 덮어 설치

두 APK의 applicationId는 com.gamebridge.sdk.physicalupgrade이고 서명 인증서는 동일하다. Android APK의 versionCode는 1에서 102로 증가했다. Player가 보고한 SDK 버전은 0.1.1-dev에서 0.1.2-dev로 바뀌었다. 이전 APK에서 구매가 서버에 기록된 뒤 첫 응답을 유실시켰다. adb install -r 뒤 새 프로세스에서 기존 세션을 복원했고 미완료 구매 1건을 회수했다. 재동기화에서 추가 회수는 0건이었다. 서버 구매 검증은 2회, 최종 지급은 1건·100코인이다.

## 개인정보 로그 검사와 모의 푸시

개인정보 시험은 합성 데이터를 Unity Android 콜백으로 주입했다. 공개 이벤트 payload, 해당 앱 프로세스 로그, 별도 Backend 로그를 대조했다. GB_PII_PROBE PASS와 GB_MOCK_REDACTION PASS를 각 1회 관측했다. 구매 원장은 1건·100코인이다.

푸시는 전용 앱 연결의 TCP 프록시에서 연결을 끊고 재접속 1회를 거부한 뒤 복구했다. 같은 메시지 ID를 두 번 발송했을 때 Unity 메인 스레드 수신은 1회였다. 연결이 끊긴 동안 보낸 메시지는 전달되지 않았고, 재접속 뒤 보낸 새 메시지가 도착했다. A 로그아웃과 B 세션 등록 뒤 이전 세션 발송은 403이었고, 합성 지연 콜백도 차단됐다. 마지막 로그아웃 뒤 DB의 푸시 토큰은 0개다.

## Google 실계정 로그인 준비와 취소

기존 Google Cloud Android OAuth 등록의 applicationId와 APK 서명에 맞춘 v0.1.2-dev Native·Unity 시험 빌드를 설치했다. localhost 이름과 시험 CA를 검증하는 별도 HTTPS Sandbox를 USB로 연결했다. Native와 Unity 모두 Google 계정 선택 창을 열고 뒤로 가기에서 CANCELED를 확인했다. Native의 재시도는 테스트 계정을 선택하기 전에 challenge 유효시간이 끝났다. 최종 DB 집계는 Google challenge 3건, 소비 0건, Google identity 0건, SDK 세션 0건이다.

### 사용자 계정 선택 후 재개

localhost HTTPS Sandbox와 USB reverse를 다시 연결했다. Native에서 사용자가 계정을 선택한 뒤 로그인했다. 앱 프로세스를 바꿔도 동일 세션이 복원됐고, 로그인 challenge나 세션은 추가 발급되지 않았다. 로그아웃 뒤 서버에서 세션을 폐기했고 다시 실행한 앱은 No saved session을 표시했다. 로그인과 재실행의 앱 로그를 검사해 이메일·OAuth 토큰 패턴 0건을 확인했다.

첫 재개에서 Unity 계정 선택 요청은 선택 전에 만료됐다. 이 실행에서 서버는 Google challenge 2건 중 Native의 1건을 소비했다. 세션은 1개 발급·1개 폐기·활성 0개였다.

### Unity 실계정 검증 완료

새 localhost HTTPS Sandbox에서 사용자가 지정한 테스트 계정을 Unity 앱의 Google 선택 창에서 골랐다. 로그인과 새 프로세스에서의 기존 세션 복원이 통과했다. 복원 과정에서 인증 요청이나 세션은 추가 발급되지 않았다. 로그아웃 후 앱은 RESTORE NO_SESSION을 기록했다. 이 독립 실행의 최종 DB는 challenge 1건 소비, Google identity 1개, 세션 1개 발급·1개 폐기·활성 0개다. Unity로 전달된 원본 URL 이벤트와 검사한 앱 로그의 이메일·OAuth 토큰 패턴은 각각 0건이다.

이전 Android API 34 AVD의 v0.1.1-dev 실계정 결과는 해당 실행의 근거로 보존한다. [이전 Android Google 실계정 증거](android-google-live-20261125.md)

## 원본 기록

로컬 실행 폴더 artifacts/android-physical-followup-20261127.tURKWe에 upgrade-result.json, pii-result.json, push-result.json, google-native-result.json, google-unity-result.json과 재개 실행의 google-native-resumed-result.json과 google-unity-resumed-result.json을 보존했다. Unity 완료 결과는 google-unity-physical-completion-result.json에 있다. 덮어 설치의 전후 Player, 개인정보 검사, 푸시의 결과 마커와 각 시험 APK 체크섬도 같은 폴더에 있다. 본문은 검사한 한 기기와 시나리오의 범위를 나타낸다.
