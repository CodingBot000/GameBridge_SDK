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

### [P01-T01] 시작 — 2026-11-10 Asia/Seoul
- P00-T05가 미완료이나 계획에 확정된 공통 오류·모델 계약은 환경 격리 구현에 의존하지 않아 독립적으로 작성한다. 전체 Task 완료 판정은 선행 작업 및 언어 간 검증을 기다린다.
- `python3 -m json.tool contracts/error-codes.json` 종료 0: 오류 registry JSON 구문 확인만 수행. 계약 완성 및 언어별 DTO 검증은 미실행.
- `python3 -m json.tool contracts/models.schema.json` 종료 0: JSON 구문 확인. UserProfile, StoreProduct, SdkError, EntitlementSnapshot만 명세; 다른 모델·DTO·fixture 및 schema 검증 미구현.
- 커밋 직전: 공통 계약의 부분 결과만 포함. P01-T01은 IN_PROGRESS/PARTIAL 유지.

- 체크포인트: P00-T02~T05와 P01-T01 미완료. Unity 생성 실패로 남은 `unity/Demo/`와 검사기 실행으로 생긴 `scripts/__pycache__/`는 미추적이며 삭제하지 않았다. 다음: P01-T01 모델·DTO·fixture 및 P00 잔여 작업. 실제 Provider, Mock 경로, P02~P11과 최종 보고서는 미구현.

### [P01-T01] 재개 — 2026-11-10 Asia/Seoul
- `git status --short --branch` 종료 0: 이전에 기록한 Unity 미완성 프로젝트와 Python 캐시만 미추적. 기존 파일을 보존하고 공통 모델·fixture 및 Native 직렬화를 계속한다.
- `./android/gradlew -p android :sdk-core:test` 종료 0: 공통 fixture의 한글·emoji·큰 정수·null 왕복과 필수 nullable 필드 누락 및 알 수 없는 enum 거부 확인. 전체 테스트 수는 XML에 기록된 결과를 확인한다.
- `swift test --package-path ios` 종료 0: XCTest 5건 중 모델 fixture 2건 통과. 공통 fixture 왕복, nullable 필드 누락·unknown enum 거부를 macOS에서 확인. iOS 기기 실행 아님. Kotlin XML은 전체 4건(모델 2, 설정 2), 실패 0.
- `python3 -c import jsonschema` 종료 1: 로컬 Python에 schema 검증 라이브러리가 없다. 임시 환경에서 설치해 검증을 시도하며 프로젝트 제품 의존성으로 추가하지 않는다.
- 임시 venv에서 `jsonschema==4.25.1` 설치 종료 0. Draft 2020-12 schema 자체 검사와 fixture 4종 유효성 및 각 필수 필드 누락 거부 검사 종료 0. 이 확인은 전체 모델 완성이나 플랫폼 실행을 뜻하지 않는다.
- Unity C# 모델 필드를 작성했지만 Newtonsoft 직렬화 adapter, 필수 필드 검증, Editor 컴파일·fixture 왕복은 미구현/미실행이다(ENV-002). 전체 모델과 외부 사용 API도 미완료.
- 커밋 직전 `python3 scripts/verify-progress.py` 종료 0. Kotlin/Swift에서 테스트된 부분과 미검증 C# 모델을 포함하며 P01-T01을 IN_PROGRESS/PARTIAL로 유지한다.

### [P01-T02] 시작 — 2026-11-10 Asia/Seoul
- P01-T01은 부분 완료. 계획에 확정된 Bridge envelope와 operation 검증은 독립적으로 작성하되 통합 완료로 판정하지 않는다.
- `/tmp/gamebridge-schema-venv/bin/python` Draft 2020-12 검사 종료 0: Bridge schema와 정상 fixture 3건, 오류 없는 실패·미허용 operation·구버전 fixture 3건의 거부를 확인. 길이 제한·요청 상관관계는 schema 외 런타임 검증 필요.
- `./android/gradlew -p android :sdk-core:test` 종료 0: Bridge parser 시험 2건을 포함한 테스트 통과. 정상 요청/보류 응답 및 잘못된 버전·operation·오류 응답·다른 요청 ID·잘못된 UTF-8·크기 초과를 확인. Swift/C# 파서와 Native transport는 미구현.
- `swift test --package-path ios` 종료 0: XCTest 7건 중 Bridge 검사 2건 통과. 잘못된 UTF-8, 크기, 버전, operation, 실패 envelope 및 다른 request ID 거부 확인. macOS 결과이며 C ABI·iOS 기기 왕복은 미검증.
- 커밋 직전: Bridge schema, fixture, Kotlin/Swift 파서와 로컬 테스트만 포함. C# 파서·이벤트 전체 계약·실제 transport 미구현이므로 P01-T02는 IN_PROGRESS/PARTIAL.

### [P02-T01] 시작 — 2026-11-10 Asia/Seoul
- P00-T03/P01-T01이 일부 미완료이나 독립적인 PostgreSQL·Flyway 기동 기반을 구현한다. 기존 개인 DB는 사용하지 않는다.
- `./backend/gradlew -p backend test` 종료 0: 기존 profile 단위 시험 2건 통과, 신규 DB migration/HTTP 실행은 아직 미검증.
- `lsof -nP -iTCP:54329 -sTCP:LISTEN` 종료 1: 기동 전 해당 포트 listener 없음. `docker compose -p gamebridge-sdk-local -f infra/compose.yaml up -d --wait` 종료 0: 전용 PostgreSQL 컨테이너 healthy. 전용 named volume은 보존하며 다른 서비스 데이터는 건드리지 않았다. 개발 전용 테스트 비밀번호를 해당 명령 환경에만 사용.
- `SPRING_PROFILES_ACTIVE=local-mock ... ./backend/gradlew -p backend bootRun` 실행 중: 로그에서 PostgreSQL 17.6 연결과 Flyway V1 최초 적용 및 127.0.0.1:18080 서버 기동 관측. HTTP health와 재시작 확인은 이어서 실행한다.
- `curl --fail --silent --show-error -i http://127.0.0.1:18080/health` 종료 0: HTTP 200, UP 및 X-Request-Id 확인. readiness/인증·구매 검증은 아님.
- 테스트 서버를 Ctrl-C로 종료(130), 같은 전용 DB에서 재기동해 migration 멱등성을 확인한다.
- 같은 전용 DB에서 `bootRun` 재실행: Flyway가 migration 1건 검증 후 schema version 1, 추가 적용 불필요로 보고하고 서버 기동. 현재 프로세스 실행 중; 종료 코드는 아직 없음.
- 재기동 후 `curl --fail --silent --show-error http://127.0.0.1:18080/health` 종료 0, UP 확인. `scripts/run-demo-backend.sh`와 volume 보존 정책 작성; 스크립트 자체는 아직 실행 전.
- 재기동 테스트 서버 Ctrl-C 종료 130. 표준 실행 스크립트에서 같은 DB를 사용해 재시작을 확인한다.
- `GAMEBRIDGE_DB_PASSWORD=<local-test> bash scripts/run-demo-backend.sh` 실행: 전용 DB healthy 확인 후 local-mock 서버 기동 및 migration up-to-date 로그 관측. 스크립트는 서버 프로세스로 유지되므로 아직 종료 코드 없음.
- 스크립트로 기동한 서버의 `curl --fail --silent --show-error http://127.0.0.1:18080/health` 종료 0: UP. 단순 health만 확인했다.
- 스크립트 foreground 서버를 Ctrl-C로 종료(130). 전용 DB는 데이터 volume을 보존하고 컨테이너만 정지한다.
- `docker compose -p gamebridge-sdk-local -f infra/compose.yaml stop` 종료 0. 전용 volume과 데이터는 삭제하지 않았다.
- 커밋 전: local DB·migration·health만 검증. 요청 입력 검증과 오류 매핑 완성, 인증·구매·푸시 및 실제 Provider는 아직 미구현이므로 P02-T01은 PARTIAL 유지.
- P02-T01 계속: 예측 가능한 입력 실패의 공통 오류 응답을 추가하고 requestId가 응답 본문에도 일치하는지 확인한다.
- `./backend/gradlew -p backend test` 종료 0: 기존 profile 2건과 MockMvc 입력 오류·requestId 검사 1건 통과(유효성 실패 및 JSON 형식 오류 2개 입력). 공통 예외 처리에서 원문 요청을 반환하지 않음. 실 HTTP 인증·구매 endpoint는 아직 없음.
- 커밋 전: HTTP 입력 오류 처리와 검증만 포함. DB schema의 전체 계약 및 추가 endpoint 검증은 후속 작업으로 남아 P02-T01 PARTIAL 유지.

### [P02-T02] 시작 — 2026-11-10 Asia/Seoul
- P02-T01 DB 기동과 schema는 부분 검증됨. P01-T05 secure storage는 미완료이나 서버의 독립적 세션 구현과 로컬 검증을 진행한다. local-mock 전용 접근키는 사용자 환경 변수로 공급하고 실 Provider와 구분한다.
- `./backend/gradlew -p backend test` 종료 0: 신규 세션 코드가 컴파일되고 기존 테스트 3건 통과. 세션 통합·보안 검증은 아직 실행 전이며 기능 완료로 보지 않는다.
- `./backend/gradlew -p backend test` 재실행 종료 0: 상태 예외 매핑과 filter 중복 등록 방지 추가 후 기존 3건 통과. DB 통합 시험 미실행.
- 전용 Compose DB `up -d --wait` 종료 0, healthy. 기존 데이터를 삭제하지 않고 로컬 인증 흐름 검증에 사용한다.
- local-mock 서버가 전용 DB에 연결하여 기동. Spring Security가 사용하지 않는 임시 기본 사용자 설정을 자동 생성하는 경고를 관측했으며 이를 제거한 뒤 재검증할 예정이다. 테스트 세션 토큰은 로그에 남기지 않는다.
- Python HTTP smoke 종료 0, local-mock에서 10개 assertion 통과: 무인증/잘못된 개발키 거부, A/B 사용자 분리, me, refresh 회전, 이전 refresh 재사용 거부 및 family 폐기, logout 후 접근 차단. 토큰·키 원문은 증거에 기록하지 않음. 실제 Google/Apple 인증이 아니다. 반복 logout 멱등성과 sandbox 차단은 미검증.
- 기본 Spring Security 사용자 자동 생성을 제외한 뒤 `./backend/gradlew -p backend test` 종료 0, 기존 3건 통과. 해당 변경 반영 후 실제 서버 재기동·Sandbox 분리 확인은 이어서 수행한다.
- local-mock 테스트 서버 Ctrl-C 종료 130. Sandbox 프로필 차단 시험은 기존 local-mock과 별도 DB로 분리한다.
- 전용 PostgreSQL에서 `gamebridge_sandbox_verify_20261110` DB 부재를 조회(종료 0, count 0)하고 별도 검증 DB 생성(종료 0). 테스트 데이터는 보존한다.
- 별도 빈 DB로 sandbox 프로필 서버 기동 및 V1 migration 적용 관측. 기본 사용자 자동 생성 경고는 다시 나타나지 않음. 실제 외부 인증 설정이나 검증이 아닌 프로필 격리 시험이다.
- 별도 DB의 sandbox 서버에 개발키를 포함해 `POST /v1/dev/auth` 호출: HTTP 404, Python assertion 종료 0. 개발 Mock route가 sandbox에 등록되지 않음을 확인했으며 실제 Sandbox Provider 시험은 아니다.
- Sandbox 검증 서버 Ctrl-C 종료 130. 이제 logout 재호출을 멱등 처리하고 일반 API의 폐기 토큰 차단과 함께 검증한다.
- logout 재호출에서만 아직 만료되지 않은 폐기 access token을 인식하도록 보정. `./backend/gradlew -p backend test` 종료 0, 기존 단위 시험 3건 통과; 실제 HTTP 재호출은 아직 미확인.
- 변경된 서버를 local-mock으로 재기동하고 migration up-to-date 및 서버 시작 확인. 재사용 가능한 인증 smoke를 추가했고 아직 실행 전이다.
- `GAMEBRIDGE_DEV_AUTH_KEY=<local-test> python3 scripts/smoke-auth-local.py` 종료 0: local-mock HTTP/DB assertion 11건 통과(재호출 logout 포함). 실제 외부 인증 아님.
- local-mock smoke 서버를 Ctrl-C 종료 130. 전용 DB 컨테이너는 데이터 보존 상태로 정지한다.
- 전용 Compose DB `stop` 종료 0, named volume 보존. local-mock에는 A/B 사용자 및 테스트 session 기록이 남아 있다. 분리 sandbox 시험 DB도 같은 전용 volume에 남아 있다.
- 커밋 전: 인증·세션의 제한된 Mock 경로와 11개 smoke 확인. 속도 제한, 실제 identity 검증, Native 보안 저장소와 전체 contract는 미구현이므로 P02-T02는 IN_PROGRESS/PARTIAL로 유지한다.

### [P02-T03] 시작 — 2026-11-10 Asia/Seoul
- P02-T02는 속도 제한 및 Native 연동이 남아 PARTIAL. 인증된 Mock 사용자를 기준으로 구매 검증·원장 경로를 작성하며 실제 스토어 거래와 격리한다.
- `./backend/gradlew -p backend test` 종료 0: 신규 Mock proof 검사 1건 포함 전체 테스트 4건 통과. 사용자·상품 불일치와 실제처럼 보이는 namespace를 거부한다. 이는 조작 가능한 local-mock 증명이며 실제 스토어 proof 검증이 아니다.
- 커밋 직전: Mock verifier만 추가. 구매 API·DB 거래 지급·중복 방지·스토어 최종화는 아직 없어 P02-T03 IN_PROGRESS/PARTIAL로 유지한다.

### [P00-T05] 환경 격리 보강 — 2026-11-10 Asia/Seoul
- Mock session DB를 Sandbox에 잘못 지정하면 기존 token을 조회할 수 있는 위험을 발견했다. 실제 설정 전에도 방지하도록 DB별 환경 소유권을 고정하고 충돌 기동을 차단한다.
- `./backend/gradlew -p backend test` 종료 0: 환경 guard 코드 컴파일 및 기존 4건 통과. DB별 profile 충돌 방지는 실제 기동 시험 전이다.
- `scripts/run-demo-backend.sh` local-mock 기동: 전용 DB에 V2 environment marker migration 적용 후 서버 시작 관측. 프로세스는 아직 실행 중이며 종료 코드는 없다.
- V2 적용 후 `python3 scripts/smoke-auth-local.py` 종료 0, local-mock 세션 assertion 11건 통과.
- local-mock 서버 Ctrl-C 종료 130. 프로필 충돌을 migration 이후에만 확인하면 잘못된 DB에 향후 migration이 먼저 적용될 수 있어, 이미 marker가 있는 DB는 Flyway 실행 전에도 검사하도록 보강한다.
- Flyway 실행 전 marker 비교 추가 후 `./backend/gradlew -p backend test` 종료 0, 기존 4개 단위 시험 통과. 환경 충돌 실제 DB 검증을 실행한다.
- Sandbox 프로필을 의도적으로 local-mock DB에 지정한 `bootRun` 종료 1: Flyway 실행 전 `CONFIG_REQUIRED: database belongs to a different environment profile`로 거부됨. 이는 기대한 음성 시험이다.
- marker 없는 기존 Flyway DB는 환경을 임의 추정하지 않고 차단하도록 보정. `./backend/gradlew -p backend test` 종료 0, 기존 4건 통과. 이전에 생성한 별도 Sandbox 시험 DB로 음성 검증한다.
- marker 없는 별도 Sandbox DB 기동 시험은 종료 1. 출력이 잘려 정확한 원인 문구를 확인하지 못해 요약 로그를 별도 파일에 받아 원인을 확인한다.
- 기존 marker 없는 Sandbox 시험 DB를 향한 `bootRun` 재확인 종료 1: `CONFIG_REQUIRED: existing database has no environment marker`로 migration 전 차단됨을 로그에서 확인. 기대한 음성 시험이다.
- 동일 local-mock DB와 일치하는 프로필에서는 migration 확인 후 서버가 정상 기동했다.
- 최종 guard 반영 후 `python3 scripts/smoke-auth-local.py` 종료 0, local-mock assertion 11건 재통과. 신규 빈 DB 최초 기동과 production 전환 검증은 아직 미실행이다.
- local-mock 테스트 서버 Ctrl-C 종료 130. 전용 DB 컨테이너는 volume 삭제 없이 정지한다.
- `docker compose ... stop` 종료 0; 전용 volume과 두 시험 DB는 보존.
- 커밋 직전: 환경 guard 및 V2 migration만 반영. 이 guard는 DB 공유 방어의 일부이며 전체 개발 모드 격리·실 Provider·Unity 검증은 미완료다.

### [P02-T03] 원장 구현 재개 — 2026-11-10 Asia/Seoul
- DB profile 격리 guard를 반영했다. Mock 거래 고유키·서버 결정 지급액·동일 DB transaction·소유권을 보장하는 경로를 작성한다. 실제 스토어 검증과 완료 처리는 별도 미완료로 남긴다.
- `./backend/gradlew -p backend test` 종료 0: Mock 원장 코드 컴파일과 기존 테스트 4건 통과. 신규 HTTP·DB 구매 및 원장 불변식은 아직 검증 전이다.
- 점검 중 Mock 상품 seed가 공통 migration 경로에 있음을 발견해 Sandbox DB에 Mock 상품이 들어가지 않도록 profile 전용 migration으로 이동한다.
- Mock seed를 local-mock Flyway 경로로 분리하고 사용자/멱등 충돌 코드를 구분한 뒤 `./backend/gradlew -p backend test` 종료 0, 기존 4건 통과. DB 통합 확인은 이어서 수행.
- `scripts/run-demo-backend.sh` 실행 중: 전용 local-mock DB에 V3 Mock catalog migration 적용과 서버 기동 확인. 실제 구매 기능 검증은 아직 미실행.
- `GAMEBRIDGE_DEV_AUTH_KEY=<local-test> python3 scripts/smoke-purchase-local.py` 종료 0: local-mock DB assertion 13건 통과. 동일 거래 재검증 및 동시 두 요청의 1회 지급, 다른 계정 충돌, key/body 충돌, 수량 2 거부, premium 재요청을 확인. 실제 스토어 proof·finalization은 미검증.
- 검토 중 catalog 누락 시 ledger 없이 GRANTED가 기록될 위험을 발견해 상품 행과 ledger insert 수를 검사하고 실패 시 transaction을 rollback하도록 보정. `./backend/gradlew -p backend test` 종료 0. 변경 후 HTTP/DB 재검증 필요.
- 변경 전 서버 Ctrl-C 종료 130. 수정된 서버로 재기동해 Mock 구매 smoke를 반복한다.
- 보정된 local-mock 서버 재기동 관측. 기존 전용 DB는 보존한다.
- 보정 후 `python3 scripts/smoke-purchase-local.py` 종료 0, local-mock assertion 13건 재통과. catalog 누락 강제 주입과 재시작·실제 스토어 검증은 별도로 남는다.
- 테스트 서버 Ctrl-C 종료 130; 전용 DB는 데이터 보존 상태로 정지한다.
- 전용 DB `docker compose ... stop` 종료 0. 실제 코인 구매가 아닌 Mock 구매·원장 데이터는 전용 volume에 보존됐다.
- 커밋 전: local-mock catalog·동일 transaction 원장 지급·일부 멱등 처리와 smoke만 포함. 최종화 worker·실 스토어 검증·장애 복구·정밀 revision 계약 등은 미구현이므로 P02-T03은 PARTIAL 유지한다.

### [P02-T04] 시작 — 2026-11-10 Asia/Seoul
- P02-T03 Mock 지급·중복 방지 일부 확인. 영속적인 완료 처리 큐와 재시도를 작성한다. 실제 Google consume/acknowledge는 아직 구현하지 않으며 Mock 완료와 구별한다.
- `./backend/gradlew -p backend test` 종료 0: 새 Mock finalizer의 첫 시도 실패·후속 성공을 포함해 단위 테스트 통과. DB 큐·worker 재시작·원장 불변은 아직 미검증이며 구매 경로에 연결되지 않았다.
- 전용 PostgreSQL `docker compose ... up -d --wait` 종료 0, healthy. DB test는 local-mock marker를 확인하고 새 UUID 행만 생성하며 사용자 기존 데이터는 삭제하지 않는다.
- `GAMEBRIDGE_RUN_DB_TESTS=true ... ./backend/gradlew -p backend test` 종료 0: 전용 PostgreSQL에서 Mock 첫 실패 후 worker 객체 재생성·성공과 원장 1행/100 유지 확인. 상세 테스트 수와 skip 여부는 XML로 확인한다. 이 시험은 실제 프로세스 종료나 실제 스토어 finalization이 아니다.
- JUnit XML: 총 6건, 실패 0, skip 0 (DB finalization 1건 포함). 검토 중 테스트가 대기 중인 다른 Mock 작업을 집어갈 수 있음을 발견해 테스트 대상 purchase ID만 선택하도록 보정한다.
- 테스트 전용 purchase ID를 명시적으로 선택하도록 보정 후 DB 포함 `./backend/gradlew -p backend test` 종료 0. 다른 대기 작업을 시험이 소비하지 않도록 제한했다.
- 전용 DB container는 데이터 삭제 없이 정지한다.
- 전용 DB `docker compose ... stop` 종료 0. 시험 전용 UUID 사용자·구매·원장·완료 처리 행은 volume에 보존했다.
- 커밋 전: Mock worker 독립 DB 시험만 통과. 실제 구매와 job 생성 연결·자동 실행·프로세스 재시작 시험·실제 Play finalizer는 미구현이므로 P02-T04 PARTIAL 유지.
- 자동 finalizer 동시성·재시도 간격은 사용자 결정 대기. 독립적으로 Mock 지급 commit과 job 생성을 같은 transaction에 연결한다. 기본값을 승인된 정책으로 간주하지 않는다.
- `./backend/gradlew -p backend test` 종료 0: 구매·job 연결 코드 컴파일 및 사용 가능한 단위 시험 통과. DB 통합 테스트는 환경 미설정으로 이 실행에서 skip; HTTP job 생성 검증은 아직 미실행.
- local-mock 서버가 전용 DB와 함께 기동됨. 구매 응답의 PENDING 및 DB의 job 동반 여부를 확인한다.
- 연결된 서버에서 `python3 scripts/smoke-purchase-local.py` 종료 0: 13개 로컬 Mock assertion 및 신규 구매의 finalization PENDING 확인. DB job 누락 여부는 별도 확인한다.
- 전용 PostgreSQL에서 PENDING 구매 중 job이 없는 행의 수 조회 종료 0, 결과 0. 이 값은 실제 외부 스토어 완료 처리 성공을 뜻하지 않는다.
- 테스트 서버 Ctrl-C 종료 130. 전용 DB는 volume을 유지하고 컨테이너를 정지한다.
- `docker compose ... stop` 종료 0. 자동 worker 동시성·백오프는 사용자 답변 대기. 현재 1초 Mock 재시도 간격과 30초 임대는 수동 시험용 내부값이며 승인된 운영 정책이 아니다. 자동 실행·실제 Provider 작업은 미구현이다.
- 커밋 전: Mock 지급과 queue 동시 기록 및 PENDING 표시를 포함. P02-T04 IN_PROGRESS/PARTIAL 유지.

### [P02-T05] 시작 — 2026-11-10 Asia/Seoul
- P02-T04 자동 재시도 정책은 사용자 결정 대기. 별도로 로컬 Mock push token의 암호화·소유권 및 서비스 설정을 구현한다. 실제 FCM/APNs와 전송은 미구현으로 구분한다.
- `./backend/gradlew -p backend test` 종료 0: AES-GCM 난수 nonce, 복호화, AAD 불일치 거부, 누락 key 실패를 확인하는 2개 단위 시험 통과. DB 기반 token 회전·소유권 검증은 아직 미실행. 실제 FCM/APNs token 및 전송 구현이 아니다.
- 암호화 key와 개발키를 일회성 테스트 값으로 공급해 local-mock 서버 기동을 확인. 등록 해제 후 토큰 보존 여부는 사용자 결정 대기이므로, 해당 결정에 의존하는 삭제·보관 구현은 잠시 보류하고 독립적인 등록·회전·소유권을 검증한다.
- `python3 scripts/smoke-device-local.py` 종료 0: local-mock assertion 7건, 공개 기본 설정·등록·token 회전·다른 계정 소유권 차단·응답 원문 미노출 확인. 수신/원격 푸시 검증 아님.
- 보존 정책 미결정으로 등록 해제 endpoint 임시 구현을 제거했다. `./backend/gradlew -p backend test` 종료 0; 마지막 DB 시험은 변경 전 서버의 등록 기능만 검증했으며 삭제는 검증하지 않았다.
- local-mock 서버 Ctrl-C 종료 130, 전용 DB container를 데이터 보존 상태로 정지한다.
- 전용 DB `docker compose ... stop` 종료 0. UUID test installation과 암호화된 Mock token은 전용 volume에 보존했다.
- 커밋 직전: local-mock 등록·암호화·소유권 확인 및 기본 config만 포함. 등록 해제·로그아웃 연결 제거는 토큰 보존 정책 결정 대기, push sender·실연동은 미구현이므로 P02-T05 PARTIAL.

### [P02-T06] 시작 — 2026-11-10 Asia/Seoul
- P02-T04/T05는 일부 구현·정책 미결정. 이미 실행 가능한 local-mock smoke를 모으고 미구현 필수 항목은 성공 처리하지 않는다.
- `bash scripts/smoke-local.sh` (개발키 미설정) 종료 2, CONFIG_REQUIRED를 확인. 하위 검사 집계와 미구현 표시 검증은 서버 기동 후 수행한다.
- 전용 DB healthy 및 local-mock 서버 재기동 확인. 아래 통합 명령은 시험 데이터를 전용 volume에 추가한다.
- `bash scripts/smoke-local.sh` (테스트 개발키 공급) 종료 1: 인증 11·구매 13·기기 등록 7 assertions 개별 통과, 자동 finalization 복구·등록 해제/로그아웃 연결 해제·보호된 push 전송이 미구현으로 전체 명령은 의도적으로 비성공 반환. 실제 플랫폼 검증 아님.
- 테스트 서버 Ctrl-C 종료 130. 전용 DB는 volume 보존 후 정지한다.
- 전용 Compose DB `stop` 종료 0; 테스트로 생성된 Mock 사용자·구매·설치 기록은 전용 volume에 보존.
- 커밋 전: 세 개의 기존 smoke를 순서대로 실행하며 미구현 필수 기능이 있으면 비성공 처리. P02-T06은 IN_PROGRESS/PARTIAL로 남기고 완성 주장하지 않는다.

### [P01-T03] 시작 — 2026-11-10 Asia/Seoul
- P01-T01/T02는 부분 완료. 초기화·종료 상태와 Provider 계약은 확정된 범위에서 독립 구현하며 전체 Native/Unity 통합은 별도 검증한다.
- `./android/gradlew -p android :sdk-core:test` 종료 0: 동시 동일 설정 합류, 다른 설정 거부, shutdown/reinit, 공통 UI gate 검사를 포함한 시험 통과. 검토 중 초기화 완료와 shutdown 경합 및 실패 직후 재시도 상태 보정이 필요함을 확인했다.
- Kotlin 초기화·종료 경합과 실패 후 상태 복구를 보정한 뒤 `./android/gradlew -p android :sdk-core:test` 종료 0. 초기화 중 shutdown의 취소 및 SHUTDOWN 전이 시험 추가 통과. Android 기기·Unity 연동은 미검증.
- `swift test --package-path ios` 종료 1: Swift Package에 macOS 최소 버전이 없어서 async Task의 macOS availability 검사 실패. macOS는 로컬 테스트 대상이며 패키지 최소 버전을 설정한 뒤 재검증한다.
- macOS 12 테스트 플랫폼을 명시한 뒤 `swift test --package-path ios` 종료 0: XCTest 총 8건, 실패 0. Swift 상태기계의 동시 동일 설정 합류·다른 설정 거부·중복 shutdown 확인. iOS simulator/device 및 Unity 검증은 아님.
- 검토 중 Swift shutdown이 취소된 초기화의 종료를 기다리지 않고 Provider를 종료할 수 있는 경합을 발견하여 수정한다.
- Swift shutdown이 초기화 취소 완료를 기다리도록 보정 후 `swift test --package-path ios` 종료 0: XCTest 총 9건, 실패 0. 초기화 중 shutdown 시험 추가. 취소에 협력하지 않는 Provider의 timeout 처리는 아직 미구현이다.
- 커밋 전: Kotlin/Swift coordinator와 최소 Provider interface만 포함. Unity 상태 mirror, 세부 Provider interface, timeout·모든 생명주기 및 플랫폼 빌드는 미구현/미검증이므로 P01-T03 PARTIAL 유지.

### [P01-T04] 시작 — 2026-11-10 Asia/Seoul
- P01-T03은 기본 coordinator만 구현. 별도 test module에서 결정적 offline Fake를 작성하고 실제 Provider 또는 Backend 지급과 혼동하지 않는다.
- `./android/gradlew -p android :sdk-testing:test` 종료 0: 별도 Kotlin Offline Fake에서 pending·취소 미지급, 동일 거래 중복 미지급, 상품 충돌, 네트워크 실패, Sandbox 모드 사용 거부 확인. DB나 실제 플랫폼 테스트가 아니다.
- `swift test --package-path ios` 종료 0: XCTest 총 10건, 별도 Swift Offline Fake의 모드 격리·pending 미지급·중복 미지급 포함. 이는 macOS 메모리 Fake 시험이며 서버·iOS 기기·실제 결제 성공이 아니다.
- Kotlin Offline Fake에 명시적 권한·등록·allowlist route·messageId 중복 제거 추가 후 `./android/gradlew -p android :sdk-testing:test` 종료 0. 이는 메모리 주입 이벤트이며 FCM 수신이 아니다.
- Swift Offline Fake에도 권한·등록·route 허용 목록·중복 이벤트 제거를 추가하고 `swift test --package-path ios` 종료 0, XCTest 10건 통과. APNs 전송·수신 검증이 아니다.
- 커밋 전: Kotlin/Swift의 독립 테스트용 메모리 Fake만 포함. Unity Editor Fake, late callback 시나리오, Native→Backend LOCAL_MOCK 통합은 미구현이므로 P01-T04 PARTIAL 유지.

### [P01-T05] 시작 — 2026-11-10 Asia/Seoul
- P01-T03은 부분 완료. Native HTTP와 보안 저장소를 별도 인터페이스로 작성하고 Unity에 토큰을 전달하지 않는다. 실제 플랫폼 저장소 검증은 가능한 환경에서 별도 수행한다.
- `./android/gradlew -p android :sdk-core:test` 종료 1: 전체 10건 중 BackendClientTest 1건 실패. XML에서 실제 실패 원인을 확인한 뒤 수정한다.
- XML 위치는 `BackendClientTest.kt:19`: JSON parser가 `bad`를 primitive로 수용해 오류가 발생하지 않았다. API 응답은 JSON object로 제한하고 Android 최소 API에서 사용 가능한 bounded stream 읽기로 교체한다.
- JSON object 확인과 bounded stream 보정 후 `./android/gradlew -p android :sdk-core:test` 종료 0, 10건 통과. BUG-001 재현 오류 해소. HTTP 세부 오류 매핑·timeout·실기기 확인은 아직 미완료.
- `ANDROID_HOME=<installed SDK> ./android/gradlew -p android :sdk-android:assembleDebug` 종료 0: Android Keystore AES-GCM 저장소 소스 AAR 컴파일. SDK XML 버전 경고 관측; 기기 저장·복원 및 백업 복원은 미검증.
- `swift test --package-path ios` 종료 0: Swift HTTP·Keychain 소스 컴파일 및 기존 XCTest 10건 통과. 새 HTTP 동작·Keychain 저장은 이 실행에서 검증하지 않았다.
- `swift test --package-path ios` 종료 0: XCTest 총 11건 중 URLProtocol mock을 이용한 HTTP 성공·401·잘못된 JSON·timeout·경로 거부 확인. 실제 네트워크·Keychain 기기 저장 검증은 아님.
- `ANDROID_HOME=<installed SDK> ./android/gradlew -p android :sdk-core:test :sdk-android:assembleDebug` 종료 0: HTTP timeout을 포함한 core 시험 10건 및 Keystore 코드 AAR 빌드. 실제 기기 저장·복원 검증은 미실행.
- 커밋 전: Native HTTP와 OS 보안 저장소 기반만 포함. 세션 갱신·오류 코드 세분화·취소·기기 Keychain/Keystore 실행·백업 정책 및 LOCAL_MOCK 수직 연결은 미완료. Swift 응답 크기는 수신 완료 후 검사한다. P01-T05는 PARTIAL 유지.

### [P03-T01] 시작 — 2026-11-10 Asia/Seoul
- P01-T04/T05 및 P02-T06은 부분 완료. 이미 확인된 local-mock Backend 경로를 Kotlin SDK와 연결하고 Compose/실기기 검증은 별도 기록한다.
- `./android/gradlew -p android :sdk-core:test` 종료 0: 새 local-mock client 컴파일 및 기존 10건 통과. 신규 수직 client 테스트는 아직 없으며 검토 중 catalog 응답이 배열인데 HTTP object-only 검사에 막히는 문제를 발견해 수정한다.
- `./android/gradlew -p android :sdk-core:test` 및 `swift test --package-path ios` 종료 0: JSON object/array 허용 후 기존 시험 통과(Swift XCTest 11건). 신규 opt-in Backend 수직 시험은 미실행/skip이다.
- 전용 PostgreSQL과 local-mock 서버 기동 확인. JVM Native client 수직 시험은 임시 메모리 TokenStore를 사용하며 전용 Mock DB에 구매 기록을 남긴다.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... ./android/gradlew -p android :sdk-core:test --rerun-tasks` 종료 0: Kotlin JVM SDK→실제 local-mock HTTP/PostgreSQL 경로의 로그인·상품·구매·동일 거래 재요청·서버 잔액·메모리 저장소 복원·로그아웃 검증. XML에서 통합 테스트가 skip 없이 실행되었는지 확인한다. Android 기기·Keystore 실행이 아니다.
- JUnit XMLで Kotlin Native client の local-mock integration 1件、失敗0・skip0を確認。次に Android Compose consumer を SDK API のみに接続する。
- `ANDROID_HOME=<installed SDK> ./android/gradlew -p android :sample-app:assembleDebug` 종료 0: Compose 샘플이 SDK public API로 local-mock 초기화·로그인·복원·상품·구매·서버 잔액·로그아웃을 컴파일. debug 전용 제한된 localhost/emulator cleartext 설정 사용. 네이티브 라이브러리 strip 경고가 있으며 앱 실행은 아직 확인 전이다.
- `adb devices` 종료 0: 연결된 Android 기기·emulator 없음. 설치된 AVD가 있으면 직접 실행 가능 여부를 추가로 확인한다.
- `emulator -list-avds` 종료 0: 기존 사용자 AVD들이 존재. 기존 AVD 데이터를 사용하지 않고 별도 테스트 AVD를 만들 수 있는지 확인; Android 36 arm64 system image가 설치되어 있다.
- `avdmanager create avd` 종료 0: 기존 AVD와 별도로 GameBridge_SDK_Test_20261110을 프로젝트 artifacts 경로에 생성. 앱 실행은 아직 미확인.
- 専用 AVD を `emulator -avd GameBridge_SDK_Test_20261110 -port 5566 -no-window -no-audio -no-snapshot -no-boot-anim` で起動中。既存 AVD は変更していない。boot 終了とアプリ実行は未確認。
- `adb -s emulator-5566 shell getprop sys.boot_completed` 폴링 종료 0: 전용 Android 36 AVD 부팅 완료 확인. 앱 실행은 미검증.
- `adb -s emulator-5566 install -r .../sample-app-debug.apk` 종료 0: 전용 테스트 AVD에 Debug APK 설치 성공.
- `adb ... am start -n com.gamebridge.sample/.MainActivity` 종료 0: Activity 실행 요청 성공. 화면과 기능 수행 결과는 별도 확인한다.
- `uiautomator dump` 종료 0: Compose 초기 화면과 LOCAL_MOCK 미연결 상태가 실제 AVD에 표시됨. 로그인·구매 흐름은 아직 미검증.
- 전용 AVD에서 테스트 전용 개발키를 입력하고 Initialize 클릭 후 UI dump 종료 0: `Initialized LOCAL_MOCK` 표시. 키와 토큰은 dump 요약에서 제외.
- AVD에서 Mock login A 클릭 후 UI dump 종료 0: 로그인 성공 표시. localhost Backend에 연결된 LOCAL_MOCK 결과이며 Google 인증은 아니다.
- AVD에서 상품·잔액 조회 후 UI dump 종료 0: 두 Mock 상품과 서버 잔액(전용 테스트 DB의 기존 잔액) 표시 확인. 구매 후 변화 확인은 이어서 수행한다.
- AVD Mock coins_100 구매 후 UI dump 종료 0: 전용 Backend 서버 잔액 900→1000, `GRANTED / PENDING` 표시. 이는 실제 Play 결제나 완료 처리 성공이 아니다. 앱 재시작·Keystore 복원을 확인한다.
- 앱 재시작 직후 화면이 준비되기 전 자동 입력해 테스트 전용 키 문자열이 URL 칸에 들어갔고 `INTERNAL_ERROR`가 표시됐다. 실제 키/토큰은 사용하지 않았으며 이는 복원 성공 증거가 아니다. 화면 준비를 확인하고 재시험한다.
- 재시작 후 UI 준비를 확인하고 개발키를 올바른 password 칸에 입력해 `Initialized LOCAL_MOCK`을 다시 확인. 복원 동작은 다음 단계에서 확인한다.
- 준비 확인 후 Restore 클릭 및 UI dump 종료 0: 앱 재시작 뒤 Keystore 저장 세션으로 local-mock 사용자 복원 성공. ENV-004 자동화 입력 오류 해소.
- 전용 AVD `run-as`로 SDK preferences를 읽어 내용 자체를 출력하지 않고 검사: session 암호문 항목 존재, accessToken·refreshToken 필드명과 테스트 개발키 평문 없음, Python 종료 0. 전체 기기 보안 감사는 아니다.
- AVD 복원 후 서버 상태 재조회 UI dump 종료 0: 잔액 1000과 `Server state loaded` 확인. 실제 Play/Google 통과가 아니라 local-mock 연동이다.
- AVD에서 Sign out 클릭 후 `Signed out` UI 확인(명령 종료 0). 기기에 저장된 SDK session 제거 여부를 따로 검사한다.
- AVD SDK preferences를 내용 비출력으로 검사: 로그아웃 후 session 항목 없음, 종료 0. push 설치 연결 해제는 별도 미구현이며 이 시험에서는 등록하지 않았다.
- `adb -s emulator-5566 emu kill` 종료 0: 이번 작업에서 만든 전용 AVD만 종료, AVD 및 테스트 데이터는 삭제하지 않았다.
- local-mock 테스트 서버 Ctrl-C 종료 130. DB는 전용 volume을 보존하고 컨테이너만 정지한다.
- 전용 DB container `stop` 종료 0. 전용 volume과 새 AVD는 보존했다. Android SDK 요청·local-mock server·DB 수직 경로는 확인했으나 실제 Store/Google, Unity, 릴리스 패키지 및 세션 예외 전체는 미검증이다.
- `docs/evidence/p03-t01-android-local-mock.md`에 비식별 결과와 한계를 기록. `python3 scripts/verify-progress.py` 종료 0.
- 커밋 전: Kotlin Native LOCAL_MOCK 경로와 Compose debug 소비자·제한적 emulator 네트워크 설정을 포함한다. Provider·실결제·Unity·전체 오류 처리와 선행 작업은 남아 P03-T01 PARTIAL 유지.

### [P03-T02] 시작 — 2026-11-10 Asia/Seoul
- Swift Core HTTP·Keychain 기반과 local-mock Backend를 연결하고 iOS 16 SwiftUI 샘플을 구성한다. XcodeGen 부재 및 Simulator 상태를 조사하며 iOS 빌드/실행을 macOS Swift 테스트와 구분한다.
- XcodeBuildMCP simulator 목록 확인: iOS 26.5 iPhone simulator 1대가 이미 부팅 중. 기존 simulator를 지우거나 다른 앱 데이터는 변경하지 않는다.
- `brew fetch --formula xcodegen` 종료 0: Homebrew 검증된 2.46.0 bottle을 다운로드. 시스템 전역 설치는 하지 않고 프로젝트 로컬 도구로 사용한다.
- 프로젝트 로컬 경로에 bottle 압축을 해제하고 `xcodegen --version` 종료 0, 2.46.0 확인. Xcode 프로젝트 생성·빌드는 아직 미실행.
- `swift test --package-path ios` 종료 0: Swift local-mock client 컴파일 및 기존 XCTest 11건 통과. 신규 client의 Backend 수직 검증은 아직 미실행. actor 재진입 검토에서 늦은 401이 회전된 이전 refresh를 다시 사용해 family를 폐기할 수 있어 보정한다.
- 늦게 도착한 401은 이미 교체된 access token을 우선 사용하고 로그인/로그아웃 generation이 바뀌면 오래된 응답을 거부하도록 보정 후 `swift test --package-path ios` 종료 0, 기존 11건 통과. 동시 refresh와 실제 Backend 통합 시험은 아직 미실행.
- Swift client 수직 검증을 위해 전용 local-mock DB 및 서버가 정상 기동됨. 구매 시험 데이터는 전용 volume에 남는다.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios` 종료 0: XCTest 12건 중 신규 Swift SDK→local-mock Backend/DB 수직 시험 1건 실행·통과. Mock 로그인·상품·동일 거래 재검증·서버 잔액·메모리 저장소 복원·로그아웃 확인. macOS 테스트이며 iOS Simulator 실행이나 실제 플랫폼 검증은 아니다.
- `xcodegen generate --spec ios/Framework/project.yml` 종료 0: iOS 샘플 Xcode 프로젝트 생성. 컴파일·시뮬레이터 실행은 아직 미검증. Debug에서만 loopback cleartext 예외를 명시했다.
- XcodeBuildMCP session 기본값은 비어 있었음. 부팅된 Simulator에서 샘플 placeholder bundle의 기존 설치 여부 조회 종료 2(해당 앱 없음); 기존 앱을 덮어쓰지 않는다.
- XcodeBuildMCP `build_run_sim` 성공: iOS 26.5 Simulator Debug 샘플 빌드·설치·launch 완료(경고/오류 0). 앱 화면 및 local-mock 연동은 아직 미확인. 기존 Simulator 삭제·초기화는 하지 않음.
- Simulator `snapshot_ui`는 요소 1개·상호작용 대상 0개를 반환하여 화면 준비나 앱 활성 상태를 확인하지 못했다. 스크린샷과 런타임 로그로 원인을 확인한다.
- XcodeBuildMCP screenshot에서 SwiftUI의 LOCAL_MOCK 샘플과 URL·개발키·Initialize 화면을 직접 확인. 화면 초기화 이후 접근성 snapshot을 다시 시도한다.
- Simulator 화면은 확인됐지만 XcodeBuildMCP snapshot이 두 차례 접근성 대상 0개를 반환했고 컴퓨터 UI 입력·스크롤에서도 다음 화면을 검증하지 못했다. 실행 성공으로 기록하지 않는다. XCTest의 샘플 전용 UI smoke로 독립 확인을 시도한다.
- XcodeGen UI smoke target을 추가하고 `xcodegen generate` 종료 0. 테스트 코드에는 로컬 서버와 맞춘 공개 테스트 전용 값만 사용하며 실제 자격증명은 없다. 테스트 실행 전이다.
- XcodeBuildMCP `test_sim` 실패: UI test target의 Info.plist가 없어 코드 서명 단계에서 빌드 실패, 테스트 0건. 테스트 target에 Info.plist 자동 생성을 설정하고 재실행한다.
- `test_sim` 첫 재실행: UI test 1건 실패, 0건 통과. 개발키 입력 후 키보드/스크롤 상태에서 `signIn` 버튼을 찾지 못함. local-mock UI 전체 성공으로 기록하지 않는다. 키보드 닫기와 세밀한 스크롤을 보정한다.
- UI 키보드 닫기·세밀한 스크롤 보정 후 XcodeBuildMCP `test_sim` 성공: iOS 26.5 Simulator XCTest UI smoke 1건, 실패 0, skip 0. 샘플 Mock 로그인·상품 조회·coins 구매 후 `GRANTED / PENDING` 표시 확인. macOS Swift integration 1건은 별도이며 Apple 인증·StoreKit 결제는 아니다. ENV-005 대체 검증 성공.
- Debug Simulator 앱 Info.plist를 `PlistBuddy`로 검사(종료 0): ATS cleartext 예외는 127.0.0.1 및 localhost에만 존재. Release 설정과 실제 기기 정책은 별도 검증 필요.
- UI smoke를 앱 재시작·Keychain 복원·로그아웃까지 확장해 같은 Simulator에서 재검증한다.
- 확장된 XcodeBuildMCP `test_sim` 성공: iOS 26.5 Simulator UI 시험 1건, 실패 0·skip 0. Mock 구매 후 앱 종료·재실행·Keychain 세션 복원(`Restored`) 확인, 로그아웃 버튼도 클릭. 로그아웃 완료 표시 확인은 추가한다.
- XcodeBuildMCP `test_sim` 재실행 성공: iOS 26.5 UI 시험 1건, 실패 0, skip 0. Mock 로그인·상품·구매·앱 재시작 후 Keychain 세션 복원·로그아웃 완료 표시 확인. 실제 Apple 인증·App Store 거래·원격 푸시는 실행하지 않았다.
- XcodeBuildMCP `build_sim` Release 구성 성공(경고/오류 0): 컴파일만 확인했으며 출시 가능성을 뜻하지 않는다. Debug 전용 ATS 예외가 Release plist에 없는지 확인한다.
- Release Simulator app Info.plist 검사 종료 0: NSAppTransportSecurity 예외 없음. Release 앱 실행·실기기 검증은 하지 않았다.
- XcodeBuildMCP `stop_app_sim`은 대상 앱 프로세스를 찾지 못해 실패(이미 실행 중이지 않음). Simulator 자체나 다른 앱은 종료하지 않았다.
- local-mock 서버 Ctrl-C 종료 130. 전용 DB는 삭제하지 않고 정지한다.
- 전용 DB `docker compose ... stop` 종료 0. Swift Mock 구매·세션 시험 기록은 전용 volume에 보존했다. 사용자 Simulator 자체는 그대로 둔다.
- `bash scripts/generate-ios-project.sh` 종료 0: 로컬 XcodeGen 2.46.0으로 샘플 프로젝트 재생성. 산출 Xcode project와 빌드 산출물은 Git 제외하고 spec을 보존한다.
- `docs/evidence/p03-t02-ios-local-mock.md`에 Simulator 결과·실패 이력·한계 기록. 커밋 전: Swift Native client와 SwiftUI 샘플, Debug/Release 보안 설정 및 UI smoke 포함. 실제 Apple Provider·StoreKit·Unity와 전체 세션 경합 검증이 남아 P03-T02는 PARTIAL 유지.

### [P03-T03] 시작 — 2026-11-10 Asia/Seoul
- P03-T01과 Bridge 계약은 부분 검증됨. Unity 클래스를 직접 참조하지 않는 Android 진입점과 명시적 미지원 응답을 작성한다. Unity Editor/JNI 실행은 라이선스 환경과 패키징이 준비된 뒤 검증한다.
- `ANDROID_HOME=<installed SDK> ./android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 0: dispatcher 테스트 및 JNI facade AAR 컴파일. Unity 호출·콜백 실행은 미검증이고 status/shutdown 외 모든 작업은 명시적 UNSUPPORTED_OPERATION이다.
- 검토 중 shutdown 응답 후 status가 고정 UNINITIALIZED로 되돌아가는 문제를 발견해 상태를 보정한다.
- 상태 보정 후 `ANDROID_HOME=<SDK> ./android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 0. C# AndroidJavaProxy 소스는 Unity 미실행으로 컴파일·JNI 왕복 미검증.
- 구현 검토 중 무제한 executor 대기열과 callback 교체 후 이전 응답 전달 위험을 발견해 계획의 큐 상한과 callback 세대 차단을 추가한다.
- 큐 상한 100 및 BUSY 응답, callback 세대 확인을 추가한 뒤 Android core 시험과 bridge AAR 빌드 종료 0. Unity C# 컴파일·JNI 실행은 여전히 미검증.
- 세대 확인과 callback 교체 사이의 경합 가능성이 남아 동일 lock에서 검사·전달하도록 수정한다.
- callback 세대 검사·전달을 동일 lock으로 보호한 뒤 `:sdk-unity-bridge:assembleDebug` 종료 0. Unity 라이선스 부재로 C# 컴파일 및 JNI callback thread 검증은 아직 불가.
- `unzip -p .../sdk-unity-bridge-debug.aar proguard.txt` 종료 0: facade 및 callback keep 규칙이 AAR에 포함됨을 확인. R8 최종 앱 실행은 미검증.
- Unity C# callback 대기열의 계획상 상한 100과 drop counter, 종료 후 수신 차단을 작성했다. `python3 scripts/verify-progress.py` 종료 0. Unity Editor 미기동으로 C# 컴파일·런타임 검증은 NOT_RUN이다.
- 커밋 전: status/shutdown만 처리하고 나머지는 명시적 UNSUPPORTED_OPERATION. 잘못된 envelope는 callback 없이 거부되어 호출자 timeout 처리가 필요하며, 실제 Unity JNI 왕복·인증·lifecycle·R8 release는 미완료이므로 P03-T03 PARTIAL 유지.

### [P03-T04] 시작 — 2026-11-10 Asia/Seoul
- P03-T02는 Simulator local-mock을 부분 검증. Swift C ABI와 static framework의 독립적 기반을 구현하며 Unity iOS 링크·실기기 검증은 별도다.
- `swift test --package-path ios` 종료 0: XCTest 13건 중 12건 통과, local Backend opt-in 시험 1건 skip. 신규 C ABI fixture 1건에서 한글·emoji 입력 buffer 복사와 callback 응답 requestId를 macOS 프로세스에서 확인. iOS static framework·Unity 호출은 아직 미검증.
- Swift Bridge 대기열 상한 100과 BUSY 응답을 추가하고 `swift test --package-path ios` 종료 0: 12건 통과, local Backend opt-in 1건 skip. 포화·Unity callback 경합은 미검증이다.
- XcodeBuildMCP `build_sim` GameBridgeNative Release 성공이나 `GameBridgeCore`의 library evolution 경고 발생. `canImport`가 외부 module을 참조하여 static framework의 자족성이 불확실하므로 target 전용 컴파일 조건으로 수정하고 재빌드한다.
- target 전용 컴파일 조건을 적용한 뒤 XcodeBuildMCP `build_sim` Release 성공(경고 0). static 형식 및 C export는 별도 검사한다.
- `file`/`nm -g` 종료 0: iOS Simulator Release framework binary가 arm64/x86_64 static ar archive이며 `_GB_ProtocolVersion`, `_GB_SetCallback`, `_GB_Dispatch`, `_GB_Shutdown` export 관측. XCFramework, device slice, Unity 링크는 아직 미검증.
- Swift C ABI용 C# transport를 작성했으나 Unity 컴파일·iOS 링크는 ENV-002로 미검증. 코드 검토에서 dispose lock과 native callback lock의 역순 대기 가능성을 발견해 수정한다.
- C# callback의 InstanceLock 취득을 제거해 lock 순서 역전을 피했다(소스 검토만, Unity 미실행). `swift test --package-path ios` 종료 0: 12건 통과, local Backend opt-in 1건 skip.
- 사용자 정책 결정 수신: 자동 완료 처리 동시 1개·5초 시작 지수 백오프, 푸시 등록 해제/로그아웃 시 해당 토큰 즉시 삭제. DECISIONS에 기록. 아직 구현·검증 전이며 블로커는 코드 반영 전까지 열린 상태로 유지.
- `xcodebuild archive` generic iOS, signing disabled 종료 0. Swift-only static framework에서 umbrella header/module map 경고가 발생했으며 바이너리 C symbol 검증은 별도로 한다. 실제 기기 서명·실행은 아님.
- `xcodebuild archive` generic iOS Simulator, signing disabled 종료 0. 동일 umbrella header 경고가 발생했다. 두 archive에서 XCFramework 생성과 slice·symbol 검사를 수행한다.
- `xcodebuild -create-xcframework` 종료 0: device·Simulator archive로 로컬 XCFramework 생성. 내용과 export는 아직 확인 전.
- XCFramework Info.plist·`file`·`nm -g` 검사 종료 0: device arm64와 simulator arm64/x86_64 각각 static archive, 4개 C export 확인. 시뮬레이터/실기기 Unity 실행 및 링크 확인은 아직 안 됨. archive 시 Swift-only umbrella header 경고는 남아 있다.
- `nm -u` device static archive 검사 종료 0: 외부 `GameBridgeCore` 참조 0건. Swift runtime 의존성과 UnityFramework 링크는 이 결과만으로 증명되지 않는다.
- 커밋 전: Swift C ABI, C# iOS transport 소스, static framework target 및 심볼 검증만 포함. 실제 SDK 요청 연결·Unity 빌드·device 실행·archive 경고 해결은 미완료로 P03-T04 PARTIAL 유지.

### [P02-T05] 사용자 결정 반영 — 2026-11-10 Asia/Seoul
- 등록 해제와 로그아웃 시 해당 토큰 즉시 삭제를 구현한다. 각 등록을 세션에 묶어 다른 세션·다른 사용자의 토큰을 삭제하지 않으며, 기존 세션 미연결 행은 임의 귀속하지 않는다.
- 사용자 결정에 따라 세션 소유권 migration과 등록 해제·로그아웃 시 물리 삭제 코드를 작성. `./backend/gradlew -p backend test` 종료 0, 기존 단위 시험만 통과했으며 DB 삭제·다른 세션 보존 검증은 아직 미실행.
- 검토 중 이미 인증된 등록 요청과 동시에 로그아웃하면 삭제 직후 token이 다시 기록될 수 있는 경합을 발견했다. 같은 session row lock으로 직렬화하고 폐기 상태를 다시 확인한다.
- 등록·로그아웃이 같은 session row를 잠그고 등록 시 폐기/만료를 재확인하도록 보정 후 `./backend/gradlew -p backend test` 종료 0. 실 DB 경합·삭제 결과 검증은 아직 미실행.
- 전용 local-mock DB에 V4 세션 소유권 migration 적용 후 서버 기동 확인. 신규 token은 해당 session에 연결하며 기존 session_id 없는 행은 자동 삭제·귀속하지 않는다.
- `python3 scripts/smoke-device-local.py` 종료 0: local-mock HTTP/PostgreSQL assertion 15건 통과. 다른 사용자 삭제 거부, 같은 사용자의 다른 세션 토큰 보존, 해당 세션 로그아웃 시 행 삭제, 명시적 등록 해제 삭제 및 등록↔로그아웃 경합 후 토큰 미잔존을 확인. 실제 FCM/APNs는 아님.
- `SELECT count(*) ... WHERE session_id IS NULL` 종료 0, 기존 Mock 시험 행 2개. 이전 schema의 행은 특정 session에 안전하게 귀속할 수 없어 임의 삭제하지 않았다. 신규 등록부터 즉시 삭제 정책 적용.
- 커밋 전: 정책과 설정/문서, local-mock token 삭제·경합 검증을 함께 포함. 실제 FCM/APNs, legacy 행 처리 및 개발 push sender는 미구현이므로 P02-T05는 PARTIAL 유지.

### [P02-T04] 사용자 결정 반영 — 2026-11-10 Asia/Seoul
- 사용자가 선택한 기본 동시 1개·5초 시작 지수 백오프를 local-mock worker의 설정과 실행에 반영한다. 실제 Google finalizer는 여전히 미구현이다.
- 사용자 선택에 따라 local-mock 기본 concurrency=1, initial backoff=5초, 지수 증가 및 설정 변수를 구현하고 `./backend/gradlew -p backend test` 종료 0. 자동 scheduler·PostgreSQL advisory slot·재시작 및 동시성은 아직 실제 DB 검증 전이다.
- 전용 PostgreSQL 사용 opt-in `./backend/gradlew -p backend test` 종료 0: 5초 첫 backoff, worker 객체 재생성 후 처리, 원장 1회 유지, 두 worker가 동시에 외부 처리에 진입하지 않는 기본 동시 1개를 확인. 실제 process restart·자동 scheduler는 아직 검증 전이다.
- 최종화 중 예외도 안전한 실패로 바꾸어 동일 지수 백오프를 적용하도록 보정 후 DB 포함 Gradle test 종료 0. 실제 scheduler 재기동 시험을 진행한다.
- opt-in JUnit XML 총 10건, 실패·skip 0. 자동 scheduler 시험 전 별도 `gamebridge_finalization_verify_20261110` DB의 부재를 조회하고 생성(각 종료 0). 기존 DB와 사용자 데이터는 변경하지 않는다.
- 별도 빈 finalization 시험 DB와 local-mock 서버(127.0.0.1:18081) 기동 및 migration 확인. 실제 scheduler 실패 후 서버 재시작과 복구를 검증한다.
- 별도 테스트 DB에서 Mock 구매 후 자동 scheduler의 첫 시도가 실패하고 job이 `PENDING`, attempt 1로 남는 것을 Python/psql 검사 종료 0으로 확인. 원장·재시작 후 완료는 다음 단계에서 검증한다.
- 첫 실패 관측 후 해당 시험 서버를 Ctrl-C 종료(130). job이 아직 대기 중인지 확인한 뒤 동일 DB로 재시작한다.
- 첫 실패 후 수동 서버 종료 전 다음 시도가 이미 완료되어 DB 상태 확인 assertion 종료 1(`FINALIZED|2`). 자동 재시도는 관측됐지만 프로세스 재시작 복구 증거는 아니다. 테스트가 시작한 서버만 첫 실패 즉시 종료하는 방식으로 재시험한다.
- 전용 테스트 서버를 동일 격리 DB의 18081 포트로 재기동했다. 다음 시험은 서버 로그에서 확인한 이번 테스트 프로세스만 식별해 첫 실패 직후 종료한다.
- 식별된 전용 서버에 대해 첫 자동 실패를 DB에서 관측한 직후 해당 테스트 프로세스만 SIGTERM하는 Python 검사 종료 0. 종료 시 저장된 상태는 별도로 확인한다.
- 서버 종료 후 별도 DB 조회 종료 0: job `PENDING|1` 영속 확인. SIGTERM된 Java process는 143, Gradle bootRun은 종료 1로 보고했으며 의도된 테스트 종료다. 같은 DB에서 재기동한다.
- 동일 테스트 DB로 local-mock 서버 재기동 확인. 저장된 job의 자동 완료 및 ledger 불변식을 조회한다.
- 동일 DB로 프로세스 재시작 후 DB 검사 종료 0: Mock job `FINALIZED`, attempt 2, purchase `GRANTED/FINALIZED`, ledger 1행·합계 100. 첫 실패 상태에서의 프로세스 재시작을 확인했으며 처리 도중 강제 중단이나 실제 Google finalizer 검증은 아니다.
- 두 테스트 서버(기존 local-mock 및 별도 finalization DB)를 각각 Ctrl-C 종료 130. 전용 PostgreSQL container는 volume 보존 후 정지한다.
- `docker compose ... stop` 종료 0. 별도 finalization 시험 DB 및 전용 volume은 삭제하지 않았다.
- 커밋 전: 사용자 승인 Mock scheduler 정책, DB 전역 advisory slot, 지수 backoff, 사용자 선택 설정과 실 DB 검증을 포함한다. 실제 Google consume/ack, 비정상 처리 중 crash·다중 배포·운영 안전성은 미완료이므로 P02-T04 PARTIAL 유지.

### [P03-T03] C# 독립 컴파일 재개 — 2026-11-10 Asia/Seoul
- Unity Editor에 포함된 .NET SDK 및 Unity managed assembly를 발견했다. Editor 라이선스 없이 C# 컴파일을 별도 확인하며 이를 Unity Editor/JNI 실행으로 취급하지 않는다.
- Unity 포함 .NET SDK 8.0.318로 실제 Unity managed assembly를 참조해 Android C# transport 독립 `dotnet build ... -p:DefineConstants=UNITY_ANDROID` 종료 0, 경고·오류 0. Editor/JNI 실행이 아니다. .NET 첫 실행이 개발용 HTTPS 인증서를 자동 설치했다고 출력했으며 신뢰 설정은 하지 않았다. 이후 첫 실행 인증서 생성을 끄고 사용자 인증서 임의 삭제는 하지 않는다.
- 동일 Unity managed assembly와 내장 .NET 8.0.318로 `UNITY_IOS` 분기 독립 컴파일 종료 0, 경고·오류 0. Unity IL2CPP·iOS C ABI 링크나 실행은 아니다. 이후 DOTNET_GENERATE_ASPNET_CERTIFICATE=false 사용.
- `UNITY_EDITOR_PATH=<Unity 실행파일> bash scripts/check-csharp-compile.sh` 종료 0: UNITY_ANDROID 및 UNITY_IOS 두 분기 모두 실제 Unity managed reference 대상으로 .NET 8 컴파일, 경고·오류 0. Editor import·IL2CPP·양 플랫폼 링크/콜백 실행은 하지 않았다.
- 커밋 전: 재현 가능한 컴파일 전용 script와 도구 증거를 포함한다. P03-T03/T04의 Unity 실연동은 ENV-002로 PARTIAL 유지.

### [P03-T05] 시작 — 2026-11-10 Asia/Seoul
- Native transport는 부분 구현, Unity Editor 라이선스는 ENV-002. C# 요청 registry를 독립 구현·컴파일하고, Editor import/IL2CPP 실행은 별도 대기한다. Unity 공식 registry에서 Newtonsoft package 3.2.2 metadata를 확인했다.
- Unity 공식 registry의 `com.unity.nuget.newtonsoft-json` 3.2.2 패키지를 프로젝트 artifacts에 내려받고 압축 해제(명령 종료 0). Unity Editor import·IL2CPP 호환성은 아직 검증하지 않았다.
- Unity 공식 Newtonsoft 3.2.2 의존성과 C# 요청 registry를 추가하고 `check-csharp-compile.sh` 종료 0: Android/iOS 조건부 분기 독립 컴파일, 경고 0. 실제 registry 동작·Unity Editor 실행은 아직 미검증.
- `UNITY_EDITOR_PATH=<installed Unity> bash scripts/smoke-csharp-registry.sh` 종료 0: .NET 8 독립 프로세스에서 request/session 상관관계, 잘못된 operation, 중복, timeout·취소, 100개 상한, 종료 시 대기를 검증했다. Unity Editor/IL2CPP 실행이 아니다.
- trailing JSON과 실패 응답에 error 누락된 경우를 추가한 뒤 독립 C# registry smoke 종료 0. Unity Editor·IL2CPP·native callback 실제 왕복은 미실행이다.
- 커밋 전: registry·Unity Newtonsoft 의존성과 compiler-only smoke만 포함. 이벤트, Unity facade 및 Editor Fake는 아직 미구현으로 P03-T05 PARTIAL 유지.
- P03-T05 계속: Unity Editor에서만 컴파일되는 별도 Offline Fake transport를 추가하고 실제 Native Provider에 대한 자동 fallback을 금지한다.
- `UNITY_EDITOR_PATH=<installed Unity> bash scripts/smoke-csharp-registry.sh` 종료 0: 독립 .NET에서 Editor-only Fake 초기화·Mock 로그인·동일 거래 1회 지급·가짜 푸시 등록·종료 및 registry 확인. Unity Editor·FCM·실스토어 실행은 아님.
- Sandbox 모드에서 Fake 사용 거부, pending/cancel 미지급을 추가한 독립 registry·Fake smoke 종료 0. Unity Editor 및 실제 Provider 검증이 아님.
- Offline Fake의 동일 설정 재초기화·다른 설정 거부·종료 상태 표시를 보정하고 독립 smoke 종료 0. 실제 Unity Editor는 아직 미실행.
- `check-csharp-compile.sh` 종료 0: Android/iOS/Editor 3개 분기 각각 독립 컴파일, 경고·오류 0. Unity Editor 실행 및 packaging은 여전히 ENV-002다. 다음으로 Native 응답을 공개 DTO에 안전하게 변환한다.
- 공통 fixture를 C# DTO로 읽는 독립 smoke 종료 0: 한글·emoji, 64-bit 문자열, unknown enum 및 필수 nullable 누락 검사. 검토 중 JSON.NET이 숫자를 문자열로 암묵 변환할 수 있으므로 wire JSON 타입과 민감 오류 세부정보를 추가 검증한다.
- C# wire model에 JSON 타입·필수 nullable·enum·UUID·64-bit 문자열 및 UTC 시각 검증과 공개 오류 정보 정제를 추가하고 독립 smoke 종료 0. 숫자형 priceMicros·unknown enum·누락 필드 거부 확인. Unity Editor/IL2CPP 검증은 아님.
- 커밋 전: Editor-only 메모리 Fake, transport 공통 interface 및 C# 모델 검증을 포함. Unity facade·main-thread dispatcher·실제 native operation과 이벤트 처리 미완료로 P03-T05 PARTIAL 유지.
- P03-T05 계속: 캐시 snapshot을 반환하는 C# facade와 main-thread Pump 소유자를 작성한다. Native bridge의 미구현 operation은 성공으로 치환하지 않는다.
- `check-csharp-compile.sh` 종료 0: 새 C# client facade가 Android/iOS/Editor 조건에서 각각 독립 컴파일. 구현 검토 중 초기 상태를 임의 Editor 모드로 표시하는 문제와 초기화 전 취소·빈 상태 shutdown 뒤 새 session ID 필요성을 발견해 보정한다.
- 초기 상태 Mode를 미정(null)으로 표현하고, 이미 취소된 초기화는 dispatch하지 않으며, 초기화 전 shutdown 이후 새 wire session을 사용하도록 보정. Android/iOS/Editor C# 독립 컴파일 재실행 종료 0. facade 동작 smoke는 다음에 확인한다.
- 확장한 `smoke-csharp-registry.sh` 종료 1: smoke 코드의 지역 변수 중복으로 C# 컴파일 실패(제품 코드 검증 전). 변수명을 분리하고 불필요한 미대기 경고도 수정 후 재실행한다.
- smoke 코드 변수 중복을 수정한 뒤 `smoke-csharp-registry.sh` 종료 0: C# facade의 Fake 로그인·상품·구매·잔액·복원·종료, 동일 초기화 합류, 호출자별 취소 및 종료 뒤 새 session ID 확인. Unity runtime은 미실행.
- `check-csharp-compile.sh` 종료 1: 독립 컴파일 프로젝트에서 Unity.Scripting reference가 빠져 RuntimeInitializeOnLoadMethod의 PreserveAttribute를 찾지 못했다. 실제 Unity Editor 오류로 간주하지 않고 설치된 reference 위치를 확인한다.
- Unity.Scripting reference를 추가한 재검사: Android/iOS 분기 컴파일 성공, Editor 분기에서 platform namespace가 조건부로 사라져 컴파일 실패(종료 1). 조건부 using을 수정한다.
- 조건부 using 수정 후 Android/iOS/Editor 세 C# 분기 독립 컴파일 종료 0, 경고·오류 0. Unity Editor import/재생 및 domain reload 검증은 여전히 미실행이다.
- domain reload 정적 초기화에서 이전 driver를 분리·파괴하도록 보정하고 Android/iOS/Editor/미지원 플랫폼 네 C# 분기 독립 컴파일 종료 0, 경고 0. 실제 Unity domain reload/scene 전환은 ENV-002로 검증하지 않았다.
- 최종 `smoke-csharp-registry.sh` 종료 0: C# facade·Editor Fake 경로와 request registry 동작 재확인. 이는 .NET 독립 테스트이며 Unity Editor 실행·Native operation 연동이 아니다.
- 커밋 전: C# client facade 및 단일 main-thread driver 기반만 포함. capabilities·push·sync·이벤트 공용 facade 일부와 Native init/auth/purchase 연결, Unity scene/domain reload·IL2CPP 검증은 미완료이므로 P03-T05 PARTIAL 유지.
- P03-T05 계속: 공용 동기 snapshot·push/config/sync API의 실제 Fake 경로와 strict 모델 변환을 보완한다. Native에서 구현되지 않은 요청은 UNSUPPORTED_OPERATION을 그대로 전달한다.
- C# facade에 capability/diagnostics 캐시와 sync·push permission/register/unregister·service config API를 추가하고 `smoke-csharp-registry.sh` 종료 0. 확인한 경로는 Editor-only Fake이며 Native 구현·Unity Editor 실행은 아니다.
- `check-csharp-compile.sh` 종료 0: 추가된 facade 및 DTO를 포함해 Android/iOS/Editor/미지원 네 분기 독립 컴파일, 경고 0. Unity runtime 실행은 미검증.
- C# facade에 sync·push·config 및 capability/diagnostic snapshot을 추가하고, 오류 원문·token-sized fingerprint 노출 거부를 포함한 독립 .NET smoke 종료 0. 이 결과는 Unity Editor나 실제 Native Provider 실행이 아니다.
- 커밋 전: 추가 facade와 strict wire 모델만 포함. Native 초기화/인증/결제 연결, 공통 이벤트 및 Unity Editor 검증은 미완료로 P03-T05 PARTIAL 유지.

### [P04-T01] 시작 — 2026-11-10 Asia/Seoul
- Android local-mock 수직 경로는 부분 검증, Unity JNI operation 연결은 미완료. 실제 Credential Manager adapter를 독립 작성하고 Google 콘솔/실기기 인증은 USER-AUTH-GOOGLE로 분리한다. 공식 Android/Google nonce·client ID 문서를 확인했다.
- Google Maven metadata 조회 종료 0: 안정 버전 androidx.credentials 1.6.0, credentials-play-services-auth 1.6.0, googleid 1.2.1 확인. 공식 가이드의 알파 예제는 사용하지 않는다.
- `:sdk-android:assembleDebug` 종료 1: googleid 1.2.1의 Kotlin metadata 2.4.0이 현재 Kotlin compiler 2.1과 호환되지 않음. 안정 이전 버전의 실제 빌드 호환성을 확인한다. 이 실행에서 Google Provider는 빌드되지 않았다.
- googleid 1.1.1로 낮춘 `:sdk-android:assembleDebug` 종료 0: Credential Manager 실제 호출 코드 컴파일. 이전 metadata 실패는 재현 후 해결했지만 실 Google 로그인·서버 token 검증은 미실행이다.
- 호환 googleid 1.1.1로 `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. stub gateway/backend로 server nonce 전달·Native 저장·profile 불일치 거부·설정 누락·동시 UI BUSY 확인. XML에서 실제 시험 수·skip 확인한다. 실제 Credential Manager UI·Google 서버 연동은 미실행.
- 정정: JUnit XML은 2건·실패0·skip0이었다. 위 기록 중 동시 UI BUSY는 실제 실행되지 않았다. 해당 테스트가 Kotlin expression body에서 UserProfile을 반환해 JUnit이 인식하지 못한 것이 원인이며 Unit 반환으로 수정한다.
- `:sdk-android:testDebugUnitTest --rerun-tasks` 종료 0, JUnit XML에서 테스트 3건·실패0·skip0 확인. 이번에는 동시 UI BUSY도 실제 실행됐다. Google 계정이나 실제 Credential Manager UI는 미실행.
- `:sdk-android:testDebugUnitTest :sample-app:assembleDebug` 종료 0. JUnit XML에서 Google adapter stub 시험 4건·실패0·skip0 확인(사용자 취소 전파 포함). Mock 샘플 빌드이며 Google 계정 UI와 서버 token 교환은 미실행이다.
- challenge nonce 공백·잘못된 응답을 거부하고 credential/session/challenge 문자열 표현을 정제한 뒤 `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. JUnit XML 4건·실패0·skip0. 서버 실제 challenge/exchange, sample 실 Provider 선택, 공통 UI gate 및 실제 Google 인증은 미구현/미검증이다.
- 커밋 전: Android 실제 호출 adapter와 stub 시험, 버전 근거 및 USER_SETUP 준비 상태를 포함. 선행 서버 인증/샘플 통합이 미완료이므로 P04-T01은 IN_PROGRESS/PARTIAL/WAITING_USER 유지.

### [P04-T02] 시작 — 2026-11-10 Asia/Seoul
- iOS Simulator local-mock은 확인했으나 실제 Apple 인증·서버 verifier는 미구현. AuthenticationServices UI/anchor/nonce와 Native 전용 token 처리 및 fake callback 검증을 별도 구현한다.
- `swift test --package-path ios` 종료 0: 기존 XCTest 12건 통과·local Backend opt-in 1건 skip. macOS에서는 UIKit 조건부 AppleSystemGateway 본문이 컴파일되지 않았고 fake callback 시험도 아직 없다. iOS Simulator 빌드로 실제 API 컴파일을 확인한다.
- `swift test --package-path ios` 종료 0: XCTest 15건 중 14 통과·local Backend opt-in 1 skip. Apple fake gateway/backend 시험 2건에서 raw nonce 전달, 취소, 사용자 불일치 거부, credential revoked 시 로컬 삭제 및 서버 revoke 실패 분리 확인. UIKit 실제 코드는 macOS 조건부 제외되어 아직 미컴파일.
- Apple target을 sample에 연결한 뒤 XcodeBuildMCP `build_sim` Debug 성공(경고/오류 0). 빌드 로그에서 UIKit gateway 파일이 실제 컴파일됐는지 확인한다. Simulator 실제 Apple UI·서명·계정 검증은 미실행.
- Xcode build log에서 `AppleSystemGateway.swift`가 iOS Simulator target으로 실제 컴파일된 것을 확인(검색 종료 0). 실제 Apple authorization UI·계정·server signature 검증은 아님.
- 코드 검토에서 취소 callback이 늦게 도착해 새 요청을 취소하거나 anchor 해제 후 강제 unwrap할 가능성을 발견해 요청별 세대와 안전한 정리를 추가한다.
- Swift 요청별 취소 세대·오래된 delegate 차단 보정 후 macOS `swift test` 종료 0, 14건 통과·1 skip. UIKit 조건부 부분 재빌드 전이며, 검토 중 서버 ISO 시각의 fractional seconds를 기본 formatter가 거부할 수 있어 수정한다.
- Fractional UTC 시각 허용 및 동시 Apple authorization BUSY 시험을 추가한 `swift test --package-path ios` 종료 0: 총 16건 중 15 통과, local Backend opt-in 1 skip. Apple gateway 실제 iOS 컴파일을 재확인한다.
- 보정 후 XcodeBuildMCP `build_sim` Debug 성공(경고/오류 0): UIKit AuthenticationServices gateway 포함 iOS Simulator 컴파일. Apple 계정 authorization, entitlement/서명 및 Backend 서명 검증은 미실행.
- 검증 중 서명 entitlement 예제 파일이 샘플 app bundle에 복사된 것을 발견했다. 비밀값은 없지만 예제는 배포 리소스가 아니므로 XcodeGen source에서 제외하고 별도 새 DerivedData로 확인한다.
- XcodeGen 예제 제외 설정과 문자열 정제 테스트를 반영한 `swift test --package-path ios` 종료 0: 15 통과·local Backend 1 skip. 실제 iOS gateway 재컴파일·clean bundle 점검은 이어서 수행한다.
- 새 DerivedData에서 XcodeBuildMCP `build_sim` 성공(경고·오류 0). 수정된 UIKit gateway의 iOS Simulator 컴파일 완료. 예제 파일이 앱에 포함되지 않는지 별도 확인한다.
- 새 Debug app bundle 검사 종료 0: `*.example` 파일 0개. 검토 중 credential-state 확인과 새 로그인 경합이 새 세션을 지울 가능성을 발견해 동일 provider gate로 직렬화한다.
- Apple 로그인과 credential-state 확인에 공통 provider gate를 적용하고 취소 오류를 표준 CANCELED로 매핑한 뒤 `swift test --package-path ios` 종료 0: 15건 통과·1건 skip. Fake gateway의 동시 state 검사 BUSY 확인. iOS 실제 gateway 수정본 컴파일은 이어서 확인한다.
- 최종 Apple gateway 수정본에 대한 XcodeBuildMCP `build_sim` Debug 성공(경고·오류 0). AuthenticationServices 실제 사용자 UI·서명·계정·서버 교환은 미실행.
- 커밋 전: Swift Apple adapter, fake gateway 시험, iOS Simulator 컴파일 및 entitlement 예제를 포함. Backend verifier·실제 샘플/Unity 연결과 Apple 계정 검증은 남아 P04-T02 IN_PROGRESS/PARTIAL/WAITING_USER 유지.

### [P04-T03] 시작 — 2026-11-10 Asia/Seoul
- Google/Apple 실제 공개키 검증 코드와 로컬 서명 fixture를 작성한다. 인증 요청 수 제한은 사용자 수치 결정 대기이므로 그 결정에 의존하는 공개 route는 아직 활성화하지 않는다.
- 공식 Google discovery와 Apple JWKS를 읽어 현재 두 Provider의 공개 ID-token key algorithm이 RS256임을 확인(조회 종료 0). Spring Security 공식 문서의 JWKS cache·30초 통신 timeout과 issuer/audience/expiry 계약을 확인했다. 요청별 audience와 DB에 저장된 nonce hash를 비교하며, 실 Provider 서명 성공으로 기록하지 않는다.
- `./backend/gradlew -p backend test` 종료 0: IdentityVerifier JUnit XML 3건·실패0·skip0. 메모리에서 생성한 RSA 서명 fixture로 Google 양 issuer·Apple issuer, 잘못된 audience/issuer/nonce/만료/알고리즘/서명 및 JWKS network 오류 거부를 확인했다. 실제 Provider 발급 토큰 테스트가 아니다. DB opt-in 테스트는 별도다.
- 검토 중 Google의 두 허용 issuer 표기를 그대로 identity key에 쓰면 같은 subject가 서로 다른 계정으로 분리될 수 있어, 검증 후 canonical issuer로 정규화한다.
- 사용자 결정 수신: 단일 서버 IP별 challenge 30회/분·token 교환 10회/분, 설정 가능. DECISIONS에 기록했으며 rate limiter 및 실제 route 적용은 아직 미구현이다.
- Google issuer 표기를 동일한 canonical issuer로 정규화 후 Backend test 종료 0. 사용자 승인 rate limit은 단일 서버 메모리에서 IP별 rolling 1분으로 구현하며 reverse proxy header는 신뢰하지 않는다.
- 사용자 승인 rate limit과 rolling-minute 구현 후 `./backend/gradlew -p backend test` 종료 0: Identity verifier 3건 및 rate limiter 1건 XML에서 실행·통과 확인. IP별·operation별 분리와 1분 만료를 단위 검증했다. HTTP route 연동과 다중 서버 전역 제한은 아직 검증하지 않았다.
- 커밋 전: 실제 고정 JWKS endpoint verifier와 로컬 서명 fixture, 사용자 결정 rate limiter만 포함. challenge 발급·원자적 소비·실제 HTTP 인증 연결과 외부 실연동은 미완료이므로 P04-T03 PARTIAL/WAITING_USER 유지.
- P04-T03 계속: app별 복수 audience 허용 설정과 DB 단일 사용 challenge, 검증 후 identity/session 생성의 원자적 경로를 구현한다. 실제 client ID와 bundle ID는 사용자 설정 전까지 요구만 하고 기본값을 넣지 않는다.
- app별 복수 audience를 단일 signature 검증 후 대조하도록 보정하고 Backend test 종료 0. 단일 사용 challenge·identity/session transaction 및 HTTP 연결은 다음 구현이다.
- 単一使用 challenge・app別 audience・signature 検証後の identity/session transaction と HTTP route を追加し `./backend/gradlew -p backend test` 종료 0。既存 unit test のみで新しい DB challenge race・HTTP route は未検証。
- `./backend/gradlew -p backend test` 종료 0: app/provider별 audience 설정과 복수 audience의 authorized-party 검사를 포함해 AudiencePolicy 1건·IdentityVerifier 4건 실제 실행·통과. DB 단일 사용 경합 및 HTTP 통합은 아직 미실행.
- 전용 PostgreSQL container `up -d --wait` 종료 0. 신규 app별 audience·서명 fixture·동시 challenge 재사용 시험은 격리된 sandbox DB에서 실행할 예정이다.
- `gamebridge_auth_verify_20261110` DB가 없음을 확인하고 별도 생성(조회·생성 각 종료 0). 기존 DB는 지우거나 수정하지 않는다.
- 127.0.0.1:18082 포트가 비어 있음을 확인한 후 synthetic audience 설정과 별도 DB로 sandbox profile 서버 기동. `/health` HTTP 200(폴링 종료 0). 실제 Provider 토큰이나 사용자 계정은 사용하지 않았다.
- `GAMEBRIDGE_RUN_AUTH_DB_TESTS=true ... ./backend/gradlew -p backend test --rerun-tasks` 종료 0. JUnit XML DB 시험 1건·실패0·skip0: challenge nonce hash 저장, 동시 재사용 1건만 성공, subject 재로그인 동일 user, 잘못된 audience 실패 시 challenge 미소비 확인. 자체 서명 시험이며 실제 Provider는 아니다.
- `GAMEBRIDGE_TEST_BASE_URL=http://127.0.0.1:18082 python3 scripts/smoke-auth-rate-local.py` 종료 0: sandbox 시험 서버에서 challenge 30회·잘못된 교환 10회 허용 후 각각 429, X-Forwarded-For 위장 무시, requestId 일치와 오류의 token 미노출 확인. 실제 Provider token은 사용하지 않았다.
- profile 응답에 서버 저장 displayName을 추가하고 Google issuer 두 표기가 동일 사용자로 연결되는 DB 검증을 재실행해 종료 0. 잘못된/누락 audience 처리와 민감 DTO 문자열 정제를 이어서 확인한다.
- 누락 audience 실패 처리와 민감 session/refresh/proof/token DTO의 toString 정제를 추가한 뒤 opt-in DB 포함 Backend test 종료 0. 실제 Google/Apple token은 사용하지 않았다.
- Backend 민감 DTO 문자열 정제 시험 1건 실행·통과(XML 확인), Gradle test 종료 0. Native response 정제 시험과 실제 HTTP 교환 통합은 이어서 수행한다.
- Native response 문자열 정제 후 `:sdk-core:test` 및 `swift test --package-path ios` 각각 종료 0. Swift XCTest 15 통과·local Backend 1 skip; Android core도 opt-in local Backend 시험은 미실행. 실제 Provider 검증 아님.
- opt-in `./backend/gradlew -p backend test --rerun-tasks` 종료 0: sandbox Spring HTTP 통합 시험 1건, DB 경합 시험 1건 및 identity fixture 시험이 실제 실행되어 통과. 시험 전용 메모리 RSA decoder로 Google/Apple 교환·/me displayName·replay 409·잘못된 audience 후 올바른 재시도를 확인. 실제 Provider 서명 검증 PASS는 아니다.
- opt-in `./backend/gradlew -p backend test bootJar --rerun-tasks` 종료 0: 격리 sandbox DB와 테스트 전용 RSA decoder를 사용한 HTTP 성공/거부·DB replay 경합 검증, sandbox 개발 auth 404 확인. JUnit XML에서 대상 시험 실행·0 실패·0 skip을 확인했고 배포 jar에 test 전용 verifier/key fixture가 없는 것을 검사했다. 실제 Google/Apple token 검증은 미실행이다.
- 필수 exp·nonce·subject 누락 거부 시험을 추가한 opt-in `test bootJar --rerun-tasks` 종료 0. IdentityVerifier 6건, HTTP 통합 1건, DB 경합 1건, rate 1건이 XML상 모두 실행·통과. 별도 finalization DB 시험 2건은 이번 실행에서 skip이다. 자체 서명 fixture만 사용했다.
- sandbox HTTP 시험 서버 Ctrl-C 종료 130. 전용 DB volume을 보존하고 container만 정지한다.
- sandbox 시험 DB container 정지 종료 0, 데이터와 전용 volume은 보존했다. 진행 원장 집계가 실제 Task 행과 달라진 것을 발견해 행 기준으로 재계산한다.
- 커밋 전: HTTP/DB 실험과 자체 서명 fixture 결과를 증거에 기록하고 실제 Task 행 기준 집계를 재계산했다. P04-T03의 구현·필수 로컬 검증은 완료로 표시하되 실제 Google/Apple 토큰 및 실기기는 WAITING_USER로 유지한다.

### [P04-T04] 시작 — 2026-11-10 Asia/Seoul
- P04-T03 서버 검증은 로컬 완료, 외부 토큰은 대기. Native 세션을 app·mode·Backend에 결속하고 refresh 응답 유실 시 이전 refresh 재사용을 막는다. Mock/실 Provider 실행은 별도 판정한다.
- Kotlin LOCAL_MOCK session에 app/mode/Backend 결속을 추가하고 refresh 전 암호화 저장소를 token 없는 tombstone으로 원자 교체하도록 변경. `:sdk-core:test` 종료 0이나 신규 유실·환경 불일치 시험은 아직 미실행이다.
- `:sdk-core:test --rerun-tasks` 종료 0, LocalMockRefreshTest XML 1건·실패0·skip0: 다른 app 설정에서 기존 저장 데이터 사용 거부, refresh 응답 timeout 뒤 tombstone 유지 및 앱 재생성 시 이전 refresh 재사용 없음 확인. mock HTTP fixture이며 실제 Google 세션 검증 아님.
- Swift LOCAL_MOCK 저장 record에 app·mode·Backend 결속 및 refresh 전 tombstone을 추가한 뒤 기존 `swift test` 종료 0(15 통과·1 skip). 코드 검토 중 session 불일치·갱신 중 재로그인 경합을 발견해 추가 보정한다.
- 신규 Swift session fixture `swift test` 종료 1: 한 줄 JSON에 Swift 다중행 문자열 구문을 잘못 사용해 테스트 컴파일 실패, 실행 0건. raw string 구문으로 수정한다.
- Swift 새 session 시험은 최초 raw 문자열 구문 오류로 컴파일 실패 후 수정해 `swift test` 종료 0: 총 18건 중 17 통과·1 skip. Mock URLProtocol로 refresh 응답 유실 시 tombstone 유지, 다른 app 복원 거부, 늦은 401 두 건이 refresh 한 번만 발생시키는지 확인. 실제 플랫폼 인증 아님.
- Google·Apple Native 저장 session에도 app/mode/Backend provenance 필드를 추가해 다른 환경의 저장값을 오인하지 않도록 보정. `swift test --package-path ios` 종료 0: 17건 통과·1 skip. Apple/Google 실제 token refresh는 아직 연결되지 않았다.
- `:sdk-core:test :sdk-android:testDebugUnitTest :sample-app:assembleDebug` 종료 0. session provenance 변경 후 core/Google stub 시험 및 Android Mock 샘플 빌드 재확인. opt-in Backend 통합은 이 실행에서 skip이다.
- 전용 local-mock DB·서버를 재기동. 새 session 한 행만 만료시킨 뒤 병렬 API 호출에서 refresh 회전 횟수를 검사한다.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... :sdk-core:test --rerun-tasks` 종료 0, local Backend 통합 XML 2건·실패0·skip0. 테스트가 생성한 session만 만료시킨 후 8개 동시 잔액 호출과 refresh history 1건을 확인했다. Kotlin 구현은 요청을 mutex로 직렬화하므로 병렬 조회 성능 검증은 아니다.
- opt-in local Backend을 포함한 Android `:sdk-core:test :sdk-android:testDebugUnitTest :sample-app:assembleDebug --rerun-tasks` 종료 0. XML 확인: LocalMockIntegration 2건·Refresh 1건·Google stub 4건 모두 실패/skip 0. 다른 app·서버 및 Google 저장 session을 Mock Backend에 보내지 않고 저장값을 보존함을 확인.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios` 종료 0: XCTest 18건·실패0·skip0. Mock HTTP 유실·늦은 401 및 실제 local Backend 수직 경로, Apple 저장 session을 Mock 서버에 보내지 않고 보존하는 분기를 확인했다. 실제 Apple token refresh는 미구현이다.
- session provenance/tombstone 변경 후 XcodeBuildMCP `test_sim` 성공: iOS 26.5 UI smoke 1건·실패0·skip0, local-mock 로그인·구매·재시작 Keychain 복원·로그아웃 재확인. 실제 Apple 계정/StoreKit은 아니다.
- Google Native provider에 app/mode/Backend 결속 복원·직렬화된 refresh·응답 유실 tombstone·오프라인 logout을 추가하고 `:sdk-android:testDebugUnitTest :sample-app:assembleDebug` 종료 0. XML 6건·실패0·skip0: stub에서 8개 동시 복원 refresh 1회, 유실 후 재사용 금지, 서버 revoke 실패에도 로컬 삭제 확인. 실제 Google token/기기 검증은 아니다.
- Apple Native session 확장 후 `swift test` 종료 1: XCTest assertion의 autoclosure 안에 async task.value를 넣어 테스트 코드 컴파일 실패. 실행 0건이며 값을 먼저 await하도록 수정한다.
- Apple Native provider의 8개 동시 복원 single-flight·응답 유실 tombstone·다른 서버 결속 및 offline revoke 실패 분기를 fake backend로 구현. 첫 테스트 컴파일 오류 수정 후 `swift test` 종료 0: 19건 통과·1 skip. 실제 Apple 계정/Backend 통합은 미실행.
- 검토 중 refresh tombstone 이후 로그아웃이 원격 revoke를 확인할 수 없는데 성공을 반환할 수 있음을 발견했다. 로컬 삭제를 먼저 수행하되 미확인 원격 revoke를 명시적으로 보고하도록 보정한다.
- Kotlin Mock/Google logout에서 refresh 유실 tombstone을 지운 후 `REVOCATION_UNCONFIRMED`를 반환하고, 저장된 다른 환경 session은 삭제하지 않도록 보정. opt-in Backend 포함 Android 테스트·샘플 빌드 종료 0; LocalMock 통합 2, 유실 1, Google fake 6건 모두 실패/skip 0 확인. 실제 Google 인증은 미실행.
- Swift LocalMock/Apple logout에 저장된 세션의 환경 재확인과 `REVOCATION_UNCONFIRMED` 표시를 추가한 뒤 `swift test` 종료 0: 기존 19건 통과·local Backend 1건 skip. 유실 후 logout 및 동시 복원 검증을 추가한다.
- Swift에서 동일 저장 세션의 동시 복원과 늦은 401이 refresh를 1회만 수행하는 Mock URLProtocol 시험을 추가하고, tombstone logout을 `REVOCATION_UNCONFIRMED`로 보고하도록 보정. `swift test` 종료 0: 20 통과·local Backend 1 skip. Apple 실제 실연동 검증 아님.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios` 종료 0: XCTest 21건·실패0·skip0. 새 session format 및 logout 보정 후 실제 local-mock Backend와 Swift 수직 시험도 재통과. 실제 Apple/Google 인증은 아니다.
- session provenance와 logout 보정 후 XcodeBuildMCP `test_sim` 성공: iOS 26.5 local-mock UI 1건·실패0·skip0, 로그인·구매·재시작 복원·logout 재확인. 실제 Apple 인증/결제 아님.
- 이번 작업 전용 Android 36 AVD를 재기동하고 boot_completed 확인(종료 0). 기존 사용자 AVD는 사용하지 않았다.
- 전용 AVD에 최신 Debug APK 설치·Activity 실행·UI dump 종료 0. 새 session format의 로그인/앱 재시작/복원을 자동 입력으로 확인한다.
- `python3 artifacts/android-avd/session-ui-smoke.py` 종료 1: 첫 로그인 뒤 재시작한 화면에서 Initialize 요소를 찾지 못해 UI 복원 확인 전 중단. 자동 입력/화면 상태를 조사하며 성공으로 기록하지 않는다.
- `dumpsys window` 종료 0: 실패 시 전용 emulator가 launcher에 있었다. 자동화의 무조건 Back 입력이 키보드가 닫힌 상태에서 앱을 닫은 것으로 보여 키보드 표시 상태를 확인하고 보정한다.
- 전용 AVD에서 화면 준비 후 테스트 키 입력 시 `dumpsys input_method`의 `mInputShown=true`를 확인했다. 키보드 표시일 때만 Back을 사용해 수동 복원 경로를 재검증한다.
- 화면 준비 확인 후 재시도에서 `Initialized LOCAL_MOCK`, 이어 앱 재시작 후 `Restored` 표시 확인(각 UI dump 종료 0). 전용 Keystore에 저장된 새 session 형식으로 local-mock 복원된 결과이며 Google 실인증은 아니다. ENV-004 재발 원인은 UI 자동화였고 재검증으로 해소.
- AVD에서 `Signed out` 표시 후 SDK private preferences에 session 항목이 없음을 내용 비출력 검사(종료 0). 원격 logout 결과가 성공한 local-mock 상황이며 오프라인 revoke 보류 상태는 별도 stub 시험으로 구분한다.
- `adb -s emulator-5566 emu kill` 종료 0: 이번 작업의 전용 AVD만 정지하고 데이터는 보존했다.
- Native logout의 remote revoke 실패를 정제된 `REVOCATION_UNCONFIRMED`로 표시하고 Swift session 시각 검증을 강화. Android opt-in Backend 포함 core·Google stub·샘플 빌드 종료 0, 대상 시험 2+1+6건 실제 실행·실패0·skip0.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios` 종료 0: XCTest 21건·실패0·skip0. mock timeout 후 tombstone, 다른 환경 거부, 동시/지연 401 single-flight 및 Apple fake 복원·오프라인 logout 분기를 확인했다. 원격 revoke 미확인을 UI가 숨기지 않도록 샘플을 보정한다.
- Android 샘플이 logout 실패 시에도 화면의 이전 재화 상태를 지우고 원격 revoke 미확인을 명시하도록 수정. `:sample-app:assembleDebug` 종료 0, 화면 분기 실제 실행은 아직 미검증.
- XcodeBuildMCP `build_sim` Debug 성공(경고·오류 0): Swift 샘플의 logout 실패 표시 변경 컴파일. 실패 UI 직접 실행은 미검증.
- Kotlin logout 중 coroutine 취소도 원격 revoke 미확인으로 구분하고 Google restore 취소를 CANCELED로 정제. local Backend opt-in 포함 Android core·Google stub 시험 및 sample build 종료 0.
- Kotlin Native HTTP가 401 인증 실패/세션 만료, 409 구매 계정·멱등 충돌, 429 제한 및 설정/네트워크 오류를 허용된 코드만으로 구분하도록 보정. local Backend opt-in 포함 Android core·Google stub·sample build 종료 0; 오류 메시지의 임의 token은 노출하지 않도록 시험. Swift 동등 검증은 이어서 실행한다.
- Swift Native HTTP도 401 인증/세션, 409 거래 충돌, 429 제한과 503 설정/네트워크를 허용 목록으로 구분하도록 수정. opt-in local Backend 포함 `swift test` 종료 0: XCTest 22건·실패0·skip0. Google/Apple 실제 발급 token 시험은 아니다.
- 다른 app/server/provider의 저장 세션을 잘못된 client logout이 삭제하지 않도록 하는 Android 검증을 추가했고 local Backend opt-in core·Google stub·sample build 종료 0. Swift 동일 분기는 이어서 시험한다.
- Swift에서 잘못된 app/server 세션에 대한 logout이 저장값을 보존하는 검사까지 포함해 local Backend opt-in `swift test` 종료 0: XCTest 22건·실패0·skip0.
- P04-T04 계속: 계획의 access 또는 refresh 기반 logout 계약에 비해 서버는 access만 받는 누락을 발견했다. 소유 세션의 현재 refresh로 revoke하는 경로를 추가하고, 미확인 revoke는 계속 명시한다.
- 서버 refresh 기반 logout 경로를 추가하고 `./backend/gradlew -p backend test` 종료 0. 실제 PostgreSQL/HTTP 경로 및 Native fallback은 아직 미검증이다.
- Native Google/Apple 및 local-mock logout에서 access 만료 시 현재 refresh로 server revoke를 요청하도록 추가. Android core·Google stub·sample build 종료 0, opt-in 실제 Backend 검증은 아직 실행 전이다.
- `:sdk-core:test --rerun-tasks` 종료 0, LocalMockRefreshTest 2건·실패0·skip0: 저장 session으로 access 만료 logout 시 refresh fallback 및 local 삭제를 mock HTTP로 확인. 실제 Backend fallback은 후속 검증한다.
- `swift test` 종료 1: 새 logout fallback 관련 시험 2건 실패, 전체 24건 중 2 skip. 실패 원인을 로그에서 확인하고 성공으로 기록하지 않는다.
- 실패 2건은 테스트 URLProtocol에서 refresh logout의 `request.httpBody`가 비어 있어 확인 counter가 0으로 남은 assertion이다. URLSession이 제공하는 body stream도 읽도록 fixture를 보정하며 실제 서버 동작으로 대체해 성공을 주장하지 않는다.
- Swift URLProtocol fixture가 request body를 stream으로 전달하는 점을 반영한 뒤 `swift test` 종료 0: 24건 중 22 통과·local Backend 2 skip. LocalMock 및 Apple HTTP revoke의 access 401→refresh fallback은 mock transport에서 확인했으며 실제 서버 검증은 아직 미실행.
- 변경 전 local-mock 서버 Ctrl-C 종료 130. refresh logout 경로를 포함한 새 서버로 재기동한다.
- refresh logout 구현을 포함한 local-mock 서버와 전용 DB가 정상 기동했다. 테스트 생성 session만 만료시키고 refresh revoke·연결 token 삭제를 확인한다.
- 새 local-mock 서버에서 `smoke-auth-local.py` 종료 0: 16 assertion(만료 access 후 현재 refresh logout·재호출·refresh 폐기 포함). `smoke-device-local.py` 종료 0: 19 assertion(동일 refresh logout의 해당 push token 삭제 포함). 실제 스토어/원격 push 아님.
- local Backend opt-in Android core·Google stub·샘플 빌드 종료 0. XML: LocalMockIntegration 3건·Refresh 2건·Google stub 6건, 실패0·skip0. 실제 local-mock DB에서 access를 만료시킨 본인 테스트 session을 Native client가 refresh 기반으로 revoke한 것을 확인.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios` 종료 0: XCTest 25건·실패0·skip0. 실제 local-mock PostgreSQL에서 만료 access 후 Swift Native client가 refresh 기반 logout을 수행하고 해당 session revoke를 확인. Apple 실제 계정은 사용하지 않았다.
- Google HTTP revoke test seam 추가 후 Android build 종료 1: constructor lambda의 suspend 함수 타입 추론 실패. 테스트 실행 전 컴파일 오류이며 명시적 suspend 함수형 타입으로 수정한다.
- 명시적 suspend 타입 보정 후 local Backend opt-in Android core·Google adapter 테스트·sample build 종료 0. XML: local Backend 3건·Mock refresh 2건·Google fake 7건 모두 실패/skip 0. Google HTTP revoke fallback은 stub transport로 확인했고 실제 Google 계정 사용은 아님.
- local Backend opt-in `swift test --package-path ios` 종료 0: XCTest 25건·실패0·skip0. 실제 local-mock DB에서 access 만료 후 Swift client의 refresh logout 및 revoke 확인, Apple HTTP fallback은 URLProtocol stub으로 확인했다. 실제 Apple token은 사용하지 않았다.
- 최신 session·logout 변경 후 XcodeBuildMCP `test_sim` 성공: iOS 26.5 local-mock UI 1건·실패0·skip0. 실제 Apple 인증·StoreKit/원격 push 미실행.
- `bash scripts/smoke-local.sh` 종료 1: Mock 인증 16·구매 13·기기 19 assertion 각각 통과했지만 보호된 개발 push send가 미구현이므로 집계는 실패 유지. 실제 Provider 인증/구매/원격 푸시 통과가 아니다.
- local-mock 테스트 서버 Ctrl-C 종료 130; 전용 DB는 삭제하지 않고 정지한다.
- `GAMEBRIDGE_RUN_AUTH_DB_TESTS=true ... ./backend/gradlew -p backend test --rerun-tasks` 종료 1: AuthFlowDatabaseTest 및 AuthHttpIntegrationTest 각 1건 실패. 원인을 확인하기 전 통합 성공으로 기록하지 않는다.
- 실패 원인 조사: 전용 PostgreSQL container가 `exited`, exit 0, OOM false이며 로그에는 정상 fast shutdown이 기록돼 있다. 중지 주체는 확인하지 못했다. DB가 없어 2개 opt-in 시험이 실패한 환경 사건이며 테스트 DB를 보존한 채 재기동한다.
- 전용 PostgreSQL container `up -d --wait` 종료 0, healthy. 사용자 DB 삭제 없이 실패한 두 DB 시험을 재실행한다.
- DB healthy 후 동일 opt-in Backend test 재실행 종료 0. AuthHttpIntegrationTest와 AuthFlowDatabaseTest 각각 1건·실패0·skip0. sandbox 자체 서명 fixture에 대해서도 access 만료 후 현재 refresh logout과 멱등 재호출을 확인. ENV-008 해소.
- `curl ...:18080/health` 종료 7: local-mock 서버가 현재 실행 중이지 않음. sandbox DB 시험은 통과했으며 Native 최종 회귀를 위해 전용 서버를 다시 시작한다.
- local-mock server/전용 DB가 새 logout 코드로 기동했다. Native 회귀는 공유 Mock 잔액이 겹치지 않도록 Kotlin과 Swift를 순차 실행한다.
- 최신 서버로 Android opt-in core·Google stub·sample build `--rerun-tasks` 종료 0. XML: local Backend 3건, refresh fixture 2건, Google stub 7건, 실패/skip 0. 실 Google 계정 UI·token 사용은 아니다.
- 최신 서버로 Swift local Backend opt-in `swift test` 종료 0: XCTest 25건·실패0·skip0. Native Mock session/refresh logout과 Apple fake callback을 확인했으며 실제 Apple 계정은 사용하지 않았다.
- 최신 refresh logout 및 session 변경 후 XcodeBuildMCP `test_sim` 성공: iOS 26.5 local-mock UI 1건·실패0·skip0. Google/Apple 계정·실제 구매·원격 push는 실행하지 않았다.
- 테스트 서버 Ctrl-C 종료 130. 전용 PostgreSQL container를 volume 삭제 없이 정지한다.
- 전용 DB `docker compose ... stop` 종료 0, volume/시험 데이터 보존. 검토 중 계획의 access 15분·refresh 7일은 코드에서 고정돼 설정 변경이 불가능한 점을 확인해 명시적 설정으로 노출한다.
- 계획의 세션 TTL을 `GAMEBRIDGE_SESSION_ACCESS_TTL_SECONDS`(기본 900), `GAMEBRIDGE_SESSION_REFRESH_TTL_SECONDS`(기본 604800)로 설정 가능하게 추가한 뒤 Backend test 종료 0. Spring 설정값이 실제 session에 반영되는지는 DB 통합 시험으로 확인한다.
- 전용 PostgreSQL `up -d --wait` 종료 0, healthy. 격리된 sandbox 시험에서 임시 TTL 설정이 응답에 실제 반영되는지 확인한다.
- opt-in sandbox DB `./backend/gradlew -p backend test --rerun-tasks` 종료 0. AuthHttpIntegrationTest 1건 실패/skip 0: 시험 전용 access TTL 설정이 발급 시각에 반영되고 refresh logout·재호출이 통과했다. 실제 Provider token은 아니다.
- refresh 7일 TTL의 기준(최초 로그인 고정 또는 갱신 때마다 연장)은 계획에 명시되지 않아 사용자에게 선택을 요청했다. 현재 고정 만료 코드는 기존 미확정 구현일 뿐 승인된 정책이 아니며, 답변 전 의존 동작을 완료·배포하지 않는다.
- P04-T04 독립 산출물 `docs/SECURITY.md` 초안을 작성해 현재 token 경계·검증된 Mock·미완료 실제 Provider 및 revoke 한계를 기록. refresh 만료 기준은 사용자 결정 대기이며 이 문서에 임의 확정하지 않았다.

### [P05-T01] 시작 — 2026-11-10 Asia/Seoul
- P04-T04 refresh TTL 정책은 사용자 결정 대기. 구매 account binding의 독립적 서버 저장·고유성은 계획에 확정되어 있어 먼저 구현한다. 기존 session의 app 귀속은 임의 추정하지 않는다.
- account binding 초안 컴파일용 `./backend/gradlew -p backend test` 종료 0. 새 DB test는 환경 미설정으로 skip이므로 아직 동시성 증거가 아니다. 플랫폼 간 불필요한 상관을 줄이기 위해 Apple과 Google에 서로 다른 무작위 binding을 사용하고 격리된 test schema에서 검증한다.
- 전용 local-mock DB healthy 확인(`up -d --wait` 종료 0). UUID로 새 test schema를 만들고 원본 migration을 적용해 binding 동시성 시험을 실행한다. 기존 public schema 데이터는 수정하지 않는다.
- DB opt-in `./backend/gradlew -p backend test --rerun-tasks` 종료 0, PurchaseBindingsDatabaseTest XML 1건·실패0·skip0. 격리 schema에서 10개 동시 생성이 동일 user/app에 같은 binding을 반환하고 app·user·store별로 구분됨을 확인. 새 시험 schema는 데이터 보존을 위해 삭제하지 않았다.
- 커밋 전: store별 임의 UUID binding DB 서비스와 격리 schema 동시성 시험만 포함. 기존 session app 귀속, Native 전달·상태기계·스토어 검증은 미구현으로 P05-T01 PARTIAL 유지. refresh TTL 선택은 여전히 대기.
- P05-T01 계속: 세션 TTL 결정과 독립적인 Native 거래·지급·완료 처리 상태기계를 작성한다. 클라이언트는 자체 재화 지급 없이 서버 검증 결과만 반영한다.
- `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. Kotlin purchase 상태기계 XML 1건·실패0·skip0: pending grant 거부, user/binding 불일치 거부, 서버 grant 중복과 finalization 멱등성 확인. Native store 연결·실제 지급은 아니다.
- `swift test --package-path ios` 종료 0: purchase 상태기계 1건 포함 총 26건 중 23 통과·local Backend 3 skip. pending grant 거부, account mismatch, 중복 grant, finalization 상태를 확인. 실제 StoreKit 거래 검증은 아니다.
- 거래 binding/transaction 값의 문자열 표현을 정제한 뒤 Android 상태기계 unit test 재실행 종료 0. Swift 동일 변경을 이어서 확인한다.
- Swift ServerGrant 문자열 정제 후 `swift test --package-path ios` 종료 0: 23 통과·local Backend 3 skip. Native 상태기계는 서버 검증 결과를 상태로 반영할 뿐 자체 코인 지급을 하지 않는다.
- 커밋 전: Android/Swift 거래 상태기계와 단위 시험만 포함. server app scope·binding API·실제 구매 검증 및 StoreKit/Play 연결은 미완료이므로 P05-T01 PARTIAL 유지.

### [P05-T02] 시작 — 2026-11-10 Asia/Seoul
- server binding 공개 API와 실제 구매 검증은 미완료이나 Native Play Billing 실제 호출은 독립 작성한다. Google 공식 문서의 pending 미지급, 서버 consume/ack 책임과 supported version을 확인했다. refresh TTL 결정과 무관한 작업이다.
- Google Maven metadata 및 공식 release/deprecation 문서 확인: Billing 9.1.0 안정 버전. 의존성 추가 후 `:sdk-android:assembleDebug` 종료 0; 실제 Billing adapter와 구매는 아직 작성·실행 전이다.
- Play Billing 9.1 실제 gateway 초안의 `:sdk-android:assembleDebug` 종료 1: nullable offerToken을 non-null API에 직접 전달한 Kotlin 컴파일 오류. null/empty를 분기해 재빌드한다. 실제 스토어 UI는 실행하지 않았다.
- nullable offerToken 보정 후 `:sdk-android:assembleDebug` 종료 0, BUG-003 컴파일 오류 해소. 실제 Play Billing 9.1 조회·UI·callback·복구 호출 코드는 있으나 Backend proof sink 연결과 실제 Play 실행은 미완료다.
- 검토 중 Backend 응답이 다른 proof에 대한 결과일 가능성을 막도록 transaction fingerprint와 account binding 확인을 강화한다.
- Play fake boundary 테스트 추가 후 Gradle 종료 1: FakePlayGateway의 public `observer` setter가 `setObserver` 메서드와 JVM signature 충돌. 제품 거래 시험은 실행되지 않았고 테스트 변수명을 수정한다.
- 테스트 변수 충돌 수정 후 `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. JUnit XML Play boundary 4건·실패0·skip0: verifier 없을 때 UI 시작 차단, pending/계정 불일치/수량 2 미검증·미지급, 서버 응답 proof fingerprint 일치/불일치, raw proof 정제 확인. Fake gateway/sink 시험이며 실제 Play 결제는 아니다.
- 구매 증빙의 기기 내 동시 서버 검증 한도는 계획에 없어 사용자 선택을 요청했다. 선택 전 실제 verifier 조립·구매 UI를 활성화하지 않으며, callback queue와 검증 동시성은 명시 값이 있을 때만 사용한다.
- 사용자 결정 전 실제 검증 동시성 값이 없으면 구매 UI와 서버 proof 검증을 활성화하지 않도록 수정하고 bounded callback queue를 추가. fake boundary 테스트 재실행 종료 0; 실제 Play 이용은 아직 미실행.
- 검토 중 무관한 지연 구매 callback이 현재 UI 대기 요청을 잘못 종료할 수 있어 product별 router로 분리한다.
- Play callback router 보정 후 `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. Billing boundary XML 5건·실패0·skip0: 무관한 callback이 현재 구매 대기를 소비하지 않음을 추가 확인. 실제 Play UI·서버 proof 검증은 미실행.
- Play gateway 검토에서 계정 변경 중 늦은 검증 응답 노출, 미완료 callback 대기와 worker 예외 시 소비 중단 가능성을 발견했다. 계정 재확인·기본 timeout·worker 오류 격리를 추가한다.
- Play gateway timeout·계정 재확인 추가 후 Android build 종료 1: `withTimeout` lambda 내부에서 허용되지 않는 return 문법. 위치를 확인해 수정한다. 사용자 결제 UI는 실행하지 않았다.
- `recover` lambda return 수정 후 `:sdk-android:testDebugUnitTest :sdk-android:assembleDebug` 종료 0. Play 실제 UI는 미실행이고, 다른 계정으로 전환된 동안 지연된 검증 결과가 새 UI로 전달되지 않는지 fake 경계 시험을 추가한다.
- Play gateway에 기본 timeout·예외 격리·검증 중 계정 전환 재확인을 반영하고 fake boundary 시험 재실행 종료 0. XML 7건·실패0·skip0: 동시성 미설정 구매 UI 차단, 전환 후 stale 성공 이벤트 억제 포함. 실제 Play 연동은 USER-BILLING-GOOGLE 대기.
- Play adapter fake test/compile partial 결과를 보존하면서 사용자에게 기기별 증빙 검증 동시성을 문의한 상태다. 선택 없는 production 구성은 구매 UI를 시작하지 않는다.
- Play adapter에서 client `consumeAsync`·`acknowledgePurchase` 호출이 없음을 소스 검사(종료 0). Billing 9.1 의존성을 포함한 `:sample-app:assembleDebug` 종료 0. 샘플은 아직 LOCAL_MOCK이며 실제 Play UI와 상품 조회를 실행하지 않았다.
- 커밋 전: Play Billing 실제 gateway와 fake 경계 검증만 포함. 사용자 검증 동시성 결정, 실제 서버 verifier/sink·binding API·consumer 연결 및 실제 Play 테스트가 남아 P05-T02 PARTIAL/WAITING_USER 유지.

### [P05-T03] 시작 — 2026-11-10 Asia/Seoul
- 실제 StoreKit 2 경계를 작성한다. 서버 검증 연결 및 기기별 검증 동시성 결정 전 구매 UI를 차단하며, 실제 Apple 거래와 로컬 테스트를 구분한다.
- StoreKit 실제 API 경계 초안을 작성했다. 컴파일 전이며, 서버 sink·검증 동시성 미설정 시 구매를 차단한다. 이제 Swift 빌드를 확인한다.
- `swift test --package-path ios` 종료 0: 26건 중 23 통과, local Backend opt-in 3 skip. StoreKit API 컴파일 확인이며 거래 실행 증거가 아니다. grant/account/transaction 경계 단위시험을 추가해 재검증한다.
- StoreKit grant 경계 단위시험 1건 통과: account 전환·transaction 불일치 거부와 JWS 문자열 정제 확인. StoreKit 실제 거래 시험이 아니다.
- 커밋 전: StoreKit API 호출 및 grant 경계만 부분 구현. .storekit 구성·scheme·실거래·server sink·검증 동시성 정책은 미완료. 동시성 한도 초과 시 미완료 거래는 추후 복구가 필요하고 자동 재시도는 미구현이다. P05-T03 PARTIAL을 유지한다.

### [P05-T04] 시작 — 2026-11-10 Asia/Seoul
- 실제 스토어 서버 검증을 공식 라이브러리와 가짜 응답으로 구현한다. 외부 credential 없이 통과한 로컬 검증을 실제 스토어 검증으로 기록하지 않는다.
- Apple 공식 Java server library 5.2.0과 Google 공식 구매 상태 문서를 확인했다. 먼저 의존성 해석과 공개 API를 확인한다.
- 사용자 결정 수신: refresh 기본 만료는 최초 로그인부터 7일 고정, 기기별 구매 증빙 검증 기본 동시성은 1건(변경 가능). 문서에 기록하고 각 코드와 검증에 반영한다.
- 검증 중 Android Gradle 종료 1: 이 셸에 Android SDK 환경 변수가 없어 SDK 위치를 찾지 못했다. 기존 설치 위치를 확인해 환경 변수로 재실행한다. 제품 테스트 실패는 아니다.
- Android SDK 환경 변수를 기존 설치 위치로 설정해 unit test 재실행 종료 0. Swift StoreKit 경계 unit test 1건 통과. 기본 동시성 1 반영 결과이며 실제 구매 검증은 아니다. 기존 refresh 구현은 갱신 시 최초 만료를 유지한다.
- 커밋 전: 사용자 결정 문서와 Android/iOS 검증 동시성 기본값만 포함한다. 실제 서버 sink·스토어 연결은 미완료다.
- Apple SignedDataVerifier를 이용하는 서버 경계 초안 작성. SANDBOX/PRODUCTION만 허용하며 실제 자격 증명 및 Apple root를 제공하지 않아 외부 검증은 미실행이다. Kotlin 컴파일을 확인한다.
- Apple library와 Kotlin 컴파일 종료 0. fake decoder로 환경·상품·계정·취소·수량 거부 및 재시도 가능 오류 구분을 검증한다. 실제 서명된 Apple 거래는 아니다.
- Apple fake decoder 경계 시험 2건 통과: app/environment/product/account/state 불일치와 위조 오류 거부, retryable 검증 오류 구분. 실제 인증서 chain·서명 검증은 미실행이다.
- 커밋 전: Apple 공식 library 기반 verifier와 fake 경계 시험만 포함. credential 조립·Google verifier·지급 연결·실거래 검증은 미완료여서 P05-T04 PARTIAL 유지.

### [P04-T04] 커밋 전 — 2026-11-10 Asia/Seoul
- 사용자가 최초 로그인 기준 7일 고정을 승인했으며 DB refresh UPDATE는 원래 만료를 변경하지 않는다. 앞서 local Backend Kotlin/Swift single-flight·응답 유실·logout 및 mock HTTP 시험을 통과했다. 실제 Provider와 revoke 실패의 재시작 후 재시도는 미검증/미구현으로 PARTIAL 유지한다.
- P05-T04 계속: Google 공식 Android Publisher Java client를 사용해 스토어 상태 조회를 구성한다. 로컬 fake 응답과 실제 Play 조회를 분리한다.
- Google Publisher v2 조회 adapter 초안 작성. package는 설정에서 고정하고 product·상태·account·test 환경·수량을 검증한다. compile 및 fake 응답 시험 전이다.
- Google 공식 client 포함 Kotlin 컴파일 종료 0. fake Publisher 응답과 네트워크 실패를 이용해 승인/거부 경계를 확인한다.
- Google fake Publisher 응답 시험 2건 통과: PENDING·계정·상품·환경·수량 불일치 거부와 네트워크 오류 분리. 실제 Google API 조회·취소/환불 처리·지급 연결은 미검증이다.
- 커밋 전: 공식 Google Publisher client 조회 경계와 fake 시험만 포함한다. 자격 증명 조립 및 실제 거래, 원장 연결은 미완료로 P05-T04 PARTIAL 유지.

### [P04-T04] 승인된 만료 기준 추가 검증 — 2026-11-10 Asia/Seoul
- 최초 로그인 후 refresh 회전 시 DB의 원래 7일 만료가 유지되는지 전용 local-mock DB에서 확인한다. 고유 시험 사용자만 추가하고 기존 데이터를 삭제하지 않는다.
- local-mock PostgreSQL opt-in 시험 1건 통과(skip 0): 최초 발급 만료가 약 7일이며 refresh 회전 후 정확히 같은 시각으로 유지됨을 확인. 실제 Provider 시험은 아니다.
- 커밋 전: 사용자 승인 만료 정책의 DB 회귀 시험만 추가한다. P04-T04 실제 기기·서버 revoke 재시도 등 미완료 항목은 PARTIAL 유지.
- P05-T04 계속: Google credentials는 Host가 명시 제공한 경우에만 scoped Publisher client를 생성하도록 조립 경로를 추가한다. local-mock은 자격 증명을 읽지 않는다.
- Google/Apple verifier fake unit 시험 각 2건 통과. 명시 credentials 기반 client 구성은 컴파일됐지만 실제 권한·네트워크 호출은 미실행이다. USER_SETUP에 현재 미연결 상태를 갱신했다.
- 커밋 전: Google host credential client 조립과 사용자 설정 안내만 추가. 서비스 런타임의 provider 조립·지급 연결 및 실제 스토어는 여전히 미완료다.

### [P05-T02] 승인된 동시성 추가 검증 — 2026-11-10 Asia/Seoul
- 사용자 선택인 기본 동시 1건이 두 거래의 서버 검증에 실제 적용되는지 fake sink로 확인한다. 실제 Play 결제는 실행하지 않는다.
- Android fake sink 시험 통과: 첫 거래의 서버 응답을 보류한 동안 두 번째 검증이 시작되지 않고 첫 검증이 끝나면 시작한다. 전체 Android unit task 종료 0. 실제 Play와 서버 검증은 아니다.
- 커밋 전: 기본 동시 1건 회귀 시험만 포함하며 P05-T02 실제 스토어·서버 연결은 PARTIAL/WAITING_USER로 유지한다.

### [P06-T02] 시작 — 2026-11-10 Asia/Seoul
- StoreKit 로컬 시험 가격 선택을 기다리는 동안 독립적인 APNs host forwarding을 구현한다. 실 APNs token·원격 발송은 사용자 설정/실기기 없이 완료로 기록하지 않는다.
- APNs host adapter 초안과 샘플 delegate forwarding을 작성했다. permission은 명시 호출시에만 요청하며 completion handler를 호출한다. iOS simulator 빌드를 확인한다. 서버 등록 연결은 아직 없다.
- iOS Simulator SDK의 GameBridgeSample Debug unsigned build 성공. 실제 알림 권한 UI, payload 주입, APNs token 및 원격 수신은 실행하지 않았다.
- 커밋 전: APNs host forwarding·권한 API와 샘플 delegate의 completion 호출만 포함. 사용자 action UI·서버 token 연결·payload 검증·실 APNs는 미완료이므로 P06-T02 PARTIAL/WAITING_USER 유지.

### [P06-T01] 시작 — 2026-11-10 Asia/Seoul
- FCM adapter를 host-owned Firebase 초기화 및 별도 service forwarding 방식으로 작성한다. Firebase 공식 문서의 26.0.1 API와 Android permission 가이드를 확인했다. Mock 빌드에는 설정 파일을 요구하지 않는다.
- FCM host adapter 초안 작성: 명시적 token 요청·권한 요청·channel·host service callback 전달. Firebase SDK 의존성은 compileOnly이며 실제 host가 설정한다. 컴파일 및 Mock 샘플 빌드를 확인한다.
- Android unit task 및 Firebase 설정 없는 Mock 샘플 assembleDebug 종료 0. FCM adapter 자체의 token rotation·권한 거부·메시지 unit 및 실제 FCM 발급/수신은 아직 미실행이다. host service/manifest 예시를 추가했다.
- 커밋 전: host adapter·compileOnly Firebase·통합 예시만 포함한다. Backend 등록 및 실제 OS/스토어 검증은 미완료이므로 P06-T01 PARTIAL/WAITING_USER 유지.

### [P06-T05] 시작 — 2026-11-10 Asia/Seoul
- 계획에 명시된 messageId·home/store route·campaignId만 허용하는 공통 payload 정규화를 구현한다. 콜드스타트 queue 및 실제 OS 클릭은 별도 미완료로 유지한다.
- Android/iOS 共通 payload parser와 허용 경로 단위시험을 작성했다. platform host 연결 전 unit 시험을 실행한다.
- Android·Swift parser unit 시험 각각 통과. host adapter에 parser를 연결해 raw URL/임의 필드가 callback으로 전달되지 않게 하고 Native 빌드를 재확인한다.
- Android library 및 iOS Simulator sample build 통과. 단위시험은 home/store 외 URL과 빈 messageId를 거부하고 추가 필드를 전달하지 않음을 확인했다. 실제 OS 클릭·콜드스타트·중복 제거는 아직 검증하지 않았다.
- 커밋 전: payload 정규화 및 host adapter 연결만 포함한다. queue·dedup·Unity routing·실제 원격 수신은 미완료로 P06-T05 PARTIAL 유지.

### [P08-T01] 시작 — 2026-11-10 Asia/Seoul
- 미완료 기능 감사를 완료한 것으로 간주하지 않고 독립적인 Android 로컬 Maven 패키징을 준비한다. 버전은 계획의 0.1.0-dev이며 외부 publish는 하지 않는다.
- 세 모듈에 로컬 Maven publication 설정을 추가했다. 산출물 생성과 POM 전이 의존성을 확인한다.
- 로컬 세 모듈 publication 성공, POM의 SDK 모듈 의존성을 확인했다. 별도 소비 프로젝트에서 repository coordinate만 사용하고 R8 release를 빌드한다.
- 좌표만 사용하는 별도 소비 앱의 R8 release build 성공, BridgeFacade keep 규칙이 mapping에 유지됨. 미서명 로컬 build이며 실행/기능 검증은 아니다. 기존 스크립트의 --mock 명시 계약을 유지한 채 전체 명령을 확인한다.
- `bash scripts/build-android.sh --mock` 종료 0: 세 모듈 로컬 Maven publish 및 별도 좌표 소비 R8 release build 성공. Firebase는 optional compileOnly이므로 FCM host가 별도로 의존성을 제공해야 한다. 해당 빌드에서 실제 Firebase 경로·앱 실행 및 전체 기능은 검증하지 않았다.
- 커밋 전: 로컬 publication·독립 소비 앱·명시적 mock build script만 포함. 기능 감사 및 실제 provider 포함 소비 검증은 미완료로 P08-T01 PARTIAL 유지. 외부 publish 없음.

### [P08-T02] 시작 — 2026-11-10 Asia/Seoul
- 기존 static XCFramework에는 Core/Bridge만 포함되어 실제 Apple Provider가 빠져 있음을 확인했다. Apple 소스를 binary target에 포함하고 source package와 분리 빌드를 확인한다. Unity 링크·실기기 검증은 별도다.
- Apple 소스를 포함한 iOS simulator static framework build 성공. 이제 기존 산출물을 덮어쓰지 않는 새 output에 무서명 device/simulator archive와 XCFramework를 생성한다.
- 무서명 device arm64와 simulator arm64/x86_64 archive·XCFramework 생성 성공. ApplePushHostAdapter 심볼과 source Swift unit 1건을 확인했다. Xcode가 umbrella header 부재/module map warning을 양 archive에서 출력했으므로 별도 consumer 링크 전 패키징 완전 통과로 기록하지 않는다.
- 독립 Swift consumer에서 XCFramework의 공개 ApplePushHostAdapter를 import/링크해 경고가 실제 소비를 막는지 확인한다.
- 독립 Swift consumer가 simulator 대상 XCFramework를 import/링크했고 Mach-O platform IOSSIMULATOR 확인. 컴파일러 sysroot 경고는 있었으므로 실제 실행 증거는 아니다. 누락된 public C ABI umbrella header를 추가해 module map 경고를 해결하고 다시 archive한다.
- public C umbrella header 추가 후 device/simulator 재archive 성공, module map 경고가 사라졌다. simulator Swift consumer가 SDK 지정 링크와 public Apple adapter import에 성공했다. C ABI 함수 호출도 링크 확인한다.
- 별도 Swift consumer에서 Apple adapter와 C ABI GB_ProtocolVersion 호출을 simulator 대상으로 컴파일·링크하고 Mach-O/심볼 확인했다. 실제 simulator 실행과 Unity link는 미실행이다.
- 커밋 전: Apple 소스를 포함한 unsigned static XCFramework build·header·독립 link 경로만 포함. 실제 기기 서명/실행과 Unity consumer는 미완료이므로 P08-T02 PARTIAL 유지.

### [P08-T03] 시작 — 2026-11-10 Asia/Seoul
- 로컬 Maven과 XCFramework를 UPM staging에 묶는 경로를 작성한다. Unity 라이선스/Editor import는 ENV-002로 미검증이며 staging 생성만으로 설치 가능하다고 주장하지 않는다.
- 기존 출력 덮어쓰기를 거부하고 Maven/XCFramework 필수 입력을 검사하는 staging script 초안 작성. 새 전용 경로에 복사 및 checksum을 확인한다.
- 전용 UPM staging 생성 성공. SHA256 목록 일치, 재실행 overwrite 거부와 누락 입력 실패를 확인한다. Unity import 증거는 아니다.
- staging checksum 93개 전체 일치, 기존 출력 overwrite와 누락 입력 각각 종료 2를 확인했다.
- 커밋 전: staging script만 포함한다. Gradle/iOS build hook·Unity .meta/import·package 소비 실행은 미구현/미검증이므로 P08-T03 PARTIAL이며 배포 가능한 패키지로 취급하지 않는다.
- 진행표 재집계 결과 local NOT_RUN 29 / PARTIAL 33 / PASS 2였으나 기존 수치가 각각 1건씩 달랐다. 실제 64행 기준으로 수정했다. Android --mock 진입점에 샘플 assemble이 누락되어 추가 검증한다.
- 샘플 assemble을 포함한 `build-android.sh --mock` 재실행 및 소비 release 빌드 모두 종료 0. 실제 실행·실스토어 시험이 아니다.
- 커밋 전: 진입점 누락 수정과 진행표 집계 보정만 포함한다.
- P08-T03 계속: Unity Android export의 기존 Gradle 설정을 보존하면서 마커 블록만 추가하는 독립 patcher를 작성한다. Android build module 부재는 실제 export 검증의 ENV-002로 남긴다.
- Gradle patcher 초안을 순수 C#으로 작성했다. 기존 블록 보존, 두 번 적용 시 동일 결과, 불완전 마커 및 예상 밖 설정 거부를 Unity 내장 .NET에서 확인한다.
- 순수 C# Gradle patcher smoke 통과: 기존 설정 보존, 2회 적용 불변, 부분 마커·예상 밖 layout 거부. 아직 Unity callback에 연결하지 않았으며 Unity Editor 검증은 아니다. 재실행 가능한 smoke로 저장한다.
- 저장된 `scripts/smoke-gradle-patcher.sh` 재실행 종료 0. Unity callback 및 iOS build hook은 아직 없다.
- 커밋 전: 순수 patcher와 smoke만 포함하고 실제 Editor/export는 미검증으로 P08-T03 PARTIAL 유지한다.
- 사용자 결정 수신: Xcode StoreKit 로컬 시험 표시 가격 coins $0.99 / premium $1.99. 실제 상품 가격과 별개이며 결정 문서와 USER_SETUP에 기록했다.
- Unity 공식 callback은 export된 unityLibrary 경로를 전달함을 확인했다. Android callback 초안은 staged repo가 없거나 기존 export repo와 내용이 다르면 명시 실패하며 기존 repo를 덮어쓰지 않는다. Unity Editor는 여전히 실행 불가다.
- callback을 stub Unity API와 임시 Gradle export fixture로 두 번 실행하고, 기존 repo 내용 변경 시 overwrite를 거부하는지 검증한다. 이는 실제 Unity Editor 시험이 아니다.
- stubbed Unity API 기반 callback smoke 통과: 두 번 적용 결과 동일하고 기존 Maven repo 변경을 감지해 덮어쓰기를 거부한다. 실제 Unity Editor/Android export가 아니며 iOS hook은 미구현이다.
- 커밋 전: 사용자 StoreKit 시험 가격 결정, Android callback과 stub smoke만 포함한다. P08-T03 PARTIAL/ENV-002 유지.

### [P05-T03] 로컬 StoreKit 구성 계속 — 2026-11-10 Asia/Seoul
- 승인된 로컬 시험 가격 coins $0.99, premium $1.99를 별도 Xcode StoreKit scheme에만 적용한다. 실제 Sandbox 및 production 가격과 거래는 영향을 받지 않는다. 기존 StoreKit 거래를 삭제하지 않는다.
- 별도 StoreKit 구성/테스트 scheme과 상품 조회 시험을 작성했다. 계획과 Apple 공식 형식에 맞춘 로컬 fixture이며 실제 App Store 서버가 아니다. 설정 생성과 simulator 시험을 확인한다.
- 블로커: iOS 26.5 simulator에서 StoreKitTest 상품 조회가 빈 배열을 반환해 테스트 1건 실패(가격 assertion 포함). bundle 구성·scheme 및 test environment를 확인한다. 실제 결제나 거래 삭제는 하지 않았으며 로컬 StoreKit PASS가 아니다.
- 시험 번들에 GameBridge.storekit이 포함됐으나 SKTestSession이 SKInternalErrorDomain Code 3 설정 저장 오류를 출력했다. Apple Developer Forums에 같은 iOS 26.5 증상과 조사 중인 문제 보고가 있다(https://developer.apple.com/forums/thread/826971). 동일 원인이라고 단정하지 않으며 이 로컬 상품 조회는 FAIL로 기록한다.
- 커밋 전: 사용자 승인 시험 가격, 별도 scheme 및 실패한 회귀 시험을 보존한다. StoreKit local transaction·실 Apple Sandbox·서버 지급은 미검증이다.

### [P08-T03] staging 입력 검증 계속 — 2026-11-10 Asia/Seoul
- POM만 있고 JAR/AAR 또는 XCFramework slice가 없는 경우를 막는다. 독립 작업이며 StoreKit simulator 실패를 해소한 것으로 간주하지 않는다.
- 새 staging 96개 checksum 일치. simulator slice 이름을 고정하지 않고 XCFramework Info.plist의 device/simulator 실제 binary를 검사하도록 보정해 다른 아키텍처 환경에서도 동작하게 한다.
- Info.plist 기반 slice 확인 후 새 staging 생성 및 96개 checksum 재검증 성공. 기존 staging은 보존했다. .NET 테스트의 생성 bin/obj를 ignore해 기존 파일을 제거하지 않았다.
- 커밋 전: staging 입력 완전성 검사와 로컬 생성물 ignore만 포함한다. Unity import/iOS build hook은 미검증/미구현이다.
- 패키징 검토에서 Maven repository 내부 AAR/JAR을 Plugins/Android에 두면 Unity가 자동 plugin import해 중복될 위험을 발견했다. Unity import 대상에서 제외되는 Editor의 `GameBridgeArtifacts~` 아래로 이동하고 callback 경로를 함께 수정한다. 기존 staging은 보존한다.
- 숨김 artifact 경로로 변경 후 stubbed Android hook smoke와 새 staging 생성·checksum 통과. Unity 공식 매뉴얼은 `~`로 끝나는 폴더를 Asset import에서 제외한다고 설명한다. 실제 UPM import는 아직 확인하지 않았다.
- 커밋 전: 중복 plugin import 방지용 artifact 경로 변경과 대응 시험만 포함. iOS hook과 Unity import는 미완료다.
- P08-T03 계속: static XCFramework를 UnityFramework에 명시적으로 링크하는 iOS post-build 경계를 작성한다. 기존 Xcode export의 동일 경로 파일이 다르면 overwrite하지 않는다. Unity 실행 검증은 ENV-002로 남긴다.
- iOS post-build callback 초안을 추가해 숨김 staging XCFramework를 복사/검증하고 UnityFramework target에 링크한다. 먼저 Android 회귀와 iOS 코드 컴파일 경계를 검증한다.
- iOS callback을 stubbed PBX API와 별도 export fixture로 컴파일·2회 호출한다. stub은 실제 Xcode project link나 Unity Editor 동작의 증거가 아니다.
- Android/iOS stubbed callback smoke 통과. 설치된 Unity iOS Xcode 관리 assembly로 iOS callback의 실제 API 컴파일을 추가 확인한다(실제 Editor 실행은 아님).
- 실제 Unity managed assembly 대상 iOS callback 컴파일 실패: `UnityEditor.PackageInfo`와 `UnityEditor.PackageManager.PackageInfo` 이름 충돌(CS0104). stub 시험이 놓친 차이이며 전체 이름으로 수정한다.
- 실제 Unity iOS Xcode assembly 대상 callback 컴파일 오류 수정 후 경고0/오류0. Unity PBXProject가 동일 file link를 두 번 추가할 때 중복을 방지하는지 생성 프로젝트를 읽기 전용 입력으로 시험한다.
- Unity의 실제 PBXProject managed API를 생성 Xcode 프로젝트에 읽기 전용으로 적용한 독립 .NET 시험에서 같은 file link 2회 추가가 동일 결과임을 확인했다. 이 검증을 재실행 가능한 smoke로 저장한다. 실제 Unity export는 아니다.
- gerçek Unity Xcode managed API smoke 및 Android/iOS stub hook smoke 재실행 통과. 새 staging 98개 checksum 일치. 실제 Unity Editor import/iOS export·static Swift runtime/IL2CPP 링크는 미검증이다.
- 커밋 전: iOS Xcode hook, 안전 복사 공통화 및 독립 시험만 포함. P08-T03 PARTIAL/ENV-002 유지한다.

### [P06-T04] 시작 — 2026-11-10 Asia/Seoul
- FCM/APNs 실제 서버 전송 경계를 작성한다. 재시도 및 개발 API rate 수치는 사용자 결정 대기이므로 그 정책에 의존하는 자동 발송·API 활성화는 하지 않는다. 외부 credential과 원격 발송은 사용자가 준비해야 한다.
- Firebase Admin 공식 9.11.0과 Apple APNs HTTP/2 토큰 인증 문서를 확인했다. 우선 요청 한 번의 전송/오류 분류를 작성하며 자동 retry·개발 API는 사용자 정책 결정 전 비활성으로 둔다.
- 실제 Firebase Admin 단발 전송과 APNs HTTP/2 ES256 단발 전송 초안을 추가했다. 자동 재시도·DB token 삭제·dev API 연결은 없다. 컴파일 및 fake transport 검증을 진행한다.
- Firebase Admin 9.11 컴파일 성공. `setToken`은 Firebase의 2026 FID 전환에서 deprecated로 표시된다. 현재 계획과 Android adapter는 legacy 등록 토큰을 사용하므로 이를 FID로 임의 변환하지 않고 호환 경로로 남긴다. 실제 FID 전환·데이터 이관은 미구현이다.
- APNs fake transport의 host/topic/status·네트워크 오류와 test-only ES256 서명, FCM 오류 mapping 검증을 실행한다. 실제 스토어·원격 push는 호출하지 않는다.
- Apple 공식 APNs 지침상 provider JWT는 매 요청 갱신하면 안 되므로 40분 재사용 캐시를 추가한다(20~60분 범위). APNs 5xx 재시도는 별도 15분 지침이 있어 사용자에게 요청한 일반 재시도와 구분해 적용해야 한다.
- 단발 전송 경계 fake 시험 4건 통과: FCM 오류 구분, APNs host/topic·상태·네트워크 오류, synthetic ES256 서명, provider token 40분 재사용. 실제 Firebase/APNs 외부 호출은 없다.
- 커밋 전: 실제 SDK/HTTP 단발 sender와 fake 시험만 포함. 사용자가 선택할 재시도·개발 API 제한, DB lifecycle, 실 credential 조립/발송은 미완료이며 P06-T04 PARTIAL/WAITING_USER 유지한다.
- 진행표의 오래된 체크포인트와 이미 해결된 XcodeGen·Mock 삭제/재시도 설명을 실제 검증 상태로 정정했다. 전체 프로젝트 완료를 뜻하지 않는다.
- 커밋 전: 진행 문서 사실관계 수정만 포함한다.

### [P07-T01] 시작 — 2026-11-10 Asia/Seoul
- push retry 정책을 기다리는 동안 계획에 명시된 200개 진단 ring buffer를 독립 구현한다. 원문 payload·token을 받는 API를 제공하지 않으며 config cache/maintenance는 별도 미완료다.
- Android/iOS typed diagnostics 초안 작성. 두 플랫폼의 200개 제한 및 오래된 이벤트 제거 unit을 확인한다. 실제 SDK 각 작업에 아직 연결하지 않았다.
- Android core unit task와 Swift diagnostics 단위시험 통과: 최신 200개 보유와 이전 이벤트 제거를 확인했다. enum/UUID만 입력하므로 원문 문자열·토큰을 받지 않지만 전체 SDK redaction/내보내기 연결은 미구현이다.
- 커밋 전: 독립 typed buffer만 포함한다. 진단 이벤트 연결·export 상한·config cache/점검 동작은 미완료로 P07-T01 PARTIAL 유지.

### [P06-T04] APNs 요청 경계 보강 — 2026-11-10 Asia/Seoul
- Apple의 4KB 알림 한도 및 HTTP/2 요구에 맞춰 크기 초과를 전송 전 거부하고 HTTP/1 fallback을 성공으로 취급하지 않도록 보강한다. fake 시험을 재실행한다.
- APNs fake transport unit 4건 재통과. 4KB 초과는 실제 전송 호출 전에 실패한다. HTTP/2 version 확인은 코드 검사/컴파일만 했으며 실제 네트워크 협상은 미실행이다.
- 커밋 전: APNs protocol 경계 보강만 포함. 재시도 및 실제 발송은 여전히 미완료다.

### [P05-T01] 신규 세션 app scope 연결 — 2026-11-10 Asia/Seoul
- 신규 인증 세션에 검증된 app scope를 저장하고 서버 발급 구매 binding을 인증 세션으로만 조회한다. 기존 scope 없는 세션은 추정·수정·삭제하지 않고 재인증을 요구한다. 격리 schema에서 검증한다.
- nullable app_scope migration과 신규 세션에만 scope를 쓰는 API 초안 작성. 기존 세션은 손대지 않는다. 컴파일 및 격리 schema 검증을 진행한다.
- 서버 Kotlin 컴파일 종료 0. 별도 schema에서 신규 세션 app별 binding 분리와 legacy null scope 거부·보존을 DB 시험한다.
- 전용 PostgreSQL 격리 schema의 binding 시험 2건 통과(skip 0): 10개 동시 생성의 안정성, 신규 app scope 분리, legacy null scope 거부 및 기존 값 보존. 실제 Apple/Google 서버 증빙·지급/Native 전달은 아니다. 테스트 schema는 삭제하지 않았다.
- 커밋 전: nullable migration, 신규 세션 scope 및 인증 binding 조회 경로만 포함. Native sink·실 결제 및 기존 세션 마이그레이션은 미완료이므로 P05-T01 PARTIAL 유지.
- 새 session scope 변경 후 Backend 전체 일반 unit suite를 실행한다. 별도 opt-in DB와 실제 provider 시험은 일반 suite 결과에 합산하지 않는다.
- 블로커: Backend 일반 suite 32건 중 1 실패·7 skip. HttpInfrastructureTest의 sanitized 400 JSON path가 없음. 원인을 분리하고 수정 후 재실행하기 전 전체 PASS로 기록하지 않는다.
- 실패 원인 확인: Firebase 의존성 추가로 XML converter가 추가되어 Accept 미지정 요청의 오류 응답이 XML로 직렬화됐다. SDK 계약은 JSON이므로 모든 ApiErrors 응답 content type을 명시한다.
- 오류 응답 JSON content type 명시 후 Backend 일반 suite 종료 0: 32건 중 25 통과·7 opt-in skip, 실패0. 실패했던 HTTP sanitized 오류와 request ID 시험이 통과했다. DB opt-in·실 provider 시험은 이 결과에 포함하지 않는다.
- 커밋 전: XML 오류 응답 회귀 수정 및 실패/재검증 증거만 포함한다.
- 오류 경로 수정 후 추가 검토: 동일 XML converter가 성공 응답에도 영향을 줄 수 있다. Accept 미지정 성공 응답의 JSON 기본 협상을 Spring MVC에서 고정하고 독립 web slice 시험으로 확인한다.
- JSON web slice 초기 실행 1건 실패: Spring test context의 누락 bean으로 기동하지 못했다. 실제 응답 검증은 실행되지 않았으며 의존성을 확인한다.
- web slice가 auth SessionFilter를 자동 검색하지만 SessionService를 포함하지 않는 것이 원인이었다. 테스트 전용 mock bean을 제공해 실제 content negotiation 검증을 재실행한다.
- mock SessionService를 포함한 web slice 1건 통과: Accept 없는 health 성공 응답이 JSON이다. Backend 일반 suite를 재실행한다.
- Backend 일반 suite 재실행 종료 0: 33건 중 26 통과, 7 opt-in skip, 실패0. 성공·오류의 Accept 미지정 JSON 계약을 각각 확인했다.
- 커밋 전: 기본 JSON content negotiation과 web slice 시험을 포함한다. 실제 외부 provider 및 생략한 DB opt-in은 이 결과에 포함하지 않는다.

### [P05-T01] Android purchase binding 연결 — 2026-11-10 Asia/Seoul
- Google 인증 세션 복원 후 server binding을 인증된 내부 경로로 조회한다. 토큰·binding은 Unity/public profile에 노출하지 않고 logout/계정 변경과 경합을 검사한다. 실제 결제 검증 연결은 별도다.
- Android 내부 binding 조회 초안과 malformed 응답 단위시험을 작성했다. 세션 mutex를 유지한 채 요청하며 실제 Backend 연결 전 단위 컴파일을 확인한다.
- Android binding parser unit 및 전체 sdk-android unit task 통과. 인증 session 요청 도중 logout이 기존 계정과 경합하지 않는지도 fake 경계 시험을 추가한다.
- Android unit 재실행 종료 0. fake 인증 backend에서 binding 요청 진행 중 logout이 기다리고 완료 후 session이 비워짐을 확인했다. 실제 Google 인증·Backend binding HTTP·Play 거래는 미실행이다.
- 커밋 전: Native-only account source와 parser·session 경합 unit만 포함. Apple 연결, provider 조립 및 real proof sink는 미완료로 P05-T01 PARTIAL 유지.

### [P05-T01] Apple purchase binding 연결 — 2026-11-10 Asia/Seoul
- Apple 인증 세션을 복원하고 서버 binding을 Native 내부 cache에만 연결한다. async 요청 중 logout/계정 변경 시 이전 계정 결과를 버린다.
- Apple Native-only binding source 초안과 logout 후 cache 무효화 단위시험을 추가했다. session generation으로 요청 도중 변경을 감지한다.
- Swift Apple auth fake 단위시험 7건 통과. binding 요청 중 logout 후 늦게 도착한 응답을 폐기하는 경합 시험을 추가한다.
- Swift Apple auth fake 시험 8건 통과: logout 후 cache 무효화, 요청 지연 중 logout 시 응답 폐기 포함. simulator 타깃 컴파일을 확인한다.
- 새 Apple binding source를 포함한 simulator static framework build 성공. 이전 XCFramework/staging은 이 커밋을 포함하지 않으므로 최신 산출물로 간주하지 않는다. 실제 StoreKit·Backend HTTP 연동은 미실행이다.
- 커밋 전: Apple Native-only binding source와 generation 경합 unit만 포함한다. 양 플랫폼 provider 조립·실 proof sink·실거래는 미완료로 P05-T01 PARTIAL 유지.

### [P05-T05] 시작 — 2026-11-10 Asia/Seoul
- 검증된 Apple 거래의 DB 원자 지급과 중복/계정 충돌을 구현한다. Google finalizer의 암호화 증빙 삭제 시점은 사용자 결정 대기이며 해당 저장·삭제 동작은 정하지 않는다. 실 StoreKit/HTTP 연결은 별도다.
- Apple 검증 결과만 받는 내부 grant service 초안 작성: session scope/binding/catalog 확인과 ledger transaction. 실제 verifier route와 StoreKit 연결은 아직 없다. 컴파일한다.
- Apple grant service Kotlin 컴파일 성공. 검증 결과는 synthetic fixture로만 만들고 격리 schema에서 동시 10건, 1회 원장과 타 계정 거래 재사용 거부를 확인한다.
- PostgreSQL 격리 schema 시험 1건 통과(skip 0): 같은 synthetic Apple 거래 10개 동시 요청에서 grant 1회·동일 purchase ID·원장 총 100, 다른 사용자의 거래 재사용 거부. 실제 Apple 서명/거래와 연결된 검증은 아니다. 시험 schema는 삭제하지 않았다.
- 커밋 전: 내부 Apple grant transaction과 synthetic DB 시험만 포함. 실제 verifier endpoint, client finish 연결, Google 증빙 보관 및 서버 finalizer는 미완료이므로 P05-T05 PARTIAL 유지.
- P05-T05 계속: Apple 검증기와 원자 지급을 실제 순서로 묶는 내부 pipeline을 만든다. 공개 endpoint/credential 구성은 여전히 미완료이며 임의 인증서나 mock 성공으로 대체하지 않는다.
- Apple pipeline 초안은 verified payload의 account/product/environment 검사 후 grant 시점에 session·binding을 다시 검사한다. 격리 schema의 10건 경쟁 시험을 pipeline 경유로 재실행한다.
- Apple pipeline 경유 동시 10건 DB 시험 통과. 검증 단계의 다른 계정 거부도 추가 확인한다. 실제 서명 검증 경로는 fake decoder가 아닌 Apple library 구성·root가 필요하다.
- 검증기(fake decoder)→grant pipeline의 동시성·타 계정 거부 DB 시험 통과. 실제 Apple root/서명·공개 endpoint·Native finish 연동은 미실행이다.
- 커밋 전: 내부 pipeline 및 fake+격리 DB 시험만 포함하며 P05-T05 PARTIAL 유지한다.

### [P07-T03] 시작 — 2026-11-10 Asia/Seoul
- 현재 구현에 맞는 README/API/연동 안내 초안을 작성한다. 미연결 provider, 로컬 시험 실패와 Unity 제한을 완료처럼 쓰지 않고 이후 전체 기능 audit 시 다시 검토한다.
- README/API/INTEGRATION 초안을 현재 공개 소스와 검증 상태에 맞춰 작성하고 USER_SETUP의 오래된 Mock 설명을 수정했다. 명령 경로·API 이름과 실패 표기를 검토한다.
- 문서에 적힌 로컬 명령 파일 존재와 주요 공개 class/method 이름을 소스에서 대조했다. 기존 `smoke-local.sh`는 보호된 dev push 미구현으로 실패하는 사실을 명시했다. 문서 전체 flow 및 실 provider 예제 감사는 미완료다.
- 커밋 전: 현재 상태의 문서 초안만 포함한다. 기능 완결 및 API 전체 교차 감사 전이므로 P07-T03 PARTIAL 유지.
- P05-T05 계속: Google 공식 Publisher consume/ack 단발 경계를 작성한다. 저장된 grant 검증을 선행하며, 증빙 보관 및 자동 retry는 사용자 결정 전 연결하지 않는다.
- Google finalizer 초안: durable grant 확인 후 제품·계정·스토어 상태 재조회, 미완료만 consume/ack한다. credential·worker/증빙 저장소와는 연결되지 않았다. 컴파일을 확인한다.
- Google finalizer 编译 성공. fake gateway로 grant 이전 호출 차단·계정 불일치·기완료 재조회·consume/ack 분기를 검증한다.
- Google finalizer fake gateway 시험 2건 통과: grant 전 조회 차단, 계정 불일치 거부, 완료 상태 스토어 재조회, consume/ack 분리. 실제 Publisher 호출은 없다.
- 커밋 전: Google 공식 client 단발 finalization과 fake 경계만 포함. durable grant check 실제 DB 구현, 증빙 보관·삭제 정책, job worker 연결 및 실제 Play 시험은 미완료다.

### [P07-T04] 시작 — 2026-11-10 Asia/Seoul
- 현재 public operation→Native/Server→sample 경로를 조사한다. `rg TODO/FIXME/NotImplementedException/fatalError` 결과가 비어 있어도 호출 경로가 없는 기능을 구현 완료로 간주하지 않는다. 최종 P11 audit은 별도다.
- Unity facade operation, Editor fake switch, Native Bridge 제한, Native sample/Backend source를 대조해 FEATURE_MATRIX 초안을 작성했다. 실 StoreKit 실패와 미연결 endpoint·Unity 경로를 명시했다. 전체 API/설정 재검토와 수정 후 재감사는 남았다.
- 커밋 전: 1차 traceability 초안만 포함하고 P07-T04 PARTIAL 유지한다. `TODO` 검색 결과만으로 기능 완료를 판정하지 않았다.
- P05-T05 추가 검증: Apple 서명 검사 중 logout이 일어나면 늦은 검증 결과가 지급되지 않는지 격리 DB에서 확인한다. 기존 데이터를 변경하지 않는다.
- 격리 DB 시험 통과: synthetic 검증 도중 session logout 시 grant 단계에서 SESSION_EXPIRED로 거부하고 원장 항목은 증가하지 않았다. 실제 Apple 서명/스토어 거래는 아니다.
- 커밋 전: 경합 회귀 시험만 포함한다. 서버 endpoint·실 credential 연결은 미완료다.
- P05-T05 계속: Apple endpoint의 중복 요청 key가 같은 거래에만 재사용되도록 grant transaction에 idempotency record를 연결한다. 실제 인증서 구성과 HTTP 노출은 별도로 검증한다.
- 격리 PostgreSQL 시험 통과: 같은 attempt key 동시 10개는 원장 1건, 같은 key로 다른 거래는 IDEMPOTENCY_CONFLICT이며 logout 경합도 거부한다. synthetic Apple 응답이다.
- 커밋 전: Apple grant의 idempotency DB transaction만 포함한다. 공개 endpoint·실 서명·Google finalizer는 미완료다.

### [P05-T04] Apple verifier 실행 구성 — 2026-11-10 Asia/Seoul
- Apple 공식 root와 app별 bundle/product 설정이 명시된 경우에만 verifier를 lazy 생성하는 경로를 추가한다. 설정 없이 시작하거나 실제 credential 없이 local-mock을 이용할 수 있어야 한다.
- 앱별 bundle·상품 allowlist·Apple 공개 root 경로를 최초 사용 시 읽는 registry 초안 작성. local-mock profile에는 bean을 만들지 않는다. 환경/설정 누락은 fail-closed여야 한다.
- verifier registry Kotlin 컴파일 성공. 앱 설정·root 누락 및 잘못된 production 설정이 네트워크 호출 없이 503으로 실패하는지 검증한다.
- app/root 누락 registry 시험 1건 통과. 공개 Apple root와 실제 signed transaction을 사용하지 않았으며 공개 purchase endpoint도 아직 없다.
- 커밋 전: lazy Apple verifier 설정과 fail-closed unit만 포함. 실제 인증서·스토어·원장 HTTP 연결은 미검증이다.
- P05-T04 계속: sandbox/production에서만 Apple 증빙을 처리하는 인증 endpoint 초안을 작성한다. 앱·계정은 세션에서 유도하며 미설정 verifier는 503, 위조·계정 충돌은 지급 없이 실패해야 한다.
- Apple 전용 authenticated verify endpoint와 오류 상태 mapping 초안을 작성했다. 컴파일 및 HTTP fixture 검증 전이며 Google endpoint와 실제 서명 시험은 별도다.
- Apple Native proof sink 초안은 인증 세션 잠금/세대 확인과 Backend의 durable grant 응답 확인 후에만 내부 ServerGrant를 반환한다. 서버 검증 불가와 위조를 구분하며 iOS/Backend 컴파일을 확인한다.
- Swift Apple auth unit 8건通과(실 receipt 아님). Apple endpoint에 fake pipeline을 주입해 인증 principal, idempotency key, 응답 mapping과 malformed key 거부를 HTTP slice로 확인한다.
- HTTP slice 최초 실행은 테스트 컴파일 실패: public 테스트 property가 internal pipeline 타입을 노출(Kotlin). 제품 endpoint 실행 전이며 test visibility를 수정한다.
- Apple HTTP slice mock pipeline 1건 통과. Native proof sink의 credential header·idempotency·서버 GRANTED만 수락하는 fake URLProtocol 시험을 추가한다. 실제 JWS/스토어 요청이 아니다.
- Swift fake URLProtocol 시험 포함 9건 통과: 서버 GRANTED만 Native ServerGrant로 수락한다. Backend HTTP slice에서 위조와 retryable 서명 검증 실패의 응답 구분도 확인한다.
- Backend HTTP slice에서 fake pipeline의 정상 grant, 잘못된 idempotency key, 위조 증빙 400, retryable 검증 오류 503을 확인했다. security filter는 slice에서 꺼져 있으므로 실제 HTTP 인증 검증을 대체하지 않는다.
- 커밋 전: sandbox/production Apple 검증 endpoint, Native proof sink와 fake HTTP/unit만 포함. 실제 Apple 서명·StoreKit finish, 제품 catalog 설정, 보안 필터 통합 및 Android Google sink는 미완료여서 P05-T04/T05 PARTIAL 유지.
- Apple endpoint의 실제 Spring Security 필터와 DB 세션 연결을 별도 sandbox 시험 DB에서 확인한다. test-only identity 서명을 사용하며 Apple root가 없는 상태에서 구매 지급 없이 503이어야 한다.
- 별도 sandbox PostgreSQL의 실제 Spring HTTP 통합 시험 1건 통과(skip 0): 익명 binding 401, synthetic 로그인 세션의 binding 200, Apple root 미설정 verify 503 CONFIG_REQUIRED 및 원장 변화 없음. V6 migration은 전용 시험 DB에만 적용했다. 실제 Apple/Google 계정과 서명은 미사용이다.
- 커밋 전: 인증 필터·설정 누락 fail-closed 회귀 시험만 포함한다. 실제 Apple signed transaction grant 및 StoreKit finish는 여전히 미검증이다.
- Apple HTTP 경로의 synthetic decoder→실제 인증 filter→격리 sandbox DB grant를 10개 동시 요청으로 연결하는 통합 시험을 작성한다. 사용자 계정·Apple 서명은 사용하지 않는다.
- synthetic decoder를 주입한 실제 sandbox HTTP·보안 filter·PostgreSQL 통합 시험 1건 통과(skip 0): 10개 동시 verify 모두 200, GRANTED 1건·동일 purchase ID·ledger 1건/100. 실제 Apple signature/StoreKit 거래가 아닌 fixture이다. 시험 DB 기록은 보존했다.
- 커밋 전: synthetic HTTP/DB 회귀만 포함. 실제 Apple root·Sandbox 및 Native finish는 여전히 미검증이다.

### [P05-T06] 시작 — 2026-11-10 Asia/Seoul
- Apple Native 인증·binding·StoreKit·server proof sink를 하나의 내부 runtime으로 조립한다. 실제 StoreKit 시험 실패와 실제 Apple credential 부재는 별도로 남기며 공개 Unity 연결은 이 작업으로 완료되지 않는다.
- AppleStoreRuntime 초안은 유저 binding 획득 후 listener/unfinished 복구를 시작하고 구매 전에 현재 StoreKit 상품과 binding을 재확인한다. 명시적 userRestore에서만 AppStore.sync를 호출한다. 컴파일을 확인한다.
- 검토에서 StoreKit 상품 유형 불일치와 중복 구매 UI 시작 위험을 발견해 목록/구매 시 유형 확인 및 구매 single-flight를 추가한다. 실제 StoreKit UI 시험은 ENV-STOREKIT-26으로 실패 상태다.
- StoreKit runtime 类型校验和单一购买 UI 代码编译通过；已有 grant 匹配 unit 1件通过，不代表实际 UI 测试。增加商品配置 fail-closed unit。
- Swift Apple unit 10건 통과(설정 누락·중복 상품 ID 거부 포함). 새 runtime을 포함하는 iOS simulator static framework compile을 확인한다.
- Apple runtime 포함 iOS simulator static framework build 성공. 이는 StoreKit 거래를 실행하지 않았으며 Swift fake 시험만 통과했다. 이전 XCFramework/staging은 현재 코드보다 이전 산출물이다.
- 커밋 전: Apple 내부 조립, 제품 유형 검사와 중복 UI 차단만 포함한다. 공개 facade/sample, timeout 후 event/완료 복구, Android server finish 및 실제 StoreKit 시험은 미완료로 P05-T06 PARTIAL 유지.
- P05-T06 계속: StoreKit 구매와 transaction listener가 같은 시간에 검증할 때 기존 BUSY 분기에서 복구 항목을 놓칠 수 있다. 승인된 기기별 동시 1건과 계획의 queue 100을 이용해 대기열로 직렬화하고, Apple 로그인/결제 UI도 공통 gate로 상호 배제한다.
- Apple concurrency 변경 컴파일 실패: actor 격리 생성자를 default argument에서 호출해 Swift actor isolation 오류가 발생했다. 생성 시점으로 옮겨 재검증한다. 실제 구매는 실행하지 않았다.
- actor default argument 수정 후 Swift auth unit 10건 통과. 검증 limiter 동시 1건·취소 waiter slot 반환과 로그인 중 결제 UI gate 차단을 fake 단위시험으로 확인한다.
- Swift fake concurrency/auth 단위 12건 통과: verification slot 직렬화·취소 후 반환 및 로그인 중 UI gate BUSY를 확인했다. 실제 StoreKit transaction listener/결제 UI는 실행하지 않았다. simulator framework compile을 재확인한다.
- iOS simulator static framework compile 성공. Apple limiter/UI gate는 fake unit만 확인했고 실 StoreKit transaction과 Android 공통 UI gate는 미완료다.
- 커밋 전: Apple verification 대기열·UI 상호 배제와 unit만 포함한다. 취소/복구의 실제 OS 동작과 Google 경로를 확인하지 않았으므로 P05-T06 PARTIAL 유지.
- P05-T06 계속: Android Google 로그인과 Play 결제도 공통 UI gate를 사용할 수 있도록 연결한다. 서버 proof sink가 없을 때 구매 UI 차단은 유지한다.
- Android billing에 공유 가능한 gate를 주입하고 gate 보유 중 UI를 시작하지 않는 fake 시험을 추가했다. 실제 Android UI와 runtime 조립은 아직 미검증이다.
- Android shared gate fake 시험 통과. 실제 Google gateway·account source·auth gate를 조립하는 Native-only factory를 추가한다. 실제 Backend sink가 반드시 주입되어야 하며 현재 sink 구현은 미완료다.
- Android library assembleDebug 성공. shared gate unit은 fake gateway이며 실제 Credential Manager/Play UI 중첩 시험이 아니다.
- 커밋 전: Android gate 공유·내부 factory 및 fake unit만 포함. Google proof sink·실 store 결제와 Unity 연결은 미완료다.
- P05-T05 계속: Google 검증 결과를 durable grant에 기록하고 pending finalization에만 암호화 증빙을 보관하는 독립 경로를 작성한다. 완료 후 삭제/보관 정책은 사용자 답변 전 미정이며 worker에 연결하지 않는다.
- Google grant 초안은 암호화 증빙·원장·미완료 job을 같은 DB transaction에 기록하고 account/proof hash를 재확인한다. 아직 worker/HTTP에 연결하지 않았으며 완료 후 증빙 정책도 미정이다. 컴파일한다.
- Google grant 컴파일 성공. 전용 test-only AES 키와 synthetic 거래로 10개 동시 원장 1건, 증빙 암호문·AAD 변조 거부, pending job을 격리 DB에서 확인한다.
- synthetic Google 거래 10건 동시 DB 시험 1건 통과(skip 0): grant 1건·원장 100·pending consume job, 암호문/AAD 검증. test-only key 사용, 실제 Google 조회/발송은 없다.
- 커밋 전: 미완료 증빙 암호화와 내부 grant transaction만 포함. 완료 후 삭제 정책, 실제 verifier endpoint·worker·실 Play는 미완료로 P05-T05 PARTIAL 유지.
- P05-T04/T05 계속: Google 검증기→암호화 pending grant pipeline을 연결한다. 완료 후 증빙 보존 정책이 정해지기 전 worker는 활성화하지 않는다.
- Google pipeline 신규 session scope/binding을 기준으로 공식 verifier를 호출한 뒤 grant에서 다시 검증한다. fake Publisher 응답과 격리 DB 경쟁 시험을 실행한다.
- fake Publisher→Google grant 경쟁 시험 통과. unknown product를 grant 없이 거부하는 경계도 재확인한다.
- fake Publisher→Google grant 격리 DB 시험 재실행 통과: 동일 거래 10건 중 지급 1건, unknown product 거부. 실제 Play 서버 또는 worker는 호출하지 않았다.
- 커밋 전: 내부 검증/지급 조립과 fake DB 시험만 포함한다. 서버 credential 설정·HTTP·완료 후 증빙 정책·worker는 미완료다.
- Google 공식 Publisher verifier를 앱별 package·상품·명시 service account 경로로만 lazy 구성하는 registry를 작성했다. 누락 시 ambient credential을 읽지 않고 실패하는지 확인한다.
- Google registry 누락·잘못된 credential 경로 fail-closed 단위시험 1건 통과. 실제 service account/Publisher 네트워크는 사용하지 않았다.
- 커밋 전: lazy configuration과 단위시험만 포함한다. 공개 verify endpoint·finalizer worker·실 Play와 완료 후 증빙 정책은 미완료다.
- Google Native proof sink를 구현한다. 아직 server Google endpoint/worker가 없으므로 실제 구매 UI와 실 연결을 활성화하지 않고 fake HTTP 경계만 확인한다.
- Google Native proof sink는 인증 session이 일치할 때만 configured Backend로 토큰을 보내고, GRANTED/ALREADY_GRANTED 및 fingerprint 형식을 검증한다. fake request 단위시험을 실행한다.
- Android fake proof sink 및 core unit 통과. 서버 검증 실패 `VERIFICATION_FAILED`를 Android/iOS Native가 일반 INVALID_ARGUMENT로 뭉개지 않도록 HTTP 오류 mapping과 테스트를 보강한다.
- Android core/sdk unit task 및 Swift BackendClient unit 통과. fake sink는 GRANTED만 허용하고 proof 원문을 응답 문자열에 노출하지 않음을 확인했다. 실제 Google endpoint/Play UI는 실행하지 않았다.
- 커밋 전: Native proof 전송 경계와 오류 매핑만 포함한다. Google endpoint·durable worker·완료 후 증빙 정책이 준비되지 않아 실제 UI 조립을 활성화하지 않는다.

### [P05-T07] 서버 상품·지급 상태 조회 — 2026-11-10 Asia/Seoul
- Native에서 실제 store ID·서버 지급 상태를 다시 확인할 수 있도록 app scope와 소유권을 강제하는 sandbox/production 읽기 경로를 작성한다. 샘플/Unity UI와 실제 store 거래는 별도다.
- authenticated catalog, app/environment 범위 entitlement 및 소유 purchase 조회 초안 작성. 가격과 증빙 원문을 반환하지 않는다. 컴파일 및 HTTP/DB fixture를 확인한다.
- catalog/read controller Kotlin 컴파일 성공. synthetic Apple HTTP 통합 시험에서 지급 후 잔액/상태 조회와 다른 계정의 purchase 접근 거부를 확인한다.
- synthetic HTTP/DB 시험 통과: 잔액·catalog·본인 구매 조회, 타 계정 404. 검토에서 내부 CLIENT_PENDING이 공통 공개 enum에 없음을 발견해 PENDING으로 정규화하고 재시험한다.
- synthetic sandbox HTTP/DB 재시험 통과: 공개 finalization PENDING 정규화, 본인 잔액·catalog·구매 조회와 다른 사용자 404. 실제 store 구매는 아니다.
- 커밋 전: 서버 읽기 경로 및 소유권 fixture만 포함한다. Native/Unity 상점 UI와 실제 store 연결은 미완료이므로 P05-T07 PARTIAL/WAITING_USER 유지.

### [P06-T01] host forwarding 단위 검증 — 2026-11-10 Asia/Seoul
- 실제 Firebase 초기화 없이 host가 토큰 회전과 클릭 payload를 adapter에 전달하는 경로를 검증한다. 실제 권한 대화상자·FCM 서버는 실행하지 않는다.
- host callback 단위시험을 작성했다. test runtime에만 Firebase SDK를 추가하고 mock sample에 google-services 설정은 요구하지 않는다.
- Android host forwarding 단위 1건 통과(skip 0): 토큰 A→B 회전 callback, 빈 토큰 오류, 허용 route만 클릭 전달. google-services 없는 mock sample assemble도 통과했다. 실제 Firebase 초기화·권한 거부·원격 수신은 미실행이다.
- 커밋 전: test runtime 의존성과 fake host unit만 포함한다. P06-T01 실제 platform 검증은 WAITING_USER로 유지.

### [P06-T02] APNs host callback 검증 — 2026-11-10 Asia/Seoul
- iOS simulator에서 host adapter에 synthetic token/payload를 직접 전달하고 sample background completion handler 호출을 확인한다. 실제 APNs 발급/원격 수신은 아니다.
- synthetic host callback와 completion handler XCTest를 별도 scheme으로 작성했다. StoreKit 실패 시험과 혼합하지 않는다.
- iOS 26.5 simulator의 synthetic PushHostTests 1건 통과: token callback, home/store allowlist, sample background completion(.noData) 호출. 실제 APNs token 발급·원격 전송·OS 클릭이 아니다.
- 커밋 전: 별도 iOS host XCTest/scheme만 포함한다. 실제 APNs 및 server token 연결은 미완료이므로 P06-T02 PARTIAL/WAITING_USER 유지.

### [P06-T04] 실 provider 토큰 등록 경로 — 2026-11-10 Asia/Seoul
- sandbox/production의 FCM/APNs 토큰을 인증된 app·session·installation에 암호화 결속한다. 등록 해제/로그아웃 시 즉시 삭제하는 사용자 결정에 맞추며 외부 발송이나 실제 토큰 발급은 하지 않는다.
- provider/platform 검증 및 session/app 소유권을 강제하는 등록/해제 초안을 작성했다. test-only token으로 ciphertext와 logout 삭제를 검증하기 전이다.
- Kotlin compile 성공. sandbox HTTP/security/DB 시험에 synthetic FCM token 등록·암호문·잘못된 platform 거부·logout 즉시 삭제 검사를 추가한다. test-only AES 키 사용.
- sandbox HTTP 등록·logout 삭제 시험 통과. 등록 해제 즉시 삭제 및 AES-GCM AAD 검증도 추가해 재시험한다(합성 토큰만 사용).
- sandbox 실제 HTTP/security/DB 시험 재통과(skip 0): synthetic FCM 등록 ciphertext와 AAD, 명시 해제 즉시 삭제, 재등록 후 logout 즉시 삭제, provider/platform 불일치 거부. 실제 FCM/APNs token이나 원격 발송은 아니다.
- 커밋 전: 실제 profile 토큰 등록·삭제 경로와 synthetic 시험만 포함. Native 등록 연결, 발송 worker·retry/rate 정책 및 실제 플랫폼은 미완료로 P06-T04 PARTIAL 유지.
- 등록 해제 구현 검토 중 동일 app/user/installation에 플랫폼별 행이 둘 이상일 때 DELETE 후 count>1을 오류로 응답하는 불일치를 발견했다. 해당 installation의 소유된 연결이 하나 이상 삭제되면 성공으로 수정한다.
- 기존 sandbox 등록/삭제 회귀 통과. 동일 소유 installation의 두 platform 행을 해제할 때 둘 다 삭제되고 200 응답인지 synthetic 시험을 추가한다.
- synthetic sandbox HTTP 시험에서 같은 installation의 FCM/APNs 두 행을 모두 삭제한 뒤 200, 재등록 후 logout 삭제 확인. 다른 사용자·app 행은 delete 조건에서 제외된다. 실제 push 서비스는 사용하지 않았다.
- 커밋 전: 등록 해제 응답 불일치 수정과 회귀 시험만 포함한다.
- Android Native 내부 등록/해제 client 초안을 작성했다. installation UUID는 Host가 제공하고 session 보호와 fingerprint만 반환한다. fake request 시험을 실행한다.
- Android token 등록/해제 fake 단위시험 통과. iOS도 Host 제공 installation UUID와 현재 session을 사용하고 APNs bytes는 Backend에만 전송하도록 작성해 fake 시험한다.
- iOS push test 컴파일 실패: XCTest autoclosure 안에 async 호출을 직접 넣었다. 제품 코드 오류는 아니며 await 결과를 먼저 받아 재시험한다.
- Swift auth/push fake 단위 11건 통과: APNs bytes→hex, session header, fingerprint, 해제, logout 후 거부. 실제 APNs token이나 network는 아니다. 새 소스의 iOS target compile을 확인한다.
- iOS simulator static framework compile 성공. Android/iOS Native 등록 client는 fake Backend만 사용했으며 호스트 callback에 자동 조립하지 않는다.
- 커밋 전: Native-only token 등록/해제 client와 fake 시험만 포함한다. 실제 FCM/APNs·공개 facade·host 조립은 미완료다.
- P05-T05 계속: Google finalizer 호출 전에 DB의 지급·proof hash·계정·catalog/action과 app별 package 설정을 일치시키는 read-only guard를 구현한다. 완료 후 증빙 보존 정책은 여전히 사용자 결정 대기이며 worker는 연결하지 않는다.
- Google DB grant guard 초안과 synthetic DB mismatch 시험을 작성했다. 테스트에서는 실제 Publisher에 호출하지 않는다.
- synthetic 격리 DB 시험 통과: durable grant가 있을 때만 확인하고 잘못된 proof hash/package/action을 거부했다. 실제 Google 조회와 job 실행은 없다.
- 커밋 전: DB read-only guard 및 test만 포함한다. 암호화 증빙 완료 후 정책과 worker/실 API는 여전히 미완료다.
- 진행 문서 점검: 초기 FINAL_REPORT 양식의 “미실행” 문구가 현재 상황으로 오해되지 않도록 양식 보존 안내를 추가했다. StoreKit 실패는 블로커 표의 ENV-STOREKIT-26으로 이동했다. P11 최종 보고서는 아직 작성하지 않았다.
- 커밋 전: 문서 상태 정확성 수정만 포함한다.

### [P02-T01] 서버 요청 크기 경계 — 2026-11-10 Asia/Seoul
- 계획의 입력 상한 256 KiB를 서버 JSON 요청에도 적용해 credential/proof endpoint가 과대 body를 처리하기 전에 거부한다. Content-Length가 없는 경우도 제한하며 기존 API 응답 형식·request ID를 유지한다.
- 256 KiB 제한 filter 초안은 JSON API body를 최대 상한+1까지만 읽고 413 JSON으로 거부한다. 우선 일반·초과·길이 미지정 fixture를 검증한다.
- server filter Kotlin 컴파일 성공. 정확히 256 KiB 허용과 Content-Length 유무에 관계없이 초과 차단·requestId를 단위시험한다.
- filter unit 1건 통과: 256 KiB까지 전달하고 known/unknown length 초과는 413·PAYLOAD_TOO_LARGE와 일치 requestId를 반환한다. 실제 Spring security/DB HTTP 회귀도 재실행한다.
- filter unit 및 sandbox auth/purchase HTTP 통합 3건 통과(skip 0). Native HTTP client가 413을 PAYLOAD_TOO_LARGE로 반환하도록 두 플랫폼 매핑도 보정하고 검증한다.
- Android core unit 및 Swift BackendClient unit에서 413→PAYLOAD_TOO_LARGE를 확인했다. 실제 플랫폼/외부 서비스 검증은 아니다.
- 커밋 전: 서버 body 상한 filter, Native 오류 mapping 및 단위/통합 시험을 포함한다. P02-T01 전체 완료 판정은 다른 미완료 항목 때문에 유지하지 않는다.

### [P07-T02] Unity Editor offline 샘플 시작 — 2026-11-10 Asia/Seoul
- 기존 사용자 Demo scene은 수정하지 않고 UPM의 별도 Samples~에 home/store uGUI 샘플을 작성한다. `ui-ugui` 지침에 따라 생성 UI를 명시적으로 구성한다. Unity license 오류로 Editor 렌더링은 미검증이다.
- 기존 Demo를 건드리지 않고 Samples~에 Editor offline home/store uGUI 코드 초안을 작성했다. Canvas 및 명시 배너·잔액·두 mock 상품을 포함한다. 실제 화면과 Input System은 아직 확인하지 않았다.
- Unity Editor 실행 없이 설치된 실제 UnityEngine/UI managed assembly와 Unity Newtonsoft package로 샘플 C# 컴파일을 시도한다. 이는 Unity hierarchy 렌더링 검증이 아니다.
- Unity managed assembly 대상 샘플 C# compile 경고0/오류0. 실제 EventSystem은 Host가 기존 input 설정에 맞게 제공하도록 명시하고, 초기화 실패 시 버튼이 활성화되지 않도록 보정해 재컴파일한다.
- uGUI layout 검토에서 childControlHeight=false가 preferredHeight를 적용하지 않는 점을 발견해 두 vertical group에서 true로 수정한다. 시각 렌더링은 Editor 부재로 아직 확인하지 못한다.
- 수정 후 Unity managed assembly 대상 독립 C# compile 경고0/오류0. Editor 렌더링·터치/입력·scene 전환은 라이선스 오류로 NOT_RUN이며, 사용자 기존 Demo와 EventSystem은 수정하지 않았다.
- 커밋 전: 별도 Editor offline sample 및 compile check만 포함한다. 세 sample 전체 연결·실기기·Unity Editor 검증은 미완료이므로 P07-T02 PARTIAL/ENV-002 유지.
- P05-T06 안전 검토: Apple runtime이 서버 verifier/catalog 미구성 상태에서 실제 구매 UI를 열 수 있었다. 인증된 readiness 검사로 app binding·store ID·Apple verifier 설정을 확인한 후에만 UI를 열도록 수정한다. 실제 StoreKit 결제는 실행하지 않는다.
- readiness 검사 초안을 추가했다. Native purchase UI 전에 서버 응답을 요구하며, 검증 중 거래 복구는 readiness에 막지 않는다. fake DB 및 Native unit을 확인한다.
- sandbox 모사 verifier+격리 DB readiness 및 unknown product 거부 시험 통과. Swift fake HTTP 응답 ready=false일 때 차단되는지 확인한다.
- Swift fake HTTP/auth 11건 통과. 실제 Spring security/DB + synthetic registry로 readiness 성공과 미등록 상품 거부를 통합 검증한다.
- sandbox 실제 HTTP/DB + synthetic registry readiness 성공·unknown 상품 404 및 기존 동시 grant 시험 통과. 실제 StoreKit 구매 화면 차단은 실행하지 못했다. simulator framework 컴파일을 확인한다.
- iOS simulator static framework build 성공. 실제 StoreKit UI/상품 조회는 ENV-STOREKIT-26 실패가 남아 있으므로 readiness가 실제 결제 화면을 막는지 OS 수준 검증은 미실행이다.
- 커밋 전: Apple readiness 서버·Native 호출 및 fake/격리 DB 검증을 포함한다. 실제 provider 설정·StoreKit/기기 검증·공개 sample 연결은 미완료다.
- P07-T01 계속: 확인된 maintenance=true일 때 신규 구매만 막고 기존 검증·복구·로그아웃은 허용하는 순수 정책을 구현한다. config offline TTL과 default는 별도이며 이 작업에서 임의 결정하지 않는다.
- Android/iOS 순수 maintenance gate와 회귀시험 작성. 실제 원격 config cache 및 SDK 구매 경로에는 아직 연결하지 않았다.
- Android core 및 Swift gate unit 통과: 점검 중 신규 구매는 거부, 검증·복구·로그아웃은 허용. 실제 config fetching과 구매 UI 적용은 아직 검증되지 않았다.
- 커밋 전: 순수 정책과 unit만 포함하며 P07-T01 PARTIAL 유지.

### [P08-T04] 신규 Unity 소비 프로젝트 검사 시작 — 2026-11-10 Asia/Seoul
- 최신 소스에서 Android/iOS 산출물을 새로 만들고 새 staging을 사용한다. Unity CLI는 새 전용 경로에만 프로젝트를 생성하며 기존 Demo와 사용자의 다른 Unity 프로젝트를 변경·삭제하지 않는다. 라이선스 실패가 반복되면 import는 환경 대기로 기록한다.
- 최신 Android SDK local Maven publish·mock sample·별도 R8 consumer build 모두 종료 0. 다음으로 최신 iOS XCFramework를 새 경로에 생성한다.
- 최신 Apple 코드 포함 무서명 device/simulator archive 및 XCFramework 생성 성공, module-map 경고 없음. 새 output에 Unity staging을 생성해 checksum을 확인한다.
- 최신 staging 생성 및 checksum 101개 검증 성공. 새 `artifacts/GameBridgeConsumerP08` 경로에서 Unity CLI로 독립 프로젝트 생성을 시도한다. 기존 경로가 있으면 실행하지 않는다.
- Unity CLI 새 소비 프로젝트 생성 실패: Editor exit 198 licensing failure. import 이전 종료이며, 실제 UPM 재설치·씬·Android/iOS export는 실행되지 않았다. 기존 Demo/다른 프로젝트는 건드리지 않았다. ENV-002 유지.
- 사용자 정책 결정 수신: push retry 최대 3회/5초 지수, 개발 발송 관리자 키별 분당 10회, Google 완료 증빙 즉시 삭제, 세션 push ID 최근 200개, usable config 없으면 신규 구매 차단. APNs 5xx는 최소 15분 후 재시도하도록 추가로 결정했다. 문서에 기록하고 코드·검증에 반영한다.

### [P05-T05] 사용자 결정 반영 — Google finalizer worker
- 기존 승인 동시 1개·5초 지수 백오프와 신규 결정 완료 확인 즉시 증빙 삭제를 durable DB worker에 반영한다. 외부 Store 호출은 DB transaction 밖에서 하며 테스트에서는 fake executor만 사용한다.
- Google worker/공식 Publisher lazy executor 초안 작성. 성공 시 job DONE과 암호문 NULL을 같은 DB transaction에 기록하고 실패는 증빙을 보존한다. 테스트 전이며 실제 Play 호출은 하지 않았다.
- Google worker 컴파일 성공. test-only 암호화 거래와 fake finalizer로 전역 동시 1개, 첫 실패의 증빙 보존·5초 backoff, 성공 시 job/암호문 원자 삭제, 원장 불변을 격리 DB에서 검증한다.
- Google worker 격리 DB 시험 통과: advisory slot 1개, 첫 실패의 증빙 유지/5초 backoff, 재시도 성공 시 DONE·FINALIZED·증빙 NULL과 원장 불변 확인. cache가 claim 객체를 붙잡지 않도록 조정하고 성공 시 구매 상태 update 실패는 전체 transaction rollback하도록 강화한다.
- 개선 후 Google worker 격리 DB 시험 재통과. sandbox profile의 실제 Spring bean 조립과 기존 인증 HTTP 회귀를 별도 시험 DB에서 확인한다. 외부 credential은 제공하지 않는다.
- sandbox Spring context와 인증/Apple synthetic HTTP 통합 2건 통과(skip 0). 실제 Google credential 없이 lazy executor가 서버 시작을 막지 않음을 확인했다. 실제 Google finalization은 실행하지 않았다.
- 커밋 전: 사용자 결정 6건 기록 및 Google worker·fake DB 검증을 포함한다. push retry/rate, message dedup, config default는 승인된 기준으로 구현 진행 중이며 실제 Play·remote push는 미검증이다.

### [P06-T04] 승인된 push retry·rate 정책 — 2026-11-10 Asia/Seoul
- 초기 시도 후 최대 3회 재시도, 5초 지수 백오프와 APNs 5xx 최소 15분을 명시한다. 개발 API 관리 key별 rolling 1분 10회 제한을 구현한다. endpoint·실제 발송 연결은 별도다.
- pure retry/rate 초안 및 fake monotonic clock 시험 작성. 관리자 key 원문은 rate map에 저장하지 않는다. 실제 endpoint는 미연결이다.
- fake clock retry/rate unit 2건 통과: 초기 시도 뒤 3회 5/10/20초, APNs 5xx 각 최소 900초, key별 분당 10회. 선택한 값을 설정으로 노출하고 sandbox startup 회귀를 검증한다.
- sandbox 설정 주입·HTTP 회귀 통과. retry 정책은 production에서도 필요하지만 dev limiter는 local/sandbox에만 존재하도록 profile 범위를 분리한다.
- profile 조정 후 retry/rate unit 재통과. dev endpoint/worker에 정책을 아직 적용하지 않았으므로 실 요청 제한이나 retry가 동작한다고 기록하지 않는다.
- 커밋 전: 사용자 승인된 pure 정책·설정·fake clock 시험만 포함, P06-T04 PARTIAL 유지.

### [P06-T05] 사용자 승인 dedup 기준 반영
- 각 앱 세션에서 최근 messageId 200개를 기억하고 초기화 전 최대 100개 이벤트를 대기한다. 수신과 열기는 다른 이벤트로 보존하되 같은 종류의 중복을 차단한다. 계정 변경/logout 시 전체 상태를 비우는 명시적 reset을 제공한다.
- Android/iOS pure router 초안 작성. 세션 초기화 전 queue, 수신/열기 구분, 200 ID LRU와 reset을 fake unit으로 확인한다. 실제 OS callback 연결은 아직 없다.
- Android core 및 Swift router unit 각각 통과. 두 플랫폼의 full queue에서 기존 ID recency 처리 차이를 맞추고 실제 LRU 갱신/퇴출을 추가 시험한다.
- Android/Swift router unit 재통과: 100개 대기 한도, 실패한 overflow 재시도, 수신/열기 구분, 200 ID LRU 및 reset 확인. 실제 lifecycle·OS 알림 callback과는 아직 연결되지 않았다.
- 커밋 전: 승인된 dedup/queue 순수 router와 단위시험만 포함한다. Native/Unity 연결·실원격 수신은 미완료다.

### [P07-T01] config 부재 시 구매 안전 기본값
- 사용 가능한 서버 설정/캐시가 없을 때 신규 구매를 차단하고 진행 중 거래 검증·복구·로그아웃을 허용하는 사용자 결정을 반영한다. 기본 cache TTL 숫자는 별도 사용자 결정 대기다.
- Android/iOS pure gate에서 config 부재(nil)를 fail-closed로 처리하도록 수정했다. 단위시험 후 실제 구매 경로에 연결한다.
- Native config repository는 서버 제공 expiry가 미래일 때만 cache를 사용하며, timeout/오프라인은 유효 cache로 fallback하고 없으면 nil을 반환한다. 숫자 TTL은 테스트 fixture일 뿐 정책이 아니다.
- Android config cache unit 통과. Swift 컴파일 실패: async BackendClient.request 호출에 await를 빠뜨렸다. 수정 후 재실행한다.
- Swift config actor의 동시 fetch가 서로 다른 응답을 덮어쓸 수 있어 하나의 in-flight 요청을 공유하도록 보강한다. 동시 요청 fake 시험으로 확인한다.
- Swift 동시 config fetch 1회 공유 단위시험 통과. 늦게 재개한 이전 waiter가 더 최신 cache를 덮어쓰지 않게 flight 소유자만 cache 갱신하도록 보정한다.
- Native config cache unit 통과. Android/iOS 실제 store runtime에서 구매 시작 전 알려진 정상 config만 허용하도록 연결하고, 검증·복구·logout 경로는 차단하지 않는다. fake gate 단위시험을 실행한다.
- Android sdk unit 통과: config 없음/점검 시 Billing UI 미실행, 정상 config의 기존 fake flow 유지. Swift 내부 runtime의 동일 차단을 fake config로 검증한다.
- Swift fake config·auth 15건 통과. Android에서 config 미상일 때 신규 구매 UI만 차단하고 store recovery는 계속 호출되는지 별도 확인한다.
- Android fake store 시험에서 설정 미상 구매 UI 차단과 recovery 허용을 확인했다. 현재 서버 기본 config에는 expiry가 없어 실제 store runtime은 차단 상태이며 TTL 사용자 결정이 필요하다. local-mock sample gate는 미연결이다.
- 커밋 전: 승인된 안전 기본값, 유효기간 기반 메모리 cache 및 Native store gate와 fake unit만 포함한다. server TTL·영속 cache·sample/Unity 연동은 미완료로 P07-T01 PARTIAL 유지한다.

### [P02-T05] 보호된 개발 push endpoint
- 별도 admin key·installation allowlist·현재 사용자 소유권·분당 10회 제한을 적용한다. local-mock은 SIMULATED만 반환하며 sandbox 실제 sender 미연결 시 fail-closed한다. production에는 route를 등록하지 않는다.
- local-mock/sandbox dev endpoint 초안은 key·allowlist·소유권·route·rate를 검사한다. sandbox sender는 아직 CONFIG_REQUIRED이며 실제 push를 실행하지 않는다. compile 및 HTTP fixture를 확인한다.
- auth rate filter와 body filter가 같은 우선순위였으므로 auth rate 검사 후 body 제한이 적용되도록 순서를 명시했다.
- 별도 local-mock HTTP 시험으로 익명/잘못된 admin/미허용 installation/다른 사용자 거부 및 관리자 키당 10회 제한을 확인한다. 실제 원격 발송은 하지 않는다.
- local-mock 진짜 HTTP/security/DB 시험 통과: key·allowlist·소유권 거부와 10회 이후 429 확인. 429의 retryable flag를 true로 보정하고 production route 미등록도 검증한다.
- local-mock 실제 HTTP 및 production web slice 총 2건 통과(skip 0): 사용자 인증·별도 admin·allowlist·소유권·분당 10회, production route 404. local-mock은 SIMULATED이고 sandbox sender는 fail-closed다.
- 커밋 전: 개발 endpoint 접근 통제와 mock 응답만 포함한다. sandbox 실제 sender, retry worker 및 전체 push 전달·클릭 smoke는 미완료로 P02-T05/P06-T04 PARTIAL 유지.
- P06-T04 계속: 실제 발송 중 폐기된 토큰은 삭제가 아니라 비활성화하고, 오래된 응답이 새로 회전한 토큰을 비활성화하지 않게 hash 조건을 둔다. 재시도 worker 동시성은 사용자 선택을 기다린다.
- nullable invalidation migration과 hash 조건부 비활성화/재등록 해제를 작성했다. sandbox synthetic rotation race를 HTTP/DB로 검증한다.
- sandbox synthetic HTTP/DB 시험 통과(skip 0): 회전 전 hash의 늦은 invalidation은 새 토큰에 영향 없고, 현재 hash는 비활성화되며 재등록 시 해제된다. 실제 FCM/APNs invalid response는 아직 미실행이다.
- 커밋 전: nullable migration·조건부 invalidation 및 회귀시험만 포함한다. sender 연결과 동시성 정책은 미완료다.
- P06-T04 실제 sender의 앱별 FCM service account와 APNs .p8 설정을 lazy 로드하는 registry를 작성했다. 설정 누락 시 503이며 원격 발송 전에 단위시험한다.
- lazy provider registry编译成功。synthetic P-256 key와 임시 test-only 파일로 APNs 구성/cache 분리 및 FCM/APNs 누락 설정 실패를 확인한다. 네트워크 요청은 없다.
- synthetic APNs EC key 기반 lazy registry/cache 및 누락 FCM/APNs config, fake sender unit 총 5건 통과. 실제 .p8/service account/원격 전송은 사용하지 않았다.
- 커밋 전: 실제 provider 구성·단발 sender의 lazy 조립만 포함한다. sandbox dev endpoint 연결·retry worker·실 인증정보 검증은 미완료다.
- APNs 5xx와 429에 서로 다른 승인 재시도 간격을 적용할 수 있도록 단발 sender 결과에 redacted failure 종류를 추가한다. fake status/exception mapping을 재검증한다.
- FCM/APNs failure 종류 mapping 검증 통과. push content의 자동 문자열화가 제목·본문을 노출할 수 있어 redaction을 추가하고 잘못된 FCM 메시지는 영구 오류로 분류한다.
- fake sender/config/policy unit 7건 통과: APNs 429·5xx failure 구분, token/content 정제, 서명/cache 및 제한 정책. 실제 remote push는 없다.
- 커밋 전: 단발 sender 결과 분류와 redaction만 포함한다. 실제 endpoint retry worker 동시성은 사용자 결정 대기다.
- P06-T04 계속: sender가 매 시도마다 현재 session/installation 소유의 활성 token만 DB에서 조회·복호화하고 invalid 응답은 같은 hash에만 적용하도록 만든다. worker 동시성 선택 전 endpoint 자동 발송에는 연결하지 않는다.
- token을 보유하지 않는 단발 dispatcher 초안을 작성했다. 활성 session·app·설치/user를 재조회하고 중복 플랫폼 record는 전송하지 않으며 invalid 응답은 같은 hash에만 적용한다.
- dispatcher를 fake provider·격리 PostgreSQL에서 검증한다. 전송 중 token 회전 후 이전 invalid 응답은 새 token에 영향을 주지 않고 logout 후 재시도는 호출되지 않아야 한다.
- synthetic rotation/logout DB 시험 통과. 추가 검토에서 요청자 logout 후 같은 사용자가 새 session에 token을 재등록하면 이전 retry가 전송될 수 있어, 요청자 session도 재검증하고 회귀시험한다.
- 격리 DB fake dispatcher 재검증 통과: 오래된 invalid 응답이 회전 토큰을 비활성화하지 않고, logout 후 새 session이 재등록해도 이전 session의 대기 발송은 거부된다. 이미 네트워크 전송이 시작된 요청은 취소 보장하지 않는다.
- 커밋 전: DB token 재조회·조건부 invalidation dispatcher와 fake 시험만 포함한다. sandbox endpoint/worker에는 아직 미연결이며 실제 push는 없다.
- push worker 동시성 및 server config 기본 TTL의 사용자 선택 대기를 blocker 표에 등록했다. 이 값이 필요한 scheduler/default는 결정 전 활성화하지 않는다.
- 커밋 전: 미결정 항목 문서화만 포함한다.
- 사용자 결정 수신: server config cache 기본 TTL 5분, push worker 기본 동시 1건(설정 가능). 결정 문서에 기록하고 구현·검증한다.
- 사용자 결정 수신: 서버 점검 상태 미설정 시 신규 구매 차단. 설정됨을 가장하지 않고 config endpoint는 명시 여부 없으면 CONFIG_REQUIRED로 응답하도록 구현한다.
- server config endpoint는 명시적 true/false가 없으면 503, 설정 시 선택한 기본 TTL 300초의 expiry를 제공하도록 작성한다. 실제 운영 점검값을 자동 선택하지 않는다.
- config controller unit 통과: 미설정 503, 명시 false/true와 기본 TTL 300초 확인. Android/iOS local-mock 신규 구매 전에 config gate를 연결한다. 검증·복구·logout은 영향을 받지 않는다.
- Android core unit 통과, Swift 전체 40건 중 37 통과·local Backend opt-in 3 skip. 명시적 GAMEBRIDGE_MAINTENANCE_ENABLED=false와 test-only 키로 전용 local-mock 서버를 시작해 실제 Native↔Backend 통합 회귀를 실행한다.
- 명시 정상 config로 실행한 local Backend에서 Android core integration 재실행 통과, Swift 전체 40건 중 40 통과(skip0). config 미설정/점검 시 신규 구매만 막고 wallet/logout을 유지하는 fake HTTP 회귀를 추가한다.
- Android fake HTTP config 미설정·maintenance 차단 및 wallet/logout 허용 시험 통과. 같은 동작을 Swift fake URLProtocol로 확인한다.
- Swift fake HTTP 시험 1건 통과했으나 async 테스트에서 직접 NSLock을 사용해 Swift 6 경고가 발생했다. 동기 helper로 이동해 재확인한다.
- Swift fake HTTP 재시험 경고 없이 통과. Android fake server 상태를 atomic으로 바꿔 시험 간 thread 가시성을 보강한다. 문서에 명시적 maintenance 설정을 추가한다.
- 수정된 local-mock config 응답을 포함한 device smoke를 기동 중인 전용 Backend에서 실행한다. 새 시험 데이터만 생성하며 원격 push는 하지 않는다.
- local-mock device smoke 19 assertions 통과, 원격 push 없음. 직접 기동한 Backend만 종료했고 전용 DB/volume과 시험 기록은 보존했다. sandbox 실제 HTTP에서 점검 미설정 시 503을 확인한다.
- sandbox synthetic HTTP 통합에서 점검 미설정 config 503 CONFIG_REQUIRED 확인. Android/iOS fake test에서는 미설정·점검 시 새 구매만 차단하고 wallet/logout은 허용했다.
- 커밋 전: 사용자 선택한 명시 설정 전 차단, 5분 TTL, Native local-mock gate와 시험을 포함한다. config cache의 재시작 후 영속성과 Unity 적용 및 실제 플랫폼 검증은 미완료다.
- 交叉 검토에서 Android local-mock은 logout 후 config를 먼저 조회해 Swift와 다른 오류를 반환할 수 있음을 발견했다. 인증 상태를 먼저 확인하도록 맞추고 회귀시험한다.
- Android core unit 통과: logout 뒤 구매는 SESSION_EXPIRED, config 미설정·점검의 신규 구매는 각각 CONFIG_REQUIRED/MAINTENANCE다.
- 커밋 전: 오류 우선순위와 fake HTTP 회귀만 포함한다.
- P06-T04 계속: 사용자 선택 동시 1건과 3회 retry를 sandbox 개발 발송에 연결한다. 재시도 대기에는 token 원문을 보관하지 않고 매회 DB 소유권을 재확인한다. 테스트는 fake provider로만 실행한다.
- sandbox sender와 제한된 in-memory retry worker 초안을 연결했다. provider credentials는 최초 수동 요청 때 확인하며 queue에는 token 대신 installation/session만 저장한다. 아직 테스트 전이고 실제 remote push는 실행하지 않는다.
- worker queue는 기존 100 상한을 지키고 queue full과 미등록 장치를 분리한다. 1초는 test-only 지연으로 사용해 동시 1건/일시 실패 retry를 단위시험한다.
- 1초 test-only worker 시험에서 동시 1건과 재시도 실행을 확인했다. FCM이 messaging-specific code 없이 일반 UNAVAILABLE/DEADLINE_EXCEEDED를 내는 경우도 retry로 분류하도록 보강한다.
- sandbox 실제 HTTP/security/DB 경로에 mock FCM provider를 주입해 수동 요청→QUEUED→일시 실패 retry를 확인한다. 1초는 시험 전용이며 실제 remote push는 호출하지 않는다.
- sandbox synthetic HTTP→fake FCM 시험 통과: 승인된 route가 QUEUED 후 시험용 1초 retry로 성공, token은 응답에 없음. worker의 최초 시도+3회 제한과 queue 100 초과 거부도 fake 시험한다.
- fake worker에서 최초+3회 종료, 동시 1개와 queue 100 제한 확인. DB 일시 연결 장애도 token 재조회 자체를 재시도하도록 구분해 시험한다.
- worker fake 시험 4건 통과: 동시 1건, 100개 제한, 최초+3회 후 종료, DB 일시 오류 재시도. sandbox HTTP 및 local dev/production route 회귀를 다시 실행한다.
- sandbox HTTP/security/DB→fake FCM QUEUED/retry 및 production 개발 route 미등록 시험 2건 통과(skip 0). 실제 서비스 자격증명·원격 발송은 사용하지 않았다. retry queue는 in-memory여서 서버 재시작 시 소실되고, 이미 시작된 원격 요청 취소는 보장하지 않는다.
- 커밋 전: 사용자 선택 동시 1건/3회 retry, APNs 5xx 최소 15분, 제한 queue 및 sandbox 개발 sender 조립을 포함한다. production sender runtime, 실제 수신·token 발급·원격 발송과 재시작 복구는 미검증 또는 미구현이므로 P06-T04 PARTIAL/WAITING_USER 유지.

### [P05-T04] Google 실 검증 경로 연결
- 승인된 증빙 삭제 기준과 worker가 구현되어 Google sandbox/production verify endpoint 및 구매 전 readiness를 연결한다. 실제 Play API/구매는 실행하지 않고 synthetic Publisher fixture로 검증한다.
- Google verifier의 30초 network timeout, server readiness(구매 binding·catalog·credential·암호화 키)와 verify endpoint 초안 작성. 실제 Play 서버는 호출하지 않았다.
- Google server Kotlin compile 성공. Native sink 및 공유 runtime에 readiness를 연결하며 config 미설정·credential 누락 시 Billing UI가 열리지 않게 한다.
- Android gate 初次 unit 通过. readiness가 없거나 false면 실제 UI를 시작하지 않는 fake 시험과 JSON boolean 엄격 검증을 추가한다.
- Google verify→durable grant→fake finalizer→증빙 삭제를 실제 sandbox HTTP/security/PostgreSQL에서 동시 요청 10건으로 검증한다. Publisher/완료 응답은 test-only fake이며 외부 Play 호출은 없다.
- synthetic Google HTTP 10건→원장 1건→fake 완료 후 증빙 NULL 통합 시험 통과. readiness의 암호화 키 부재 및 pending 증빙 무지급도 추가 확인한다.
- 격리 local DB readiness의 암호화 키 누락 503, sandbox 실제 HTTP/security/DB에서 synthetic PENDING 무지급, 10개 동시 verify 중 grant 1건 및 fake 완료 뒤 증빙 NULL을 확인했다. 실제 Google Play 조회/결제/consume/ack는 미실행이다.
- 커밋 전: Google verifier/readiness/HTTP·Native sink 조립 및 synthetic 통합만 포함한다. 실제 Play와 sample/Unity는 미완료로 P05-T04/T05/T07 PARTIAL·WAITING_USER 유지한다.
- 1차 feature matrix와 통합 안내의 과거 “Google verify endpoint/worker 미연결” 문구를 현재 synthetic 연결 상태로 정정했다. 실제 외부 검증 미완료 표기는 유지한다.
- 커밋 전: 추적 문서 정정만 포함한다.

### [P06-T03] Unity iOS push host adapter
- Unity 공식 registry의 com.unity.mobile.notifications 최신 2.5.0(Unity 6000.0+)을 선택했다. 사용자 프로젝트 manifest는 편집하지 않고 SDK package dependency로 명시한다. Editor import는 ENV-002로 미검증이다.
- Unity Mobile Notifications 2.5.0 공식 source/API를 확인했다. iOS 전용 별도 assembly와 internal host operation을 작성한다. 현재 Swift bridge는 host operation 미구현이므로 응답은 명시적 UNSUPPORTED이며 완료로 기록하지 않는다.
- iOS host adapter 초안은 명시적 permission 요청, foreground callback 및 last-opened, 100 queue/200 ID dedup, internal host operation 전송을 구현한다. foreground remote callback 구독은 Unity package 특성상 기본 표시를 막으며 실제 UI 표시 정책은 별도다.
- host adapter 검토에서 local 알림을 remote open으로 오인하지 않도록 push trigger를 확인하고, token 완료 시 attach된 client가 바뀐 경우 이전 성공 상태를 노출하지 않도록 보강했다.
- Unity Notifications 2.5.0 공식 source와 실제 Unity managed reference를 별도 .NET assembly로 컴파일해 adapter API 계약을 확인한다. Unity Editor/IL2CPP 실행은 아니다.
- Unity package 2.5.0에서는 기존 GetLastRespondedNotification이 deprecated여서 비동기 Query API로 변경한다. queue 파서를 Unity 없이 시험할 수 있도록 분리한다.
- Unity official source 기반 3개 assembly 컴파일 경고0/오류0. host attach 변경 중 지연 callback이 새 client 상태를 오염시키지 않도록 검사하고, 분리한 queue의 fake 입력 회귀를 추가한다.
- Unity iOS host code/official source 3개 assembly compile 및 queue smoke 통과. NSNumber messageId의 암묵 변환 방지, authorization error와 거부 구분, coroutine 종료 시 gate 반환을 보강한다.
- Unity Notifications 2.5.0 공식 source와 Unity managed reference의 iOSHost 별도 assembly compile 경고0/오류0, normalized queue fake smoke 통과. Editor/Android/iOS/unsupported C# 조건부 compile 각 통과. Unity Editor import/IL2CPP/실 remote 및 Swift host operation은 미실행·미구현이다.
- 커밋 전: Unity iOS host adapter, 패키지 의존성, internal 전달 경계, 독립 compile/smoke만 포함. Swift host operation 미연결로 P06-T03 PARTIAL/WAITING_USER 유지.

### [P05-T07] Apple Native store facade
- 내부 Apple runtime을 공개 Native facade에 연결하고 서버가 확정한 구매 ID와 entitlement 조회만 노출한다. StoreKit proof·계정 binding·session token은 공개 결과에 넣지 않는다. 실제 Apple UI와 서명 시험은 대기다.
- AppleStore 공개 facade 초안은 StoreKit 가격, server purchase ID, entitlement만 제공하고 raw proof는 포함하지 않는다. Swift unit 및 platform build를 확인한다.
- Swift auth unit 12건 통과했으나 async 결과 미사용 경고가 있어 명시 처리했다. 공개 entitlement가 현재 session user와 다르면 거부하는 fake HTTP 시험을 추가한다.
- Apple auth/store fake 단위 15건 통과: 현재 session 외 entitlement 거부 포함. simulator static framework compile을 실행한다.
- AppleStore 포함 iOS simulator static framework compile 성공. 실제 StoreKit 구매/finish 및 샘플 UI 연결은 미실행이며 이전 XCFramework staging은 갱신 전이다.
- 커밋 전: 공개 Native facade 및 fake entitlement 검증만 포함한다. P05-T07 PARTIAL/실 Apple WAITING_USER 유지.
- 보안 검토에서 공개 AppleStore가 인증 provider와 다른 Backend 설정을 받을 수 있음을 발견했다. 이 경우 세션 token이 잘못된 서버로 전송될 수 있으므로 구성 일치 검사를 추가하고 회귀시험한다.
- Swift fake 13건 통과. public AppleStore가 다른 서버 설정을 CONFIG_REQUIRED로 거부함을 명시 검증하고, Android 공개 facade에 사용할 동일 config 비교 경계도 추가한다.
- Swift auth fake 13건 및 Android sdk unit task 통과: AppleStore가 다른 Backend config를 CONFIG_REQUIRED로 거부하며, Android auth의 설정 비교도 확인했다. 실제 네트워크에 토큰을 보내지 않았다.
- 커밋 전: Apple 공개 생성자의 구성 일치 강제와 Android 내부 비교 경계만 포함한다. 실제 계정·스토어 검증은 별도다.

### [P05-T07] Android Native store facade
- Google auth와 Backend config가 정확히 일치할 때만 공개 store facade를 조립한다. 상품·상태·서버 entitlement만 노출하고 proof/token은 Native 내부에 둔다. 실제 Play UI는 실행하지 않는다.
- Android facade 초안과 public Flow의 전이 의존성(api)을 설정했다. init config 불일치 시 즉시 거부하며 Billing client 생성 전 상품 mapping을 검증한다. compile 및 unit을 확인한다.
- Android facade와 mock sample build 통과. 불필요한 JSON 객체 재생성을 줄이고 다른 사용자 entitlement 거부 시험, Maven 소비자의 public Flow 전이 의존성 compile을 추가한다.
- Android sdk unit 및 Maven publish는 통과했으나 독립 consumer release build 실패. 원인을 확인하기 전 배포 소비 성공으로 기록하지 않는다.
- 원인: 새 소비자 Kotlin task는 기본 JVM 21, Java는 17이라 target 불일치. SDK와 동일한 JVM 17로 지정해 전체 packaging/consumer build를 재실행한다.
- 독립 consumer failure는 JVM target 17 통일 후 R8 release build 통과. Android 공개 facade의 인증/Backend 일치 및 상품 mapping 사전 검사를 독립 unit으로 보강한다.
- Android store config/unit 재실행 통과: 다른 Backend 및 중복 상품 ID 거부. 마지막 SDK 변경을 포함해 local Maven publication과 별도 consumer R8 compile을 다시 확인한다.
- Android unit 및 최신 Maven publish·mock sample·source 없는 Kotlin Flow consumer의 R8 release build 재통과. 최초 JVM 21/17 불일치 실패는 consumer target 17로 수정했다. 실제 Play UI/스토어는 미실행이다.
- 커밋 전: Android public facade·entitlement 사용자 검증 및 Maven API dependency/consumer compile만 포함한다. Native sample/Unity 연동과 실제 Play 시험은 미완료다.
- P07-T02 계속: 기존 local-mock 샘플을 보존하고 별도 Apple Sandbox 화면에 실제 auth/store facade를 연결한다. 화면의 명시적 버튼 없이 로그인·구매를 실행하지 않는다.
- Apple Sandbox 샘플 화면 초안은 host 입력 구성·명시적 로그인/store 연결/구매/복원·서버 잔액을 제공한다. 실제 계정·결제는 실행하지 않고 simulator build/UI 회귀를 확인한다.
- iOS sandbox sample simulator build 성공. 빈 설정 오류를 UI에서 CONFIG_REQUIRED로 표시하도록 보정하고, 실제 계정 없이 sandbox 화면의 명시적 설정 차단과 기존 local-mock UI를 XCTest로 확인한다.
- iOS Sandbox 화면의 빈 설정 UI XCTest 1건 실패: CONFIG_REQUIRED 상태 기대를 5초 내 관찰하지 못했다. 기존 local-mock UI 시험은 계속 실행 중이며, 원인을 확인하기 전 전체 PASS로 기록하지 않는다.
- 同一 UI suite의 local-mock 상품 버튼 확인도 실패했다. 로그인/설정/화면 상태 원인을 조사하고 두 실패를 모두 재검증하기 전 UI PASS로 기록하지 않는다.
- UI 실패 분석: sandbox 상태가 긴 Form 하단에 있어 찾기 어려웠다. 상태를 설정 상단에 배치하고 local-mock 로그인 성공을 명시적으로 기다려 실제 실패 지점을 확인한다. 기존 실패 기록은 유지한다.
- sandbox UI 재시험에서도 Configure 버튼이 화면 밖 hit point로 실패했다. 스크롤 탐색을 개선하며, 실행 중인 Mock UI 결과는 별도로 확인한다.
- 재실행 결과 sandbox UI 버튼 위치와 local-mock 로그인 상태 확인 모두 실패했다. 두 UI 시나리오는 여전히 FAIL이며, status 가시성/실제 오류값을 분리해 진단한다.
- xcresult의 status attachment에서 local-mock 로그인 상태가 실제 INTERNAL_ERROR였음을 확인했다(단순 조회 실패가 아님). unsigned simulator의 Keychain 접근 가능성을 포함해 재현한다. sandbox UI는 짧은 스크롤과 bounds 확인으로 보정한다.
- ad-hoc signed simulator 재시도에서 sandbox Configure도 offscreen으로 판정되어 UI 시험이 다시 실패했다. 상태/설정 버튼을 navigation toolbar에 고정해 스크롤 의존성을 제거한다.
- ad-hoc simulator 서명 후 local-mock 로그인·구매·재시작 복원은 진행됐지만 signOut 버튼 hit point에서 실패했다. 앞선 unsigned INTERNAL_ERROR는 Keychain 서명 조건과 일치하는 정황이나 단정하지 않는다. Sandbox 설정 버튼도 화면 밖 접근 실패여서 status/action을 고정 배치한다.
- ad-hoc simulator 재시험: sandbox 빈 설정 차단은 통과했지만 local-mock 재시작 후 logout 상태 기대가 실패했다. logout의 실제 상태값을 결과 bundle에서 확인한다.
- 결과 attachment의 logout 후 status는 여전히 Restored였고 해당 시험 session은 revoked되지 않았다. sticky status 영역에 가려진 버튼 hit 가능성을 줄이도록 안전한 화면 중앙 영역으로 스크롤하고 enabled 상태를 기다린다. sandbox Configure는 toolbar 고정으로 scroll하지 않는다.
- iOS 26.5 ad-hoc simulator 서명 UI 재시험 2건 통과: Sandbox 빈 설정 CONFIG_REQUIRED 및 LOCAL_MOCK 로그인→구매→재시작 복원→로그아웃. 실제 Apple 계정/스토어 거래는 실행하지 않았다. 이전 unsigned Keychain INTERNAL_ERROR 및 두 UI hit-point 실패는 이력으로 보존한다. 직접 기동한 Backend만 종료하고 DB/volume은 보존했다.
- 커밋 전: iOS sandbox 화면, 기존 Mock 상태 표시 및 UI 시험만 포함. 실제 Apple Sandbox·Android 실제 sample·Unity player 및 P07 전체 검증은 미완료다.
- Android 샘플 연결 전 기존 KeystoreTokenStore가 Mock과 실제 provider의 동일 저장 항목을 사용해 서로의 세션을 덮어쓸 수 있음을 발견했다. 기존 default 항목은 보존하고 별도 namespace를 추가한다.
- Android unit/build 통과. 기존 Java 소비자의 1인자 constructor 호환성을 유지하도록 @JvmOverloads를 추가하고 bytecode를 확인한다. 실제 Keystore namespace 분리 기기 검증은 별도다.
- Android Keystore namespace의 기기 동작을 확인하기 위해 전용 AVD에만 설치하는 instrumented test를 작성한다. test 전용 무작위 namespace만 사용하고 기존 기본 session 항목은 읽거나 삭제하지 않는다.
- sample APK 및 Android instrumented test APK build 성공. 기존 전용 AVD만 무창으로 기동해 namespace 시험을 실행하며 사용자 AVD나 데이터 초기화는 하지 않는다.
- 전용 Android 36 emulator에서 instrumented Keystore namespace 시험 1건 통과: 두 무작위 test namespace가 서로 덮어쓰지 않고 한쪽 삭제가 다른 쪽에 영향 없음. 기존 default 사용자 session은 읽거나 지우지 않았다. Java 1인자 생성자도 bytecode에서 확인했다.
- 커밋 전: namespace 분리와 전용 AVD 검증만 포함한다. 실제 Google 계정 및 상점은 미실행이다.
- P07-T02 계속: 기존 Android local-mock 화면을 유지하고 별도 Google Sandbox 화면을 추가한다. provider/coordinator는 ViewModel에서 화면 전환 동안 유지하고 로그인·구매는 명시적 버튼에서만 시작한다.
- Google Sandbox sample 초안은 별도 Keystore namespace와 ViewModel 소유 coordinator를 사용한다. user가 설정·로그인·store·구매를 명시적으로 누르기 전 외부 호출하지 않는다. 컴파일 및 전용 emulator 확인을 진행한다.
- Android sandbox sample assembleDebug 성공. 빈 config 예외를 CONFIG_REQUIRED로 표시하고 전용 emulator에서 화면 진입·구성 거부만 확인한다. Google 계정 또는 실제 Billing UI는 시작하지 않는다.
- 전용 Android 36 emulator에서 Google Sandbox 화면 진입과 빈 config의 CONFIG_REQUIRED 표시를 확인했다. 실제 Google 로그인이나 Play 구매는 시작하지 않았다. 기존 local-mock 흐름 회귀를 실행한다.
- Android local-mock UI 회귀는 로그인·앱 재시작·복원까지 진행했으나 Signed out 상태를 관찰하지 못해 실패했다. 원인을 확인하기 전 전체 UI 통과로 기록하지 않는다.
- Android 화면에는 `NETWORK_UNAVAILABLE — local session cleared; server revoke unconfirmed`가 표시됐다. 서버/에뮬레이터 포트는 열려 있어, 테스트 전용 namespace를 이용한 instrumented 로그인→복원→logout으로 네트워크 경로를 분리한다.
- 전용 emulator instrumented 로그인/복원 후 logout도 NETWORK_UNAVAILABLE로 재현되어 단순 UI hit 문제가 아님을 확인했다. test-only session으로 body 없는 POST의 Android HttpURLConnection 예외 종류만 확인한다(토큰/응답 원문 출력 금지).
- Android 직접 HttpURLConnection test에서 body 없는 logout POST가 서버 HTTP 500을 반환하는 것을 확인했다. 이전 NETWORK_UNAVAILABLE은 서버 500 매핑이었고 실제 네트워크 단절이 아니다. 예외 class만 정제 로깅하고 동일 form-content POST를 sandbox HTTP test로 재현한다.
- sandbox HTTP test에서도 body 없는 form-content logout이 실패해 서버 오류를 재현했다. 정제된 예외 class를 확인해 원인을 수정한다.
- 서버 정제 로그로 HttpMediaTypeNotSupportedException을 확인했다. Android의 빈 form-content POST도 받을 수 있게 logout을 ByteArray body로 수신하고, refresh logout JSON은 명시적으로 파싱해 기존 인증/오류 경계를 유지한다.
- logout 수정 최초 컴파일 실패: nullable ByteArray에 isNullOrEmpty 확장이 없다. null/empty를 명시 분기해 재검증한다.
- sandbox 실제 HTTP 테스트에서 빈 form-content access logout과 refresh JSON logout이 모두 통과했다. 직접 기동한 local 서버를 새 코드로 재시작해 Android emulator instrumented/UI 회귀를 확인한다.
- 전용 Android emulator instrumented 3건 통과: 독립 namespace, body 없는 form logout, 실제 local-mock 재시작 session 복원/로그아웃. 기존 Android UI smoke를 재실행한다.
- 수정된 서버에서 전용 Android UI login→재시작→restore→logout smoke 통과. Android 3 instrumented tests도 통과했으며 실제 Play/Google은 아니다. 실패한 form-content logout은 BUG-008로 기록·해결했다.
- 커밋 전: 서버 logout media-type 수정·정제 예외 class 로그 및 Android 기기 회귀시험만 포함한다. 샘플 화면 변경은 별도 커밋한다.
- Android sandbox sample 검토에서 빈 Google server client ID를 초기 구성 단계에서 거부하고, callback 취소를 삼키지 않도록 수정했다. iOS 설정 입력도 구성 후 잠가 실제 적용값과 화면값이 어긋나지 않게 한다.
- 수정 후 전용 Android emulator에서 Google Sandbox 빈 설정 차단 재통과. 기존 local-mock UI 재실행도 통과했고 Google 계정/스토어는 사용하지 않았다. iOS 설정 필드 잠금 변경을 simulator build로 확인한다.
- Android sample 수정 후 emulator의 sandbox 빈 설정 UI 통과, local-mock 로그인/재시작/restore/logout 재통과. iOS 설정 필드 잠금 변경도 simulator build 성공. 직접 기동한 Backend와 전용 AVD만 종료하고 데이터·volume은 보존했다.
- 커밋 전: Google Sandbox sample 및 iOS 설정 표시 일치만 포함한다. 실제 Google/Apple 계정·스토어, Unity player 연결 및 전체 UI audit은 미완료다.

### [P03-T03/P03-T04] Unity Native bridge 재개
- Task 시작: 현재 bridge wire 계약과 Native LOCAL_MOCK 호출 경계를 확인하고 가능한 실제 연결부터 구현한다. Unity Editor 및 실 플랫폼 검증은 기존 환경·인증 대기를 유지한다.
- 작업 디렉터리를 잘못 지정해 수정 스크립트가 FileNotFoundError로 실패했다. 이어 실행된 기존 테스트는 변경 검증이 아니며, 저장소 루트에서 수정 후 다시 실행한다.
- Android bridge dispatcher에 검증된 요청만 받는 provider 연결점, 배열 결과 및 정제된 SDK 오류 전달을 추가했다. 실제 handler는 아직 연결 전이며 단위 검증을 시작한다.
- 검증: `android/gradlew -p android :sdk-core:test --tests com.gamebridge.BridgeDispatcherTest` 종료 0. 배열 결과, 요청 상관관계, 오류 재시도 표시, 잘못된 요청 미전달 및 예외 메시지 비노출 확인. 실제 provider 연결과 Unity 실행은 아직 미검증이다.
- 커밋 전: Android bridge handler 경계와 해당 단위 시험만 포함하며 P03-T03은 PARTIAL로 유지한다.
- 다음 하위 작업 시작: Android JNI에서 로컬 mock client를 실제 Backend에 연결한다. 인증 정보는 Native 저장소에 남기고, 개발키는 명시적 LOCAL_MOCK 설정으로만 전달한다. 실제 Google 및 iOS 연결은 이 작업의 검증으로 간주하지 않는다.
- 사용자 요청으로 안전한 지점에서 일시 중단. 직전 로컬 커밋 0b3502b는 Android bridge의 검증된 handler 경계와 단위 시험만 포함한다. 다음 LOCAL_MOCK handler 및 Unity 설정 전달은 코드 착수 전이며, 기존 BridgeFacade에는 handler가 아직 연결되지 않아 Unity Native 초기화는 여전히 미지원이다.
- 재개 시 AGENTS.md, START_HERE.md, DEVELOPMENT_PLAN.md, 진행 원장과 git 상태를 다시 확인한다. 미추적 unity/Demo 및 scripts/__pycache__와 기존 artifacts/DB 데이터는 보존한다. 실제 플랫폼 인증·StoreKit 환경 대기와 P09~P11 미완료 상태는 그대로다. 자동 push/배포는 하지 않았다.
- 커밋 전: 일시 중단 및 재개 지점 기록만 포함한다.

### [P03-T03] Android LOCAL_MOCK 연결 재개
- Task 시작: 중단 기록과 Git 상태를 확인했다. 검증된 JNI dispatcher에 실제 Native LOCAL_MOCK client를 연결하고, 명시적인 개발 전용 설정을 통해 인증·상품·구매·잔액 경로를 구성한다. 기존 미추적 파일은 보존한다.
- Android LOCAL_MOCK handler 초안은 Native 보안 저장소와 Backend client를 연결하며 사용자·상품·구매·잔액만 반환한다. Unity 설정은 명시적인 개발키와 Mock 계정을 Native에 전달한다. 구매 sync·push·config bridge와 실제 Provider는 아직 미연결이다. Kotlin 컴파일 및 계약을 검증한다.
- `android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 1: 현재 셸에 Android SDK 경로가 없어 Gradle이 SDK location not found로 중단했다. 기존 설치 경로를 확인해 명시적으로 재실행한다. 코드 컴파일 성공으로 기록하지 않는다.
- Android SDK 경로 지정 후 빌드 종료 1: capability reason의 Kotlin 분기에서 String과 JsonNull이 Any로 추론되어 컴파일 오류가 발생했다. JSON 문자열로 명시 변환해 재검증한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 0: 기존 Kotlin 단위 테스트와 Android bridge AAR compile 통과. 새 연결 자체의 HTTP 경로·Unity C# compile은 아직 확인하지 않았다.
- 새 bridge HTTP 시험 첫 컴파일 종료 1: JDK HttpServer 응답 길이에 Int를 전달했다. Long으로 변환 후 재실행한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-core:test --tests com.gamebridge.LocalMockBridgeHandlerTest` 종료 0: synthetic HTTP의 개발 인증→구매 검증→서버 잔액→로그아웃, 자격정보 비노출, 다른 bridge session 차단을 확인했다. 실제 Backend/Unity JNI/Google 검증은 아니다. C# 조건부 컴파일을 실행한다.
- `UNITY_EDITOR_PATH=... bash scripts/check-csharp-compile.sh` 종료 0: Android/iOS/Editor/미지원 조건부 C# 각 compile, 경고·오류 0. Unity Editor 실행, JNI 또는 IL2CPP 검증은 아니다.
- 실제 격리 local-mock Backend와 PostgreSQL을 통한 bridge 인증·구매·잔액·복원 시험을 추가한다. test subject B에 로컬 Mock 지급 1건만 기록하며 실제 스토어 호출은 없다.
- 전용 local-mock Backend/PostgreSQL에서 `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... :sdk-core:test --tests com.gamebridge.LocalMockIntegrationTest.bridge…` 종료 0: bridge→Native→실제 로컬 HTTP/DB Mock 로그인·구매·서버 코인 100 증가·세션 복원·로그아웃을 확인했다. 실제 Play/Unity JNI는 실행하지 않았다. 이 시험은 test subject B에 Mock 구매 1건을 남긴다.
- 설정 생성자의 기존 4인자 바이너리 서명을 보존하고 개발 전용 6인자 overload를 추가했다. 사용자 설정과 JNI 미검증 범위를 문서화했다. 직접 기동한 Backend만 종료했으며 DB와 volume은 보존했다. 변경 후 C# 컴파일과 원장 검사를 다시 실행한다.
- 생성자 호환성 수정 후 `scripts/check-csharp-compile.sh` 종료 0: 네 가지 조건부 compile 모두 경고·오류 0. 코드 검토 중 Unity Dispose가 명시적 shutdown 없이 호출되면 Native dispatcher의 이전 session이 남는 문제를 발견해 재생성 경계를 보강한다.
- dispose 시 callback 세대가 바뀌면 대기 중 이전 요청은 실행하지 않고, Native handler 메모리 상태를 executor에서 정리하도록 했다. 큐가 가득 찬 경우 다음 유효 요청 전에 정리한다. 저장된 세션은 복원 가능하도록 삭제하지 않는다. 회귀 컴파일·단위 시험을 진행한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 0: Native 단위 시험과 bridge AAR compile 통과. synthetic HTTP에서 reset 후 새 bridge session 초기화도 확인했으나 Unity lifecycle 실행은 미검증이다.
- 커밋 전: Android LOCAL_MOCK bridge와 개발 전용 설정, 단위/로컬 DB 검증 및 사용자 안내만 포함한다. 실제 Google/Apple, iOS bridge, Unity JNI, push/config/sync는 미완료다.

### [P03-T04] iOS LOCAL_MOCK C ABI 연결
- Task 시작: Swift C ABI 기존 수명주기와 Native actor·Keychain 저장소를 확인하고 명시적인 LOCAL_MOCK 요청을 연결한다. 실제 Apple Provider 및 Unity iOS 실행과는 구분한다.
- Swift LOCAL_MOCK bridge handler 초안을 작성했다. Native actor와 분리된 Keychain 저장소 주입을 사용하며 인증·상품·구매·잔액을 반환한다. C ABI 연결 전 compile 확인을 진행한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 1: capability reason의 삼항식에서 NSNull/String 타입 추론이 실패했다. 명시적 Any 분기로 변경 후 재검증한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0: 기존 C ABI 한글 callback 1건 및 새 handler compile 통과. 아직 handler를 C ABI에 연결한 검증은 아니다.
- Swift C ABI에 LOCAL_MOCK handler와 session 소유권·종료 정리를 연결했다. 비동기 Native 요청은 전용 직렬 queue에서 순서를 유지하며 Unity main thread를 기다리지 않는다. Swift C ABI 및 simulator build를 검증한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0: 변경 후 기존 C ABI callback 1건 통과. 신규 초기화·소유 session 경계와 로컬 Backend 경로는 별도 확인한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0, 2건: C ABI UTF-8 복사/상관관계와 Mock 초기화·다른 session 거부·종료를 확인했다. Keychain 로그인·실제 Unity linkage는 이 시험에 포함되지 않는다.
- Swift handler를 격리된 로컬 Backend/DB에 연결하는 opt-in 시험을 추가한다. subject B의 Mock 구매 1건이며 실제 스토어 호출은 없다.
- `GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST=true ... swift test --package-path ios --filter LocalMockIntegrationTests.testBridgeHandlerAgainstLocalBackend` 종료 0, 1건: Swift handler→실제 local-mock HTTP/DB 로그인·구매·코인 100 증가·복원·로그아웃. test subject B의 Mock 구매 1건을 기록했다. C ABI와 Keychain을 경유한 실행은 아니다.
- `xcodebuild ... -scheme GameBridgeNative ... build -quiet` 종료 65: 기존 생성된 Xcode project가 새 Swift 파일을 포함하지 않아 LocalMockBridgeHandler를 찾지 못했다. project 생성 스크립트의 기존 파일 보호 정책을 확인한다.
- 별도 임시 Xcode project 생성 시도는 패키지 상대 경로가 artifacts/Package.swift를 가리켜 종료 74 (의존성 해석 실패). 기존 project를 덮어쓰지 않도록 독립 디렉터리에 원본 구조를 symlink로 재현해 다시 생성한다.
- 격리 Xcode project 생성이 UITests 경로 누락으로 실패했다(후속 xcodebuild도 project 없음). 누락된 테스트 경로를 포함해 마지막으로 재시도한다.
- 격리된 `artifacts/ios-bridge-layout.VrB66L`에서 XcodeGen 재생성 및 `xcodebuild ... -scheme GameBridgeNative -destination generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. 무서명 simulator static framework 컴파일이며 Unity linkage/실기기 실행은 아니다. 생성된 기존 Xcode project는 덮어쓰지 않았다.
- `swift test --package-path ios` 종료 0: 총 44건, 4건은 opt-in local Backend 시험으로 skip, 나머지 실패 0. 앞서 별도 실행한 handler opt-in 1건은 성공했지만 skip된 나머지 3건을 이번 전체 실행의 통과로 간주하지 않는다.
- 커밋 전: Swift LOCAL_MOCK handler·C ABI 연결과 별도 단위/로컬 Backend 증거만 포함한다. Unity 실행과 실제 Apple·구매 sync·push·config는 미완료로 남긴다. 직접 기동한 Backend만 종료하고 기존 DB와 artifacts를 보존했다.

### [P07-T01] LOCAL_MOCK config bridge
- Task 시작: Android/iOS가 이미 보유한 점검 설정 fetch·TTL cache 경로를 Unity config.get에 연결한다. 설정 부재는 CONFIG_REQUIRED로 반환하며 만료 캐시로 신규 구매를 허용하지 않는다.
- 양쪽 Native Mock client의 기존 유효기간 cache를 config.get에 연결했다. source는 공개 계약의 NETWORK/CACHE를 사용하며 설정·cache 부재는 CONFIG_REQUIRED다. 컴파일 및 차단·cache 검증을 진행한다.
- Android `:sdk-core:test --tests LocalMockBridgeHandlerTest :sdk-unity-bridge:assembleDebug` 종료 0: 설정 부재 CONFIG_REQUIRED, 정상 NETWORK, 일시 실패시 유효 CACHE 및 기존 Mock 구매를 synthetic HTTP로 확인했다. 실제 Unity JNI는 아니다. Swift 동일 경계를 확인한다.
- `swift test --package-path ios --filter LocalMockMaintenanceTests` 종료 0, 2건: synthetic URLProtocol에서 config 없음·NETWORK·유효 CACHE 및 점검 중 구매 차단/로그아웃을 확인했다. 실제 Unity/iOS 실행은 미검증이다.
- 커밋 전: LOCAL_MOCK config bridge와 양 플랫폼 synthetic 시험만 포함한다. 실 Provider config bridge, 구매 sync와 push는 계속 미완료다.

### [P04-T05] Unity 실제 인증 연결
- Task 시작: 기존 Native Google/Apple 인증 facade를 Unity bridge에 연결할 수 있도록 host·구성·세션 수명주기와 공개 결과 계약을 조사한다. 실제 계정 인증은 사용자 설정 전까지 WAITING_USER로 유지한다.
- Android에서 공개 GoogleAuthProvider를 실제 Credential Manager 경로로 조립하고 Unity에는 provider·사용자만 반환하도록 bridge를 작성한다. 개발키는 sandbox에 전달하지 않으며 Google OAuth server client ID는 공개 식별자 설정이다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-unity-bridge:assembleDebug` 종료 0: Google 인증 bridge가 컴파일됐다. Google 계정·Credential Manager UI·Unity JNI는 실행하지 않았고 fake provider 경계를 별도 검증한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-unity-bridge:testDebugUnitTest` 종료 0: fake Google provider로 sandbox mode 분기, Mock fallback 차단, 사용자 결과 및 미연결 상점 오류, 종료 cleanup을 확인했다. 실제 Google UI/계정 시험이 아니다. C# 소비 설정을 컴파일한다.
- `UNITY_EDITOR_PATH=... bash scripts/check-csharp-compile.sh` 종료 0: 네 플랫폼 조건부 C# compile 경고·오류 0. 실제 Unity Editor와 Android JNI 실행은 아니다.
- 커밋 전: Android Google 인증 bridge와 fake mode 격리 시험만 포함. Apple 인증 bridge·스토어/푸시 및 실제 Google 계정 검증은 미완료이며 WAITING_USER를 유지한다.
- 다음 하위 작업 시작: iOS AppleAuthProvider의 presentation anchor와 main-actor 수명주기를 확인하고 C ABI sandbox 인증을 연결한다. 실제 계정 시험은 수행하지 않는다.
- Swift bridge에 AppleAuthProvider 실제 경로와 foreground key window 전달을 연결했다. 개발키가 포함된 sandbox 요청과 다른 provider 요청을 거부하며 mock fallback을 두지 않는다. Swift 컴파일과 fake 인증 경계, iOS simulator static build를 확인한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0, 2건: 기존 Mock C ABI 동작 회귀 통과. 새 Apple handler의 fake 테스트와 iOS 전용 UIKit 빌드는 아직 별도다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 0, 1건: fake Apple provider로 sandbox mode·Mock 거부·미연결 상점 오류·정리 확인. 실제 iOS 인증 UI는 아니다. UIKit 포함 simulator static framework를 독립 생성 프로젝트에서 확인한다.
- 격리 프로젝트 `artifacts/ios-apple-bridge.JMOwJF`에서 UIKit·AuthenticationServices 포함 `GameBridgeNative` simulator static framework 무서명 build 종료 0. 실행·Apple 계정·Unity linkage는 확인하지 않았다.
- 커밋 전: iOS Apple 인증 C ABI 연결과 fake 시험·컴파일만 포함한다. 실제 Apple 계정과 Unity 실동작은 WAITING_USER이며 상점/푸시는 미연결이다.

### [P05-T07] Unity 실제 상점 bridge
- Task 시작: 이미 구현된 Native Google Play/StoreKit facade의 상품 매핑, 결과, 복구, 비동기 이벤트와 구매 상태 계약을 확인한다. 실제 결제는 사용자 설정 전까지 실행하지 않는다.
- Native 상점 조사 결과 Google Play는 구매 UI 후 결과를 별도 event flow로 제공하지만 현재 Unity RequestRegistry는 event를 모두 무시한다. 결제 결과를 성공으로 조작하지 않도록 상점 연결의 선행 작업으로 Unity event 수신 경계를 구현한다.

### [P03-T05] Unity 구매 이벤트 수신
- Task 시작: 현재 session의 유효한 PurchaseUpdated 이벤트만 검증·전달하고 응답 Task 완료와 분리한다. Native 실제 이벤트 발행 연결은 별도다.
- Unity RequestRegistry에 현재 session의 PurchaseUpdated 이벤트를 추가했다. 이벤트 ID·시각·상품·상태·서버 구매 ID·오류를 검증하고 허용 필드만 공개하며, 구매 응답 Task와 별도 경로다. Native 발행은 아직 연결 전이다. C# compile 및 수신 경계를 확인한다.
- `scripts/check-csharp-compile.sh` 종료 0: 네 조건부 compile 성공. 이벤트에 숫자형 enum 문자열을 허용하지 않도록 엄격 검사를 추가하고 현재 session·검증된 구매 ID·민감정보 필터 경계를 smoke로 확인한다.
- `UNITY_EDITOR_PATH=... bash scripts/smoke-csharp-registry.sh` 종료 0: 현재 session의 서버 구매 ID가 있는 이벤트 수신, 다른 session·미확인 구매·숫자 enum 거부를 확인했다. Unity runtime과 Native 이벤트 발행은 미검증이다.
- 커밋 전: Unity 구매 이벤트 수신·sanitized model과 독립 .NET smoke만 포함한다. Native 발행 및 실제 상점 연결은 다음 작업이다.

### [P05-T07] Android Google Play bridge
- Task 시작: 기존 GooglePlayStore를 Unity sandbox에 연결한다. UI 결과는 서버 지급 전 PENDING 또는 VERIFICATION_PENDING으로 반환하고, 검증 후 Native 이벤트만 PURCHASED로 전달한다. 실 스토어 거래는 실행하지 않는다.
- 사용자 요청으로 일시 중단한다. P05-T07 Android Google Play bridge는 Native facade와 비동기 구매/event 계약을 조사했으며 코드 변경은 시작하지 않았다. 재개 시 상품 ID 설정 전달, 서버 검증 전 PENDING/VERIFICATION_PENDING 반환, 검증 후 PurchaseUpdated 발행과 session/lifecycle 격리를 구현·검증한다. 이어 iOS 상점·푸시 및 P08~P11을 진행한다.
- 이 세션의 Android/iOS Mock bridge, Android Google/iOS Apple 인증 bridge, Unity 구매 이벤트 수신은 로컬 커밋됐다. Mock 및 fake 시험은 실제 계정·결제·Unity JNI/IL2CPP 성공이 아니다. ENV-002와 StoreKit 실패, USER_SETUP의 외부 인증 대기는 유지한다. 새 생성 검증 artifacts와 기존 미추적 unity/Demo·scripts/__pycache__ 및 DB 데이터는 보존한다. 자동 push/배포는 하지 않았다.
- 커밋 전: 일시 중단 및 재개 지점 문서만 포함한다.
- 재개: Git 상태 및 계획의 결제 불변식을 확인했다. 기존 미추적 파일을 보존하며 실제 Play 거래 없이 상품 설정·구매 대기·검증 이벤트 경로를 구현한다.
- Unity 설정에 실제 두 store 상품 ID를 명시적으로 전달하고 Android handler에 상품·구매·잔액 경계를 추가했다. 구매 즉시 결과는 PENDING/VERIFICATION_PENDING만 허용하고 지급 전 상태로 반환한다. 실제 provider 및 지연 이벤트 연결을 진행한다.
- GooglePlayStore 실제 facade를 지연 생성하고 검증 결과 flow를 Unity PurchaseUpdated로 전달하도록 연결했다. callback 세대·SDK session·로그인 변경 epoch를 묶어 이전 계정/종료 후 이벤트를 거부하며, 원본 영수증은 직렬화하지 않는다. 컴파일과 fake 경계 시험을 진행한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug` 종료 0. 기존 인증 단위 시험과 AAR compile이 통과했으며 새 구매 결과·이벤트 격리 검증은 아직 추가 중이다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-unity-bridge:testDebugUnitTest` 종료 0: fake Play 결과가 VERIFICATION_PENDING/NOT_GRANTED로 전달되고 잘못된 상품 mapping은 provider 생성 전에 차단됨을 확인했다. 검증 ID 없는 구매 이벤트 및 로그아웃 이후 이전 이벤트도 차단했다. 실제 Play·Unity JNI는 아니다.
- `scripts/check-csharp-compile.sh` 및 `scripts/smoke-csharp-registry.sh` 종료 0: 네 조건부 C# compile과 독립 registry smoke 통과. 실제 Unity Editor/JNI 및 Google Play는 검증하지 않았다.
- 커밋 전: Android Play 상품 조회·대기 구매·서버 잔액·검증 이벤트 연결과 fake 시험만 포함한다. 실제 Play/Unity JNI 및 구매 sync/recovery, iOS 상점은 미완료로 유지한다.

### [P05-T07] iOS StoreKit bridge
- Task 시작: Native AppleStore의 사용자 인증·상품 ID·지급 후 finish 경로를 C ABI에 연결한다. 명시적 사용자 복원과 앱 복귀 복구를 구분하며 실제 Apple 거래는 실행하지 않는다.
- StoreKit 거래 수신 이후 서버 검증의 일시 오류를 VERIFICATION_PENDING으로 구분하고, 실제 서버 GRANTED/ALREADY_GRANTED 상태를 Native 결과에 보존하도록 보완했다. 검증 실패·계정 불일치는 계속 오류이며 미검증 거래는 finish하지 않는다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 2건: 기존 server grant 결합과 검증 동시성 시험 통과. 새 검증 대기 분기 자체 및 실제 StoreKit 거래는 이 시험에 포함되지 않는다.
- iOS AppleStore를 sandbox C ABI에 지연 연결하고 두 상품 mapping, 서버 확인된 지급 상태·finish 결과, pending/cancelled를 구분하는 handler 초안을 작성했다. 복구 수치 및 지연 이벤트는 아직 연결하지 않았다. Swift fake 및 simulator compile을 확인한다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 0, 1건으로 기존 인증 경계 회귀 통과. 새 상점 결과의 지급 상태 분기와 서버 응답 상태 전달을 추가 시험한다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 1: fake provider가 상품 mapping 없이 구매 결과를 반환해 기존 미설정 차단 시험이 실패했다. handler 자체에서 store 호출 전 mapping을 강제하고 재시험한다. 뒤이은 sink 시험은 실행되지 않았다.
- 재시험 `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 0, 2건: 미설정 차단, 검증 전 미지급, 서버 ALREADY_GRANTED 보존, 구매 ID 없는 가짜 완료 거부. `--filter AppleAuthProviderTests.testAppleProofSinkRequiresDurableServerGrant` 종료 0, 1건: 서버 ALREADY_GRANTED가 Native에 보존된다. 모두 fake 시험이며 StoreKit UI는 아니다.
- `xcodebuild -project artifacts/ios-apple-bridge.JMOwJF/... -scheme GameBridgeNative -destination generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. StoreKit·UIKit 포함 무서명 컴파일이며 실제 거래·Unity 실행은 아니다. 이제 verified transaction update의 지연 이벤트를 연결한다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 2건: 기존 검증 불변식·동시성 회귀 통과. StoreKit update 후 verified grant callback 경계가 추가됐으나 실제 transaction listener는 아직 실행하지 않았다.
- StoreKit listener/미완료 복구에서 서버 검증과 finish를 마친 grant만 Native 업데이트 callback으로 내보내고, C ABI에서 callback 세대·SDK session·계정 epoch를 확인한다. 원본 transaction/JWS는 이벤트에 넣지 않는다. 컴파일과 fake 경계를 확인한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0, 2건 및 `--filter AppleAuthBridgeTests` 종료 0, 2건. macOS Swift 시험은 UIKit 분기나 실제 StoreKit update를 실행하지 않는다. simulator framework compile을 재실행한다.
- `xcodebuild -project artifacts/ios-apple-bridge.JMOwJF/... -scheme GameBridgeNative -destination generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0: UIKit/StoreKit 이벤트 분기 포함 컴파일. 실제 listener·기기·Unity 동작은 미실행이다. 전체 Swift 회귀를 실행한다.
- `swift test --package-path ios` 종료 0: 총 47건 중 4건 opt-in local Backend skip, 나머지 실패 0. 이 결과는 실제 StoreKit 거래 또는 UIKit 이벤트 실행을 뜻하지 않는다.
- 커밋 전: iOS sandbox 상점의 상품·구매·잔액 및 검증된 지연 이벤트 코드와 fake/compile 증거만 포함한다. 실제 StoreKit 거래·listener·Unity와 사용자 복원/sync bridge는 미완료다.

### [P05-T06] LOCAL_MOCK 구매 복구
- Task 시작: 로컬 Mock의 거래는 서버에서 즉시 지급하고 별도 스토어 완료 처리가 없으므로 sync에서 서버 entitlement를 재조회한다. 실제 스토어의 비동기 복구 건수는 확인 전 임의로 성공 집계하지 않는다.
- 정정: 앞선 “별도 스토어 완료 처리가 없다”는 기록은 부정확하다. MockPurchaseController는 서버 MOCK finalization job을 생성하고 worker가 별도 완료한다. 또한 현재 Native Mock client는 구매 요청의 transaction/attempt를 재시작용으로 저장하지 않아 응답 유실 뒤 복구 건수를 알 수 없다. entitlement 재조회만으로 sync 성공·0건이라고 표시하지 않고, 이 누락을 남긴 채 독립적인 실제 상점 복구 경로를 조사한다.
- Mock 재시작 pending 단서 누락은 BUG-009 OPEN으로 원장에 등록했다. Android Play는 기존 queryPurchases 결과를 단일 검증 경계에서 처리하고 실제 결과를 집계할 수 있으므로 독립적으로 개발한다.
- Google Play recovery가 조회한 거래를 기존 callback worker와 공유하는 검증 semaphore에서 처리하고 실제 PURCHASED/PENDING/FAILED 결과를 집계하도록 작성했다. 1건 동시 검증 기본값과 계정 전환 차단을 유지한다. Fake gateway 회귀를 확인한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-android:testDebugUnitTest --tests com.gamebridge.android.purchase.GooglePlayBillingProviderTest` 종료 0: 기존 Play fake 검증 불변식과 기본 동시 1건 회귀 통과. 새 recovery 집계와 worker 동시성은 추가로 검증한다.
- 동일 GooglePlayBillingProviderTest 재실행 종료 0: fake 거래 4건의 verified 1·pending/일시 장애 2·실패 1 집계, callback 처리와 recovery가 검증 동시 1건을 공유하는 것을 확인했다. 실제 Google Play 조회/consume은 실행하지 않았다.
- 커밋 전: Android Native recovery 결과 집계와 fake 검증만 포함한다. Unity sync 연결은 다음 하위 작업이며, recovery 요청 중복의 완전한 single-flight와 BUG-009는 미완료다.

### [P05-T07] Android Unity 구매 복구
- Task 시작: Google Play 실제 recovery 검증 결과와 서버 entitlement를 Unity store.sync 응답으로 전달한다. APP_RESUME과 USER_RESTORE만 받으며 실제 Play 검증은 사용자 설정 대기다.
- Android sandbox bridge에 실제 회복 건수와 서버 잔액을 반환하는 store.sync 경로를 추가하고, 허용되지 않은 복구 사유는 차단한다. fake provider 및 AAR compile 검증을 실행한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug` 종료 0: fake 회복 건수·서버 잔액 전달, 잘못된 사유 거부 및 AAR compile 확인. 실제 Play/Unity JNI는 미실행이다.
- 커밋 전: Android Unity sync bridge 및 fake 시험만 포함한다. 반복 복구의 완전한 single-flight, iOS sync, Mock BUG-009 및 실제 플랫폼 검증은 미완료다.

### [P05-T06] iOS 구매 복구 집계
- Task 시작: StoreKit 미완료 거래와 사용자 명시 복원의 검증 결과를 구분하여 집계한다. 앱 복귀 시 AppStore.sync 인증 UI를 호출하지 않고, 검증되지 않은 거래를 완료로 세지 않는다.
- iOS 회복에서 고유 transaction별 서버 검증·finish 성공/일시 대기/영구 실패를 집계하고 중복 transaction은 한 번만 센다. 사용자 복원에만 AppStore.sync를 호출하며 중첩 복구는 BUSY로 거부한다. Swift 컴파일과 fake 범위를 확인한다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 2건: 기존 grant 결합과 검증 동시성 시험 통과. 새 집계 분류는 StoreKit transaction이 없는 환경에서 별도 순수 경계 시험을 추가한다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 3건: 순수 집계에서 transaction 중복 제거, 서버 완료·네트워크 대기·계정 불일치 실패 분리와 취소 전파를 확인했다. StoreKit transaction sequence 자체는 미실행이다.
- `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. 무서명 static simulator compile이며 실제 사용자 복원·StoreKit sequence 실행은 아니다.
- 커밋 전: iOS Native recovery 집계와 순수 fake 경계만 포함한다. Unity sync bridge와 실제 StoreKit 복원, BUG-009는 미완료다.

### [P05-T07] iOS Unity 구매 복구
- Task 시작: StoreKit의 실제 회복 집계와 서버 entitlement를 Unity에 전달한다. USER_RESTORE에만 AppStore.sync를 호출하는 기존 Native 경계를 유지한다.
- iOS bridge에 회복 결과·서버 잔액과 APP_RESUME/USER_RESTORE 명시 분기를 연결했다. fake provider로 요청 분기와 결과 계약을 확인한다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 0, 2건: fake에서 APP_RESUME은 false, USER_RESTORE는 true로 전달되고 회복 집계·잔액이 반환되며 잘못된 사유가 거부됐다. 실제 AppStore.sync는 호출하지 않았다.
- `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0: iOS sync bridge를 포함한 무서명 simulator compile. 실제 StoreKit 복원 및 Unity iOS는 미검증이다.
- 커밋 전: iOS sync bridge와 fake 요청 분기만 포함하며 실제 StoreKit local 실패·Apple 계정·Unity 검증 및 BUG-009는 미완료다.

### [P05-T06] BUG-009 Android Mock 응답 유실 복구
- Task 시작: Mock 구매 transaction/attempt 단서를 별도 Native 암호화 저장소에 기록하고 서버 확인 전에는 보존한다. 재시작 후 같은 사용자·설정의 요청만 동일 transaction/멱등키로 재검증한다. 다른 사용자의 보류 데이터는 삭제하지 않는다.
- Android Mock client에 별도 TokenStore 기반 pending transaction/attempt 기록과 동일 사용자·Backend 범위 재검증 경로를 작성했다. 서버 지급 응답을 검증하고 확인 후에만 해당 단서를 제거하며, 미설정 기존 소비자에서는 recovery를 가장하지 않는다. 기존 Mock sample·Unity는 별도 Keystore namespace를 사용한다. 컴파일과 장애/재시작 시험을 진행한다.
- Android 전체 compile 첫 시도 종료 1: LocalMockBridgeHandler에 두 번째 함수형 인자를 추가하면서 기존 trailing lambda 호출이 마지막 인자에 바인딩됐다. 기존 단일 생성자 overload를 보존하도록 수정한다.
- 생성자 수정 후 Android 전체 테스트 종료 1: 기존 synthetic bridge 구매 fixture의 serverPurchaseId가 UUID가 아니어서 새 응답 검증을 통과하지 못했다. fixture와 실제 실패 위치를 확인한다. 전체 suite PASS로 기록하지 않는다.
- 확인: 실패 fixture의 `serverPurchaseId=purchase-1`은 계약상 UUID가 아니었다. 테스트 값을 유효한 고정 UUID로 교체하고 응답 유실·재시작·사용자 전환 복구를 별도 시험한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-core:test :sdk-unity-bridge:assembleDebug :sample-app:assembleDebug` 종료 0: synthetic 응답 유실→다른 사용자 차단→원래 사용자 재시작 복구에서 같은 proof/멱등키 재사용 및 확인 후 pending 삭제를 확인했다. 실제 DB commit 후 응답 유실과 기기 Keystore는 이 시험에 포함되지 않는다.
- Android Unity Mock store.sync와 Native sample 복원에 pending 재검증 및 서버 잔액 조회를 연결했다. 실제 복구 건수만 표시하며 기존 session 저장소와 거래 단서 저장소는 분리했다.
- `ANDROID_HOME=$HOME/Library/Android/sdk android/gradlew -p android :sdk-core:test :sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug :sample-app:assembleDebug` 종료 0: Android core/bridge fake 시험 및 AAR/sample APK compile 통과. 실제 Unity JNI와 기기 Keystore 복구 시험은 미실행이다.
- 같은 TokenStore 인스턴스를 session과 pending에 동시에 전달하면 서로 덮어쓸 수 있어 초기화 시 거부하도록 보강하고 회귀를 실행한다.
- `:sdk-core:test --tests com.gamebridge.LocalMockRecoveryTest` 종료 0: 동일 session/pending 저장소 인스턴스 차단과 synthetic 응답 유실 복구 재검증. BUG-009는 iOS 및 실제 DB 응답 유실/기기 복구 검증이 남아 OPEN이다.
- 커밋 전: Android Mock pending 보존·recovery 및 sample/Unity 연결만 포함한다. 실결제·Unity JNI·iOS 복구는 미검증 또는 미완료다.

### [P05-T06] BUG-009 iOS Mock 응답 유실 복구
- Task 시작: Swift LOCAL_MOCK의 구매 단서를 별도 Keychain 저장소에 보존하고, 재시작 후 같은 사용자·Backend에서 동일 transaction/멱등키로 확인한다. 다른 사용자의 보류 기록은 보존한다.
- Swift Mock client에 별도 pending 저장소, 사용자·서버 범위 확인, 검증 후 삭제 및 actor 재진입 중 구매/복구 동시성 차단을 작성했다. 기존 세션 저장소와 같은 인스턴스는 거부한다. Swift 컴파일과 synthetic 재시작 시험을 진행한다.
- `swift test --package-path ios --filter LocalMockMaintenanceTests` 종료 0, 2건: 기존 점검 차단 및 cache 시험 통과. 새 응답 유실 복구는 별도 synthetic 시험 전이다.
- 새 Swift recovery 시험 첫 컴파일 종료 1: multiline 문자열 시작 뒤 공백으로 Swift 구문 오류가 발생했다. 공백을 제거해 재실행한다.
- Swift recovery synthetic 시험은 사용자 B가 A의 pending을 처리하는 것처럼 보여 실패했다. URLProtocol의 auth 요청 body가 비어 테스트 서버가 기본 A로 응답한 가능성을 확인 중이며, 사용자 분리 성공으로 기록하지 않는다.
- Swift fake 인증 서버가 요청 body를 읽지 못하면 A로 기본 처리하던 문제를 수정하고 명시적으로 B user ID를 검증했다. `swift test --package-path ios --filter LocalMockRecoveryTests` 종료 0, 1건: 다른 user는 보류 단서를 처리하지 않고 원래 user 재시작 시 복구했다. HTTP body의 proof 캡처가 실제인지 추가 확인한다.
- proof 캡처 nonempty 검증을 추가하자 Swift URLProtocol synthetic 시험이 실패했다. 기존 proof 비교는 빈 문자열 간 비교였으므로 증거로 취급하지 않는다. request body stream도 읽어 실제 증빙이 캡처되는지 확인한다.
- URLProtocol의 HTTP body stream을 읽도록 수정한 뒤 `swift test --package-path ios --filter LocalMockRecoveryTests` 종료 0, 1건: nonempty proof·멱등키가 재시도에서 동일하고, 다른 user의 pending은 보존되며 확인 후에만 삭제됨을 synthetic 시험으로 확인했다. 실제 DB commit 유실/Keychain 재시작은 아직 미검증이다.
- iOS Unity Mock bridge에 별도 Keychain pending 저장소와 store.sync를 연결하고 Native sample 복원에서도 recovery 및 서버 잔액을 조회하도록 변경했다. 전체 Swift 시험과 simulator build를 확인한다.
- `swift test --package-path ios` 종료 0: 총 49건 중 opt-in local Backend 4건 skip, 나머지 실패 0. Swift package 시험은 실제 iOS Keychain·Unity 또는 StoreKit 거래가 아니다. Native framework와 sample의 simulator compile을 확인한다.
- `xcodebuild ... GameBridgeNative` 및 `GameBridgeSample` generic iOS Simulator 무서명 build 종료 0. 실제 Keychain 복구와 Unity iOS 실행은 확인하지 않았다. 두 플랫폼의 실제 local PostgreSQL에서 지급 commit 뒤 응답 유실을 모사하고 동일 거래가 재지급되지 않는지 확인한다.
- Android opt-in `LocalMockIntegrationTest.persisted mock transaction recovers after committed response is lost` 종료 0: 격리 PostgreSQL에서 지급 commit의 응답을 버린 뒤 별도 client가 저장된 동일 transaction/멱등키로 복구했고 코인 증가는 100 한 번뿐이었다. 테스트 전용 Mock user B에 지급 1건을 남겼다. 기기 Keystore 시험은 아니다.
- Swift opt-in `LocalMockIntegrationTests.testPersistedMockTransactionRecoversAfterCommittedResponseIsLost` 종료 0, 1건: 격리 PostgreSQL 지급 commit 뒤 응답을 버리고 새 client에서 같은 단서로 복구해 코인이 100 한 번만 증가했다. 테스트 전용 Mock user B에 지급 1건을 남겼으며 실제 iOS Keychain/Unity 실행은 아니다.
- Swift Mock bridge의 store.sync가 실제 pending 저장소와 서버 잔액을 사용하는지 synthetic URLProtocol 경계를 추가 확인한다.
- `swift test --package-path ios --filter LocalMockMaintenanceTests` 종료 0, 3건: Mock sync의 실제 빈 pending 집계·서버 wallet 및 잘못된 reason 거부를 synthetic 시험으로 확인했다.
- 커밋 전: iOS Mock Keychain pending·recovery·sample/bridge 및 양 플랫폼 격리 DB 응답 유실 시험만 포함한다. Android/iOS 실제 기기 보안 저장소 및 Unity player 복구가 남아 BUG-009는 OPEN 유지한다. 직접 기동한 Backend만 종료하고 DB·volume은 보존했다.

### [P05-T06] Android 기기 Mock 복구 확인
- Task 시작: 기존 전용 AVD와 테스트 전용 임의 Keystore namespace만 사용해 저장소 재생성 및 격리 local DB의 응답 유실 복구를 확인한다. 사용자 AVD·기존 저장소·DB volume은 삭제하지 않는다.
- 전용 AVD에서 임의 test namespace 2개를 사용하여 Android Keystore 재생성 후 local DB의 동일 transaction 복구·중복 지급 방지 instrumented test를 추가했다. 이 테스트는 격리 Mock user B에 지급 1건을 남기며 기존 namespace는 건드리지 않는다.
- `:sample-app:assembleDebug :sample-app:assembleDebugAndroidTest` 종료 0. 전용 AVD(포트 5566)와 격리 local Backend를 기동해 instrumented test 준비 중이며, 기존 데이터는 지우지 않는다.
- 전용 Android 36 emulator에서 테스트 APK 설치 후 `am instrument ...KeystoreNamespaceTest#pendingPurchaseSurvivesNewKeystoreInstancesAndDoesNotDoubleGrant` 종료 0, 1건: 별도 Keystore 인스턴스 재생성→격리 local DB 동일 거래 복구→코인 100 한 번 증가·pending 삭제를 확인했다. Mock user B에 테스트 지급 1건을 남겼다. 프로세스 강제 종료나 Unity JNI는 이 시험 범위가 아니다.

### [P05-T06] iOS simulator Mock 복구 확인
- Task 시작: 전용 iOS simulator와 무작위 test Keychain service만 사용해 Keychain 재생성 및 격리 local DB 응답 유실 복구를 시험한다. 기존 Keychain 항목은 건드리지 않는다.
- 격리 Xcode project `artifacts/ios-recovery-check.k370d0`에서 ad-hoc 서명 `xcodebuild ... -only-testing:GameBridgePushTests/MockRecoveryDeviceTests test -quiet` 종료 0. quiet 출력에 시험 건수가 나타나지 않아 xcresult에서 실제 실행 수와 결과를 확인하기 전 PASS로 기록하지 않는다.
- `xcrun xcresulttool get test-results summary/tests` 확인: iOS 26.5 전용 simulator에서 `MockRecoveryDeviceTests/testKeychainInstancesRecoverCommittedMockPurchaseOnce` 1건 실행·통과, skip 0. 임의 test Keychain service 재생성 후 격리 local DB 지급 재검증·100 한 번 증가를 확인했다. 실제 기기·프로세스 강제 종료·Unity player는 아니다. Mock user B에 지급 1건을 남겼다.
- 직접 기동한 Android 전용 AVD와 local Backend만 종료했다. emulator 데이터·PostgreSQL volume·iOS simulator는 보존했다.
- 커밋 전: 두 플랫폼의 보안 저장소 인스턴스 재생성 및 격리 DB Mock 복구 기기 시험과 정제된 결과만 포함한다. 실기기 프로세스 재시작·Unity player와 실제 스토어는 미검증이다.

### [P06-T03] Unity iOS push host 연결
- Task 시작: Unity host-managed APNs의 token·수신·열기 이벤트와 Native 인증·Backend 등록 경계를 확인한다. 실제 APNs 발송은 사용자 설정 전 실행하지 않는다.
- iOS host adapter는 이미 정규화된 알림을 Swift host operation으로 전달하지만 현재 Unity 공개 이벤트와 Native operation이 연결되지 않았다. 우선 허용 route만 노출하는 이벤트 수신 경계를 추가한다.
- `UNITY_EDITOR_PATH=... bash scripts/smoke-csharp-registry.sh` 종료 0: 같은 session의 PushOpened 허용 route만 공개하고 임의 URL route를 거부하는 독립 .NET 시험 통과. Native 발행·Unity 실행은 아직 미검증이다.
- Swift C ABI에 host push 수신·열기를 연결해 route allowlist와 기존 200-ID 중복 제거기를 통과한 안전한 필드만 Unity 이벤트로 반환한다. 이 작업은 원격 APNs 수신이나 토큰 등록 성공을 뜻하지 않는다. C ABI synthetic 시험을 추가한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0, 기존 2건. 새 host push 이벤트의 route·중복·민감 필드 제거는 별도 C ABI synthetic 시험으로 검증한다.
- `swift test --package-path ios --filter CBridgeTests` 종료 0, 3건: synthetic host PushOpened 전달, 허용 외 URL 필드 제거·중복 억제·비허용 route 거부를 확인했다. 실제 원격 APNs 및 Unity player는 실행하지 않았다. C# 조건부 및 iOS simulator compile을 확인한다.
- C# 네 조건부 compile 및 iOS simulator static framework build 종료 0. 추가 검토에서 RequestRegistry allowlist가 internal `host.push*` 요청을 차단해 Unity host adapter가 Native까지 도달하지 못하는 기존 결함을 발견했다. 내부 host operation만 allowlist에 추가하고 회귀 확인한다.
- `scripts/smoke-csharp-registry.sh` 재실행 종료 0: internal host.pushOpened 요청이 registry allowlist를 통과하고 응답에 상관되는 것을 확인했다. 실제 Unity notification package/원격 APNs는 미실행이다.
- 커밋 전: Unity public push 이벤트 수신 및 iOS host 알림 route·중복 제거 synthetic 경로만 포함한다. APNs token 등록·실제 원격 전달과 Unity player 검증은 미완료다.

### [P06-T03] Unity iOS APNs token 등록
- Task 시작: host가 제공하는 installation UUID와 APNs token을 Native의 인증된 Backend 등록 경계에 연결한다. token 원문은 공개 결과·로그에 넣지 않고 등록 해제·로그아웃 삭제 정책을 유지한다. 실제 원격 APNs는 사용자 설정 대기다.
- Unity 설정에 host-provided installation UUID를 추가하고 ApplePushClient의 인증된 등록·해제 경로를 `host.pushToken` 및 `push.unregister`에 연결했다. Unity Mobile Notifications 2.5.0의 token 문자열이 hex임을 package source로 확인했으며 공개 응답에는 fingerprint만 둔다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` 종료 0, 2건 및 `--filter AppleAuthProviderTests.testPushRegistrationUsesSessionAndReturnsFingerprint` 종료 0, 1건. 기존 인증·Native fake PUT/DELETE 경계만 확인했으며 새 bridge token 검증·UIKit 분기는 별도 확인한다.
- Swift fake `AppleAuthBridgeTests` 종료 0, 3건 및 Native push registration 시험 종료 0, 1건: 잘못된 token 거부, fingerprint만 반환, unregister, 인증/Backend 설정 불일치 차단을 확인했다. 실제 APNs·Backend 실계정은 아니다. C# 및 UIKit simulator compile을 실행한다.
- `scripts/check-csharp-compile.sh` 4개 조건부 및 `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 모두 종료 0. 실제 Unity Player·원격 APNs·실계정 Backend 등록은 미검증이다.
- 커밋 전: iOS host token의 Native Backend 등록·해제와 installation ID 설정, fake 검증만 포함한다. Unity public permission/register facade 연결과 실제 원격 APNs는 미완료다.

### [P06-T03] Unity iOS public push API
- Task 시작: 공식 Mobile Notifications host adapter가 권한 UI와 APNs 등록을 소유하는 구조를 유지하면서 public permission/register 요청을 host에 연결한다. 사용자 요청 없이 권한 dialog를 띄우지 않는다.
- Unity public push facade에 host driver 주입 경계와 Native 등록 응답 fingerprint 검증을 추가했다. UI host driver는 아직 구현 중이며 컴파일/동작 검증 전이다.
- iOS host adapter가 public permission 요청은 OS 권한만, register 요청은 명시적 APNs 등록과 Backend fingerprint 확인을 수행하도록 연결했다. 취소·detach·중복 UI 요청은 오류로 구분한다. Unity 공식 package 참조 컴파일과 fake host API 시험을 진행한다.
- `scripts/check-unity-ios-host.sh` 종료 0: Unity Mobile Notifications 2.5.0 공식 source와 host adapter 별도 assembly compile, 경고·오류 0. 실제 권한 dialog/Unity 실행은 아니다. public facade의 host 분기와 fingerprint 검증을 fake transport로 확인한다.
- `scripts/smoke-csharp-registry.sh` 종료 0: fake host는 attach만으로 권한/등록을 호출하지 않고 명시적 public API에서만 실행되며, Native 응답의 raw token 형태 fingerprint는 거부된다. 실제 Unity coroutine·OS 권한 UI는 아니다.
- client Dispose 시 host driver를 해제하고 대기 중 요청을 종료하도록 연결했다. OS authorization 객체 생성 자체가 실패해도 Task가 무한 대기하지 않도록 보강 후 공식 package compile을 재실행한다.
- `scripts/check-unity-ios-host.sh` 및 `scripts/check-csharp-compile.sh` 종료 0: 공식 Notifications source와 iOS host assembly, 4개 조건부 C# compile 모두 경고·오류 0. 실제 Unity coroutine/권한 대화상자, 원격 APNs는 검증하지 않았다.
- 커밋 전: iOS host driver의 public permission/register 연결·fake facade 검증과 source compile만 포함한다. 실제 Unity Player/기기·원격 APNs 및 Android push 연결은 미완료다.

### [P06-T01] Android FCM 등록 bridge
- Task 시작: host가 초기화한 Firebase와 Android notification 권한을 전제로 Native token 등록·해제를 Unity sandbox bridge에 연결한다. 실제 Firebase 설정 및 원격 발송은 사용자 설정 대기로 유지한다.
- Android sandbox bridge에 host 설치 UUID와 Native GooglePushClient 등록·해제, 명시적 FCM token 조회 경로를 추가했다. Firebase가 없거나 OS 권한이 없으면 성공으로 처리하지 않고 오류를 반환한다. 컴파일과 fake 경계를 확인한다.
- Android FCM bridge 첫 컴파일 종료 1: 기본 `unregisterPush`의 Kotlin 반환형이 Nothing으로 추론되어 실제 Unit 구현과 충돌했다. 반환형을 명시하고 재검증한다.
- 재컴파일에서 Native 코드는 통과했지만 기존 fake test factory lambda 한 곳이 새 installation 인자를 받지 않아 test compile 종료 1. fake signature를 맞추어 재실행한다.
- `:sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug` 재실행 종료 0. 기존 fake 인증·구매 시험 및 AAR compile 통과했고, 새 FCM token redaction·등록 해제는 추가 fake 시험이 필요하다.
- FCM fake 통합 시험에서 bridge test는 실행됐지만 Android test compile이 실패했다. 새 설정 불일치 시험이 기존 `config()` 함수를 값처럼 참조한 위치를 확인해 수정한다.
- 수정 후 `:sdk-android:testDebugUnitTest --tests GoogleAuthProviderTest :sdk-unity-bridge:testDebugUnitTest` 종료 0: fake FCM 등록·해제, token 비노출, 다른 Backend 설정 거부를 확인했다. 실제 Firebase token/원격 수신은 미실행이다.
- push capability에는 installation ID가 있어도 Firebase 초기화와 OS 권한은 별도 확인이 필요하다는 이유를 명시했다. 변경 후 bridge fake 시험을 재실행한다.
- `:sdk-unity-bridge:testDebugUnitTest` 재실행 종료 0. Firebase host 실제 초기화·Android OS permission UI·token refresh 수명주기 및 원격 FCM은 확인하지 않았다.
- 커밋 전: Android sandbox FCM token 조회·Backend 등록/해제 코드 및 fake 경계만 포함한다. Unity permission dialog·host service 자동 forwarding·실제 FCM 및 FID 전환은 미완료다.

### [P06-T01] Unity Android 알림 권한
- Task 시작: Unity Android host가 명시적 public 권한 요청에서만 OS 권한 UI를 표시하도록 연결하고, 거부 또는 미설정 상태는 등록 성공으로 처리하지 않는다.
- Unity 공식 PermissionCallbacks/RequestUserPermission 문서를 확인했다: https://docs.unity3d.com/ja/6000.0/ScriptReference/Android.Permission.RequestUserPermission.html . Android 13 이상에서 명시적 호출로만 runtime 권한 dialog를 띄우고, 이전 버전은 별도 runtime 알림 권한 요청이 없도록 구현한다.
- Unity Android transport에 notification permission 전용 host 경계를 작성했다. 연결/초기화만으로 prompt하지 않으며 Android 13 이상은 Unity PermissionCallbacks 결과를 사용하고, 취소·중복·종료를 구분한다. 공식 Unity managed reference compile 및 facade fake 시험을 진행한다.
- `scripts/check-csharp-compile.sh` 종료 0이나 Android 조건부에서 `PermissionDeniedAndDontAskAgain` deprecated 경고 1개가 발생했다. Unity 공식 문서가 해당 callback을 신뢰하지 않고 PermissionDenied fallback을 권장하므로 deprecated 구독을 제거하고 재검증한다.
- `scripts/check-csharp-compile.sh` 재실행 종료 0, Android 포함 경고 0; `scripts/smoke-csharp-registry.sh` 종료 0: fake transport 초기화 시 prompt 없음과 명시적 Android 권한 거부 전달을 확인했다. 실제 Android 권한 dialog는 미실행이다.
- Android 13 미만에서도 앱 알림이 설정에서 꺼져 있을 수 있어 NotificationManager 실제 허용 상태를 확인하도록 보강했다. 취소된 요청은 가능한 경우 dialog 시작 전에 중단한다. Native compile과 C# 조건부 compile을 재확인한다.
- `:sdk-android:testDebugUnitTest --tests AndroidPushHostAdapterTest` 종료 0, `scripts/check-csharp-compile.sh` 종료 0(경고 0). Native test는 token callback fake이며 실제 OS 알림 설정은 아직 실행하지 않았다.
- C# 권한 snapshot도 Native 등록 검사와 동일하게 앱 전체 알림 허용 상태를 확인하도록 보정한다. 최종 조건부 compile을 확인한다.
- 최종 `scripts/check-csharp-compile.sh` 종료 0, 4개 조건부 경고·오류 0. 실제 Android 13+ dialog·권한 설정 및 Unity Player 실행은 미검증이다.
- 커밋 전: Android permission driver와 fake facade/compile만 포함한다. Firebase token rotation·수신 host forwarding 및 실제 원격 FCM은 미완료다.

### [P06-T05] Android FCM host callback
- Task 시작: host 소유 FirebaseMessagingService와 클릭 intent에서 token·허용 route를 Unity session으로 안전하게 전달한다. cold-start와 인증 전 token 처리 범위를 명시하고 실제 FCM 발송은 수행하지 않는다.
- Android cold-start 알림은 SDK READY 전에 도착할 수 있다. 초기화 응답보다 먼저 전달된 안전한 이벤트를 Unity facade가 버리지 않도록 일시 큐에 보관한 뒤 메인 thread Pump에서 전달한다. token refresh는 session이 없으면 등록을 시도하지 않고 다음 명시적 등록으로 넘긴다.
- `scripts/check-csharp-compile.sh` 종료 0, 4개 조건부 경고 0. 초기화 중 도착한 push를 READY 후 Pump에서 전달하도록 구현했으며, 초기화 실패·종료 시 큐가 남지 않도록 확인한다.
- C# 4개 조건부 compile 통과. 초기화 중 queue는 실패·로그아웃·종료 시 비우고, token 이벤트의 등록 상태와 fingerprint/error 일관성을 엄격 검사한다. Android Native host callback 전달을 구현한다.
- Android host notification callback을 기존 100 queue/200 ID router와 Unity 안전한 이벤트에 연결했다. FCM token rotation은 활성 session에서만 Native 인증 등록을 큐에 넣고 결과는 fingerprint 또는 오류 이벤트로 반환하며, 반환 Boolean은 등록 성공이 아닌 큐 접수다.
- `:sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug` 종료 0: 기존 fake suite 및 AAR compile 통과. 새 cold-start 이벤트와 token callback 실패 경계는 별도 시험한다.
- `scripts/smoke-csharp-registry.sh` 종료 0: 초기화 전 이벤트는 READY/Pump까지 보관하고, token fingerprint 검증에서 raw token을 거부함을 독립 .NET fake로 확인했다. 실제 Unity Player는 아니다.
- `:sdk-unity-bridge:testDebugUnitTest --tests HostPushDeliveryTest` 종료 0: 초기화 전 알림 queue·중복 및 위험 route 거부, session 없는 token 미접수와 fake 등록 실패 이벤트의 raw token 비노출 확인. 실제 Firebase 서비스/앱 cold-start는 아니다. 기존 host의 서비스·Activity에 호출을 삽입하는 예제를 추가했다.
- 커밋 전: Android host callback API·cold-start 메모리 queue·Unity token/event 검증 및 fake 시험만 포함한다. host 앱 통합, 실제 Firebase 원격 발송·Unity Player 및 process 종료를 넘는 보관은 구현/검증하지 않았다.

### [P05-T06] Play recovery single-flight
- Task 시작: 이전 Android recovery는 동시 요청을 직렬화하지만 두 번째 요청도 재조회한다. 동시에 들어온 호출이 하나의 조회·검증 작업을 공유하도록 수정하며 caller 취소가 다른 호출자의 복구를 중단시키지 않도록 한다.
- Android 복구 호출이 동일 계정의 진행 중 Deferred를 공유하도록 변경하고, 조회 전후 계정 binding을 재확인한다. 한 caller 취소는 공유 작업을 취소하지 않는다. fake 동시·계정 전환 경계를 확인한다.
- 기존 `GooglePlayBillingProviderTest` 종료 0: 기본 검증 동시성·account binding·복구 집계 회귀 통과. 새 공유 복구 및 caller 취소/계정 전환은 별도 fake 시험을 추가한다.
- `:sdk-android:testDebugUnitTest --tests GooglePlayBillingProviderTest` 재실행 종료 0: 동시 복구 요청은 조회 1회를 공유하고 한 caller 취소 후 다른 caller가 완료했으며, 도중 계정 변경은 공유와 결과를 CANCELED로 차단했다. 실제 Play는 미실행이다.
- 커밋 전: Android Native recovery single-flight와 fake 시험만 포함한다. iOS의 중첩 복구는 현재 BUSY 처리이며 실제 플랫폼 검증은 대기다.

### [P05-T06] StoreKit recovery single-flight
- Task 시작: iOS의 중첩 복구 BUSY를 동일 계정·동일 사유에 한해 공유 작업으로 변경한다. APP_RESUME과 USER_RESTORE는 합치지 않아 background에서 사용자 인증 UI가 생기지 않도록 한다.
- StoreKit recovery를 동일 계정·동일 사유에서 공유하고, 다른 계정은 CANCELED, 다른 사유는 BUSY로 분리했다. 명시적 USER_RESTORE만 AppStore.sync/UI gate를 사용하며 stop 시 공유 작업을 취소한다. fake concurrency 시험을 진행한다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 기존 3건 회귀 통과. 새 flight 공유·취소 및 다른 사유/계정 차단은 별도 fake 시험을 추가한다.
- `swift test --package-path ios --filter StoreKitBillingProviderTests` 종료 0, 4건: fake 공유 복구 1회, caller 취소 격리, 다른 사유 BUSY·다른 계정 CANCELED를 확인했다. 실제 AppStore.sync 및 StoreKit 거래는 실행하지 않았다. simulator framework compile을 확인한다.
- `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. 무서명 simulator compile이며 실제 StoreKit 복원·Unity player는 아니다.
- 커밋 전: iOS 동일 사유·계정 recovery single-flight 및 fake 시험만 포함한다. 실제 StoreKit 복원과 ENV-STOREKIT-26은 미검증/실패 유지한다.

### [P06-T05] LOCAL_MOCK push 연결
- Task 시작: 로컬 Backend의 token 등록·삭제 및 개발용 SIMULATED 발송 계약을 조사하고 Native/Unity Mock 경로를 연결한다. 실제 FCM/APNs 원격 발송과 구분한다.
- 블로커 BUG-010 발견: `GET /v1/config`는 16진 hash revision을 반환하지만 Unity ServiceConfig decoder는 10진 64-bit 문자열만 허용한다. 실제 config 조회가 BRIDGE_PROTOCOL_MISMATCH가 되므로 서버를 63-bit 비음수 10진 문자열 계약으로 일치시키고 실제 경계를 확인한다. 기존 설정 내용이나 cache 보존값을 삭제하지 않는다.
- 서버 config revision을 같은 설정에서 안정적인 비음수 signed 63-bit 10진 문자열로 변경했다. config 내용 변경 시 revision이 달라지는지 서버 unit과 실제 local HTTP→Unity decoder를 확인한다.
- `backend/gradlew -p backend test --tests com.gamebridge.push.PublicServiceConfigControllerTest` 종료 0: 설정 누락 차단, TTL, 10진 revision 안정성·변경 반영 확인. 실제 local HTTP 응답을 Unity decoder에 전달한다.
- 실제 local config→.NET smoke 첫 실행 종료 134(BRIDGE_PROTOCOL_MISMATCH). 조사 결과 테스트가 JObject.Parse의 기본 날짜 자동 변환을 사용해 expiresAt을 Date로 만들었으며 실제 RequestRegistry는 DateParseHandling.None을 사용한다. 실제 경로와 같은 reader 설정으로 재검증한다.
- local `GET /v1/config` 응답을 DateParseHandling.None으로 읽어 Native가 사용하는 source NETWORK로 표기한 뒤 Unity ServiceConfig decoder에 전달한 .NET smoke 재실행 종료 0. 실제 Unity Player/JNI/C ABI 전체 왕복은 아니다.
- 직접 기동한 local Backend만 종료하고 DB는 보존했다. revision 변경은 기존 실행 중 in-memory cache가 만료되기 전 과거 16진 값을 보유할 수 있으며, cache 만료 또는 재시작 후 새 형식을 사용한다.
- 커밋 전: 서버 revision 계약 수정과 서버 unit/local HTTP→Unity decoder 증거만 포함한다. Unity Player 전체 config 왕복은 미검증이다.

### [P06-T05] LOCAL_MOCK push 등록
- Task 시작: host가 명시한 installation UUID로 개발용 Mock token을 Native에서 생성하고 인증된 Backend 등록·해제를 연결한다. Mock permission은 OS dialog를 호출하지 않는 simulated 결과이며 실제 원격 push로 취급하지 않는다.
- Android Mock client에 Native 생성 가짜 token의 인증된 Backend 등록·해제를 추가했다. Unity LOCAL_MOCK은 Mock permission을 사용해 실제 OS 권한 창을 열지 않으며 installation UUID를 명시해야 한다. iOS 동등 경로를 구현하고 검증한다.
- Android `:sdk-core:test :sdk-unity-bridge:assembleDebug` 종료 0: 기존 core fake와 bridge AAR compile 통과. 새 Mock token 등록·해제는 별도 local HTTP/DB 검증 전이다.
- Swift Mock client에도 별도 임의 token의 Backend 등록·해제 및 simulated permission을 추가했다. token 원문은 결과에 넣지 않으며 remote delivery는 구현·성공으로 간주하지 않는다. Swift compile과 fake 경계를 확인한다.
- `swift test --package-path ios --filter LocalMockMaintenanceTests` 종료 0, 기존 3건 회귀 통과. 양 플랫폼 Mock token의 실제 local DB 등록·해제·로그아웃 삭제를 확인하기 위한 opt-in 시험을 추가한다.
- Mock에서 실제 host 권한창을 차단한 뒤 기존 .NET smoke가 EditorOffline에 붙인 fake APNs host가 호출되기를 기대해 종료 134. 기대가 새 모드 격리와 충돌하므로 Mock에서는 host 미호출을 검증하고 sandbox fake에서 host 호출을 별도로 검증한다.
- `scripts/smoke-csharp-registry.sh` 재실행 종료 0: EditorOffline에서 host permission/register가 호출되지 않고 sandbox에서만 명시적 호출됨을 확인했다. LOCAL_MOCK 전체 bridge 및 실제 OS dialog는 이 시험 범위가 아니다.
- Android opt-in `LocalMockIntegrationTest.mock push registration unregister and logout remove token` 종료 0: 격리 local DB에 Mock token 1건 등록 후 unregister 즉시 삭제, 재등록 후 logout 즉시 삭제를 확인했다. 외부 FCM 발송은 없다.
- Swift opt-in `LocalMockIntegrationTests.testMockPushUnregisterAndLogoutRemoveToken` 종료 0, 1건: 격리 local DB의 Mock token unregister·logout 즉시 삭제를 확인했다. 실제 APNs는 실행하지 않았다. 두 플랫폼 bridge handler도 같은 Backend와 연결해 확인한다.
- Android opt-in `LocalMockIntegrationTest.bridge uses real local backend for mock purchase and restore` 종료 0: Native bridge→local Backend의 Mock permission·token 등록/해제와 구매·잔액이 함께 통과했다. 테스트 Mock user B에 구매 1건을 남겼다. Unity JNI 및 FCM은 아니다.
- Swift opt-in `LocalMockIntegrationTests.testBridgeHandlerAgainstLocalBackend` 종료 0, 1건: Swift handler→local Backend의 Mock token 등록/해제와 구매·잔액 통과. 테스트 Mock user B에 구매 1건을 남겼다. Swift C ABI 전체·Unity iOS 및 APNs는 아니다.
- Mock token fingerprint는 서버 JSON의 문자열만 허용하도록 엄격화했다. 직접 기동한 Backend만 종료하고 DB volume을 보존했다. C#·iOS compile 및 Android core 회귀를 확인한다.
- `:sdk-core:test`, `scripts/check-csharp-compile.sh` 4개 조건부, `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 모두 종료 0. 실제 Unity Player와 Mock push 전체 전달은 미검증이다.
- 커밋 전: 양 Native Mock token 등록·해제, Mock permission 모드 격리, local DB/fake 및 compile 증거만 포함한다. Backend SIMULATED 발송의 client 전달 E2E·실제 FCM/APNs는 미구현/미검증으로 유지한다.

### [P07-T02] Unity sample Native 경로
- Task 시작: 기존 사용자 소유 `unity/Demo`는 보존하고 UPM sample의 설정·Mock/sandbox 기능·상태 표시를 조사한다. Backend SIMULATED push는 실제 수신으로 가장하지 않는다.
- UPM에 별도 Native Demo를 추가했다. runtime 입력으로 Mock/Sandbox 설정, 로그인·상품·구매·잔액·복구·push·로그아웃을 명시적으로 호출하며 개발키는 scene asset에 저장하지 않는다. Unity Editor 실행은 허위 지원하지 않는다. Unity managed reference로 컴파일한다.
- `scripts/check-unity-sample.sh` 종료 0: Native Demo와 기존 Offline Demo가 Unity managed/uGUI 참조로 컴파일됐다. Editor 렌더링·기기 실행은 아니다. 구매 완료 이벤트가 UI 작업 중 도착해도 서버 잔액 재조회가 누락되지 않도록 보강한다.
- Native Demo의 iOS host bridge는 사용자가 scene에 명시적으로 추가하도록 분리했다. 단순 생성만으로 foreground 알림 표시 정책을 바꾸지 않으며, 실제 iOS 분기와 공식 host assembly를 별도 compile한다.
- `scripts/check-unity-sample.sh` 두 번째 iOS 조건부 compile 종료 1: 별도 시험 project에 UnityEngine.UIModule/TextRenderingModule 참조가 빠져 Canvas/Font를 찾지 못했고 FindFirstObjectByType deprecated 경고가 발생했다. 실제 Unity 빌드 실패로 오인하지 않고 시험 참조와 API를 수정한다.
- `scripts/check-unity-sample.sh` 재실행 종료 0: Editor 조건부 sample 및 iOS host branch가 실제 Unity managed/uGUI/Notifications 참조로 각각 경고·오류 0 컴파일됐다. Unity Editor 렌더링·IL2CPP·기기 실행은 아니다.
- 샘플 객체가 UI 요청 중 파괴될 때 늦은 Task가 제거된 상태 UI를 갱신하지 않도록 보호를 추가한다. 최종 sample compile을 확인한다.
- `scripts/check-unity-sample.sh` 최종 종료 0: Native/Offline sample과 iOS host bridge가 Unity managed/uGUI/Notifications 참조로 경고 0 컴파일됐다. sample object 파괴 후 late Task UI 접근을 막았다. 실제 scene 렌더링·입력·Unity player는 ENV-002로 미검증이다.
- 커밋 전: UPM Native sample 소스·설치 안내 및 독립 compile project만 포함한다. 기존 미추적 unity/Demo는 보존하고 실제 Native 앱 실행은 미완료다.

### [P07-T04] 기능 matrix 갱신
- Task 시작: 기존 matrix가 Native bridge·config cache를 미구현으로 표시해 현재 코드와 어긋나므로 호출 경로와 실제 검증 범위를 다시 대조한다. 최종 P11 완료 감사와 혼동하지 않는다.
- Android/iOS Mock·실 Provider bridge, push, config, sample, packaging의 실제 호출 경로와 WORK_LOG 증거를 대조해 오래된 matrix를 수정했다. 검증은 코드/기록 검토이며 새 플랫폼 실행은 아니다.
- 커밋 전: 기능 matrix 상태 문서만 포함한다. P11 최종 감사나 전체 완료로 표시하지 않는다.

### [P07-T01] Sandbox config 공개 bridge
- Task 시작: Android/iOS sandbox의 `config.get`을 Native 상점의 점검 gate와 같은 서버 설정 repository에 연결한다. 캐시 부재 시 사용자 결정대로 신규 구매를 막고, 실패를 정상 상태로 바꾸지 않는다.
- Android에 인증 설정이 일치하는 Backend 전용 GoogleStoreSession을 추가해 공개 config 조회와 구매 gate가 같은 cache를 사용하도록 했다. 임의 fake cache를 실제 store에 주입하는 공개 경로는 만들지 않는다. Android compile/fake 시험을 진행한다.
- `:sdk-android:testDebugUnitTest :sdk-unity-bridge:testDebugUnitTest :sdk-unity-bridge:assembleDebug` 종료 0: 기존 Native/bridge fake 시험과 AAR compile 통과. sandbox config 값 전달과 iOS 동등 경로는 이어서 검증한다.
- iOS에도 인증·Backend 구성이 일치하는 AppleStoreSession을 추가하여 공개 config와 StoreKit 구매 gate가 같은 Backend-backed cache를 공유하도록 했다. Swift compile과 fake config 경계를 확인한다.
- Swift `AppleAuthBridgeTests` 3건, `AppleAuthProviderTests` 13건 종료 0. 기존 fake 인증·상점·점검 회귀이며 새 config.get response와 공유 cache 동작은 별도 확인한다.
- `:sdk-unity-bridge:testDebugUnitTest` 종료 0, Swift `AppleAuthBridgeTests` 3건 및 config 일치 store test 1건 종료 0: fake CACHE·점검 상태 전달과 다른 Backend 설정 거부를 확인했다. 실제 sandbox Backend/Unity 왕복은 미실행이다. iOS simulator compile을 확인한다.
- `xcodebuild ... GameBridgeNative ... generic/platform=iOS Simulator CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. UIKit/StoreKit 포함 무서명 compile이며 실제 sandbox 서버·기기·Unity player 검증은 아니다.
- 커밋 전: sandbox config.get과 Native 구매 gate의 Backend-backed cache 공유 코드 및 fake/compile 증거만 포함한다. 실제 sandbox와 Unity 실행은 미검증이다.

### [P08-T01] 최신 Android 산출물 검증
- Task 시작: 최근 Native/Unity bridge 변경이 포함된 Maven 산출물과 소스 없는 consumer compile을 다시 확인한다. 기존 artifacts를 덮어쓰지 않는 경로를 우선 사용한다. 실제 Unity export/Play 검증은 별개다.
- 기존 Maven 경로를 덮어쓰는 build script를 새 절대 경로 또는 고유 임시 output 사용으로 변경하고, publish와 독립 consumer가 동일 경로를 읽도록 구성했다. 기존 산출물은 보존한다. 새 경로에서 빌드·R8 consumer를 검증한다.
- 새 `scripts/build-android.sh --mock`의 Maven publish·sample APK는 진행됐으나 독립 R8 consumer에서 `Missing class com.google.firebase.messaging.FirebaseMessaging`으로 종료 1. Firebase를 optional compileOnly로 선언한 SDK를 bridge가 참조하며 비-Firebase consumer의 shrink가 실패하는 회귀를 발견했다. 원인을 수정하고 새 output에서 재검증한다.
- FirebaseMessaging은 선택적 host 의존성이므로 SDK consumer ProGuard에 해당 단일 class에 대한 좁은 dontwarn을 추가했다. 실제 호출은 class 존재 확인과 LinkageError→CONFIG_REQUIRED/onError로 보호하며, Firebase 없는 기기 실행도 별도로 확인한다.
- 새 output `artifacts/maven-p08-20261111-b`에서 `scripts/build-android.sh --mock` 종료 0: Maven publish·sample APK 및 Firebase 없는 독립 consumer R8 release build 통과. SDK XML 버전 경고는 있었고, runtime CONFIG_REQUIRED 동작은 아직 별도 기기 시험 전이다.
- Firebase 없는 sandbox bridge의 runtime 차단을 검증하는 Android instrumented test를 추가했고 sample/test APK build 종료 0. 테스트는 example.invalid 설정만 사용하며 네트워크 인증을 요청하지 않는다.
- AVD가 adb 연결만 완료된 시점에 APK 설치를 시작해 package service가 없어 실패했다. `sys.boot_completed=1` 확인 후 같은 전용 AVD에 재시도한다. 테스트는 아직 실행되지 않았다.
- 전용 Android 36 emulator에서 `FirebaseOptionalBridgeTest` 1건 통과: FirebaseMessaging class 부재, sandbox bridge 초기화 후 push.register가 네트워크 호출 없이 CONFIG_REQUIRED를 반환했다. debug instrumented runtime이며 R8 release 실행 자체는 아니다.
- 동일 `GAMEBRIDGE_MAVEN_REPO=.../maven-p08-20261111-b`로 재실행 시 종료 2 및 “output exists”를 확인해 기존 Maven output을 덮어쓰지 않았다. 직접 기동한 전용 AVD만 종료했다.
- 커밋 전: 선택적 Firebase consumer 규칙·runtime fail-closed 시험과 새 Maven output 경로만 포함한다. R8 release 실제 실행, Unity import/export 및 원격 FCM은 미검증이다.

### [P08-T02] 최신 iOS XCFramework
- Task 시작: 최근 StoreKit·푸시·Mock 변경을 포함해 device/simulator static XCFramework를 새 output에 생성하고 별도 소비 link를 확인한다. 기존 generated project와 artifacts를 덮어쓰지 않는다.
- XcodeGen project를 새 artifacts 격리 layout에 생성하도록 바꾸고 build/hook이 해당 경로를 사용하게 했다. 기존 `ios/Framework/GameBridgeSample.xcodeproj`를 덮어쓰지 않는다. 새 device/simulator archive와 XCFramework를 검증한다.
- `GAMEBRIDGE_IOS_OUTPUT_DIR=.../ios-package-20261111-a bash scripts/build-ios.sh --xcframework` 종료 0: 격리 XcodeGen project에서 iOS device 및 simulator 무서명 archive와 static XCFramework 생성. Xcode output은 기존 산출물을 덮어쓰지 않았다. symbol·독립 consumer link 확인은 별도다.
- `file`/`nm -g` 종료 0: device arm64 및 simulator arm64/x86_64 static archive와 GB_ProtocolVersion/SetCallback/Dispatch/Shutdown export 확인. `xcrun swiftc ... ios/consumer-check/main.swift` simulator 별도 source consumer link 종료 0. 실제 simulator 실행·서명된 device·Unity linkage는 아니다.
- 동일 output 재실행 종료 2로 덮어쓰기를 거부했고, `scripts/smoke-ios-hook.sh`의 실제 Unity PBX managed API 중복 적용 확인 종료 0. 실제 Unity export는 아니다.
- 커밋 전: 격리 XcodeGen/build/hook 경로와 문서만 포함한다. 기존 generated project·산출물과 사용자 파일은 보존했다.

### [P08-T03] 최신 UPM staging
- Task 시작: 새 Android Maven과 무서명 iOS XCFramework를 별도 UPM staging에 묶고 체크섬 및 export hook의 독립 idempotence 시험을 확인한다. Unity 라이선스 부재는 그대로 분리한다.
- `scripts/package-sdk.sh` 종료 0: `artifacts/upm-staging-20261111-a` 생성. SHA256 110개 검사 오류 0. `smoke-gradle-patcher.sh` 종료 0(Gradle patcher·stub hook), `smoke-ios-hook.sh` 종료 0(실제 PBX managed API 멱등성). Unity Editor import/export·IL2CPP 실행은 아니다.
- staging package.json의 Offline/Native 두 sample 경로, Android bridge AAR 및 iOS XCFramework plist 존재를 확인했다. 이는 Unity import 성공을 의미하지 않는다.
- 커밋 전: staging 검증 증거와 원장만 포함한다. artifacts는 Git에 넣지 않으며 Unity 라이선스 ENV-002 대기와 미구현 기능은 유지한다.

### [P08-T05] 부분 기능 기준점
- Task 시작: 최신 코드와 protocol snapshot을 저장하고 P00~P08 전 행 및 미완료 사항을 기록한다. Unity 설치 검증·StoreKit 실패·Mock push delivery 등으로 이 기준점은 완료가 아닌 PARTIAL이다.
- snapshot 13개 SHA256과 현재 source 바이트 일치, 계획의 P00~P08 48개 Task와 기준점 표의 ID 집합·건수 일치를 확인했다. 기준점은 INCOMPLETE이며 기능 실행 검증이 아니다.
- 커밋 전: API/protocol snapshot과 미완료 기준점 문서만 포함한다. P08-T05는 PARTIAL, 기존 내부 미구현과 환경 실패는 그대로 유지한다.

### [P09-T01] regression manifest·공통 계약
- Task 시작: 미완료 P08 기준점을 유지한 채 독립적으로 가능한 하네스 작업을 시작한다. 계획의 R01~R50을 모두 등록하고 현재 시험으로 부분 검증되는 것과 미구현을 분리한다. required scenario 미구현·누락은 성공으로 처리하지 않는다.
- 계획 R01~R50을 모두 manifest에 등록하고 candidate suite와 coverage를 PARTIAL/NOT_IMPLEMENTED로 명시했다. scenario runner는 부분·미구현 또는 환경 미실행을 exit 2로 남기며 전체 통과로 승격하지 않는다. 공통 contract runner를 작성한다.
- 공통 contract runner는 Kotlin/Swift/C# fixture 시험을 실제 실행하고 Kotlin XML·Swift 실행 수·C# smoke marker가 없거나 0이면 성공을 거부한다. 로그는 새 artifacts 디렉터리에만 남긴다. manifest와 실제 runner를 검증한다.
- `python3 harness/check-manifest.py` 종료 0: 계획 R01~R50 50개 목록·실행 entry 구조 일치(시나리오 실행 아님). `harness/run-contracts.py` 종료 0: Kotlin 4, Swift 4, C# 독립 smoke 1 실행; Unity Editor/실기기 검증은 포함하지 않는다. 잘못된 공통 fixture가 실제로 실패하는지 격리 사본으로 확인한다.
- `harness/check-contract-negative.py` 종료 0: 새 격리 fixture 사본의 유효 request protocolVersion을 99로 바꿨을 때 Kotlin과 Swift contract runner가 각각 실패함을 확인했다. 원본 fixture는 변경하지 않았다.
- `harness/check-manifest-negative.py` 종료 0: 새 manifest 사본에서 R49 제거 시 검사기가 nonzero를 반환했다. `harness/run-scenario.py R49`는 NOT_IMPLEMENTED와 exit 2를 반환했다. 음성 fixture 테스트 이후 원본으로 공통 계약 시험을 다시 실행한다.
- 음성 fixture 시험 후 원본 `harness/run-contracts.py` 재실행 종료 0: Kotlin 4·Swift 4·C# smoke 1. Gradle이 test 전 실패한 경우 오래된 XML을 실행 수로 재사용하지 않도록 report 수정 시각 확인을 추가하고 재검증한다.
- report 신선도 검사 추가 후 `harness/run-contracts.py` 종료 0: Kotlin 4, Swift 4, C# 독립 smoke 1. 결과는 `artifacts/contracts-_t6il2fe/result.json`에 있으며 작업 트리는 HEAD+미커밋 변경이다. Unity Editor/IL2CPP와 50개 시나리오 전체 PASS가 아니다.
- 커밋 전: P09 manifest·부분 coverage의 fail-closed runner·공통 계약 및 격리 음성 시험만 포함한다. 50개 개별 assertion 대응과 required platform lane은 아직 미완료로 P09-T01 PARTIAL 유지한다.

### [P09-T02] Bridge 중복 callback 음성 검증
- Task 시작: 실제 소스는 수정하지 않고 새 격리 디렉터리의 registry 복제본에서 중복 응답 guard만 제거해 기존 smoke가 실패하는지 확인한다. 이후 원본 정상 시험을 재실행한다. Unity Editor scene/Domain Reload는 ENV-002 대기다.
- disposable .NET project에서 registry의 중복 응답 guard 한 곳만 제거하는 mutation 검사기를 작성했다. 컴파일 오류가 아닌 해당 runtime 경로의 실패여야 감지로 인정한다.
- `harness/check-bridge-mutation.py` 종료 0: 새 복제본의 중복 응답 guard 제거 시 registry smoke가 해당 runtime 경로 NullReferenceException으로 실패함을 확인했다. 원본 source는 변경하지 않았다. 원본 suite를 재실행한다.
- 원본 재검증: `scripts/smoke-csharp-registry.sh` 종료 0(독립 .NET smoke 1), `swift test --filter CBridgeTests` 종료 0(3건), Android `:sdk-core:test --tests BridgeDispatcherTest :sdk-unity-bridge:testDebugUnitTest` 종료 0(core 2건·bridge 6건). 일부 Gradle task는 up-to-date이며 실제 Unity Editor/JNI는 아니다.
- 커밋 전: disposable duplicate guard mutation 검사기와 정제 증거만 포함한다. R01~R12 전체·Unity scene/Domain Reload 및 stress 검증은 미완료로 P09-T02 PARTIAL 유지한다.

### [P09-T03] 인증·세션·개발모드 회귀
- Task 시작: server JWT/nonce·session rotation 및 sandbox dev endpoint 차단과 Native fake session 시험의 실제 실행 범위를 조사하고 분리 실행한다. 외부 Google/Apple 토큰 시험으로 취급하지 않는다.
- 3개 독립 인증 suite 실행: Backend opt-in sandbox PostgreSQL/HTTP 및 JWT fixture 8건, Android session/provider fake 13건, Swift fake 17건 모두 실패 0. Backend는 테스트 전용 RSA 키와 sandbox DB이며 실제 Google/Apple token이 아니다. sandbox dev-auth는 HTTP 404로 확인했고 fake identity token 직접 제출을 추가 확인한다.
- `GAMEBRIDGE_RUN_AUTH_DB_TESTS=true ... backend/gradlew -p backend test --tests AuthHttpIntegrationTest` 종료 0, sandbox test DB HTTP 1건: Mock identity 문자열 직접 제출 401, 개발 인증 route 404 및 동일 challenge의 정상 test-key 인증을 확인했다. 실제 외부 token은 아니다. 재현 가능한 분리 suite runner를 작성한다.
- `harness/run-auth-regression.py`을 명시적 전용 sandbox DB 설정으로 실행해 종료 0: test-key JWT 6건, sandbox HTTP/DB 2건, Android fake 13건, Swift fake 17건, skip 0. 실제 Google/Apple 검증은 포함하지 않는다. 결과 `artifacts/auth-regression-igvg0n7w/result.json`.
- DB URL에 credentials를 내장한 설정은 runner가 사용하지 않도록 했고, R13~R22의 후보 suite를 synthetic auth runner로 연결했다. DB 미설정 시 DEFERRED_ENV/exit 2를 확인한다.
- DB 환경값을 제거하고 `harness/run-auth-regression.py` 실행 시 JWT 6·Android 13·Swift 17은 실행됐으나 sandbox DB suite는 DEFERRED_ENV/0건, 전체 exit 2를 확인했다. 결과 `artifacts/auth-regression-iu23pa2v/result.json`; 누락을 성공으로 처리하지 않는다.
- 커밋 전: test-key sandbox HTTP fake-token 거부 assertion과 재현 가능한 인증 runner만 포함한다. 실 Google/Apple·모든 R13~R22 완전 coverage는 미검증으로 P09-T03 PARTIAL 유지한다.

### [P09-T04] 구매·DB 회귀
- Task 시작: 격리 PostgreSQL에서 중복 지급·계정 binding·finalization 및 Mock 응답 유실 복구를 실행하고 검증 범위를 분리한다. 실제 스토어 거래는 호출하지 않는다.
- 구매 원장 unique 불변식 시험을 추가했다. 매 실행마다 새 UUID schema를 만들고 opt-in mutation은 해당 새 schema의 constraint만 제거한다. 기존 schema·DB row는 지우거나 변경하지 않는다. 정상·손상·정상 순서로 검증한다.
- 격리 local-mock DB에서 `LedgerInvariantDatabaseTest` 정상 실행 종료 0, 1건: 같은 purchase의 두 번째 ledger insert를 DB가 거부했다. 생성된 새 schema는 보존했다. 이제 새 schema에 한정된 제약 제거 음성 시험을 수행한다.
- `GAMEBRIDGE_MUTATE_LEDGER_TEST=true ... LedgerInvariantDatabaseTest --rerun-tasks`는 의도대로 종료 1, 1건 실패. XML에서 예상한 “중복 insert가 예외 없이 성공” assertion 실패를 확인했다. mutation은 새 test schema 안에서만 수행했고 schema는 보존했다. 원본 설정으로 정상·관련 suite를 재실행한다.
- 정상 원복 후 격리 local DB 구매 suite 종료 0, 7건(skip 0): ledger invariant·Google/Apple grant·binding·finalization. Android fake 16건, Swift fake 6건 종료 0. 실제 Play/StoreKit은 아니다. 이어 sandbox test-key HTTP/DB fixture를 확인한다.
- sandbox test-key HTTP/DB `GooglePurchaseHttpIntegrationTest`·`ApplePurchaseHttpIntegrationTest` 종료 0, 2건(skip 0): synthetic verifier와 DB transaction 경로 확인. 실제 Play/Apple API가 아니다. 재현 가능한 구매 suite와 mutation 감지 runner를 작성한다.
- `harness/check-ledger-mutation.py` 종료 0: 새 test schema의 unique 제약 제거가 예상 assertion 실패로 검출됐고 별도 새 schema에서 정상 불변식을 재실행해 통과했다. 기존 schema는 수정·삭제하지 않았다.
- 구매 runner는 local-mock DB, sandbox test-key DB, Native fake, 명시적 local response-loss lane을 분리하고 누락/0건을 DEFERRED_ENV 또는 FAIL로 처리한다. 두 DB URL과 local server opt-in은 명시된 경우에만 사용한다.
- 구매 runner 재현 전 직접 기동한 local Backend의 주기 worker가 별도 DB worker 시험과 경쟁할 수 있음을 확인했다. 검증용 서버의 poll 간격만 임시로 늘려 테스트 간 간섭을 피하며, 제품 기본 정책은 변경하지 않는다.
- 명시적 test DB/local server 설정으로 `harness/run-purchase-regression.py` 종료 0: local PostgreSQL fixture 7, sandbox HTTP fixture 2, Android fake 16, Swift fake 6, Android/Swift 응답 유실 local DB 각 1건, skip 0. 결과 `artifacts/purchase-regression-sszt6cay/result.json`. 실제 스토어·Unity는 포함하지 않는다.
- DB/local server opt-in을 제거한 구매 runner는 Native fake 22건만 실행하고 DB·응답 유실 lane 4개를 DEFERRED_ENV/0건으로 표시해 전체 exit 2를 반환했다 (`artifacts/purchase-regression-zm5t9s81`). 직접 기동한 Backend만 종료하고 DB·생성 schema는 보존했다.
- `check-ledger-mutation.py`의 DB 설정 누락은 DEFERRED_ENV/exit 2로 확인했다. URL 내장 credentials는 사용하지 않으며 runner의 import로 생긴 이번 작업 전용 Python bytecode 1개만 제거했다(기존 `scripts/__pycache__` 보존).
- 커밋 전: 격리 ledger invariant/mutation, 구매 fixture runner 및 증거만 포함한다. Testcontainers, 실제 Play/Apple, 모든 R23~R39 완전 coverage는 미완료로 P09-T04 PARTIAL 유지한다.

### [P09-T05] Push·Lifecycle·패키징 회귀
- Task 시작: token·route·점검 fake, iOS host callback, staging checksum과 필수 binary 누락 음성 시험을 분리 실행한다. 실제 원격 알림 및 Unity player는 대기로 유지한다.
- push fake suite 실행: Backend 10건, Android core 3·Native 1·bridge 1건, Swift 8건 모두 종료 0/skip 0. 일부 Gradle build task는 up-to-date다. 실제 원격 전송은 아니며 iOS simulator host callback을 별도 확인한다.
- iOS 26.5 전용 simulator `PushHostTests` 실행 종료 0, xcresult에서 1건 통과/skip 0 확인: synthetic host callback·completion 경계다. 실제 APNs와 Unity player는 아니다. 산출물 누락 음성 시험을 구현한다.
- staging verifier에 checksum 전체 목록·경로·버전·sample·Maven·iOS slice 검사를 추가했다. 별도 fake 전용 디렉터리에서 Android/iOS binary 누락과 기존 출력 보존을 음성 시험한다. 실제 산출물은 삭제하지 않는다.
- `harness/check-staging.py artifacts/upm-staging-20261111-a` 종료 0: 110개 checksum·version·samples·Maven·iOS slice 확인. `harness/check-package-negative.py` 종료 0: 새 fake fixture의 Android/iOS binary 누락과 기존 output 덮어쓰기 거부를 확인했다. Unity import/export는 아니다.
- push/package runner는 fake·sandbox DB·iOS host simulator·staging을 분리하고 Mock delivery E2E 미구현과 Unity Player 미실행을 별도 비성공 상태로 항상 남긴다. 명시된 test 환경에서 실행한다.
- 명시적 sandbox test DB·iOS simulator·staging 설정으로 `harness/run-push-regression.py` 실행: Backend fake 10, sandbox fake HTTP 1, Android fake 5, Swift fake 8, iOS synthetic simulator 1, staging 1, package negative 1 통과. LOCAL_MOCK delivery E2E는 NOT_IMPLEMENTED, Unity player는 DEFERRED_ENV로 전체 exit 1. 결과 `artifacts/push-regression-33t3bvsw/result.json`. 실제 FCM/APNs는 실행하지 않았다.
- checksum inventory에서 root 이외의 같은 이름 파일까지 예외로 두지 않도록 좁혔다. staging 검사를 재확인한다.
- 수정 후 `check-staging.py` 110개 checksum, `check-package-negative.py`, `check-manifest.py` 모두 종료 0. 원격 전달이나 Unity import를 뜻하지 않는다.
- 커밋 전: push/package runner·staging 검증·격리 음성 fixture와 증거만 포함한다. 내부 Mock delivery 미구현 및 Unity/외부 대기는 유지한다.

### [P09-T06] fail-closed 전체 검증 집계
- Task 시작: 각 suite의 exit·실행 수·skip·환경 대기와 외부 대기를 분리하는 aggregate를 구현한다. P08 미완료, 기존 StoreKit 실패, 미구현 push E2E와 Unity 미실행을 성공으로 승격하지 않는다.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s harness -p test_aggregation.py -v` 종료 0, 8건: pass/failure/required skip/external 대기/0건/미구현/중복 lane 분리 확인. required lane 자체가 없는 경우도 실패시키도록 보강한다.
- 전체 runner 초안은 실제 suite별 결과 JSON과 실행 수를 수집하고, 미구현 scenario·Unity NOT_RUN·원장에 남은 실패를 별도 required lane으로 유지한다. 외부 WAITING_USER는 local PASS와 분리한다. 우선 unit 및 CLI 검증 후 실제 available 실행을 확인한다.
- 집계 분류 unit 9건 통과 및 CLI usage 확인. nested runner가 비정상 종료했는데 내부 보고서가 우연히 PASS인 경우도 실패로 처리하도록 보강한 뒤 실제 `--available`을 실행한다. DB opt-in은 제공하지 않아 해당 lane은 대기로 남아야 한다.
- 실제 `scripts/verify-all.sh --available` 종료 1, 결과 `artifacts/verify-all-02yt04zk`: Mock delivery NOT_IMPLEMENTED, Unity NOT_RUN, 기존 StoreKit 실패를 유지했고 DB opt-in 누락 lane은 DEFERRED_ENV, 외부 13개는 WAITING_USER로 분리했다. 집계 self-test의 실제 9건을 1개 check로 기록한 점과 nested report 불일치 검사를 보강한다.
- 집계 unit 재실행 종료 0, 11건: PASS/exit·failure 불일치, abnormal nested exit, 필수 lane 0건도 실패로 감지한다. 수정된 strict-local 실제 실행을 확인한다.
- aggregate 음성 검사 추가 수정 스크립트가 Python 문자열 구문 오류로 실행 전 실패했다. 이어 실행된 unit 11건은 수정 전 상태 검증이므로 새 기능 통과로 기록하지 않는다. 수정 스크립트를 단순화해 다시 적용한다.
- 음성 검사 포함 최종 `scripts/verify-all.sh --strict-local` 종료 1, `artifacts/verify-all-nxzojdaf/result.json`: manifest/contract negative 통과, DB 미설정 및 ledger mutation은 DEFERRED_ENV, Mock delivery NOT_IMPLEMENTED·Unity NOT_RUN·기록된 StoreKit FAIL과 외부 WAITING_USER 13개를 분리했다. aggregation self-test 실제 11건을 기록했다.
- 커밋 전: fail-closed aggregate와 unit/실제 실행 증거만 포함한다. 모든 required lane이 실행된 것은 아니므로 P09-T06은 PARTIAL 유지한다.

### [P09-T07] CI 플랫폼 lane
- Task 시작: PR에서 외부 인증·secret 없이 Linux Backend/Android, macOS Swift, 별도 Unity 대기를 구분하는 workflow를 작성한다. GitHub push/실행은 하지 않으며 로컬 정적 검증만 기록한다.
- CI 준비용 DB script는 loopback·명시적 disposable 접두사·빈 public schema를 요구하고 migration만 적용하며 기존 DB를 삭제하지 않는다. required scenario coverage 미완료는 별도 gate에서 실패시킨다.
- 전용 새 DB `gamebridge_ci_060e9d3bdae7`에서 CI 준비 script 종료 0, ledger/finalization DB 시험 3건 종료 0. 같은 DB 재실행은 비어 있지 않음을 감지해 exit 2로 거부했다. DB와 새 schema는 보존한다.
- 공식 GitHub Actions 문서·runner image 및 고정 checkout/setup-java commit, XcodeGen 2.46.0 release SHA256을 확인했다. Linux Backend/Android, macOS simulator, 명시적 미구현 Unity lane과 fail-closed gate workflow를 작성했다. 원격 workflow는 실행하지 않는다.
- actionlint 1.7.12 공식 release 다운로드 첫 시도는 connection reset으로 실패했다. 뒤따른 checksum/추출 명령도 파일 부재로 실패했으며 workflow static 검증은 아직 미실행이다. 새 경로에서 다운로드 재시도한다.
- actionlint 1.7.12은 첫 download connection reset 후 새 로컬 경로에 재시도해 공식 SHA256 일치·workflow static 검증 종료 0. GitHub Actions는 실행하지 않았다. Swift test의 0건 및 필수 class 누락을 CI에서 놓치지 않도록 추가 검사를 작성한다.
- actionlint 재실행 종료 0. CI DB 보호 검사를 table뿐 아니라 view/sequence/function까지 확장했고 기존 test DB 재실행은 exit 2로 거부했다. Swift 및 JUnit 실행 수 검사기의 양·음성 경계를 확인한다.
- CI Swift 선택 suite 12건/필수 class 5개를 실제 실행·검사했고, 존재하지 않는 class 및 없는 JUnit XML은 각 exit 1로 거부했다. XcodeGen 공식 archive SHA256 검증 후 로컬 실행 버전 2.46.0을 확인했다. GitHub 원격 실행은 하지 않았다.
- 강화된 빈 DB 확인은 새 `gamebridge_ci_d67cc2b8fd70`에서 migration 적용에 성공했다. 그러나 이어진 Gradle test가 DB URL 변경을 입력으로 인식하지 못해 UP-TO-DATE였으므로 그 DB에서 시험 통과라고 기록하지 않는다. CI test 명령에 --rerun-tasks를 추가하고 같은 DB에서 실제 실행한다.
- `--rerun-tasks`로 새 CI test DB에서 ledger/finalization 3건을 실제 재실행하고 JUnit 3건·skip 0을 확인했다. 변경 후 actionlint 1.7.12 재검증 종료 0. 기존 DB·새 test DB는 보존했다. GitHub 원격 workflow는 실행하지 않았다.
- 커밋 전: CI workflow·disposable DB 준비·0건/skip 방지 검사와 로컬 정적/대응 검증만 포함한다. Unity lane은 명시적 NOT_IMPLEMENTED로 실패하며 remote Actions 결과는 NOT_RUN이다.

### [P09-T08] 하네스 fail-closed 자체 시험
- Task 시작: 새 격리 fixture에서 문서 누락, 실패·0건, 필수 시나리오 누락, Native binary 누락, sandbox fake token 거부를 검증한다. 원본 제품 소스와 기존 산출물은 변조하지 않는다.
- 진행 원장 검사기를 대조한 결과 PASS의 evidence 문자열 존재만 검사하고 실제 파일 부재와 집계 숫자 불일치를 놓친다. P09-T06/08 요구에 맞춰 evidence 경로·WORK_LOG anchor·분모/상태 집계를 검증하고 격리 문서에서 음성 시험한다.
- 강화한 `scripts/verify-progress.py`는 현재 원장에서 종료 0. `harness/check-progress-negative.py`는 새 복사본에서 USER_SETUP 누락·증거 파일 부재·구현 집계 조작을 각각 거부했으며 원본은 보존했다.
- 자체 검사 runner는 격리 문서·manifest·binary·fixture 및 중복/원장 mutation, 실패/0건, 명시적 sandbox test-key HTTP, 원본 contract 재실행을 각각 집계한다. DB/Unity 도구가 없으면 성공으로 처리하지 않는다.
- `harness/run-self-check.py` 명시적 전용 DB/Unity 참조 설정으로 종료 0: progress·manifest·binary·fixture 음성 시험, bridge/ledger mutation, 실패/0건 3검사, sandbox fake token 거부, 원본 계약 재실행을 각각 확인했다. 결과 `artifacts/harness-self-ogtz_a87/result.json`. 제품 전체 완료를 뜻하지 않는다. 필수 suite 자체 제거도 별도로 감지하도록 보강한다.
- 격리 manifest에서 required suite 자체를 제거해도 검사기가 nonzero를 반환하도록 음성 시험을 추가했다. 원장의 증거 경로가 repo 밖 symlink를 가리키거나 상태 집계 key가 중복되는 경우도 거부하도록 보강했고 기존 문서 및 격리 음성 검사 재실행 종료 0이다. 전체 self-check를 다시 실행한다.
- manifest에서 coverage를 IMPLEMENTED로 바꾸기만 해 gate를 우회하지 못하도록 구체 test file·test case·suite·evidence mapping을 요구하고, 이를 생략한 격리 mutation의 실패를 추가 검증한다. R50은 self-check 일부 구현이므로 NOT_IMPLEMENTED에서 PARTIAL로만 조정한다.
- 구현 완료 표기는 존재하는 구체 test/assertion/evidence mapping 없이는 manifest 검사에서 거부된다. 진행 원장 격리 음성 시험에도 repo 밖 evidence symlink와 중복 집계 key를 추가했다. 전체 self-check를 재실행한다.
- `harness/run-self-check.py` 최종 재실행 종료 0: 문서·evidence·symlink·집계, scenario/suite 제거·근거 없는 완료 표기, binary 누락, contract/bridge/ledger mutation, 실패/0건, sandbox fake token, 정상 contract 재실행을 각각 확인했다. 결과 `artifacts/harness-self-rd_ntb9t/result.json`. 전체 제품 strict-local은 여전히 FAIL이며 self-check PASS와 다르다.
- 커밋 전: 진행 원장 검사 강화 및 격리 self-check만 포함한다. Unity/runtime·미구현 delivery 및 모든 required suite 정상 재실행은 미완료로 P09-T08 PARTIAL 유지한다.

### [P10-T01] Bridge 소규모 리팩토링
- Task 시작: P09 전체 gate가 미완료임을 유지하며 독립적으로 검증 가능한 Unity push 이벤트 queue 중복 분기를 정리한다. P08 snapshot과 공개 API source 형태를 비교하고 callback/session 동작을 재검증한다.
- P08 snapshot hash를 검증하고 C# public 선언과 나머지 보존 snapshot을 비교하는 보수적인 source 검사기를 추가했다. binary ABI나 Unity 호환성 성공을 주장하지 않는다. 변경 전 기준을 확인한다.
- 변경 전 `python3 harness/check-api-baseline.py` 종료 0: snapshot 13개 hash와 C# public 선언·나머지 원본 바이트 일치. Unity PushUpdated/PushTokenUpdated의 동일 queue 분기를 하나의 private 메서드로 정리한다.
- private push queue 분리 후 `check-api-baseline.py` 및 C# registry smoke 종료 0. 초기화 중 알림 queue와 session 분기 회귀를 독립 .NET에서 확인했다. 공개 선언 변경 음성 시험과 Unity 참조 compile을 실행한다.
- `harness/check-api-baseline-negative.py` 종료 0: 새 소스 사본의 public event 이름 변경을 검출했다. `scripts/check-csharp-compile.sh` 4조건부 및 `scripts/check-unity-ios-host.sh` 공식 참조 compile 종료 0/경고 0. Unity 실행·binary ABI 검증은 아니다.
- aggregate에 API snapshot 양·음성 검사를 추가했다. 커밋 전: Unity private queue 정리와 source 호환성/fake 검증만 포함하며 전체 P09 gate·Unity ABI·runtime은 미완료다.

### [P10-T02] Unity 로그아웃 오류 경계
- Task 시작: Native는 오프라인 logout에서 local token 삭제 후 `REVOCATION_UNCONFIRMED`를 반환하지만 Unity registry가 nativeCode를 모두 버려 이 상태가 사라진다. 비밀정보를 노출하지 않는 allowlist 값만 보존하고 기존 공개 생성자를 유지한다.
- BUG-012: Unity가 Native 오류의 revoke 미확인 정보를 버리고 있어 로컬 logout 이후 서버 상태를 구분할 수 없다. auth.signOut에 한해 `REVOCATION_UNCONFIRMED`만 허용하고 다른 native 문자열은 계속 제거한다. P08 snapshot에 누락된 public SdkException 선언을 원래 기준 commit에서 보충한다.
- 기존 SdkException 생성자를 유지하고 logout의 허용된 revoke 미확인 코드만 추가 공개했다. 원본 P08 commit의 누락된 exception 선언 snapshot을 보충했으며 additive C# 선언을 허용하되 기존 선언 제거·변경은 감지한다. fake logout/redaction과 API 호환성을 검증한다.
- `check-api-baseline.py`·isolated public API mutation 검사 및 C# registry smoke 종료 0: logout의 REVOCATION_UNCONFIRMED는 보존하고 임의 token 문자열은 제거했다. 실제 오프라인 Unity 기기 logout은 아니다. Native fake와 sample compile을 재검증한다.
- Android Native auth fake 13건, Swift auth/session fake 17건, `scripts/check-unity-sample.sh` Editor/iOS 조건부 compile 모두 종료 0. 실제 오프라인 Unity 기기 logout은 미검증이다.
- 커밋 전: 기존 SdkException 생성자를 보존하는 additive 필드, logout 한정 allowlist 및 sample 표시만 포함한다. arbitrary native 문자열은 계속 비노출이며 전체 P10/security 검증은 미완료다.

### [P10-T03] 로컬 lifecycle 측정
- Task 시작: 계획의 100회 초기화·종료를 독립 .NET EditorOffline fake에서 측정하고 정리 상태를 확인한다. Unity Editor/실기기 latency나 누수 profile로 일반화하지 않는다.
- 독립 .NET stress는 warm-up 5회와 실제 100회에서 fake 초기화·상품 조회·종료 및 pending 정리를 확인하고 p50/p95를 기록한다. 실행 환경과 실제 Unity/기기 미측정 한계를 함께 남긴다.
- 첫 stress 실행은 종료 0이나 측정 코드가 client 생성 뒤 stopwatch를 시작하면서 결과 설명에 create를 포함했다. 첫 수치(100회 p50 0.1475ms/p95 0.1907ms)는 생성 제외 측정으로 보존하고, 시작 시점을 생성 앞으로 수정해 새 output에서 재측정한다.
- 생성 시점 수정 후 `scripts/stress-csharp-lifecycle.sh` 종료 0: macOS Darwin 25.5 arm64, .NET 8.0.21 Release, warm-up 5·sample 100에서 fake create/init/product query/shutdown p50 0.1467ms, p95 0.2125ms; 매 회차 pending 0 확인. 결과 `artifacts/lifecycle-stress.zrf6NN/result.json`. dispose 시간은 측정에 포함하지 않으며 Unity/실기기/메모리 측정이 아니다.
- 커밋 전: 독립 fake 측정 코드와 증거만 포함한다. Unity scene 교체·기기 profiling·누수 측정은 NOT_RUN으로 P10-T03 PARTIAL 유지한다.

### [P10-T04] 리팩토링 후 재패키징
- Task 시작: 기존 P08 binary를 재사용하지 않고 현재 source에서 Android Maven과 iOS device/simulator XCFramework를 각각 새 경로에 다시 생성한다. 이전 산출물과 사용자 파일은 보존한다.
- 첫 P10 Android Maven/R8 빌드는 종료 0이지만 여러 Native 산출 task가 UP-TO-DATE였다. 계획의 리팩토링 후 재패키징은 이전 binary 재사용을 허용하지 않으므로 이것을 최종 재빌드 증거로 쓰지 않고 --rerun-tasks를 적용해 새 경로에서 재실행한다. iOS는 새 격리 Xcode project에서 device/simulator archive 및 XCFramework 생성 종료 0.
- `GAMEBRIDGE_MAVEN_REPO=.../maven-p10-20261111-b bash scripts/build-android.sh --mock` 종료 0: --rerun-tasks로 Native publish 및 별도 R8 consumer 재실행(consumer 45개 task 실행). 새 iOS XCFramework도 생성됐다. Swift 별도 소비 link·UPM staging을 확인한다.
- 새 iOS XCFramework의 device C ABI 네 symbol과 별도 simulator Swift consumer link 종료 0. 새 Android/iOS 산출물로 UPM staging 110개 checksum 및 baseline source 비교 종료 0. 기존 C# 공개 생성자·메서드 소비 fixture를 별도 assembly에 대해 컴파일한다.
- `scripts/check-csharp-compat.sh` 종료 0: 별도로 빌드된 GameBridge.Runtime assembly을 참조하여 P08 기준 생성자·메서드 consumer source를 컴파일·실행했다. 이는 binary ABI 또는 Unity Editor 실행을 증명하지 않는다.
- 커밋 전: Android 강제 재빌드 script, 과거 C# 소비자 fixture 및 P10 산출물 evidence만 포함한다. Unity clean consumer/IL2CPP·실기기와 전체 기능 gate는 미완료다.

### [P11-T01] 전체 누락·실패 감사
- Task 시작: 64개 원장 행, 구현·로컬·실연동 집계, source의 미지원·TODO와 evidence 경로를 대조한다. 미구현을 사용자 설정 대기로 바꾸지 않으며 발견 즉시 기록하고 독립 수정은 계속한다.
- 감사에서 내부 누락 BUG-013(XCODE_STOREKIT 지급/Unity 경로), BUG-014(LOCAL_MOCK push Backend→client delivery), BUG-015(Native diagnostics 공개 연결)를 별도 OPEN으로 등록했다. 환경 문제나 사용자 credential 부족으로 바꾸지 않는다.

### P11-T01 검증 및 커밋 준비
- 전체 64개 계획 Task와 진행 원장 ID를 대조하고 추적 중인 소스의 미구현 표식을 검사했다. `python3 harness/audit-ledger.py` 통과, 결과 `artifacts/ledger-audit-enavuhuo/audit.json`: OPEN 7건, 소스 표식 0건. 텍스트 검색만으로 구현 완전성을 증명하지 않으며 미추적 사용자 파일은 검사하지 않았다.
- 결제·푸시·Unity 등의 부분 검증과 내부 누락을 최종 요약에 반영했다. 전체 판정은 BLOCKED_INTERNAL이며 Task는 PARTIAL로 유지한다.
- 커밋 예정: 감사 도구와 원장; 실제 플랫폼 및 Unity는 검증하지 않았다.

### [P11-T02] 시작
- 사용자 설정 문서의 오래된 구현 상태를 소스 및 검증 기록과 대조하고, 비밀값을 노출하지 않는 설정 준비 검사 경로를 구현한다. 실제 외부 서비스 호출은 실행하지 않는다.

### P11-T02 검증 시작
- `verify-external --check-config`의 누락 설정 종료 코드 및 값 비노출을 확인하고 synthetic 설정으로 형식 검사와 실패 조건을 확인한다. 이는 실제 자격증명 유효성 또는 서비스 연결 검증이 아니다.

- 원장 검증 최초 실행에서 P11-T02 로그 표식 형식 누락으로 실패했다. 표식을 수정한 뒤 재검증한다.
- 합성 설정 전체 및 빈 audience 실패 조건과 비밀값·경로 비출력 확인 통과. 실제 외부 호출 NOT_RUN. 원장 검증 재실행 통과.
- 커밋 준비: 설정 형태 검사와 현행 설명만 포함하며 실연동 runbook 및 실제 검증은 PARTIAL로 유지한다.

### [P11-T03] 시작
- 이미 생성·검증한 Android, iOS, UPM 산출물을 보존하고 실제 빌드 소스와 checksum을 연결한다. 미검증 기능과 내부 블로커를 최종 보고에 명시한다.
- 산출물 파일별 SHA-256 manifest 및 최종 보고 초안을 작성했다. P10 빌드 당시 작업 트리가 깨끗하지 않았다는 제한을 명시했다.
### P11-T03 검증 시작
- 산출물 manifest의 모든 파일을 재계산하고 원장 및 문서 변경을 확인한다. 이는 Unity import나 실제 플랫폼 검증을 대체하지 않는다.
- manifest의 192개 파일 크기 및 SHA-256 재계산과 원장 검증 통과. 산출물은 로컬에만 있고 소스 기준은 빌드 당시 변경을 포함한다.
- 커밋 준비: 최종 보고 초안과 checksum manifest를 저장한다. 재현 빌드·Unity 설치·미완성 기능이 남아 P11-T03은 PARTIAL이다.

### [P11-T04] 시작 및 검증 준비
- strict-local 집계, 원장 검사와 diff 검사를 실행한다. 미구현 시나리오·Unity 미실행·기존 StoreKit 실패는 성공으로 바꾸지 않는다.
- `bash scripts/verify-all.sh --strict-local` 종료 1, `artifacts/verify-all-g_lqddbb/summary.md`: Kotlin/Swift contract, 여러 Native fake 및 부정 시험 통과; DB 등 opt-in 환경과 일부 도구는 DEFERRED_ENV, Mock push 전달·시나리오 미구현, Unity NOT_RUN, 기존 StoreKit 실패로 전체 FAIL. 외부 13개 WAITING_USER. `git diff --check` 통과.
- 커밋 준비: 실패 및 미실행을 그대로 보존하고 다음 내부 누락 수정을 계속한다.

### [P07-T01] BUG-015 재개
- Native typed 진단 ring과 Unity 공개 경계의 연결을 조사한다. payload·토큰을 노출하지 않는 구조화된 정보만 대상으로 구현 및 검증하며 기존 공개 API 호환성을 유지한다.
- Android bridge dispatcher에 요청 payload를 보관하지 않는 typed 진단 event 기록과 diagnostics.get snapshot을 연결했다. iOS 및 Unity 공개 경계는 아직 미연결이다.
### P07-T01 BUG-015 Android 검증 시작
- 기존 dispatcher 회귀 및 200개 제한·예외 비밀값 비노출 시험을 실행한다. Native 단위 검증으로 Unity 실행을 대체하지 않는다.
- Android `:sdk-core:test --tests com.gamebridge.BridgeDispatcherTest --rerun-tasks` 종료 0, 기존 dispatcher와 신규 200개 ring·민감 문자열 비노출 확인. `harness/check-api-baseline.py` 통과. 실제 Unity 및 iOS는 아직 미검증.
- 커밋 준비: Android 경계의 독립 부분만 기록하고 BUG-015 OPEN 유지한다.
### P07-T01 BUG-015 iOS 연결 시작
- iOS C ABI dispatcher에도 동일한 typed event와 snapshot을 연결하고 C bridge 시험을 추가한다. 실제 Unity player 검증은 별도다.
### P07-T01 BUG-015 iOS 검증 시작
- Swift C bridge 회귀 및 민감 payload 비반환 시험을 실행한다. simulator/device와 Unity 실행 결과는 포함하지 않는다.
- 검토 중 세션 종료 뒤 다른 사용자가 이전 request ID를 조회할 가능성을 발견했다. READY 세션에서만 snapshot을 허용하고 신규 소유 세션 시작 시 ring을 비우도록 두 플랫폼에 보강한다. 검증 전까지 BUG-015 OPEN이다.
### P07-T01 세션 격리 검증 시작
- Android dispatcher 및 Swift C bridge 시험을 다시 실행한다.
- 세션 격리 추가 시험의 첫 실행은 실패했다. 테스트 fake가 shutdown에서도 예외를 발생시켜 종료 상태가 되지 않은 원인을 확인했으며, fake의 정상 shutdown을 명시한 뒤 재실행한다. Swift 시험은 앞선 명령 실패로 이번 조합에서 미실행이다.
- fake 수정 후 Android dispatcher 3건과 Swift C bridge 3건 통과. 두 플랫폼에서 종료 후 조회 차단 및 새 세션 ring 초기화를 확인했다. 실제 Unity는 미실행.
- 커밋 준비: iOS 연결과 Android/iOS 세션 격리만 포함하며 Unity 공개 API가 남아 BUG-015는 OPEN이다.
### P07-T01 BUG-015 Unity 경계 시작
- 기존 동기 진단 API를 유지하면서 Native typed events의 별도 비동기 조회를 추가한다. 허용 enum·UUID·시각만 수용하고 범위를 벗어난 응답은 오류 처리한다.
### P07-T01 BUG-015 Unity 검증 시작
- 네 조건부 managed compile과 독립 .NET fake 경계를 실행한다. Unity Editor 및 실제 Native 연동은 라이선스 문제로 별도 미실행이다.
- 네 조건부 compile은 통과했으나 Editor fake에서 사용하지 않는 필드 경고가 1건 발생했다. fake 응답의 기존 상태 필드를 보존하고 숫자 문자열 enum도 거부하도록 보강한 뒤 재검증한다.
- Native typed event 조회, 200개 상한, UUID·enum 검증, offline 빈 목록 및 숫자 enum 거부를 독립 .NET fake로 확인했다. 네 조건부 managed compile과 API baseline 비교 통과. Unity player 실제 Native 경계는 ENV-002로 미실행이므로 BUG-015 OPEN 유지.
- 커밋 준비: Unity 공개 비동기 조회와 fake 시험. 기존 P10 패키지는 이 변경 이전이므로 재패키징 필요.

### [P08-T01] [P08-T02] [P08-T03] 진단 변경 후 재패키징 시작 및 검증 준비
- 52f60f7 소스 기준 새 Android Maven/R8 consumer와 iOS XCFramework, UPM staging을 생성한다. 이전 산출물은 보존하며 Unity import는 미실행으로 유지한다.
- 사용자가 LOCAL_MOCK push는 앱 연결 중에만 전달하고 미연결 시 버리도록 결정했다. 실제 FCM/APNs에는 적용하지 않는다. 구현은 아직 시작 전이며 `docs/DECISIONS.md`에 기록했다.
- Android Maven 강제 재빌드 및 별도 R8 consumer 45개 task 실행 성공, iOS device/simulator XCFramework archive 성공, 새 UPM staging checksum 전체 통과. Unity import 및 새 iOS 독립 consumer 실행은 미검증이다.
- 커밋 준비: 산출물 SHA-256 manifest, 사용자 푸시 정책 및 검증 증거만 기록한다. 기존 산출물과 미추적 사용자 파일은 보존한다.

### [P06-T05] BUG-014 전달 구현 시작
- 사용자가 승인한 LOCAL_MOCK 연결 중 전달·미연결 폐기 정책으로 서버의 연결 기반 전송부터 구현한다. 실제 FCM/APNs 경로와 분리하고 인증·installation 소유권 및 로그아웃 후 차단을 유지한다. Native와 Unity 연결 및 E2E 전까지 미완료다.
### P06-T05 연결 기반 broker 검증 시작
- 메시지를 저장하지 않는 LOCAL_MOCK broker의 사용자·앱·installation 분리 및 미연결 폐기, 실패 구독 정리를 단위 시험한다. 서버 HTTP와 Native 수신 연결은 아직 없다.
- `backend/gradlew -p backend test --tests com.gamebridge.push.MockPushBrokerTest --rerun-tasks` 종료 0: 2건 통과. 기존 Jackson/FCM deprecation 경고가 출력됐다. HTTP/Native 수신 미구현으로 BUG-014 OPEN.
- 커밋 준비: 사용자가 승인한 무보관 broker 및 단위 시험만 저장하고 나머지 경로를 계속 연결한다.
### P06-T05 LOCAL_MOCK HTTP 구독 시작
- 인증된 세션과 해당 세션 소유 installation을 확인하는 연결 전용 스트림을 추가한다. 전달 직전 세션 및 등록 상태를 재확인하며 오프라인 메시지는 보관하지 않는다. 별도 서버·클라이언트 통합 시험 전까지 미완료다.
### P06-T05 HTTP 구독 검증 시작
- 우선 서버 컴파일과 broker 단위 시험을 실행한다. 실제 HTTP 인증·소유권·logout 경쟁 및 Native 수신은 별도 시험이 남았다.
- 서버 compile과 broker 단위 시험 통과. 구독 등록과 연결 종료가 동시에 일어날 때 dangling 구독이 남을 수 있는 경합을 발견해 종료 flag로 보강했다. 실제 HTTP 및 Native 수신은 아직 미검증이다.
### P06-T05 HTTP 통합 시험 준비
- 전용 빈 DB에서 실제 HTTP 연결의 소유권 거부와 연결된 세션의 수신 및 title/body 비노출을 검증한다. 비밀정보는 출력하지 않고 기존 DB·volume은 보존한다.
- 첫 HTTP 통합 시험 실패: 다른 사용자 구독이 기대 403 대신 500을 반환했고 `HttpMediaTypeNotAcceptableException`이 기록됐다. SSE 요청의 Accept 협상과 오류 응답을 수정한 뒤 재시험한다. 전용 DB `gamebridge_ci_e34ff4020a`는 보존한다.
- Accept에 SSE와 JSON을 명시한 재시험에서 소유권 거부와 연결 수신 시험은 통과했으나, 클라이언트 종료 뒤 서버 graceful shutdown이 30초 제한까지 대기했다. 끊긴 연결의 heartbeat 정리 및 서버 종료 시 구독 정리가 필요하며, heartbeat 간격은 사용자에게 확인 중이다. 명시 Accept 없는 첫 실패도 수정·재검증 전까지 OPEN이다.
### P06-T05 스트림 종료·협상 재검증 시작
- 서버 종료 시 연결을 완료하도록 하고 SSE error 협상을 재시험한다. heartbeat 동작은 사용자 결정 전 미구현이다.
- `produces` 강제를 제거한 뒤 Accept 미지정 요청의 403과 연결 수신 시험은 통과했다. 서버 종료 시 `@PreDestroy`가 graceful shutdown보다 늦게 호출되어 30초 대기 문제는 재현됐다. lifecycle 종료 순서를 보강한다.
### P06-T05 lifecycle 종료 검증 시작
- 별도 빈 DB에서 같은 HTTP 통합 시험을 재실행해 서버 graceful shutdown을 확인한다. heartbeat 및 Native 수신은 아직 미구현이다.
- 전용 DB `gamebridge_ci_ac6dcaa892`의 HTTP 시험에서 타 사용자 403·연결 수신·title/body 비노출이 통과했고 graceful shutdown이 즉시 완료됐다. DB는 보존한다. Native 수신·재연결과 heartbeat는 미구현이다.
- 커밋 준비: local 전용 인증 스트림과 HTTP 시험을 저장한다. 사용자 선택 전 heartbeat 정책을 확정하지 않으며 BUG-014 OPEN이다.
### P06-T05 세션 변경 시 전달 차단 검증 시작
- 기존 연결이 logout 뒤 새 세션의 동일 installation 메시지를 수신하지 않는지 전용 DB HTTP 시험으로 확인한다. heartbeat와 클라이언트 수신은 아직 미구현이다.
- 세션 변경 시험 첫 실행 실패: logout의 실제 성공 HTTP 상태는 200인데 시험에서 204를 기대했다. 기존 endpoint 계약에 맞춰 시험 기대값을 수정하고 재실행한다. 전용 DB `gamebridge_ci_ef603351fa` 보존.
- 재시험에서 구 세션 스트림은 새 메시지를 보내지 않고 닫혔지만 Java HTTP client가 정상 EOF 대신 연결 EOFException을 보고해 assertion이 실패했다. 연결 종료와 메시지 미전달을 별도로 확인하도록 시험을 보정한다. 전용 DB `gamebridge_ci_512a1dba1e` 보존.
- 전용 DB `gamebridge_ci_faeb266f16` 재시험 통과: logout·동일 사용자 새 세션 재등록 뒤 기존 연결에는 새 메시지가 전달되지 않고 연결 종료됨을 확인했다. 서버 종료도 정상이다. heartbeat·Native 수신은 미완료다.
- 커밋 준비: 세션 소유권 회귀 시험만 추가한다. BUG-014 OPEN 유지.
### P06-T05 Native Mock 이벤트 입력 검증 시작
- 연결 확인 주기 결정과 독립적으로 서버 이벤트를 Native의 허용된 messageId·route·campaignId로 변환하는 경계를 구현한다. 임의 payload와 URL route는 전달하지 않는다. 스트림 연결 및 Unity 이벤트 연결은 아직 없다.
### P06-T05 Native decoder 검증 시작
- Android에서 허용 필드·route, 크기, UTF-8 및 타입 오류 거부를 단위 시험한다. 실제 스트림 및 Unity player 검증은 포함하지 않는다.
- 사용자가 LOCAL_MOCK 연결 확인 30초를 선택했고 이후 질문 없이 권장안을 선택해 진행하도록 명시했다. 결정을 `docs/DECISIONS.md`에 기록한다.
### P06-T05 양 플랫폼 decoder 재검증 시작
- 기존 bridge의 256 KiB 상한을 재사용하고 Android·Swift에서 같은 허용 필드와 오류 거부를 검증한다.
- Android 및 Swift decoder 단위 시험 통과: 허용 route·필드만 반환하고 UTF-8/크기/타입 오류를 거부한다. 기존 256 KiB bridge 상한을 재사용한다. Native 스트림 연결은 미구현이다.
- 커밋 준비: 사용자 승인 정책과 Native 입력 검증만 저장하고 30초 연결 확인 및 클라이언트 연결을 이어간다.
### P06-T05 30초 연결 확인 구현 시작
- 사용자가 선택한 30초 기본 주기로 LOCAL_MOCK 스트림의 소유권과 연결을 확인하고 실패 시 구독을 정리한다. 종료 시 scheduler도 정리하며 실제 원격 푸시에는 적용하지 않는다.
### P06-T05 heartbeat 검증 시작
- 기본 30초 설정과 scheduler·종료 컴파일, 기존 broker 및 HTTP 시험을 재검증한다. 실제 기다림 없이 테스트 설정을 주입한 연결 해제 검증은 다음에 추가한다.
- 서버 컴파일 및 broker 단위 시험 통과. 테스트에서만 heartbeat를 1초로 주입하여 실제 연결 종료 감지·구독 정리를 확인한다. 운영 기본은 사용자 선택 30초다.
- 전용 DB `gamebridge_ci_115d8aa8cc`에서 시험용 1초 설정으로 heartbeat 수신 후 끊긴 연결 구독 제거 통과. 서버 기본은 30초. 테스트 간 관리자 key rate limit이 공유되지 않도록 각 시험 후 context를 분리한다.
### P06-T05 전체 HTTP 회귀 검증 시작
- 동일 테스트 클래스의 기존 속도 제한·소유권 시험과 신규 스트림 및 heartbeat를 함께 실행한다.
- 전용 DB `gamebridge_ci_63c66d6f09`에서 기존 제한·소유권 및 신규 stream·heartbeat HTTP 시험 전체 통과. 테스트 DB는 보존한다. Native 연결 및 전체 E2E는 미구현이다.
- 커밋 준비: 30초 기본 heartbeat, 설정, 연결 정리 및 회귀 시험만 포함한다. BUG-014는 OPEN이다.
### P06-T05 Android 스트림 transport 시작
- 위임된 권장안으로 LOCAL_MOCK 연결 재시도 5초부터 최대 60초 지수 백오프를 결정해 DECISIONS에 기록했다. 등록 해제·로그아웃·종료에서 스트림을 중단하며 서버 이벤트는 검증된 허용 필드만 전달한다. 먼저 독립 transport와 fake HTTP 시험을 구현한다.
### P06-T05 Android transport 검증 시작
- 합성 HTTP 서버에서 인증 header·installation 경계, heartbeat 무시 및 안전한 이벤트 변환을 확인한다. 실제 Backend·Unity와 등록 수명주기는 아직 연결하지 않았다.
- `:sdk-core:test --tests com.gamebridge.MockPushStreamTest --rerun-tasks` 통과: synthetic HTTP에서 인증 header, installation query 및 heartbeat 무시·허용 payload 전달을 확인했다. 실제 Backend/등록·종료 수명주기는 미연결이다.
- 커밋 준비: 독립 Android transport와 fake HTTP 시험 및 위임된 재시도 결정을 저장한다. BUG-014 OPEN 유지.
### P06-T05 Android Mock 수명주기 연결 시작
- 등록 성공 후 스트림을 시작하고 토큰은 Native에만 유지한다. 로그아웃·등록 해제·재로그인·종료 시 스트림을 중단하며 Unity 전달은 기존 session/epoch 가드와 route 검증을 사용한다. 실 DB E2E 전까지 미완료다.
### P06-T05 Android 연결 compile·회귀 검증 시작
- Native core 및 Unity Android bridge를 빌드하고 기존 fake 회귀를 실행한다. 실제 local Backend→Unity 전달은 별도로 검증한다.
- Android core 全 unit、Unity bridge unit 및 AAR compile 강제 재실행 통과. SDK XML 버전 경고는 있으나 빌드 성공. 실제 Backend/Unity player 검증은 아직 아니다.
### P06-T05 Android 수명주기 fake 검증 시작
- 등록 후 수신과 logout 시 중단을 합성 HTTP에서 검증한다.
- 합성 HTTP에서 Native 등록→안전 이벤트→로그아웃 시험 통과. 다만 응답을 바로 닫는 서버였으므로 열린 연결에서 logout이 막히지 않는 별도 시험을 추가한다.
- 열린 스트림에서 logout 완료가 2초 내 반환되지 않아 시험 실패했다. `HttpURLConnection.disconnect()`가 읽기 중인 연결에서 호출 스레드를 막는 것으로 확인되어 취소 경계를 분리하고 재시험한다. 미해결 동안 Android 경로는 완료로 기록하지 않는다.
- disconnect를 별도 daemon에서 처리하고 취소 이후 새 연결을 만들지 않도록 검사해 열린 연결에서 logout이 2초 내 반환되는 fake 회귀가 통과했다. 읽기 연결의 비동기 정리 지연은 timeout으로 제한하며 실제 기기 수명주기 검증은 남았다.
### P06-T05 Android 브리지 재검증 시작
- core/bridge 단위 시험 및 compile을 강제 재실행한다.
- Android core 전체 및 bridge unit·AAR compile 48개 task 강제 재실행 통과. fake HTTP에서 열린 연결 logout 지연 회귀 확인. 실 Backend/Unity player는 미검증이다.
- 커밋 준비: Android 등록·session epoch 가드·종료 수명주기를 저장한다. iOS 및 실제 local E2E가 남아 BUG-014 OPEN 유지.
### P06-T05 iOS 스트림 transport 시작
- 승인된 연결 확인·재시도 정책을 iOS LOCAL_MOCK에도 적용한다. redirect 거부, bounded UTF-8 SSE 파싱과 token 비노출을 유지한다. 먼저 parser 및 transport를 구현한다.
### P06-T05 iOS transport 검증 시작
- Swift package compile 및 incremental SSE parser fake 시험을 실행한다. 실제 URLSession 스트림과 Native lifecycle은 아직 미검증이다.
- Swift incremental parser 단위 시험 통과. URLSession 테스트 설정 주입을 추가해 합성 인증 응답의 실제 AsyncBytes 경계를 확인한다.
- Swift SSE parser와 `URLProtocol` 합성 인증 응답을 사용한 실제 URLSession AsyncBytes 시험 통과. iOS simulator/device·서버 및 Unity 경계는 미검증이다.
- 커밋 준비: 독립 iOS transport와 fake 시험만 저장한다. 등록 수명주기 및 E2E가 남아 BUG-014 OPEN이다.
### P06-T05 iOS Mock 수명주기 연결 시작
- 등록 성공 후 Native 소유 토큰으로 스트림을 시작하고 계정 epoch 및 Unity session 가드 아래서만 이벤트를 전달한다. 로그아웃·등록 해제·종료 시 중단한다.
### P06-T05 iOS 연결 compile·회귀 검증 시작
- Swift core 및 C bridge 단위 시험을 실행한다. 실제 simulator 및 Unity player는 별도다.
- Swift C bridge 기존 3건 통과. 등록→Native 스트림→로그아웃의 합성 URLProtocol 시험을 추가해 새 수명주기를 직접 확인한다.
- Swift 합성 URLProtocol에서 등록→AsyncBytes 이벤트→로그아웃 및 토큰 삭제 시험 통과. 실제 Backend·iOS simulator·Unity는 별도다.
### P06-T05 iOS simulator compile 검증 시작
- 격리된 Xcode project에서 Native framework simulator compile을 수행한다. 스토어와 Unity 실행 검증으로 간주하지 않는다.
- 격리 project `artifacts/ios-project.TTcc9k`의 iOS simulator Native framework compile 종료 0. Xcode 다중 destination 경고만 표시됐고 실제 simulator 실행은 아니다.
- 커밋 준비: iOS 등록·세션 가드·종료 연결과 synthetic lifecycle 시험을 저장한다. 실제 DB 및 Unity E2E가 남아 BUG-014 OPEN이다.
### P06-T05 실제 로컬 Backend E2E 시작
- 전용 임시 DB와 local-mock 서버를 사용해 Android/iOS Native 수신을 검증할 opt-in harness를 작성한다. synthetic key만 사용하고 실제 외부 서비스는 호출하지 않는다. Unity player는 별도 대기다.
### P06-T05 Android E2E 컴파일 검증 시작
- opt-in 시험이 기본 실행에서 건너뛰어지는지와 Kotlin compile을 확인한다. 실제 local DB 실행은 전용 harness 구성 후 수행한다.
### P06-T05 iOS E2E 컴파일 검증 시작
- 명시 opt-in이 없을 때 실제 서버에 연결하지 않고 skip되는지 확인한다.
- iOS E2E 첫 컴파일은 `XCTUnwrap` autoclosure 안의 async 호출 제약으로 실패했다. 응답을 먼저 await한 뒤 unwrap하도록 시험을 수정한다.
### P06-T05 로컬 DB E2E 실행 시작
- `harness/run-mock-push-e2e.py --run-local`은 새 DB·role을 만들고 기존 데이터는 삭제하지 않는다. 생성된 synthetic key는 출력하지 않으며 local Backend→Android 및 Swift Native receiver를 시험한다. Unity 및 실제 원격 발송은 포함하지 않는다.
- `python3 harness/run-mock-push-e2e.py --run-local` 종료 0, `artifacts/mock-push-e2e-imlgc2et/result.json`: 전용 DB `gamebridge_ci_003a23e777`, Android·Swift Native 각 1건 PASS. synthetic key, local-mock만 사용했고 Unity player·실기기·원격 푸시는 미검증이다. 테스트용 DB와 role은 보존한다.
- 커밋 준비: opt-in E2E harness, 양 Native 시험 및 실제 확인 범위 문서만 저장한다. BUG-014는 Unity lifecycle 검증까지 OPEN이다.

### [P09-T05] Mock 푸시 Native E2E 하네스 재개
- 새 전용 DB E2E를 opt-in 회귀 lane으로 연결한다. 미실행은 DEFERRED_ENV, Unity player는 별도로 미실행으로 유지한다. 합성 메시지와 실제 원격 푸시를 구분한다.
### P09-T05 회귀 집계 검증 시작
- opt-in이 없으면 Native DB E2E가 DEFERRED_ENV이고 Unity lane이 별도로 남는지 확인한다. DB를 자동 생성하지 않는다.
- opt-in 없는 `harness/run-push-regression.py` 종료 2, `artifacts/push-regression-bgnyz5k6`: Native DB E2E와 Unity lane DEFERRED_ENV, fake 시험은 PASS. DB 자동 생성은 없었다.
### P09-T05 opt-in 집계 검증 시작
- 명시 opt-in으로 전용 DB E2E를 다시 실행하고 두 Native 시험의 비skip·source head 일치가 집계에 반영되는지 확인한다. Unity lane은 미실행으로 둔다.
- opt-in 집계 `artifacts/push-regression-zbx_69dj/result.json`: Native local DB E2E 2건 PASS, 기존 fake·UPM checksum PASS, sandbox DB·iOS host·Unity player는 DEFERRED_ENV, 전체 종료 2. 이전 UPM staging은 최신 Mock push binary를 포함하지 않아 체크섬 자체만 확인했다.
- 커밋 준비: fail-closed 조건으로 Native E2E lane을 연결하고 Unity lane 미실행을 유지한다.

### [P05-T03] BUG-013 격리 개발 경로 재개
- Xcode StoreKit 자체 검증 결과를 개발 전용 fake 서버 지급에 연결한다. 서버는 Apple 서명을 검증했다고 주장하지 않으며 local-mock profile·개발키·분리된 Xcode 사용자/구매 namespace를 강제한다. sandbox/production에서 경로를 노출하지 않는다.
### P05-T03 서버 경계 검증 시작
- local-mock 전용 Xcode fake account/grant/wallet의 컴파일과 기본 테스트를 실행한다. Apple 서명 서버 검증이 아니며 Native StoreKit 연결도 아직 없다.
- grant transaction에서 세션 행을 잠가 logout과의 경합을 차단했다. local Xcode 사용자·구매 namespace가 일반 Mock 지갑에 섞이지 않도록 별도 계정을 사용한다.
### P05-T03 개발 지급 DB 검증 시작
- 전용 빈 DB에서 개발키, 사용자 소유권, 중복 지급 및 일반 Mock 잔액 격리를 확인한다. production에서 endpoint가 없는지도 별도로 시험한다.
- 전용 DB `gamebridge_ci_f0c4a4cb59`에서 개발키·소유권·중복 지급·일반 Mock 잔액 분리 및 production endpoint 부재 통과. sandbox 차단과 동시 요청도 추가 확인한다.
### P05-T03 동시 지급·sandbox 차단 검증 시작
- 전용 DB `gamebridge_ci_de4a583e88`에서 동일 거래 8건 동시 요청 중 1회만 지급, Mock/Xcode 잔액 분리, 타 사용자 차단이 통과했다. sandbox·production 개발 endpoint 부재 시험도 통과했다. StoreKit client와 Unity는 아직 미연결이며 Apple 서버 서명 검증은 아니다.
- 커밋 준비: local 전용 fake grant 및 DB/환경 격리 시험. BUG-013 OPEN 및 실제 StoreKit 실패 상태를 유지한다.
### P05-T03 Swift 개발 지급 client 시작
- 명시적 local-mock 개발 경로에서만 Xcode account·grant·wallet 요청을 허용하고 Native 세션·개발키를 유지한다. 요청·응답 소유권과 거래 식별자를 검사한다. 실제 StoreKit 연결은 다음 단계다.
### P05-T03 Swift 개발 client 검증 시작
- Swift compile과 기존 인증·Backend request 회귀를 실행한다. 개발 grant 응답의 실제 서버 연결과 StoreKit은 별도다.
- Swift 기존 인증·HTTP 시험 5건 통과. Xcode 개발 account/grant/wallet에서 개발키 및 session header 사용을 synthetic URLProtocol로 추가 검증한다.
- 신규 Swift fake 시험의 첫 컴파일은 JSON 문자열 escaping과 XCTest async autoclosure 오류로 실패했다. 시험 코드를 수정하고 재실행한다.
- Swift fake account/grant/wallet 시험 재실행 통과. 개발키와 Native access token 헤더를 확인했으며 실 서버/StoreKit과는 별도다.
- 커밋 준비: local-mock에서만 명시된 Xcode 개발 endpoint 호출을 허용하는 Swift client와 fake 시험. BUG-013 OPEN 유지.
- Apple 공식 문서의 `Transaction.environment` 및 `.xcode` 구분을 확인했다(https://developer.apple.com/documentation/storekit/transaction/environment, https://developer.apple.com/documentation/storekit/appstore/environment). Xcode fake grant에 실제 sandbox/production 거래가 들어가지 않도록 검증된 거래의 환경을 검사한다.
### P05-T03 StoreKit Native 합성 시작
- 기존 StoreKit 2 provider를 재사용하되 Xcode 환경의 검증된 거래만 local fake grant에 전달하고 지급 확인 후 finish한다. 구매·복원 실동작 검증 전까지 미완료다.
### P05-T03 StoreKit Native compile 검증 시작
- Swift compile과 기존 StoreKit fake verifier 시험을 수행한다. 실제 StoreKit 거래·Unity player는 실행하지 않는다.
- 첫 Swift compile 실패: 새 거래 환경 판별 closure가 initializer 매개변수에 추가되지 않아 발생했다. 선언을 바로잡고 재실행한다.
- Swift compile 오류 수정 후 기존 StoreKit fake 및 개발 client 5건 통과. Xcode 환경만 허용하는 분기와 sandbox/production 거부를 추가 단위 검증한다.
- Swift StoreKit fake 5건 통과. Xcode 환경만 허용하고 sandbox/production을 거부하는 조건도 확인했다. 실제 transaction에 대한 guard 및 finish는 simulator 재시험이 필요하다.
- 커밋 준비: Native Xcode session·verified environment gate만 저장한다. Unity bridge와 실제 거래가 남아 BUG-013 OPEN이다.
### P05-T07 Xcode StoreKit Unity bridge 시작
- iOS 전용 XCODE_STOREKIT 모드가 개발 인증·격리된 Xcode 사용자·StoreKit 제품/구매/복구 및 지갑으로 연결되도록 구현한다. Android·sandbox에서 개발 경로를 허용하지 않는다. 실제 Unity player 및 StoreKit 실행은 별도 검증한다.
### P05-T07 Xcode bridge compile 검증 시작
- Swift package 및 iOS simulator framework, Unity C# 네 조건부 compile을 실행한다. 실제 Xcode StoreKit 거래와 Unity player는 별도다.
- Swift C bridge·StoreKit fake 8건, iOS simulator framework compile 및 Unity 네 조건부 managed compile 통과. 실제 Xcode 거래와 Unity player는 아직 미검증이다.
### P05-T07 Xcode bridge fake 경계 검증 시작
- 개발 모드 설정·초기화·Native account 매핑을 합성 transport로 확인하고 개발키 누락과 플랫폼 조건을 검사한다.
- Swift 합성 Xcode bridge/account 시험 2건 및 독립 C# fake mode/개발키 전달 시험 통과. simulator framework compile과 4개 managed compile은 성공했으나 StoreKit 실제 거래·Unity player는 미실행이다.
- 커밋 준비: Xcode 모드 Unity 설정·iOS bridge 및 fake 경계만 저장한다. 실제 로컬 거래 실패/환경 대기는 그대로 둔다.
### P05-T03 iOS 18.6 격리 simulator StoreKit 재시험 시작
- 이전 iOS 26.5 SKTestSession Code 3 실패를 유지한 채 새로 생성한 전용 iOS 18.6 simulator에서 기존 상품 조회 시험을 재실행한다. 사용자 기존 simulator 데이터와 거래는 수정·삭제하지 않는다. 이 시험은 구매/서버 지급 검증이 아니다.
- 새 iOS 18.6 전용 simulator `D7C33BEE-66F5-4C37-A896-8649CE20A9F7`에서 `GameBridgeStoreKit` 상품 조회 시험 1건 PASS, skip 0: 두 상품 및 사용자 승인 시험 가격 확인. 결과 `artifacts/storekit-p05-18-1794332423.xcresult`. iOS 26.5의 기존 실패는 별도 OPEN으로 유지하며 구매·취소·대기·서버 지급은 이 시험에 포함되지 않는다. 전용 simulator는 보존한다.
- 커밋 준비: 대체 simulator의 제한된 상품 조회 증거와 현재 구현 상태를 기록한다. P05-T03 전체 FAIL과 BUG-013 OPEN은 유지한다.
### P05-T03 Xcode 실제 로컬 거래 시험 시작
- 격리 iOS 18.6 simulator에서 StoreKit 구매와 Native의 Xcode 환경 확인, synthetic 서버 지급 응답, finish를 연결하는 시험을 추가한다. 실 Apple Sandbox와 실제 Backend/DB 지급은 별도다. 기존 simulator 거래를 초기화하거나 삭제하지 않는다.
### P05-T03 로컬 거래 검증 실행
- 기존 전용 iOS 18.6 simulator에서 Xcode StoreKit 구매 및 synthetic server grant/finish 시험을 실행한다. 실패 시 원인을 남기고 이전 상품 조회 통과와 구분한다.
- iOS 18.6 실제 Xcode 테스트 구매에서 transaction은 생성됐으나 결과가 VERIFICATION_PENDING이고 finish되지 않아 실패했다(`artifacts/storekit-purchase-p05-18-1794332528.xcresult`). fake 서버 호출 경계를 추가 계측해 원인을 확인한다. 이 거래는 전용 simulator에 보존하며 실제 Apple 결제가 아니다.
### P05-T03 StoreKit 지급 실패 진단 검증 시작
- synthetic HTTP 호출 경로와 body 유효성만 기록하고 비밀값이나 거래 증빙은 출력하지 않는다. 같은 전용 simulator에서 재실행한다.
- 재시험 `artifacts/storekit-purchase-debug-1794332613.xcresult`도 VERIFICATION_PENDING. synthetic backend의 grant endpoint에 도달하지 않아 StoreKit 검증 후 Native 내부 단계에서 중단됨을 확인했다. 전용 simulator의 미완료 거래 정보에서 원인을 더 좁힌다.
### P05-T03 미완료 거래 진단 검증 시작
- 전용 Xcode simulator transaction의 식별자·환경·account token 존재 여부만 확인한다. raw JWS나 인증키는 기록하지 않는다.
- 진단 결과 전용 iOS 18.6의 검증된 Xcode transaction ID가 `0`이다(`artifacts/storekit-purchase-diag-1794332670.xcresult`). 기존 양수 검사 때문에 fake grant 전에 실패한다. 단순히 0을 허용하면 여러 Xcode 거래가 같은 키로 합쳐져 중복·누락이 생길 수 있으므로, 검증된 Xcode JWS의 SHA-256을 별도 거래 식별자로 쓰고 동일 증빙 재복구의 멱등성을 검증한다. 실제 Apple 경로 식별자는 변경하지 않는다.
### P05-T03 Xcode 0 거래 ID 보강 검증 시작
- Swift fake 검증 및 서버 격리 회귀를 먼저 수행한 뒤 simulator에서 같은 transaction 재복구와 finish를 재시험한다. JWS 원문은 로그·DB에 저장하지 않는다.
- 첫 Swift compile은 두 인자 identity closure의 기본 구현에서 두 번째 인자를 명시하지 않아 실패했다. 선언을 수정하고 재실행한다.
- Swift 回归 7건 통과. 기존 Apple sandbox 경로는 여전히 숫자 transaction ID를 사용하며 Xcode 경로만 검증된 JWS 해시를 사용한다. 전용 simulator에서 미완료 거래 복구와 새 거래 finish를 다시 확인한다.
### P05-T03 simulator 재시험 시작
- iOS 18.6 `artifacts/storekit-purchase-hash-1794332782.xcresult` 1건 PASS: Xcode 검증 거래→synthetic grant→finish 및 미완료 목록 0건. 이전 실패 거래도 시작 복구 경로에서 처리됐다. 이는 실제 DB·Unity player·Apple sandbox 검증이 아니다.
### P05-T03 거래 해시 멱등성 검증 시작
- 서로 다른 Xcode 구매의 해시가 구분되는지 simulator에서 확인하고 서버에서 같은 해시 재요청의 중복 지급 방지를 시험한다.
- `artifacts/storekit-purchase-distinct-1794332839.xcresult` iOS 18.6 1건 PASS, skip 0: 두 Xcode 테스트 구매의 JWS 해시가 달라 각각 synthetic 지급·finish됐다. 전용 DB `gamebridge_ci_d8c58af962`에서는 동일 해시 재요청에 중복 지급이 없고 sandbox/production 개발 경로가 없는 것을 확인했다. 동일 미완료 거래의 JWS 재발급 안정성, 실제 DB와 결합한 StoreKit 복구, Unity player는 아직 미검증이다.
- 커밋 준비: Xcode 전용 JWS 해시 식별자, fake 서버 멱등성 및 simulator 시험을 저장한다. Apple 실제 거래 검증은 WAITING_USER이며 BUG-013 OPEN 유지.
### P05-T03 미완료 거래 JWS 안정성 검증 시작
- 새 전용 simulator에서 생성한 Xcode 테스트 거래에 대해 구매 직후와 미완료 조회의 JWS digest가 같은지 확인한다. 시험이 생성한 로컬 거래만 마지막에 finish하며 실제 서버 지급이나 Apple sandbox 시험으로 취급하지 않는다.
- 블로커: 전용 iOS 18.6 simulator에서 같은 미완료 거래의 구매 시점과 재조회 JWS SHA-256이 달라 안정적이지 않음이 확인됐다(`artifacts/storekit-stability-1794332909.xcresult`, 1 FAIL). 현재 JWS 전체 해시를 거래 식별자로 쓰면 복구 시 중복 지급 위험이 있으므로 즉시 Xcode fake 지급을 fail-closed로 차단하고 안정적인 필드를 조사한다. 기존 PASS는 synthetic 단일 실행 범위로만 유지한다.
### P05-T03 임시 차단 검증 시작
- 거래 식별자 재조회 불안정 상태에서 fake 지급을 호출하지 않도록 차단한 후 Swift 회귀를 확인한다. 차단 중 구매는 finish되지 않는다.
- 임시 차단 상태에서 기존 Swift fake 7건 통과. Xcode 실제 지급은 의도적으로 중단 상태이며 안정적 거래 ID 확정·DB 복구 재검증이 필요하다.
- 커밋 준비: 재현 시험과 fail-closed 차단을 먼저 기록한다. 사용자 거래·기존 simulator 데이터는 삭제하지 않았다.
### P05-T03 Xcode 거래 안정 필드 조사 시작
- 검증된 JWS payload의 필드명만 비교해 서명 재생성 시 변하는 부분을 확인한다. 필드값·원문 증빙은 출력하지 않는다. 생성한 전용 simulator 시험 거래만 finish한다.
### P05-T03 안정 필드 진단 시험 실행
- Xcode 서명 payload에서 같은 거래 재조회 시 달라지는 필드는 `deviceVerification`, `deviceVerificationNonce`, `signedDate`로 확인됐다(`artifacts/storekit-fields-1794333020.xcresult`). 임의로 나머지 전체를 해시하면 향후 새 가변 필드가 추가될 때 다시 중복 지급될 수 있으므로 고정 허용 필드 후보와 구매 간 유일성을 검증한다. fake 지급 차단 유지.
### P05-T03 허용 필드 목록 진단 시작
- 개인정보·서명 원문 없이 필드명만 기록하는 의도적 실패 시험을 실행한다.
- 의도적 필드 목록 시험 `artifacts/storekit-fields-list-1794333087.xcresult`에서 고정 후보로 transactionId, originalTransactionId, productId, purchaseDate, originalPurchaseDate, appAccountToken, bundleId, appTransactionId가 있음을 확인했다. 같은 계정의 연속 구매에서 실제 어떤 고정 필드가 달라지는지 확인하기 전까지 지급은 차단한다.
### P05-T03 다른 구매의 고정 필드 진단 시작
- 동일 계정에서 연속 두 Xcode 로컬 거래를 생성하고 값은 출력하지 않은 채 서로 다른 필드명만 의도적 실패로 기록한다. 테스트가 생성한 거래만 finish한다.
- 동일 account에서 연속한 별도 Xcode 구매 두 건의 서명 payload를 비교한 결과, 서로 다른 것은 앞서 재조회 시에도 바뀌는 세 필드뿐이었다(`artifacts/storekit-fields-different-1794333146.xcresult`). 관측된 고정 필드로는 서로 다른 거래를 구분할 수 없어 해시로 멱등성을 보장할 수 없다. fake grant 차단에 더해 신규 StoreKit 구매 자체도 차단하고 기존 미완료 거래는 finish하지 않는다. 실제 Apple sandbox 경로는 영향 없다.
### P05-T03 신규 구매 차단 검증 시작
- StoreKit provider fake 회귀와 코드 compile을 실행하고 미해결 상태를 명시한다. Xcode 거래를 더 생성하지 않는다.
- Swift 기존 fake 7건 통과. 구매 화면 호출 전에 `CONFIG_REQUIRED`를 반환하는 직접 unit 시험을 추가한다.
- 직접 unit 시험 3건 통과: 모호한 식별자일 때 StoreKit 구매 화면 호출 전에 CONFIG_REQUIRED를 반환한다. 실패 재현 시험을 고정 후보 필드 충돌을 검출하는 명시적 회귀로 정리했다.
- 커밋 준비: fail-closed 신규 구매 차단·재현 시험·보고 수정. 실제 복구 및 Unity 검증은 미완료다.

### [P09-T02] R12 반복 수명주기 보강 시작
- 독립 .NET EditorOffline fake 100회에서 초기화 중 푸시 queue와 pending registry의 종료 정리, 종료된 객체 보존 여부를 검사한다. Unity scene/실기기 검증으로 일반화하지 않는다.
### P09-T02 100회 수명주기 검증 시작
- 각 주기에서 초기화 중 fake push를 queue에 넣고 종료 후 비움·pending 0을 확인한다. 100회 종료 후 강제 GC에서 client/transport weak reference가 남지 않는지도 확인한다. Unity Editor 실행이나 장시간 memory profile은 아니다.
- 첫 stress 컴파일은 결과 변수 이름이 후속 보고 변수와 충돌해 실패했다. 테스트 변수 이름을 바꾸고 재실행한다. 생성된 실패 evidence는 보존한다.
- `artifacts/lifecycle-stress.B1S3dz/result.json`: 100회 모두 queued push 및 pending 0, 강제 GC 뒤 client·transport 각각 0개 보존. 독립 .NET fake이며 Unity player나 장시간 메모리 profile은 아니다. R12를 해당 로컬 stress 범위로 연결한다.
### P09-T02 R12 하네스 검증 시작
- manifest 검증과 명시적 로컬 실행을 수행한다. 다른 49개 시나리오의 상태는 변경하지 않는다.
- `harness/run-scenario.py R12` 명시 실행 종료 0, 새 evidence `artifacts/lifecycle-stress.A8iyaJ`에서 100회 queue/pending 정리 및 client/transport weak reference 0 확인. manifest 음성 검사와 원장 검사도 통과. Unity 및 무한 시간 누수 부재를 주장하지 않는다.
- 커밋 준비: R12 독립 .NET fake 범위만 IMPLEMENTED로 반영하고 다른 시나리오·Unity 검증은 그대로 둔다.

### [P08-T04] 독립 Unity consumer 검증 경로 재개
- Unity CLI 지침과 Unity Test Framework 공식 설명을 확인했다. staging package를 복사한 새 격리 프로젝트에서 Editor lifecycle test를 실행하는 명령을 작성한다. 기존 사용자 unity/Demo는 건드리지 않으며 라이선스 실패는 통과로 기록하지 않는다.
### P08-T04 consumer runner 검증 시작
- 결과 XML이 누락·실패·skip인 경우 통과하지 않음을 synthetic fixture로 검사한 뒤 Unity 라이선스 환경에서 실제 명령을 실행한다. staging은 새 소비 프로젝트에 복사하며 사용자 Demo는 보존한다.
- 실제 CLI 재시험은 Editor test 결과 없이 CLI 초기 단계에서 50초 이상 대기해 중단했다(`artifacts/unity-consumer.uXtPNZ`); 테스트는 NOT_RUN이다. CLI exit 6은 컴파일 오류와 환경 오류를 모두 포함하므로 환경 대기로 단정하면 안 되는 점을 발견했다. 외부 timeout과 결과·컴파일 오류 분류를 보강한다.
### P08-T04 수정된 runner 재검증 시작
- CLI 전체 호출에 시간 제한과 자식 프로세스 정리를 적용하고 compile 실패와 결과 없는 미완료를 구분한다. 여전히 Unity 라이선스 없이 PASS를 만들지 않는다.
- Unity CLI가 아직 결과를 내지 않아 별도로 Unity 설치본의 managed reference를 사용해 consumer test 소스의 C# compile을 확인한다. 이는 Editor 테스트 실행을 대체하지 않는다.
- 수정 runner의 실제 호출은 `artifacts/unity-consumer.uQc96O/unity-cli.log`에 기록된 외부 65초 timeout으로 종료 2, XML 없음; Editor 시험은 NOT_RUN이다. `unity` 및 자식 프로세스는 정리됐다. consumer test 소스는 설치된 Unity managed reference에 대해 독립 C# compile 경고 0·오류 0이며 실제 Unity 실행은 아니다.
### P09-T05 Unity Editor lane 연결 시작
- 새 runner를 manifest와 aggregate에 opt-in으로 연결한다. 실제 실행하지 않거나 결과가 없으면 통과가 아니다.
### P09-T05 Unity lane 검증 시작
- manifest·음성 검사, 실제 결과 XML parser의 skip/missing 거부를 재검증한다. Unity Editor 실제 통과로 표시하지 않는다.
- manifest/누락 음성/원장 검사와 shell 구문 검증 통과. aggregate에서 Editor opt-in 시 XML 검증의 실제 실행 건수를 읽으며, 미실행은 NOT_RUN이다. 테스트 자체는 아직 Editor에서 실행되지 않았다.
- 커밋 준비: 격리 Unity consumer runner·테스트 소스와 fail-closed XML 판정만 포함한다. 오래된 staging으로 수행한 실행은 결과가 없어 import PASS로 기록하지 않는다.

### [P08-T01] [P08-T02] [P08-T03] 현재 소스 재패키징 시작 및 검증 준비
- Mock push와 Xcode 지급 차단을 포함하는 최신 소스에서 Android Maven·iOS XCFramework·UPM staging을 새 경로에 생성한다. 이전 산출물과 사용자 파일은 보존한다. Unity 실제 import는 별도다.
- source HEAD `10e2a3c`에서 Android Maven 45 task 강제 재실행 및 R8 소비자 빌드, iOS device/simulator XCFramework, simulator Swift 독립 link, device C ABI symbol 4개, UPM staging checksum 통과. Xcode 신규 구매는 안전 차단된 상태다. Unity import/export 및 실제 기기는 미검증이다. 산출물 경로와 SHA-256은 `docs/evidence/current-artifact-manifest.json`에 기록했다.
- 커밋 준비: 현재 산출물 manifest와 범위만 기록한다. 이전 산출물 및 user `unity/Demo`는 보존한다.
### P05-T03 Xcode 완료 후 별도 거래 식별 검증 시작
- 앞선 두 purchase 호출은 첫 거래를 finish하기 전에 실행했으므로 StoreKit이 같은 미완료 거래를 반환했을 가능성을 배제하지 못한다. 첫 거래를 finish한 다음 두 번째를 생성해 고정 필드를 비교한다. SDK의 fail-closed 차단은 유지한다.
- `artifacts/storekit-sequential-identity-1794333841.xcresult`: 첫 거래 finish 후 새 구매의 고정 필드 digest가 다른 것 1건 PASS. 앞서 finish 전 두 호출의 고정 필드가 같았다는 관찰은 동일 미완료 거래 재반환 가능성이 있어 별개 거래 충돌로 단정하지 않는다. 재서명·응답 유실·재시작에 걸친 원자적 중복 방지는 아직 검증되지 않아 fail-closed 유지.
- 커밋 준비: 시험 순서와 과도했던 보고 표현을 바로잡는다. 신규 구매 차단은 해제하지 않는다.
### P05-T03 안정 식별자 연구 재개
- 확인된 고정 필드만 canonicalize한 Xcode 전용 후보 식별자를 구현하고 동일 미완료 거래 재조회 및 완료 후 다른 구매와 비교한다. 이것만으로 충돌·응답 유실 후 정확히 한 번 지급이 보장되지는 않으므로 구매·fake grant 차단은 유지한다.
### P05-T03 후보 식별자 simulator 검증 시작
- 고정 필드 canonicalization이 동일 미완료 거래에서는 일치하고 완료 후 연속 구매에서는 다른지 재시험한다. 실패·충돌 가능성에 대비해 실제 지급 차단은 유지한다.
- `artifacts/storekit-candidate-identity-1794333968.xcresult` 1건 PASS: 같은 미완료 거래 재조회 후보 digest 일치, finish 후 연속 구매 digest 구분. 이는 제한된 iOS 18.6 사례이며 충돌 불가능을 증명하지 않는다. 개발 지급과 신규 구매 차단을 유지한다.
### P05-T03 후보 식별자 입력 검증 시작
- 가변 필드 무시, 고정 필드 변경, 누락·불리언·잘못된 JWS 거부를 synthetic unit으로 검증한다.
- Swift StoreKit 및 개발 client 9건 통과. 후보 함수는 StoreKit의 verified 결과에서만 사용하며 자체 서명 검증기는 아니다. 새/기존 거래 충돌 및 재시작 응답 유실을 다루는 durable attempt 연동 전까지 구매 차단 유지.
- 커밋 준비: 후보 정규화와 실제 simulator 재조회·unit 시험만 저장한다. 완료나 실제 Apple 검증으로 표시하지 않는다.
### [P05-T05] Xcode 개발 거래 durable attempt 시작
- 후보 식별자만으로 유일성을 가정하지 않는다. 사용자 위임에 따라 테스트 전용 시도 UUID를 로컬에 보존하고 서버에서 거래 키와 원자적으로 연결해 다른 시도의 키 충돌을 거부한다. 완료 후 로컬 단서는 삭제한다. 서버 거래 기록은 개발 DB 수명 동안 유지하며 실 Apple/sandbox에는 적용하지 않는다. 전체 경로 검증 전 구매 차단 유지.
### P05-T05 Xcode 시도 UUID 서버 검증 시작
- 전용 DB에서 동일 시도 동시 재요청 1회 지급, 다른 시도의 동일 거래 키 충돌 및 같은 시도의 다른 키 충돌을 시험한다. 구매 차단은 유지한다.
- 전용 DB `gamebridge_ci_a94a1d843b`에서 동일 시도 8건 중복 요청의 1회 지급, 다른 시도의 같은 키·같은 시도의 다른 키 거부, sandbox/production endpoint 부재 통과. Native는 아직 attempt ID를 보내지 않으므로 구매 차단 유지.
- 커밋 준비: 서버의 개발 전용 원자적 attempt 결합 및 DB 회귀만 저장한다. Native journal과 StoreKit 복구는 다음 작업이다.
### P05-T05 Xcode Native attempt journal 시작
- 원문 JWS 대신 account·후보 key·시도 UUID만 Native 보안 저장소에 저장한다. 같은 거래 재시도는 UUID를 재사용하고 다른 거래·계정은 충돌로 차단하며 finish 확인 후 삭제한다. 아직 구매 차단은 유지한다.
### P05-T05 Native journal 단위 검증 시작
- 재생성 시 같은 attempt 재사용, 계정/거래 차단, finish 삭제, 기록 손상 fail-closed를 synthetic 저장소로 검증한다. Keychain·서버 연결 및 구매 차단 해제는 아직 아니다.
- journal 첫 단위 시험 5건 통과. 추가 검토에서 StoreKit 조회가 비어 있는 것만으로 완료를 단정하면 복구 단서를 잃을 수 있어, 해당 transaction의 완료 이력이 확인될 때만 stale journal을 정리하도록 강화한다.
### P05-T05 journal 보수적 정리 검증 시작
- journal 재시험 2건 통과: 재시도 시도 ID 유지, 타 계정·다른 거래 차단, 정상 finish 삭제, 미확인 빈 조회에서는 보존, 완료 이력 확인 시 정리, 손상 기록 fail-closed. 아직 Keychain·StoreKit·서버 통합 전이다.
- 커밋 준비: Native journal 및 필수 attempt ID client만 저장한다. 실제 구매 차단 유지.
### P05-T05 StoreKit finish와 journal 연결 시작
- 성공적인 서버 지급 후 StoreKit finish가 돌아온 경우에만 해당 attempt 단서를 지우는 callback을 연결한다. Xcode 구매는 여전히 차단하며 실제 provider 기본 동작은 그대로 유지한다.
### P05-T05 finish callback 회귀 검증 시작
- 기존 Apple sink와 journal 단위 시험을 실행한다. 실 StoreKit 지급 차단은 유지한다.
- Swift 기존 StoreKit 및 journal 8건 통과. protocol 기본 callback은 기존 Apple sink에서 no-op이며 실제 StoreKit finish 순서는 simulator 통합에서 다시 확인해야 한다.
- 커밋 준비: finish 이후 callback 경계만 저장하고 Xcode 구매 차단은 유지한다.
### P05-T05 Xcode journal 통합 시작
- Keychain journal을 StoreKit 완료 순서 및 서버 attempt와 연결한다. 여러 거래의 후보 key 충돌이나 완료 증거 부재는 차단한다. 실제 Unity 공개 경로의 구매 차단은 유지하고 별도 테스트 전용 경계에서만 통합 흐름을 검증한다.
### P05-T05 journal 통합 compile 검증 시작
- Xcode 공개 경로는 차단 유지, 내부 시험 경로만 시도 ID·완료 후 정리를 활성화한다. Swift unit 및 iOS simulator compile을 확인한다.
- Swift 합성 journal·StoreKit 및 공개 차단 unit 11건 통과. 내부 시험 전용 구성에서 시도 ID와 완료 후 단서 삭제를 simulator로 확인한다. 외부 공개 구성은 차단 상태다.
### P05-T05 내부 구성 StoreKit 통합 검증 시작
- 격리 iOS 18.6 simulator `444C37EF-E7F9-4EF1-AC2E-012E28889BB1`, `artifacts/storekit-attempt-1794334311.xcresult`: 내부 시험 전용 설정에서 Xcode 구매 2건, fake attempt 결합, finish 및 journal 삭제 1개 시험 PASS/skip 0. Keychain, 실제 local DB 응답 유실·재시작과 Unity 경로는 아직 검증되지 않았다. 공개 Xcode 구매는 계속 차단 중이다.
- 커밋 준비: journal/finish 통합과 내부 simulator 시험 경계만 저장한다. 테스트 전용 우회는 공개 SDK 설정에 노출하지 않는다.
### P05-T05 Xcode StoreKit 실제 local DB 응답 유실 시험 시작
- 새 전용 simulator와 전용 local-mock DB에서 StoreKit 구매→서버 commit 후 응답 유실→Keychain journal 재생성→같은 attempt 복구·finish·단서 삭제를 시험하는 opt-in harness를 구현한다. synthetic 개발키만 사용하며 실제 Apple sandbox·Unity는 포함하지 않는다. 공개 구매 차단은 유지한다.
### P05-T05 Xcode DB E2E test compile 검증 시작
- opt-in 없는 simulator 실행에서는 skip되어야 한다. 실제 실행은 전용 DB·synthetic 서버 준비 후 수행한다.
- opt-in 없는 Xcode DB 시험은 `artifacts/storekit-db-skip-1794334430.xcresult`에서 1건 SKIP, PASS 0으로 확인했다. 이제 독립 DB·서버와 전용 simulator를 준비하는 opt-in runner를 추가한다.
### P05-T05 실제 local DB 응답 유실 E2E 실행 시작
- 명시 opt-in runner로 새 DB·role 및 새 iOS 18.6 simulator를 만들고 기존 데이터는 보존한다. server commit 뒤 synthetic 응답 유실, Keychain instance 재생성, 동일 attempt 복구·finish·잔액 확인을 수행한다.
- 실제 local DB/Xcode E2E 첫 실행 `artifacts/xcode-storekit-e2e-7p8zh2_a/result.json` FAIL, 1건 INTERNAL_ERROR. 전용 DB `gamebridge_ci_ac23f963a3`와 simulator는 보존한다. 무서명 simulator Keychain 가능성을 포함해 실패 단계를 비밀값 없이 계측하고 ad-hoc 서명으로 재시험한다. 공개 구매 차단 유지.
### P05-T05 local DB E2E 재시험 시작
- 전용 simulator ad-hoc 서명과 단계 계측을 사용한다. synthetic 키·거래 payload는 기록하지 않는다.
- ad-hoc 서명 재시험 `artifacts/xcode-storekit-e2e-l4d287dk/result.json`은 1건 PASS였으나, 응답 유실이 실제 서버 commit 뒤였는지 시험이 별도 assertion으로 확인하지 않았다. PASS를 최종 증거로 쓰기 전에 commit 직후 잔액과 의도적 응답 유실 횟수를 명시적으로 검증한다.
### P05-T05 commit 후 유실 assertion 재검증 시작
- 새 전용 DB와 simulator에서 commit 후 wallet 100 및 성공 응답 드롭 횟수, 재시작 이후 wallet 100·journal 삭제를 모두 확인한다.
- 강화된 `artifacts/xcode-storekit-e2e-7p_3v_5l/result.json` PASS/skip 0: 전용 DB `gamebridge_ci_88cb73f12b`에서 commit 뒤 응답 드롭 횟수>0 및 복구 전/후 잔액 100, Keychain 재생성·finish·journal 삭제 확인. 실제 OS 프로세스 kill·Unity 및 Apple sandbox는 아니다.
- Apple 공식 문서 확인: 기본 `Transaction.all`은 완료된 소모품을 제외한다(https://developer.apple.com/documentation/storekit/transaction/all). finish 직후 journal 삭제 전에 종료되면 완료 이력을 찾지 못해 복구 단서가 남거나 충돌 검사에 빈틈이 생길 수 있으므로, Xcode 내부 시험은 host의 `SKIncludeConsumableInAppPurchaseHistory=true`를 요구하고 이 경계도 검증한다. 공개 구매 차단은 계속 유지.
### P05-T05 완료된 소모품 이력 guard 검증 시작
- debug simulator host에만 이력 설정을 넣고 Native session store와 pending store의 동일 인스턴스를 거부한다. 이어 실제 완료 후 journal 삭제 실패·재생성을 시험한다.
### P05-T05 finish 직후 저장 실패 복구 검증 시작
- 실제 local DB가 지급한 뒤 StoreKit finish와 journal 삭제 사이의 실패를 주입하고 Keychain 재생성 후 완료된 소모품 이력으로 단서를 안전하게 정리하는지 확인한다. 잔액은 100을 유지해야 한다.
- `artifacts/xcode-storekit-e2e-3b0ibts2/result.json` PASS/skip 0: 전용 DB `gamebridge_ci_2c900d894e`에서 서버 commit 후 응답 유실, Keychain 재생성, finish 뒤 journal 삭제 실패, 두 번째 재생성에서 완료 소모품 이력 확인·정리 및 잔액 100을 검증했다. 실제 프로세스 kill·Unity player·Apple sandbox는 아니다.
- 공식 WWDC 자료는 완료된 소모품 이력 opt-in을 iOS 18에서 도입했다고 설명한다(https://developer.apple.com/videos/play/wwdc2024/10061/). 이전 OS에서는 해당 보장을 가정하지 않는다. 공개 구매 차단은 유지한다.
- 커밋 준비: opt-in local E2E runner와 ad-hoc simulator Keychain 시험 및 debug host 이력 설정을 기록한다. 생성된 전용 DB·simulator는 보존한다.
### P05-T05 Keychain namespace alias 검증 시작
- 서로 다른 KeychainTokenStore 인스턴스라도 같은 service를 사용하면 동일 항목을 가리킨다. 객체 동일성만 검사하면 세션과 구매 단서가 서로 덮어쓸 수 있어 저장소 identity도 비교하도록 보강한다. 공개 Xcode 구매는 계속 차단한다.
### P05-T05 Keychain alias 회귀 실행
- synthetic Swift 회귀와 전용 simulator의 다른 인스턴스·같은 service 거부를 검증한다.
- Swift journal·개발 client·session 회귀 10건 통과. 별도 Keychain 인스턴스가 같은 service를 가리키는 실제 simulator 검증과 local DB 응답 유실 시험을 다시 실행한다.
- `artifacts/xcode-storekit-e2e-uxr0msws/result.json` PASS/skip 0: 전용 DB `gamebridge_ci_2d66f2ac62`, 서로 다른 Keychain 객체의 같은 service 거부와 응답 유실·finish 후 삭제 실패 복구를 확인했다. 실제 프로세스 강제 종료 및 Unity player는 미검증이다.
### P05-T06 Native 저장 namespace alias 공통 수정 시작
- 같은 Keychain/Keystore namespace를 서로 다른 객체로 전달하면 기존 Mock session·pending 검사가 우회될 수 있어 양 플랫폼에서 실제 저장소 identity를 비교한다. 기존 다른 namespace 데이터는 이동·삭제하지 않는다.
### P05-T06 alias 검증 시작
- synthetic alias 객체 및 기존 복구 회귀, Android native compile을 실행한다. 실제 사용자 저장소는 건드리지 않는다.
- Android alias·복구 및 AAR compile과 Swift 복구 2건 통과. 다만 기존 공개 TokenStore protocol에 요구사항을 추가하면 기존 바이너리 구현체와 호환성이 깨질 수 있어, 선택적 별도 identity interface로 분리한다.
### P05-T06 공개 interface 호환성 재검증 시작
- 별도 선택적 identity interface와 기존 TokenStore 구현의 compile·회귀를 확인한다. 외부 바이너리 전체 호환성은 별도다.
- 선택적 identity interface로 분리한 후 Android alias·복구 및 AAR compile, Swift 6건 통과. simulator Keychain의 서로 다른 객체·같은 service 거부 및 local DB 응답 유실 시험을 다시 확인한다.
- `artifacts/xcode-storekit-e2e-43y9hasx/result.json` PASS/skip 0, 전용 DB `gamebridge_ci_2ca15a4099`: 서로 다른 Keychain 객체의 동일 service 거부와 실제 local DB commit 후 응답 유실·단서 삭제 실패 복구 재확인. Android alias는 synthetic unit과 native compile 범위다.
- 커밋 준비: 선택적 저장소 identity와 양 플랫폼 alias 보호. Xcode 공개 구매 차단·Unity 실제 검증 대기는 유지한다.

### [P00-T02] Unity 라이선스 상태 재확인
- `unity license status --json`은 로그인 상태이나 활성 라이선스 0개, 종료 4를 반환했다. 자동 라이선스 발급이나 계정 변경은 하지 않았다. ENV-002 OPEN 및 Unity Editor/player 검증 미실행을 유지한다.
### [P05-T03] Xcode 구매 차단 해제 조건 보강 시작
- local DB commit 유실·finish 후 journal 정리 E2E가 통과했지만 후보 key 충돌을 안전하게 다뤄야 한다. 개발 경로에서 iOS 18+ 및 완료 소모품 이력 opt-in을 필수로 하고, 지급 직전 StoreKit 검증된 전체 이력에서 같은 후보 key가 정확히 1건인지 검사한다. 0건은 재시도 대기, 2건 이상은 충돌로 거부한다. 실제 Apple sandbox 경로는 변경하지 않는다.
### P05-T03 충돌 guard 및 공개 경계 검증 시작
- 테스트에서 0·1·2건 판정과 host 설정 부재 차단을 확인한 뒤 공개 initializer로 실제 local DB 응답 유실 복구를 재시험한다. Unity player·실 Apple 검증과는 별개다.
- Swift 13건 통과: identity 0/1/2 판정, host 이력 설정 부재 차단 및 journal 회귀. 실제 StoreKit 이력과 공개 initializer를 사용하는 local DB E2E는 지금 실행한다.
- `artifacts/xcode-storekit-e2e-dwma413h/result.json` 1건 PASS/skip 0: 공개 Native initializer에서 검증된 전체 이력의 단일 식별자 검사, 실제 local DB commit 응답 유실, Keychain 단서 재생성, finish 직후 삭제 실패 및 완료 이력 복구를 확인했다. Unity 및 실제 Apple sandbox는 미검증이다.
- 실제 경로와 시험 경로의 불필요한 내부 enable flag를 제거하고, 동일 설정 검사를 항상 적용한다. host Info.plist와 OS 조건은 명시한다.
### P05-T03 공개 Xcode Native 경로 재검증 시작
- 불필요한 내부 enable flag 제거 후 단위 시험과 실제 local DB/StoreKit 응답 유실 복구를 다시 실행한다. host 이력 설정이 없거나 iOS 18 미만이면 차단한다.
- 단순화한 공개 경로의 `artifacts/xcode-storekit-e2e-v0xdbk5f/result.json` PASS/skip 0: iOS 18.6, 전용 DB `gamebridge_ci_d831d20ff8`, 실제 StoreKit local·서버 commit 후 응답 유실·Keychain 재생성·finish 후 삭제 실패 복구. 실제 프로세스 kill·Unity player·Apple sandbox는 미검증이다.
- 커밋 준비: host 설정·OS guard, verified StoreKit 이력 단일성 검사 및 공개 경로를 저장한다. iOS 26.5 실패와 BUG-013은 OPEN으로 유지한다.
### [P08-T03] Xcode StoreKit 개발 build 설정 자동화 시작
- host가 `GAMEBRIDGE_XCODE_STOREKIT` scripting define을 명시한 iOS Development Build에 한해 Info.plist 소모품 이력 옵션을 설정한다. 일반/Release 빌드 설정은 수정하지 않고, 명시 define과 non-development 조합은 실패시킨다. Unity export 실제 실행은 라이선스 대기다.
### P08-T03 plist hook 검증 시작
- Unity 설치본의 Xcode managed API를 사용해 기존 plist 보존·두 번 적용 멱등성을 검사한다. Unity Editor export는 아직 미실행이다.
- Unity Xcode managed API로 plist 기존 값 보존·2회 적용 멱등성 및 define 활성 조건부 compile 경고 0·오류 0 확인. non-development 조합 실패 검사는 파일 변경보다 먼저 수행하도록 정리한다. 실제 Unity export는 NOT_RUN이다.
### P08-T03 최종 hook 회귀 실행
- 재실행: PBX 파일 추가·plist 설정 멱등성 PASS, `UNITY_IOS;GAMEBRIDGE_XCODE_STOREKIT` 활성 managed compile 경고 0·오류 0. Unity Editor export와 .storekit scheme 연결 실행은 미검증이다.
- 커밋 준비: 명시적 iOS 개발 build 전용 plist hook과 synthetic managed 시험을 저장한다.

### [P09-T04] Xcode local DB 회귀 집계 시작
- 실제 Xcode StoreKit simulator 및 local DB 응답 유실·finish 후 journal 복구 시험을 명시 opt-in 회귀 lane으로 연결한다. 미실행·0건·skip·stale source는 PASS가 아니다. Apple sandbox와 Unity는 별도다.
### P09-T04 회귀 집계 검증 시작
- opt-in 없이 Xcode local DB lane이 DEFERRED_ENV로 남고, Native fake suite의 추가 시험이 통과하는지 확인한다.
- opt-in 없는 집계 `artifacts/purchase-regression-37l7snf5` 종료 2: Android fake 16, Swift fake 16 PASS, Xcode local DB lane과 미설정 DB는 DEFERRED_ENV. 이제 명시 opt-in에서 실제 증거를 재확인한다.
### P09-T04 Xcode opt-in lane 검증 시작
- opt-in 집계 `artifacts/purchase-regression-qqoq1op6/result.json`: Xcode local DB recovery 1건 PASS, Android/Swift fake 각 16건 PASS; 별도 DB·local response-loss 미설정 lane은 DEFERRED_ENV라 전체 종료 2. 실제 Apple sandbox/Unity는 아니다.
- 커밋 준비: 명시 opt-in·source 일치·비skip 확인을 포함한 구매 회귀 lane만 저장한다.

### [P11-T03] 변경 후 문서 정합성 재개
- 현재 코드와 fake/Native/실제 플랫폼 증거를 API·통합·보안·기능 매트릭스에 반영한다. Unity와 외부 스토어 미실행, 기존 StoreKit 26.5 실패를 유지한다.
### P11-T03 문서 정합성 검증 시작
- 변경 문서의 오래된 미연결·미구현 표현과 상태 원장을 점검하고 `smoke-local`의 Unity 미실행 표현을 확인한다.
- 원장·diff 검사 통과, 갱신한 문서에서 이미 연결된 Provider를 미연결로 쓰던 표현을 제거했다. `smoke-local`은 Unity player 경로가 실제 미실행이므로 계속 실패하며 NOT_RUN으로 표시한다.
- 커밋 준비: 사실 관계와 검증 범위 문서 및 smoke 상태 문구만 포함한다. 실제 Unity·외부 서비스 PASS는 없다.

### [P09-T05] 최신 Mock 푸시 E2E 재검증 시작
- Native 저장소 identity 변경 후 새 전용 DB에서 Android·Swift local Mock 발송→수신을 재실행한다. Unity player 및 FCM/APNs는 포함하지 않는다.
- `artifacts/mock-push-e2e-1sbjzmqn/result.json`: 전용 DB `gamebridge_ci_8353e458cb`에서 Android 및 Swift Native 각 1건 PASS/skip 0. Unity player·원격 발송은 미검증이다.
- 커밋 준비: 재검증 결과와 원장만 기록한다.

### [P10-T04] 최신 소스 재패키징 시작 및 검증 준비
- 저장소 alias 보호, Mock push, Xcode local recovery 및 Unity iOS hook을 포함한 현재 소스에서 Android·iOS·UPM을 새 경로로 재생성하고 별도 consumer/checksum을 확인한다. Unity import/player 및 실제 스토어는 포함하지 않는다.
- source HEAD `6a3fea5`에서 Android Maven·별도 R8 consumer 45 task 강제 재실행, iOS device/simulator XCFramework archive·simulator Swift 별도 link·device C ABI symbol 4개, UPM staging 110개 무결성 통과. 전체 192개 산출물 SHA-256/크기 재계산 결과 `docs/evidence/final-artifact-manifest.json`. 제품 소스는 커밋된 상태, 진행 문서는 빌드 당시 수정 중이었다. Unity import/IL2CPP·실기기·실스토어는 미실행이다.
- 커밋 준비: 새 산출물 manifest와 확인 범위만 기록한다. 산출물은 로컬에 보존하며 공개 배포하지 않는다.

### [P11-T04] 격리 strict local 재검증 시작
- 새 local/sandbox DB 및 synthetic 테스트 서버를 사용해 DB·Native fake·Xcode local recovery와 package 검증을 집계한다. Unity Editor와 실제 외부 서비스는 대기로 유지하고 기존 DB·사용자 파일은 삭제하지 않는다.
### P11-T04 strict local 실행
- 전용 DB·role을 새로 만들고 실제 원격 제공자 대신 synthetic key 및 local/sandbox fixture만 사용한다. 결과와 미실행 lane을 그대로 기록하며 DB·simulator는 보존한다.
- `artifacts/verify-all-f7dtxw81/summary.md` strict 종료 1: 전용 local/sandbox DB의 인증·구매·원장 mutation·푸시 synthetic 시험과 Xcode local DB recovery, Android/Swift Native mock push E2E, C#·계약·패키지 검증 PASS. Unity Editor NOT_RUN, Unity notification 및 iOS host opt-in 미제공, 49개 시나리오 PARTIAL, 기존 P05-T03 iOS 26.5 실패로 전체 FAIL; 외부 13개 WAITING_USER. 전용 DB `gamebridge_ci_d0ef0b748d_local`, `_sandbox` 보존.
- 집계의 `scenario-coverage: NOT_IMPLEMENTED`는 실제로 49개 PARTIAL을 포함해 구분이 부족했다. 사용자 요구에 맞게 PARTIAL과 NOT_IMPLEMENTED를 별도 상태로 집계하되 둘 다 전체 통과를 차단한다.
### [P09-T06] 부분 시나리오 상태 분리 시작 및 검증 준비
- 결과 분류 unit과 음성 검사를 실행하고 미검증을 PASS로 바꾸지 않는다.
- 집계 unit 12건, manifest 음성 및 원장 검사 통과. `check-required-coverage`는 `49 PARTIAL, 0 NOT_IMPLEMENTED`를 출력하고 종료 1로 전체 통과를 막는다. 이전 strict 결과는 수정 전 source의 증거로 보존한다.
- 커밋 준비: 격리 strict runner와 부분/미구현 구분만 저장한다. 실제 Unity·외부 서비스는 미실행이다.
### [P11-T04] strict 집계 누락 보강 시작
- R12가 manifest에 기록됐어도 aggregate가 해당 stress를 실제로 실행하지 않으면 최종 PASS가 될 수 있는 누락을 발견했다. 필수 lane으로 실행·건수 확인을 추가한다. iOS synthetic host simulator도 새 전용 simulator에서 실행해 미제공 lane을 줄인다.
### P11-T04 aggregate 변경 unit 검증 시작
- 집계 분류 unit과 원장 검사를 먼저 실행하고 R12 실패·0건이 통과하지 않도록 확인한다.
### P11-T04 보강된 strict 실행 시작
- 새 전용 local/sandbox DB, Xcode local 구매 복구, Native Mock push, iOS synthetic host simulator, R12 100회 stress를 함께 실행한다. Unity Editor 및 실제 외부 서비스는 별도로 대기한다.
- 보강 strict `artifacts/verify-all-4ktnqqlg/summary.md` 종료 1: R12 100회, iOS synthetic host 포함 다수 PASS이나 Xcode local DB recovery 1건 FAIL(`artifacts/xcode-storekit-e2e-mo4zgb3s/result.xcresult`), 49 PARTIAL, Unity NOT_RUN, 기존 iOS 26.5 실패, 외부 13 WAITING_USER. 문제 시험은 finish 후 단서 삭제 실패를 한 번만 주입했으나 StoreKit updates listener가 재시도해 단서를 지웠을 수 있다. 삭제 실패를 해당 인스턴스에서 지속시키고 재생성 뒤만 해제해 동작을 결정적으로 검증한다. 최초 실패는 보존한다.
### P05-T05 결정적 저장 실패 재검증 시작
- 전용 DB와 simulator에서 동일 응답 유실·finish 후 지속 삭제 실패·인스턴스 재생성을 다시 시험한다. 실패하면 구현과 테스트를 계속 조사한다.
- 지속 삭제 실패 주입으로 수정한 `artifacts/xcode-storekit-e2e-gtiqgyob/result.json` PASS/skip 0: 전용 DB `gamebridge_ci_558f36962d`, 서버 commit 후 응답 유실, Keychain 재생성, finish 뒤 지속 삭제 실패, 다음 인스턴스의 완료 이력 정리 및 잔액 100 확인. 이전 strict 실패는 그대로 보존하고 수정 후 aggregate를 재실행한다.
- 커밋 준비: 결정적 회귀 시험과 R12·iOS host 포함 aggregate 보강을 저장한다. Unity player·실기기·실 Apple은 미검증이다.

### [P11-T04] 수정 후 strict 전체 재검증 시작
- 수정한 Xcode 지속 실패 주입, R12 100회 및 iOS synthetic host를 포함해 격리 DB와 local harness를 다시 실행한다. Unity 및 외부 실연동은 미실행 상태를 유지한다.
- 수정 후 `artifacts/verify-all-vc71_h1b/summary.md` strict 종료 1: 전용 DB·synthetic 인증/구매/푸시, Xcode local DB recovery, iOS host simulator, 100회 lifecycle 등 실행된 lane PASS. 49개 시나리오 PARTIAL, Unity player DEFERRED_ENV·Editor NOT_RUN, 기존 P05-T03 iOS 26.5 FAIL로 전체 FAIL이며 외부 13개 WAITING_USER다. 전용 DB `gamebridge_ci_379100a8a9_local`, `_sandbox`와 test simulator는 보존한다.
### [P09-T08] 필수 suite 누락 감지 보강 시작
- 현재 aggregator는 1개 이상의 required lane만 있으면 개별 필수 lane 누락을 직접 알지 못한다. 알려진 필수 lane 목록을 대조하고 하나를 제거하는 음성 시험을 추가한다. 자체 self-check도 strict 집계에 실제 포함한다.
### P09-T08 필수 suite 누락 음성 검증 시작
- 알려진 required lane 하나가 결과에서 빠지면 다른 lane이 모두 PASS여도 실패하는지 unit으로 확인한다.
- 필수 lane 누락을 다른 PASS lane이 가리지 못하는 aggregate unit 포함 13건 통과. missing document/evidence 및 외부 symlink 음성 검증, manifest 음성 검증도 통과했다. self-check가 이제 strict에서 실제 실행되도록 연결했다.
- 커밋 준비: fail-closed 필수 lane inventory 및 자체 검증 연결만 저장한다. 전체 재실행은 별도로 수행한다.

### [P11-T04] 필수 suite 강화 후 strict 실행 시작
- 모든 required lane 이름과 self-check를 실제 집계에 포함해 전용 DB·simulator에서 재실행한다. 외부 서비스와 Unity Editor/player는 실행하지 않으며 기존 실패도 그대로 남긴다.

### [P09-T08] R50 필수 suite·증거 누락 게이트 시작
- 수정 후 strict `artifacts/verify-all-jqyyy3g2/summary.md` 종료 1. self-check·Native/DB/Xcode local·iOS synthetic host·100회 stress는 PASS, 49 PARTIAL·Unity 미실행 및 기존 iOS 26.5 FAIL 유지. 외부 13개 WAITING_USER. 전용 DB `gamebridge_ci_91455f1057_local`, `_sandbox` 보존.
- R50의 필수 suite 누락과 증거 누락 음성 시험을 credential 없는 독립 scenario로 연결해 실제 실행한다. 다른 시나리오 상태는 바꾸지 않는다.
### P09-T08 R50 검증 시작
- required suite 누락과 evidence 누락 음성 시험을 독립 runner로 실행한다. 플랫폼 기능 검증은 포함하지 않는다.
- `python3 harness/run-r50.py` 종료 0: required lane 누락·미실행·0건과 증거 문서 누락을 각각 거부했다. 이를 R50 하네스 범위로만 IMPLEMENTED 연결한다.
### P09-T08 R50 manifest 실행 검증 시작
- evidence/assertion mapping과 scenario entry의 실제 실행을 다시 확인한다.
- `harness/run-scenario.py R50` 및 manifest·누락 음성·원장 검사 모두 통과. strict aggregate에도 R50 자체를 필수 lane으로 추가했다. Unity 및 다른 미완료 시나리오는 그대로다.
- 커밋 준비: R50 하네스 범위의 검증 및 증거 mapping만 IMPLEMENTED로 기록한다.

### [P09-T03] 인증 scenario assertion 보강 시작
- R13/R14의 잘못된 서명·알고리즘·발급자·audience·만료를 Google/Apple synthetic test key 모두에서 검사하고, R15 nonce 불일치 뒤 challenge 미소비·정상 재시도 및 재사용 거부를 전용 sandbox DB에서 검증한다. 실제 외부 계정은 사용하지 않는다.
### P09-T03 인증 assertion 검증 시작
- 양 Provider synthetic 서명 unit과 전용 sandbox DB nonce·replay 회귀를 실행한다.
- `IdentityVerifierTest` 6건 통과: synthetic Google·Apple 양쪽의 wrong signature/algorithm, issuer/audience/expiry/nonce를 거부했다. 전용 sandbox DB 시험을 이어간다.
- sandbox DB nonce mismatch 후 미소비·정상 재시도·replay 거부와 HTTP dev endpoint 차단을 통과했다(`gamebridge_ci_35dd5c15ed`). Apple 최초 profile 누락·후속 이름·재누락 시 동일 subject 유지 assertion을 추가한다.
### P09-T03 Apple profile 누락 DB 검증 시작
- 전용 sandbox DB `gamebridge_ci_f89c70feaa`에서 Google/Apple synthetic verifier 6건, nonce/replay DB 1건, Apple profile·sandbox mock 차단 HTTP 1건 모두 PASS/skip 0. R13/R14/R15/R17/R21의 정확한 assertion과 evidence를 연결한다. 실제 Google/Apple 서비스 검증은 아니다.
### P09-T03 scenario entry 및 manifest 검증 시작
- R13/R14 독립 entry와 manifest·음성 검사 통과. R15/R17/R21이 사용하는 전체 auth-regression entry를 새 전용 sandbox DB로 재실행해 후보 suite 연결도 확인한다.
### P09-T03 auth-regression entry 검증 시작
- 전체 auth-regression `artifacts/auth-regression-ow4xd7hv/result.json` 종료 0: 전용 sandbox DB `gamebridge_ci_e092ef4315`, JWT 6·DB HTTP 2·Android fake 13·Swift fake 17 PASS/skip 0. 실 Provider 계정이나 네트워크 토큰은 사용하지 않았다.
- 커밋 준비: R13/R14/R15/R17/R21의 실제 assertion·suite·증거를 연결한다. 나머지 부분 scenario 및 외부 실연동 대기는 유지한다.

### [P09-T04] 구매 원장 scenario assertion 시작
- R23~R26 및 R31의 전용 PostgreSQL 합성 Apple grant 테스트를 대조한다. 다른 멱등키의 동일 거래와 중간 ledger 실패 rollback을 추가해 원장 원자성을 확인한다. 실제 Apple 스토어 거래는 아니다.
### P09-T04 구매 DB assertion 검증 시작
- 새 test-owned schema에만 실패 제약을 추가하고 purchase/ledger/idempotency rollback을 확인한다. 기존 사용자 DB schema는 수정하지 않는다.
- 전용 local DB `gamebridge_ci_2d069129ec`에서 10회 동시 지급 1회, 다른 attempt의 동일 거래 재요청, 같은 attempt 다른 거래 충돌, 타 계정 차단, ledger 제약으로 유도한 중간 실패 rollback이 통과했다. R25의 실제 HTTP 409도 synthetic sandbox 테스트에 추가한다.
### P09-T04 HTTP 409 회귀 검증 시작
- 전용 sandbox DB `gamebridge_ci_93ac210a09`의 synthetic Apple HTTP에서 동일 idempotency key·다른 검증 거래는 409이고 잔액은 100으로 유지됨을 확인했다. scenario별 실행 경로는 local/sandbox 전용 DB opt-in을 요구한다.
### P09-T04 scenario runner 검증 시작
- 격리 DB 두 개와 synthetic verifier로 candidate runner가 두 시험 모두 실행하는지 확인한다. 실 Apple 서버는 호출하지 않는다.
- scenario runner `artifacts/purchase-db-scenarios-18xuxp_k`: 전용 local/sandbox DB에서 각 시험 PASS/skip 0. R23~R26 및 R31의 정확한 assertion·실행 경로·증거를 연결한다. 실제 Apple store 및 Unity는 별개다.
### P09-T04 manifest·부정 검증 시작
- R23~R26·R31 manifest/assertion 검증 및 음성 검사 통과. opt-in 없는 DB scenario runner는 종료 2로 설정 부족을 표시하고 PASS를 만들지 않는다.
- 커밋 준비: synthetic DB 테스트·scenario evidence만 저장한다. 실제 Apple 검증 및 Unity는 미실행이다.

### [P09-T04] R29/R30/R39 구매 증빙 거부 검증 시작
- 합성 Apple verifier 실패·앱/상품/환경 불일치·철회·다중 수량을 실제 sandbox fixture HTTP/DB에 주입하고 지급이 추가되지 않는지 확인한다. 실제 Apple 서명이나 외부 스토어 호출은 아니다.
### P09-T04 거부·무지급 DB 검증 시작
- synthetic HTTP/DB에서 잘못된 bundle·상품·환경·철회·다중 수량 및 위조 verifier 결과가 모두 거부되고 잔액이 증가하지 않았다(`gamebridge_ci_47fb203141`). 위조 JWS의 경우 실제 Apple server library 검증기가 합성 비신뢰 서명을 거부하는 단위 시험을 추가한다. 합성 공개 test root만 저장하고 개인키는 보존하지 않는다.
### P09-T04 실제 라이브러리 forged JWS 거부 검증 시작
- 실제 Apple server library에 synthetic 비신뢰 ES256 compact JWS를 전달했을 때 거부되는 단위 시험과 Google/Apple verifier 합성 경계가 통과했다. 정상 Apple 서명·실 서버 검증은 아니다. DB scenario runner를 새 assertion 포함 상태로 다시 실행한다.
### P09-T04 verifier·DB scenario 재검증 시작
- 실제 Apple 검증기 거부 및 synthetic Google verifier 5건 `artifacts/purchase-verifier-2l6nsxv4`, local/sandbox DB runner `artifacts/purchase-db-scenarios-0_5gs2l8` PASS. R29/R30/R39는 해당 로컬 거부·무지급 범위에서만 IMPLEMENTED로 연결한다.
### P09-T04 scenario mapping 검증 시작
- strict aggregate에도 purchase verifier를 필수 lane으로 연결해 scenario IMPLEMENTED 표시만으로 실행을 생략할 수 없도록 했다.
- 커밋 준비: R29/R30/R39 synthetic 거부와 무지급 증거 및 필수 실행 연결. 실제 서명/스토어는 WAITING_USER 유지.

### [P09-T02] Core·Bridge scenario assertion 보강 시작
- 초기화 전 호출, 동일·다른 config 동시 초기화, 중복 callback과 취소/종료 경쟁을 독립 Kotlin·Swift·C# fake에서 검증한다. 실제 Unity Editor/JNI는 별도로 유지한다.
### P09-T02 Core race·parser 검증 시작
- C# 100회 cancel/shutdown race의 각 Task 완료 1회·pending 0과 Kotlin/Swift coordinator를 실행하고 중복 guard 제거 mutation을 확인한다.
- C# fake의 100회 cancel/shutdown 경쟁·중복 callback 정확히 1회 완료, 동일 config 두 호출의 단일 초기화·동일 READY 결과와 초기화 전 API 거부, Kotlin coordinator 3건, Swift coordinator 3건 통과. common contract runner에 coordinator 시험을 포함하고 duplicate guard mutation도 재실행한다.
### P09-T02 공통 runner·mutation 검증 시작
- 공통 runner는 Kotlin 7·Swift 7·C# fake 1 통과하고 duplicate guard 제거 mutation을 감지했다. R07 필수 필드 누락과 단순 malformed JSON을 양 Native parser에서 명시적으로 추가한다.
### P09-T02 malformed·필수 필드 재검증 시작
- `artifacts/contracts-p2sh2c22` Kotlin 7·Swift 7·C# fake 1 suite PASS, malformed/필수 필드 음성 fixture 및 원본 보존 확인. R01/R02/R03/R04/R06/R07/R10의 assertion을 로컬 fake 범위로 연결한다. Unity Editor/JNI는 포함하지 않는다.
### P09-T02 scenario mapping 검증 시작
- manifest 검증은 통과했으나 음성 검사에서 기존 첫 scenario가 이제 IMPLEMENTED여서 변조 대상이 더 이상 미완료 항목이 아닌 문제가 발견됐다. 원본을 건드리지 않는 격리 사본에서 첫 PARTIAL을 선택해 변조하도록 고친다. 수정 전 음성 검사는 FAIL로 기록한다.
### P09-T02 manifest 음성 검사 재실행
- 격리 manifest 음성 검사 수정 후 원장·manifest 통과, 필수 시나리오 28개 PARTIAL로 전체 gate는 계속 실패한다. 새로 연결한 각 Core scenario entry를 순차 재실행한다.
### P09-T02 개별 scenario entry 검증 시작
- `harness/run-scenario.py` R01/R02/R03/R04/R06/R07/R10 각각 종료 0. R04는 별도 guard mutation 감지도 통과했다. Kotlin/Swift unit 및 독립 C# fake 결과이며 Unity Editor/JNI 실행은 아니다.
- 커밋 준비: 새 assertion, 공통 runner, 부분 scenario의 근거 있는 로컬 범위 승격 및 음성 검사 유지 보정만 포함한다.

### [P09-T02] R05/R08 늦은 응답·길이 경계 시작
- timeout 이후 응답이 Task를 다시 완료하지 않더라도 검증된 별도 거래 이벤트는 전달되는지, Swift C ABI 음수·과대 길이에서 메모리를 읽지 않고 생존하는지 확인한다. 실제 Unity JNI는 별도다.
### P09-T02 timeout·C ABI 검증 시작
- Kotlin dispatcher·Swift C ABI 및 독립 C# registry를 공통 runner로 실행한다. 과대 pointer 길이는 실제 할당보다 큰 값으로 전달하되 guard가 읽기 전에 거부해야 한다.
- `artifacts/contracts-aoe84z1m`: Kotlin 10·Swift 11·C# fake 1 suite PASS/skip 0. 늦은 callback 뒤 구매 이벤트 보존과 음수·과대 C ABI 길이 거부를 확인해 R05/R08 로컬 범위 assertion을 연결한다.
### P09-T02 R05/R08 scenario 검증 시작
- R05·R08 개별 entry, manifest 음성·원장 및 duplicate guard mutation 재실행 통과. 실제 JNI/Unity player는 별도다.
- 커밋 준비: timeout 후 이벤트 및 Swift C ABI 입력 경계 시험과 로컬 scenario evidence만 저장한다.

### [P09-T05] R44/R45/R46 회귀 보강 시작
- 초기화 전 클릭의 READY 후 전달과 중복·route 제한을 양 Native/C# fake에서 확인하고, 실제 pending 단서를 만든 뒤 점검 중 신규 구매 차단·기존 복구 허용을 양 Native에서 검증한다. 실제 OS 알림·Unity player는 별도다.
### P09-T05 점검 중 pending 복구 검증 시작
- 양 Native에서 신규 구매는 MAINTENANCE로 거부하고 기존 pending은 같은 idempotency 단서로 복구되는지 synthetic HTTP로 시험한다.
- Android synthetic router·payload·pending 恢復 및 Swift 4건 PASS: 점검 중 신규 구매는 MAINTENANCE로 차단됐고 기존 pending은 같은 단서로 복구됐다. C# fake cold click과 함께 전용 runner로 재실행한다.
### P09-T05 router/maintenance scenario runner 검증 시작
- `artifacts/push-router-scenarios-ohmtb_j0`: 양 Native router·점검 중 pending 복구와 C# cold event fake PASS. R44/R45/R46에 정확한 assertion을 연결하고 strict aggregate에서도 필수 실행한다. 원격 알림·Unity는 미검증이다.
### P09-T05 scenario mapping 검증 시작
- R44/R45/R46 manifest·부정 검사·원장 검사 통과, 나머지 23개는 PARTIAL로 유지한다. strict runner도 해당 synthetic lane 실행을 요구한다.
- 커밋 준비: router 및 점검 중 pending 복구의 검증·evidence만 포함한다. 실제 Unity/OS 알림은 미검증이다.

### [P09-T05] R47/R48 패키지 음성 검증 시작
- Android의 새 소비 프로젝트에서 필수 전이 의존성을 제거했을 때 실제 build가 실패하는지 확인하고, iOS XCFramework의 slice·C ABI symbol을 package 전에 검사한다. 모든 손상은 새 격리 사본에만 적용하며 기존 산출물은 보존한다.
### P09-T05 XCFramework 기본 검증 시작
- 최신 iOS 실제 산출물의 architecture와 C ABI symbol을 각 architecture별로 확인한다. 실제 기기 실행은 포함하지 않는다.
### P09-T05 패키지 누락 실제 음성 검증 시작
- 새 Android 소비 프로젝트의 정상 R8 build 뒤 복사본에서 sdk-core JAR만 제거해 실제 Gradle 오류를 확인한다. iOS는 새 XCFramework 복사본에서 simulator slice와 device C symbol을 각각 제거해 검출한다. 원본 artifact는 수정하지 않는다.
- Android 새 consumer baseline R8 성공 뒤 복사본 sdk-core JAR 제거로 예상된 Gradle dependency 오류 검출(`artifacts/android-dependency-negative-2v90vblk`). iOS 실제 framework 통과 후 격리 사본의 simulator binary 및 device C symbol 누락을 각각 검출(`artifacts/ios-xcframework-negative-os4u5n1z`). package script에 실제 arch/symbol 검증을 추가했다. 원본은 보존했다.
### P09-T05 패키지 scenario mapping 검증 시작
- 각 scenario entry를 실제 opt-in artifact로 실행하고 manifest 음성 검사를 확인한다.
- R47/R48 개별 entry 재실행과 manifest 음성 검사 통과. 새 `artifacts/upm-validated-20261111` 생성 시 XCFramework arch/C ABI 선검사와 110개 staging checksum 통과. Unity import/export는 실행하지 않았다.
- 커밋 준비: 패키지 선검사 및 격리 consumer/artifact 음성 시험과 새 UPM 해시를 기록한다.

### [P09-T04] R33 Google 완료 처리 실패 재시도 시작
- 기존 consume fake 실패 재시도 DB 시험에 non-consumable acknowledge 실패·worker 재생성·재시도와 entitlement/원장 불변을 추가한다. 실제 Google 호출은 하지 않는다.
### P09-T04 Google ACK/consume DB 검증 시작
- 새 전용 local DB와 test-owned schema에서 consume·ack 실패 후 worker 재생성, retry 및 확인 후 암호화 증빙 삭제를 확인한다.
- `gamebridge_ci_584b8f5ac2`에서 Google synthetic consume와 acknowledge 각각 실패→worker 재생성→retry→확인 뒤 암호화 증빙 삭제 및 원장/entitlement 불변 통과. 실제 Play API 호출은 없다. 이를 scenario runner에 포함해 재검증한다.
### P09-T04 Google 최종화 scenario runner 검증 시작
- `artifacts/purchase-verifier-34g3k75m` 7건 및 전용 DB `gamebridge_ci_92bb74bec6_local/_sandbox`의 `artifacts/purchase-db-scenarios-cye0z6z8` PASS. R33에 consume·ack durable retry assertion과 evidence를 연결한다. 실제 Google Play는 미검증이다.
### P09-T04 R33 mapping 검증 시작
- R33 manifest·필수 scenario 음성·원장 검사 통과. 다른 20개 scenario는 PARTIAL, 외부 실연동은 대기로 유지한다.
- 커밋 준비: synthetic Google ACK/consume retry 시험과 증거 연결만 저장한다.

### [P04-T04] BUG-016 발견 및 작업 시작
- Google/Apple Provider는 요청 직전 profile에서 만료를 갱신하지만, 실제 인증된 Backend 요청 자체가 그 후 401을 반환하면 자동 refresh/retry하지 않는 누락을 발견했다. 재시도 시 구매 증빙 idempotency key를 유지하고 계정 변경·취소·반복 401을 안전하게 처리한다. R18은 미완료로 유지한다.
### P04-T04 Android 인증 요청 401 수정 시작
- Android Provider의 authenticated operation 401에서 잠금 안 단일 refresh 후 1회만 재시도한다. 구매 검증 attempt UUID는 재시도 전 생성해 동일하게 유지한다. 사용자 변경·취소·재시도 실패는 기존 오류 정책을 유지한다.
### P04-T04 Android 401 검증 시작
- 동시 10개 호출·반복 401의 1회 재시도 한도·구매 proof attempt UUID 동일성을 fake Provider로 검사한다. 실제 Google 로그인은 포함하지 않는다.
- Android synthetic Provider에서 동시 10개 호출은 lock으로 직렬화돼 실제 401을 받은 첫 호출만 refresh했고 모두 성공했다. 반복 401은 두 번 호출 후 중단했고 구매 검증 attempt UUID는 재시도 전후 동일했다. refresh 후 계정 불일치도 재시도하지 않는지 추가 검증한다.
### P04-T04 Android 계정 일치 회귀 시작
- Android Google fake에서 refresh 후 profile 소유자 불일치 시 AUTH_FAILED, 재시도 0회, refresh tombstone 보존을 확인했다. 전체 GoogleAuthProviderTest 통과. 실제 Google credential/UI는 미검증이다.
- 커밋 준비: Android 요청 401의 단일 refresh 및 purchase attempt 보존만 저장한다. iOS와 전체 동시 401 검증이 남아 BUG-016 OPEN이다.
### P04-T04 iOS 인증 요청 401 수정 시작
- Apple Provider의 기존 refresh single-flight를 profile 및 실제 Backend 요청 401에서 공유한다. 같은 계정 검증 후 1회만 재시도하며 StoreKit proof의 idempotency key는 재시도 전 생성한다.
### P04-T04 iOS 기존 refresh 회귀 검증 시작
- 우선 기존 Apple fake 인증·single-flight·취소·로그아웃 회귀를 실행한다. 이후 10개 실제 요청 401과 동일 attempt 재시도를 별도 검증한다.
- iOS 기존 Apple Provider fake 13건 통과. 실제 요청 경계에서 10개 동시 401, 반복 401 제한, refresh 중 logout, StoreKit proof 동일 idempotency key를 별도 fake 시험한다.
### P04-T04 iOS 401·계정 경계 검증 시작
- iOS fake 17건 통과: 실제 action의 401 10건이 refresh 1회 공유, 반복 401 재시도 1회, refresh 중 logout 취소 및 StoreKit proof 동일 attempt. 추가 검토에서 refresh된 session의 profile을 저장 전에 확인해야 잘못된 계정이 저장되지 않으므로 보강한다.
### P04-T04 iOS refresh 소유권 재검증 시작
- iOS Provider fake 18건 통과: action 401 10개가 refresh 1회를 공유하고 같은 요청을 1회만 재시도, logout 시 취소, profile 불일치 시 tombstone 유지, StoreKit proof UUID 재사용을 확인했다. Android는 동시 호출을 lock으로 직렬화한다. 실제 플랫폼·실 Backend 동시 만료는 별도다.
### P04-T04 Native build 회귀 시작
- Android AAR 및 iOS simulator framework를 새 격리 project에서 compile한다. 실제 Google/Apple 인증은 실행하지 않는다.
- Android AAR 53 task 및 iOS simulator framework compile 종료 0. iOS는 기존 Xcode 환경 guard의 중복 availability 경고가 있어 단순화한다. BUG-016의 코드 경계는 양쪽 fake 동시 요청·반복 401·소유권·동일 증빙 key 검증으로 해소했으며 실제 기기 및 실 Provider는 별도 대기다.
### P04-T04 iOS guard 단순화 재검증 시작
- iOS Apple Provider·StoreKit fake 25건 통과, simulator framework 재컴파일 종료 0(중복 availability 경고 제거). BUG-016 해결은 Native fake/compile 범위이며 실제 플랫폼·실 Backend 동시 401은 아직 미실행이다.
- 커밋 준비: iOS 공유 refresh·요청 재시도·StoreKit proof idempotency 및 fake 시험을 저장한다. 외부 인증 대기는 유지한다.

### [P09-T03] R16/R18 Provider fake 회귀 시작
- Google/Apple 취소 시 세션 미저장, iOS 동시 10개 요청 401의 단일 refresh, Android 10개 호출의 직렬화와 단일 refresh를 전용 DB 포함 auth-regression으로 재실행한다. 실 Provider 계정은 사용하지 않는다.
- `artifacts/auth-regression-qp1sjplw` 전용 DB `gamebridge_ci_064dab9080`의 backend 6+2·Android fake 17·Swift fake 22 PASS/skip 0. R16/R18을 synthetic Provider 범위로 연결한다. Android는 10개 호출을 직렬화해 실제 401은 1개이고, iOS는 10개 401이 1회 refresh를 공유한다. 실제 Provider는 미검증이다.
### P09-T03 R16/R18 mapping 검증 시작
- R16/R18 manifest·음성·원장 검사 통과. P04-T04의 실 Backend 동시 만료·실기기 검증은 별개로 PARTIAL이다.
- 커밋 준비: Provider fake assertion과 evidence만 연결한다.

### [P09-T03] R19 refresh replay 검증 시작
- 전용 local 서버에서 실제 HTTP로 refresh rotation 후 이전 token 재사용, 동일 family 폐기, 다른 family 보존 및 재로그인을 확인한다. 기존 default DB를 직접 수정하는 smoke 경로는 사용하지 않는다.
### P09-T03 refresh replay HTTP 검증 시작
- 새 local DB와 loopback 서버를 만들고 Native 실행 opt-in 환경에서만 자체 생성 세션을 시험한다. 기존 세션은 건드리지 않는다.
- 전용 DB `gamebridge_ci_86c05d06d1` HTTP 시험에서 오래된 refresh 재사용 후 해당 family의 access/refresh가 거부되고, 다른 family와 재로그인은 유지됐다. Python 최적화 옵션이 assertion을 제거해 false PASS를 만들지 않도록 명시적 검증 함수로 보강한다.
### P09-T03 refresh replay 최적화 모드 음성 검증 시작
- 명시적 optimized-mode local HTTP 재시험(`gamebridge_ci_58132ab74a`)과 잘못된 응답을 주는 별도 synthetic 서버 음성 검증 모두 의도대로 통과했다. R19를 local mock HTTP 범위로 연결하고 strict에 필수 lane을 추가한다.
### P09-T03 R19 mapping 검증 시작
- R19 assertion·manifest 및 음성 검사 통과, 나머지 17 scenario는 PARTIAL이다. 실제 Apple/Google 계정 검증은 포함되지 않는다.
- 커밋 준비: 격리 local HTTP replay test와 fail-closed aggregate 연결만 저장한다.

### [P09-T04] R27/R28/R35 pending·검증 실패 회귀 시작
- Play fake에서 같은 거래의 PENDING→PURCHASED 및 중복 검증을 확인하고, timeout/검증 실패 시 미완료 상태를 검사한다. Xcode local StoreKit은 응답 유실 뒤 unfinished 보존을 확인한다. 실 Play/Apple은 실행하지 않는다.
### P09-T04 Play pending/timeout 검증 시작
- synthetic Play gateway의 PENDING→PURCHASED·중복 지급 방지와 timeout 후 pending을 실행한다. Google DB의 PENDING proof는 purchase/job 생성 전 거부되어야 한다.
- Android Play Provider fake의 PENDING→PURCHASED·중복 1회 지급 및 timeout 후 VERIFICATION_PENDING→복구가 통과했다. Google PENDING proof의 DB 무지급과 Xcode local 미완료 거래 보존을 검증한다.
### P09-T04 Google pending DB 검증 시작
- 전용 DB `gamebridge_ci_9870ea16ad`에서 Google synthetic PENDING proof가 purchase/finalization job을 만들지 않음을 확인했다. Apple 공식 StoreKitTest Ask to Buy 설정 문서(https://developer.apple.com/documentation/storekittest/sktestsession/asktobuyenabled)에 따라 별도 simulator에서 실제 Xcode pending이 fake grant에 도달하지 않는지 검증한다.
### P09-T04 Xcode Ask to Buy pending 검증 시작
- `artifacts/storekit-pending-1794339452.xcresult`: iOS 18.6 전용 simulator Ask to Buy pending 1건 PASS/skip 0, 서버 grant 호출 없음. 테스트 코드의 async NSLock 사용 경고는 동기 helper로 정리했다. 대기 거래는 전용 simulator에 보존한다.
### P09-T04 Xcode timeout 후 unfinished 확인 시작
- local DB commit 후 synthetic 응답 유실에서 StoreKit unfinished가 실제로 남고, 복구 후 없어지는 assertion을 추가해 재실행한다.
- `artifacts/xcode-storekit-e2e-azc6m12g/result.json` 1건 PASS/skip 0: 전용 DB `gamebridge_ci_8bb91acbd1`에서 서버 commit 후 응답 유실 시 실제 Xcode transaction이 unfinished로 남고, 재생성 복구 후 finish·journal 삭제 및 잔액 100을 확인했다. 실제 프로세스 kill·Unity/Apple sandbox는 아니다.
### P09-T04 pending scenario runner 검증 시작
- Android fake 전용 entry의 실행 건수와 Xcode DB runner opt-in 부재 시 미실행 처리를 확인한다.
- `artifacts/play-pending-08y6r7o4` Play fake 17건 PASS. Xcode wrapper는 opt-in이 없을 때 종료 2였다. 명시 opt-in wrapper의 실제 결과·source·skip 검사를 재확인한다.
### P09-T04 Xcode opt-in entry 재검증 시작
- 명시 opt-in Xcode entry `artifacts/xcode-storekit-e2e-71smgiej` PASS/skip 0. Play fake와 전용 DB assertion을 조합해 R27/R28/R35를 로컬 synthetic/Xcode 범위로 연결한다. 실제 Play/Apple 서버와 Unity는 미검증이다.
### P09-T04 pending mapping 검증 시작
- manifest/음성/원장 검증 통과, 14개 scenario PARTIAL 유지. 신규 Google PENDING assertion을 포함한 local/sandbox DB scenario runner 전체를 새 DB에서 확인한다.
### P09-T04 pending 포함 DB runner 재실행
- 신규 pending assertion 포함 DB runner `artifacts/purchase-db-scenarios-bdz2e9vh`, 전용 `gamebridge_ci_534be12e3b_local/_sandbox` PASS. 시나리오에 필요한 각 suite를 실행했다.
- 커밋 준비: pending/검증 실패 회귀, Xcode unfinished assertion 및 explicit opt-in entry를 저장한다. 실제 스토어·프로세스 kill·Unity는 미검증이다.

### [P09-T04] R32/R36/R37/R38 구매 복원·소유권 검증 시작
- 전용 local DB의 Native 소비 잔액·비소모성 복원을 확대하고 synthetic Apple DB의 entitlement 중복 방지 및 계정 전환 보호 assertion을 대조한다. 실제 Play/Apple/Unity는 별도다.
### P09-T04 non-consumable DB 검증 시작
- 전용 test schema에서 같은 non-consumable 거래를 다른 attempt로 재검증해 entitlement 한 건만 유지하는지 확인한다. 기존 DB는 변경하지 않는다.
- synthetic Apple DB `gamebridge_ci_84c1faaad9`에서 비소모성 동일 거래 재검증 시 entitlement 한 건과 동일 purchase ID를 확인했다. Native의 소모성 잔액·비소모성 복원과 commit 응답 유실을 전용 local 서버로 함께 실행한다.
### P09-T04 구매 복원 전체 runner 검증 시작
- `artifacts/purchase-regression-jclkbpp1/result.json`: 전용 DB `gamebridge_ci_be36c79f67_local/_sandbox`, Android fake 18·Swift fake 16·각 Native local 2건 및 Xcode local DB 1건 등 전체 PASS. 복원 이후 과거 소모성/비소모성 거래를 다시 검증해도 지급되지 않는 assertion을 추가해 재실행한다.
### P09-T04 복원 후 재지급 방지 재검증 시작
- `artifacts/purchase-regression-hnncaxbh` 전체 PASS/skip 0: 전용 `gamebridge_ci_248eb1b40b_local/_sandbox`. 복원 후 동일 소모성·비소모성 거래 재검증에도 재지급 없고 synthetic Apple entitlement 한 건, 계정 전환 시 binding 보호를 확인했다. R32/R36/R37/R38을 로컬 Mock·synthetic 범위로 연결한다. 실제 프로세스 kill·스토어·Unity는 미검증이다.
### P09-T04 복원 scenario mapping 검증 시작
- R32/R36/R37/R38 manifest·필수 coverage 음성·원장 검사 통과, 10개 scenario는 PARTIAL로 남긴다. 개별 suite는 격리 DB opt-in을 요구하며 정상 Provider 시험을 대체하지 않는다.
- 커밋 준비: 복원 assertion·runner 및 검증 범위 evidence만 저장한다.

### [P09-T05] R41/R42 푸시 token 소유권 검증 시작
- 전용 local DB/HTTP에서 token 회전 시 한 installation의 이전 token이 교체되고 logout 직후 삭제되며 다른 사용자 로그인 시 소유가 바뀌는지 검증한다. 실제 FCM/APNs 발송은 없다.
### P09-T05 token 회전·소유권 DB 검증 시작
- 새 전용 DB에서 실제 local HTTP/security 및 암호화 token row를 검증한다. synthetic token만 사용한다.
- 전용 local DB `gamebridge_ci_f32d3b9216`에서 기존 사용자 소유 중 타 사용자 등록 403, token 회전 후 옛 hash 미존재, logout 시 삭제, 다른 사용자 재등록·logout 삭제가 통과했다. stale invalidation 방지 및 Android host rotation fake와 함께 scenario runner로 확인한다.
### P09-T05 token 소유권 runner 검증 시작
- `artifacts/push-ownership-b0926wkl`, 전용 DB `gamebridge_ci_bd89663e7b`: token 회전·logout 후 다른 사용자 소유권 전환, stale invalidation 보호 및 Android host fake PASS. R41/R42는 local/synthetic 범위로 연결하고 strict에서 필수 실행한다. 실제 FCM/APNs는 미검증이다.
### P09-T05 R41/R42 mapping 검증 시작
- R41/R42 manifest·누락 음성·원장 검사 통과. 나머지 8개는 PARTIAL이며 Unity 및 실제 원격 푸시는 대기다.
- 커밋 준비: 격리 HTTP/DB ownership 시험과 scenario runner·strict 연결만 저장한다.

### [P09-T05] R43 iOS host delegate 보존 검증 시작
- 전용 simulator에서 기존 notification delegate를 보존하고 Host completion callback을 호출하는지 synthetic 입력으로 검증한다. Unity host·실 APNs는 별도다.
### P09-T05 iOS delegate simulator 검증 시작
- 사용자 기존 simulator가 아닌 새로운 전용 iOS 18.6 simulator에서 synthetic host callback을 시험한다.
- 전용 iOS 18.6 simulator `193C8CC2-18B0-46A4-827C-4AAFAC245D47`, `artifacts/push-delegate-1794340271.xcresult` 1건 PASS/skip 0: 기존 UNUserNotificationCenter delegate가 adapter 생성·전달 뒤 유지되고 sample remote callback completion이 호출됐다. 실제 APNs 및 Unity host 동작은 미검증이므로 R43은 PARTIAL 유지한다.
- 커밋 준비: 실제 iOS simulator synthetic host assertion만 기록한다.

### [P09-T04] R34 Xcode 앱 프로세스 복구 시작
- 별도 simulator 전용 테스트 앱에서 local 서버 commit 후 응답 유실·unfinished 보존을 확인하고 앱 프로세스를 실제 종료한 뒤 새 프로세스의 Keychain 복구·finish·잔액 불변을 검증한다. 기존 사용자 앱·simulator는 건드리지 않으며 실 Apple sandbox/Unity와 구분한다.
### P09-T04 프로세스 테스트 앱 compile 검증 시작
- 전용 iOS simulator 테스트 app을 ad-hoc 서명으로 build한다. 실제 실행·종료와 local DB는 다음 단계다.

- P09-T04 R34 빌드 FAIL: 일반 앱 타깃에 StoreKitTest framework 검색 경로가 없어 모듈을 찾지 못했다. simulator SDK Developer/Library/Frameworks 경로를 확인했으며 테스트 타깃에만 적용한다. 실행 검증은 아직 미실행이다.
- P09-T04 R34 테스트 앱 재빌드 PASS. 다음으로 별도 DB·simulator와 두 프로세스를 사용하는 실행 하네스를 작성한다.
### P09-T04 R34 실제 프로세스 종료 검증 시작
- opt-in runner는 별도 simulator 및 DB를 생성해 보존하며 합성 인증과 Xcode 로컬 StoreKit만 사용한다.
- 첫 R34 실행 `artifacts/xcode-process-recovery-i569kmy7` FAIL: 프로젝트 생성 진단이 경로에 혼입됐다. 전용 DB·simulator는 보존했고 앱 종료·복구는 미실행이다.
- P09-T04 R34 생성 결과의 마지막 줄을 프로젝트 경로로 사용해 새 전용 환경에서 재실행한다.
- R34 `artifacts/xcode-process-recovery-ajl4a6cr` FAIL: 테스트 앱 빌드·설치는 통과했으나 prepare 단계에서 INTERNAL_ERROR. 어떤 세부 단계인지 확인되지 않아 결론을 보류한다.
- R34 테스트 전용 실패 상태에 단계·오류 형식만 포함해 원인을 좁힌다. 토큰·거래 증빙은 기록하지 않는다.
- `artifacts/xcode-process-recovery-qrz8pvrt`에서 첫 프로세스 pending 및 종료 확인. 새 프로세스 재시작 이후 INTERNAL_ERROR가 발생했으며 wallet·recover·assertion 단계도 분리해 조사한다.
- R34 재시작 후 잔액·추가 복구 건수·journal 존재 여부를 비밀값 없이 각각 확인한다.
- R34 재시작 시 잔액 100·미완료 거래 0·pending journal 존재로 검증 FAIL (`artifacts/xcode-process-recovery-b49vwcfs`). 거래가 새 Xcode StoreKit 테스트 세션에서 노출되지 않는 원인은 미확정이며 임의 journal 삭제는 안전하지 않다. 재현 하네스와 실패 증거를 저장한다.
- 커밋 준비: 테스트 전용 앱·격리 runner 및 실패 기록. 실제 플랫폼 검증과 R34 완료로 표시하지 않는다.
### P11 최종 산출물 및 변경 이력 감사 시작
- 계획에서 요구한 문서 존재 여부와 현재 구현·검증 근거를 확인한다. 진행 중인 R34 실패와 외부·Unity 대기를 완료로 기록하지 않는다.
### P08 최신 제품 소스 재패키징 검증 시작
- 이전 산출물은 최근 인증 변경 이전 소스이므로 현재 커밋 기준 새 경로에서 Android 독립 consumer와 iOS XCFramework 및 UPM checksum을 검증한다.
- P08 Android `artifacts/maven-2bc9d77`: mock sample·로컬 Maven 및 독립 R8 release consumer PASS (45개 실행). iOS device/simulator archive를 새 경로에 생성한다.
- P08 `artifacts/ios-2bc9d77/GameBridgeNative.xcframework` 생성·arch/symbol 검사 PASS, `artifacts/upm-2bc9d77` 체크섬 PASS. 이전 산출물을 보존했다. strict runner가 특정 오래된 경로를 고정하고 있어 환경변수 override를 추가한다.
### P09 최신 산출물 strict-local 검증 시작
- strict runner에 산출물 경로 override를 추가하고 2bc9d77 제품 소스의 새 패키지 및 격리 DB·simulator로 실행한다.
- P11 `docs/CHANGELOG.md` 신규 작성. FINAL_REPORT에 R34 재시작 FAIL과 2bc9d77 재패키징·무결성 결과를 기록했으며 Unity import는 미실행으로 유지한다.
- P11 감사에서 PROGRESS 상단 BUG-013 및 요약이 실제 구현보다 오래된 것을 발견해 재시작 FAIL과 Unity 미검증으로 정정했다. strict runner와 재현 runner의 Python 컴파일은 통과했다.
### P09-T04 R34 이력 노출 원인 조사 시작
- 테스트 앱에 StoreKit transaction 건수만 추가해 재시작 직후 노출 상태를 확인한다. strict 검증과 별개이며 실제 기기 결론은 내리지 않는다.
- 재시작 직후 transaction history 및 unfinished 건수 계측을 추가했다. 원격 스토어·거래 원문은 수집하지 않는다.
- R34 runner가 sourceDirty를 무조건 true로 기록하는 부정확한 표현을 실제 작업 트리 확인으로 교체했다.
- R34 재시작 직후 이력과 미완료 건수 계측을 별도 simulator·DB에서 실행한다. 다른 strict suite와 데이터는 분리한다.
- strict `artifacts/verify-all-2cnr0y99/summary.md` 종료 1: 실행된 Native synthetic·local DB·하네스/패키지 음성 검사는 PASS, Unity Editor NOT_RUN·Unity push DEFERRED_ENV·시나리오 PARTIAL 및 기존 unresolved FAIL로 전체 FAIL. Xcode local DB 복구 PASS는 프로세스 종료 복구 실패와 별개다. 외부 13개는 WAITING_USER.
- R34 이력 계측 재실행 FAIL: 새 프로세스의 historyBefore=1, unfinishedBefore=1, 복구 후 잔액 100·unfinished 0·journal 잔존 (`artifacts/xcode-process-recovery-b7metfgc`). 이력 유실로 단정하지 않고 listener와 복구 경로의 중복 처리를 조사한다.
- R34에서 unfinished 0은 listener의 journal 정리가 끝났다는 보장이 아니다. 테스트에 최대 10초 유한 대기를 추가해 최종 journal 상태를 확인하고 미완료라면 계속 FAIL로 둔다.
- 별도 프로세스 복구에서 비동기 journal 정리 완료를 최대 10초 기다리는 시험을 실행한다.
- R34 이력 1·unfinished 1에서 재시작 후 10초간 기다려도 잔액 100·unfinished 0·journal 잔존. 단순 비동기 지연 가설은 현재 결과로 기각한다.
- R34 테스트 전용 TokenStore wrapper에 save/clear 호출 및 오류 횟수를 기록한다. 값이나 식별자는 기록하지 않는다.
- 새 격리 simulator에서 Keychain 호출 횟수와 비동기 완료 대기를 함께 시험한다.
- R34 clear 1회 성공·save 1회, 잔액 100·unfinished 0·journal 잔존 확인. listener와 recovery가 같은 거래를 순차 처리해 완료 후 attempt가 재생성되는 경로로 좁혔다. Xcode local 검증 직전에 해당 거래가 여전히 unfinished인지 검증하는 방안을 적용한다.
- Xcode local sink가 history 단일성에 더해 현재 unfinished 일치를 검사한 후에만 attempt를 생성하도록 변경했다. 실 Apple sandbox 경로는 해당하지 않는다. 우선 프로세스 재시작 시험을 실행한다.
- R34 수정 후 전용 iOS 18.6 simulator·DB에서 첫 프로세스 종료와 두 번째 프로세스 복구 PASS (`artifacts/xcode-process-recovery-vm_w1hpt`): 중복 지급 없이 잔액 100, unfinished 0, journal 없음. Xcode local fake 범위이며 실제 플랫폼이 아니다. 기존 local DB/Swift 회귀를 재실행한다.
- R34 통과가 정리 직후 일시 상태일 가능성을 막기 위해 1초 관찰 및 recover 프로세스의 새 journal save 0회 검증을 추가했다. 강화된 시험은 재실행 예정이다.
- Xcode local sink 변경에 대한 Swift package unit tests를 실행한다. StoreKit simulator E2E와 범위를 구분한다.
- `swift test --package-path ios` 종료 0: XCTest 77건, 실패 0, skip 7; 추가 Swift Testing suite 0건. macOS host unit 범위다.
- 강화된 R34 프로세스 시험을 전용 DB·simulator에서 재실행한다.
- 기존 Xcode local StoreKit + DB 응답 유실·Keychain journal 복구 재시험 PASS (`artifacts/xcode-storekit-e2e-lk2ae3ys`, 1 pass, skip 0). 실제 Apple sandbox는 미실행.
- 강화 R34 `artifacts/xcode-process-recovery-f_w2fsya` PASS: 서로 다른 두 PID, 잔액 100, unfinished 0, journal 제거 및 재생성 없음 확인. Xcode simulator local fake만 증명하며 Unity·실기기·Apple sandbox는 미검증이다. 누락 방지를 위해 strict 필수 lane과 manifest 연결을 추가한다.
- R34 evidence와 manifest assertion, 구매 regression 및 strict 필수 lane을 추가했다. manifest 및 fail-closed 검사를 실행한다.
- `harness/check-regression-manifest.py`는 존재하지 않아 검증을 실행하지 못했다. 저장소의 실제 manifest 검사 명령을 확인한다.
- `harness/check-manifest.py`와 음성 검사로 연결 및 assertion 참조를 검증한다.
- `python3 -m unittest discover -s harness -p test_aggregation.py -v` PASS(13 tests). `harness/check-progress.py`는 존재하지 않아 원장 검사는 미실행; 실제 경로를 확인해 다시 실행한다.
- `scripts/verify-progress.py`로 진행 원장 일관성을 확인한다.
- R34 강화 시험 PASS 및 기존 Xcode DB 회귀 PASS, Swift 77건 중 skip 7·실패 0, manifest/음성·집계 13건·진행 원장 검사 PASS. 커밋 준비: 중복 attempt 방지, 재현 하네스, strict 연결 및 문서만 저장한다. 최신 패키지는 이 수정 전이므로 다시 빌드한다.
### P08 수정 후 패키지 재검증 시작
- e9b64fb iOS 중복 복구 수정이 이전 XCFramework에 없으므로 별도 산출물을 생성한다. Android 제품 입력의 변경 여부를 검사하고 수정이 없을 때 기존 R8 검증 산출물을 재사용한다.
- `git diff 2bc9d77 e9b64fb -- android` 변경 없음. iOS device/simulator archive PASS (`artifacts/ios-e9b64fb`); 기존 `maven-2bc9d77`와 묶어 새 UPM staging을 검증한다.
- `artifacts/ios-e9b64fb/GameBridgeNative.xcframework` arch/symbol 및 `artifacts/upm-e9b64fb` checksum PASS; 파일별 hash `docs/evidence/artifacts-e9b64fb.json`. Android 제품 소스 무변경으로 2bc9d77 R8 산출물 재사용. 새 R34 필수 lane 포함 strict-local을 전용 환경에서 재실행한다.
### P09-T03 R20 offline logout 증거 감사 시작
- 기존 Native fake와 Unity 경계 테스트가 요구 결과를 실제 검증하는지 확인하고 부족한 경우 보강한다.
- R20 Android `GoogleAuthProviderTest`와 iOS `AppleAuthProviderTests`는 token 삭제와 revoke 미확인 오류를 실제 assertion으로 확인한다. `artifacts/verify-all-2cnr0y99`의 관련 synthetic suite PASS. 증거 `docs/evidence/offline-logout.md`를 추가했다.
### P09-T02 R09 문자열 경계 감사 시작
- Native C ABI 및 Android JNI에서 한글·emoji 복사와 callback 이후 소유권이 실제로 검증되는지 확인한다.
- R09 `CBridgeTests.testCopiedUTF8AndCorrelatedResponse`는 iOS 문자열 복사를 검증한다. Android JNI 경계의 동일 문자열 및 메모리 수명 실행 근거가 없어 완료로 승격하지 않는다.
### P09-T05 R40 푸시 권한 거부 감사 시작
- Native fake와 simulator 시험이 시스템 권한 거부 후 상태와 crash 방지를 모두 검증하는지 확인한다.
- R40 기존 push 테스트 검색에서 OS 거부 시나리오 실행 assertion은 확인되지 않았다. 실제 권한 팝업·설정 검증 없이 완료로 변경하지 않는다.
### P09-T02 R22 진단·결과 redaction 감사 시작
- token·증빙을 synthetic 값으로 주입한 회귀가 Native 로그와 Unity 결과에 적용되는지 검토한다.
- zsh의 미일치 glob 때문에 첫 검색은 미실행됐다. 실제 경로에서 재검색한다.
- R22 일부 Native bridge 오류·push token·진단 redaction assertion을 확인했다. 실제 Unity player 및 전체 로그 수집을 통한 증거는 없어 부분 상태를 유지한다.
- 최종 보고서에 최신 iOS·UPM 산출물과 hash, Android 트리 동일성 근거 및 Unity 미실행을 반영했다.
- source e9b64fb + 문서 변경 strict `artifacts/verify-all-k8z14qqw/summary.md` 종료 1: R34 process recovery와 실행된 local/synthetic suite PASS; Unity Editor NOT_RUN, Unity push DEFERRED_ENV, PARTIAL 시나리오 및 기존 실패로 전체 FAIL. 실제 제공자 13개 WAITING_USER.
- R20 Android/iOS revoke 실패·token 삭제 assertion을 auth-regression manifest에 연결했다. 실제 네트워크·Unity 검증은 별도로 유지한다. manifest 및 원장 검증을 실행한다.
- R20 manifest 검사와 음성·원장 검사 PASS. 커밋 준비: 최신 패키지 hash·strict 결과·R20 증거 매핑 및 감사 기록만 저장한다. strict 실행은 매핑 전이므로 최신 manifest 기준 전체 재실행으로 주장하지 않는다.
### P11-T01 소스 미완성 표식 재감사 시작
- 제품 소스의 TODO/FIXME·unsupported 경로와 원장의 제한 사항을 대조한다. 테스트 fixture와 명시 범위 제외는 구분한다.
- Android/iOS/Backend/Unity 제품 경로에서 TODO·FIXME·NotImplementedException·fatalError 표식은 검색되지 않았다. unsupported/config-required 분기는 별도 계약·제한으로 남아 있고, 표식 부재를 전체 구현 완료로 취급하지 않는다.
- e9b64fb iOS simulator slice를 별도 Swift consumer source에서 link한다. 실행·서명·Unity link 시험은 아니다.
- `xcrun --sdk iphonesimulator swiftc ... ios/consumer-check/main.swift` 종료 0. 별도 Swift consumer의 arm64 simulator link만 확인했다.
- 커밋 준비: TODO 감사 및 최신 iOS consumer link 결과와 FINAL_REPORT 갱신. 새 제품 동작이나 실제 플랫폼 PASS는 주장하지 않는다.
### P11-T02 외부 설정 형태 확인 시작
- 실키·서명·기기 설정은 USER_SETUP으로 유지하고 비밀값을 출력하지 않는 check-config만 실행한다. 통과하더라도 실제 provider 검증은 아니다.
- `bash scripts/verify-external.sh --check-config` exit 2: auth audiences, Google purchase, Apple purchase, FCM, APNs, purchase encryption, push token encryption이 MISSING_OR_INVALID. 비밀값은 출력하지 않았고 실제 인증·발송·결제는 수행하지 않았다.
- 커밋 준비: 외부 설정 형태 재확인 결과만 기록한다. 실연동은 NOT_RUN이고 USER_SETUP의 사용자 작업이 남아 있다.
### P05-T03 iOS 26.5 로컬 StoreKit 재검증 시작
- 기존 전용 iOS 18.6 재시작 runner에 런타임 선택을 추가하고 별도 26.5 simulator에서 실행한다. 실패를 자동으로 성공 처리하지 않으며 Apple sandbox와 구분한다.
- iOS 26.5 전용 simulator·DB 재시험 `artifacts/xcode-process-recovery-ifyufa3n` exit 1: 앱 prepare 상태 보고 timeout. 이번 결과만으로 기존 SKInternalErrorDomain Code 3과 동일 원인이라고 판단하지 않는다. 제품 StoreKit 기능 검증은 FAIL 유지한다.
- runtime override 및 증거 JSON에 사용 런타임을 기록하도록 보강했고 Python 문법 검사는 PASS. 커밋 준비: 테스트 runner와 실패 사실만 저장한다.
- iOS 26.5 prepare timeout의 위치를 구분하기 위해 테스트 앱의 안전한 단계 checkpoint를 추가하고 전용 환경에서 재실행한다.
- 상태 파일에 테스트 단계 이름만 쓰고 timeout에서 마지막 단계를 기록하도록 한 뒤 새 전용 simulator·DB로 실행한다.
- 26.5 전용 simulator에서 SKTestSession 생성 단계 timeout (`artifacts/xcode-process-recovery-p8qyld6o`); Code 3 발생 여부는 미확인. 테스트 계측 자체의 회귀를 배제하기 위해 iOS 18.6에서 동일 runner를 재실행한다.
- 동일 계측 runner의 iOS 18.6 process recovery PASS (`artifacts/xcode-process-recovery-2jktejkt`), 반면 26.5는 SKTestSession 생성에서 timeout. 두 runtime 결과는 분리해 기록한다.
- 커밋 준비: 테스트 앱 단계 checkpoint와 timeout 결과, 26.5 실패·18.6 대조 PASS를 보존한다. 실제 Apple sandbox는 미실행이다.
### P09-T03 R20 타깃 회귀 재검증 시작
- synthetic revoke 실패 시 로컬 token 삭제와 revoke 미확인 오류를 Android 및 Swift에서 각각 실행한다.
- R20 Android 단일 테스트 첫 호출은 SDK location 누락으로 Gradle 준비 단계 FAIL, 테스트 0건. 기존 설치 SDK 경로를 지정한다.
- `ANDROID_HOME=$HOME/Library/Android/sdk`로 동일 단일 테스트를 재실행한다.
- SDK 경로 설정 후 Android R20 단일 테스트 Gradle 종료 0. Swift 대응 테스트를 실행한다.
- R20 타깃 재시험: Android XML 1 test/0 failure/0 skip, Swift XCTest 1 test/0 failure/0 skip. 첫 Android 호출의 SDK 경로 오류는 환경 지정 후 해결했다.
- 커밋 준비: R20 단일 테스트 결과·초기 환경 오류 기록만 포함한다.
- R09 Android 점검: `adb devices` 연결 기기 0. 기존 사용자 AVD는 사용·수정하지 않았다. 실제 Unity AndroidJavaProxy/JNI 경계는 실행되지 않아 PARTIAL 유지한다.
- P11 진행 원장·manifest 및 누락 음성 검사 PASS. 커밋 준비: R09 연결 기기 부재 및 재개 체크포인트를 기록하며 검증 미실행을 완료로 바꾸지 않는다.
### 공개 저장소 생성 및 푸시 준비
- 사용자 요청에 따라 `CodingBot000/GameBridge_SDK` 공개 저장소를 생성하고 `main`을 푸시할 예정이다. GitHub 로그인 계정과 동일 이름 저장소 부재를 확인했다. 전체 이력 blob 1,690개에서 주요 인증키·개인키 패턴은 검출되지 않았다(패턴 검사는 모든 비밀의 부재를 보장하지 않음). 기존 미추적 `unity/Demo/`, Python 캐시는 포함하지 않는다. 생성·푸시 전 로컬 기록을 커밋한다.
### PX-T01 Unity Android LOCAL_MOCK 통합 시작
- v2.md 지시에 따라 기존 상태·소스와 Unity 라이선스, Editor/Android 모듈을 확인한다. 실제 Android Player 검증 전 EditorOfflineTransport나 Native 단위 테스트를 대체 증거로 사용하지 않는다.
- Unity `license status --format json`: signedIn=true, active=false, licenses=[]; `editors --installed --format json`: 6000.5.8f1과 6000.4.0f1, Android 모듈 없음. 두 설치 경로의 AndroidPlayer 디렉터리 검색 결과 없음. `adb devices` 연결 기기 0. 이는 LOCAL_MOCK Player 검증을 막는 환경 상태이며 앱 실행 결과는 아니다.
- PX-T01 새 소비 프로젝트를 격리 경로에 생성하는 스크립트와 Android Player 전용 검증 소스를 작성한다. 실제 Unity import/build/run은 라이선스·Android 모듈 확보 전 NOT_RUN으로 유지한다.
- `tests/UnityAndroidMockConsumer` 및 `scripts/prepare-unity-android-mock.sh`를 작성했다. 새 프로젝트의 개발 전용 cleartext 설정은 해당 격리 앱에만 적용하며, 개발키는 실행 시 synthetic intent로만 전달하고 로그에 출력하지 않는다. 실제 import/build/run은 미실행이다.
- `GAMEBRIDGE_UPM_STAGING=.../upm-e9b64fb bash scripts/prepare-unity-android-mock.sh --prepare` 종료 0, 110개 파일 무결성 PASS. 새 프로젝트는 파일 생성만 했으며 Unity import는 실행되지 않았다. Android 시나리오의 독립 managed compile 검증을 시작한다.
- 설치된 Unity 6000.5.8f1의 managed reference와 .NET 8로 `UNITY_ANDROID` SDK+시나리오 컴파일 성공(경고 0, 오류 0). 빌드 파이프라인·Android JNI·실행을 확인한 것은 아니다.
- README Native bridge 설명을 현재 구현과 미검증 상태로 정정했다. USER_SETUP에는 로그인과 활성 라이선스의 차이, Android 모듈·기기 준비, 격리 소비 프로젝트 생성 범위를 기록했다.
- Unity bridge request ID와 별도로 실제 Backend 호출을 증명하려고 local-mock 전용·opt-in API tracing을 구현한다. 허용된 고정 경로·HTTP method·서버 request ID·응답 코드만 기록하며 비밀·본문·사용자 식별자는 제외한다.
- local-mock trace의 허용 경로·UUID·응답 코드 및 synthetic secret 비노출, profile/설정 이중 조건을 단위 테스트한다.
- `backend/gradlew -p backend test --tests com.gamebridge.config.LocalMockTraceFilterTest` 종료 0, 2 test/0 skip. opt-in과 local-mock 동시 요구, 경로 allowlist와 synthetic secret 비노출을 확인했다. 전용 DB·실 HTTP 확인을 시작한다.
- 전용 DB와 local-mock 서버에서 `/v1/dev/auth` HTTP 200의 X-Request-Id와 `LOCAL_MOCK_TRACE` ID가 일치했고 synthetic key·DB password는 서버 로그에 없었다 (`artifacts/unity-mock-trace-2tz526dj`). 이 검증은 Unity 또는 Android Player 실행이 아니다.
- 재사용 가능한 시나리오 managed compile 명령을 추가하고 동일 참조로 재검증한다.
- `scripts/check-unity-android-mock-compile.sh` 종료 0, Android 조건부 시나리오 managed compile 경고·오류 0. Unity Android Player 빌드 스크립트에 라이선스·모듈 preflight와 새 APK 경로 검사를 추가했다. 실제 빌드는 미실행이다.
- 새 빌드 스크립트 호출은 exit 2, APK 없음. Unity CLI가 active=false JSON과 비영 종료를 함께 반환하므로 ‘상태 조회 불가’라고 잘못 분류됐다. JSON 유효성과 active 값을 먼저 구분하도록 수정한다.
- `active=false` 응답을 inactive로, 무효 응답을 unknown으로 구분하도록 수정해 재검증한다.
- 빌드 preflight 재실행 결과 `DEFERRED_ENV: Unity license inactive`, exit 2. CLI 종료 코드도 명시적으로 수집하며 상태를 통과로 간주하지 않는다.
- README와 USER_SETUP에 실제 구현 범위, 격리 consumer 준비·서버 trace 사용 및 Player 미실행을 명시했다. 개발키는 test intent로만 공급하고 실제 키는 사용하지 않는다.
- staging 누락을 거부하는지, 비활성 Unity license에서 APK를 만들지 않고 종료 2인지 재검증한다.
- 생성기 staging 누락 exit 2, 빌드 preflight inactive license exit 2·APK 미생성 확인. Backend trace 단위 2건 및 local HTTP 대조, Unity managed compile과 구별한다. 사용자 라이선스 활성화·Android Build Support 후 실제 Player 흐름을 계속해야 한다.
- 커밋 준비: 새 consumer 준비·compile-only 검증, local-mock opt-in trace 및 실제 HTTP 단독 검증, README·USER_SETUP 정정. Unity import·Android Player·Unity→Kotlin→Backend 전체 흐름은 활성 라이선스와 Android 모듈 부족으로 NOT_RUN이며 push는 하지 않는다.
### PX-T02 전용 Android 에뮬레이터 준비 시작
- 설치된 Android 36 ARM64 system image를 사용해 신규 AVD를 격리 경로에 생성한다. 사용자 기존 AVD는 변경하지 않으며 Unity 앱 빌드·실행을 성공으로 간주하지 않는다.
- `GameBridge_V2_20261111_161918` AVD를 `artifacts/GameBridge_V2_20261111_161918.avd`에 생성하고 목록과 config를 확인했다. 기존 AVD는 수정하지 않았다. 전용 포트에서 부팅한다.
- 전용 AVD 첫 백그라운드 기동은 프로세스 종료 후 ADB 미연결, 부팅 대기는 중단했다. 기존 기기에는 영향이 없고 foreground 관리 세션에서 재시도한다.
- 전용 AVD를 foreground 세션으로 실행하고 별도 ADB에서 부팅 상태를 확인한다.
- foreground 세션의 전용 `GameBridge_V2_20261111_161918`이 부팅 완료됐다. 에뮬레이터 포트 5598은 도구의 권장 범위 밖 경고가 있었으나 `adb -s emulator-5598`와 boot_completed=1을 확인했다. 기존 AVD는 사용하지 않았다. 이제 10.0.2.2 host 연결만 검증한다.
- 전용 에뮬레이터에서 `10.0.2.2`를 통한 로컬 TCP 서버 응답 PASS. 이는 네트워크 도달성만 확인하며 SDK, Backend, Unity Player 검증은 아니다.
- 커밋 준비: 전용 AVD·ADB 부팅 및 host 연결 결과와 USER_SETUP 갱신만 저장한다. 테스트 AVD와 로그는 로컬 artifacts에 남기며 자동 push하지 않는다.
### PX-T03 Android Kotlin bridge 대조 경로 시작
- 사용자 목표의 Unity 호출에 앞서 격리 에뮬레이터에서 실제 Android Kotlin bridge와 local Backend의 초기화·인증·상품·구매·서버 잔액·로그아웃을 독립 검증한다. Unity JNI/Player는 별도 NOT_RUN이다.
- `LocalMockBridgeDeviceTest`는 opt-in synthetic key, request ID별 callback 매칭, 상품·구매·서버 잔액 +100·로그아웃을 검증한다. 테스트 input과 credential은 로그에 남기지 않는다. 기기에서 실행하기 전에 빌드를 확인한다.
- `:sample-app:assembleDebug :sample-app:assembleDebugAndroidTest` 종료 0. 이어 전용 local-mock 서버와 DB·에뮬레이터에서 opt-in 테스트를 실행한다.
- 전용 DB·에뮬레이터의 `LocalMockBridgeDeviceTest` 1건 PASS: Android Kotlin bridge 초기화/로그인/상품/구매/서버 잔액/로그아웃 및 서버 trace, DB 원장 1건·100 확인 (`artifacts/android-mock-bridge-e2e-3xwlhqj0`). Unity는 사용되지 않았다. Native request ID의 공개 가능한 logcat 증거 수집을 보강한다.
- Native 로그에서 operation·UUID·PASS만 저장하고 서버 trace와 분리한다. runner가 기존 설치 앱을 덮어쓰지 않으므로 새 전용 AVD를 준비한다.
- 새 전용 AVD·DB 재실행 1 test PASS, skip 0. Native bridge request ID는 `native-requests.log`, Backend HTTP request ID는 `server.log`에 각각 저장했다. 원장 1건·delta 100 및 synthetic secret 비노출을 확인했다. Unity Android Player/JNI는 실행하지 않았다. 증거 `docs/evidence/px-t03-android-mock-bridge.md`.
- 커밋 준비: Android Native bridge 장치 검증과 격리 DB/로그 증거만 포함한다. 설치한 테스트 앱과 전용 DB·AVD는 보존한다. 자동 push하지 않는다.
- 사용자 조작이 필요한 잔여 블로커: Unity Hub 라이선스 활성화 및 Android Build Support 설치·해당 약관 동의. 6000.5.8f1 설치는 확인했고 전용 Android 36 AVD, 격리 consumer 및 단독 Native/Backend 증거는 준비돼 있다. Unity Player 전체 검증은 수행하지 않았다. 기존 미추적 Demo·캐시 보존, 자동 push 없음.
- 커밋 준비: USER_SETUP의 Native 대조 결과와 사용자 준비 단계·정확한 재개 위치만 기록한다.


### [PX-T04] Unity Android Player LOCAL_MOCK E2E runner 작성 (후속 변경 브랜치)
- 변경: harness/run-unity-android-mock-e2e.py. 신규 전용 GameBridge_V2_ AVD, 미설치 상태, UPM staging 무결성, 활성 라이선스와 Android 모듈 preflight를 확인한 다음 Unity APK 빌드·설치·실행을 시도하도록 구성했다.
- 구현: Unity GB_MOCK_STEP·GB_MOCK_NATIVE·GB_MOCK_RESULT, Backend LOCAL_MOCK_TRACE 및 전용 DB wallet_ledger의 1건·100코인까지 대조한 경우만 PASS. 원본 로그는 artifacts 내 격리.
- 이 대화의 원격 편집에서는 Unity Editor·Android emulator·Backend를 실행하지 않았으므로 Exit Code와 PASS 없음. 코드 확인은 별도 실제 검증을 대체하지 않는다.
- 현재 환경 블로커: Unity 활성 라이선스 0, Android Build Support 없음. 실제 Unity import·APK·Player 실행은 NOT_RUN이며 이전 PX-T03 Native-only PASS와 구분한다.

### [PX-T05] Android Native-only Runner의 환경 종속성 제거
- 변경: harness/run-android-mock-bridge-e2e.py. adb 경로·serial·전용 AVD 이름·격리 로컬 PostgreSQL 컨테이너/사용자/포트를 인자/환경변수로 설정하게 했다.
- 안전 조건: GameBridge_V2_ prefix, 온라인 emulator, 기존 앱 무덮어쓰기, 로컬 Compose PostgreSQL 컨테이너 이름 제한, 무작위 테스트 DB 보존. 테스트 당시 HEAD, tracked dirty 및 backend jar digest를 result.json에 저장하도록 구성했다.
- 수정본 테스트 명령을 아직 실행하지 않았다 (NOT_RUN). 기존 PX-T03 PASS는 원래 버전의 증거이며 이 버전 재현 성공을 뜻하지 않는다.

### [PX-T06] 공개 검증 증거 및 CI 보강
- 변경: harness/export-mock-e2e-evidence.py, harness/test_export_mock_e2e_evidence.py, .github/workflows/verify.yml, 관련 사용자 설정·원장.
- Exporter는 PASS·현재 SHA·추적 파일 clean·1건/100코인 지급과 Unity/Native 근거를 개별적으로 검사한다. 원본 로그와 환경 식별자는 Markdown에 복사하지 않는다. 미실행·실패·stale은 거부한다.
- GitHub Actions Linux lane에 py_compile 및 오프라인 단위 테스트를 추가했지만 해당 변경에 대한 Actions 실행 결과는 아직 없다 (NOT_RUN). 기존 unity-runtime-required placeholder 및 strict 전체 게이트는 성공으로 주장하지 않는다.
- 다음 행동: 라이선스·Android 모듈 준비, 새 UPM staging, 별도 전용 AVD에서 실제 Runner 실행, 이후에만 새로운 docs/evidence 결과 생성. 실패 시 명령·exit·오류 코드부터 수집해 원장 갱신.
### PX-T04 Unity Android 통합 재검증 재개 (2026-11-12)
- 원격 `origin/fix/unity-android-mock-e2e-evidence`를 fetch해 같은 이름의 로컬 추적 브랜치로 전환했다. 사용자 미추적 Demo 및 Python 캐시는 보존한다. Unity 라이선스·모듈과 PX-T04~T06 기존 구현을 확인하고 새 산출물 및 별도 에뮬레이터로 실제 Player 검증을 진행한다. 아직 결과는 NOT_RUN이다.
- Unity CLI `license status`는 active=true, signedIn=true, licenseCount=3. `unity modules list 6000.5.8f1`은 android, android-sdk-ndk-tools, android-open-jdk 및 ios Installed. 실제 모듈 디렉터리는 `/Applications/Unity/Hub/Editor/6000.5.8f1/PlaybackEngines` 아래며 SDK/NDK/OpenJDK도 존재한다. 기존 `scripts/build-unity-android-mock.sh`가 `Unity.app/Contents/PlaybackEngines`만 확인하므로 유효한 설치를 거부하는 코드 문제를 발견했다. Player 검증 전 경로를 수정한다.
- `scripts/build-unity-android-mock.sh`에서 Unity Hub의 버전 디렉터리 및 기존 Unity.app 내부의 AndroidPlayer 양쪽을 확인하도록 수정했다. 실행 검증 전이며 Player PASS가 아니다.
- `bash -n scripts/build-unity-android-mock.sh` 종료 0, `python3 -m unittest discover -s harness -p test_export_mock_e2e_evidence.py -v` 4건 PASS/skip 0. 실제 Player 빌드 검증은 미실행이다. 커밋 준비: Unity Hub Android 모듈 경로 수정과 환경 확인 기록만 포함한다.
### P08 / PX-T04 최신 SDK 패키지 재생성 시작 (2026-11-12)
- 기준 제품 소스 HEAD `f1e12b6`. 새 Android Maven 산출물과 독립 R8 consumer, iOS device/simulator XCFramework 및 UPM staging을 순차 생성·검증한다. 이전 산출물을 덮어쓰지 않으며 Unity Player는 아직 미실행이다.
- `GAMEBRIDGE_MAVEN_REPO=.../maven-v2-20261112-f1e12b6 bash scripts/build-android.sh --mock` 종료 0: mock sample 및 별도 R8 consumer 포함. 이어 iOS device/simulator XCFramework를 생성한다.
- `GAMEBRIDGE_IOS_OUTPUT_DIR=.../ios-v2-20261112-f1e12b6 bash scripts/build-ios.sh --xcframework` 종료 0. 새 staging에 Android/iOS 산출물을 결합하고 무결성과 버전을 확인한다.
- `scripts/package-sdk.sh` 및 `python3 harness/check-staging.py .../upm-v2-20261112-f1e12b6` 종료 0: XCFramework device arm64 / simulator arm64,x86_64와 각 C ABI 4종 검사 PASS, staging 110개 파일 checksum PASS. Android 3개 Maven POM과 UPM package version `0.1.0-dev` 일치. 이 결과는 Unity Player를 증명하지 않는다.
- 커밋 준비: 최신 산출물 위치·빌드 검사 결과만 기록하고 생성물은 Git에 추가하지 않는다. Unity E2E는 새 전용 AVD에서 후속 실행한다.
### PX-T04 Unity Android Player 전체 경로 검증 시작
- `harness/run-unity-android-mock-e2e.py --run-local`을 새 전용 AVD 및 `artifacts/upm-v2-20261112-f1e12b6`로 실행한다. 제품 소스는 f1e12b6 이후 문서 외 변경이 없고 staged source 일치 검사를 수행한다. 합성 개발키·전용 DB를 사용하며 Unity/Native/HTTP/원장을 모두 확인하기 전까지 PASS가 아니다. 실행 전 기록을 커밋해 소스 clean 여부도 확인한다.
- `python3 harness/run-unity-android-mock-e2e.py --run-local --staging .../upm-v2-20261112-f1e12b6 --serial emulator-5584 --expected-avd GameBridge_V2_20261112_011301` 종료 1, `UNITY_APK_INSTALL_FAILED`; Unity APK 생성 이후 설치에서 멈췄고 Player 전체 실행은 수행하지 못했다. runner가 adb 상세 오류를 감춰 전용 AVD에서 원인을 확인한다.
- 첫 실패 후 같은 전용 AVD에서 APK 재설치 없이 빈 상태를 확인하고 `adb -s emulator-5584 install .../gamebridge-mock-consumer.apk` 재시도 종료 0. 최초 실패 원인은 기록이 없어 불명이다. 앱을 보존하며 runner에 설치 출력 저장을 추가하고 새 AVD로 재실행한다.
- `harness/run-unity-android-mock-e2e.py`가 adb install 출력과 종료 코드·Success 마커를 검사해 실패 근거를 artifacts에 저장하도록 보완했다. 개발키는 설치 명령에 포함되지 않는다.
- runner `python3 -m py_compile` 종료 0. 커밋 준비: 설치 진단 보강과 실제 실패·재시도 기록만 포함한다.
- 최초 전용 AVD와 설치한 APK는 삭제하지 않고 종료만 한다. 새 GameBridge_V2_ AVD에서 `harness/run-unity-android-mock-e2e.py`를 다시 실행한다. 진행 기록을 먼저 커밋해 clean 상태를 확보한다.
- 두 번째 `harness/run-unity-android-mock-e2e.py`는 Unity APK 빌드 후 `UNITY_APK_INSTALL_FAILED` exit 1. adb 설치 진단이 저장됐으므로 원인을 조사한다. 기존 증거를 PASS로 승격하지 않는다.
- `artifacts/unity-android-e2e-usi585vl/adb-install.log`: adb daemon 재시작 직후 전용 emulator 미발견. 이후 `adb devices`에서 동일 serial online 확인. Unity 빌드 후 ADB 재검색 지연을 기다리고 AVD 이름·기존 앱 미존재를 다시 확인하는 방향으로 수정한다.
- Unity 빌드 이후 최대 45초 동안 동일 전용 AVD를 재확인하고, 잘못된 기기나 기존 앱은 즉시 거부하도록 runner를 수정했다. 오프라인 복구와 안전한 거부에 대한 단위 테스트를 실행한다.
- `python3 -m unittest discover -s harness -p test_unity_device_rediscovery.py -v` 종료 0, 2건 PASS/skip 0. 커밋 준비: ADB 재검색·전용 AVD 안전 조건 및 진단 기록만 포함한다.
- Unity가 재시작한 ADB의 재검색을 기다리는 runner 수정 후 새 전용 AVD에서 전체 경로를 재실행한다. 기존 두 전용 AVD·DB·APK는 보존한다. 실행 전 기록을 커밋해 tracked-clean 검사를 유지한다.
- ADB 재검색 보강 후 세 번째 runner exit 1, `UNITY_LAUNCH_FAILED` (`artifacts/unity-android-e2e-8t7go26x`). 설치 단계는 통과했으나 앱 실행 요청이 실패했으므로 Native·Backend 전체 시나리오를 PASS로 기록하지 않는다. 원인을 확인한다.
- `aapt dump badging`에 launchable activity가 없고 `cmd package resolve-activity`도 No activity found. `scripts/prepare-unity-android-mock.sh`의 최소 custom manifest가 Unity 기본 Activity 선언을 대체한 것이 원인이다. 현재 생성 프로젝트의 Android entry는 GameActivity이며 Unity 설치본 템플릿을 기준으로 MAIN/LAUNCHER와 GameActivity metadata를 복원한다.
- 개발용 cleartext manifest에 `UnityPlayerGameActivity`, exported MAIN/LAUNCHER 및 Unity/lib_name metadata를 추가했다. 사용자 앱 manifest는 변경하지 않으며 실제 빌드·실행은 재검증 전이다.
- 생성기와 XML 구조 검사 종료 0: GameActivity 및 두 Unity metadata 존재. Unity APK 내부 manifest와 Player 작동은 재빌드·재실행 전이다. 커밋 준비: 테스트 전용 manifest 수정과 실패 원인 기록만 포함한다.
- launcher GameActivity manifest 수정본을 새 AVD에서 Unity APK 재빌드·설치·실행하고 전체 local Backend·DB 원장을 확인한다. 실행 전 기록 커밋으로 tracked-clean 상태를 확보한다.
- manifest 수정 후 새 전용 AVD 전체 runner exit 1, `UNITY_LAUNCH_FAILED`. 설치 이후 launch 오류이며 원인을 확인하기 전에는 수정 성공이나 Player PASS를 기록하지 않는다.
- `aapt dump badging`과 package resolver에서 `com.unity3d.player.UnityPlayerGameActivity` 확인. 기존 `am start -a MAIN -c LAUNCHER -p ...`는 unable to resolve, 동일 APK에 `-n com.gamebridge.sdk.mockconsumer/com.unity3d.player.UnityPlayerGameActivity`는 Status ok. 사용된 key는 합성 placeholder며 Backend 복구 검증이 아니다. runner를 수정한다.
- 실제 테스트 manifest에 맞춰 명시적 GameActivity를 실행하고 adb 결과의 Status ok와 종료 코드를 함께 확인하도록 변경했다. launch 출력에 개발키가 포함되면 redaction하며 raw argv는 기록하지 않는다.
- Python 문법 및 ADB 재검색·기기 안전 테스트 2건 PASS/skip 0. 커밋 준비: 명시적 launcher·redacted 진단 및 실패 기록만 포함한다.
- 수정 runner와 launcher manifest를 새 전용 AVD에서 재검증한다. 기존 AVD·앱·DB·산출물은 삭제하지 않고 실행 전 기록을 커밋한다.
- 명시적 GameActivity launch는 Status ok. 새 AVD에서 Android 전체화면 안내가 Unity 포커스를 막아 전용 에뮬레이터에서 안내만 닫았고, 이후 runner는 `UNITY_PLAYER_REPORTED_FAILURE` exit 1을 기록했다. 실제 오류 단계와 원인은 미확인이다.
- `artifacts/unity-android-e2e-sapxskap`: GameActivity launch 후 `GB_MOCK_RESULT FAIL stage=configuration code=INTERNAL_ERROR`. 생성 Gradle의 settings.gradle·unityLibrary/build.gradle에 GameBridge Maven 의존성이 없고 `AndroidGradleBuildHook`은 `#if UNITY_ANDROID`; `unity run`에 Android build target 지정이 빠져 Editor hook이 실행되지 않은 것으로 추정한다. PlayerSettings의 최초 전체화면 시스템 안내로 일시 정지된 것은 전용 AVD에서 안내를 닫아 확인했다. 클래스 로드 실패 여부는 추가 진단 후 판단한다.
- `scripts/build-unity-android-mock.sh`에서 Editor 시작 시 Android target을 선택하도록 수정. `MockPlayerScenario`의 Android intent·설정·Native transport 오류 단계를 분리하고 오류 타입만 출력한다. 명령·managed compile 검사 후 새 AVD에서 실제 Gradle hook/전체 흐름을 확인한다.
- `bash -n scripts/build-unity-android-mock.sh` 및 Android scenario managed compile 종료 0, 경고·오류 0. 커밋 준비: Android active target 선택, 비밀 없는 오류 단계 및 실패 근거만 포함한다.
- Android target을 선택한 Unity import/build 및 새 전용 AVD의 전체 LOCAL_MOCK 재실행을 시작한다. 기존 AVD·DB는 보존하고 실행 전 tracked-clean을 확보한다.
- PX-T04 `python3 harness/run-unity-android-mock-e2e.py --run-local --staging artifacts/upm-v2-20261112-f1e12b6 --serial emulator-5584 --expected-avd GameBridge_V2_20261112_012825` 종료 0, `artifacts/unity-android-e2e-zbdkbnnl/result.json` PASS. source c58b4a6 및 tracked-clean, Unity 단계 6개, Native 진단 request ID, Backend mock-auth/catalog/entitlements/verify/logout HTTP 200, DB wallet_ledger 1건·100코인 확인. 최초 Android 전체화면 안내는 새 전용 AVD에서 수동으로 닫았으므로 완전 무인 실행으로 주장하지 않는다. Google 로그인·실제 스토어 및 Unity iOS는 미검증이다. `harness/export-mock-e2e-evidence.py --kind unity ...` 종료 0으로 공개 요약만 생성했다.
- README, USER_SETUP, FINAL_REPORT 및 FEATURE_MATRIX에 Unity Android LOCAL_MOCK 실제 Player 통과와 범위·수동 전체화면 안내를 반영했다. 과거 실패 기록은 지우지 않고 실제 외부 인증/결제, Unity iOS는 미검증으로 유지한다.
- PASS evidence에 실행 명령 형태·exit 0·Unity 6000.5.8f1/Android 36 ARM64·staging checksum과 전체화면 안내 수동 처리를 추가했다. 합성값·원시 로그는 커밋하지 않는다.
- 진행 매트릭스의 Unity Android local-mock 및 UPM import/IL2CPP 결과를 갱신하고, Editor 테스트·push·복구 및 iOS/외부 서비스는 별도로 유지했다. README의 오래된 Runner NOT_RUN 문구도 정정했다.
- USER_SETUP에서 2026-11-11 라이선스·모듈 미비는 과거 상태로 보존하고 2026-11-12 실제 환경과 Android LOCAL_MOCK PASS를 명시했다.
- 커밋 준비: PX-T04 공개용 검증 요약 및 README/PROGRESS/USER_SETUP/FEATURE_MATRIX/FINAL_REPORT의 현재 상태만 포함한다. source c58b4a6에서 실제 PASS, Unity iOS·실제 Google/스토어는 NOT_RUN, 최초 전체화면 안내는 수동으로 닫았음을 보존한다. 원본 로그·APK·DB 및 사용자 미추적 파일은 추가하지 않는다.
- PX-T04 결과 정리 후 `python3 scripts/verify-progress.py` 종료 0, `python3 -m unittest discover -s harness -p test_unity_device_rediscovery.py -v` 2건 PASS/skip 0. 이는 Player E2E 결과와 별도다. 커밋 준비: 최종 검사 기록만 저장한다.
### PX-T07 Unity iOS LOCAL_MOCK 통합 시작 (2026-11-12)
- 요청된 `fix/unity-android-mock-e2e-evidence` HEAD `2a116c22aa8a8d79b95f3a55e516f1325c8d53d8` 및 작업 트리를 확인했다. Unity 라이선스 active=true, 6000.5.8f1 iOS 모듈 Installed, Xcode 26.6 build 17F113, Swift 6.3.3, iOS simulator 18.6/26.5 확인. 기존 Android PASS와 사용자 미추적 데이터 보존. 실제 Unity iOS 빌드·실행은 NOT_RUN.
- `python3 harness/check-staging.py artifacts/upm-v2-20261112-f1e12b6`, `python3 scripts/verify-xcframework.py .../GameBridgeNative.xcframework` 종료 0. 기존 패키지 무결성과 심볼 검사이며 Unity iOS 링크·실행 PASS가 아니다.
- `tests/UnityIosMockConsumer`, `scripts/prepare-unity-ios-mock.sh`, `scripts/build-unity-ios-mock.sh` 작성. Unity C#이 실제 SDK API를 사용하고 process environment로 임시 local key를 전달하며, 테스트 Xcode plist에 loopback HTTP 예외를 적용한다. Simulator 프로젝트 생성과 링크·실행은 아직 검증 전이다.
- `bash -n` 및 `GAMEBRIDGE_UPM_STAGING=.../upm-v2-20261112-f1e12b6 bash scripts/prepare-unity-ios-mock.sh --prepare` 종료 0. 110개 checksum 및 별도 소비 프로젝트 생성만 확인했다. Unity iOS Simulator export 검증을 실행한다.
- `bash scripts/build-unity-ios-mock.sh .../project .../xcode` 종료 0: Unity iOS Simulator Xcode export 완료. 아직 Xcode 링크·실행 검증은 아니다. arm64 Simulator 및 code signing 비활성으로 빌드한다.
- `xcodebuild -project .../Unity-iPhone.xcodeproj -scheme Unity-iPhone -configuration Debug -sdk iphonesimulator -derivedDataPath .../Derived ARCHS=arm64 CODE_SIGNING_ALLOWED=NO build -quiet` 종료 0. GameBridgeNative.xcframework가 UnityFramework target에 연결됨을 project.pbxproj에서 확인했다. libtool의 빈 object 경고가 있었으며 Player 동작은 아직 확인하지 않았다.
- 생성된 UnityFramework arm64 Simulator binary `nm -g`에서 GB_ProtocolVersion/SetCallback/Dispatch/Shutdown 확인. Info.plist에는 테스트 전용 127.0.0.1 도메인 예외만 있다. 실제 Unity callback 및 서버 거래는 미실행이다. 전용 Simulator·DB runner 구현을 시작한다.
- `harness/run-unity-ios-mock-e2e.py`에 checksum/source 대조, Unity iOS export, arm64 무서명 Simulator build, XCFramework/C ABI, 전용 Simulator·DB, Unity/Native diagnostics·HTTP trace·원장 확인을 작성했다. runner 전체 실행은 아직 미실행이다.
- 커밋 준비: iOS consumer, 테스트 전용 loopback ATS, Unity iOS Simulator export와 E2E runner 초안. Unity export/Xcode arm64 Simulator link·C ABI만 실제 확인했으며 Player/Backend 전체 통합은 재실행한다.
- `python3 harness/run-unity-ios-mock-e2e.py --run-local --staging .../upm-v2-20261112-f1e12b6`를 실행할 준비를 한다. 새로운 Simulator·DB를 만들고 기존 데이터는 보존한다. Player·Native callback·Backend·원장 대조가 끝나기 전에는 PASS가 아니다. 실행 전 이 기록을 커밋한다.
- Unity iOS Simulator 앱 최초 실행에서 테스트 시나리오가 명시적으로 push 권한을 요청하지 않았는데 알림 허용 dialog가 표시됐다. 전용 Simulator 화면에서 확인했으며 원인을 조사한다. 실행은 진행 중이고 아직 Player/Backend PASS는 아니다.
- 첫 `harness/run-unity-ios-mock-e2e.py` 실행 결과 FAIL `UNITY_PLAYER_REPORTED_FAILURE`, evidence `artifacts/unity-ios-e2e-sbwq4jn5`. 전용 Simulator의 예기치 않은 알림 창은 ‘허용 안 함’으로 닫았다. runner가 실패 시 Player markers를 보존하지 않는 결함이 있어 원인 추적을 보강하고 권한 요청도 조사한다. 전체 경로는 PASS가 아니다.
- 실패 결과의 서버 trace에서 mock-auth HTTP 200 확인. 별도 합성 placeholder 실행에서는 Unity initialize 뒤 로그인 NETWORK_UNAVAILABLE이 관찰됐으나 서버를 연결하지 않은 음성 시험이므로 최초 실패 원인 증거는 아니다. Unity Notifications 기본 plist `UnityNotificationRequestAuthorizationOnAppLaunch=true`가 예상치 못한 알림 창을 유발해 테스트 전용 앱에서 비활성화하고, 실패 시 `GB_MOCK_` 마커를 남기도록 보강한다.
- 테스트 소비 앱 post-build plist에서 Unity Notifications 시작 시 로컬/원격 권한 요청을 모두 false로 설정했다. Player 실패 시에도 credential 없는 GB_MOCK 마커를 artifacts에 남긴다. 운영 SDK/사용자 앱 설정은 변경하지 않는다.
- Python 및 셸 문법 검사 종료 0. 커밋 준비: 테스트 앱의 불필요한 알림 자동 요청 억제, 실패 마커 보존 및 실제 FAIL 기록만 포함한다.
- 알림 자동 요청 억제와 실패 마커 보존 후 `harness/run-unity-ios-mock-e2e.py`를 새로운 Simulator·DB에서 재실행한다. 실행 전 기록을 커밋해 tracked-clean 상태를 확보한다.
- 알림 자동 요청 억제 후 새 Simulator의 runner 재실행 종료 1, `UNITY_PLAYER_REPORTED_FAILURE`. 실패 마커와 서버 trace가 보존됐으며 실제 실패 단계는 조사한다. 전체 통과는 아니다.
- `artifacts/unity-ios-e2e-rfz6jnz2/unity-test-markers.log`: initialize PASS、login INTERNAL_ERROR。Backend mock-auth 200。初期化後の Keychain 保存などを調査する。現在の app は linker ad-hoc signature・entitlement 無し。Apple Developer 登録を必要としない local ad-hoc Xcode build との違いを検証する。
- 같은 Unity Xcode 프로젝트에서 `CODE_SIGN_IDENTITY=- CODE_SIGNING_REQUIRED=YES` Simulator build 종료 0. `codesign`은 ad-hoc 서명 및 올바른 bundle identifier를 보고했다. 이는 키·유료 계정을 사용하지 않는 로컬 대조이며 아직 Keychain 및 E2E 성공을 뜻하지 않는다.
- `--adhoc`은 요청 시에만 로컬 코드 서명을 선택하며 기본 무서명 경로는 유지한다. result.json에 signing 방식을 기록한다. 두 방식 모두 실제 Apple 계정·상용 서명은 아니다.
- runner 문법 검사 종료 0. 커밋 준비: local ad-hoc Simulator 선택 경로 및 첫 실패·대조 빌드 사실만 저장한다. 전체 E2E는 아직 FAIL이다.
- `harness/run-unity-ios-mock-e2e.py --run-local --adhoc --staging .../upm-v2-20261112-f1e12b6`를 새 전용 Simulator/DB에서 실행해 unsigned 실패와 구분한다. 실행 전 tracked-clean 기록을 커밋한다.
- `python3 harness/run-unity-ios-mock-e2e.py --run-local --adhoc --staging .../upm-v2-20261112-f1e12b6` 종료 0, `artifacts/unity-ios-e2e-f5r4zwvp/result.json` PASS. 무서명 Simulator에서는 login INTERNAL_ERROR였고 로컬 ad-hoc Simulator 빌드로 전체 요청/DB 원장 1건·100코인을 확인했다. Apple Developer 계정이나 실키는 사용하지 않았다. Unity main thread 조건을 명시적으로 검사하고 최신 코드에서 다시 실행한다.
- iOS 테스트 consumer에 각 await 후 managed thread ID와 시작 시 Unity 메인 thread 일치를 검사하고 `GB_MOCK_MAIN_THREAD PASS`를 출력하도록 추가했다. runner가 해당 마커를 필수 검사한다. 기존 PASS는 이전 테스트 코드의 결과로 보존한다.
- iOS test scenario main-thread assertion 및 runner marker 조건, Python/셸 문법 검사 종료 0. 커밋 준비: 테스트 전용 강화와 기존 PASS의 범위·새 코드 미검증 상태만 기록한다.
- 메인 스레드 확인 marker를 필수로 하는 Unity iOS LOCAL_MOCK 전체 runner를 새로운 전용 Simulator/DB에서 재실행한다. 실행 전 기록을 커밋하여 tracked-clean 상태를 확보한다.
- `python3 harness/run-unity-ios-mock-e2e.py --run-local --adhoc --staging .../upm-v2-20261112-f1e12b6` 종료 0, `artifacts/unity-ios-e2e-29s8tvel/result.json` PASS. 소스 tracked-clean에서 Unity iOS Player의 메인 스레드·SDK 전체 단계, Swift Native diagnostics, Backend HTTP trace 및 PostgreSQL 원장 1건/100코인을 확인했다. Simulator local ad-hoc signing만 사용했고 Apple 계정·실결제는 미실행. 공개 evidence 생성 전 원본 결과를 대조한다.
- `docs/evidence/px-t07-unity-ios-local-mock.md`를 실제 `artifacts/unity-ios-e2e-29s8tvel/result.json` PASS, source SHA 일치·tracked-clean·원장 1건/100 및 메인 스레드 marker 대조 후 작성했다. 최초 unsigned FAIL, local ad-hoc 성공 및 과거 알림 창 조작을 명확히 구분했다.
- PX-T07 공개 evidence와 README/FEATURE_MATRIX/USER_SETUP/FINAL_REPORT/PROGRESS를 갱신했다. Simulator local ad-hoc 서명과 초기 unsigned 실패를 구분하고 Android PASS 기록 및 외부 제공자 미검증 상태를 유지했다.
- 최초 iOS 테스트 앱의 Unity Notifications 기본 자동 권한 요청과 최종 테스트 전용 plist의 비활성화 사실을 USER_SETUP에 명시했다. 운영 host의 권한·push 동작 검증 결과로 확대하지 않는다.
- `python3 scripts/verify-progress.py`, iOS runner `py_compile`, Android ADB 안전 단위 테스트 2건 모두 종료 0. 공통 SDK/Android 제품 코드는 수정하지 않아 Android Player E2E는 재실행하지 않았으며, 테스트 안전 단위 결과와 기존 PX-T04 PASS는 별개다. 커밋 준비: 검증 문서와 PASS evidence만 포함하고 원본 로그·키·Simulator 데이터는 제외한다.
### PX-T08 Unity Android LOCAL_MOCK Push/Lifecycle 시작
- 요청 문서를 읽고 기존 Android/iOS Player E2E 및 Mock push stream·bridge를 대조한다. Android부터 실제 Player에서 확인하며, 기존 인증·구매 PASS나 Native-only 시험을 Push/Lifecycle 전체 PASS로 취급하지 않는다. 기존 미추적 Demo·캐시 및 데이터는 보존하고 자동 push하지 않는다.
- `tests/UnityAndroidPushConsumer/MockPlayerScenario.cs`는 실제 Unity SDK API 및 PushReceived를 사용하고 synthetic key는 실행 시 intent로만 받는다. callback의 main-thread·중복·해제 후 이벤트를 검사하며 실제 FCM은 사용하지 않는다. 기기 실행 전이다.
- Unity 6000.5.8f1 managed reference의 `UNITY_ANDROID` 조건에서 푸시 시나리오 compile 종료 0, 경고·오류 0. Player 실행이 아니므로 Push PASS로 기록하지 않는다. 기존 Android E2E의 전용 기기·DB 안전검사를 재사용하는 runner를 작성한다.
- `harness/run-unity-android-mock-push-e2e.py`는 기존 전용 AVD/DB·staging 검사를 재사용해 합성 발송 3회, Unity 수신 중복 제거/메인 스레드, unregister 후 403·DB token 삭제를 확인한다. background/network/restart는 명시적으로 NOT_RUN이며 실제 FCM이 아니다. `python3 -m py_compile` 종료 0. 커밋 준비: 테스트 코드와 현 상태만 저장한다.
- 전용 AVD와 DB를 신규 생성해 `harness/run-unity-android-mock-push-e2e.py --run-local`을 실행한다. 기존 AVD·앱·데이터는 수정하지 않는다. 실행 전 이 기록을 커밋한다.
- `python3 harness/run-unity-android-mock-push-e2e.py --run-local --staging ... --serial emulator-5582 --expected-avd GameBridge_V2_20261112_162817` 종료 0, `artifacts/unity-android-push-z1lufhpv/result.json`: 실제 Unity Android Player에서 LOCAL_MOCK 등록·3회 중복 발송의 단일 수신 및 main-thread, unregister·logout 이후 이벤트 미전달, 서버 token 0개와 unregister 후 403 확인. 전용 AVD의 첫 전체화면 안내를 수동으로 닫았다. FCM 및 background/network/process restart는 확인하지 않았다.
- Android Push 기본 E2E PASS에 한정해 공개용 evidence를 작성했다. 커밋 준비: 실제 확인한 범위·수동 에뮬레이터 안내와 미검증 항목을 명시하며, 원본 로그·합성 키·APK는 포함하지 않는다.
### PX-T09 Android Unity lifecycle·연결 복구 시작
- PX-T08 Player 시나리오를 확장해 OnApplicationPause의 background/foreground, test AVD의 연결 중단 및 복구 후 재수신·오프라인 미전달을 실제 검증한다. 로그아웃/프로세스 강제 종료와 구분한다. 아직 NOT_RUN이다.
- 별도 Unity 시나리오에 background/foreground callback과 온라인 전용 푸시 재연결 assertion을 추가했다. 환경 제어 및 실제 실행 검증은 다음 단계다.
- runner가 해당 전용 AVD에서 HOME/재개, Wi-Fi·data 비활성 및 loopback host 접근 실패 확인, offline 발송, 연결 복원 후 재발송과 Player callback을 검증하도록 확장했다. 테스트 종료 시 변경한 네트워크는 복원하며 기존 기기를 변경하지 않는다. 실행 검증은 아직이다.
- `python3 -m py_compile harness/run-unity-android-mock-push-e2e.py` 종료 0. 커밋 준비: Android lifecycle/network test harness와 미실행 범위만 저장한다.
- `harness/run-unity-android-mock-push-e2e.py --run-local` 수정본을 새 전용 AVD에서 재실행한다. 실제 Unity Player 메인 스레드 및 네트워크 차단·복구 검사 전 PASS가 아니다. 실행 전 기록을 커밋한다.
- 수정된 `harness/run-unity-android-mock-push-e2e.py --run-local` 새 전용 AVD 실행 종료 0 (`artifacts/unity-android-push-a82dcn48`). Unity Player의 실제 background/foreground callback, 에뮬레이터 Wi-Fi/data 차단 및 host TCP 접근 실패, offline 메시지 미관측, 네트워크 복구 후 새 LOCAL_MOCK 메시지 수신·main-thread, 등록 해제/로그아웃·서버 token 제거를 확인했다. 전용 AVD의 첫 전체화면 안내는 수동으로 닫았다. 프로세스 종료·재시작과 pending/실제 FCM은 미검증이다.
- `docs/evidence/px-t08-unity-android-mock-push.md`에 별도 source·APK hash·실제 background/network 재검증 결과와 수동 안내를 추가했다. 커밋 준비: evidence 및 두 원장만 포함한다.
### PX-T10 Android Unity process 종료·pending 복구 시작
- 독립 test-only loopback proxy에서 최초 구매 검증의 서버 commit 응답만 합성 실패로 바꾸고, 전용 AVD에서 Unity 앱을 force-stop한 뒤 세션 복원·pending sync·원장 불변을 검증한다. 실제 Play 스토어 또는 푸시 오프라인 전달로 취급하지 않는다. 아직 NOT_RUN이다.
- 별도 Android Unity consumer가 실제 GameBridge API로 pending 재시도와 session restore를 검증하도록 작성했다. test-only fault proxy 및 실제 Player 실행은 다음 단계다.
- Android restart consumer의 Unity managed reference compile 종료 0. 실제 pending 보존과 앱 강제 종료는 아직 NOT_RUN이며, 외부 자격증명 없이 테스트할 로컬 전용 fault proxy를 추가한다.
- `harness/run-unity-android-mock-restart-e2e.py`는 검증 서버가 200 commit한 최초 응답만 test-only proxy로 503 처리하고, 전용 앱 force-stop 전후 PID·세션 restore·pending 1회 복구·재지급 없음과 DB 원장을 대조한다. proxy는 헤더/본문 로그를 남기지 않는다. Python 문법 PASS. 커밋 준비: 아직 Player 검증은 미실행이다.
- 새 전용 GameBridge_V2_ AVD에서 Unity 앱 강제 종료와 pending 복구 전체 runner를 실행한다. 기존 AVD 및 앱은 보존한다. 실행 전 기록을 커밋한다.
- `python3 harness/run-unity-android-mock-restart-e2e.py --run-local --staging ... --serial emulator-5580 --expected-avd GameBridge_V2_20261112_163957` 종료 0, `artifacts/unity-android-restart-r3p6hl0d/result.json`: test-only proxy로 첫 구매 검증 서버 commit 이후 응답을 503으로 주입, Unity 앱 강제 종료 및 다른 PID 재실행, session restore, pending 1회 복구·재sync 0·원장 1건/100·main-thread 확인. 전용 AVD의 최초 전체화면 안내 수동 처리. 실제 Play Billing과 구분한다.
- Android evidence에 강제 종료 전 서버 commit·응답 유실, 서로 다른 PID, pending 복구·재sync 및 원장 불변, main-thread 범위를 기록했다. 커밋 준비: 공개 증거·원장만 포함하고 test APK·원본 로그는 보존하되 Git에 넣지 않는다.
### PX-T11 Android Unity 세션 전환·지연 이벤트 검증 시작
- 기존 PX-T09 Push 시나리오에 세션 A 종료, 새 세션 B 등록, A 소유권 발송 거부와 B 이벤트 단일 수신을 추가한다. 이전 세션 이벤트가 B에 섞이지 않는지 별도 assertion을 두며 actual Player 실행 전 NOT_RUN이다.
- 동일 설치의 새 B session에서 이전 A 소유권 발송 403, B Mock 이벤트 및 main-thread·중복·이전 이벤트 미수신을 검증하도록 test/runner를 확장했다. API 제한을 지키도록 재발송 횟수도 조정했다.
- Android Push scenario managed reference compile 경고·오류 0, runner Python 문법 PASS. 커밋 준비: 세션 A→B 및 늦은 이벤트 관측 test와 미검증 상태를 기록한다.
- Android Player에서 A→B 전환을 포함한 등록/중복/background/network/로그아웃 경로를 새 전용 AVD와 DB로 재검증한다. 시작 기록을 커밋한다.
- `harness/run-unity-android-mock-push-e2e.py --run-local` 수정본 새 AVD 실행 종료 0 (`artifacts/unity-android-push-h9oyrtjy`): Unity Player의 Mock 등록·중복·main-thread, background/foreground, offline drop·복구, A 로그아웃 후 B 등록, 이전 A 소유권 발송 403, B 단일 수신 및 이전 이벤트 미관측 통과. 전용 AVD 첫 전체화면 안내는 수동으로 닫았다. 임의 지연 callback 및 재연결 실패 자체의 주입·iOS·실 FCM은 미검증이다.
- Android 공개 evidence에 새 source의 A→B 전환·이전 소유권 403·B 이벤트·기존 lifecycle/network 회귀 결과를 추가했다. 커밋 준비: 원본 로그·APK·DB를 제외하고 사실 확인된 범위만 기록한다.
### PX-T12 Unity iOS LOCAL_MOCK Push/Lifecycle 시작
- Android의 실제 Player 시나리오를 토대로 별도 iOS Simulator consumer 및 안전한 local Backend/DB runner를 작성한다. iOS push, lifecycle 및 실제 APNs를 Android PASS로 대체하지 않는다.
- `tests/UnityIosPushConsumer/MockIosPlayerScenario.cs`를 추가했다. 실제 Unity SDK API/PushReceived를 호출하며 loopback만 사용하고 key를 로그·에셋에 저장하지 않는다. iOS Player 검증은 미실행이다.
- iOS Push consumer `UNITY_IOS` managed compile 종료 0, 경고·오류 0. 실제 iOS Player, Swift C ABI 및 서버 수신은 미실행. 다른 사용자 네트워크를 변경하지 않도록 test 전용 loopback TCP proxy에서 SDK 연결만 차단·복구하는 방식을 준비한다.
- iOS Push runner는 신규 Simulator·DB, local ad-hoc, 개발 서버 allowlist, 중복·main-thread·세션 전환, Simulator background/foreground 및 테스트 전용 TCP 연결 차단/복구를 검사한다. OS 전체 네트워크와 실제 APNs는 건드리지 않는다. Python 문법 종료 0, Player 실행 전이므로 커밋 준비한다.
- `harness/run-unity-ios-mock-push-e2e.py --run-local --staging .../upm-v2-20261112-f1e12b6`를 신규 Simulator/DB에서 실행한다. 실제 Unity Player·Swift·Backend·DB 결과 확인 전 PASS가 아니다. 실행 전 이 기록을 커밋한다.
- `artifacts/unity-ios-mock.6cWqlO/project/Logs/upm.log`: Unity Package Manager가 `packages.unity.com` 연결 ETIMEDOUT. 기존 Unity 설치/네트워크 설정을 변경하지 않고 이전 격리 프로젝트의 동일 버전 package cache로 새 소비 프로젝트를 구성할 수 있는지 조사한다. 현재 Player 성공은 아니다.
- 첫 iOS Push 실행 `artifacts/unity-ios-push-*`는 UPM registry 연속 timeout으로 자체 Unity 프로세스를 중단(exit 130). 기존 runner가 KeyboardInterrupt를 별도 처리하지 않아 결과 JSON은 FAIL로 남았으며 실제 Player는 NOT_RUN이었다. 이전에 성공한 격리 프로젝트의 notifications 2.5.0 / Newtonsoft 3.2.2 cache를 확인했고, 원본과 전역 설정을 수정하지 않는 새 프로젝트 한정 embedded 복사 경로를 검토한다.
- iOS test runner의 `--package-cache`는 별도 저장된 기존 PackageCache에서 mobile notifications 2.5.0 및 Newtonsoft 3.2.2만 검사·복사하고 새 격리 소비 프로젝트의 embedded package로 사용한다. 전역 Unity 설정·원본 cache는 수정하지 않는다. 실제 resolver/Player는 아직 검증 전이다.
- embedded package 선택 경로가 정확한 2.5.0/3.2.2만 복사하고 source 보존 및 누락 실패를 수행하는지 isolated unit test를 실행한다.
- `python3 -m unittest discover -s harness -p test_unity_ios_push_cache.py -v` 2건 PASS/skip 0. 커밋 준비: 격리 embedded cache 경로, interrupted 분류 및 registry timeout 기록을 저장한다. 네트워크 우회나 전역 설정 변경은 없다.
- 기존 Unity 성공 프로젝트의 package cache를 읽기 전용 원본으로 사용하여 새 격리 소비 프로젝트에 exact-version embedded package를 복사하고 iOS Player E2E를 재실행한다. 성공 전에는 PASS로 기록하지 않는다. 실행 전 진행 문서를 커밋한다.
- exact-version cached packages를 embedded로 복사한 재시도는 Unity export FAIL exit 1. `artifacts/unity-ios-mock.Y0BHBq/project/Logs/Editor.log`에 Notifications package의 Tests/Runtime이 NUnit/Test Framework 미참조로 CS0246을 발생시켰다. SDK/runtime 소스의 실패로 단정하지 않는다. 새 임시 복사본에서 해당 패키지의 test-only 디렉터리만 제외하고 resolver/build를 재검증한다.
- 임시 embedded package의 Tests/Tests.meta만 제외해 runtime/editor 코드는 보존하고 source cache test 디렉터리는 그대로 유지한다. 누락·원본 보존 unit test를 재실행한다.
- `python3 -m unittest discover -s harness -p test_unity_ios_push_cache.py -v` 종료 0, 2건 PASS/skip 0. 커밋 준비: 임시 embedded test 제외와 원인 기록만 포함한다.
- exact-version embedded cache의 test-only 디렉터리를 제외한 새 소비 프로젝트로 전체 iOS Push runner를 재실행한다. 전역 환경과 이전 artifacts는 보존하며 실행 전 기록을 커밋한다.
- cached package 적용 iOS runner는 Unity export/Xcode build 및 Simulator 앱 실행 후 `BACKGROUND_FAILED`로 종료 1 (`artifacts/unity-ios-push-cggylkb4`). `simctl openurl about:blank`의 실패 원인과 이미 수행된 Player 마커를 확인한다. iOS 전체 Push/Lifecycle은 FAIL 상태다.
- `artifacts/unity-ios-push-cggylkb4/unity-push-markers.log`: Unity initialize/login/ready/received 및 deduplicate-main-thread PASS. `simctl openurl ... about:blank`는 -10814로 지원되지 않았으며 동일 전용 Simulator에서 `http://127.0.0.1:1/` 열기는 종료 0. 실제 네트워크 접근 없이 별도 앱 전환으로 local URL을 사용한다.
- `simctl openurl` 대상은 외부 사이트가 아닌 test Backend의 loopback health URL로 바꿨다. 다른 사용자 기기 및 운영 네트워크는 사용하지 않는다. Python 문법 검사 후 실제 Simulator 전체 흐름을 다시 검증한다.
- runner Python 문법 검사 종료 0. 커밋 준비: Simulator가 지원하는 loopback URL background 전환 및 실제 부분 PASS/실패 기록을 보존한다.
- iOS Player의 local-mock Push·background/foreground·전용 TCP 연결 중단/복구·세션 전환을 새 전용 Simulator/DB에서 다시 확인한다. 실행 전 기록을 커밋한다.
- `python3 harness/run-unity-ios-mock-push-e2e.py --run-local --staging ... --package-cache ...` 종료 0 (`artifacts/unity-ios-push-248n_2n2/result.json`): Unity iOS 18.6 Simulator Player→Swift bridge→local Backend/DB에서 Mock 등록·중복 제거·Unity main-thread·background/foreground·test-only loopback TCP 차단/복구·offline 메시지 미전달·A→B 소유권·logout 후 token 0 PASS. OS 전체 네트워크 차단, process force-stop/pending, 실제 APNs는 별도 미검증이다. Local ad-hoc 서명과 exact-version embedded package cache 사용.
- iOS Push/Lifecycle 실제 통과 범위, local TCP fault와 OS 전체 연결 차단의 차이, registry cache 경로, unsigned/실제 APNs 제외를 공개 evidence에 반영했다. 커밋 준비: 원본 로그·키·DB·Simulator 파일은 제외한다.
### PX-T13 Unity iOS Simulator process/pending 복구 시작
- Android PX-T10과 동일하게 test-only loopback proxy로 서버 commit 뒤 응답만 일회 실패시키고 iOS Simulator 앱을 terminate/relaunch해 세션 복원·pending 1회 복구·중복 지급 방지를 확인한다. 별도 Simulator·DB를 사용하며 실제 StoreKit 결제는 포함하지 않는다.
- `tests/UnityIosRestartConsumer/MockIosPlayerScenario.cs`는 Swift bridge를 통해 실제 SDK API를 호출하고 환경 변수로 합성 key만 공급받는다. libc getpid로 강제 종료 전후 프로세스를 구분한다. Unity build/Simulator 실행은 미검증이다.
- `harness/run-unity-ios-mock-restart-e2e.py` 및 Simulator consumer 작성. 최초 서버 200 후 합성 503, Simulator terminate/relaunch, 별도 PID, 세션 restore·pending 1회 복구·재sync 0·원장 1건/100을 검사한다. Python 문법 종료 0. 커밋 준비: 실제 E2E는 아직 미실행이다.
- `harness/run-unity-ios-mock-restart-e2e.py --run-local`을 새 Simulator/DB 및 local ad-hoc Simulator signing으로 실행한다. 실행 전 진행 기록을 커밋해 tracked-clean 상태를 보존한다.
- `harness/run-unity-ios-mock-restart-e2e.py --run-local --staging ... --package-cache ...` 종료 0 (`artifacts/unity-ios-restart-vidqoa21/result.json`). Unity iOS Simulator Player에서 서버 commit 응답을 test-only proxy가 503으로 바꾼 뒤 앱 terminate/relaunch, 서로 다른 PID, 세션 복원·pending 1회/재sync 0, Unity main-thread 및 DB 원장 1건·100코인을 확인했다. 로컬 ad-hoc, 실제 StoreKit/기기는 아님.
- `docs/evidence/px-t12-unity-ios-mock-push.md`에 iOS Player terminate/relaunch, 서버 commit 응답 유실·session/pending 복구 및 원장 불변 결과를 추가했다. 커밋 준비: 합성 키·원본 로그·Simulator·DB는 제외한다.
### PX-T14 Unity Android/iOS Mock Push 재연결 실패 주입 시작
- 기존 offline drop/reconnect PASS와 재연결 실패 assertion은 다르므로, test-only loopback TCP proxy에서 연결 시도를 거부한 횟수를 계측하고 복구 후 이벤트 수신을 다시 확인한다. 운영 코드와 사용자 네트워크 설정은 변경하지 않는다.
- iOS 전용 TCP fault proxy에 차단 상태에서 발생한 실제 수락/즉시 종료 시도 수를 비밀 없이 기록하고, 최소 1회 실패와 복구 후 이벤트 전달을 함께 요구한다. 기존 PX-T12 PASS를 새 테스트 PASS로 대체하지 않는다.
- Android test는 기존 AVD Wi-Fi/data 차단 확인을 유지하면서 SDK 연결만 받는 loopback proxy의 재연결 거부를 추가했다. 다른 host 네트워크·운영 SDK는 변경하지 않는다. 성공은 각각 새 Player 실행 후에만 기록한다.
- 양 플랫폼 runner `py_compile` 및 iOS cached-package 안전 단위 2건 PASS. Android server log 검사에 B session 합성 token도 추가했다. 커밋 준비: test 전용 fault 계측만 포함하고 실제 Player 결과는 이전 source에 한정한다.
- Android Unity Player에서 OS 네트워크 차단·복원 뒤 test-only proxy의 연결 거부 시도 관측과 재연결 후 전달을 새 전용 AVD/DB로 실행한다. 실행 전 이 기록을 커밋한다.
- PX-T14 Android E2E 새 전용 AVD 실행 종료 0 (`artifacts/unity-android-push-n3lvsnkx`). 실제 Player에서 Wi-Fi/data 차단·복원 및 test-only TCP proxy의 재연결 거부 후 복구를 검사했다. 첫 전체화면 안내는 전용 AVD에서 수동으로 닫았다. 실제 FCM은 아니다.
- Android 결과 source `ea5e17f`, tracked-clean, proxy 재연결 거부 2회, 이후 수신 및 기존 lifecycle/session 통과를 evidence에 추가했다. 커밋 준비: 원본 로그·APK·DB 제외.
- iOS Unity Simulator에서 test-only TCP proxy 연결 거부 시도 관측과 재연결 후 수신을 새 전용 Simulator/DB로 검증한다. 실행 전 기록을 커밋한다.
- iOS Push runner 새 전용 Simulator 실행 종료 0 (`artifacts/unity-ios-push-gcmp59n7`). test-only loopback proxy가 SDK의 재연결 시도를 거부한 후 연결을 복구했고 Unity Player의 local mock push/lifecycle/session 검사가 통과했다. OS 전체 네트워크 차단이나 APNs 원격 전달을 의미하지 않는다.
- iOS source `837c016`, tracked-clean, proxy 재연결 거부 6회 및 후속 수신·기존 lifecycle/session 재검증을 evidence에 기록했다. 커밋 준비: 원시 로그·키·DB·Simulator 산출물은 포함하지 않는다.
### PX-T15 Android/iOS Unity 인증·구매 회귀 시작
- 사용자 요청에 따라 기존 PX-T04/PX-T07 인증·구매 전체 Runner를 현재 source에서 재실행한다. Unity registry timeout을 고려해 기존 iOS Push test의 exact-version embedded cache 복사 기능을 새 격리 프로젝트에만 선택적으로 적용한다. 이전 PASS를 새 결과로 대신하지 않는다.
- 기존 두 Runner가 `--package-cache`를 받으면 PX-T12에서 검증한 exact-version embedded copy를 새 소비 프로젝트에만 적용한다. 기존 전역 Unity 환경 및 package 원본은 수정하지 않는다. 재실행 전 문법/안전 단위를 확인한다.
- 두 Runner Python 문법 및 cache/기기 안전 단위 4건 PASS/skip 0. cache helper의 오류를 해당 runner의 fail-closed 분류로 변환한다. 커밋 준비: 환경 옵션과 진행 기록만 포함한다.
- 기존 Android Player 인증·구매 E2E를 새 전용 AVD와 DB에서 현재 runner로 재실행한다. 기존 AVD·앱·DB는 보존하고 실행 전 기록을 커밋한다.
- `harness/run-unity-android-mock-e2e.py --run-local ... --package-cache ...` 새 전용 AVD 실행 종료 0 (`artifacts/unity-android-e2e-7001epc_`). Unity Player 초기화·Mock 로그인·상품·구매·잔액·로그아웃, Native 진단·서버 trace·DB 원장 검사 통과. 최초 전체화면 안내는 수동으로 닫았다. 기존 Android 회귀와 실제 제공자 검증은 별도다.
- iOS 기존 인증·구매 전체 Runner를 새 Simulator·DB에서 다시 실행한다. 실행 전 진행 기록을 커밋한다.
- `harness/run-unity-ios-mock-e2e.py --run-local --adhoc --package-cache ...`를 새 Simulator/DB에서 실행한다. Unity 인증·구매 이전 PASS를 현재 결과로 대체하지 않는다. 시작 기록을 커밋한다.
- `harness/run-unity-ios-mock-e2e.py --run-local --adhoc ... --package-cache ...` 새 전용 Simulator·DB 실행 종료 0 (`artifacts/unity-ios-e2e-zizcrlvt`): Unity C#→Swift C ABI→Backend/DB의 Mock 로그인·상품·구매·잔액·로그아웃 및 main-thread/Native 진단 통과. Apple 계정·StoreKit 실거래는 사용하지 않았다.
- Android source `8afe5d0`, iOS source `9031124`의 새 tracked-clean 전체 회귀 PASS를 플랫폼 evidence에 추가했다. 커밋 준비: 검증 요약과 원장만 포함하며 원본 로그·APK·키는 제외한다.
### PX-T16 지연 콜백 및 이전 세션 이벤트 검증 시작
- 기존 실제 Android/iOS Player의 session A→B 전환·이전 사용자 발송 거부는 확인했다. 지연된 Native callback 자체를 실제 Player에 주입한 적은 없으므로, 우선 SDK wire registry의 timeout 이후 응답·다른 세션 이벤트 및 dispose 이후 이벤트를 격리 .NET 테스트로 확인한다. 이를 Player 주입 PASS로 대체하지 않는다.
- `tests/UnityLateCallback`은 timeout 후 동일 응답 두 번, 이전 session push, 현재 session 정상 push, dispose 이후 push를 SDK의 실제 RequestRegistry에 합성 주입한다. 이는 C#/managed 단위 시험이며 JNI/C ABI Player 지연 callback 직접 주입은 아니다.
- `dotnet run`은 custom OutputPath로 빌드한 뒤 기본 경로 실행파일을 찾다가 exit 1 (`Win32Exception`); 테스트는 실행되지 않았다. 생성된 명시적 DLL 경로로 다시 실행한다.
- 동일한 테스트를 Unity 동봉 dotnet으로 명시적 출력 DLL에서 실행한다.
- managed wire 단위의 timeout 후 응답·이전 session·dispose 이후 이벤트 테스트는 DLL 직접 실행 PASS. 여기에 더해 각 실제 Player의 platform transport callback 수신 경로에 이전 session 메시지를 test-only 합성 주입해 큐/main-thread에서 폐기되는지 확인한다. 이는 실제 원격 FCM/APNs 발송이 아니다.
- test-only `LateCallbackProbe`와 link.xml을 격리 소비 프로젝트에 복사해 B session에서 A session 이벤트를 Android callback queue 또는 iOS C ABI callback 입력에 합성 주입한다. 메시지가 구독자에 전달되지 않고 ignored counter가 증가해야 한다. Android는 JNI를 통하지 않는 합성 callback 메서드 호출이며 iOS는 합성 C ABI 입력이다. 실제 Player 검증은 아직 미실행이다.
- Unity wire registry의 timeout 후 이중 응답·이전 session·dispose 이후 이벤트 합성 단위는 DLL 직접 실행 PASS. Player probe를 포함한 Android/iOS 조건부 managed compile 각각 0 warning/0 error. JNI나 C ABI의 실제 지연 callback을 이미 통과한 것은 아니다. 커밋 준비: test-only probe·검사와 실제 오류 이력을 포함한다.
- Android Unity Player의 B session에서 A session 합성 메시지를 Android callback queue에 주입하고 무시되는지 확인한다. 새로운 전용 AVD/DB에서 기존 Push/Lifecycle도 재검증하며 시작 기록을 커밋한다.
- Android 실제 Player에서 test-only로 이전 A session 메시지를 B의 Android transport callback 메서드/큐에 지연 합성 주입하고 ignored counter 증가·구독자 미전달을 확인했다 (`artifacts/unity-android-push-3n9bo6qw`, exit 0). 기존 Mock push/background/network/session도 통과, 최초 전체화면 안내는 수동으로 닫았다. 합성 메서드 호출이므로 실제 JNI/FCM 지연 발생을 의미하지 않는다.
- Android evidence에 최신 source의 Player test-only 지연 callback 주입 PASS, 제한된 회귀 범위 및 합성 주입/JNI 차이를 추가했다. 커밋 준비: 원본 로그·APK·DB 제외.
- iOS Unity Player의 B session에 A session 메시지를 Swift C ABI callback 입력과 동일한 C# callback 경로로 합성 주입하고 버퍼 해제 후 폐기 여부를 확인한다. 실제 APNs callback이 아니며 새 Simulator·DB를 사용한다. 실행 전 기록을 커밋한다.
- iOS 실제 Simulator Player에서 test-only 합성 A session 메시지를 B의 C ABI callback 수신 경로에 주입하고 입력 버퍼를 즉시 해제한 뒤 ignored counter 증가·구독자 미전달을 확인했다 (`artifacts/unity-ios-push-213zsmr5`, exit 0). 기존 Mock push/background/test TCP 재연결 실패·session 전환도 통과. 실제 APNs 지연 callback은 아니다.
- iOS evidence에 최신 source Player의 C# callback 수신 메서드 합성 입력·즉시 버퍼 해제·이전 session 폐기 및 test-only scope를 추가했다. 커밋 준비: 원시 로그·키·DB·Simulator 산출물은 제외한다.
### PX-T17 Push/Lifecycle 결과 및 문서 감사 시작
- Android/iOS 실제 Unity Player의 LOCAL_MOCK 시험별 PASS, test-only fault·합성 callback·수동 안내 및 미실행 실제 제공자/실기기 범위를 README, FEATURE_MATRIX, FINAL_REPORT 및 evidence에 정리한다. 과거 결과와 source SHA를 보존한다.
- 현재 Push/Lifecycle 결과를 주요 문서와 플랫폼별 matrix에 반영했다. Android/iOS Player 실험, force-stop 별도 실행, 합성 callback 및 iOS test proxy 범위를 분리하고 FCM/APNs·실기기 미실행을 유지했다.
- BUG-014/015 및 FINAL_REPORT의 오래된 Unity Player 미검증 표현을 Android emulator/iOS Simulator local-mock PASS 범위로 정정했다. 실제 기기·FCM/APNs·다른 모드는 미검증이므로 OPEN 유지한다.
- evidence 내 선행 시험의 시점별 NOT_RUN과 후속 PASS가 충돌하지 않도록 과거 범위임을 명시했다. 각 시험 source SHA·실행 결과 및 실제 FCM/APNs 미검증은 보존했다.
- FEATURE_MATRIX의 push 등록/수신·pending 복구 행 및 USER_SETUP의 오래된 Unity push 미검증 문구를 현재 범위로 정정했다. 실제 알림 클릭·원격 전송·실기기는 PASS로 표시하지 않았다.
- `python3 scripts/verify-progress.py`, 네 runner `py_compile`, cache/ADB 안전 단위 총 4건 및 `git diff --check` 종료 0. 커밋 준비: README·FEATURE_MATRIX·FINAL_REPORT·USER_SETUP·PROGRESS·WORK_LOG·플랫폼 evidence만 포함한다. Unity Runtime CI 전체 gate 및 실제 FCM/APNs는 성공으로 변경하지 않는다.
### PX-T18 P09 시나리오 및 CI 고도화 시작
- 요청된 브랜치·HEAD `058742df270f42d146843c25cdc2bbfc3ec3b341`와 미추적 Demo/cache를 확인했다. manifest의 R09/R11/R22/R40/R43/R49 및 현재 CI gate를 실제 코드/증거와 대조한다. 기본 CI, 라이선스 기반 Unity E2E, fail-closed Release 판정을 분리한다. 실제 검증 전 상태는 변경하지 않는다.
### P09-T07 CI 게이트 분리 시작
- 현 `verify.yml`의 결합된 Linux Backend/Android와 의도적 Unity 실패 placeholder를 조사했다. 사용자 요청에 따라 호스팅 기본 검증을 독립 gate로 분리하고 Unity는 라이선스 준비된 명시적 self-hosted workflow_dispatch에서만 실제 실행한다. Release gate는 누락·실패·부분 검증을 거부한다. 원격 Actions 실행은 아직 NOT_RUN이다.
- `.github/workflows/verify.yml`의 무조건 실패 Unity placeholder를 실제 명시적 self-hosted workflow_dispatch gate로 교체하고, 기본 hosted CI 4개 및 Release readiness를 분리했다. Unity gate는 Editor smoke, Android/iOS Player 및 동일 run의 strict suite가 전부 통과해야 성공한다. Unity job 미실행은 release gate에서 DEFERRED_ENV 비영 종료다. 신뢰되지 않은 PR 코드를 self-hosted에서 자동 실행하지 않는다. 실제 원격 Actions는 아직 미실행이다.
- `bash -n scripts/ci-unity-e2e.sh` PASS. Python YAML 검사 시 PyYAML 미설치로 exit 2, workflow 구문은 아직 미확인이다. 별도 설치 없이 Ruby 내장 parser로 재검증한다.
- Ruby YAML 구문 검사 PASS, 새 7개 job 확인. `python3 harness/check-required-coverage.py`는 예상대로 6 PARTIAL / 0 NOT_IMPLEMENTED, exit 1이다. 이는 Release 준비 성공이 아니다. Unity 미실행 및 실패를 별도 gate에서 거부하는 테스트를 추가한다.
- `scripts/ci-release-gate.sh`를 별도로 만들어 기본 CI 실패, Unity 미실행 및 부분 시나리오가 Release PASS가 되지 않는 음성 테스트를 실행한다.
- 첫 음성 테스트는 실제 manifest가 완성되면 실패하는 구조여서, 임시 PARTIAL fixture를 사용하도록 수정했다. 향후 시나리오 완료를 막지 않는다.
- self-hosted Unity job은 필수 환경뿐 아니라 실제 활성 라이선스를 확인한 다음에만 Editor/Player 검사를 실행한다. basic inventory job에 gate 음성 tests를 추가했다. 원격 Actions는 실행하지 않았다.
- `test_ci_gate.py` 3건 PASS, Ruby YAML 구문/7개 job 구조 및 bash 문법 PASS. `docs/CI.md`에 basic vs Unity vs Release, opt-in self-hosted 보안 경계, 미실행/부분 시나리오 차단 및 현재 strict Unity push 미연결을 명시했다. 원격 CI는 실행하지 않았다.
- 커밋 준비: CI 분리, 라이선스 확인·fail-closed release script, 격리 음성 테스트 및 CI 문서만 포함한다. 원격 workflow 설정/실행 및 자동 push는 하지 않는다.
### P09 R49 신규 Unity 소비 프로젝트 근거 대조 시작
- PX-T04/PX-T07 및 후속 Android/iOS Player 회귀의 새 소비 프로젝트·Unity package copy·APK/Xcode build를 기존 Demo 의존 여부와 대조한다. 재현 가능한 양 플랫폼 runner를 추가하며 근거 확인 전 manifest를 완료로 변경하지 않는다.
- Android `8afe5d0` 및 iOS `9031124` 실제 Player 결과는 동일 staging manifest SHA를 사용하며 SDK 제품 디렉터리 diff 없음. 각 prepare 스크립트는 `unity/Demo`가 아닌 별도 소비 프로젝트에 UPM과 테스트 소스만 복사한다. `harness/run-unity-consumer-e2e.py`는 opt-in 시 Android/iOS 실제 새 실행·현재 HEAD·tracked-clean·원장 검증을 요구한다. runner 음성 검사를 실행한다.
- `docs/evidence/r49-unity-fresh-consumers.md`에 기존 두 Player의 source/staging·새 consumer·서로 동일한 제품 소스 및 한계를 정리했다. R49는 실제 실행된 Android/iOS local-mock 근거로 IMPLEMENTED, 새 wrapper 실제 실행은 NOT_RUN이다. `harness/test_unity_consumer_e2e.py` 2건 PASS/skip 0; manifest·누락 음성 검증을 실행한다.
- `harness/check-manifest.py`, `harness/check-manifest-negative.py` 종료 0, `test_unity_consumer_e2e.py` 2건 PASS/skip 0. 커밋 준비: R49 실제 선행 증거·매핑 및 fail-closed runner만 포함한다.
### P09 R11 Unity Editor scene/domain reload 검증 시작
- 기존 `ConsumerLifecycleTests`는 테스트 소스만 있고 과거 라이선스 미비로 실행되지 않았다. 현재 Unity 6000.5.8f1 활성 환경에서 실제 EditMode test를 실행하고 callback/객체 재생성 검증의 부족 여부를 대조한다. 기존 Unity 프로젝트와 설정은 건드리지 않는다.
- `scripts/build-unity.sh --editor-smoke`가 선택적 `GAMEBRIDGE_UNITY_PACKAGE_CACHE`에서 정확한 두 Unity package를 격리 소비 프로젝트에 복사하고 Unity 6000.5.8f1의 내장 Test Framework 1.7.0/NUnit 2.1.0을 해당 프로젝트에만 embedded할 수 있게 했다. test timeout은 기본 300초 및 외부 watchdog으로 유지한다. 실제 테스트 결과는 아직 없다.
- `GAMEBRIDGE_UPM_STAGING=... GAMEBRIDGE_UNITY_PACKAGE_CACHE=... bash scripts/build-unity.sh --editor-smoke` 종료 0, 실제 Unity Editor EditMode tests 2건 PASS/skip 0 (`artifacts/unity-consumer.j4aGtO/results.xml`), play mode/domain reload 및 scene 전환 실행. 기존 test에는 동일 실행 내 재생성·이전 callback 미전달 검사가 없어서 R11 완료로 승격하지 않는다. 격리 테스트를 보강한다.
- 격리 consumer test에서 동일 play session 내 dispose→재생성, old/new session 합성 event 및 subscriber count, dispatcher 정리를 추가했다. 두 domain reload 경로 각각의 완료 marker도 기록한다. 실제 새로운 Editor 검증을 실행한다.
- 수정된 `scripts/build-unity.sh --editor-smoke` 실행은 `Unity consumer result invalid`, exit 1 (`artifacts/unity-consumer.upNR5n`). 테스트별 실패 메시지를 조사하며 이전 2건 PASS로 새 assertion을 통과 처리하지 않는다.
- 실패한 두 Editor 시험 중 첫 오류는 test의 `SessionId(client)`가 dispose 후 null registry를 참조한 것. 두 번째 시험도 이전 실패에서 남은 객체 영향 가능성이 있으므로 session ID를 dispose 전에 캡처하고 finally에 양 client 정리를 추가했다. 제품 버그로 단정하지 않는다.
- dispose 전 session 캡처 수정 후 강화 Editor 테스트도 exit 1 (`artifacts/unity-consumer.d0MHsU`). 최초 오류 해결 여부 및 남은 assertion을 확인한다.
- `artifacts/unity-consumer.d0MHsU/results.xml`: reload-disabled PASS, reload-enabled test state machine에서 closure 필드 null. Player 제품 오류로 단정하지 않으며 coroutine/domain reload를 넘는 테스트 closure를 static callback으로 대체한다. 같은 오류에 대한 세 번째 시도다.
- static callback으로 수정한 Unity Editor `build-unity.sh --editor-smoke` 종료 0 (`artifacts/unity-consumer.U1ob4f/results.xml`): reload-enabled/disabled 2건 PASS, 각 완료 marker 존재. 두 차례 실패는 test 측 수명/closure 문제로 기록돼 있다. 결과 판정이 실행되지 않은 assertion을 PASS 처리하지 않도록 각 test의 marker를 필수화한다.
- `scripts/check-unity-test-result.py`가 두 test 이름과 PASS뿐 아니라 각 test의 해당 완료 marker를 개별 검사하도록 변경했다. 기존 실제 XML 및 marker 누락/skip/중복 음성 fixture를 확인한다.
- 실제 `artifacts/unity-consumer.U1ob4f/results.xml`은 두 marker 검사 PASS. `test_unity_consumer_result.py` 1 test PASS/skip 0(누락·skip·중복 fixture 포함). 커밋 준비: R11 test source·결과 parser·offline 격리 runner 및 원장만 포함한다. 신규 source 재실행 전 manifest는 PARTIAL 유지한다.
- R11 커밋된 테스트 코드를 동일 버전의 격리 consumer에서 재실행한다. 실행 전 진행 기록을 커밋하며 사용자 Demo 및 다른 Unity 프로젝트는 변경하지 않는다.
- clean tracked source `a0ba7a5`의 `scripts/build-unity.sh --editor-smoke` 종료 0 (`artifacts/unity-consumer.EfzZEr/results.xml`): Unity 6000.5.8f1 Editor에서 domain reload enabled/disabled 2건 PASS/skip 0, 각 완료 marker, scene 전환·client dispose/recreate·이전 session synthetic callback 차단·dispatcher 1→0 확인. 실제 OS callback이나 Player 대체가 아닌 Editor 범위다.
- 실제 Editor 테스트·marker 및 격리 package 조건을 `docs/evidence/r11-unity-scene-domain-reload.md`에 기록하고 R11을 해당 범위로 매핑했다. manifest 및 진행 원장을 검증한다.
- `harness/check-manifest.py`, `harness/check-manifest-negative.py`, `scripts/verify-progress.py` 종료 0. 커밋 준비: R11 실제 Editor 결과의 요약·manifest 및 원장만 저장한다. 원본 로그·Unity project는 Git에 넣지 않는다.
### P09 R09 UTF-8 JNI 및 C ABI 검증 시작
- Android Unity Player에서 C#→AndroidJavaClass→Kotlin→AndroidJavaProxy→Unity 이벤트의 한국어/emoji를 확인하고, iOS C ABI 입력 buffer 재사용과 callback 데이터 복사 후 문자열 동일성을 직접 검증한다. 단순 JSON parser나 링크 성공을 ABI PASS로 대신하지 않는다.
- `CBridgeTests.testHostPushEventRoutingAndDedup`이 원시 UTF-8 `한글 🎮🚀`을 포함한 요청을 GB_Dispatch 후 즉시 덮어쓰고 callback이 복사한 메시지 ID 동일성을 검사하도록 강화했다. iOS C ABI test 실행 전이다.
- `swift test --package-path ios --filter CBridgeTests.testHostPushEventRoutingAndDedup` 종료 0, XCTest 1건 PASS/skip 0: 실제 GB_Dispatch 입력을 반환 직후 덮어쓴 뒤 복사된 callback의 한국어·emoji 동일성 확인. macOS host ABI 시험이며 iOS 실제 기기는 아니다.
- Android UTF-8 Player probe managed compile 종료 0, 경고·오류 0. 커밋 준비: iOS C ABI의 명시적 버퍼 복사 시험과 Android JNI probe/run option만 포함하며 Android 실제 JNI 검증은 재실행 전이다.
- `harness/run-unity-android-mock-e2e.py --utf8-probe`를 새 전용 AVD에서 실행한다. Java→AndroidJavaProxy callback 이후 문자열 및 main-thread가 일치해야 PASS다. 실행 전 기록을 커밋한다.
- R09 iOS C ABI 한국어·emoji/입력 버퍼 덮어쓰기의 macOS host test는 통과했으나 iOS Simulator 실행은 별도다. 기존 CBridgeTests를 Swift Package product와 연결하는 전용 simulator XCTest target을 생성한다.
- XcodeGen에 GameBridgeCBridgeTests target/scheme을 추가하고 Swift package의 GameBridgeUnityBridge·Core를 연결했다. 사용자 기존 Xcode project는 변경하지 않는다. 새 전용 iOS 18.6 Simulator에서 UTF-8 C ABI test를 실행한다.
- `xcodebuild ... -scheme GameBridgeCBridge -only-testing:GameBridgeCBridgeTests/CBridgeTests/testHostPushEventRoutingAndDedup test -quiet` 종료 0, `artifacts/r09-ios-20261112203456.xcresult`: 1 test PASS/failed 0/skipped 0. iOS 18.6 전용 Simulator에서 C ABI 원시 UTF-8 입력 buffer 덮어쓰기와 callback 한국어·emoji 동일성을 확인했다. Android JNI는 별도 진행 중.
- `harness/run-unity-android-mock-e2e.py --run-local --utf8-probe ...` 전용 Android 36 AVD 실행 종료 0 (`artifacts/unity-android-e2e-c26jgz32`): Unity C#→AndroidJavaClass→Kotlin bridge→AndroidJavaProxy callback→Unity 이벤트에서 `한글 🎮🚀` 동일성 및 main-thread 확인. 최초 전체화면 안내는 수동으로 닫았다. iOS Simulator의 C ABI test 1건 PASS와 별도로 기록한다.
- Android source `11dcde9`, tracked-clean 결과 PASS; iOS Simulator는 동일 기반에 당시 미커밋 `ios/Framework/project.yml`의 CBridge XCTest target을 추가한 working diff에서 test 1건 PASS. 커밋 준비: XcodeGen test-only target과 검증 기록을 저장하며 제품 SDK binary 변경은 없다.
- `docs/evidence/r09-jni-cabi-utf8.md`에 Android tracked-clean 실 Player와 iOS Simulator 1건의 당시 test-only working diff를 명시했다. 새 `harness/run-r09-utf8.py`는 현재 source Android Player 및 iOS XCTest를 각각 새로 실행하고 성공·skip/marker를 검사한다. wrapper 전체 재실행은 아직 NOT_RUN이다. manifest 검사 시작.
- `harness/check-manifest.py`, `harness/check-manifest-negative.py`, `scripts/verify-progress.py`, wrapper `py_compile` 종료 0. 커밋 준비: R09 evidence, 재현 runner, manifest 및 작업 이력만 포함한다.
### P09 R43 iOS host delegate 및 Unity 전달 경계 시작
- 기존 `PushHostTests.testSyntheticHostCallbacksAndCompletion`은 iOS Simulator에서 기존 delegate 보존과 completion 호출을 확인했으나 Unity host adapter 연결 자체는 검증하지 않았다. 별도 Unity iOS Player에서 synthetic iOSNotification을 host adapter에 전달해 Swift bridge 및 Unity callback을 검사한다. APNs 실제 원격 발송은 아니다.
- 테스트 소비 앱은 synthetic `iOSNotificationPushTrigger`를 Unity host adapter에 전달하고 Swift bridge가 되돌린 `PushReceived` 이벤트의 단일 전달과 main-thread를 검증한다. SDK 또는 실제 APNs provider를 수정하지 않으며 실제 Player 실행 전이다.
- iOS Runner Python 문법 검사 종료 0. 커밋 준비: test-only Unity host probe, 제한적인 linker 보존 설정 및 runner 옵션만 포함한다. 실행 결과는 아직 없다.
- `harness/run-unity-ios-mock-e2e.py --run-local --adhoc --host-callback-probe ...`를 새 Simulator/DB에서 실행한다. 실제 remote APNs가 아니다. 시작 기록을 커밋한다.
- `harness/run-unity-ios-mock-e2e.py --host-callback-probe` 새 Simulator E2E는 Unity export 단계에서 exit 1 (`artifacts/unity-ios-e2e-429_2_xw`). C ABI/Player 실행 전이므로 원인을 조사한다.
- Unity Editor.log `Assets/MockIosPlayerScenario.cs(9,18) CS0234`: `GameBridge.iOSHost`는 iOS 전용 assembly인데 using이 Editor에도 노출됐다. test-only consumer에 `UNITY_IOS && !UNITY_EDITOR` 조건을 추가한다. 제품 SDK 자체의 변경은 없다.
- 커밋 준비: iOS 전용 using 조건 및 실제 compile 실패 원인만 기록한다. 새 test source의 Player 검증은 미실행이다.
- iOS host callback probe를 새 Simulator·DB에서 다시 실행한다. 실행 전 기록을 커밋한다.
- `GameBridgePushTests/PushHostTests.testSyntheticHostCallbacksAndCompletion`를 새 Simulator에서 별도로 실행하여 기존 delegate 보존 및 host completion을 재검증한다. 실제 APNs 발송은 아니다.
- `GameBridgePushTests/PushHostTests.testSyntheticHostCallbacksAndCompletion` 새 Simulator XCTest 종료 0, 1건 PASS/skip 0 (`artifacts/r43-ios-20261112204204.xcresult`). 기존 notification delegate 보존과 sample host completion을 합성 입력으로 확인했다. APNs 원격 수신 및 Unity host는 이 결과에 포함하지 않는다.
- `harness/run-unity-ios-mock-e2e.py --run-local --adhoc --host-callback-probe ...` 새 iOS Simulator 실행 종료 0 (`artifacts/unity-ios-e2e-f7bwumjl`): test-only synthetic iOSNotification host adapter→Swift C ABI→Unity PushReceived, 동일 이벤트 중복 억제·main-thread 및 기존 LOCAL_MOCK 인증/구매 흐름 확인. 이는 실제 APNs 전달이 아니다.
- `docs/evidence/r43-ios-host-unity-boundary.md`에 Swift host Simulator XCTest와 Unity iOS Player의 분리된 synthetic host callback 실측을 정리했다. 신규 `harness/run-r43-host.py`는 현재 source의 새 두 실행을 요구한다. manifest·runner 문법을 검증한다.
- R43 `py_compile`, manifest/음성 및 진행 원장 검사 종료 0. 커밋 준비: 실제 Simulator host XCTest·Unity Player evidence, 두 새 실행을 요구하는 wrapper 및 manifest만 포함한다.
### P09 R40 실제 Android 권한 거부 검증 시작
- Android 13+ 전용 테스트 Player에서 OS 알림 권한을 명시 요청하고 거부한 후 SDK 등록 차단 및 재요청 상태를 확인한다. Firebase/실제 Google 로그인 또는 원격 발송은 사용하지 않는다. iOS/Mock 거부 및 Android 실제 결과를 혼동하지 않는다.
- `tests/UnityAndroidPermissionConsumer/MockPlayerScenario.cs`는 합성 sandbox 설정으로 알림 권한만 요청하며 계정 로그인/외부 network를 사용하지 않는다. 실제 Android permission dialog와 재요청은 별도 에뮬레이터 실행 전이다.
- Android test-only permission 시나리오 managed compile 종료 0. 격리 소비 프로젝트에만 POST_NOTIFICATIONS 및 Unity 자동 권한창 생략 설정을 추가하고 명시적 SDK 요청으로 실제 OS dialog를 검증한다.
- `regression-manifest.json` 현재 48 IMPLEMENTED, 2 PARTIAL(R22/R40). `docs/CI.md`와 `docs/FINAL_REPORT.md`의 이전 44/6 집계를 갱신했고, 실제 실행 중인 R40은 아직 승격하지 않았다.
- 격리 Unity 소비 프로젝트의 Android OS 권한 test APK 빌드 `bash scripts/build-unity-android-mock.sh ...` 종료 0 (`artifacts/r40-android-permission.apk`). 실제 권한 거부/재요청은 새 AVD에서 수행한다.
- 전용 Android 36 AVD의 실제 OS 알림 dialog에서 거부 후 Unity `GB_PERMISSION_FIRST_DENIED PASS`를 확인했다. 이어 `GB_PERMISSION_RESULT FAIL stage=registration type=InvalidOperationException`으로 test FAIL. 현재 test가 다른 SdkException code를 숨겨 root cause를 특정할 수 없어 오류 코드만 안전하게 출력하도록 보강한다. Player 종료·재요청은 미확인이다.
- R40 test-only consumer가 등록 성공 여부 또는 SdkException의 허용된 code만 출력하도록 변경한다. 새 APK 빌드 후 전용 AVD에서 동일 실제 OS 거부를 재현한다.
- R40 test-only consumer에 code 진단을 추가한 Unity Android APK 두 번째 빌드 종료 0 (`artifacts/r40-android-permission-2.apk`). 기존 전용 AVD를 종료만 하고 새 AVD에서 권한 dialog를 다시 검증한다.
- 두 번째 전용 Android AVD의 OS dialog 거부 후 `GB_PERMISSION_REGISTRATION_CODE CONFIG_REQUIRED`. 코드상 Firebase host class linkage 실패가 permission check보다 앞설 수 있어 해당 결과만으로 PERMISSION_DENIED 차단을 주장하지 않는다. 실제 Firebase 설정·계정·원격 발송 없이 테스트 앱에 SDK dependency만 제공해 재시험한다.
- 격리 테스트 프로젝트의 Gradle postprocess에 `firebase-messaging:26.0.1` runtime dependency만 추가했다. 앱 계정/서비스 설정은 하지 않으며 permission 거부 시 token 획득이나 network 전에 차단되는지 확인한다. 이 문제에 대한 세 번째 원인 기반 시도다.
- R40 test-only Firebase dependency를 포함한 Unity Android APK 빌드 종료 0 (`artifacts/r40-android-permission-3.apk`). 서비스 키나 Firebase 프로젝트는 추가하지 않았다. 새 전용 AVD에서 세 번째 원인 기반 재검증을 수행한다.
- R40 세 번째 원인 기반 재시험: 격리 Unity Android Player와 새 Android 36 AVD에서 OS 알림 dialog를 두 번 수동 거부. 첫 요청 DENIED, Firebase SDK dependency가 존재할 때 등록 `PERMISSION_DENIED`, 두 번째 요청 DENIED, `GB_PERMISSION_RESULT PASS ANDROID_OS_DENIED` 확인 (`artifacts/r40-android-os-denial-20261112/markers.log`). test-only Firebase 앱 설정·계정·원격 연결 없음. 초기 전체화면 안내도 수동으로 닫았다. 이전 두 시도는 Firebase dependency 부재로 CONFIG_REQUIRED가 우선되어 권한별 차단을 증명하지 못했다. iOS OS 및 Mock 거부 주입은 NOT_RUN이며 R40은 PARTIAL이다.
### P09 사용자 요청 일시 중단 및 재개 지점
- 현재까지 R49(양 플랫폼 신규 Unity consumer 실제 기존 근거), R11(Unity Editor domain reload 두 설정 및 scene/재생성/합성 callback), R09(Android JNI Player 및 iOS Simulator C ABI UTF-8), R43(iOS synthetic host delegate + Unity Player 경계)를 검증하고 IMPLEMENTED로 매핑했다. manifest 총 50개 중 48 IMPLEMENTED, 2 PARTIAL(R22/R40), NOT_IMPLEMENTED 0.
- CI는 inventory/backend/Android/Swift hosted 기본 gate, opt-in self-hosted Unity 실제 실행 gate, fail-closed Release readiness로 분리했다. Ruby YAML 구문 및 로컬 음성 unit 3건은 PASS이나 GitHub Actions 실제 실행은 NOT_RUN. strict-local 이번 변경 후 NOT_RUN; `push/unity-player-notifications`의 실제 Player 집계 연결도 아직 미구현/DEFERRED_ENV이므로 release PASS로 주장하지 않는다.
- R40 Android 36 OS 두 차례 권한 거부·등록 차단은 실제 Player에서 부분 확인했다. iOS OS 권한·Mock 거부 주입과 R22의 SDK 로그/Unity 결과/Backend 오류 민감정보 검사 완료가 남았다. R40 test-only Firebase dependency/consumer는 이번 커밋에 포함하며 서비스 인증 및 원격 발송은 하지 않았다.
- 네트워크 중단을 앞둔 사용자 요청에 따라 새 작업을 시작하지 않고 여기서 중단한다. 재개 시 문서와 Git 상태를 읽고 남은 R22/R40, strict-local 전체, CI Unity push 결과의 fresh-source 집계 및 README/FEATURE_MATRIX/FINAL_REPORT 일관성 감사를 계속한다. 기존 미추적 Demo/cache와 모든 테스트 artifacts·DB·AVD를 보존하고 push하지 않는다.
- 중단 전 `python3 scripts/verify-progress.py`, `python3 harness/check-manifest.py`, `git diff --check` 종료 0. 커밋 준비: R40 test-only 코드/부분 증거, CI/FINAL_REPORT 현재 집계와 재개 기록만 포함한다. Unity Player 전체 또는 CI 성공을 새로 주장하지 않는다.
### P09-T06 Unity Push 실측 집계 연결 시작
- strict의 `unity-player-notifications`는 이전 Player PASS 이후에도 무조건 DEFERRED_ENV다. 명시적 opt-in과 별도 전용 Android AVD가 제공될 때만 현재 source의 Android/iOS Push Player runner를 새로 실행하고 각 result·marker를 검증해 집계하는 경로를 추가한다. 이전 결과 재사용, 누락·실패를 PASS로 바꾸는 것을 금지한다.
- `harness/run-unity-push-current.py`는 별도 전용 Android AVD와 iOS 신규 Simulator에서 두 실제 Runner를 실행하며 정확한 source·clean·status·marker·재연결 거부·token 삭제를 확인한다. 미지정 시 strict lane은 계속 DEFERRED_ENV다. self-hosted CI는 인증/구매 AVD와 서로 다른 push AVD를 요구한다. 현재 구현은 아직 실제 재실행 전이다.
- 현재 run source 일치·Player PASS·두 플랫폼 별 네트워크 결과·재연결 관측·token 삭제·필수 marker가 빠지면 false가 되는지 격리 result fixture로 음성 검증한다. 실제 Unity E2E를 테스트 fixture로 대체하지 않는다.
- `test_unity_push_current.py` 1건, `test_ci_gate.py` 3건 PASS/skip 0. 둘 다 합성 증거 및 gate 검사다. Player 재실행은 NOT_RUN. 두 Player를 순차 실행하는 lane에 기존 600초 제한이 부족할 수 있고 테스트가 기존 artifacts 디렉터리를 가정하는 문제를 발견해 보완한다.
- 깨끗한 checkout을 가정한 임시 root에서 Push 증거 단위 1건, CI gate 3건, 집계 13건 PASS/skip 0. Python compile, shell 구문 및 Ruby YAML parse PASS. 순차 Player 실행의 외부 timeout을 확장했다. 실제 양 플랫폼 Player 및 GitHub Actions는 이번 변경에서 NOT_RUN이다. 커밋 전: 관련 실행기·CI·검증 문서만 포함한다.
### P09-T03/R22 민감정보 검증 재개
- 로그와 Unity 공개 결과에서 synthetic token·secret의 노출을 각각 확인할 기존 경로와 검증을 조사한다. 실제 credential은 사용하지 않는다.
- Kotlin/Swift diagnostics는 enum·UUID만 수용하고 기존 bridge 시험은 synthetic secret을 주입한다. Unity Player 전체 공개 결과 및 Backend 오류 로그를 포괄하는 시험은 아직 확인되지 않았다. 기존 Android BridgeDispatcher 및 Swift CBridge synthetic 시험을 현재 소스에서 재실행한다.
- Android 검증 첫 호출 `./gradlew`는 저장소 루트에 파일이 없어 exit 127이며 테스트 NOT_RUN. `./android/gradlew`로 수정해 재실행한다. Swift 시험은 실행 중이다.
- `./android/gradlew -p android :sdk-core:test --tests com.gamebridge.BridgeDispatcherTest --tests com.gamebridge.DiagnosticsTest` exit 0; synthetic secret 오류·typed diagnostics. `swift test --package-path ios --filter CBridgeTests|DiagnosticsTests` exit 0, XCTest 5건/실패0. 실제 Unity Player 전체 및 Backend 오류 로그는 포함되지 않아 R22 PARTIAL.
- Backend ApiErrors 예외 로그는 타입만 기록하도록 구현되어 있으나 이를 실제 logger 및 HTTP 응답으로 검증하는 회귀가 없다. MockMvc와 in-memory log appender에서 synthetic secret 노출을 확인한다.
- `./backend/gradlew -p backend test --tests com.gamebridge.config.HttpInfrastructureTest` exit 0: MockMvc 요청 header/body와 예외 메시지에 합성 secret을 주입하고 500 응답 및 캡처된 ApiErrors logger의 메시지·예외 stack 부재를 확인했다. 실제 계정·전체 서버 로그·Unity Player는 범위 밖. 앞선 Android 4건과 Swift 5건도 PASS. 커밋 전: 테스트와 진행 기록만 포함, R22 PARTIAL 유지.
### P09-T05/R40 iOS 권한 거부 재개
- Unity iOS host adapter의 OS 거부·재요청과 등록 차단을 실제 Simulator에서 확인할 수 있는 기존 격리 test 경로를 조사한다. Mock 거부는 별도다.
- `tests/UnityIosPermissionConsumer/MockIosPlayerScenario.cs`는 sandbox 설정과 실제 iOS host adapter로 DENIED→PERMISSION_DENIED→DENIED를 검사한다. 계정 로그인·원격 APNs를 사용하지 않으며 아직 컴파일·Simulator 실행 전이다.
- iOS 권한 소비자에 Unity notifications 의존성을 격리 프로젝트에 포함하고 새 Unity Simulator Xcode export를 시도한다. 기존 Simulator·프로젝트는 수정하지 않는다.
- `artifacts/unity-ios-mock.PLDU8j`의 새 격리 프로젝트에서 iOS 권한 소비자 Unity export exit 0. Simulator Xcode build·Player·OS 권한은 아직 NOT_RUN이다.
- export된 격리 Xcode 프로젝트를 Simulator arm64와 ad-hoc 서명으로 빌드한다. 빌드 출력은 로컬 artifacts에만 둔다.
- `artifacts/unity-ios-mock.PLDU8j`의 iOS Simulator arm64 Xcode build exit 0, ad-hoc 서명. Player 권한 시험은 아직 미실행이다. 새 전용 Simulator를 생성한다.
- 전용 Simulator C766DB3F-3D32-499F-AF04-CA3960842487 부팅 PASS. 설치 시 고정한 `Unity-iPhone.app` 경로가 없어 simctl 설치 실패, 앱 실행은 NOT_RUN이다. 결과 명령의 마지막 cat 성공을 설치 성공으로 간주하지 않는다. 실제 산출물 경로를 확인한다.
- 새 iOS 18.6 Simulator C766DB3F-3D32-499F-AF04-CA3960842487에서 격리 Unity Player를 실행하고 OS 알림 팝업의 허용 안 함을 선택했다. 첫 DENIED, SDK 등록 PERMISSION_DENIED, 재요청 DENIED marker 모두 PASS (`artifacts/unity-ios-mock.PLDU8j/player-console.log`). 현재 HEAD e0acbd6 + 미커밋 test-only 소비자 소스. 합성 sandbox 설정이며 APNs 전송·실기기·Mock 거부 주입은 NOT_RUN, R40 PARTIAL이다.
- iOS OS 권한 marker만 정제하여 `docs/evidence/r40-ios-os-permission-partial.md`에 기록했다. 커밋 전: 전용 테스트 소비자와 부분 증거·진행 기록만 포함하며 raw 로그·빌드 산출물은 제외한다.
### P09-T05/R40 Mock 거부 주입 시작
- 실제 EditorOfflineTransport를 감싼 test-only transport에서 permission 요청의 DENIED 응답만 주입한다. 로그인 후 실제 EditorOffline 등록 로직이 PERMISSION_DENIED를 반환하고 재요청도 거부되는지 Unity C# 공개 API로 확인한다. 실제 Unity Player/OS 검증과 구분한다.
- `UNITY_EDITOR_PATH=<installed Unity> bash scripts/smoke-unity-mock-permission.sh` exit 0: test transport가 permission DENIED만 주입하고 Unity C# 공개 API가 실제 EditorOffline 등록의 PERMISSION_DENIED와 재요청 DENIED를 처리했다. 독립 .NET managed fake이며 Unity Editor/Player 실행이 아니다. Android/iOS OS는 별도 부분 증거로 보존하고 R40 자동 scenario 연결 전 PARTIAL 유지. 커밋 준비: 테스트와 문서만 포함한다.
### P09-T06 현재 소스 strict-local 재검증 시작
- `harness/run-strict-local-isolated.py --run-local`을 최신 staged UPM으로 실행한다. 새 DB/role과 전용 simulator를 보존하며 외부 제공자 credential을 사용하지 않는다. Unity Editor/Push Player는 이 호출에서 별도 opt-in이 없어 미실행으로 집계한다.
### 테스트 Simulator 정리 시작
- 사용자 요청에 따라 부팅된 GameBridge 테스트 전용 Simulator 중 현재 strict 시험용을 제외하고 shutdown한다. 삭제·초기화는 하지 않으며 타 앱·타 Simulator는 건드리지 않는다. 향후 독립 상태가 불필요한 시험은 전용 Simulator를 재사용한다.
- 부팅된 GameBridge 기기 전체를 열거하는 종료 명령은 strict 구매 검증이 도중에 만든 새 기기를 포함할 가능성이 있어 중단(exit 130). 일부 기존 기기는 종료됐을 수 있다. 작업 시작 전 확인한 기존 Simulator ID만 대상으로 제한해 계속한다. 기기 삭제는 없다.
- 시작 전에 확인한 기존 GameBridge Simulator만 shutdown했다. 두 번째 제한 목록에서 남아 있던 7개는 exit 0; 앞선 중단된 일괄 명령에서 이미 종료된 기기도 있다. 기기와 데이터는 삭제하지 않았다. strict 검증용 기기는 목록에서 제외했다.
- `GAMEBRIDGE_UPM_STAGING=<validated stage> python3 harness/run-strict-local-isolated.py --run-local` exit 1, 전체 FAIL; 결과 `artifacts/verify-all-n8ajxtoz/summary.md`, orchestration `artifacts/strict-isolated-okbwk6f6`. 소스 HEAD 9b02b71 + 문서 변경 및 기존 미추적 파일, 외부 13개 WAITING_USER. 세부 lane과 Simulator 종료가 실행에 영향을 주었는지 확인한다.
- `xcresulttool` 결과 XcodeStoreKitLocalDatabaseTests 1건은 `Test crashed with signal term`, exit 65; 명확한 제품 결함 원인은 확인되지 않았다. 기존 Simulator shutdown과 시간대가 겹치므로 간섭 가능성을 배제하지 않고, 전용 새 DB/Simulator에서 해당 시험을 따로 재실행한다. Process-recovery는 독립 PASS.
- 동일 `harness/run-xcode-storekit-e2e.py --run-local` 단독 재시험 exit 0, `artifacts/xcode-storekit-e2e-he6ows9_/result.json` PASS 1건/skip0: Xcode local StoreKit 및 합성 DB 복구만 확인. 이전 strict run의 signal TERM FAIL은 변경하지 않고 원인도 확정하지 않는다. 단독 성공을 strict 전체 성공으로 대체하지 않는다.
- 커밋 전: strict 전체 실패·미실행·재시험 결과와 사용자 요청에 따른 기존 기기 shutdown 기록만 포함한다. Simulator/DB와 미추적 사용자 파일은 삭제하지 않는다.
### P09-T03/R22 Unity typed 결과 경계 재검증 시작
- 기존 purchase error·fingerprint 검사 외에 profile/purchase/push 응답에 synthetic access token·receipt·push token 필드를 주입하고 typed 결과 직렬화에서 사라지는지 확인한다. 독립 managed test이며 Player 전체 로그를 대체하지 않는다.
- 새 결과 redaction smoke의 첫 빌드는 `JsonConvert` namespace 누락 3건(CS0103)으로 실패했고 시험은 미실행이다. 참조 이름을 수정해 재실행한다.
- namespace 수정 후 `UNITY_EDITOR_PATH=<installed Unity> bash scripts/smoke-csharp-registry.sh` exit 0. 합성 credential 추가 필드가 profile·purchase·push typed 결과의 직렬화에서 제거됨을 확인했다. standalone managed test이며 Unity Player나 실제 credential 시험이 아니다. R22 PARTIAL 유지. 커밋 전: 시험 및 기록만 포함.
### P09-T06 Unity Push 동일 실행 실측 시작
- `harness/run-unity-push-current.py` 양 플랫폼 실행을 검증한다. Android runner는 기존 테스트 앱 설치 기기를 거부하므로 별도 비어 있는 GameBridge_V2_ AVD가 필요하다. iOS runner도 독립 Simulator를 만든다. 현재 HEAD와 tracked-clean 조건을 지키기 위해 시작 기록을 먼저 커밋한 뒤 실행하고 이전 PASS는 재사용하지 않는다.
- 커밋 전: 실측 시작 기록만 저장한다. 실제 Player 결과는 아직 NOT_RUN이다.
- `GAMEBRIDGE_RUN_UNITY_PUSH_E2E=true ... python3 harness/run-unity-push-current.py` exit 0, 양 플랫폼 실제 Unity LOCAL_MOCK Player 2건 PASS. 소스 f40f8d5, tracked-clean; Android `artifacts/unity-android-push-0b67f62g`, iOS `artifacts/unity-ios-push-ejpifgez`. 중복·foreground/background·연결 복구·late callback·계정 전환·token 삭제와 marker를 각 runner 및 상위 gate가 확인했다. Android 신설 AVD 최초 전체화면 안내는 수동으로 닫았다. 이는 GitHub Actions·실제 FCM/APNs·실기기 검증이 아니다.
- 결과 파일 요약 재확인 명령의 작업 디렉터리 오타로 프로세스가 시작되지 않았다. Player 통과 결과는 별도이며 올바른 경로로 재확인한다.
- 양 result JSON의 source·tracked-clean·Player PASS·token 0 및 플랫폼별 network 범위를 재확인했다. 사용자 요청에 따라 실행 종료 후 테스트 iOS Simulator 2개 및 Android emulator를 shutdown했고 데이터는 삭제하지 않았다. 커밋 전: 공개 요약·진행 및 CI 문서만 포함, raw log·APK·DB는 제외.
### P09-T05/R40 Mock 거부 집계 연결 시작
- 독립 managed 거부 주입 시험을 `run-push-regression.py`와 strict 필수 lane에 연결한다. 시험이 실행되지 않거나 marker가 없을 때 aggregate가 성공하지 않게 한다. 실제 OS 수동시험은 별도 증거다.
- Mock 거부 managed 시험 exit 0, 집계 음성 포함 13건 PASS/skip0, Python compile PASS. 다음으로 독립 Push runner에서 새 lane 실제 집계와 누락 환경의 비성공을 확인한다.
- `UNITY_EDITOR_PATH=<installed Unity> python3 harness/run-push-regression.py` exit 2: 새 mock-permission-denied 1건 PASS, backend/Android/Swift fake 각 PASS, DB·iOS host·staging·Player 등 미제공 lane은 DEFERRED_ENV (`artifacts/push-regression-0qh7drmi/result.json`). 전체 성공이 아니다. 커밋 전: 필수 lane 및 기록만 포함, OS 수동시험 자동 재현은 여전히 미완료.
### P09-T07 self-hosted 환경 사전검사 보완
- strict의 managed 검증이 UNITY_EDITOR_PATH를 요구하지만 CI preflight와 문서에서 이를 빠뜨린 점을 확인했다. build 전에 명시적으로 확인해 환경 누락이 늦게 드러나지 않도록 한다.
- `bash -n scripts/ci-unity-e2e.sh` 및 CI gate 단위 3건 PASS/skip0. 잘못된 UNITY_EDITOR_PATH가 실제 build 실행 전 거부되는지 별도 음성 시험을 추가한다.
- 잘못된 Unity 실행 파일 경로를 조기에 DEFERRED_ENV로 거부하는 시험 포함 `test_ci_gate.py` 4건 PASS/skip0, shell 문법 PASS. GitHub Actions 실제 실행은 NOT_RUN. 커밋 전: 사전검사·음성 시험·문서만 포함한다.
### P11 현재 증거 문구 정합성 점검 시작
- 기존 Android R40 증거가 당시 iOS/Mock NOT_RUN이라고 적고 있어 현재 증거에 대한 오해를 막을 현재 상태 연결 문장을 추가한다. 개별 시험 당시 사실과 전체 PARTIAL/실플랫폼 미검증은 보존한다.
- R40 과거 시점별 증거와 USER_SETUP·FEATURE_MATRIX·FINAL_REPORT 주요 항목의 현재 결과를 정정하고 `verify-progress.py` PASS. 각 문서의 나머지 과거 Unity 미실행 표현은 당시 산출물과 현재 결과를 구분해 추가 점검한다.
- `python3 scripts/verify-progress.py`, `python3 harness/check-manifest.py`, `git diff --check` exit 0. 문서 검사는 제품 시험이 아니다. 커밋 전: R40 시점별 증거와 사용자 설정·기능 matrix·보고서의 오류 표현만 정정하며 strict FAIL과 실연동 미검증을 유지한다.
### P09-T06 격리 strict 실행 시간 제한 점검
- Push runner 내부는 양 Player 합산 최대 3300초인데 isolated orchestration은 전체 strict를 900초로 제한한다. 명시적 Unity Push opt-in에서 긴 실행을 중간에 끊을 수 있어 외부 timeout 일관성을 검토한다.
- isolated 전체 900초는 opt-in Unity Push의 3600초 상위 timeout보다 짧아 양 Player가 진행 중이어도 잘릴 수 있다. opt-in true에만 전체 5400초를 적용하고 기본 900초는 유지한다.
- `test_strict_timeout.py` 1건, `test_aggregation.py` 13건 PASS/skip0 및 Python compile PASS. opt-in에서 장시간 전체 strict 실행은 아직 NOT_RUN이다. 커밋 전: timeout 조정·단위 검사·CI 등록만 포함한다.
### P09-T03/R22 Unity Player 결과 경계 확장 시작
- Android/iOS test-only LOCAL_MOCK consumer의 인증·구매·진단 결과를 직렬화해 해당 실행의 합성 개발키가 포함되지 않는지 검사한다. raw token·실제 provider·전체 로그 증거를 대신하지 않는다. 실제 Player 재실행 전까지 NOT_RUN이다.
- Android/iOS test-only consumer가 profile·purchase·diagnostics를 직렬화해 현재 합성 개발키 부재를 확인하고 marker를 출력한다. 두 E2E runner는 이 marker가 없으면 FAIL이다. 아직 컴파일·실행 전이다.
- Android consumer `check-unity-android-mock-compile.sh` exit 0, 경고·오류 0; 두 Python runner compile PASS. iOS 조건부 소비자도 같은 격리 참조로 컴파일한다. 이는 Player 실행이 아니다.
- iOS `UNITY_IOS` 조건부 consumer managed compile exit 0, 경고·오류 0; Android도 동일. 실제 Player는 아직 NOT_RUN. 커밋 전: test-only 결과 검사·runner marker·기록만 포함, R22 PARTIAL 유지.
### P09-T03/R22 Player 실제 재검증 시작
- source cc3cc60 test-only 결과 검사를 새 Android/iOS Player에서 실행한다. Android는 기존 설치된 테스트 앱을 보존하므로 빈 전용 AVD를 만든다. 기존 Player 결과를 새 실행으로 재사용하지 않는다.
- 커밋 전: 실제 실행 시작 기록만 포함한다. 실행 결과는 NOT_RUN이다.
- `run-unity-android-mock-e2e.py` exit 1 `UNITY_RESULT_REDACTION_MISSING` (`artifacts/unity-android-e2e-419abzrk`). 새 marker 부재를 정확히 분류하며 Player 통과를 주장하지 않는다. iOS는 NOT_RUN.
- Android runner 검토에서 두 원인을 확인했다: logcat allowlist에 REDACTION이 없고, Player 최종 PASS 전에 새 marker 부재를 즉시 실패시켰다. 조기 실패이므로 Player 성공·노출 여부는 미확정. 두 문제와 marker 누락 거부·미완료 대기를 검증한다.
- `test_unity_redaction_marker.py` 2건 PASS/skip0: 실행 중은 대기, 최종 PASS에 marker가 없으면 FAIL, 로그 필터가 marker를 보존한다. Python compile PASS. 실제 수정 Player 재실행은 NOT_RUN. 커밋 전: runner 수정·음성 테스트·실패 이력만 포함.
- 수정 runner의 실제 Player 재시험을 시작한다. 실패한 기존 AVD의 앱과 데이터는 보존하고 종료 후 새 빈 AVD에서 실행한다. iOS도 해당 실행 source를 기록한다.
- 커밋 전: 재검증 시작 기록만 포함한다. Player 결과는 미실행이다.
- 수정 Android runner 재실행 exit 0, `artifacts/unity-android-e2e-m62mfexg`: Unity LOCAL_MOCK 인증·구매·진단 결과에 합성 개발키가 없는 marker PASS, source 7156dac tracked-clean; 최초 전체화면 안내 수동 처리. 이전 e1f83e1 runner 실패는 보존한다. iOS 및 실제 credential 검증은 별도다.
- 커밋 전: Android 재시험 기록만 포함한다. iOS Player는 미실행이다.
- iOS Unity LOCAL_MOCK consumer의 인증·구매·진단 결과에 synthetic 개발키가 없는지 실제 Simulator Player에서 새로 확인한다. 실행 전이며 실 Apple/APNs는 사용하지 않는다.
- 커밋 전: iOS 실행 시작 기록만 포함한다.
- `run-unity-ios-mock-e2e.py --run-local --adhoc` exit 0 (`artifacts/unity-ios-e2e-nz5fz8r5`): Unity iOS LOCAL_MOCK 인증·구매·진단 결과에서 합성 개발키 비노출 marker와 기존 흐름 PASS. 실제 Apple 인증·실제 token·전체 로그 범위는 검증하지 않아 R22 PARTIAL이다.
- Android source 7156dac와 iOS source b2087e1 각각 tracked-clean·Player PASS를 재확인했다. 요청에 따라 사용한 Simulator/AVD는 shutdown만 했고 데이터는 보존했다. 커밋 전: 정제된 부분 증거와 진행 기록만 포함한다.
### P09-T02/R22 공유 consumer 회귀 호환성 점검 시작
- Android UTF-8 및 iOS host callback 전용 소비자가 동일 runner를 사용한다. 새 필수 redaction marker가 해당 소비자에 없어 회귀 시험이 잘못 실패할 가능성을 확인해 수정한다.
- R09/R43 전용 test consumer에는 합성 개발키 결과 검사가 없는데 공유 runner는 marker를 필수로 요구한다. 제품 결함이 아닌 시험 호환성 결함이며 실제 R09/R43 재실행은 아직 NOT_RUN. 같은 profile/purchase/diagnostics 검사를 양 consumer에 추가한다.
- R09 Android UTF-8 및 R43 iOS host consumer에 같은 개발키 결과 비노출 검사를 추가했고 marker 단위 2건 PASS. 이제 양 조건부 managed compile을 검증한다. 실제 Player 재실행은 별도다.
- Android UTF-8 `UNITY_ANDROID`, iOS host `UNITY_IOS` consumer 각각 managed compile exit 0, 경고·오류 0. 이는 실제 Player 재실행이 아니다. 향후 네 소비자 중 marker 누락을 방지할 inventory 검사를 추가한다.
- `test_unity_redaction_marker.py` 3건 PASS/skip0, 원장 및 diff 검사 PASS. R09/R43 전용 consumer의 실제 수정 후 Player는 미실행이며 이전 source의 성공과 구분한다. 커밋 전: 전용 test consumer·inventory 검사·기록만 포함한다.
- 수정된 iOS host callback 전용 Unity LOCAL_MOCK consumer를 새 Simulator에서 실행한다. host callback은 합성 주입이며 실제 APNs가 아니다. 실행 시작 기록을 먼저 커밋한다.
- 커밋 전: 시작 기록만 포함하고 실제 시험은 NOT_RUN이다.
- `run-unity-ios-mock-e2e.py --run-local --adhoc --host-callback-probe` exit 0 (`artifacts/unity-ios-e2e-fj2ddrvp`): 수정 host consumer에서 기존 합성 callback·중복 억제·main-thread와 결과 개발키 비노출을 함께 확인했다. 실제 APNs·실기기는 범위 밖이다.
- 결과 source 4744035 tracked-clean을 확인하고 테스트 Simulator를 삭제 없이 shutdown했다. 커밋 전: 해당 결과 기록만 포함한다.
- 수정된 Android UTF-8 consumer를 빈 전용 AVD에서 실제 Unity JNI LOCAL_MOCK 흐름으로 실행한다. 이전 AVD 앱을 덮어쓰지 않으며 테스트 시작 기록만 먼저 커밋한다.
- 커밋 전: 시작 기록만 포함한다. 실제 시험은 NOT_RUN이다.
- `run-unity-android-mock-e2e.py --run-local --utf8-probe` exit 0 (`artifacts/unity-android-e2e-jtraqi0j`): 수정 소비자의 JNI 한글/emoji round-trip과 합성 개발키 결과 비노출 및 기존 LOCAL_MOCK 흐름 PASS. 최초 전체화면 안내는 수동으로 닫았다. 실기기·실제 제공자는 미검증이다.
- 사용한 전용 AVD를 shutdown만 하고 데이터를 보존했다. 커밋 전: R09 실제 재시험 결과와 수동 조작 조건만 기록한다.
### P09-T03/R22 Native 실제 합성 세션 토큰 경계 시작
- Native LOCAL_MOCK bridge 통합시험의 임시 memory token store에서 해당 실행의 access/refresh token을 확인해 공개 응답에서 값 자체가 없는지 검증한다. 값은 로그·문서에 쓰지 않으며 외부 계정 토큰이 아니다.
- Android `:sdk-core:compileTestKotlin` PASS. Swift 대상은 컴파일됐으나 opt-in 미설정으로 1건 SKIP이므로 토큰 assertion은 미실행이다. 새 전용 local DB·서버를 사용해 Android/Swift 대상만 실행하며 synthetic token은 출력하지 않는다.
- 새 격리 local DB·Backend에서 Android `LocalMockIntegrationTest.bridge uses real local backend for mock purchase and restore` 1건 및 Swift `LocalMockIntegrationTests.testBridgeHandlerAgainstLocalBackend` 1건 PASS/skip0 (`artifacts/r22-native-9f0p4b_t`). 실행 중 발급한 synthetic access/refresh token 원문과 bridge 결과를 메모리에서 비교했으며 값을 출력하지 않았다. 실제 provider token·전체 로그는 미검증이다.
- 실제 synthetic 세션 토큰 비노출 assertion이 향후 빠지지 않도록 기존 local Android/Swift integration regression filter에 양 bridge 시험을 추가한다. 기존 테스트의 최소 실행 여부도 함께 확인한다.
- 기존 local integration lane은 실행 건수 1건 이상만 확인하므로 세 filter 중 하나가 누락돼도 통과할 수 있다. Android/Swift 각 3건 실행을 요구해 누락을 FAIL로 처리하고 실행 결과를 재확인한다.
- 새 Native bridge token 검사를 포함한 Android/Swift local integration 세 시험 묶음과 전체 집계 재검증을 시작한다. 새로운 DB/role만 사용하며 Unity Player opt-in 및 외부 provider는 실행하지 않는다.
- 진행 중 `artifacts/purchase-regression-n4qmg2ka`에서 Android local integration XML 3건/실패0/error0/skip0, Swift 3건/실패0/skip0을 확인했다. 새 synthetic session token 결과 검사 포함. strict 전체 결과는 아직 없다.
- `artifacts/purchase-regression-n4qmg2ka/result.json`: 구매 하위 항목 모두 PASS/skip0; Android/Swift local integration 각 3건, Xcode local DB 및 process recovery 각 1건. 이는 전체 strict 통과가 아니다.
- 합성 토큰 검사 추가 후 격리 strict exit 1, `artifacts/verify-all-r1ely80_/summary.md`; 구매 하위 전체 PASS, 외부 13 WAITING_USER. 실행 당시 HEAD 150a013 + 미커밋 테스트/하네스/문서, 미추적 파일 보존. 나머지 실패·미실행을 확인한다.
- `verify-all-r1ely80_`에서 구매 하위 및 `push/mock-permission-denied` PASS; `push/unity-player-notifications` DEFERRED_ENV, `unity-editor-runtime` NOT_RUN, scenario coverage PARTIAL 및 기록된 P05-T03 FAIL로 전체 FAIL. 이전 별도 Player PASS를 이 실행의 lane PASS로 대체하지 않는다. 실행 후 전용 Simulator shutdown, 데이터 보존.
- `verify-progress.py`, purchase runner Python compile 및 diff 검사 PASS. 커밋 전: Android/Swift 합성 token assertion, regression 필수 3건, 정제 증거·strict/보고서만 포함한다. 외부 token 및 전체 로그 안전은 주장하지 않는다.
### P09-T01 부분 시나리오 증거 연결 시작
- R22의 local token bridge 시험은 purchase regression에, R40 Mock 거부는 push regression에 추가됐다. manifest의 부분 증거 경로와 후보 suite를 현재 상태에 맞게 연결하되 전체 검증 미완료 상태는 그대로 유지한다.
- `check-manifest.py`, `check-manifest-negative.py`, `verify-progress.py`, `git diff --check` exit 0. 파일 연결 검사이며 제품 통과를 뜻하지 않는다. 커밋 전: PARTIAL 유지한 증거·후보 suite 및 진행 기록만 포함한다.
- Android synthetic token 검사에서 저장소가 비어 있으면 token 비교가 생략되는 결함을 확인했다. sign-in 직후 실제 합성 access/refresh token이 모두 존재하고 비어 있지 않아야 통과하도록 한다.
- token 존재 사전조건 추가 후 Android 테스트 컴파일 exit 0. 새 DB·Backend에서 양 Native bridge의 합성 token assertion을 재현하고 JUnit/XCTest 실제 실행·skip을 검증하는 runner를 추가한다.
- `python3 harness/run-r22-native-redaction.py --run-local` exit 0 (`artifacts/r22-native-vdwala6w`): Android/Swift 각 1건 PASS/skip0 및 token 존재 선행조건 확인. synthetic local DB·Backend만 사용, 원문 token은 출력하지 않았다. opt-in 없는 호출과 문법 검사를 이어간다.
- `run-r22-native-redaction.py` 인자 없이 exit 2, Python compile·원장·diff PASS. 부분 증거와 candidate suite에 재현 명령을 연결한다. 전체 로그·실제 provider 미검증으로 R22 PARTIAL 유지. 커밋 준비.
### P09-T03/R22 synthetic 세션 token 서버 로그 검증 시작
- 전용 격리 Backend 로그에 해당 실행의 synthetic access/refresh token이나 개발키가 들어 있는지 Android/Swift integration에서 메모리로 비교한다. runner는 양쪽 검사 marker가 없으면 PASS를 거부한다. 원문 token이나 로그는 커밋하지 않는다.
- 강화한 `run-r22-native-redaction.py --run-local` exit 0 (`artifacts/r22-native-37ca4aes`): Android/Swift 각 1건/skip0, 해당 synthetic access/refresh token과 개발키가 지정된 격리 Backend 로그에 없고 bridge 결과에도 노출되지 않음을 검사했다. 실 provider credential·모든 앱 로그는 범위 밖. marker 누락 음성 검사를 추가한다.
- marker 부재·빈 값·FAIL·불완전 값·추가 데이터 거부 단위 1건 PASS/skip0, Python·원장 검사 PASS. helper 보완 후 격리 양 플랫폼을 재실행한다.
- `run-r22-native-redaction.py --run-local` 재실행 exit 0 (`artifacts/r22-native-bpyoimew`), 양 플랫폼 각 1건/skip0 및 정확한 server-log 검사 marker 확인. 커밋 전: synthetic 테스트·실행기·음성 검사와 정제 증거만 포함하며 전체 로그 및 실제 provider 결과는 주장하지 않는다.
- `check-required-coverage.py` exit 1: R22/R40 포함 required 시나리오 2개 PARTIAL, 0개 NOT_IMPLEMENTED. 기존 미추적 `unity/Demo`, `harness/__pycache__`, `scripts/__pycache__`는 보존한다. 검사 직전 별도 검증 시작 기록을 빠뜨려 이 결과와 누락을 즉시 기록했다.
- 커밋 전: coverage 검사 결과와 검증 시작 기록 누락의 정정만 포함한다. 제품 상태·원격은 변경하지 않는다.
### P09-T03/R22 합성 구매 증빙 노출 시험 시작
- 기존 Google fake verifier·전용 sandbox DB HTTP 통합시험에서 synthetic 구매 증빙 및 access token이 응답과 수집된 서버 로그에 노출되지 않는지 추가한다. 실제 Google Play 거래는 수행하지 않는다.
- `backend/gradlew -p backend compileTestKotlin` exit 0. 실제 fake verifier·HTTP·DB 시험은 아직 미실행이므로 새 전용 sandbox DB에서 실행한다.
- 전용 sandbox DB에서 `GooglePurchaseHttpIntegrationTest` 1건 PASS/skip0 (`artifacts/r22-proof-0bcej9x1`): synthetic 구매 증빙·거부 증빙·access/refresh token이 성공/실패 HTTP 결과와 캡처된 root logger 메시지·stack에 없는지 확인했다. fake verifier/finalizer이며 실제 Play는 아니다.
- 성공한 증빙 시험의 try/finally 본문 들여쓰기만 정리했다. 기능 변경 여부 확인을 위해 테스트 컴파일을 재실행한다.
- 서식 정리 후 `compileTestKotlin` exit 0, diff 검사 PASS. 기존 격리 HTTP 검증은 의미가 변하지 않은 서식 정리 전 실행이다. 커밋 전: fake proof HTTP/log test 및 정제 증거만 포함한다.
### P11-T01 완료 상태 원장 점검 시작
- ENV-002는 RESOLVED이고 별도 Android/iOS 소비 프로젝트 빌드·Player 증거가 있지만 P08-T04는 여전히 DEFERRED_ENV다. bootstrap 문서 그대로의 재설치 등 완료 기준과 분리해 현재 상태를 정정한다.
- R49 실제 신규 staged consumer 양 플랫폼 Player 증거를 확인했고 ENV-002는 RESOLVED다. P08-T04를 DEFERRED_ENV→PARTIAL로 정정하고 blocker를 제거했다. bootstrap 문서 재현 등 남은 기준은 수행하지 않아 PASS/IMPLEMENTED로 변경하지 않았다.
- `verify-progress.py`, `check-progress-negative.py`, `git diff --check` exit 0. 문서 정합성 검사이며 제품 시험이 아니다. 커밋 전: 행·분모·감사 기록만 포함한다.
### P09-T08 R22 runner 환경 실패 분류 점검
- isolated DB helper의 DEFERRED_ENV 예외를 신규 R22 runner가 무조건 FAIL로 기록하는 경계 결함을 발견했다. 환경 대기와 시험 실패를 구분하되 성공으로 바꾸지 않는다.
- `test_r22_native_redaction.py` 2건 PASS/skip0, Python compile PASS. 실제 포트 점유 대기와 정상 격리 실행을 검증한다.
- 실제 18080 포트 점유 fixture에서 R22 runner exit 2/DEFERRED_ENV, 정상 격리 실행 exit 0 Android·Swift PASS (`artifacts/r22-native-b5e3facc`). 커밋 전: 상태 분류·음성 시험·기록만 포함한다.
### P08-T04 문서 기준 샘플 설치 점검 시작
- 사용자 문서의 Offline Demo import·uGUI·빈 scene 실행 절차를 실제 검증할 조건을 조사한다. `unity status --format json`은 Pipeline 연결 Editor 0건/exit 6이며 Unity 미설치나 라이선스 실패를 뜻하지 않는다. 상태 명령을 시작 원장보다 먼저 실행한 순서 누락을 기록한다. 사용자 프로젝트는 변경하지 않는다.
- Offline Demo 문서의 staged sample, uGUI, EventSystem 및 빈 GameObject 조건을 격리 소비 프로젝트에 구성해 Unity Editor Play에서 실제 UI 컴포넌트 callback·fake 로그인/구매를 확인할 테스트를 작성한다. sample 복사는 패키지 관리자 UI의 Import 버튼 동작을 검증하지 않으며 화면 렌더링도 별도다.
- staged sample 복사·정확한 cached dependency·EventSystem·mock 로그인/상품/구매 UI callback을 검사하는 Editor test와 격리 runner를 작성했다. `bash -n` PASS이나 아직 Unity 실행은 NOT_RUN이다.
- `GAMEBRIDGE_UPM_STAGING=<stage> GAMEBRIDGE_UNITY_PACKAGE_CACHE=<cache> bash scripts/smoke-unity-offline-sample.sh` exit 0, Unity Editor Test Framework 1건 PASS (`artifacts/offline-sample.wpOk2c/results.xml`): 샘플 객체·EventSystem 생성 후 mock 로그인/상품/100코인 구매 UI callback을 실행했다. sample은 Assets로 복사했으며 Package Manager UI import, 화면 렌더링/포인터 및 실제 기기·결제 검증은 아니다.
- 실제 Unity NUnit 보고서에서 1건 Passed/skip0 및 `GB_OFFLINE_SAMPLE_FLOW PASS` marker를 확인했다. 향후 빈 보고서·skip·실패·marker 누락이 허위 성공되지 않도록 결과 판정과 음성 시험을 보강한다.
- `test_unity_offline_sample_result.py` 1건 PASS/skip0, 실제 기존 NUnit 결과 재검사 PASS, shell 구문 PASS. 판정 강화 후 새 Unity Editor 실행을 다시 수행한다.
- 강화된 `smoke-unity-offline-sample.sh` exit 0, 새 격리 Unity Editor test 1건 PASS/skip0 (`artifacts/offline-sample.JGRMHJ/results.xml`). 샘플 callback을 프로그램으로 호출한 fake flow이며 시각 QA·패키지 관리자 UI가 아니다. 샘플 README의 현재 라이선스 실패 문구를 당시 이력과 현재 범위로 정정한다.
### P08-T03 sample 문서 반영 staging 시작
- Offline Demo README 수정으로 기존 UPM staging은 현재 checkout과 달라졌다. 기존 Maven/XCFramework를 사용해 새 staging에만 패키징하고 checksum 및 sample Editor test를 재실행한다. 제품 Native binary 재빌드는 아니다.
- `package-sdk.sh <existing Maven> <existing XCFramework> artifacts/upm-offline-sample-20261112` exit 0, XCFramework arch/C ABI 및 staging 110개 checksum PASS. Native binary 재빌드는 아니며 새 staging Editor test는 별도다.
- 새 `artifacts/upm-offline-sample-20261112`를 사용한 `smoke-unity-offline-sample.sh` exit 0, Unity Editor 1건 PASS/skip0 (`artifacts/offline-sample.0FsGva/results.xml`). fake UI callback flow이며 Package Manager UI import·화면 렌더링·실결제는 아니다.
- `verify_staged_source_matches_checkout` 및 sample 결과 음성 1건/skip0, workflow YAML parse, diff 검사 PASS. staging source는 현재 미커밋 sample README 수정 포함, 기존 Native binary 재사용. 화면 렌더링·Package Manager UI는 아직 미검증이다.
- `docs/evidence/p08-offline-sample-editor.md`에 staged hash·실제 Unity Editor fake flow 및 미검증 범위를 기록했다. 커밋 전: sample README 정정, 격리 시험/runner, 음성 검사와 정제 문서만 포함한다. 생성 staging·Unity cache는 Git 제외, P08-T04 PARTIAL 유지.
- 새 sample staging과 직전 `upm-v2-20261112-f1e12b6`의 Native payload hash 비교 결과 81개 파일 중 41개 불일치. 앞선 staging은 오래된 `maven-final`/`ios-final`을 사용했으므로 최신 Native로 간주할 수 없다. 기존 f1e12b6 staging에 포함된 검증된 Maven·XCFramework를 복사해 새 경로로 재패키징하고 비교 및 Editor test를 다시 한다. 앞선 후보·결과는 보존한다.
- 기존 f1e12b6 UPM의 Maven/XCFramework에서 `artifacts/upm-offline-sample-current-20261112`를 새로 생성하고 XCFramework 검증 및 110개 checksum PASS. Native payload byte 동일성과 Editor 실행을 별도로 확인한다.
- 새 staging의 Native payload 81개 파일은 f1e12b6 staging과 hash 일치, SDK source도 현재 checkout과 일치. 새 staging으로 Unity Offline Demo Editor 시험을 다시 수행한다.
- `upm-offline-sample-current-20261112`로 격리 Unity Editor sample 시험 exit 0, 1건 PASS/skip0 (`artifacts/offline-sample.Tg04iK/results.xml`). 직전 f1e12b6 Native payload 81개와 byte 동일한 staging이며 Package Manager UI/실제 렌더링은 미검증이다. 구 staging 후보와 구분해 evidence를 수정한다.
- `verify-progress.py`, `check-manifest.py`, `git diff --check` exit 0. 커밋 전: 올바른 staging hash·81개 Native byte 일치·새 Editor 결과와 이전 후보 차이만 기록한다. staging 바이너리/캐시는 커밋하지 않는다.
- sample runner는 현재 staging 자체 checksum만 확인해 소스가 오래된 패키지도 실행할 수 있다. 기존 Android E2E와 같은 checkout 소스 일치 확인을 선행해 stale stage를 거부한다. Native artifact provenance는 별도로 기록한다.
- `smoke-unity-offline-sample.sh`에 기존 `upm-v2-20261112-f1e12b6`를 제공한 음성 시험 exit 1, checksum 정상·source 불일치 거부. 의도된 검출이며 제품 실패가 아니다. 현재 stage로 양성 실행한다.
- `upm-offline-sample-current-20261112`로 source 일치 검사 후 Unity Editor sample test exit 0, 1건 PASS/skip0 (`artifacts/offline-sample.k1uWmY/results.xml`). 커밋 전: stale stage 거부·재실행 증거만 포함한다. 실제 시각 QA는 아니다.
### P08-T04 Native Demo Editor guard 검증 시작
- staged Native Demo를 Editor의 별도 객체로 실행해 실제 Native 호출 대신 안내가 표시되고 동작 버튼이 비활성인지 확인한다. 이는 Native Player의 로그인/결제/실제 UI 검증이 아니다.
- 양 sample Editor test와 두 marker 누락 거부 단위 1건 PASS, Python/shell 구문 PASS. Native Demo Editor guard 실제 실행은 아직 NOT_RUN이다.
- staged 양 sample을 격리 프로젝트에서 실행한 `smoke-unity-offline-sample.sh` exit 0, Unity test 1건 PASS/skip0 (`artifacts/offline-sample.TwukI1/results.xml`). Offline fake flow와 Native Demo Editor에서 안내·Native 버튼 비활성을 확인했다. Native Player와 실제 화면/포인터는 시험하지 않았다.
- sample 음성 단위 1건·실제 XML 판정·원장 PASS. `git diff --check`는 checker 15행 후행 공백으로 exit 2; 공백을 제거한 뒤 재검증한다.
- 공백 수정 후 sample 결과 음성 1건, 실제 Editor XML, 원장 및 diff 검사 PASS. 커밋 전: Native Demo Editor guard test 및 정확한 한계만 기록한다. Native Player 실행으로 간주하지 않는다.
### P08-T04 Native Demo Android Player 검증 시작
- 문서의 staged Native Demo와 uGUI를 새 소비 프로젝트에 복사하고 runtime 설정을 입력해 초기화·로그인·상품·모의 구매·로그아웃 버튼 callback을 실제 Android Unity Player에서 실행할 전용 probe를 추가한다. 포인터·화면 QA와 실 Play 거래는 별도다.
- staged Native Demo에 runtime 설정을 입력하고 실제 UI callback으로 mock 로그인·상품·구매·로그아웃 및 합성키 결과 검사를 실행하는 Android probe를 추가했다. runner는 별도 marker·정확한 uGUI 2.5.0을 요구한다. 아직 Unity/Player 미실행이다.
- `UNITY_ANDROID` 조건부 Native Demo probe managed compile exit 0, 경고·오류 0. 실제 Player는 NOT_RUN. marker 수집·서로 다른 probe 동시 설정 거부를 확인한다.
- `test_unity_redaction_marker.py` 4건 PASS/skip0 및 두 전문 probe 동시 선택의 argparse exit 2 확인. 커밋 전: test-only sample probe·격리 runner와 기록만 포함한다. 실제 Player·시각 QA는 미실행이다.
- staged Native Demo sample의 Android LOCAL_MOCK Player를 실제로 빌드·실행한다. 새 빈 AVD는 기존 시험 앱 덮어쓰기를 막기 위해 필요하며 사용자 데이터는 보존한다. 최초 전체화면 안내 수동 처리 가능성을 별도 기록한다.
- 커밋 전: 실행 시작 기록만 포함, 실제 결과는 NOT_RUN이다.
- `run-unity-android-mock-e2e.py --run-local --native-demo-probe` exit 0 (`artifacts/unity-android-e2e-j7ir0wt8`): staged Native Demo의 runtime 설정·초기화·로그인·상품·100코인 mock 구매·로그아웃 callback 및 DB 원장 1건/100 확인, 입력 개발키 삭제·결과 비노출 검사 포함. 전용 AVD 최초 전체화면 안내는 수동으로 닫았다. 실제 터치/시각 QA, Play 결제·실기기는 아니다.
- Native Demo test AVD shutdown, 데이터 보존. 커밋 전: `docs/evidence/p08-native-demo-android.md`와 기능 문서에 Android LOCAL_MOCK 범위·수동 안내·미검증 항목만 반영한다. iOS Native Demo Player와 실제 UI는 미실행이다.
### P08-T04 Native Demo iOS Player 검증 시작
- Android에서 검증한 동일 staged Native Demo의 iOS Simulator probe를 추가한다. 런타임 입력·mock 구매 callback 및 main-thread, key 삭제, DB 원장 검사만 수행하며 실 Apple 계정·APNs·실기기 검증은 아니다.
- iOS Native Demo test-only consumer와 격리 runner option을 추가했다. Python compile 및 host/native 전문 probe 동시 선택 exit 2 확인. Unity managed compile과 Simulator Player는 별도다.
- Native Demo iOS `UNITY_IOS` 조건부 probe managed compile exit 0, 경고·오류 0. Unity Simulator Player는 아직 미실행이다. 커밋 전: test-only probe·runner와 기록만 포함한다.
- 수정 staged Native Demo iOS LOCAL_MOCK Player를 새 Simulator에서 실행한다. test-only UI callback과 synthetic local DB만 사용하며 clean-source 실행을 위해 시작 기록을 먼저 커밋한다.
- 커밋 전: 시작 기록만 포함, 실제 결과는 NOT_RUN이다.
- `run-unity-ios-mock-e2e.py --native-demo-probe` 첫 실행 exit 1, UNITY_EXPORT_FAILED (`artifacts/unity-ios-e2e-kd8mlvys`); Simulator Player는 NOT_RUN. 격리 Unity 로그의 빌드 원인을 확인한다.
- 격리 Unity Editor 로그의 실제 컴파일 오류는 `NativeDemoIosPush.cs(11,13) CS0246 GameBridgeClient`다. `GameBridge.NativeDemo.iOS.asmdef`가 해당 타입을 가진 `GameBridge.Runtime`을 직접 참조하지 않는다. .NET managed compile의 transitive project reference가 놓친 실제 UPM sample assembly 결함으로 수정 및 재패키징한다.
- iOS sample asmdef에 `GameBridge.Runtime` 직접 참조를 추가하고 Unity 비전이적 참조 계약 단위 검사를 CI inventory에 추가했다. 실제 Unity export는 아직 재실행 전이다.
- `test_unity_sample_assemblies.py` 1건 PASS/skip0, YAML·diff 검사 PASS. 수정 asmdef를 반영한 새 staging을 직전 Native payload로 생성하고 실제 Unity iOS export를 재검증한다.
- `package-sdk.sh`로 기존 f1e12b6 Native payload를 사용해 `upm-native-sample-fix-20261112` 생성, XCFramework/110개 checksum PASS. 수정 소스 tracked-clean에서 iOS Player를 재실행하기 위해 코드 및 회귀 검사를 먼저 커밋한다. 실제 Player는 NOT_RUN이다.
- iOS Native Demo의 수정 asmdef를 새 stage에 반영해 실제 Unity export·Simulator Player·LOCAL_MOCK flow를 재실행한다. 첫 CS0246 실패는 기록 그대로 보존한다.
- 커밋 전: 재검증 시작 기록만 포함한다.
- asmdef 수정 후 `run-unity-ios-mock-e2e.py --native-demo-probe --adhoc` exit 0 (`artifacts/unity-ios-e2e-56e5wx05`): staged Native Demo iOS Simulator LOCAL_MOCK 설정·인증·상품·100코인 mock 구매·로그아웃 callback, main-thread·키 삭제, DB 원장 1건/100 PASS. 첫 CS0246 실패는 보존한다. 실제 포인터·렌더링, Apple 거래·APNs·실기기는 아니다.
- source aa9c155 tracked-clean과 새 stage Native payload 81개 byte 동일성을 확인했고 전용 Simulator를 shutdown했다. asmdef 수정 stage로 Offline/Native Editor sample도 다시 실행해 최신 evidence를 갱신한다.
- `upm-native-sample-fix-20261112`로 격리 Editor sample test 1건 PASS/skip0 (`artifacts/offline-sample.GHbI58/results.xml`): Offline fake flow와 Native Editor guard. iOS Native Player PASS 및 첫 asmdef FAIL을 별도 증거에 기록한다.
- `verify-progress.py`, `check-manifest.py`, diff 검사 exit 0. 커밋 전: iOS 수정 후 실제 Player·Editor sample·staging provenance와 첫 실패만 정제 기록한다. raw log·키·빌드 산출물은 제외한다.
### P09-T07 sample Editor gate 연결 시작
- 재현 가능한 staged sample Editor 시험을 self-hosted Unity gate에 포함한다. 이 시험은 정확한 cache 패키지가 필요하므로 runner preflight에서 경로를 확인하며 미실행을 PASS로 바꾸지 않는다. GitHub Actions 실행은 별도다.
- `bash -n scripts/ci-unity-e2e.sh`, `test_ci_gate.py` 4건 PASS. cache 미존재를 build 이전에 환경 대기로 분류하는 시험을 추가한다.
- cache 경로 부재 등 `test_ci_gate.py` 5건 PASS/skip0, shell·원장·diff PASS. self-hosted 전체 및 GitHub Actions는 실행하지 않았다. 커밋 전: gate 연결·음성 검사·설정 문서만 포함.
### P11-T03 최신 stage·strict 기준 정합성 시작
- iOS sample asmdef 수정 이후 최신 staged UPM과 package cache를 체크포인트에 명시한다. strict 기존 결과가 새 asmdef 수정 이전 source와 당시 미커밋 test에서 실행됐다는 사실을 최종 보고서에 명시한다.
- 현재 stage/cache 및 이전 strict source·dirty 범위를 명시하고 `verify-progress.py`, `git diff --check` PASS. 커밋 전: 재개 경로·보고서 정합성 기록만 포함한다.
### P09-T07 self-hosted strict fixture 준비 점검
- 현재 Unity CI gate는 strict 집계를 직접 호출하지만 DB/test server opt-in을 준비하지 않아 기본 provisioning에서 필수 lane이 DEFERRED_ENV다. 기존 격리 DB/server orchestration 재사용 가능성을 검토한다.
- 기존 `run-strict-local-isolated.py`는 전용 local/sandbox DB·서버·synthetic iOS fixture를 만들고 opt-in Unity 환경을 상속한다. self-hosted gate의 direct strict 호출을 이 orchestration으로 교체해 미준비 환경이 PASS되는 것을 막고, 기존 90분 strict timeout과 사전 Player 실행을 수용할 job timeout을 120분으로 설정한다.
- `test_ci_gate.py` 5건·strict timeout 단위 1건 PASS/skip0, shell/YAML 구문 PASS. 외부 도구를 모사한 격리 fixture로 gate가 isolated orchestration을 호출하고 실패를 숨기지 않는지 추가 검증한다.
- 새 CI fixture 첫 호출에서 mock unity 문자열의 Python 따옴표 오류(SyntaxError), test import FAIL. 실제 self-hosted CI는 실행되지 않았다. fixture 문자열을 수정해 재시험한다.
- fixture 문자열 수정 후 `test_ci_gate.py` 6건 PASS/skip0: mock 도구 환경에서 isolated strict 호출 및 실패 전파를 확인했다. 실제 self-hosted/GitHub Actions는 NOT_RUN이다. 커밋 전: CI fixture 준비·timeout·음성 시험·문서만 포함한다.
### P09-T07 선택 환경 경로 일치 점검
- isolated strict helper가 CI에서 지정한 UNITY_EDITOR_PATH를 하드코딩된 버전으로 덮고, Maven/XCFramework가 별도 오래된 기본 경로를 사용할 수 있다. 선택 Editor와 현재 staged Native 산출물을 일관되게 쓰도록 보강한다.
- `run-strict-local-isolated.py`의 하드코딩 Editor와 과거 Maven/XCFramework 기본값을 확인했다. 지정 Editor/Newtonsoft를 존중하고 기본 artifact는 제공된 stage에서 가져오며 CI gate는 stage 경로를 명시한다.
- 선택 Editor 경로·timeout 단위 2건, CI gate 단위 6건 PASS/skip0, Python/shell syntax PASS. CI stub에 staging Native 경로 전달 assertion을 추가한다.
- CI mock fixture가 현재 staging의 Maven/XCFramework 경로를 strict로 전달함을 확인했고 gate 6건·Editor/timeout 단위 2건 PASS/skip0, 원장/diff PASS. 실제 self-hosted 전체는 NOT_RUN이다. 커밋 전: 경로 수정·단위 검증·문서만 포함한다.
### P09-T07 전체 Unity CI gate 로컬 검증 시작
- `scripts/ci-unity-e2e.sh`를 실제 licensed Unity와 현재 staging, 별도 baseline/push AVD 2개 및 격리 DB로 실행한다. 각각의 최초 전체화면 안내는 수동 처리가 필요할 수 있다. 누락·기존 실패를 그대로 보존하고 GitHub Actions나 실제 provider 검증으로 간주하지 않는다.
- 커밋 전: 실행 시작 기록만 포함한다. 전체 gate 실제 결과는 NOT_RUN이다.
- 실제 `scripts/ci-unity-e2e.sh` 첫 호출은 Editor consumer 2건과 sample Editor 1건 PASS 뒤 Android baseline `TARGET_NOT_AN_ONLINE_EMULATOR`/exit 2 (`artifacts/unity-android-e2e-ds3m3hkh`). Android Player 이후 및 strict는 NOT_RUN이다. Unity의 ADB 재시작·두 AVD online 복구를 조사한다.
- 최초 `find_dedicated_device` 호출은 ADB 재시작 순간 offline을 즉시 환경 대기로 반환한다. 기존 `wait_for_dedicated_device`는 동일 serial/전용 AVD/기존 앱 보존 검사를 유지하며 offline만 재시도하므로 baseline 및 push의 최초 조회에도 적용한다.
- `test_unity_device_rediscovery.py` 3건 PASS/skip0, 양 runner Python compile·원장/diff PASS. offline은 제한 시간 내 재시도하며 다른 AVD와 설치된 앱은 즉시 거부한다. 실제 수정 gate 재실행은 NOT_RUN. 커밋 전: runner·음성 검증·기록만 포함한다.
- 두 전용 AVD에 테스트 패키지가 설치되지 않은 것을 확인했다. 기존 기기 데이터 삭제 없이 동일 AVD를 재사용해 수정된 Unity 전체 gate를 재실행한다. 시작 기록을 먼저 커밋한다.
- 커밋 전: 재실행 시작 기록만 포함, 전체 결과는 NOT_RUN이다.
- `scripts/ci-unity-e2e.sh` 실제 로컬 재실행 exit 1, strict `artifacts/verify-all-4r3l36i6/summary.md`, orchestration `artifacts/strict-isolated-8vglqxoq`. Editor 소비자·sample, Android/iOS 기본 Player 후 strict가 완료됐으나 전체 FAIL. 두 AVD 최초 전체화면 안내는 수동으로 닫았으며 GitHub Actions/실제 provider 검증은 아니다. 세부 lane을 확인한다.
- strict `verify-all-4r3l36i6`: Unity Editor 2건·Push 양 Player 2건 PASS, 구매 포함 실행 suite PASS, scenario PARTIAL과 recorded P05-T03 FAIL로 전체 FAIL. 4개 Player source e703f43 tracked-clean; strict의 sourceDirty는 보존된 미추적 파일 포함. 두 Android 최초 안내 수동 처리. 사용한 AVD 2개·Simulator 3개는 shutdown만 했고 데이터는 보존했다.
- 실제 gate에서 Editor가 opt-in됐는데 isolated helper 고정 출력은 Editor가 분리된 것처럼 나타났다. 집계 결과와 무관한 안내 문구를 실제 opt-in 상태로 바꾸고 기존 실행 증거는 유지한다.
- helper 안내 수정 후 Python compile, timeout 단위 2건/skip0, 원장·diff PASS. 전체 gate 결과는 수정 전 e703f43 실행이므로 현재 HEAD의 재실행으로 주장하지 않는다. 커밋 전: 로컬 CI evidence·문서·안내 문구만 포함한다.
- 최신 gate의 Android/iOS 기본 및 Push 각 server.log 4개에서 `mock:<UUID>` 합성 token/증빙 패턴 검색 결과 모두 없음. 원문 로그·일치값은 출력하지 않았다. 다른 형식·Player 전체 로그를 검사한 것은 아니다. 검증 시작 기록을 먼저 남기지 않은 순서 누락을 즉시 기록했다.
- `LocalMockClient`의 합성 push token·구매 proof는 `mock:<UUID>` 형태임을 확인했다. R22 전용 runner가 서버 로그 전체에서 이 패턴을 검사하고 실패시키도록 추가하며, 알려지지 않은 형식/실제 provider에 대한 보장으로 확대하지 않는다.
- `test_r22_native_redaction.py` 3건 PASS/skip0 및 Python compile PASS. pattern 검사 추가 후 격리 Android/Swift integration을 새로 실행한다.
- 강화한 R22 격리 runner exit 0 (`artifacts/r22-native-7r45s8ui`): Android/Swift bridge 각 1건과 서버 로그 synthetic session key/push token·purchase proof 형태 검사 PASS. 이는 로컬 mock 형식에 한정하며 실제 provider·모든 로그 포맷 보장이 아니다.
- 결과 JSON의 양 test PASS 및 mockCredentialServerLog PASS, 원장/diff 검사 확인. 커밋 전: pattern 탐지·음성 test·정제 증거만 포함하며 raw 로그와 synthetic token 값은 제외한다.
### P09-T03/R22 Unity 로그 synthetic credential 검사 시작
- 기존 gate는 개발키 등 알려진 일부 값만 Unity/server 로그에서 검사한다. LOCAL_MOCK push token·구매 proof 형식 `mock:<UUID>`을 공통 검사해 누출 시 marker 저장·PASS를 막는다. 실제 credential이나 다른 형식은 별도다.
- Android/iOS 기본·Push runner에 test-only mock credential 패턴 검사 추가, Python compile 및 marker 4건 PASS/skip0. Android 원시 logcat 유출이 marker 필터 전에 거부되는지 음성 fixture를 추가한다.
- `test_unity_redaction_marker.py` 5건, `test_unity_push_current.py` 1건 PASS/skip0, 원장/diff PASS. R22 전용 runner의 동일 패턴을 공통 helper로 통일해 검사 기준의 차이를 방지한다.
- 공통 helper 연결 후 R22 단위 3건/skip0과 격리 Native runner exit 0 (`artifacts/r22-native-7__7z_m1`). Unity 기본·Push runner의 변경 후 실제 Player는 아직 NOT_RUN이다. 커밋 전: synthetic 패턴 검사·음성 test·기록만 포함한다.
- synthetic mock token/proof 원시 로그 검사 추가 후 실제 iOS LOCAL_MOCK Player 기본 경로를 새로 실행한다. 실 provider·다른 포맷을 검사하는 것이 아니다. clean-source 실행 시작 기록만 먼저 커밋한다.
- 커밋 전: 시작 기록만 포함하며 실제 재검증은 NOT_RUN이다.
- 강화 로그 검사 적용 `run-unity-ios-mock-e2e.py --run-local --adhoc` exit 0 (`artifacts/unity-ios-e2e-o2mypwsg`): synthetic mock token/proof 형태와 알려진 개발키가 iOS Unity 원시 console 및 local Backend log에서 발견되지 않았고 기본 LOCAL_MOCK flow PASS. 실제 provider·다른 포맷은 미검증이다.
- iOS Simulator를 삭제 없이 shutdown했다. 커밋 전: iOS 부분 검증과 사용된 source만 포함한다. 다른 세 runner의 변경 후 실제 실행은 NOT_RUN이다.
- synthetic mock credential 로그 검사 추가 후 Android 기본 LOCAL_MOCK Player를 새로 실행한다. 기존 AVD 앱 데이터를 덮어쓰지 않는다. clean-source 시작 기록만 커밋하며 결과는 아직 NOT_RUN이다.
- 강화 로그 검사 적용 `run-unity-android-mock-e2e.py --run-local` exit 0 (`artifacts/unity-android-e2e-j9tb9ven`): 알려진 개발키 및 synthetic mock token/proof 형태가 Unity 원시 logcat과 Backend log에서 검출되지 않고 기본 LOCAL_MOCK flow PASS. 최초 안내는 수동 처리. 실제 provider·다른 포맷은 미검증.
- 테스트 AVD는 삭제 없이 shutdown했다. 커밋 전: Android 부분 결과·수동 안내 조건만 포함하고 Push runner 재실행은 미완료로 남긴다.
- mock token/proof raw 로그 검사 추가 후 양 플랫폼 Push LOCAL_MOCK Player를 같은 실행에서 새로 검증한다. 앱이 설치된 기존 AVD를 보존하기 위해 빈 전용 AVD를 사용한다. 시작 기록만 커밋하고 결과는 아직 NOT_RUN이다.
- 강화 로그 검사 적용 `run-unity-push-current.py` exit 0, Android/iOS LOCAL_MOCK Player 각 PASS (`artifacts/unity-android-push-918elqj3`, `artifacts/unity-ios-push-anrcrvlm`), 동일 source tracked-clean 및 필수 marker 확인. raw Unity/server 로그에서 알려진 키·synthetic mock token/proof 형태 비노출. Android 최초 안내 수동 처리; 실제 FCM/APNs·다른 형식은 미검증.
- Push 시험 Simulator/AVD는 삭제 없이 shutdown했다. 커밋 전: 강화 로그 검사 양 플랫폼 검증 요약만 포함하고 raw 로그·빌드·키는 제외한다. R22 전체·실제 provider는 미완료다.
### P08-T04 Package Manager sample import 검증 시작
- 기존 sample Editor runner는 staged sample을 직접 복사했다. 새 격리 프로젝트에서 Unity Package Manager의 Sample API로 Offline/Native sample metadata를 찾아 import한 다음 같은 Play-mode 테스트를 실행하도록 개선한다. Package Manager GUI 클릭 및 시각 QA는 별도다.
- Package Manager Sample.FindByPackage/Import로 두 sample을 가져오는 Editor setup을 작성하고, import 완료 marker 뒤에만 Play-mode test를 컴파일하도록 runner를 조정했다. shell 구문만 PASS, 실제 import는 아직 미실행이다.
- 강화 `smoke-unity-offline-sample.sh` exit 0 (`artifacts/offline-sample.wdb0LN`): Unity Package Manager Sample API가 staged UPM의 Offline/Native sample을 각각 import한 marker와, 이후 Editor Play fake 로그인/구매·Native Editor guard 1건 PASS/skip0를 확인했다. Package Manager GUI 클릭·시각 렌더링·실제 포인터는 검증하지 않았다.
- 첫 import API 시험은 runner가 import 직후 marker를 확인했지만 다음 Unity test가 같은 Editor.log를 덮어써 사후 재확인 가능한 marker 파일이 없다. 안전한 두 marker만 별도 보존하고 재실행한다. 첫 결과는 제품 실패가 아니다.
- 보완 runner 재실행 exit 0 (`artifacts/offline-sample.FAkiaR`): 별도 `import-markers.log`에 두 Sample API import PASS marker 보존, Editor test 1건 PASS/skip0. GUI import 클릭·실제 시각/포인터 QA와 실제 provider는 별도다.
- sample result 음성 1건 PASS, 원장·shell·diff PASS. import marker 중복이나 한쪽 누락을 허용하지 않도록 marker 각각 정확히 1건을 요구한다.
- 강화 runner `artifacts/offline-sample.Afsqij`: sample import marker 각각 정확히 1건, Editor Play test 1건 PASS/skip0. 커밋 전: Unity Sample API setup·runner·정제 증거만 포함하며 Package Manager GUI·시각 QA로 기록하지 않는다.
### P08-T04 Native Demo Sample API → Player 연결 시작
- 기존 Android/iOS Native Demo Player는 sample 파일을 직접 복사했고 Sample API import는 별도 Editor 시험이었다. 동일 격리 소비 프로젝트에서 실제 Sample API import 후 Native Player를 빌드·실행하는 경로로 연결한다. GUI 클릭·시각 QA 및 실제 provider는 별도다.
- 양 Native Player runner가 sample을 직접 복사하지 않고 Unity Sample API import marker를 요구하도록 변경했다. Python/shell 구문 및 marker 단위 5건 PASS. importer는 실제 Player 실행 전이며 격리 artifacts 경로 보호를 추가한다.
- Sample import helper의 artifacts 외부 consumer 거부 fixture 및 shell syntax PASS. 기존 사용자 프로젝트를 대상으로 하지 않으며 실제 양 플랫폼 Player 재실행은 아직 없다. 커밋 전: helper·runner 연결·기록만 포함한다.
- 동일 신규 프로젝트의 Sample API import 이후 Native Demo iOS LOCAL_MOCK Player를 실행한다. 현재 source 기록을 먼저 커밋하며 결과는 미실행이다.
- `run-unity-ios-mock-e2e.py --native-demo-probe` exit 0 (`artifacts/unity-ios-e2e-7ryle35b`): 같은 신규 프로젝트에서 Unity Sample API로 Offline/Native import 후 Native Demo iOS Simulator Player mock 설정·인증·구매·로그아웃 및 원장 1건/100 PASS. Package Manager GUI 클릭·포인터·실제 Apple 거래는 아니다.
- iOS Simulator는 삭제 없이 shutdown했다. 커밋 전: iOS import→Player 결과만 기록하고 Android 동일 경로는 NOT_RUN으로 유지한다.
- 동일 신규 프로젝트의 Sample API import 이후 Native Demo Android LOCAL_MOCK Player를 실행한다. 기존 AVD 앱 데이터를 보존하기 위해 빈 전용 AVD를 사용한다. 시작 기록만 커밋하며 결과는 미실행이다.
- `run-unity-android-mock-e2e.py --native-demo-probe` exit 0 (`artifacts/unity-android-e2e-8hjon046`): 같은 신규 프로젝트의 Unity Sample API import 후 Native Demo Android LOCAL_MOCK 설정·로그인·mock 구매·로그아웃 및 원장 1건/100 PASS. 최초 전체화면 안내 수동 처리. Package Manager GUI 클릭·포인터·실제 Play 거래는 아니다.
- Android test AVD는 삭제 없이 shutdown했다. 양 플랫폼 각 신규 프로젝트의 Sample API import→Native Demo LOCAL_MOCK Player 증거를 관련 문서에 반영하며 source가 서로 다름을 보존한다. GUI 클릭·실제 provider는 미검증이다.
- Android 64cb90b/iOS 083100f 사이 Unity SDK·Android SDK·iOS 제품 source diff exit 0, 두 Player의 staging SHA-256은 동일 `6f966d4b…`. 계획의 `docs/evidence/consumer-install.md`에 import·설정·Player·실제 플랫폼 한계를 정리한다.
- P08-T04 계획의 신규 staged consumer·Sample API import·Editor mock flow 및 Android/iOS export/build/LOCAL_MOCK Player 실행을 `docs/evidence/consumer-install.md`에 연결했다. 해당 Task만 IMPLEMENTED/로컬 PASS로 갱신한다. GUI 포인터·시각, 실제 계정·스토어·실기기는 별도 미검증이다.
- P08-T04 갱신 후 `verify-progress.py`, `check-progress-negative.py`, diff 검사 PASS. 커밋 전: 해당 Task의 정제된 설치 증거·상태와 기능 보고서만 포함한다. 다른 P08 Task나 실제 제공자를 완료로 바꾸지 않는다.
### P08-T03 Unity metadata 안정성 누락
- `unity/Packages/com.gamebridge.sdk` 원본에 `.meta`가 0개이고 Unity 소비 프로젝트에서만 생성됨을 확인했다. P08-T03의 `.meta` 안정성 기준을 충족하지 않아 package 원본에 안전하고 고정된 GUID를 마련하고 두 신규 프로젝트 import 결과를 비교한다. 기존 프로젝트와 원본 산출물은 수정하지 않는다.
- 격리 `offline-sample.Afsqij`의 Unity 생성 package metadata와 Sample API로 생성된 sample metadata를 원본 파일/폴더에 대조한 결과 37개 모두 대응, 누락 0. `Samples~` 자체는 Unity가 무시하는 컨테이너라 제외한다. Unity가 생성한 metadata를 원본에 고정하며 GUID 중복·누락을 검사한다.
- 격리 Unity가 만든 asset/folder metadata 37개를 대응 원본에 복사, GUID 유일성 37개 확인. 외부 경로·사용자 데이터를 수정하지 않았다. 누락/중복/orphan 검사와 두 신규 Unity import 비교는 별도다.
- `check-unity-meta.py` PASS, `test_unity_meta.py` 2건 PASS/skip0(누락·중복·orphan·폴더 표식 거부). 이는 정적 검사이며 Unity import 간 GUID 안정성은 미실행이다.
- 기존 검증 Native payload를 사용한 `upm-stable-meta-20261113` 생성, XCFramework와 147개 checksum PASS. 서로 다른 새 Unity consumer 두 곳의 package/sample GUID를 비교하기 위해 첫 import를 실행한다.
- metadata stage 첫 `smoke-unity-offline-sample.sh` exit 0 (`artifacts/offline-sample.S2hxOa`): Sample API import 및 Editor 1건 PASS/skip0. GUID 안정성 판단 전 두 번째 새 프로젝트를 실행한다.
- metadata stage 두 번째 신규 consumer도 Sample API import와 Editor fake flow 1건 PASS/skip0 (`artifacts/offline-sample.McH39f`). 이어서 두 프로젝트의 각 asset GUID를 원본과 비교한다.
- 원본과 두 신규 프로젝트 74개 GUID 비교 exit 1: mismatch 4개는 각 프로젝트의 `Samples~/Offline Demo`, `Samples~/Native Demo` import 대상 최상위 폴더다. Sample API가 target 폴더를 생성하면서 package 경로의 폴더 metadata를 복사하지 않는다. 내부 asset과 target 폴더를 구분해 추가 검증하며 전체 GUID 안정성을 PASS로 주장하지 않는다.
- 최상위 sample 폴더를 제외한 package/sample 내부 asset GUID 70회 비교 불일치 0. Sample API 생성 최상위 두 폴더는 각 프로젝트에서 서로 다른 GUID를 만들어 4회 불일치하며 전체 안정성은 미완료다. stage 147개 checksum 및 Native payload 81개 byte 동일성 확인. 정제 증거를 저장한다.
- `test_unity_meta.py` 2건/skip0, workflow YAML·원장·diff PASS. 커밋 전: Unity 생성 metadata·누락/중복 검사·정제 증거만 포함한다. Sample 최상위 폴더 GUID와 최신 Player 재시험은 미완료다.
- metadata 추가가 실제 iOS sample import/export/Player를 깨지 않는지 새 stage에서 재실행한다. Sample 최상위 폴더 GUID 불일치는 이 시험과 별도 미완료다. clean-source 시작 기록만 커밋한다.
- metadata stage iOS `--native-demo-probe` exit 0 (`artifacts/unity-ios-e2e-q9ua_s4_`): Sample API import 후 Native Demo Simulator LOCAL_MOCK Player·원장 1건/100 PASS, tracked-clean. Android와 sample 최상위 폴더 GUID는 별도다.
- iOS test Simulator shutdown, 데이터 보존. 커밋 전: iOS 부분 결과만 포함하며 Android 재실행은 NOT_RUN으로 남긴다.
- metadata 추가가 Android sample import/export/Player를 깨지 않는지 새 stage에서 재실행한다. 기존 AVD 앱 데이터를 보존하기 위해 빈 전용 기기를 사용하며 시작 기록만 커밋한다.
- metadata stage Android `--native-demo-probe` exit 0 (`artifacts/unity-android-e2e-2trvul1k`): Sample API import 후 Native Demo Player·원장 1건/100 PASS, tracked-clean. 최초 전체화면 안내는 수동으로 닫았다. Sample 최상위 폴더 GUID 불일치는 별도다.
- Android test AVD는 삭제 없이 shutdown했다. metadata stage Android/iOS Native Demo Player 재실행 PASS를 증거에 추가하고 최신 stage 경로를 갱신한다. Sample import 최상위 폴더 GUID 불일치는 여전히 별도 미완료다.
- 원장·manifest·diff 검사 PASS. 커밋 전: metadata stage 최신 경로 및 양 Player 정제 증거만 포함한다. Sample 최상위 폴더 GUID·실제 provider를 완료로 기록하지 않는다.
### P08-T03 실제 Unity iOS hook 반복 실행 시작
- 기존 PBX 독립 smoke 외에 실제 staged UPM과 Unity iOS export에서 postprocess hook을 다시 두 번 호출해 PBX 및 복사된 XCFramework의 byte hash가 유지되는지 확인한다. 외부 Apple 서명/계정은 사용하지 않는다.
- `IosHookIdempotence.cs`는 실제 BuildPipeline export 뒤 실제 UPM postprocess를 두 번 재호출하고 PBX/XCFramework 전체 hash를 비교한다. 아직 Unity compile/export는 미실행이다.
- metadata stage 격리 iOS consumer에서 Unity BuildPipeline export 후 UPM postprocess hook 두 번 재호출 exit 0, `GB_IOS_HOOK_REPEAT PASS` (`artifacts/unity-ios-mock.mWBnyZ/project/Logs/Editor.log`). PBX 및 XCFramework 파일 hash가 초기/1회/2회 동일했다. 실제 서명·Player 검증은 아니다. 재현 가능한 runner로 정리한다.
- `smoke-unity-ios-hook-repeat.sh` exit 0 (`artifacts/unity-ios-mock.yLBxjk`), 실제 Unity export + iOS hook 재호출 2회 후 PBX/XCFramework byte 동일. 이 runner가 오래된 staging을 현재 소스처럼 검증하지 않도록 source 일치 검사와 CLI preflight를 추가한다.
- 이전 `upm-native-sample-fix-20261112` 투입 음성 시험 exit 1: checksum 정상·metadata source 불일치 거부. 제품 실패가 아닌 의도된 검출이다. 현재 metadata stage로 양성 실행한다.
- `smoke-unity-ios-hook-repeat.sh`는 stale stage 음성 거부 후 현재 stage 실제 Unity export·hook 반복 2회 PASS (`artifacts/unity-ios-mock.ztGwKd`). 서명/Player 시험과 구분한다. Android 실제 Gradle export에서도 hook 반복을 확인한다.
- `AndroidHookIdempotence.cs`와 격리 runner는 실제 Unity Gradle export 후 hook을 2회 재호출하고 settings/build.gradle 및 복사된 Maven 파일 hash를 비교한다. 실제 실행은 아직 NOT_RUN이다.
- `smoke-unity-android-hook-repeat.sh` exit 0 (`artifacts/unity-android-mock.mri8OM`): staged UPM의 실제 Unity Android Gradle export 후 hook 2회 재호출 시 settings/build.gradle 및 Maven payload hash가 초기/1회/2회 동일했다. APK/Player는 별도 결과다.
- 두 실제 Unity export hook 반복 검증을 self-hosted CI gate에 연결하고 README의 과거 Unity 미검증·source/staging 구분 누락을 정정한다. 전체 gate 재실행 전이며 실제 provider는 별도다.
- Android/iOS 실제 export hook 반복 hash 증거 `docs/evidence/p08-export-hooks.md` 작성. CI gate 음성 6건/skip0, shell·원장·diff PASS. 새 gate 전체 및 GitHub Actions는 NOT_RUN이며 커밋 전: hook 테스트/runner·CI·패키징 문서만 포함한다.
### P09-T08 CI 필수 sample/hook 호출 검증 시작
- self-hosted gate에 새로 연결한 sample 및 Android/iOS export hook이 실제 순서에서 호출되는지 mock command fixture에 assertion을 추가한다. Unity 실제 hook 시험은 별도 증거다.
- `test_ci_gate.py` 6건 PASS/skip0: mock gate에서 Editor·sample·양 hook·isolated strict 호출과 실패 전파 확인. 원장/diff PASS; 실제 새 전체 gate 및 GitHub Actions는 NOT_RUN. 커밋 전: fixture·기록만 포함한다.
### P09-T03/R22 합성 개인정보 redaction 시험 시작
- R22는 token뿐 아니라 개인정보 형태 입력도 포함한다. 합성 email/전화번호를 Backend 오류·trace 및 Android/Swift diagnostics 요청/예외에 주입해 응답과 캡처 로그에서 비노출을 확인한다. 실제 개인정보는 사용하지 않는다.
- 합성 email/전화번호가 Backend 예외 응답·trace 및 Android/Swift diagnostics 공개 결과에 나오지 않아야 하는 assertion을 작성했다. 테스트 실행 전이다.
- Backend `HttpInfrastructureTest`/`LocalMockTraceFilterTest` 각 2건, Android `BridgeDispatcherTest` 3건, Swift `CBridgeTests` 4건 PASS/skip0: synthetic email/전화번호가 시험한 오류·trace/diagnostics 응답에 나오지 않음. 실제 개인정보와 Unity raw log의 개인정보 주입은 미검증이다.
- 합성 개인정보가 실제 request/exception에 주입되고 응답·로그 검사에 포함됨을 소스에서 재확인했다. 커밋 전: 테스트와 정제 증거만 포함하며 전체 R22/실 provider를 완료로 기록하지 않는다.
### P09-T03/R22 Unity synthetic 개인정보 callback 검증 시작
- test-only 합성 Native callback의 허용되지 않은 필드에 synthetic email/전화번호를 넣고 Unity 공개 Push 결과에서 제거되는지 확인한다. 양 Player 원시 로그에서도 해당 synthetic 값이 나오면 실패시킨다. 실제 개인정보·원격 push가 아니다.
- `PiiProbe`는 test-only Native callback 경로에 합성 email/전화번호를 추가하고 Unity 공개 PushUpdate에서 제거되는지 확인한다. Android/iOS Player consumer와 raw 로그 감시 연결·컴파일은 아직 남았다.
- `--pii-probe`는 양 플랫폼에서 test-only callback·link 보존·필수 marker를 적용하고 합성 email/전화번호가 원시 Unity 로그에 나오면 실패한다. Python compile PASS, Player 실행 전 managed compile을 확인한다.
- Android/iOS PII probe 조건부 managed compile 각각 경고·오류 0, `test_unity_redaction_marker.py` 6건 PASS/skip0. 실제 Player callback/log는 미실행이다. 커밋 전: test-only probe·runner·음성 시험만 포함한다.
- test-only synthetic 개인정보 Native callback이 Unity 공개 결과에서 제거되고 raw log에 남지 않는지 iOS Simulator Player에서 검증한다. 시작 기록만 먼저 커밋하며 실제 provider는 사용하지 않는다.
- `run-unity-ios-mock-e2e.py --pii-probe --adhoc` exit 0 (`artifacts/unity-ios-e2e-ehxq_12y`): synthetic Native callback의 허용되지 않은 email/전화번호가 공개 PushUpdate에 없고 raw Unity console에도 나타나지 않음. LOCAL_MOCK 기본 흐름도 PASS, 실제 개인정보/원격 APNs 아님.
- iOS PII test Simulator는 삭제 없이 shutdown했다. 커밋 전: iOS 부분 결과만 포함하며 Android PII Player는 미실행이다.
- test-only synthetic 개인정보 Native callback의 Unity 결과·원시 logcat 비노출을 Android Player에서 실행한다. 기존 AVD 앱 데이터 보존을 위해 빈 전용 AVD 사용, 시작 기록만 먼저 커밋한다.
- `run-unity-android-mock-e2e.py --pii-probe` exit 0 (`artifacts/unity-android-e2e-rtm39zwn`): synthetic Native callback의 허용되지 않은 email/전화번호가 공개 PushUpdate와 raw Unity logcat에 없음. 기본 LOCAL_MOCK flow PASS, 최초 전체화면 안내 수동 처리. 실제 개인정보/원격 push 아님.
- Android PII test AVD shutdown, 데이터 보존. Android source a42a8b2 및 iOS source 6d82338은 각각 tracked-clean. 두 test-only synthetic PII 결과를 정제 증거에 기록하며 자동 strict lane·실 provider·다른 개인정보 형식은 미완료다.
- 양 Player synthetic PII 정제 evidence 및 원장/diff 검사 PASS. 커밋 전: 결과·수동 안내 조건만 포함하고 raw log·개인정보는 저장하지 않는다. R22 PARTIAL 유지.
### P09-T07 Unity CI 기본 Player PII probe 연결 시작
- 기존 baseline Android/iOS Player는 동일 인증·구매 흐름을 유지하는 `--pii-probe`로 실행해 synthetic 개인정보 결과/로그 검사를 포함한다. 별도 AVD는 추가하지 않는다. standalone strict의 독립 PII lane과 GitHub Actions 실제 실행은 아직 없다.
- mock CI gate의 양 플랫폼 `--pii-probe` 전달 포함 `test_ci_gate.py` 6건 PASS/skip0, shell·원장·diff PASS. 변경된 실제 전체 gate 및 standalone strict의 독립 PII lane은 미완료다. 커밋 전: 설정·fixture·문서만 포함한다.
### P09-T06/R22 동일 실행 PII Player 증거 집계 시작
- 기존 Unity CI baseline의 `--pii-probe` 양 플랫폼 결과를 실행별 nonce와 현재 HEAD, tracked-clean, Player/marker/원장 검증으로 묶는다. standalone strict는 해당 실행 증거가 없으면 DEFERRED_ENV여야 한다. 이전 결과 재사용이나 필수 검증 생략을 허용하지 않는다.
- PII wrapper는 두 Player를 새로 실행하고 현재 HEAD·실행 nonce·tracked-clean·PII marker·DB 원장을 검증한다. 검사기 Python compile만 완료했고 음성 fixture와 실제 wrapper 실행은 아직 미실행이다.
- `test_unity_pii_current.py` 1건 PASS/skip0: 서로 다른 nonce·HEAD·dirty·미실행·marker 누락·잘못된 원장·플랫폼 누락을 거부했다. 아직 실제 두 Player wrapper는 NOT_RUN이며 CI/strict에 fail-closed로 연결한다.
- CI gate가 양 PII Player wrapper를 호출하고 fresh evidence/nonce를 strict 필수 lane에 전달하도록 구현했다. mock CI 6건, evidence 음성 1건 PASS; 실제 wrapper/전체 gate는 NOT_RUN이다. evidence/nonce 전달을 fixture에서 확인한다.
- `test_ci_gate.py` 6건, `test_unity_pii_current.py` 1건, `test_aggregation.py` 13건 PASS/skip0. standalone strict는 동일 실행 PII evidence/nonce 미제공 시 DEFERRED_ENV다. 커밋 전: wrapper·검사기·CI/strict 연결·음성 시험만 포함하며 실제 wrapper/원격 CI는 NOT_RUN이다.
- 실제 `run-unity-pii-current.py`로 양 synthetic PII LOCAL_MOCK Player를 순차 실행하고 HEAD·nonce·원장·marker 검증을 확인한다. 기존 AVD 앱은 보존하고 빈 전용 기기를 사용한다. clean-source 시작 기록만 먼저 커밋한다.
- `run-unity-pii-current.py --run-local ...` exit 0 (`artifacts/unity-pii-current-ml8muq1n`): source 222a2f3의 Android/iOS PII LOCAL_MOCK Player 각 PASS, tracked-clean·실행 nonce·필수 marker 및 각 원장 1건/100. Android 최초 전체화면 안내 수동 처리. 실제 개인정보/원격 provider는 아니다.
- `check-unity-pii-evidence.py`에 해당 실행 evidence/nonce를 전달해 양 Player 2건 PASS 확인. AVD·Simulator는 shutdown만 했다. 같은 논리 실행 evidence를 격리 strict로 전달해 lane 집계를 검증한다. Unity Push/Editor opt-in은 별도이며 전체 PASS는 주장하지 않는다.
- 동일 실행 PII evidence/nonce를 전달한 격리 strict exit 1 (`artifacts/verify-all-p09mpzq9`, orchestration `artifacts/strict-isolated-beow_iyv`), 외부 13 WAITING_USER. PII lane 및 다른 실패·미실행을 확인하며 전체 PASS로 기록하지 않는다.
- `verify-all-p09mpzq9`: `unity-pii-e2e` 2건 PASS, 구매 하위 PASS, Unity Push DEFERRED_ENV·Editor NOT_RUN·scenario PARTIAL·기록된 P05-T03 FAIL로 전체 FAIL이다. test Simulator는 shutdown만 했다.
### P09-T01/R22 재현 suite 연결 시작
- R22의 synthetic credential/PII 범위는 Native·Backend·양 Unity Player에서 실행했고 strict PII lane도 확인했다. 시나리오 entry에서 실제 두 Player wrapper를 명시적 opt-in으로 재현할 수 있게 하며, 미설정은 DEFERRED_ENV로 남긴다.
- `test_unity_pii_optin.py` 2건 PASS/skip0: 미설정은 exit 2, 명시 설정에서 새 nonce 생성·실제 runner 결과 전달. 새 scenario timeout 경계의 음성 검사 및 R22 assertion/evidence 매핑을 확인한다. opt-in 얇은 entry의 실제 호출은 별도다.
- R22 요구(합성 인증키·token·개인정보의 SDK 로그/Unity 결과/Backend 오류 비노출)에 대한 실행된 Backend·Native·양 Unity Player 및 strict PII lane을 `docs/evidence/r22-synthetic-redaction.md`에 assertion별로 연결해 local/fake IMPLEMENTED로 갱신한다. 외부 실 provider·모든 가능한 입력을 검증했다는 뜻이 아니며 opt-in 얇은 entry는 실제 호출 전이다.
- `check-manifest.py`, `check-manifest-negative.py` PASS. `check-required-coverage.py` exit 1: 1 PARTIAL(R40), 0 NOT_IMPLEMENTED. 이는 전체 통과가 아니다.
- opt-in child timeout 3200초, scenario 상위 3300초로 분리해 child의 DEFERRED_ENV 처리가 상위 강제 종료보다 먼저 일어나게 한다. 환경별 단위 및 manifest를 재검증한다.
- PII opt-in 2건, evidence 1건, manifest/음성/Python/diff PASS. evidence fixture의 플랫폼 누락 검사가 이전 marker 누락 상태와 겹쳐 독립 확인이 아니므로 marker 복원 후 검증하도록 보정한다.
- 플랫폼 누락 fixture를 독립화 후 evidence 1건·opt-in 2건 PASS/skip0, 원장/diff PASS. 커밋 전: R22의 실행된 synthetic 범위와 suite/timeout·음성 검사만 포함하며 opt-in entry 실제 호출·실 provider는 미실행으로 명시한다.
### P09-T05/R40 기존 OS 증거 소스 대조 시작
- 기존 Android/iOS OS 권한 시험 source와 현재 플랫폼/Unity Runtime diff를 조사한다. 첫 stat에서 Unity Runtime 변경은 새 .meta로 보인다. 제품 소스 동일성과 test-only Firebase 의존성 범위를 확인한다. 확인 시작 전에 diff를 먼저 실행한 순서 누락도 기록한다.
- Android `1fa6c0d` 및 iOS `e0acbd6`와 현재 platform/Unity Runtime 비교에서 `.meta` 외 제품 코드 차이 0. 두 기존 실제 권한 시험의 격리 프로젝트 consumer 파일과 현재 test 소스도 byte 동일하다. Android test-only Firebase dependency, 실제 OS dialog, iOS OS 및 독립 mock을 구분한다.
### P09-T05/R40 Android 실제 OS 권한 재현 runner 시작
- 기존 test-only permission consumer와 Firebase runtime dependency를 새 격리 Unity Android 프로젝트에서 빌드한다. 전용 AVD의 실제 권한 dialog를 식별해 거부하고 첫 DENIED·등록 차단·재요청 DENIED marker를 검증한다. 계정·실 Firebase 연결은 없다.
- Android permission runner는 새 Unity Player 및 전용 AVD에서 OS dialog를 resource id로 식별해 거부하고 허용된 marker만 저장한다. 초안 Python compile만 확인했으며 실제 실행 전이다. dialog 오탭 방지·미실행/중단 분류를 시험한다.
- Android permission runner 단위 2건 PASS/skip0: 유일한 permission deny resource만 선택, 중복·다른 위젯·잘못된 XML 및 필수 marker 누락 거부. 실제 OS 재실행은 아직 없다. 커밋 전: runner·음성 시험·기록만 포함한다.
- Android OS permission 재현 runner를 새 전용 AVD에서 실행한다. test-only Firebase SDK dependency를 사용하나 계정·서비스 설정·원격 발송은 없다. clean-source 시작 기록을 먼저 커밋한다.
- Android 36 실제 권한 창에서 거부 버튼 resource id가 `permission_deny_and_dont_ask_again_button`임을 관찰했다. runner는 `permission_deny_button`만 허용해 탭하지 않았으며, 오탭 방지를 위해 실행을 중단해 INTERRUPTED/exit 130 (`artifacts/unity-android-permission-ikutzs0w`). OS 거부 결과는 미판정. 명시된 두 거부 ID만 허용하도록 보강한다.
- Android OS runner selector가 명시적 두 거부 ID만 허용하도록 보완했고 단위 2건 PASS/skip0, Python·원장·diff PASS. 수정 실제 OS 재실행은 아직 없다. 커밋 전: selector·fixture·중단 이력만 포함한다.
- 실제 관찰된 denial resource ID 지원 후 Android OS runner를 새 전용 AVD에서 재실행한다. 이전 AVD는 shutdown만 했고 시작 기록을 먼저 커밋한다.
- 수정 `run-unity-android-permission-os.py --run-local` exit 0 (`artifacts/unity-android-permission-j_5q_9e9`): test-only Firebase SDK dependency와 Android 36 전용 AVD에서 실제 OS 거부 버튼을 자동 선택, 첫 DENIED·등록 PERMISSION_DENIED·재요청 DENIED marker PASS. 원격 Firebase 계정/전송은 없다. 초기 첫 실행 INTERRUPTED 기록은 보존한다.
- Android permission test AVD는 삭제 없이 shutdown했다. 커밋 전: 자동 OS 시험 결과와 수동 미선택/초기 중단 이력만 포함한다. iOS 전용 재현 runner는 아직 없다.
### P09-T05/R40 iOS 실제 OS 권한 재현 runner 시작
- 격리 Unity iOS Simulator Player의 실제 알림 권한 dialog를 요청하고, 거부 후 첫 DENIED·등록 차단·재요청 DENIED를 검증하는 runner를 만든다. GUI 거부 입력이 없으면 환경 대기로 처리하며 원격 APNs/Apple 계정은 사용하지 않는다.
- iOS permission runner 초안 compile PASS. Simulator 생성 호출의 환경 대기 category 인자와 필수 marker/명시적 opt-in을 확인하며 아직 실제 export/OS 시험은 미실행이다.
- `test_unity_ios_permission_os.py` 2건 PASS/skip0, Python·원장·diff PASS. iOS GUI denial 없이는 성공하지 않는다. 실제 runner 실행 전 커밋: test-only runner·음성 검사·기록만 포함한다.
- iOS OS permission runner를 새 Simulator에서 실행한다. 실제 알림 dialog에서 거부를 선택하며 Apple 계정·APNs는 사용하지 않는다. clean-source 시작 기록만 먼저 커밋한다.
- `run-unity-ios-permission-os.py --run-local` exit 0 (`artifacts/unity-ios-permission-d3b5a0lc`): iOS 18.6 Simulator 실제 권한 dialog에서 도구로 허용 안 함을 선택, 첫 DENIED·등록 PERMISSION_DENIED·재요청 DENIED marker PASS. GUI denial 입력은 자동화 runner 외부의 도구 조작이며 Apple 계정/APNs는 없다. 초기 snapshot은 종료된 이전 Simulator 기본값을 가리켜 실패했고 올바른 Simulator를 지정한 뒤 진행했다.
- Android runner가 실제 denial button을 선택한 횟수와 외부/기존 상태를 구분하고, iOS runner는 외부 GUI 입력 필요를 result에 명시한다. 기존 실제 OS 성공 증거는 별도로 보존한다.
- Android denial tap 횟수/interaction mode 및 iOS 외부 GUI 입력 표시를 보강했고 Android 단위 3건, iOS 2건 PASS/skip0. 양 OS 및 managed Mock을 각각 새 실행하는 opt-in R40 entry를 추가한다. iOS GUI 입력이 없으면 성공하지 않는다.
- `test_r40_permission_optin.py` 2건 PASS/skip0: opt-in 없으면 실행하지 않고 DEFERRED, Android/iOS/Mock 중 어느 하나가 대기/실패면 전체 성공하지 않는다. 세 경로 합친 실제 wrapper 및 새 interaction 기록은 아직 미실행이다. 커밋 전: test-only runner·fixture·기록만 포함한다.
- `run-r40-permission-optin.py`에서 Android 실제 OS, iOS 실제 OS, managed Mock 세 경로를 순차 실행한다. iOS OS 거부는 외부 GUI 도구 조작이며 무인 CI로 간주하지 않는다. 시작 기록을 먼저 커밋한다.
- `GAMEBRIDGE_RUN_OS_PERMISSION_E2E=true ... python3 harness/run-r40-permission-optin.py` exit 0: Android 실제 OS denial 자동 처리 (`artifacts/unity-android-permission-ube13ah7`), iOS 실제 OS denial GUI 도구 처리 (`artifacts/unity-ios-permission-hk912uou`), standalone managed Mock denial 각각 PASS. 양 OS source ef9405b tracked-clean; 실제 FCM/APNs·실기기 검증은 아니다. 첫 결과 정리 명령은 작업 디렉터리 오타로 프로세스 미시작, 올바른 경로로 재실행했다.
- R40 실제 통합 결과: Android `AUTOMATED_RESOURCE_ID` denial tap 2회, iOS `EXTERNAL_GUI_REQUIRED`이며 도구로 거부, managed Mock 별도 PASS. 양 test 기기는 shutdown했고 데이터 보존. 실행된 세 범위를 manifest assertion 및 opt-in 재현 경로에 매핑한다.
- R40의 실제 Android 자동 OS, iOS GUI 보조 OS, managed Mock 결과를 `r40-os-and-mock.md`에 연결했다. `check-manifest`, 음성 검사 PASS 및 required coverage 50개 기록 완료. 이는 현재 CI에서 모든 시나리오가 실행됐다는 뜻이 아니며 iOS GUI·실제 provider는 별도다.
- R40 실제 Android OS·iOS OS·Mock 및 opt-in 재현 wrapper를 연결해 50/50 local/fake coverage evidence를 기록했다. iOS GUI 수동 및 실제 provider 미검증을 명시하고 최종 manifest/runner 음성 검사를 실행한다.
- R40 opt-in 2건, Android OS selector 3건, iOS OS marker 2건, CI gate 6건 단위 PASS/skip0. manifest·음성·coverage·원장 PASS. 커밋 전: 실제 OS/Mock별 evidence와 local/fake coverage만 갱신하며 GUI 보조·실 provider/전체 strict 미완료를 명시한다.
### P09-T07 최신 전체 Unity CI gate 재검증 시작
- 50개 local/fake coverage, 최신 metadata stage, Sample API·양 hook·동일 실행 PII/Push lane을 포함한 현재 gate를 전용 baseline/push AVD와 격리 DB/Simulator에서 실제 재실행한다. R40 iOS OS는 앞선 GUI 보조 증거이며 이 gate가 자동 재실행하는 것은 아니다. P05-T03 및 외부 provider 상태는 그대로 유지한다. 시작 기록만 먼저 커밋한다.
- 최신 `scripts/ci-unity-e2e.sh` 실제 로컬 실행 exit 1, strict `artifacts/verify-all-n3u_5w60/summary.md`, orchestration `artifacts/strict-isolated-hqnpssju`, 외부 13 WAITING_USER. GUI 안내 수동 처리했으며 GitHub Actions·실 provider 실행은 아니다. 세부 lane 및 실패를 확인한다.
- `verify-all-n3u_5w60`: source 562c75f, 실행 lane 및 coverage 50, Unity PII 2, Push 2, Editor 2 PASS. 유일 비PASS는 기존 P05-T03 FAIL이므로 전체 FAIL/exit1, 외부 13 WAITING_USER. 4 Player는 동일 source tracked-clean; strict sourceDirty는 기존 미추적 Demo/cache 포함 기준. 두 Android 최초 안내 수동 처리. 시험 AVD 2개·Simulator 3개 shutdown, 데이터 보존. R40 iOS 실제 OS는 선행 GUI 보조 증거이며 이 CI에서 자동 재실행하지 않았다.
- 최신 로컬 gate의 실제 lane·source, Android 안내 수동 및 R40 iOS GUI 보조, P05-T03 FAIL·외부 대기를 evidence/CI/최종 보고에 반영했다. 원장·manifest·diff PASS. 커밋 전: 정제 문서만 포함하며 원본 로그/DB/빌드는 제외한다.
### P05-T03 iOS 26.5 StoreKit 실패 조사 시작
- 기존 26.5 SKTestSession 생성 timeout 및 Code 3 기록을 보존한 채 Apple 공개 문서·설치 runtime을 확인한다. 외부 보고의 유사성을 현재 환경 원인으로 단정하지 않는다. 문서 조회를 시작 기록보다 먼저 실행한 순서 누락을 기록한다.
- Apple [SKTestSession 문서](https://developer.apple.com/documentation/storekittest/sktestsession)는 named/URL 초기화 경로를 제공한다. [iOS 26.5 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-26_5-release-notes)는 선택된 설정 관련 수정을 기록하고 [Apple Developer Forums](https://developer.apple.com/forums/thread/826971)에는 유사 Code 3 보고와 DTS 답변이 있다. 현재 우리 앱의 init timeout과 동일 원인인지는 미확정이다. 설치된 runtime은 18.6/26.5, Xcode 26.6이며 test-only URL initializer 대조를 추가한다.
- RecoveryHarness는 기본 named 동작을 유지하며 opt-in URL initializer를 선택한다. runner Python compile PASS. 잘못된 선택을 DB 생성 전에 차단하도록 조정하고 음성 시험한다.
- `GAMEBRIDGE_PROCESS_STOREKIT_INIT=invalid ... --run-local` exit 2를 DB 생성 전 확인, Python/diff PASS. 먼저 iOS 18.6에서 URL initializer의 빌드·local process recovery 양성 대조를 실행한다. 실제 Apple sandbox는 아니다.
- `GAMEBRIDGE_PROCESS_STOREKIT_INIT=url ... --run-local` iOS 18.6 exit 0 (`artifacts/xcode-process-recovery-xbadp2tm`): URL initializer, synthetic local DB 구매 응답 유실 및 프로세스 재시작 복구 PASS. 당시 미커밋 test-only 변경이며 26.5/실 Apple sandbox 결과는 아니다.
- 동일 URL initializer를 별도 iOS 26.5 Simulator·local DB에서 실행한다. 이전 named init timeout/Code 3은 결과와 관계없이 이력으로 보존하고 성공 시에도 동일 원인인지 추정하지 않는다.
- `GAMEBRIDGE_PROCESS_STOREKIT_INIT=url GAMEBRIDGE_PROCESS_SIM_RUNTIME=...iOS-26-5 ... --run-local` exit 1 (`artifacts/xcode-process-recovery-97a0wg1_`): prepare 단계 `storekit-session` timeout. 같은 URL initializer의 iOS 18.6 대조는 PASS (`artifacts/xcode-process-recovery-xbadp2tm`). 두 테스트는 당시 미커밋 test-only diagnostic이며 이전 named timeout/Code 3과 같은 원인이라고 단정하지 않는다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN 유지.

### 사용자 요청 안정 중단 — 2026-11-13
- 진행 중이던 iOS 26.5 URL initializer 대조 종료 후 중단한다. 18.6 URL local recovery PASS (`artifacts/xcode-process-recovery-xbadp2tm`), 26.5 URL init 단계 timeout FAIL (`artifacts/xcode-process-recovery-97a0wg1_`); named 경로와 같은 원인 여부 미확정이다. `P05-T03` FAIL/`ENV-STOREKIT-26` OPEN을 유지한다.
- R09/R11/R22/R40/R43/R49 포함 50개 local/fake 시나리오 evidence 기록. `verify-all-n3u_5w60`는 해당 실행 suite와 coverage PASS이지만 기존 P05-T03 FAIL로 전체 FAIL, 외부 13 WAITING_USER. R40 iOS GUI 및 두 Android 초기 안내는 수동 처리, 원격 GitHub Actions/실 provider 미실행이다.
- 새 staging `artifacts/upm-stable-meta-20261113`; Sample 최상위 폴더 GUID 차이는 P08-T03 PARTIAL. 테스트 Simulator/AVD를 shutdown했으며 DB/기기 데이터, 기존 미추적 Demo/cache를 보존한다.
- 재개: P05-T03 named/URL과 26.5 runtime 원인을 계속 조사하고 필요 시 최신 source의 격리 strict 및 문서 감사를 재실행한다. 제품 Provider와 test-only 진단을 구분하고 실패·미실행을 PASS로 바꾸지 않는다. 자동 push/공개 배포는 하지 않는다.
- 커밋 전: test-only URL initializer 옵션, 18.6 대조/26.5 실패 및 이 중단 기록만 포함한다. 실제 Apple sandbox는 미검증이다.

### P05-T03 재개 — StoreKit session 단계 분리
- `AGENTS.md`, `START_HERE.md`, 기존 진단·Git 상태를 확인했다. 26.5의 기존 `storekit-session` checkpoint는 initializer와 disableDialogs setter를 모두 포함하므로 어느 호출이 멈췄는지 아직 확정할 수 없다. test-only 단계 분리와 background 실행 대조를 추가한다. 메인 스레드 의존성은 가설이며 Apple 공식 확정 원인으로 간주하지 않는다. 기존 사용자 Demo/cache는 보존한다.
- `GameBridgeRecoveryHarnessApp.swift`에서 session 생성과 설정 checkpoint를 분리하고 명시적 background 생성 옵션을 추가했다. `run-xcode-process-recovery.py`는 실행 경로를 검증·기록한다. Python compile/diff PASS이며 Swift 빌드·실행은 아직 없다.
- `GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR=invalid ... --run-local` exit 2를 DB 생성 전에 확인했다. iOS 18.6 background initializer로 local process recovery 양성 대조를 실행한다.
- `GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR=background GAMEBRIDGE_PROCESS_STOREKIT_INIT=url ... --run-local` iOS 18.6 exit 0 (`artifacts/xcode-process-recovery-dhe_8lqh`): staged test-only 코드가 실제 build 및 local purchase/process recovery PASS. 26.5 및 실제 Apple sandbox는 별도다.
- 양성 대조를 마친 동일 test-only background URL 경로를 별도 iOS 26.5 Simulator·DB에서 실행한다. 세분화된 checkpoint로 생성/설정 중 어느 단계가 멈추는지 구분한다.
- iOS 26.5에서 `GAMEBRIDGE_PROCESS_STOREKIT_EXECUTOR=background ...INIT=url` exit 1 (`artifacts/xcode-process-recovery-na8yq85t`): `storekit-session-create` timeout으로 설정 setter 이전에 멈춤을 확인했다. 동일 변경 iOS 18.6은 PASS (`artifacts/xcode-process-recovery-dhe_8lqh`). background 이동으로 해결되지 않았으나 Apple 내부 원인은 미확정, P05-T03 FAIL 유지.
- 26.5의 named/URL 및 background URL 대조가 실패해 같은 환경 재시도는 중단한다. `P05-T03` FAIL과 `ENV-STOREKIT-26` OPEN 유지. Xcode build에는 StoreKitTest SDK deprecated 경고가 있었고 이 진단 코드의 concurrency 오류는 관찰되지 않았다. 코드 변경의 기본 18.6 named 회귀만 확인한다.
- 변경된 test-only harness 기본 main/named iOS 18.6 실행 exit 0 (`artifacts/xcode-process-recovery-7v4ybj7y`): local StoreKit process recovery PASS. 26.5 실패와 실제 Apple sandbox는 별도다.
- 세 테스트 Simulator를 shutdown하고 데이터는 보존했다. 커밋 전: test-only executor/세분화 checkpoint, 18.6 두 PASS·26.5 FAIL 및 SDK 경고/미확정 원인만 기록한다. 제품 StoreKit provider와 실제 sandbox는 변경/검증하지 않았다.
### P08-T03 Sample 재가져오기 GUID 대조 시작
- 두 프로젝트의 Sample API 생성 최상위 폴더 GUID가 다르다는 기존 결과는 같은 프로젝트에서 재가져오기 시 GUID가 바뀐다는 증거가 아니다. Unity가 제공하는 OverridePreviousImports를 새 격리 consumer에만 적용해 import 전후 최상위·내부 GUID 보존을 각각 확인한다. 사용자 sample은 덮어쓰지 않는다. [Unity Sample API](https://docs.unity3d.com/ScriptReference/PackageManager.UI.Sample.html)
- 새로운 `offline-sample.KSrzqt`에서 Sample import와 Editor test 1건 PASS/skip0. 해당 작업 전용 프로젝트에서만 RepeatImport test-only Editor 코드를 실행해 재가져오기 GUID를 비교한다.
- `unity run ... GameBridgeSampleRepeatImport.Run` exit 0 (`artifacts/offline-sample.KSrzqt/project/Logs/Editor.log`): 두 sample 모두 동일 프로젝트 내 override 재import에서 ROOT=STABLE, INTERNAL=STABLE. 서로 다른 신규 프로젝트의 최상위 대상 폴더 GUID 차이는 그대로이며 내부 asset GUID 비교와 구분한다. 누락·변경 marker를 성공 처리하지 않도록 runner에 fail-closed 검사를 추가한다.
- 동일 프로젝트 재import의 두 sample ROOT/INTERNAL marker 각각 1건, CLI 성공을 요구하는 checker와 누락·중복·변경/exit 오류 음성 시험 1건 PASS. 신규 consumer 전체 실행은 아직 재확인 전이다.
- `smoke-unity-offline-sample.sh` 강화 후 exit 0 (`artifacts/offline-sample.PbKuS1`): Sample API import, Editor fake/guard 1건 PASS, 두 sample 동일 프로젝트 override 재import의 root/internal GUID 안정성 PASS. 별도 두 프로젝트의 생성 대상 root GUID가 다른 이전 결과는 유지한다.
- `docs/evidence/p08-upm-staging.md`에 checksum·실제 양 export hook 2회·package asset GUID/동일 프로젝트 재import·Android/iOS staged consumer 및 README 구분을 연결했다. 계획된 로컬 패키징 범위의 P08-T03만 IMPLEMENTED/PASS로 갱신한다. 프로젝트마다 새 sample 대상 root GUID는 다르며 실제 provider·GUI 시각 검증은 아니다.
- P08-T03 갱신 후 `verify-progress.py`, `check-progress-negative.py`, `check-unity-meta.py`, `check-manifest.py`, diff 검사 PASS. 커밋 전: sample 재import fail-closed 테스트·정제 evidence·해당 Task 상태만 포함하며 기존 사용자 파일은 제외한다.

### P08-T01/T02 Native 패키지 소비 검증 재개
- 가장 앞선 독립 가능 미완료 작업의 현재 source를 사용해 새 Android Maven publication/좌표 기반 R8 consumer 및 iOS source consumer/무서명 XCFramework slice·symbol·독립 link를 확인한다. 기존 산출물은 덮어쓰지 않고 실제 스토어·서명된 기기 검증과 구분한다.
- `swift build --package-path ios` exit 0 (`artifacts/p08-swift-source-build.log`), source package 자체 빌드 PASS. 독립 source consumer/link 및 XCFramework는 별도로 확인한다. Android/iOS archive 병렬 실행 중이다.
- `ios/consumer-source-check`와 격리 runner를 추가해 SwiftPM 제품 의존성으로 별도 source consumer를 빌드/실행한다. host 검사이며 iOS binary·실기기가 아니다. 아직 실행 전이다.
- `GAMEBRIDGE_MAVEN_REPO=<new> bash scripts/build-android.sh --mock` exit 0 (`artifacts/p08-android-reverify.log`): publication·sample APK 및 독립 coordinate R8 release build 완료. `GAMEBRIDGE_IOS_OUTPUT_DIR=<new> bash scripts/build-ios.sh --xcframework` exit 0 (`artifacts/p08-ios-reverify.log`): unsigned device/simulator archive 및 XCFramework 생성. `bash scripts/smoke-ios-source-consumer.sh` exit 0 (`artifacts/ios-source-consumer.UIxcpt`): 별도 SwiftPM Core/Apple source consumer를 macOS host에서 실행했다. 실기기/실 store 검증은 아니며 POM·manifest·slice/symbol 및 별도 iOS binary consumer link를 확인한다.
- `verify-xcframework.py artifacts/ios-p08-reverify-20261113/GameBridgeNative.xcframework` exit 0: device arm64·simulator arm64/x86_64 및 arch별 C ABI 4개 검증. Android 독립 consumer Gradle은 source project dependency 없이 Maven 좌표·R8 minification이며 POM의 sdk-core 및 runtime 의존성을 확인했다. unsigned APK 기기 실행 및 iOS link는 별도다.
- `xcrun swiftc ... ios/consumer-check/main.swift` exit 0 및 `vtool -show-build` IOSSIMULATOR 확인(실행 아님). Android release APK merged manifest에 BILLING/INTERNET 및 consumer activity 확인. Android Gradle에는 SDK XML 버전 경고가 있었다. publication은 sdk-android/bridge AAR, 순수 JVM sdk-core JAR과 각각 POM/module로 구성된다. 기존 build 디렉터리의 영향을 배제하는 신규 소비 프로젝트를 별도로 검증한다.
- `GAMEBRIDGE_MAVEN_REPO=<fresh> bash scripts/smoke-android-maven-consumer.sh` exit 0 (`artifacts/android-maven-consumer.cNk7BG`): 기존 build/.gradle을 제외한 신규 소비 프로젝트에서 Maven 좌표만으로 R8 unsigned release APK·mapping을 생성하고 merged manifest의 BILLING/INTERNET/activity를 확인했다. APK 설치/기기 실행은 아니다.
- 새 Android Maven의 POM/module scope 확인: `sdk-core` 순수 JVM JAR, `sdk-android`/`sdk-unity-bridge` AAR. R8 unsigned 소비 APK의 BILLING/INTERNET/activity가 병합됐다. 새 iOS XCFramework arch/C ABI, 독립 arm64 simulator Swift link 및 IOSSIMULATOR load command, 독립 SwiftPM host consumer를 확인했다. f1e12b6 이후 Android/iOS Native 제품 source diff 0. 실제 기기/스토어는 별도다.
- P08-T01/T02의 계획된 로컬 산출물·독립 소비 빌드 기준을 실제 확인하고 각각 `docs/evidence/p08-android-maven-consumer.md`, `docs/evidence/p08-ios-xcframework-consumer.md`에 연결해 IMPLEMENTED/로컬 PASS로 갱신했다. sdk-core는 JAR이며 unsigned APK·archive 실기기 실행, 실제 제공자 검증을 주장하지 않는다.
- P08-T01/T02 상태 갱신 후 원장·음성·shell·metadata·diff 검사 PASS. clean Maven consumer runner의 repository 미설정 환경 대기 조건도 확인한다.
- Maven repository 미설정 fixture exit 2/DEFERRED_ENV, CI YAML 및 diff PASS. 커밋 전: 두 독립 소비 runner/source, 정제된 증거, CI source-consumer 연결 및 P08-T01/T02 로컬 상태만 포함한다. APK·XCFramework·원본 로그는 제외한다.

### P08-T05 현재 기능 기준점 감사 시작
- P08-T01~04 로컬 검증 이후 현재 P00~P08 모든 Task ID·상태와 기존 API/protocol snapshot의 호환성을 대조하고 새로운 부분 기준점을 별도 기록한다. 과거 snapshot을 덮어쓰거나 P05 실패·실 provider 대기를 감추지 않는다.
- `check-api-baseline.py`와 isolated `check-api-baseline-negative.py` exit 0, 기존 public API snapshot 호환 및 변이 감지 확인(바이너리 호환 보장은 아님). 계획 P00~P08 48개 ID와 원장 48개 일치·누락/중복 0. snapshot 시점 local PASS 6/PARTIAL 41/FAIL 1. P05-T03 FAIL과 외부 대기·미완료 행을 그대로 보존해 별도 evidence를 작성한다.
- 계획 P00~P08의 48개 행, 현재 산출물·미완료/실 provider 대기, 과거 API snapshot 및 source commit을 `docs/evidence/feature-baseline-current-20261113.md`에 기록하고 P08-T05 기록 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. snapshot 자체는 FAIL 1·PARTIAL 41인 INCOMPLETE이며 제품 완성이 아니다. 기존 기준점과 P05 실패는 보존한다.
- P08-T05 갱신 직후 `verify-progress.py`는 구현/로컬 집계 불일치로 nonzero였다. 후속 명령이 성공해 전체 shell exit가 0으로 보였으나 원장 검사는 FAIL이다. 원인을 확인해 정정한 뒤 단독 재실행한다.
- 원인은 기존 P08-T05 행의 추가 WORK_LOG evidence를 교체 문자열이 포함하지 않아 행만 미변경된 것이다. 해당 행을 정확히 갱신하고 선언 집계와 비교한다.
- P08-T05 정확한 행 교체 후 `python3 scripts/verify-progress.py` 단독 exit 0. 과거 snapshot의 P05 FAIL/미완료 수와 실제 provider 대기를 바꾸지 않는다.
- `check-progress-negative.py`, `check-api-baseline-negative.py`, `check-manifest.py`, `verify-progress.py`, diff 검사 각각 PASS. 커밋 전: INCOMPLETE 48행 snapshot과 P08-T05 문서화 Task 상태만 포함하며 제품 전체를 완료로 바꾸지 않는다.

### P00-T02 도구 기준 재감사 시작
- 오래된 TOOLCHAIN의 Unity 라이선스/모듈 미검증과 과거 빌드 상태를 현재 실제 환경·증거로 정정한다. Unity 공식 지원 문서 조회를 시작 기록보다 먼저 수행한 순서 누락을 기록한다. 설치되지 않은 Editor나 실제 provider를 완료로 표시하지 않는다.
- `unity editors list --installed --format json`에서 설치 Editor는 6000.5.8f1(Android, Android SDK/NDK, iOS, OpenJDK) 및 6000.4.0f1(Web/Windows), `unity license status` active=true만 확인했다(계정/라이선스 식별자 기록 없음). JDK 21.0.10, Xcode 26.6(17F113), Swift 6.3.3, adb 37.0.1, Android SDK 34–36/37.0, build-tools 34–36, Docker 29.1.3/Compose 2.40.3, PostgreSQL 17.6 실행 확인. Unity 6000.3 LTS는 설치되지 않았으며 실제 provider·실기기 검증은 별도다.
- `TOOLCHAIN.md`에 2026-11-13 실제 조회 버전·명령·LOCAL_MOCK/외부 한계를 추가하고 `ENVIRONMENT.md`, USER-UNITY 현재 evidence, ENV-001 증상을 정정했다. Unity 공식 지원 정책은 https://unity.com/releases/unity-6/support 참조. 6000.3 LTS를 설치·검증했다고 주장하지 않는다.
- P00-T02 완료 조건인 실제 버전/명령/출처와 가능한·불가능한 검증 및 미확정 항목 후속 기록을 충족해 도구 감사 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. 6.3 LTS 미설치 ENV-001은 OPEN, 26.5 실패 및 실제 provider 대기는 그대로다.
- P00-T02 행/집계 반영 후 `verify-progress.py` PASS. 커밋 전: 도구 감사·환경 대기와 당시 결과만 포함하며 6.3 LTS/실 provider 또는 iOS 26.5 실패를 해소했다고 기록하지 않는다.

### P00-T04 원장·명령 진입점 재감사 시작
- 현재 문서 검사기와 빌드 진입점이 계획의 행 누락·증거 없는 PASS·잘못된 상태 및 도구 부재/명령 실패 구분을 충족하는지 확인한다. 제품/원본 문서에 mutation을 적용하지 않고 artifacts 임시 사본만 사용한다.
- `check-progress-negative.py`에 3개 격리 mutation(필수 행 삭제, PASS evidence 제거, 잘못된 상태)을 추가해 모두 거부했다. `test_entrypoint_exit_codes.py` 2건 PASS/skip0: 도구 부재는 exit 2, 인위적 build 실패는 exit 7. 원본 문서는 변경하지 않았다. 실제 doctor 및 Makefile 경로를 이어서 확인한다.
- `bash scripts/doctor.sh` exit 0: 도구·Docker engine·Android SDK 경로가 응답했다. 이 명령은 라이선스·서명·실기기·플랫폼 동작 검증이 아니다. Makefile의 동일 진입점도 확인한다.
- `make doctor`, `make verify-progress`, 강화 `check-progress-negative.py` 및 종료 코드 격리 단위 2건 PASS/skip0. 도구 가용성/문서 검사는 제품 통과가 아니며 플랫폼 build의 실제 결과는 별도 evidence를 참조한다.
- P00-T04 완료 조건과 실제 실행을 `docs/evidence/p00-entrypoints.md`에 연결하고 문서/진입점 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. 실제 제품 suite와 외부 provider는 별도다.
- 도구 부재 fixture는 PATH와 전용 ANDROID_HOME만 격리하고 시스템 HOME은 유지하도록 조정한다. 종료 코드 검증을 재실행한다.
- HOME 유지 fixture에서 `test_entrypoint_exit_codes.py` 2건 PASS/skip0, 원장/diff PASS. 커밋 전: 음성 검사·CI 단위·해당 Task evidence만 포함한다. 제품/실 provider 완료 선언은 아니다.

### P00-T05 ignore·설정 격리 재감사 시작
- 추적 파일명만 확인한 결과 실제 `.env`/서명·서비스 설정 파일은 추적 목록에서 발견되지 않았다. 기존 `.gitignore`는 `.env.local`만 막고 `.env`, 변형 환경 파일, Unity `.ulf` 및 독립 APK/AAB/IPA를 명시적으로 막지 않으므로 보강한다. 실제 비밀 파일 내용은 읽지 않는다.
- `test_gitignore_secrets.py` 2건 PASS/skip0: synthetic .env/서명/Unity license/빌드 산출물 이름은 ignore, example 이름은 추적 가능하다. Android Google 설정 누락의 정확한 key와 no-fallback 경로를 추가 점검한다.
- Android `GoogleAuthProvider.signIn`은 client ID가 없으면 backend 호출 전 CONFIG_REQUIRED이지만 `nativeCode`에 누락 key 이름이 없다. Unity capability reason은 auth/store 공통 문구로 실제 빠진 설정을 구분하지 못한다. P00-T05의 누락 key 진단 기준에 맞춰 허용된 key 이름만 표시하고 값/Mock fallback은 노출하지 않는다.
- Native GoogleAuthProvider의 미설정 오류에 `googleServerClientId` key 이름을 추가하고 Unity capability reason을 auth/store/push별 실제 누락 key로 분리했다. synthetic 설정 matrix 및 로그인 호출 전 차단 test를 작성했다. 실제 Google 인증은 미실행이다.
- Android provider/bridge 시험 첫 호출은 `ANDROID_HOME`이 없어 SDK location 탐색에서 exit 1, 테스트는 NOT_RUN이었다. 설치된 Android SDK 경로를 환경변수로 명시해 재실행한다. 사용자 local.properties는 만들지 않는다.
- `ANDROID_HOME=<installed SDK> android/gradlew ... GoogleAuthProviderTest ... GoogleAuthBridgeHandlerTest --rerun-tasks` exit 0: provider 15건·bridge 5건/skip0. 설치 SDK XML 버전 경고는 있었고 실 Google 인증은 아니다. Unity capability 공개 전달과 challenge 호출 전 차단을 명시적으로 확인한다.
- Android provider/bridge `--rerun-tasks` exit 0: JUnit 각각 15건·5건/실패0/skip0, client ID 없으면 gateway/challenge 미호출 및 정확한 key, capability 누락 조합을 확인했다. 이는 fake이며 실 Google 인증은 아니다. Unity managed 전달·나머지 설정 격리 테스트를 실행한다.
- Backend `EnvironmentPolicyTest`, Android `ConfigurationTest`, Swift `ConfigurationTests` 각 2건 PASS/skip0; C# `smoke-csharp-registry.sh` exit 0에서 `googleServerClientId` capability reason 전달 확인. `test_gitignore_secrets.py` 2건 PASS/skip0. synthetic/fake 및 standalone managed 시험이며 실제 Google/Apple provider는 미실행이다.
- Android Google provider/bridge 제품 코드가 바뀌어 기존 Maven·UPM·Android Player 증거는 이전 source에 대한 것이다. 재검증 전 P08-T01/T03/T04를 IN_PROGRESS/PARTIAL로 낮추고 과거 PASS evidence는 보존했다. iOS Native 제품은 변경되지 않았다.
- 새 `maven-config-diagnostic-20261113`에 변경 Android product를 다시 publish하고 독립 R8 소비자를 빌드한다. 개발키·서비스 credential 관련 환경 변수를 제거한 명령으로 backend bootJar도 빌드한다. 기존 staging/산출물은 보존한다.
- `env -u GAMEBRIDGE_DEV_AUTH_KEY -u SERVER_TOKEN_ENCRYPTION_KEY -u GOOGLE_APPLICATION_CREDENTIALS backend/gradlew -p backend bootJar` exit 0 (`artifacts/config-diagnostic-backend-build.log`): 명시적 local build만 확인, 서버 기동·실 provider는 아님. Android build는 진행 중이다.
- 개발키·Google credential 환경변수를 제거한 `build-android.sh --mock` exit 0 (`artifacts/config-diagnostic-android-build.log`, Maven `artifacts/maven-config-diagnostic-20261113`). Android 실제 provider는 미검증이다. 새 격리 clean consumer를 실행한다.
- iOS `AppleAuthBridgeHandler`의 store/push capability reason 역시 일반 문구라 `coinsStoreProductId`, `premiumStoreProductId`, `installationId`를 구체적으로 안내하지 않는다. 값 없이 key 이름만 보이도록 수정한다. Apple entitlement·실 계정 검증은 별도다.
- `swift test --package-path ios --filter AppleAuthBridgeTests` exit 0, XCTest 3건/실패0/skip0: synthetic capability의 누락 product/installation key 확인, 실제 Apple 인증/entitlement은 아님. iOS 제품 코드도 변경되어 이전 XCFramework는 구 source이며 P08-T02를 IN_PROGRESS/PARTIAL로 전환했다.
- 변경 Android Maven으로 `smoke-android-maven-consumer.sh` exit 0 (`artifacts/android-maven-consumer.IjHXTq`), unsigned R8 APK/merged manifest 확인. iOS Apple bridge 변경은 아직 새 XCFramework에 포함되지 않아 새 output으로 archive/symbol/link를 검증한다.
- `GAMEBRIDGE_IOS_OUTPUT_DIR=<new> bash scripts/build-ios.sh --xcframework` exit 0 (`artifacts/config-diagnostic-ios-build.log`), device/simulator 무서명 archive 및 XCFramework 생성. symbol/독립 link와 실기기/실 provider는 별도다.
- 변경 iOS XCFramework `verify-xcframework.py` exit 0(device arm64/simulator arm64+x86_64, C ABI 4개), 별도 `swiftc` 링크 및 IOSSIMULATOR load command 확인. 독립 SwiftPM source consumer host 실행 exit 0 (`artifacts/ios-source-consumer.OuaLdz`). 서명 실기기/실 provider는 미검증이다. 새 Android/iOS 산출물로 UPM staging을 생성한다.
- 새 stage Unity 검증 호출은 작업 디렉터리 오타로 시작되지 않아 모든 Editor/hook 시험 NOT_RUN이었다. 올바른 경로에서 실행한다.
- 새 UPM stage의 Sample API/Editor fake test 및 동일 프로젝트 GUID 재import PASS (`artifacts/offline-sample.X4RqNd`), Android 실제 Gradle hook 2회 hash 불변 PASS (`artifacts/unity-android-mock.RMw4BW`). iOS hook은 진행 중이며 원격/실기기 결과가 아니다.
- 새 UPM stage `smoke-unity-ios-hook-repeat.sh` exit 0 (`artifacts/unity-ios-mock.v5pYhN`): 실제 Xcode export hook 2회 후 PBX·XCFramework hash 불변. 이 결과는 서명/Player 실행이 아니다. 변경 product의 양 Player는 다음에 검증한다.
- Android/iOS capability 누락 key 개선, synthetic ignore 시험 및 no-key build, 새 UPM sample/양 export hook이 로컬 검증됐다. 실제 Unity sandbox 누락 경계·변경 Player 및 실제 provider는 아직 NOT_RUN이다. 커밋 전: 제품 진단 코드·관련 테스트·ignore·정제 문서만 포함하고 P00-T05/P08은 PARTIAL 유지한다.

### P00-T05 Unity sandbox 설정 누락 Player 검증 시작
- Android/iOS test-only consumer로 PLATFORM_SANDBOX 초기화 후 누락 configuration key를 capability에서 확인한다. Android는 Google sign-in이 key 검사 단계에서 CONFIG_REQUIRED, iOS는 store ID 미설정 시 products가 CONFIG_REQUIRED인지 확인한다. `example.invalid`만 사용하며 실제 계정·서버·스토어 UI는 열지 않는다.
- Android는 client ID 없음·Google sign-in CONFIG_REQUIRED, iOS는 store ID 없음·products CONFIG_REQUIRED와 양쪽 capability key 이름을 검사하는 test-only consumer를 작성했다. `example.invalid` 사용, 아직 컴파일/Player는 NOT_RUN이다.
- `run-unity-sandbox-config.py`는 Android/iOS를 명시적으로 선택해 누락 key와 no-fallback marker를 요구한다. opt-in·다른 플랫폼/누락 marker 거부 단위 2건 PASS/skip0. 실제 Provider 계정 호출은 설계상 없다. 양 managed compile을 확인한다.
- Android `UNITY_ANDROID` 및 iOS `UNITY_IOS` test-only sandbox config consumer managed compile 각각 exit 0, 경고·오류 0. runner 음성 2건 PASS/skip0. 실제 Unity Player·실 provider는 아직 미실행이다. 커밋 전: test-only consumer/runner·검증만 포함한다.
- `run-unity-sandbox-config.py --platform ios`에서 실제 Unity iOS bridge가 store/installation 누락 key capability와 products CONFIG_REQUIRED를 반환하는지 확인한다. 시작 기록을 먼저 커밋한다. 실 Apple 인증/스토어 UI는 실행하지 않는다.
- `run-unity-sandbox-config.py --platform ios` exit 0 (`artifacts/unity-sandbox-config-ios-c9m2245o`): 새 iOS Simulator Unity Player에서 store/installation 누락 key capability와 products CONFIG_REQUIRED/no-fallback marker PASS, tracked-clean. Apple 계정/스토어·서버는 호출하지 않았다.
- iOS sandbox config test Simulator를 삭제 없이 shutdown했다. 커밋 전: iOS 부분 결과만 기록하며 Android Player와 실제 provider는 미실행이다.
- `run-unity-sandbox-config.py --platform android`에서 실제 Unity Android bridge의 누락 key capability 및 Google sign-in CONFIG_REQUIRED/no-fallback를 확인한다. 새 전용 AVD를 사용하며 시작 기록만 먼저 커밋한다.
- `run-unity-sandbox-config.py --platform android` exit 0 (`artifacts/unity-sandbox-config-android-yklqwymu`): 새 Android Player에서 client/store/installation 누락 key capability와 Google sign-in CONFIG_REQUIRED/no-fallback PASS, tracked-clean. 최초 전체화면 안내 수동 처리. 실제 Google 계정/서버는 호출하지 않았다.
- `docs/evidence/p00-mode-config-isolation.md`에 no-key 빌드·fake 설정·양 Unity sandbox 누락 key/no-fallback·ignore 범위를 연결하고 P00-T05만 IMPLEMENTED/로컬 PASS로 갱신했다. Android/iOS actual provider 인증·entitlement·실기기/원격 서비스는 여전히 별도 대기다.
- P00-T05 갱신 후 `verify-progress.py`, `check-progress-negative.py`, ignore 단위 2건 PASS/skip0, diff PASS. 커밋 전: 정제된 설정 격리 evidence와 해당 Task 상태만 포함, P08 새 Native Player 회귀 및 실제 provider를 완료로 바꾸지 않는다.
