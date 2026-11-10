# GameBridge SDK — 개발 중

Android, iOS 및 Unity 게임을 위한 SDK와 Backend를 개발하고 있습니다. 현재 프로젝트는 완성품이 아닙니다. 각 기능의 구현·실행·실패 상태는 [진행 원장](docs/PROGRESS.md)과 [작업 기록](docs/WORK_LOG.md)을 확인하세요. 외부 계정·서명·키 등은 [사용자 설정](docs/USER_SETUP.md)에 정리되어 있습니다.

Android/iOS 샘플의 `LOCAL_MOCK` 로그인·구매·복원은 로컬 Backend를 사용합니다. 실제 Google/Apple 인증, 스토어 결제 및 원격 푸시 성공을 뜻하지 않습니다. Unity 네이티브 브리지는 아직 status/shutdown 외 기능이 연결되지 않았고, 설치된 Unity Editor의 라이선스 확인이 실패해 Editor 및 IL2CPP 검증을 수행하지 못했습니다. iOS 26.5의 로컬 StoreKit 상품 조회 시험은 실패 상태입니다.

## 로컬 개발

도구와 버전은 [TOOLCHAIN](docs/TOOLCHAIN.md)을 참고하세요. Backend 실행 전 Docker와 전용 로컬 DB 비밀번호, 32자 이상의 로컬 개발 인증키, Base64로 인코딩한 32바이트 로컬 token 암호화 키를 비밀 환경에 준비합니다. 기존 DB 비밀번호 및 암호화 키는 재시작할 때 유지해야 합니다. 실제 키는 소스나 채팅에 넣지 않습니다.

```sh
# GAMEBRIDGE_DB_PASSWORD, GAMEBRIDGE_DEV_AUTH_KEY,
# SERVER_TOKEN_ENCRYPTION_KEY와 GAMEBRIDGE_MAINTENANCE_ENABLED를
# 현재 셸에 명시적으로 설정한 다음 실행
bash scripts/run-demo-backend.sh
```

별도 셸에서 다음 명령으로 Native build와 일부 검사를 실행할 수 있습니다.

```sh
bash scripts/build-android.sh --mock
bash scripts/generate-ios-project.sh
bash scripts/build-ios.sh --simulator
./backend/gradlew -p backend test
```

Backend 일반 시험에는 명시적으로 활성화하지 않은 DB 통합 시험이 skip될 수 있습니다. `scripts/smoke-local.sh`는 push 전달과 라우팅의 전체 경로가 미구현이므로 전체 성공하지 않습니다. 개발 발송 endpoint의 local-mock 응답은 SIMULATED이며 원격 전송이 아닙니다. 세부 실행 조건과 실제 확인 범위는 [USER_SETUP](docs/USER_SETUP.md) 및 [WORK_LOG](docs/WORK_LOG.md)를 참고하세요.

## 패키징

`build-android.sh --mock`은 새 `artifacts/maven-build.*` 경로에 SDK를 발행하고 별도 소비 앱의 release 빌드를 검사합니다. `GAMEBRIDGE_MAVEN_REPO`에 존재하지 않는 절대 경로를 지정할 수도 있으며, 기존 출력은 덮어쓰지 않습니다. `build-ios.sh --xcframework`는 별도 출력 디렉터리에 무서명 static XCFramework를 만듭니다. 기존 출력 경로는 덮어쓰지 않으며 `GAMEBRIDGE_IOS_OUTPUT_DIR`로 새 경로를 지정할 수 있습니다. `scripts/package-sdk.sh`는 두 산출물을 Unity 패키지 staging에 묶지만 Unity import와 실제 빌드는 아직 검증되지 않았습니다. 생성된 `artifacts/`는 로컬 전용이며 배포하지 않습니다.

현재 API와 통합상의 제한은 [API](docs/API.md), [통합 안내](docs/INTEGRATION.md), [보안 경계](docs/SECURITY.md)를 참고하세요.
