# Android 실기기 추가 검증

2026-11-27 KST에 삼성 SM-G975N, Android 12(API 31), arm64-v8a에서 실행했다. USB ADB와 에뮬레이터 플래그 0을 확인했다. SDK는 v0.1.2-dev이며 버전 교체의 시작 앱은 v0.1.1-dev다. [이전 실기기 기본 검증](android-physical-local-mock-20261127.md)

| 항목 | 실행 경로 | 결과 |
| --- | --- | --- |
| 이전 버전 위 덮어 설치 | Unity Player, LOCAL_MOCK | **PASS.** 앱 데이터 유지, 기존 세션과 미완료 구매 복구, 로그아웃 뒤 복원 차단. 지급 원장 1건·100코인. |
| 로그의 개인정보 노출 검사 | Unity Android 콜백, 앱 PID logcat, 시험 Backend 로그 | **PASS.** 합성 이메일·전화번호가 공개 콜백 결과와 검사한 로그에 노출되지 않았다. 시험 자격값·토큰 패턴도 0건이다. |
| 모의 푸시 | Unity Player, LOCAL_MOCK SSE | **PASS.** 등록·수신, 중복 억제, 복귀, 재연결, 등록 해제와 세션 교체 후 이전 이벤트 차단. 종료 시 푸시 토큰 0개. |
| Google 실계정 로그인 | Native·Unity, HTTPS PLATFORM_SANDBOX | **사용자 계정 선택 대기.** 설치·시험 서버 연결·계정 선택 창·취소는 두 앱에서 확인했다. |

## 덮어 설치

두 APK의 applicationId는 com.gamebridge.sdk.physicalupgrade이고 서명 인증서는 동일하다. Android APK의 versionCode는 1에서 102로 증가했다. Player가 보고한 SDK 버전은 0.1.1-dev에서 0.1.2-dev로 바뀌었다. 이전 APK에서 구매가 서버에 기록된 뒤 첫 응답을 유실시켰다. adb install -r 뒤 새 프로세스에서 기존 세션을 복원했고 미완료 구매 1건을 회수했다. 재동기화에서 추가 회수는 0건이었다. 서버 구매 검증은 2회, 최종 지급은 1건·100코인이다.

## 개인정보 로그 검사와 모의 푸시

개인정보 시험은 합성 데이터를 Unity Android 콜백으로 주입했다. 공개 이벤트 payload, 해당 앱 프로세스 로그, 별도 Backend 로그를 대조했다. GB_PII_PROBE PASS와 GB_MOCK_REDACTION PASS를 각 1회 관측했다. 구매 원장은 1건·100코인이다.

푸시는 전용 앱 연결의 TCP 프록시에서 연결을 끊고 재접속 1회를 거부한 뒤 복구했다. 같은 메시지 ID를 두 번 발송했을 때 Unity 메인 스레드 수신은 1회였다. 연결이 끊긴 동안 보낸 메시지는 전달되지 않았고, 재접속 뒤 보낸 새 메시지가 도착했다. A 로그아웃과 B 세션 등록 뒤 이전 세션 발송은 403이었고, 합성 지연 콜백도 차단됐다. 마지막 로그아웃 뒤 DB의 푸시 토큰은 0개다.

## Google 실계정 로그인 준비와 취소

기존 Google Cloud Android OAuth 등록의 applicationId와 APK 서명에 맞춘 v0.1.2-dev Native·Unity 시험 빌드를 설치했다. localhost 이름과 시험 CA를 검증하는 별도 HTTPS Sandbox를 USB로 연결했다. Native와 Unity 모두 Google 계정 선택 창을 열고 뒤로 가기에서 CANCELED를 확인했다. Native의 재시도는 테스트 계정을 선택하기 전에 challenge 유효시간이 끝났다. 최종 DB 집계는 Google challenge 3건, 소비 0건, Google identity 0건, SDK 세션 0건이다.

실계정 로그인 완료, 앱 재시작 후 Google 세션 복원, 실제 계정의 SDK 로그아웃은 사용자 계정 선택 대기 상태다. 이전 Android API 34 AVD의 v0.1.1-dev 실계정 결과는 해당 실행의 독립 근거로 보존한다. [이전 Android Google 실계정 증거](android-google-live-20261125.md)

## 원본 기록

로컬 실행 폴더 artifacts/android-physical-followup-20261127.tURKWe에 upgrade-result.json, pii-result.json, push-result.json, google-native-result.json, google-unity-result.json을 보존했다. 덮어 설치의 전후 Player, 개인정보 검사, 푸시의 결과 마커와 각 시험 APK 체크섬도 같은 폴더에 있다. 본문은 검사한 한 기기와 시나리오의 범위를 나타낸다.
