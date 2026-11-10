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
