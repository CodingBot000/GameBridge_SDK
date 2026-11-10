# GameBridge SDK 작업 로그

이 파일은 append 중심으로 관리한다. 이전 실패를 삭제하거나 성공으로 덮어쓰지 않는다. 초기 상태에는 실제 개발 기록이 없다.

## 세션 시작 기록 양식

```text
시각(시간대 포함):
세션/모델 설정: 실제 확인 가능한 값만, 추측 금지
시작 Git branch / HEAD:
기존 사용자 변경:
환경·권한 요약:
읽은 계획 범위:
이번 시작 Task / 다음 행동:
```

## Task 기록 양식

아래 블록을 Task 시작 시 추가하고 진행 중 결과를 채운다. 긴 Task는 동일 Task ID의 하위 체크포인트를 추가한다. 상태가 바뀔 때 PROGRESS도 갱신한다.

```text
### [Task ID] 짧은 제목 — 시작 시각
의존 Task 확인:
시작 상태 / 실행 모드:
구현할 작업:
변경 파일:
실제 구현 결과:
실행 명령 (비밀값은 제거):
실행 위치 / toolchain:
종료 코드 / 실행된 테스트·assert 수:
관측 결과:
증거 파일:
남은 오류·미구현·외부 대기:
블로커 ID 및 해소 조건:
커밋 메시지의 Task ID: 현재 커밋 자기 SHA를 여기에 쓰지 않음
다음 Task / 바로 실행할 명령:
종료 또는 체크포인트 시각:
```

## 실제 실행 기록

아직 없음. 아래부터 Codex가 실제 수행한 사실만 추가한다.

### [P00-T01] 시작 — 2026-11-10 Asia/Seoul
- 제공 문서만 존재하며 현재 및 상위 디렉터리는 Git 저장소가 아님. 기존 파일은 사용자 제공 원본으로 보존한다.
- `git status --short --branch` 종료 128: Git 저장소 없음. 기존 branch/HEAD 없음.
- Git identity는 기존 설정 존재. 다음: 계획 전체 확인 및 로컬 Git 초기화.

- `git init` 종료 0; 기존 remote 없이 main 초기화. `git rev-parse --show-toplevel` 종료 0, 작업 디렉터리와 일치.
- 계획 Task 64개와 원장 64행이 각각 유일하고 일치함을 Python 검사 종료 0으로 확인. 기존 제공 문서는 그대로 보존하고 상태 문서만 갱신. `.DS_Store`는 사용자 파일로 추적하지 않음.
- 커밋 직전: P00-T01 문서 및 제공 원본을 명시적으로 stage; 다음 P00-T02 도구 조사.

### [P00-T02] 시작 — 2026-11-10 Asia/Seoul
- 선행 P00-T01 커밋 44fc2bc. 도구 설치 및 실행 가능 여부를 조사한다.

- 도구 조사 Python 실행 종료 0: JDK 21.0.10, Xcode 26.6, Swift 6.3.3, adb 37.0.1, Docker 29.1.3 및 Compose 2.40.3 응답. Gradle 명령 부재. Android API 34–36 및 37.0과 Unity 6000.4.0f1/6000.5.8f1 디렉터리 확인.
- 공식 Android, Spring, Unity 문서 확인. ENV-001: 설치된 Unity가 6.3 LTS가 아니며 라이선스/모듈 미확인. 전체 버전 조합 빌드 미실행이므로 PARTIAL.
- 커밋 직전: TOOLCHAIN, ENVIRONMENT 및 원장/로그 검토. 다음: P00-T03에서 빌드 가능한 조합 확인 후 본 Task 갱신.

### [P00-T03] 시작 — 2026-11-10 Asia/Seoul
- P00-T02 환경 조사는 부분 완료, 빌드 조합 검증은 본 Task와 연계. 최소 프로젝트를 구성한다.

- `swift test --package-path ios` 종료 0: macOS Swift Package 빌드, XCTest 1개 통과. iOS 기기/시뮬레이터, Apple API 및 다른 플랫폼은 검증하지 않았다. Swift Testing의 별도 0건 출력은 성공 시험 수에 포함하지 않는다.
- 현재 VERSION, Swift Package, 비밀·빌드 산출물 ignore 작성. Android/Backend/Unity 및 iOS 앱 구성은 미구현.
- 로컬 Gradle 8.13 배포본을 발견하여 `gradle -p backend wrapper --gradle-version 8.13` 실행, 종료 0. Backend wrapper 생성 성공이나 앱 빌드는 아직 미실행. Android는 JVM core 초기 구성만 존재한다.
- `gradle -p android wrapper --gradle-version 8.13` 종료 0. 이후 로그 갱신을 backend 작업 디렉터리에서 잘못 시도해 Python FileNotFoundError 종료 1; 원장 파일은 손상되지 않았다. Backend `./gradlew build` 진행 중.
- `backend/./gradlew build` 종료 0: Spring Boot 최소 애플리케이션 빌드 성공, 테스트는 NO-SOURCE 0건. DB·API·보안 동작 검증 아님.
- `./android/gradlew -p android build` 종료 0: Kotlin JVM 최소 core 빌드, 테스트 NO-SOURCE 0건. Android AAR/앱 빌드가 아니다.
- 중간 결과 커밋 전: iOS Swift Package, Android JVM core, Backend Spring Boot 최소 골격과 독립 wrapper만 작성됨. Unity, Compose, iOS 앱/프레임워크, Android 앱 및 기능은 미구현. P00-T03은 IN_PROGRESS/PARTIAL로 유지한다.
