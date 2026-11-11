# GameBridge SDK — 개발 중

Android, iOS 및 Unity 게임을 위한 SDK와 Backend를 개발하고 있습니다. 현재 프로젝트는 완성품이 아닙니다. 각 기능의 구현·실행·실패 상태는 [진행 원장](docs/PROGRESS.md)과 [작업 기록](docs/WORK_LOG.md)을 확인하세요. 외부 계정·서명·키 등은 [사용자 설정](docs/USER_SETUP.md)에 정리되어 있습니다.

Android/iOS 샘플의 `LOCAL_MOCK` 로그인·구매·복원은 로컬 Backend를 사용합니다. 실제 Google/Apple 인증, 스토어 결제 및 원격 푸시 성공을 뜻하지 않습니다. Unity Native bridge에는 LOCAL_MOCK의 초기화·인증·상품·구매·서버 잔액·로그아웃 경로가 연결돼 있습니다. Native 및 fake 검증은 수행했지만 Unity Android/iOS Player 전체 흐름은 아직 실행하지 않았습니다. 현재 설치된 Unity Editor는 활성 라이선스가 없어 Editor 및 IL2CPP 검증을 수행하지 못했습니다. iOS 26.5의 로컬 StoreKit 상품 조회 시험은 실패 상태입니다.

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

Backend 일반 시험에는 명시적으로 활성화하지 않은 DB 통합 시험이 skip될 수 있습니다. `scripts/smoke-local.sh`는 Unity player를 포함한 push 전달·라우팅 검증이 미완료이므로 전체 성공하지 않습니다. 개발 발송 endpoint의 local-mock 응답은 SIMULATED이며 원격 전송이 아닙니다. 세부 실행 조건과 실제 확인 범위는 [USER_SETUP](docs/USER_SETUP.md) 및 [WORK_LOG](docs/WORK_LOG.md)를 참고하세요.

## 패키징

`build-android.sh --mock`은 새 `artifacts/maven-build.*` 경로에 SDK를 발행하고 별도 소비 앱의 release 빌드를 검사합니다. `GAMEBRIDGE_MAVEN_REPO`에 존재하지 않는 절대 경로를 지정할 수도 있으며, 기존 출력은 덮어쓰지 않습니다. `generate-ios-project.sh`와 `build-ios.sh`는 기존 프로젝트를 덮어쓰지 않고 `artifacts/ios-project.*`에 격리 Xcode project를 생성합니다. `build-ios.sh --xcframework`는 별도 출력 디렉터리에 무서명 static XCFramework를 만듭니다. 기존 출력 경로는 덮어쓰지 않으며 `GAMEBRIDGE_IOS_OUTPUT_DIR`로 새 경로를 지정할 수 있습니다. `scripts/package-sdk.sh`는 두 산출물을 Unity 패키지 staging에 묶지만 Unity import와 실제 빌드는 아직 검증되지 않았습니다. 생성된 `artifacts/`는 로컬 전용이며 배포하지 않습니다.

현재 API와 통합상의 제한은 [API](docs/API.md), [통합 안내](docs/INTEGRATION.md), [보안 경계](docs/SECURITY.md)를 참고하세요.

## 로컬 회귀 집계

`bash scripts/verify-all.sh --available` 또는 `--strict-local`은 실제 실행한 suite, 필수 미실행·미구현·기존 실패, 외부 설정 대기를 구분해 `artifacts/verify-all-*`에 기록합니다. 격리 DB와 local server가 필요한 lane은 명시적인 test 환경 설정이 없으면 건너뛰며, 전체 성공으로 처리하지 않습니다. Mock push의 Backend→Native local DB 시험은 통과했으며 Unity runtime 전체 경로는 미완료입니다.

### Unity Android LOCAL_MOCK 통합 확인 준비

별도 소비 프로젝트 생성과 빌드 절차는 [사용자 설정의 Unity Android LOCAL_MOCK 절차](docs/USER_SETUP.md#unity-android-local_mock-재실행-준비-px-t01)를 참고하세요. 현재는 프로젝트 생성, 패키지 checksum, 시나리오의 managed compile 및 Backend 단독 local-mock trace만 확인했습니다. Unity Editor import와 Android Player 실행, Kotlin SDK를 거친 전체 흐름은 미실행입니다.


### 추가 검증 도구 (Unity Android LOCAL_MOCK)

준비가 완료된 Unity 환경에서 전체 Player 흐름을 확인하기 위한 별도 Runner는 harness/run-unity-android-mock-e2e.py이다. 전용 AVD 및 staging 무결성 확인, 격리 소비 프로젝트 생성, APK 빌드·설치·실행, Unity 마커·Backend trace 및 DB 1건/100코인 대조까지 수행하며 하나라도 누락되면 PASS가 아니다. **현재 실제 Unity Player 검증은 NOT_RUN이다.** Unity Hub 활성 라이선스와 Android Build Support 설치가 우선이다. 명령·비밀정보 분리·전용 환경 준비는 docs/USER_SETUP.md의 PX-T04~PX-T06 절을 따른다.

Android Native-only 재실행기는 harness/run-android-mock-bridge-e2e.py로, 기존 고정된 adb/에뮬레이터/DB 경로를 환경변수나 실행 옵션으로 변경할 수 있다. 다만 해당 수정본 재실행은 아직 NOT_RUN이다. 실제 PASS를 확보한 뒤 검증 증거의 민감정보를 제거하고 커밋하려면 harness/export-mock-e2e-evidence.py를 사용한다. 원본 로그·APK·로컬 DB는 Git에 올리지 않는다.
