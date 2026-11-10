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
- 커밋 전 `git diff --cached --check`는 생성된 Gradle Windows wrapper의 CRLF를 trailing whitespace로 감지하여 실패했다. 쉘이 후속 commit을 실행했으므로 해당 실패를 정정하기 위해 `.gitattributes`에 Windows batch의 CRLF 속성을 명시하고 재검사한다.
- `eol=crlf`만으로 과거 diff 검사는 종료 2로 계속 실패; `whitespace=cr-at-eol`을 추가한 뒤 `git diff --check HEAD^ HEAD` 종료 0. 커밋 전 수정사항 재검토.

### [P00-T03] 재개 — 2026-11-10 Asia/Seoul
- `git status --short --branch` 종료 0, main 작업 트리 깨끗함. 6a95e34 이후 Android 앱, iOS 앱·프레임워크, Unity, Compose를 이어서 구성한다.
- `unity status --format json --non-interactive` 종료 6: Pipeline 연결된 Editor 인스턴스 없음. 설치된 Editor 실행·라이선스 여부는 별도 검증한다.
- `unity projects create ... --no-initial-commit` 종료 2: 해당 옵션은 VCS 지정 시에만 허용. VCS 없이 다시 시도한다.
- `unity projects create Demo ... --no-cloud --non-interactive` 종료 6: 기본 템플릿을 결정할 수 없음. 명시적 템플릿 확인 후 재시도한다.
- `unity templates list --format json` 종료 2 (Editor 지정 필요); `--editor 6000.5.8f1` 지정 조회는 성공하고 built-in 템플릿을 확인했다.
- `unity projects create Demo --editor-version 6000.5.8f1 --template com.unity.template.3d --no-cloud --non-interactive --format json` 종료 6: Editor 종료 198, 라이선스 확인 실패로 import 전 중단. ENV-002로 기록; 사용자 계정·라이선스는 변경하지 않는다. Unity 프로젝트 생성/검증은 대기.
- `./android/gradlew -p android :sample-app:assembleDebug` 종료 1: Android SDK 경로 환경변수 또는 local.properties가 지정되지 않음. 설치 확인된 SDK 경로를 해당 명령에만 제공해 재시도한다.
- `ANDROID_HOME="$HOME/Library/Android/sdk" ./android/gradlew -p android :sample-app:assembleDebug` 종료 0: Compose 최소 앱 APK 빌드. 실행·기기·SDK 기능 검증은 미실행. SDK XML 버전 경고 및 네이티브 라이브러리 strip 경고 관측.
- `GAMEBRIDGE_DB_PASSWORD=local-test-only docker compose -f infra/compose.yaml config --quiet` 종료 0: Compose 설정 구문 검증만 수행. DB 기동·migration 미검증. Unity 패키지 메타데이터, 재생성 스크립트, SwiftUI 샘플 및 XcodeGen 프로젝트 명세 작성.
- Unity 실패 후 `unity/Demo`에 템플릿의 일부 파일이 남은 것을 확인했다. 정상 생성·import 성공으로 간주하지 않고 삭제하지 않았다. `xcodegen`은 PATH에 없음; iOS Xcode 명세는 미생성·미검증이며 framework target도 아직 미구현.
- 커밋 전: P00-T03 부분 골격과 증거를 분리해 stage. Unity 미완성 Demo와 로그·빌드 결과는 포함하지 않는다.

### [P00-T04] 시작 — 2026-11-10 Asia/Seoul
- P00-T03은 플랫폼 환경 대기로 미완료. 원장 검사 및 기존 빌드 명령 진입점은 독립적으로 작성 가능하므로 진행한다. 아직 없는 기능은 성공으로 표시하지 않는다.
- `python3 scripts/verify-progress.py` 종료 0: 현재 계획·원장·작업 로그·설정 참조 검사 통과. 제품 검증은 아니다. 음성 검사는 아직 미실행.
- Python 격리 음성 검사 종료 0: 누락 Task, 증거 없는 PASS, 불법 상태 각각 거부(3/3). 원본 원장 수정 없이 문자열 사본으로 검사.
- `bash scripts/doctor.sh` 종료 0: 주요 명령 및 Docker 엔진/SDK 디렉터리 존재 확인. 라이선스·서명·실기기 작동 검사는 포함하지 않으므로 도구 가용성만 의미한다.
- `bash scripts/build-android.sh --mock` 종료 1: Mock Provider 미구현을 명시적으로 보고. iOS/Unity 빌드 진입점도 현재 미구현 오류를 반환한다. 도구 부재와 실제 빌드 실패 분기 및 준비된 앱의 연결은 후속 작업이 필요하다.
- 커밋 직전: P00-T04 검사기와 초기 진입점만 stage; 해당 Task는 IN_PROGRESS/PARTIAL 유지.

### [P00-T05] 시작 — 2026-11-10 Asia/Seoul
- P00-T03은 일부 환경 대기. 모드·설정 검증은 독립 개발하되 기능과 Mock은 별도 미완료로 유지한다.
- `swift test --package-path ios` 종료 0: 설정 타입 컴파일 및 기존 버전 테스트 1건 통과; 설정 동작 자체는 아직 검사하지 않았다.
- `swift test --package-path ios` 종료 0: XCTest 3건 중 설정 검사 2건(명시적 오프라인/Mock, Sandbox cleartext·비밀값 노출 거부) 통과. macOS 테스트이며 iOS 앱 실행이나 Provider 검증이 아니다.
- `./android/gradlew -p android :sdk-core:build` 종료 0: Kotlin 설정 타입 컴파일 성공, 테스트 0건. 구성 검증 실행·Backend profile 격리·C# 설정·실제 Provider와 Mock 연결은 미완료.
- 커밋 직전: 설정 타입·예제·Swift 동작 확인만 포함. P00-T05는 IN_PROGRESS/PARTIAL 유지.
- P00-T05 계속: Backend에서 명시적인 단일 환경 선택을 강제하고 개발 profile 혼합을 차단한다.
- `./backend/gradlew -p backend test` 종료 0; XML 결과 테스트 2건, 실패 0. 단일 mode 허용 및 누락/혼합 거부를 검증했다. 아직 서버 route, Mock verifier 또는 실제 Provider는 구현되지 않았다.
- `./android/gradlew -p android :sdk-core:test` 종료 1: Kotlin target 17과 Java target 21 불일치로 컴파일 중단. Java compile target을 17로 맞춰 재검증한다.
- Java source/target 17 정렬 후 `./android/gradlew -p android :sdk-core:test` 종료 0. XML: 테스트 2건, 실패 0. 오프라인/Mock 설정 및 Sandbox 비보안 URL 거부를 확인. Android 기기 실행은 아님.
- 커밋 직전: Backend profile guard와 Kotlin 테스트를 포함한다. Unity 설정, 실 Provider/Mock 연결, 전체 configuration fields는 여전히 미구현으로 P00-T05 PARTIAL 유지.
- P00-T05 계속: Unity 공통 설정에 명시 모드와 URL 검증을 추가한다. Editor 실행은 ENV-002 때문에 확인할 수 없다.
- `command -v dotnet` 종료 1: .NET CLI 없음. Unity Editor도 ENV-002로 실행되지 않아 C# 설정 소스는 REVIEW_ONLY, 컴파일·동작 미검증이다.
- 커밋 직전: Unity Runtime 설정과 asmdef만 stage. 자동 생성 .meta와 Unity import는 미실행.
