# Android 실기기 LOCAL_MOCK 검증

2026-11-27 KST에 삼성 SM-G975N, Android 12(API 31), arm64-v8a에서 실행했다. USB ADB와 기기 속성 ro.kernel.qemu=0을 확인했다. 기준 SDK는 v0.1.2-dev(태그 5c899be)이며 Native와 Unity는 각각 별도 LOCAL_MOCK Backend 및 PostgreSQL 데이터베이스에 USB reverse로 연결했다.

| 확인 항목 | Native 샘플 | Unity 6000.5.8f1 Player |
| --- | --- | --- |
| APK 설치와 실행 | PASS | PASS |
| 모의 로그인과 100코인 지급 | PASS | PASS |
| 백그라운드에서 같은 프로세스로 복귀 | PASS. 잔액 화면 유지 | PASS. Pause와 Resume 콜백 확인 |
| 프로세스 종료·재실행과 세션 복원 | PASS. 기존 세션과 100코인 잔액 복원 | PASS. 기존 세션과 미완료 구매 복구 |
| 로그아웃 후 복원 차단 | PASS. 화면에 No session 표시 | PASS. 복원 차단과 SDK 종료, 대기 요청 0개 |
| 최종 DB | 지급 원장 1건·100코인, 폐기 세션 1개, 활성 세션 0개 | 지급 원장 1건·100코인, 폐기 세션 1개, 활성 세션 0개 |

Unity에서는 서버가 구매를 기록한 직후 응답 한 건을 시험 프록시에서 유실시켰다. 재시작 뒤 구매 검증 요청이 한 번 더 들어왔고 미완료 구매 1건을 회수했다. 두 번째 동기화에서 추가 회수 0건, 지급 원장과 잔액은 각각 1건·100코인이었다. 새 프로세스의 Unity 결과와 Backend 로그, DB 집계를 대조했다.

Native는 v0.1.2-dev 후보의 서명된 Debug 샘플을 사용했다. Unity는 같은 SDK staging을 포함하고 USB loopback을 사용하는 별도 테스트 앱을 빌드했다. 출고 SDK 소스와 staging 내용은 기존 v0.1.2-dev 기준이다.

| 실행 입력 | SHA-256 |
| --- | --- |
| Native 샘플 APK | 5522a3b5a9f070260fac9f3669c13587c3d6e7d36acbe3367ab6f6d1423a2447 |
| Unity 실기기 검증 APK | e1373a2989371a169efed33e22107018f1a4b2370ade3ebfb76411c133fd5fed |
| Unity UPM staging 체크섬 목록 | 441cfe72df4b23a55a4474b6cdaa0a7fd32273de191d7b5270d541cd60f6d15b |
| 로컬 Backend JAR | f7291fa7fea218494f73bcdc16d00abd7ffe213c3fe1e46c744e31d72a0d2959 |

로컬 원본은 artifacts/android-physical-20261127.t5k0SV의 native-result.json, unity-result.json, unity-prepare-markers.log, unity-recover-markers.log에 보존했다. 시험 범위는 이 기기와 OS의 LOCAL_MOCK이다. Google 실계정, Play 결제, FCM 원격 푸시 및 Android 13 이상 알림 권한 UI는 미실행이다.
