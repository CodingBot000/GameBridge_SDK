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
