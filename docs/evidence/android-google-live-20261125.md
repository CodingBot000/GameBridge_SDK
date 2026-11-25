# Android Google 실계정 인증 검증

2026-11-25 KST. PR #14를 병합한 main은 `949d4e06a38eaa35a355cadd4d1e91236c04ac0c`다. 개발자용 SDK `0.1.1-dev`의 Batch B 시험 APK를 Android API 34 전용 Google APIs AVD에서 사용했다. Backend는 인증서를 검증하는 로컬 HTTPS Sandbox와 전용 PostgreSQL DB를 사용했다. Google 계정 등록, 계정 선택과 동의는 사용자 조작으로 완료했다.

| 검증 | Native | Unity |
| --- | --- | --- |
| 시험 앱 | `com.gamebridge.sample` | `com.gamebridge.sdk.googleoauth.androidtest` |
| 인증 화면 취소 | `CANCELED`, 인증 요청 미소비, 새 세션 0개 | `CANCELED`, 인증 요청 미소비, 새 세션 0개 |
| 재시작 없는 재시도 및 실제 로그인 | 계정 선택 후 로그인 성공, 첫 전용 세션 발급 | 계정 선택 후 로그인 성공, 기존 Google identity에 별도 세션 발급 |
| 프로세스 종료·재실행 후 복원 | Google 화면 없이 동일 세션 복원, 신규 인증 요청·세션 0개 | Google 화면 없이 동일 세션 복원, 신규 인증 요청·세션 0개 |
| 로그아웃 후 복원 확인 | 서버에서 해당 세션만 폐기, `No saved session.` | 서버에서 해당 세션만 폐기, `RESTORE NO_SESSION` |

최종 DB 집계는 Google identity 1개, 소비된 인증 요청 2개, 발급 세션 2개, 폐기 세션 2개다. 각 앱의 세션 행과 사용자 행은 로컬에서 비식별 별칭으로 비교했다. Unity는 로그인·취소·복원·로그아웃에 걸쳐 C# URL 이벤트 0건을 기록했다. 로그인 및 재실행 프로세스 로그에서 JWT, OAuth 토큰·코드 파라미터, Bearer 패턴은 발견하지 못했다. 원문 로그와 계정 데이터는 Git에 저장하지 않았다.

초기 준비 시 ADB reverse 연결이 없어 Native 요청은 `NETWORK_UNAVAILABLE`이었다. 연결 복구 후 Google 계정을 등록하기 전 요청은 `AUTH_FAILED`로 끝났고 세션은 생성되지 않았다. Android OAuth 클라이언트 두 개와 AVD 계정 등록을 마친 후 위 실계정 시험을 실행했다.

- Native APK SHA-256 `30fa264067c9820120e2044bc7190e42c05e03a192f57097fbb66fab69c26dd8`
- Unity APK SHA-256 `211fdd0225564a2a9b165f07175fbbb1b340c271cd5b266a78fe14a54b422a29`
- 통합 근거는 [Batch B 호환성 검증](batch-b48-compatibility.md) 및 [PR #14 필수 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45578953794)를 참조한다.
- 실제 토큰 갱신·재사용, Android 실기기 시험, 스토어 및 릴리스 판정은 이 계정 시험의 실행 범위에 포함되지 않는다.
