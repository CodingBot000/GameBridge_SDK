# GameBridge SDK 진행 원장

> 각 Task 시작·검증·블로커·커밋 전에 갱신한다.

## 현재 체크포인트

- 전체 상태: IN_PROGRESS (작업 미완료)
- 현재 Phase / Task: P09 / P09-T04 Xcode 앱 프로세스 복구
- 마지막 갱신 시각: 2026-11-11 (Asia/Seoul)
- 마지막 검증된 소스 커밋: c22336c (격리 strict aggregate; Unity·외부 서비스는 미검증)
- 현재 작업 트리 상태: 구현 변경 커밋됨; Unity 미완성 Demo와 Python 캐시 미추적 보존
- 현재 실행 모드: LOCAL_MOCK 및 격리된 fake 시험; 실제 provider 미실행
- 바로 다음 행동: 전용 simulator 테스트 앱의 finish 전 프로세스 종료·재실행 복구 검증
- 재개 행동: AGENTS.md·START_HERE.md·계획과 원장 및 Git 상태를 확인한 뒤 현재 P11 작업과 남은 내부 누락을 이어서 진행한다. 실제 플랫폼과 Mock 증거를 분리한다.

## 집계

- 계획 Task 총수: 64
- 구현: NOT_STARTED 0 / IN_PROGRESS 62 / IMPLEMENTED 2 / BLOCKED 0
- 로컬 검증: NOT_RUN 0 / PASS 2 / FAIL 1 / PARTIAL 60 / DEFERRED_ENV 1 / REVIEW_ONLY 0
- 실연동 대상 Task: 13 / PASS 0 / WAITING_USER 13 / FAIL 0 / DEFERRED_ENV 0
- 위 실연동 WAITING_USER는 계획된 인증 필요성을 표시하며, 해당 구현이 준비되었다는 뜻이 아니다.
- 누락·추가 Task: P11 감사에서 BUG-013~015를 기존 Task의 미완료 항목으로 기록했다.

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
| P00-T05 | 모드·비밀정보·설정 격리 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P00-T05 | - |
| P01-T01 | 공통 모델·오류·상태 schema | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T01 | - |
| P01-T02 | Bridge wire protocol·공용 fixture | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T02 | - |
| P01-T03 | SDK 상태기계·Provider interface | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T03 | - |
| P01-T04 | 결정적인 Fake Provider | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T04 | - |
| P01-T05 | Native HTTP·저장소·세션 소유권 기반 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T05 | - |
| P02-T01 | Backend·PostgreSQL·migration 기동 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T01 | - |
| P02-T02 | Mock 사용자·opaque 세션·갱신 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T02 | - |
| P02-T03 | 상품·재화·구매 원장 서비스 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T03 | - |
| P02-T04 | purchase 재시도·finalization queue | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T04 | - |
| P02-T05 | device token·config·개발 푸시 API | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T05 | - |
| P02-T06 | 로컬 Backend 통합 smoke 명령 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T06 | - |
| P03-T01 | Kotlin SDK의 LOCAL_MOCK 수직 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T01 | - |
| P03-T02 | Swift SDK의 LOCAL_MOCK 수직 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T02 | - |
| P03-T03 | Android JNI 왕복 transport | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T03 | ENV-002 |
| P03-T04 | Swift C ABI 왕복 transport | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T04 | ENV-002 |
| P03-T05 | Unity facade·dispatcher·request registry | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T05 | ENV-002 |
| P03-T06 | Unity 최소 Demo·Native 경로 분기 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T02 | ENV-002 |
| P04-T01 | 실제 Android Google 로그인 adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P04-T01 | USER-AUTH-GOOGLE |
| P04-T02 | 실제 iOS Apple 로그인 adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P04-T02 | USER-AUTH-APPLE |
| P04-T03 | 서버 실제 identity 검증·nonce 재사용 방어 | IMPLEMENTED | PASS | WAITING_USER | docs/evidence/p04-t03-identity-verifier.md | USER-AUTH-GOOGLE, USER-AUTH-APPLE |
| P04-T04 | 세션 복원·single-flight 갱신·로그아웃 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P04-T04 | - |
| P04-T05 | 인증 Native·Unity 소비자 통합 | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P04-T05 | USER-AUTH-GOOGLE, USER-AUTH-APPLE |
| P05-T01 | 구매 상태·account binding 계약 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P05-T01 | - |
| P05-T02 | 실제 Google Play Billing adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P05-T02 | USER-BILLING-GOOGLE |
| P05-T03 | StoreKit 2·로컬 .storekit 시나리오 | IN_PROGRESS | FAIL | WAITING_USER | WORK_LOG P05-T03 | USER-BILLING-APPLE, ENV-STOREKIT-26 |
| P05-T04 | 실제 Google·Apple 구매 검증 서버 | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P05-T04 | USER-BILLING-GOOGLE, USER-BILLING-APPLE |
| P05-T05 | 지급 원자성·동시성·서버 finalizer 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P05-T05 | - |
| P05-T06 | Native 복구·store finish·timeout 이후 처리 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P05-T06 | - |
| P05-T07 | Unity·Native 상점 완성 | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P05-T07 | USER-BILLING-GOOGLE, USER-BILLING-APPLE |
| P06-T01 | 실제 FCM 등록·수신·권한 adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T01 | USER-PUSH-GOOGLE |
| P06-T02 | Swift APNs 등록·Host forwarding | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T02 | USER-PUSH-APPLE |
| P06-T03 | Unity iOS Push Host Adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T03 | USER-PUSH-APPLE, ENV-002 |
| P06-T04 | Backend FCM·APNs 실제 sender | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T04 | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P06-T05 | 수명주기·콜드스타트·클릭 라우팅 | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T05 | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P07-T01 | 진단·redaction·점검 설정 완성 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T01 | - |
| P07-T02 | 세 샘플 전체 사용자 흐름 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T02 | ENV-002 |
| P07-T03 | 연동 문서·오류·소유권 가이드 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T03 | - |
| P07-T04 | 구현 누락 1차 점검 | IN_PROGRESS | PARTIAL | N/A | docs/FEATURE_MATRIX.md, WORK_LOG P07-T04 | - |
| P08-T01 | Android Maven 산출물·소비 build | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P08-T01 | - |
| P08-T02 | Swift Package·static XCFramework 산출물 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P08-T02 | - |
| P08-T03 | UPM staging·멱등 build hook | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P08-T03 | ENV-002 |
| P08-T04 | 신규 Unity 프로젝트 재설치 검증 | IN_PROGRESS | DEFERRED_ENV | N/A | WORK_LOG P08-T04 | ENV-002 |
| P08-T05 | 기능 개발 기준점 고정 | IN_PROGRESS | PARTIAL | N/A | docs/evidence/feature-baseline.md, WORK_LOG P08-T05 | ENV-002, ENV-STOREKIT-26 |
| P09-T01 | 후반 하네스 manifest·공통 contract test | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T01 | - |
| P09-T02 | Core·Bridge 회귀·실패 주입 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T02 | ENV-002 |
| P09-T03 | 인증·세션·개발모드 차단 회귀 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T03 | - |
| P09-T04 | 구매·DB 동시성·복구 회귀 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T04 | - |
| P09-T05 | Push·Lifecycle·패키징 회귀 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T05 | ENV-002 |
| P09-T06 | 검증 집계·진행 원장 강제 검사 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T06 | - |
| P09-T07 | CI 설정·플랫폼 lane 분리 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T07 | ENV-002 |
| P09-T08 | Fail-closed 하네스 자체 시험 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P09-T08 | - |
| P10-T01 | 검증 기준 유지하며 Core·Bridge 리팩토링 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T01 | ENV-002 |
| P10-T02 | 인증·결제·푸시 책임과 보안 정리 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T02 | - |
| P10-T03 | 측정 기반 수명주기·메모리·응답 확인 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T03 | ENV-002 |
| P10-T04 | 리팩토링 후 재패키징·호환성 재검증 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T04 | ENV-002 |
| P11-T01 | 전체 Task·TODO·계약 누락 최종 감사 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T01 | - |
| P11-T02 | 사용자 설정·실연동 재개 runbook 완성 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T02 | - |
| P11-T03 | 최종 문서·release candidate 로컬 패키지 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T03 | - |
| P11-T04 | 마지막 검증·커밋·인계 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T04 | - |

## 블로커 원장

| ID | 유형 | 영향 Task | 실제 증상/실행 명령 | 코드 개발 지속 방법 | 해소 조건 | 상태 |
|---|---|---|---|---|---|---|
| USER-PUSH-CONCURRENCY | USER | P06-T04 | 기본 동시 1건 사용자 선택 | scheduler 설정·검증 진행 | 실제 원격 발송은 별도 | RESOLVED |
| USER-CONFIG-TTL | USER | P07-T01 | 기본 유효기간 5분 사용자 선택 | 서버 설정·local-mock 통합 진행 | 실제 플랫폼 검증은 별도 | RESOLVED |
| BUG-016 | BUG | P04-T04, P09-T03 | Native 실제 Provider의 profile 확인 이후 요청 401에서 refresh 누락 | Android/iOS 단일 refresh·1회 재시도 및 proof idempotency 유지 구현 | fake 동시 요청·계정 변경·반복 401·증빙 멱등키 검증 | RESOLVED |
| BUG-015 | BUG | P07-T01, P10-T02 | Native 진단 ring의 Unity 공개 조회 구현 및 fake 확인; 실제 Unity player 미검증 | Native typed snapshot과 C# 제한 검사 유지 | 실제 Unity player에서 Native 진단 경계·redaction 확인 | OPEN |
| BUG-014 | BUG | P02-T06, P06-T05 | LOCAL_MOCK Backend→Android·Swift Native 수신은 전용 DB E2E 통과; Unity player·재연결 실제 수명주기 미검증 | 인증·소유권·heartbeat 회귀 유지 | Unity player 전달 및 lifecycle 검증 | OPEN |
| BUG-013 | BUG | P05-T03, P05-T07 | XCODE_STOREKIT iOS 18+에서 이력 단일성·durable attempt로 local DB 응답 유실 복구 확인; Unity·실기기 미검증 | 전용 DB fake 지급과 분리 검증 유지 | 실제 프로세스 종료·Unity player 및 iOS 26.5 실패 재검증 | OPEN |
| BUG-012 | BUG | P04-T04, P10-T02 | Unity가 Native logout의 REVOCATION_UNCONFIRMED를 버려 서버 revoke 불확실성 표시 불가 | 허용된 값만 오류에 보존 | Native/C# fake logout 및 redaction 확인 | RESOLVED |
| BUG-011 | BUG | P08-T01 | Firebase optional dependency가 없는 독립 R8 consumer에서 missing class 실패 | 선택적 runtime 경계 및 consumer shrink 규칙 보강 | Firebase 없는 R8 build와 debug emulator CONFIG_REQUIRED 확인 | RESOLVED |
| BUG-010 | BUG | P07-T01 | 서버 config revision은 16진 hash인데 Unity는 10진 정수 문자열을 요구해 조회 실패 | 서버 revision을 63-bit 10진 문자열로 일치 | 서버 unit 및 local HTTP→Unity decoder 확인 | RESOLVED |
| BUG-009 | BUG | P05-T06 | LOCAL_MOCK 응답 유실 시 transaction/attempt 단서 재시작 보존 누락 | Android emulator Keystore·iOS simulator Keychain 인스턴스 재생성과 local DB 복구 통과 | 실제 기기 프로세스 재시작과 Unity player 복구 검증 | OPEN |
| BUG-008 | BUG | P04-T04 | Android body 없는 form-content logout이 서버 500 | 빈 본문을 media type과 무관하게 처리 | sandbox HTTP 및 Android emulator logout 통과 | RESOLVED |
| BUG-007 | BUG | P07-T02 | Mock과 Google이 동일 Keystore session 항목을 공유할 위험 | 기존 default 보존, sandbox 전용 namespace 사용 | 전용 emulator의 독립 namespace 시험 통과 | RESOLVED |
| BUG-006 | BUG | P08-T01 | 독립 Kotlin consumer JVM 21/Java 17 target 불일치 | JVM 17로 일치 | Kotlin Flow consumer R8 build 통과 | RESOLVED |
| BUG-005 | BUG | P05-T07 | AppleStore와 인증 provider의 Backend 설정 불일치 가능 | 공개 생성 시 전체 설정 일치 강제 | Swift fake unit 통과 | RESOLVED |
| BUG-004 | BUG | P06-T04 | Firebase 의존성 추가 후 오류 응답이 XML로 직렬화 | 오류 content type을 JSON으로 고정 | Backend 일반 suite 재검증 통과 | RESOLVED |
| BUG-003 | BUG | P05-T02 | Play Billing nullable offerToken 컴파일 실패 | 안전한 null 처리 후 재빌드 | AAR 빌드 확인, fake boundary 검증 계속 | RESOLVED |
| BUG-002 | BUG | P04-T01 | googleid 1.2.1 Kotlin metadata 2.4와 compiler 2.1 불일치 | 호환 stable 버전 확인 | 빌드 호환성 확인, adapter fake 검증 계속 | RESOLVED |
| BUG-001 | BUG | P01-T05 | BackendClientTest 1건 실패 | 원인 확인 및 재실행 | HTTP 검증 통과 | RESOLVED |
| USER-VERIFY-CONCURRENCY | USER | P05-T02 | 기본 동시 1건 사용자 선택 | 코드·검증 반영 진행 | 서버 sink 연결 별도 필요 | RESOLVED |
| USER-SESSION-TTL | USER | P04-T04 | 최초 로그인부터 7일 고정 사용자 선택 | 기존 코드와 대조·검증 진행 | 실제 인증 검증 별도 필요 | RESOLVED |
| USER-PUSH-RETENTION | USER | P02-T05 | 사용자 결정: 등록 해제·로그아웃 시 해당 토큰 즉시 삭제 | local-mock 세션별 삭제와 경쟁 상황 검증 완료 | 실제 FCM/APNs 경로 별도 구현 | RESOLVED |
| USER-RETRY | USER | P02-T04 | 사용자 결정: 동시 1개, 5초 시작 지수 백오프 | local-mock worker·재시작·동시성 검증 완료 | 실제 store finalizer 별도 구현 | RESOLVED |
| ENV-STOREKIT-26 | ENV | P05-T03 | iOS 26.5 simulator SKTestSession 설정 저장 Code 3 및 상품 조회 실패; 별도 iOS 18.6 전용 simulator 상품 조회 1건 통과 | 다른 독립 구현 진행; 실패 시험 보존 | 호환 환경에서 StoreKit local 재시험 | OPEN |
| ENV-008 | ENV | P04-T04 | 전용 PostgreSQL container 정상 종료 상태에서 opt-in DB 시험 실패 | 기존 volume 보존 후 재기동 | DB healthy 및 실패 시험 재실행 | RESOLVED |
| ENV-005 | ENV | P03-T02 | Simulator UI snapshot 대상 0개, 수동 대체 입력으로도 흐름 미확인 | XCTest 기반 독립 UI 검증 시도 | iOS local-mock UI smoke 실행 확인 | RESOLVED |
| ENV-004 | ENV | P03-T01 | 전용 emulator 복원 시험에서 화면 준비 전 입력 실패 | UI 준비 후 재시도 | Keystore 복원 확인 | RESOLVED |
| ENV-003 | ENV | P00-T03 | XcodeGen 최초 부재 | 로컬 도구 2.46.0 확보 후 프로젝트 생성·빌드 확인 | 실제 스토어 및 Unity 검증 별도 | RESOLVED |
| ENV-002 | ENV | P00-T03 및 Unity 검증 | Unity Editor 생성 시 라이선스 확인 실패, 종료 198 | 프로젝트 생성 안내 스크립트 제공, 다른 플랫폼 계속 | 사용자 라이선스 및 Editor 재확인 | OPEN |
| ENV-001 | ENV | P00-T02 | Unity 6.3 LTS 미설치; 설치 버전의 모듈·라이선스 미확인 | 설치된 Editor로 검증 시도 | 호환 Editor와 모듈·라이선스 확인 | OPEN |

유형: USER=사용자 계정·서명·콘솔, ENV=설치/실행환경, BUG=내부 버그, DEP=선행 구현 미해결. 같은 사건은 중복 ID를 만들지 않고 영향 Task를 추가한다. 사용자 인증 필요성은 USER_SETUP에 이미 계획되어 있지만 실제 구현 준비 여부는 개발 중 갱신한다.

## 기능별 검증 매트릭스

| 기능 | Android 코드/빌드 | iOS 코드/빌드 | Unity Editor | Unity Android | Unity iOS | 실제 외부 서비스 |
|---|---|---|---|---|---|---|
| Core·Bridge | BUILD:PASS / LOCAL_MOCK:PARTIAL | BUILD:PASS / LOCAL_MOCK:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | N/A |
| 인증 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 결제 | BUILD:PASS / MOCK:PARTIAL | BUILD:PASS / MOCK:PARTIAL / STOREKIT_LOCAL:FAIL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 푸시 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 세션·복구 | EMULATOR:PARTIAL | SIMULATOR:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 배포·신규 소비 | MAVEN_CONSUMER:PASS | XCFRAMEWORK_CONSUMER:PASS | UPM_IMPORT:NOT_RUN | NOT_RUN | NOT_RUN | N/A |

각 칸은 가능한 경우 `BUILD:PASS / RUN:WAITING_USER`처럼 분리한다. “Android 완료” 한마디로 Native standalone과 Unity Android를 합치지 않는다.

## 완료/미완료 요약

- 일부 계약·빌드·가짜 Provider·로컬 DB 회귀 및 독립 패키지 소비 검증 통과. 개별 범위와 명령은 WORK_LOG 참조.
- 인증·결제·푸시·복구의 실제 플랫폼 및 Unity 통합 검증은 미완료. 외부 인증·서명·콘솔 설정은 USER_SETUP 참조.
- 내부 미구현: Xcode StoreKit 전체 지급 경로, Mock 푸시의 실제 Unity 전달 검증, Native 진단의 실제 Unity 검증. BUG-009 실제 재시작 검증도 미완료.
- 환경 대기: Unity 라이선스 및 호환 Editor, StoreKit local simulator 실패. P09 하네스에는 미구현·부분 시나리오가 남아 전체 검증은 실패 상태.
- 범위 제외: Windows/C++·Unreal/Godot·구독·환불 자동화·RTDN/Server Notifications 운영·관리자 웹·Kubernetes·상용 배포.

## 최근 체크포인트 이력

| 시각 | Phase/Task | 구현 요약 | 검증 | 다음 행동 |
|---|---|---|---|---|
| 초기 문서 생성 | P00-T01 이전 | 계획만 작성됨 | 실행 없음 | 저장소 조사 |


- P09-T04 R34 블로커: 테스트 앱에서 StoreKitTest 모듈 검색 실패로 첫 빌드 FAIL. Xcode simulator SDK 개발자 프레임워크 경로를 확인하고 재검증한다.
- P09-T04 R34 테스트 앱은 simulator SDK의 개발자 framework 검색 경로 지정 후 빌드 PASS. 프로세스 종료·재시작 실행은 아직 미검증이다.
- P09-T04 R34 실행 검증 시작: 전용 DB·simulator에서 로컬 commit 이후 앱 강제 종료와 새 프로세스 복구를 확인한다.
- P09-T04 R34 실행 FAIL: runner가 XcodeGen 진단 stderr를 프로젝트 경로 stdout과 합쳐 빌드 경로가 잘못됐다. 앱 실행 전 실패이며 경로 파싱을 수정한다.
- P09-T04 R34 경로 파싱 수정 후 전용 환경에서 재검증 시작.
- P09-T04 R34 전용 simulator 실행 FAIL: 테스트 앱이 INTERNAL_ERROR를 보고해 종료·재시작 복구는 미검증이다. 테스트 단계별 진단을 추가해 원인을 확인한다.
- P09-T04 R34 단계 진단 추가 후 재검증 시작.
- P09-T04 R34 준비 프로세스는 서버 잔액 100·pending 기록을 확인하고 실제 종료됐다. 재시작 프로세스의 실패 지점은 현재 진단이 여러 호출을 묶어 식별되지 않아 복구는 FAIL 유지한다.
- P09-T04 R34 복구 단계 세분화 후 재검증 시작.
- P09-T04 R34 실제 프로세스 재시작 FAIL (`artifacts/xcode-process-recovery-b49vwcfs`): 재시작 후 서버 잔액 100, unfinished 0이지만 Keychain journal이 남았다. Xcode 테스트 세션의 프로세스 간 거래 이력 유지 여부와 복구 조건을 추가 조사해야 하며 완료 처리하지 않는다.
- P09-T04 R34 커밋 준비: 재현 하네스와 실패 기록을 로컬 저장한다. R34는 PARTIAL 유지.
