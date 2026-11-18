# GameBridge SDK 개발 시작

배치34의 최신 검증·제약은 [통합 증거](docs/evidence/p10-batch34-integrated.md)를 따른다. 실제24 HTTP operation의 성공 응답 구조, DTO23개, 새 양플랫폼 Unity LOCAL_MOCK 소비와 선정 JVM API를 확인했다. C ABI 시간은 측정했지만 Task/continuation·Android heap·Unity Scene/Frame 및 전체 Strict는 미완료이며 DEV_RC를 유지한다.


## 이 패키지의 성격

이 저장소에는 Kotlin Android SDK, Swift iOS SDK, Unity C# 패키지, Kotlin Backend와 회귀 하네스가 구현되어 있다. 이 문서는 초기 개발계획 양식에서 시작했으며, 현재 작업은 [진행 원장](docs/PROGRESS.md), [작업 로그](docs/WORK_LOG.md), [최종 보고](docs/FINAL_REPORT.md)와 최신 배치 증거에서 재개한다. 소스가 없는 초기 상태로 가정하거나 이미 검증된 작업을 다시 만들지 않는다.

구현·로컬 검증·실제 Provider 검증은 다르다. LOCAL_MOCK의 Unity Android/iOS Player 실행 근거는 있지만 실제 Google/Apple 로그인·결제·FCM/APNs·실기기는 미검증이며, 기존 StoreKit26.5 실패와 환경/문서 gap이 남아 전체 SDK는 완료가 아니다. 아래 최초 실행용 문구는 기본 계약이며 사용자가 명시한 개별 배치의 Git 인계 허용과 작업 범위를 함께 적용한다.

## 배치

압축파일을 풀고 아래 파일들을 **실제 개발 저장소 루트**에 넣는다. `gamebridge_codex_plan` 폴더가 한 겹 더 생겼다면 그 내부 내용을 루트로 옮긴다.

```text
AGENTS.md
START_HERE.md
docs/
  DEVELOPMENT_PLAN.md
  PROGRESS.md
  WORK_LOG.md
  USER_SETUP.md
  FINAL_REPORT.md
```

기존 AGENTS.md나 동일한 이름의 문서가 있다면 덮어쓰지 않는다. Codex에게 기존 지침을 보존하면서 이번 지침을 병합하게 한다. 이미 개발된 프로젝트에서는 기존 구현을 먼저 조사하고 재사용한다.

## Codex에 처음 넣을 지시문

아래 문장을 그대로 전달한다. 모델 이름이나 CLI 플래그는 여기에서 임의 지정하지 않는다. 사용 중인 Terra Medium 설정을 유지한다.

```text
AGENTS.md와 START_HERE.md를 읽고 docs/DEVELOPMENT_PLAN.md의 P00부터 P11까지 실제 개발을 수행해.
계획만 다시 작성하거나 단계마다 승인을 묻지 말고, 구현·로컬 확인·문서 갱신·로컬 커밋 후 다음 작업으로 계속 진행해.
기능 개발은 P08까지 우선 진행하고, P09에서 하네스를 붙인 뒤 P10에서 리팩토링해.
계정 로그인, 콘솔 등록, 인증서·실키, 외부 실연동 테스트는 docs/USER_SETUP.md로 넘기되 실제 Provider 코드까지는 구현해.
매 Task 시작·검증·블로커 발견·커밋 전에 PROGRESS.md와 WORK_LOG.md를 반드시 갱신해.
Mock 검증과 실제 플랫폼 검증을 구분하고, 미실행·실패·미구현을 완료라고 쓰지 마.
기존 사용자 변경과 비밀정보를 보호하고 push·공개 배포는 하지 마.
최종적으로 완료/미완료/사용자 설정 대기/환경 대기/실패를 구분한 FINAL_REPORT.md까지 작성해.
```

## 실행 환경의 최소 조건

저장소 쓰기와 로컬 명령 실행이 허용되어 있어야 한다. 읽기 전용 실행환경에서는 문서만으로 소스 작성·커밋이 가능해지지 않는다. 의존성 다운로드가 허용되어야 전체 빌드를 진행할 수 있다. Codex가 권한 설정이나 승인 정책을 몰래 바꾸지는 않는다.

macOS + Xcode, Android 개발 도구, Unity Editor, JDK, Docker가 모두 있으면 검증 범위가 넓어진다. 일부가 없어도 가능한 코드는 계속 작성하고, 실행하지 못한 검증만 환경 대기로 분류한다. Apple/Google/Unity 로그인과 유료 가입은 사용자에게 남긴다. 무인 실행을 위해 운영체제 보안이나 인증을 우회하지 않는다.

## 세션이 실제로 종료된 경우의 재개 지시문

```text
AGENTS.md와 docs/PROGRESS.md, docs/WORK_LOG.md 마지막 기록을 읽어.
Git 작업 트리를 확인하고 마지막 Task의 실제 구현과 검증 상태를 대조한 뒤 미완료 작업부터 이어서 P11까지 진행해.
이미 완료한 작업을 처음부터 다시 만들지 말고, 중간 승인 없이 문서 갱신과 로컬 커밋을 계속해.
```

한 번의 지시로 계속 진행하도록 작성했지만, 사용량 한도·세션 수명·도구 권한까지 문서가 해제할 수는 없다. 그런 종료에 대비해 재개 가능한 기록을 남기도록 강제한다.

## 사용자가 마지막에 확인할 파일

`docs/FINAL_REPORT.md`에서 전체 결과를 보고, `docs/USER_SETUP.md` 순서대로 계정·콘솔·서명을 설정한다. `PROGRESS.md`의 실연동 대기 항목을 실제로 재실행한 뒤에만 검증 완료로 바꾼다. 설정값을 채팅에 붙여넣거나 Git에 넣지 않는다.


배치33 연속 작업 결과는 [통합 증거](docs/evidence/p10-batch33-integrated.md)를 따른다. 새 Native 패키지·독립 소비와 Swift Simulator Core 계측은 확인했으나 전체 Strict, OpenAPI의 HTTP 전수 대응, Native/Unity 성능 전체 및 P11 완료는 아직 PARTIAL이다. 기존 P05 실패·StoreKit 환경 위험·실 Provider 13건 대기는 유지한다.
