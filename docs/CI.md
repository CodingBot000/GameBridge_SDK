# CI 검증 범위 — 개발 중

`.github/workflows/verify.yml`은 pull request 및 수동 실행용으로 작성했으며 이 저장소에서 원격 GitHub Actions를 실행하지 않았다. checkout과 Java setup은 공식 action의 고정 commit을 사용하고 repository 권한은 `contents: read`다. 외부 Google/Apple/Firebase/Unity credential이나 fork에 전달할 secret은 사용하지 않는다.

Linux lane은 빈 전용 PostgreSQL service, Backend test-key/local DB fixture, Android fake/unit 및 source 없는 Maven/R8 consumer를 실행한다. DB 준비 script는 loopback·`gamebridge_ci_*`·빈 public schema를 요구하며 기존 DB를 삭제하지 않는다. 선택 test의 Gradle 환경값 변경이 UP-TO-DATE로 생략되지 않도록 `--rerun-tasks`와 JUnit 실행 수/skip 검사를 사용한다.

macOS lane은 Swift fake/contract XCTest와 synthetic iOS simulator host test를 실행한다. XcodeGen 2.46.0 공식 archive를 CI 임시 디렉터리에 내려받아 SHA256을 검증한다. 실제 Apple/Google 계정, 스토어 거래, 원격 push는 수행하지 않는다.

Unity Editor/player lane은 아직 구현·라이선스 준비가 없어 명시적으로 NOT_IMPLEMENTED/실패하며 최종 gate는 이를 통과로 간주하지 않는다. 50개 required scenario 중 PARTIAL/NOT_IMPLEMENTED가 남아 있어 coverage gate도 현재 실패한다. GitHub에서 job이 성공했다고 주장할 수 있는 원격 증거는 없다.

로컬 정적 확인: actionlint 1.7.12 종료 0, Swift 선택 시험 12건, 격리 PostgreSQL 준비 및 ledger/finalization 3건, JUnit/Swift 누락 음성 검사 확인. 사용한 runner image나 실제 GitHub Actions 실행을 대신하지 않는다.
