# GameBridge SDK 진행 원장

> 각 Task 시작·검증·블로커·커밋 전에 갱신한다.

## 현재 체크포인트

- 전체 상태: IN_PROGRESS
- 현재 Phase / Task: P00 / P00-T04
- 마지막 갱신 시각: 2026-11-10 (Asia/Seoul)
- 마지막 검증된 소스 커밋: 없음 (골격 검증 중)
- 현재 작업 트리 상태: P00-T03 부분 변경 및 Unity 생성 실패의 미검증 Demo 존재
- 현재 실행 모드: 미선택
- 바로 다음 행동: P00-T04 부분 커밋 후 공통 계약을 독립적으로 작성; P00-T03·T04는 미완료
- 불가피한 세션 종료 시 재개 행동: P00-T03 미완료 항목부터 이어서 구현하고 P00-T02 버전 조합을 재검증

## 집계

- 계획 Task 총수: 64
- 구현: NOT_STARTED 60 / IN_PROGRESS 3 / IMPLEMENTED 1 / BLOCKED 0
- 로컬 검증: NOT_RUN 60 / PASS 1 / FAIL 0 / PARTIAL 3 / DEFERRED_ENV 0 / REVIEW_ONLY 0
- 실연동 대상 Task: 13 / PASS 0 / WAITING_USER 13 / FAIL 0 / DEFERRED_ENV 0
- 위 실연동 WAITING_USER는 계획된 인증 필요성을 표시하며, 해당 구현이 준비되었다는 뜻이 아니다.
- 누락·추가 Task: 아직 조사하지 않음. 추가 시 PX-Tnn으로 등록하고 분모에 포함한다.

## 상태 범례

구현 `IMPLEMENTED`와 검증 `PASS`는 다르다. 로컬 PASS와 실연동 PASS도 다르다. 실행하지 않은 항목을 PASS로 바꾸지 않는다. 로컬 일부만 실행한 경우 PARTIAL, 코드만 읽은 경우 REVIEW_ONLY다. 실연동이 환경 때문에 미실행이면 DEFERRED_ENV로 구분한다.

Task ID는 커밋 메시지에도 포함한다. 현재 커밋의 SHA를 그 커밋 내부에 넣지 않는다. 각 행의 증거 경로는 `docs/evidence/...`와 WORK_LOG의 Task 기록을 참조한다.

## Task 원장

| Task ID | 작업 | 구현 | 로컬 검증 | 실연동 검증 | 증거/로그 | 블로커/설정 |
|---|---|---|---|---|---|---|
| P00-T01 | 저장소 보존·작업 원장 초기화 | IMPLEMENTED | PASS | N/A | WORK_LOG P00-T01 | - |
| P00-T02 | 도구·라이선스·버전 조합 확정 | IN_PROGRESS | PARTIAL | N/A | docs/TOOLCHAIN.md, WORK_LOG P00-T02 | ENV-001 |
| P00-T03 | 빌드 가능한 최소 프로젝트 구성 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P00-T03 | ENV-002, ENV-003 |
| P00-T04 | 진행 문서 검사·기본 명령 진입점 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P00-T04 | - |
| P00-T05 | 모드·비밀정보·설정 격리 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P01-T01 | 공통 모델·오류·상태 schema | NOT_STARTED | NOT_RUN | N/A | - | - |
| P01-T02 | Bridge wire protocol·공용 fixture | NOT_STARTED | NOT_RUN | N/A | - | - |
| P01-T03 | SDK 상태기계·Provider interface | NOT_STARTED | NOT_RUN | N/A | - | - |
| P01-T04 | 결정적인 Fake Provider | NOT_STARTED | NOT_RUN | N/A | - | - |
| P01-T05 | Native HTTP·저장소·세션 소유권 기반 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T01 | Backend·PostgreSQL·migration 기동 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T02 | Mock 사용자·opaque 세션·갱신 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T03 | 상품·재화·구매 원장 서비스 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T04 | purchase 재시도·finalization queue | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T05 | device token·config·개발 푸시 API | NOT_STARTED | NOT_RUN | N/A | - | - |
| P02-T06 | 로컬 Backend 통합 smoke 명령 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T01 | Kotlin SDK의 LOCAL_MOCK 수직 연결 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T02 | Swift SDK의 LOCAL_MOCK 수직 연결 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T03 | Android JNI 왕복 transport | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T04 | Swift C ABI 왕복 transport | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T05 | Unity facade·dispatcher·request registry | NOT_STARTED | NOT_RUN | N/A | - | - |
| P03-T06 | Unity 최소 Demo·Native 경로 분기 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P04-T01 | 실제 Android Google 로그인 adapter | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-AUTH-GOOGLE |
| P04-T02 | 실제 iOS Apple 로그인 adapter | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-AUTH-APPLE |
| P04-T03 | 서버 실제 identity 검증·nonce 재사용 방어 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-AUTH-GOOGLE, USER-AUTH-APPLE |
| P04-T04 | 세션 복원·single-flight 갱신·로그아웃 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P04-T05 | 인증 Native·Unity 소비자 통합 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-AUTH-GOOGLE, USER-AUTH-APPLE |
| P05-T01 | 구매 상태·account binding 계약 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P05-T02 | 실제 Google Play Billing adapter | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-BILLING-GOOGLE |
| P05-T03 | StoreKit 2·로컬 .storekit 시나리오 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-BILLING-APPLE |
| P05-T04 | 실제 Google·Apple 구매 검증 서버 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-BILLING-GOOGLE, USER-BILLING-APPLE |
| P05-T05 | 지급 원자성·동시성·서버 finalizer 연결 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P05-T06 | Native 복구·store finish·timeout 이후 처리 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P05-T07 | Unity·Native 상점 완성 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-BILLING-GOOGLE, USER-BILLING-APPLE |
| P06-T01 | 실제 FCM 등록·수신·권한 adapter | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-PUSH-GOOGLE |
| P06-T02 | Swift APNs 등록·Host forwarding | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-PUSH-APPLE |
| P06-T03 | Unity iOS Push Host Adapter | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-PUSH-APPLE |
| P06-T04 | Backend FCM·APNs 실제 sender | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P06-T05 | 수명주기·콜드스타트·클릭 라우팅 | NOT_STARTED | NOT_RUN | WAITING_USER | - | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P07-T01 | 진단·redaction·점검 설정 완성 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P07-T02 | 세 샘플 전체 사용자 흐름 연결 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P07-T03 | 연동 문서·오류·소유권 가이드 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P07-T04 | 구현 누락 1차 점검 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P08-T01 | Android Maven 산출물·소비 build | NOT_STARTED | NOT_RUN | N/A | - | - |
| P08-T02 | Swift Package·static XCFramework 산출물 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P08-T03 | UPM staging·멱등 build hook | NOT_STARTED | NOT_RUN | N/A | - | - |
| P08-T04 | 신규 Unity 프로젝트 재설치 검증 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P08-T05 | 기능 개발 기준점 고정 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T01 | 후반 하네스 manifest·공통 contract test | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T02 | Core·Bridge 회귀·실패 주입 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T03 | 인증·세션·개발모드 차단 회귀 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T04 | 구매·DB 동시성·복구 회귀 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T05 | Push·Lifecycle·패키징 회귀 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T06 | 검증 집계·진행 원장 강제 검사 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T07 | CI 설정·플랫폼 lane 분리 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P09-T08 | Fail-closed 하네스 자체 시험 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P10-T01 | 검증 기준 유지하며 Core·Bridge 리팩토링 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P10-T02 | 인증·결제·푸시 책임과 보안 정리 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P10-T03 | 측정 기반 수명주기·메모리·응답 확인 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P10-T04 | 리팩토링 후 재패키징·호환성 재검증 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P11-T01 | 전체 Task·TODO·계약 누락 최종 감사 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P11-T02 | 사용자 설정·실연동 재개 runbook 완성 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P11-T03 | 최종 문서·release candidate 로컬 패키지 | NOT_STARTED | NOT_RUN | N/A | - | - |
| P11-T04 | 마지막 검증·커밋·인계 | NOT_STARTED | NOT_RUN | N/A | - | - |

## 블로커 원장

| ID | 유형 | 영향 Task | 실제 증상/실행 명령 | 코드 개발 지속 방법 | 해소 조건 | 상태 |
|---|---|---|---|---|---|---|
| ENV-003 | ENV | P00-T03 | XcodeGen 명령 없음; iOS 프로젝트 명세 생성·앱 빌드 미검증 | 독립 작업 진행; XcodeGen 준비 또는 다른 재현 가능한 프로젝트 생성 | Xcode 프로젝트 생성 및 빌드 | OPEN |
| ENV-002 | ENV | P00-T03 및 Unity 검증 | Unity Editor 생성 시 라이선스 확인 실패, 종료 198 | 프로젝트 생성 안내 스크립트 제공, 다른 플랫폼 계속 | 사용자 라이선스 및 Editor 재확인 | OPEN |
| ENV-001 | ENV | P00-T02 | Unity 6.3 LTS 미설치; 설치 버전의 모듈·라이선스 미확인 | 설치된 Editor로 검증 시도 | 호환 Editor와 모듈·라이선스 확인 | OPEN |

유형: USER=사용자 계정·서명·콘솔, ENV=설치/실행환경, BUG=내부 버그, DEP=선행 구현 미해결. 같은 사건은 중복 ID를 만들지 않고 영향 Task를 추가한다. 사용자 인증 필요성은 USER_SETUP에 이미 계획되어 있지만 실제 구현 준비 여부는 개발 중 갱신한다.

## 기능별 검증 매트릭스

| 기능 | Android 코드/빌드 | iOS 코드/빌드 | Unity Editor | Unity Android | Unity iOS | 실제 외부 서비스 |
|---|---|---|---|---|---|---|
| Core·Bridge | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | N/A |
| 인증 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 결제 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 푸시 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 세션·복구 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 배포·신규 소비 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | N/A |

각 칸은 가능한 경우 `BUILD:PASS / RUN:WAITING_USER`처럼 분리한다. “Android 완료” 한마디로 Native standalone과 Unity Android를 합치지 않는다.

## 완료/미완료 요약

- 구현 및 로컬 검증 완료: 없음
- 코드 구현됨, 로컬 검증 미완료: 없음
- 사용자 설정만 남은 항목: 아직 구현 전이므로 확정하지 않음
- 내부 미구현/실패: 아직 조사 전
- 환경 대기: 아직 조사 전
- 범위 제외: Windows/C++·Unreal/Godot·구독·환불 자동화·RTDN/Server Notifications 운영·관리자 웹·Kubernetes·상용 배포

## 최근 체크포인트 이력

| 시각 | Phase/Task | 구현 요약 | 검증 | 다음 행동 |
|---|---|---|---|---|
| 초기 문서 생성 | P00-T01 이전 | 계획만 작성됨 | 실행 없음 | 저장소 조사 |
