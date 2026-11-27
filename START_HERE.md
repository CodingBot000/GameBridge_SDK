<a id="gamebridge-포트폴리오-읽기사용-안내"></a>

# GameBridge SDK — 문서 찾아보기

**[README](README.md)**에서 핵심 성과를, **[기술 개요](docs/TECHNICAL_OVERVIEW.md)**에서 아키텍처·설계 선택·문제 해결 사례를 확인할 수 있습니다.

| 확인할 내용 | 바로가기 |
| --- | --- |
| Android 실기기 인증·구매 복구·Push·PII | [최신 실기기 검증](docs/evidence/android-physical-followup-20261127.md) · [기본 실기기 실행](docs/evidence/android-physical-local-mock-20261127.md) |
| 요청 경쟁·구매 복구·Export 복구 | [대표 기술 사례](docs/TECHNICAL_OVERVIEW.md#5-대표-기술-사례) |
| 설계 선택과 데이터 소유권 | [기술적 의사결정](docs/TECHNICAL_OVERVIEW.md#3-설계-선택과-trade-off) · [구현 상세](docs/ENGINEERING_NOTES.md) · [보안 설계](docs/SECURITY.md) |
| 구현과 테스트·실행의 연결 | [검증 근거](docs/VERIFICATION_EVIDENCE.md) · [CI 구성](docs/CI.md) |
| 기능별 검증 상태·실행 환경 | [기능 매트릭스](docs/FEATURE_MATRIX.md) · [버전·호환성](docs/COMPATIBILITY.md) |
| API·SDK 설치·Provider 설정 | [API](docs/API.md) · [통합 가이드](docs/INTEGRATION.md) · [사용자 설정](docs/USER_SETUP.md) |

## 설치·시연

- 최신 개발자용 배포본은 [v0.1.2-dev Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)입니다. 패키지 설치와 SHA-256 확인은 [통합 가이드](docs/INTEGRATION.md#1-패키지-준비)를 따릅니다.
- 직접 빌드하려면 [0.1.2-dev 패키징 절차](docs/INTEGRATION.md#1-패키지-준비)를 따릅니다. 이전 DEV_RC는 개발 이력에 보존돼 있습니다.
- [Editor Offline Demo](unity/Packages/com.gamebridge.sdk/Samples~/Offline%20Demo/README.md)는 외부 계정·서버 없이 메모리 Fake로 공통 API를 실행합니다. [Native Demo](unity/Packages/com.gamebridge.sdk/Samples~/Native%20Demo/README.md)는 Android/iOS LOCAL_MOCK 또는 명시한 Sandbox용이며, 실제 Provider 준비는 [USER_SETUP](docs/USER_SETUP.md)을 따릅니다.

0.1.2-dev의 내부 책임 분리, API·ABI, 양 플랫폼 업데이트와 로컬 회귀 결과는 [리팩토링 검증 기록](docs/evidence/bridge-client-refactor-verification.md)에 있습니다.

<details>
<summary>유지보수·개발 재개 안내</summary>

이 저장소는 Android·iOS·Unity와 Backend가 이미 구현된 개인 SDK 포트폴리오입니다. 빈 프로젝트/초기 계획으로 가정하지 않습니다. 최종 상태와 선택적 후속 범위는 [FINAL_REPORT](docs/FINAL_REPORT.md)를 따릅니다.

## 개발 종료와 재개 경계

사용자 문서36은 포트폴리오 상태를 전체 SDK 제품화 원장과 별도로 판정하도록 했습니다. 전체 Strict·Provider13건·모든 성능/OS 조건이 미완료여도 알려진 제한을 공개하고 포트폴리오 개발을 종료할 수 있습니다. 새 P1/P2 개선 사항을 자동 다음 필수 배치로 만들지 않습니다.

추가 기능·Provider 연동·지원 버전 확대는 새로운 명시적 요청이 있을 때만 선택합니다. 그때 AGENTS, PROGRESS, WORK_LOG와 관련 source/evidence를 읽고 기존 파일·Demo·DB·기기·라이선스를 보존합니다. 현재64 Task의 PARTIAL/FAIL과 실패 원본은 그대로 유지합니다.

## 내부 개발 이력 및 증거

현재 검증 상태의 기준은 [FEATURE_MATRIX](docs/FEATURE_MATRIX.md), [COMPATIBILITY](docs/COMPATIBILITY.md), [FINAL_REPORT](docs/FINAL_REPORT.md)입니다. [CI](docs/CI.md)는 Hosted와 로컬 검증의 차이를 설명합니다.

과거 계획·진행 원장·실패 및 변경 기록은 [DEVELOPMENT_PLAN](docs/DEVELOPMENT_PLAN.md) · [PROGRESS](docs/PROGRESS.md) · [WORK_LOG](docs/WORK_LOG.md) · [DECISIONS](docs/DECISIONS.md) · [CHANGELOG](docs/CHANGELOG.md)에서 확인합니다. [AGENTS](AGENTS.md)는 에이전트 작업 규칙입니다. 기존 상대 링크와 하네스의 경로 의존성을 보존하기 위해 파일을 이동하지 않습니다. 과거 기록을 현재 버전 검증으로 소급하지 않습니다.

</details>
