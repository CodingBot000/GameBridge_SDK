# GameBridge 포트폴리오 읽기·사용 안내

[README](README.md) → [Quick Start](docs/INTEGRATION.md) → [설계·문제 해결](docs/ENGINEERING_NOTES.md) → [검증/호환성](docs/COMPATIBILITY.md) 순서로 읽으면 됩니다. 면접 검토에 WORK_LOG 전체를 먼저 읽을 필요는 없습니다.

이 저장소는 Android·iOS·Unity와 Backend가 이미 구현된 개인 SDK 포트폴리오입니다. 빈 프로젝트/초기 계획으로 가정하지 않습니다. 최종 상태와 선택적 후속 범위는 [FINAL_REPORT](docs/FINAL_REPORT.md)를 따릅니다.

## 설치·시연

- 최신 개발자용 배포본은 [v0.1.1-dev Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.1-dev)입니다. 설치와 체크섬 확인은 [README](README.md#개발자용-pre-release-설치)를 따릅니다. 이전 `artifacts/portfolio-final/DEV_RC`는 역사적 후보입니다.
- 다른 checkout에는 Native 생성 바이너리가 없으므로 [기존 build/package 절차](docs/INTEGRATION.md#1-패키지-준비)를 사용합니다.
- Editor Offline Demo는 fake UI, Native Demo는 Android/iOS LOCAL_MOCK 또는 명시한 Sandbox용입니다. 실제 Provider는 [USER_SETUP](docs/USER_SETUP.md)의 별도 사용자 준비와 승인이 필요합니다.

## 개발 종료와 재개 경계

사용자 문서36은 포트폴리오 상태를 전체 SDK 제품화 원장과 별도로 판정하도록 했습니다. 전체 Strict·Provider13건·모든 성능/OS 조건이 미완료여도 알려진 제한을 공개하고 포트폴리오 개발을 종료할 수 있습니다. 새 P1/P2 개선 사항을 자동 다음 필수 배치로 만들지 않습니다.

추가 기능·Provider 연동·지원 버전 확대는 새로운 명시적 요청이 있을 때만 선택합니다. 그때 AGENTS, PROGRESS, WORK_LOG와 관련 source/evidence를 읽고 기존 파일·Demo·DB·기기·라이선스를 보존합니다. 현재64 Task의 PARTIAL/FAIL과 실패 원본은 그대로 유지합니다.
