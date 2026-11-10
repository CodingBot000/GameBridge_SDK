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
