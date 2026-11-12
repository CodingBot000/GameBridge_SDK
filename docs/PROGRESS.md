# GameBridge SDK 진행 원장

> 각 Task 시작·검증·블로커·커밋 전에 갱신한다.

## 현재 체크포인트

- 전체 상태: IN_PROGRESS (작업 미완료)
- 현재 Phase / Task: PX-T07 / Unity iOS LOCAL_MOCK E2E 통과 후 결과 정리
- 마지막 갱신 시각: 2026-11-12 (Asia/Seoul)
- 마지막 검증된 소스 커밋: 8732333 (Unity iOS LOCAL_MOCK E2E PASS; 실제 Apple 제공자·스토어 미검증)
- 현재 작업 트리 상태: 진행 문서 갱신 중; Unity 미완성 Demo와 Python 캐시 미추적 보존
- 현재 실행 모드: LOCAL_MOCK 및 격리된 fake 시험; 실제 provider 미실행
- 바로 다음 행동: PX-T07 증거·문서를 정리하고 Apple 로그인·실제 스토어·APNs·Unity push/lifecycle을 별도 미검증으로 유지
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
| BUG-013 | BUG | P05-T03, P05-T07 | XCODE_STOREKIT iOS 18.6 local DB 및 프로세스 재시작 복구 PASS; Unity·실기기 미검증 | 전용 DB fake 지급과 분리 검증 유지 | Unity player·실기기 및 iOS 26.5 실패 재검증 | OPEN |
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
| ENV-002 | ENV | P00-T03 및 Unity 검증 | 과거 Unity 라이선스 비활성 및 Android 모듈 부재 | Unity 6000.5.8f1 라이선스·Android 모듈 준비 확인, Unity Android local-mock Player 실행 | Unity iOS 및 나머지 테스트 별도 | RESOLVED |
| ENV-001 | ENV | P00-T02 | Unity 6.3 LTS 미설치; 설치 버전의 모듈·라이선스 미확인 | 설치된 Editor로 검증 시도 | 호환 Editor와 모듈·라이선스 확인 | OPEN |

유형: USER=사용자 계정·서명·콘솔, ENV=설치/실행환경, BUG=내부 버그, DEP=선행 구현 미해결. 같은 사건은 중복 ID를 만들지 않고 영향 Task를 추가한다. 사용자 인증 필요성은 USER_SETUP에 이미 계획되어 있지만 실제 구현 준비 여부는 개발 중 갱신한다.

## 기능별 검증 매트릭스

| 기능 | Android 코드/빌드 | iOS 코드/빌드 | Unity Editor | Unity Android | Unity iOS | 실제 외부 서비스 |
|---|---|---|---|---|---|---|
| Core·Bridge | BUILD:PASS / LOCAL_MOCK:PARTIAL | BUILD:PASS / LOCAL_MOCK:PARTIAL | IMPORT:PASS / TEST:NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | N/A |
| 인증 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | WAITING_USER |
| 결제 | BUILD:PASS / MOCK:PARTIAL | BUILD:PASS / MOCK:PARTIAL / STOREKIT_LOCAL:FAIL | NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | WAITING_USER |
| 푸시 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 세션·복구 | EMULATOR:PARTIAL | SIMULATOR:PARTIAL | NOT_RUN | NOT_RUN | NOT_RUN | WAITING_USER |
| 배포·신규 소비 | MAVEN_CONSUMER:PASS | XCFRAMEWORK_CONSUMER:PASS | UPM_IMPORT:PASS | IL2CPP:PASS | SIM_IL2CPP:PASS | N/A |

각 칸은 가능한 경우 `BUILD:PASS / RUN:WAITING_USER`처럼 분리한다. “Android 완료” 한마디로 Native standalone과 Unity Android를 합치지 않는다.

## 완료/미완료 요약

- 일부 계약·빌드·가짜 Provider·로컬 DB 회귀 및 독립 패키지 소비 검증 통과. 개별 범위와 명령은 WORK_LOG 참조.
- Unity Android 및 iOS Simulator LOCAL_MOCK 인증·구매는 통과했으나 실제 플랫폼·실기기·푸시·복구 전체 검증은 미완료. 외부 인증·서명·콘솔 설정은 USER_SETUP 참조.
- 내부 미완료: Xcode StoreKit 실제 기기 및 Unity 복구 검증, Mock 푸시의 실제 Unity 전달 검증, Android LOCAL_MOCK 외 Native 진단의 Unity 검증. BUG-009 실제 기기 재시작 검증도 미완료.
- 환경 대기: 계획된 Unity 6.3 LTS 및 Unity iOS 등 잔여 환경, StoreKit local simulator 실패. P09 하네스에는 미구현·부분 시나리오가 남아 전체 검증은 실패 상태.
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
- P11 누락 감사 시작: 계획의 최종 산출물과 현재 구현·검증 기록을 대조하고 누락된 변경 이력을 작성한다. 실제 플랫폼 및 실패 항목은 별도로 유지한다.
- P08-T01/T02/T03 재패키징 시작: 최근 인증 수정이 기존 산출물에 반영되지 않아 새 경로에서 Android·iOS·UPM을 다시 빌드한다. 기존 결과는 보존한다.
- P08 Android 최신 소스 로컬 Maven 및 독립 R8 consumer 재빌드 PASS (45 tasks). 실제 스토어와 Unity 실행은 미검증이다. iOS XCFramework 빌드 검증을 시작한다.
- P08 최신 iOS device/simulator XCFramework 및 arch별 C ABI 4개 검사 PASS, 새 UPM staging checksum PASS. Unity import·실기기는 미실행. P09 strict runner가 최신 산출물을 선택하도록 수정한다.
- P09 strict-local 재검증 시작: 최신 Maven·XCFramework·UPM 경로를 명시하고 전용 DB·simulator를 사용한다. 기존 실패 및 미실행은 성공으로 승격하지 않는다.
- P11 문서 감사: 누락된 CHANGELOG를 추가하고 R34 실제 재시작 실패와 최신 패키지 범위를 FINAL_REPORT에 반영했다. strict 실행은 진행 중이다.
- P11 진행 요약의 오래된 Xcode 지급 미구현 문구를 실제 구현·재시작 실패 상태로 정정했다. runner Python 문법 검사 PASS.
- P09-T04 R34 원인 조사 재개: 재시작 전후 StoreKit 이력·unfinished 노출 건수만 기록해 세션 이력 소실과 SDK 처리 실패를 구분한다. 증빙 원문과 식별자는 기록하지 않는다.
- P09-T04 R34 이력 노출 계측 추가. 재현 검증은 strict suite 종료 후 실행한다.
- P09-T04 재현 runner의 sourceDirty 보고를 실제 git 상태로 기록하도록 보완했다.
- P09-T04 R34 이력 노출 계측 재검증 시작: 새 전용 simulator 및 DB를 사용한다.
- P09 최신 strict-local 전체 FAIL (`artifacts/verify-all-2cnr0y99`, source 2bc9d77 + 작업 트리 변경): 실행된 contract·auth·purchase·Native mock push·패키지 검사는 PASS이나 시나리오 PARTIAL, Unity Editor NOT_RUN, Unity push DEFERRED_ENV 및 기존 실패가 남았다. 외부 13개 WAITING_USER.
- P09-T04 R34 재검증 FAIL (`artifacts/xcode-process-recovery-b7metfgc`): 새 프로세스 시작 시 StoreKit history 1·unfinished 1이 확인됐고 이후 잔액 100·unfinished 0·journal 잔존. 이력 미노출 가설은 반박됐으며 중복 처리 경합을 조사한다.
- P09-T04 조사: listener가 거래 finish 후 journal 정리를 비동기로 마치는 동안 테스트가 즉시 검사했을 가능성이 있어, 안전한 유한 대기로 실제 최종 상태를 확인한다.
- P09-T04 R34 유한 대기 후 최종 journal 상태 재검증 시작.
- P09-T04 R34 유한 대기 재검증도 FAIL (`artifacts/xcode-process-recovery-7j8jui66`): 10초 후에도 journal이 남아 단순 검사 시점 문제로 설명되지 않는다.
- P09-T04 원인 조사: 테스트 Keychain 저장·삭제 호출 횟수와 실패 여부만 계측해 journal 정리 미호출과 저장소 오류를 구분한다.
- P09-T04 Keychain 호출 계측 재검증 시작.
- P09-T04 계측 재검증 FAIL (`artifacts/xcode-process-recovery-oz3ycsw7`): 복구 프로세스에서 clear 성공 1회 뒤 save 1회가 추가로 발생해 중복 transaction 처리로 journal이 다시 생성됨을 확인했다. finish된 거래는 새 attempt를 만들지 않도록 보강한다.
- P05-T05/P09-T04 검증 시작: Xcode local 중복 처리에서 이미 finish된 거래의 새 journal 생성 차단과 기존 local DB 회귀를 확인한다.
- P09-T04 R34 Xcode local 별도 프로세스 종료·재시작 재시험 PASS (`artifacts/xcode-process-recovery-vm_w1hpt`): 서버 잔액 100 유지, unfinished 및 journal 정리 확인. 실기기·Unity·Apple sandbox는 미검증. 기존 회귀를 추가 실행한다.
- R34 검증 강화: 이미 대기 중인 중복 전달까지 확인하도록 정리 후 1초 관찰 및 새 journal 저장 0회 assertion을 추가했다. 추가 실행 전에는 이 강화된 조건을 통과로 기록하지 않는다.
- P05-T05 iOS Swift unit 회귀 검증 시작. Xcode local DB 회귀는 별도로 진행 중이다.
- iOS Swift package regression PASS: 77 tests, 7 skip, 0 failure (macOS host; 실제 StoreKit simulator 대체 아님).
- P09-T04 강화된 R34 재검증 시작: 정리 후 추가 관찰과 journal 재생성 0회를 확인한다.
- P05-T05 기존 Xcode local DB 응답 유실·journal 복구 회귀 PASS (`artifacts/xcode-storekit-e2e-lk2ae3ys`, 1 test). 강화된 프로세스 시험은 진행 중.
- 강화된 R34 시험 PASS (`artifacts/xcode-process-recovery-f_w2fsya`): 재시작 후 journal 제거 뒤 1초 관찰 및 새 journal 저장 0회 포함. strict 및 R34 manifest에 이 실제 로컬 시나리오를 연결한다.
- P09 R34 시나리오·strict 필수 lane 연결 검증 시작: 누락 시 PASS로 집계하지 않는다.
- P09 manifest 검증 명령 경로 오류로 미실행(exit 2). 실제 runner 경로를 확인해 재실행한다.
- P09 manifest 실제 검사 및 누락 음성 검증 시작.
- 집계 unit 검증은 실행됐으나 진행 원장 검증에 잘못된 파일 경로를 사용해 해당 검사는 미실행이다. 올바른 명령을 확인한다.
- P09/P11 진행 원장 실제 검사 시작.
- P09/P11 manifest·음성·집계 13건·진행 원장 검사 PASS. R34 local 시나리오는 IMPLEMENTED이며 실제 기기·Unity는 미검증. 커밋 후 수정 제품 소스로 패키지를 다시 생성한다.
- P08-T02/T03 최신 패키지 재생성 시작: e9b64fb iOS 수정 반영. Android 소스는 2bc9d77 이후 변경 여부를 확인해 재사용 가능성을 판단한다.
- P08 iOS e9b64fb device/simulator XCFramework archive PASS. Android 제품 소스는 2bc9d77 이후 변경 없어 독립 R8 검증된 Maven을 재사용한다. UPM staging 및 무결성 검증을 시작한다.
- P08 e9b64fb XCFramework arch·C ABI 및 UPM checksum PASS. Unity import와 실기기는 미실행이다. P09 새 필수 R34 lane을 포함한 strict 재검증을 시작한다.
- P09-T03 R20 offline logout 시나리오 감사 시작: Android·iOS 및 Unity의 로컬 token 삭제와 서버 revoke 불확실성 전달 증거를 대조한다.
- R20 감사: Android/iOS Native fake가 서버 revoke 실패 시 로컬 저장 삭제와 REVOCATION_UNCONFIRMED를 각각 검증하며 최근 strict에서 해당 두 suite가 PASS했다. 실제 기기·Unity는 별도다. 진행 중 strict 종료 후 manifest를 갱신한다.
- P09-T02 R09 UTF-8 복사 증거 감사 시작: C ABI와 JNI 각각의 한글·emoji 수명 검증을 분리해 확인한다.
- R09 감사: iOS C ABI 한글·emoji 복사 시험은 존재하지만 Android 실제 JNI 경계 수명 검증은 확인되지 않아 PARTIAL 유지한다.
- P09-T05 R40 권한 거부 시나리오 감사 시작: OS 권한 응답과 등록·표시 상태를 검증한 범위를 확인한다.
- R40 감사: Native fake의 허용 경로 외 OS 권한 거부 후 등록·표시 상태 실행 근거를 찾지 못해 PARTIAL 유지한다.
- P09-T02 R22 민감정보 노출 시나리오 감사 시작: 로그와 Unity 결과 경계의 검증 범위를 확인한다.
- R22 감사 검색에 존재하지 않는 glob을 사용해 명령이 실행되지 않았다. 경로를 수정해 계속한다.
- R22 감사: Android bridge·iOS C bridge 등 개별 synthetic redaction assertion은 있으나 전체 로그 및 실제 Unity 결과에 대한 실행 범위는 부족해 PARTIAL 유지한다.
- P11 FINAL_REPORT에 e9b64fb 패키지와 Android 무변경 재사용 근거를 추가했다. strict 결과는 실행 완료 후 갱신한다.
- P09 strict-local `artifacts/verify-all-k8z14qqw` 전체 FAIL: 새 R34 프로세스 복구 포함 실행된 Native synthetic·local DB·패키지 검사는 PASS. Unity Editor NOT_RUN, Unity push DEFERRED_ENV, 시나리오 PARTIAL 및 기존 실패로 전체 통과가 아니다. 외부 13개 WAITING_USER.
- P09 R20 Native fake 증거에 맞춰 manifest를 IMPLEMENTED로 연결하고 검사 시작한다. 실제 기기·Unity 검증을 의미하지 않는다.
- P09 R20 manifest·누락 음성·진행 원장 검사 PASS. strict는 R20 매핑 전 실행이며 전체 FAIL 상태는 변함없다. 커밋 준비 후 남은 시나리오를 계속 검토한다.
- P11-T01 소스 TODO·미구현 재감사 시작: 실제 provider와 제품 경로의 미완성 표시를 찾아 기존 원장과 대조한다.
- P11 제품 소스 TODO/FIXME·명시 미구현 표식 검색에서 추가 표식 없음. 이는 기능 완성 증거가 아니며 기존 미검증·부분 항목은 유지한다.
- P08-T02 最新 iOS XCFramework 독립 Swift consumer link 검증 시작. Unity 및 실제 기기 실행과 구분한다.
- P08 e9b64fb iOS simulator slice 독립 Swift consumer link PASS (`artifacts/ios-consumer-e9b64fb`). 실행·Unity·서명된 기기는 미검증이다.
- P11 문서·산출물 검사와 커밋 준비: source TODO 감사 결과와 최신 독립 iOS link 범위를 저장한다.
- P11-T02 외부 설정 점검 재검증 시작: 실제 인증·발송·결제를 수행하지 않는 설정 확인만 실행한다.
- P11-T02 설정 형태 확인 exit 2: 인증 audience, Google/Apple 구매, FCM/APNs 및 구매·푸시 암호화 키가 누락 또는 유효하지 않다. 실제 provider 시험은 NOT_RUN이며 USER_SETUP 대기다.
- P11-T02 커밋 준비: 설정 확인 결과와 사용자 준비 대기를 기록한다. 외부 설정은 수정하지 않았다.
- P05-T03 iOS 26.5 재검증 시작: 전용 simulator에서 현재 Xcode 로컬 앱 재시작 시험을 실행해 기존 StoreKit Code 3 실패가 유지되는지 확인한다. 기존 simulator·설정은 보존한다.
- P05-T03 iOS 26.5 전용 재검증 FAIL (`artifacts/xcode-process-recovery-ifyufa3n`): 테스트 앱 prepare 상태 보고가 제한시간 내 오지 않았다. Code 3 재현 여부는 확인되지 않았으며 기존 실패는 유지한다.
- P05-T03 runtime 선택 runner 문법 검사 PASS. 커밋 준비: iOS 26.5 재실행은 timeout FAIL로 남긴다.
- P05-T03 timeout 원인 조사 시작: 테스트 앱 진행 단계만 기록해 어디에서 멈추는지 확인한다. 거래 증빙과 인증값은 기록하지 않는다.
- P05-T03 단계 checkpoint 적용 후 iOS 26.5 timeout 위치 재검증 시작.
- P05-T03 iOS 26.5 재시험 FAIL (`artifacts/xcode-process-recovery-p8qyld6o`): SKTestSession 생성 중 prepare timeout. 기존 Code 3과 동일 원인인지는 미확정. checkpoint 변경 후 iOS 18.6 양성 대조를 확인한다.
- P05-T03 동일 계측 iOS 18.6 양성 대조 PASS (`artifacts/xcode-process-recovery-2jktejkt`). iOS 26.5 SKTestSession timeout은 별도 FAIL 유지한다.
- P05-T03 커밋 준비: 26.5 timeout 단계와 18.6 대조 결과 및 테스트 checkpoint만 기록한다.
- P09-T03 R20 Native 타깃 회귀 재검증 시작: Android·Swift 오프라인 로그아웃 단일 테스트를 각각 실행한다.
- R20 Android 타깃 실행 FAIL: ANDROID_HOME 미지정으로 SDK 위치를 찾지 못해 테스트는 미실행. 설치 경로를 설정해 재실행한다.
- R20 Android SDK 경로 지정 후 재검증 시작.
- R20 Android 단일 synthetic 테스트 PASS. Swift 단일 회귀 검증을 시작한다.
- R20 Android·Swift 타깃 synthetic 회귀 각각 1건 PASS, skip 0. 실제 네트워크·Unity 검증은 아니다.
- P09-T03 커밋 준비: R20 타깃 테스트와 최초 환경 오류를 증거에 기록한다.
- P09-T02 R09 환경 조사: 연결된 Android 기기가 없고 사용자의 기존 AVD만 확인됐다. Unity AndroidJavaProxy 경계를 실제 검증할 별도 환경과 라이선스는 미준비이므로 JNI 실행 PASS로 기록하지 않는다.
- P11 원장·manifest·음성 검사 PASS. 커밋 준비: 남은 환경 제한과 다음 검증 경로를 기록한다.
- 저장소 공개 요청: 추적 변경은 모두 커밋됐으며 Git 전체 이력 1,690개 blob의 일반적인 인증키·개인키 패턴 검사에서 의심 항목 0건. 기존 미추적 Unity Demo 및 Python 캐시는 보존한다. 공개 저장소 생성·푸시 전 로컬 기록 커밋을 준비한다.
- PX-T01 Unity Android LOCAL_MOCK 통합 재개: Unity 라이선스·Editor·Android 모듈과 실제 소비 경로를 확인한다. Native Player 전체 실행은 아직 NOT_RUN이다.
- PX-T01 환경 블로커: Unity CLI는 로그인 상태이나 활성 라이선스 0개다. 설치된 Editor 6000.5.8f1·6000.4.0f1에 Android Build Support가 확인되지 않았고 ADB 기기 0개다. Player 실행은 NOT_RUN이며 사용자 라이선스 작업을 우회하지 않는다.
- PX-T01 독립 작업 시작: 활성화 후 바로 실행할 수 있도록 별도 Unity Android LOCAL_MOCK 소비 프로젝트 생성기와 검증용 시나리오를 준비한다. 기존 사용자 Demo는 변경하지 않는다.
- PX-T01 소비 프로젝트 생성기 초안 작성: Android Player에서만 실행되는 LOCAL_MOCK 시나리오, Native 진단 request ID, 서버 잔액 증가 assertion과 격리 Android manifest를 준비했다. Unity 실행·컴파일은 아직 미검증이다.
- PX-T01 생성기 로컬 검증 PASS: `artifacts/unity-android-mock.uv2IER/project` 생성, staged UPM 110개 파일 체크섬 확인. Unity 실행은 NOT_RUN. 시나리오 C#을 실제 Unity managed reference로 컴파일 검증한다.
- PX-T01 Unity managed reference 컴파일 PASS: Android 조건부 SDK와 시나리오 소스 경고 0·오류 0. 이는 Unity import·JNI·Player 실행 증거가 아니다. Backend 요청 ID의 안전한 검증 경로도 검토한다.
- PX-T01 README의 status/shutdown만 연결됐다는 오래된 설명을 수정하고 사용자 라이선스·Android 모듈 준비 항목을 현 상태로 갱신했다.
- PX-T01 관측 경로 보강 시작: local-mock에서 명시적으로 활성화한 경우에만 핵심 API의 서버 request ID와 상태를 남기고 토큰·요청 본문은 기록하지 않는다.
- PX-T01 Backend tracing 단위 검증 시작: opt-in·profile 제한과 토큰/본문 비노출을 확인한다. 실제 Unity 호출은 아직 없다.
- PX-T01 Backend trace 단위 테스트 PASS: 2건, 실패·skip 0. 이제 격리 local-mock 서버에서 실제 HTTP 응답의 request ID가 안전한 trace와 일치하는지 확인한다.
- PX-T01 Backend 격리 local-mock 실제 HTTP trace PASS (`artifacts/unity-mock-trace-2tz526dj`): 응답 `X-Request-Id`와 서버 로그 일치, synthetic 개발키·DB 비밀번호 비노출. Unity→Kotlin 호출은 아직 NOT_RUN.
- PX-T01 재현 가능한 Android 시나리오 managed compile 명령 검증 시작.
- PX-T01 재현 가능한 managed compile 재검증 PASS(경고 0·오류 0). 격리 소비 프로젝트 빌드 명령은 활성 라이선스 및 Android 모듈 미비 시 실패하도록 작성하며, 현재 환경에서 preflight를 확인한다.
- PX-T01 Player 빌드 preflight는 exit 2로 중단되어 Unity 빌드는 NOT_RUN. CLI가 라이선스 비활성 상태를 JSON으로 반환하면서 비영 종료해 현재 메시지가 부정확하므로 수정한다.
- PX-T01 라이선스 preflight 분류 수정 후 재검증 시작.
- PX-T01 재검증: 라이선스 inactive로 정확히 분류해 exit 2, APK 없음. Unity Player 실행은 여전히 NOT_RUN이다.
- PX-T01 USER_SETUP에 라이선스·Android 모듈·격리 소비 프로젝트·synthetic intent·Backend trace 절차와 NOT_RUN 범위를 기록했다. 실제 기기/에뮬레이터 호출은 하지 않았다.
- PX-T01 소비 프로젝트 생성기·빌드 preflight의 음성 경로와 현재 라이선스 상태를 다시 검증한다. Unity import 및 Player 시험은 여전히 환경 대기다.
- PX-T01 음성 검증 PASS: staging 누락과 비활성 라이선스를 각각 exit 2로 거부하고 APK를 생성하지 않았다. Unity Android LOCAL_MOCK 전체 경로는 환경 대기로 NOT_RUN이다.

### 추가 Task PX-T01

구현 IN_PROGRESS / 로컬 검증 PARTIAL / Unity Android Player NOT_RUN. 소비 프로젝트 생성, managed compile, Backend opt-in trace 및 local HTTP 시험은 확인했다. 활성 Unity 라이선스와 Android Build Support가 없어 실제 Unity import·APK 빌드·JNI·Player 실행은 ENV-002로 대기한다. 기존 P00–P11 항목을 대체하지 않는다.
- PX-T01 커밋 준비: 격리 consumer·trace·README 및 사용자 설정을 저장한다. 실제 Android Player/DB 전체 흐름은 NOT_RUN으로 유지한다.
- PX-T02 전용 Android 에뮬레이터 준비 시작: 기존 AVD를 수정하지 않고 새 테스트 인스턴스를 만들어 ADB 연결을 확인한다. Unity Player 빌드는 라이선스·모듈 대기로 남는다.
- PX-T02 새 전용 AVD 생성 및 config 확인 PASS. 에뮬레이터 기동·ADB 연결을 검증한다.
- PX-T02 첫 에뮬레이터 백그라운드 기동은 프로세스가 종료돼 ADB 연결 미확인이다. 대기 작업을 중단하고 관리되는 세션에서 재시도한다.
- PX-T02 관리 세션의 전용 emulator 기동 재검증 시작.
- PX-T02 전용 Android 36 에뮬레이터 부팅·ADB 연결 PASS. Unity APK와 Native 통합 실행은 아직 NOT_RUN이다. 에뮬레이터에서 로컬 host 연결 가능 여부를 검증한다.
- PX-T02 전용 Android 에뮬레이터의 `10.0.2.2` host TCP 연결 PASS. SDK·Backend·Unity 호출은 하지 않았으며 Player 통합은 NOT_RUN 유지한다.
- PX-T02 커밋 준비: 격리 AVD 및 host 연결 결과를 기록한다. 실제 실행은 Unity 라이선스와 Android 모듈 준비 뒤 이어간다.
- PX-T03 독립 Android Native bridge 대조 검증 시작: 전용 에뮬레이터에서 Kotlin bridge→격리 local Backend 호출을 확인한다. Unity Player를 대체하거나 통과로 표시하지 않는다.
- PX-T03 Kotlin bridge 장치 테스트 작성. 합성 인증값을 명시할 때만 실행하며 실제 Unity Player 여부와 분리한다. Android instrumentation APK 빌드 검증을 시작한다.
- PX-T03 Android instrumentation APK 빌드 PASS. 전용 에뮬레이터와 전용 local DB로 Kotlin bridge 경로 검증을 시작한다. Unity Player는 여전히 NOT_RUN이다.
- PX-T03 전용 Android 에뮬레이터 Kotlin bridge→local Backend PASS (`artifacts/android-mock-bridge-e2e-3xwlhqj0`): 테스트 1건, 서버 trace 및 원장 1건·100코인. Unity·JNI Player 실행은 NOT_RUN이다. Native request ID 증거 수집을 추가한다.
- PX-T03 Native request ID 수집 검증 시작: 기존 테스트 앱은 보존하고 독립한 새 전용 에뮬레이터와 DB에서 재실행한다.
- PX-T03 강화 대조 시험 PASS (`artifacts/android-mock-bridge-e2e-e7bbf_tp`): Kotlin bridge operation별 request ID, 서버 HTTP ID·200 및 전용 DB 원장 1건/100. 두 ID 체계는 별개이며 Unity Player는 NOT_RUN이다.
- PX-T03 커밋 준비: Android Native instrumentation·격리 실행기와 증거를 저장한다. Unity 실행 대기는 유지한다.
- PX-T01 재개 대기: 로그인은 돼 있으나 Unity 활성 라이선스 0개이고 Android Build Support가 없어 Unity import·Player 빌드가 불가하다. 사용자 준비 이후 `docs/USER_SETUP.md`의 PX-T01 절차로 재실행한다. Android Native 대조 시험은 통과했지만 목표인 Unity Player는 NOT_RUN이다.
- PX-T01 문서 재개 지점 커밋 준비: Android Native 대조 결과와 Unity Player NOT_RUN을 분리한다.


### 추가 Task PX-T04 — Unity Android Player E2E 검증 Runner (현재 브랜치)

- 구현: IMPLEMENTED / 실제 Unity Android LOCAL_MOCK Player 검증: PASS ([공개 증거](evidence/px-t04-unity-android-local-mock.md)). 실제 제공자·Unity iOS는 NOT_RUN.
- harness/run-unity-android-mock-e2e.py를 추가했다. 기존 전용 AVD를 확인하고, 새 격리 Unity 소비 프로젝트를 생성하여 UPM staging을 검사한 후 APK를 빌드한다.
- 빌드 이후 별도의 랜덤 local-mock DB 및 Backend를 기동하고 Player를 실행한다. Unity 로그의 initialize/login/products/purchase/wallet/logout PASS, Native 진단 초기화·인증·구매 이벤트, Backend HTTP trace와 DB wallet_ledger 1건·100코인을 **모두** 확인해야 PASS다.
- Unity 6000.5.8f1 import·Android IL2CPP APK 및 전용 Android 36 에뮬레이터에서 LOCAL_MOCK 전체 경로를 검증했다. 첫 전체화면 안내는 수동으로 닫았다. 실제 Provider/스토어와 Unity iOS는 NOT_RUN 유지.
- 원본 로그와 생성 APK는 로컬 artifacts에만 남기며, 전용 AVD·DB를 삭제하지 않는다.

### 추가 Task PX-T05 — Native-only Runner 환경 가변화

- 구현: IMPLEMENTED / 로컬 재실행: NOT_RUN (변경 후).
- 기존 harness/run-android-mock-bridge-e2e.py의 emulator-5598, 사용자 홈 Android SDK 경로, Docker 컨테이너·포트 가정을 CLI/환경변수로 대체했다.
- adb로 현재 연결된 emulator와 GameBridge_V2_ 전용 AVD 이름을 확인하며 기존 com.gamebridge.sample 설치 앱을 보존한다. 재검증 전에는 이전 PX-T03 PASS 증거만 유효하며, 변경 후 재현성은 미검증이다.

### 추가 Task PX-T06 — 공개용 증거 요약과 CI 정적/오프라인 검사

- 구현: IMPLEMENTED / 테스트 실행: NOT_RUN (신규 브랜치).
- harness/export-mock-e2e-evidence.py는 result.json PASS, 소스 HEAD 일치, tracked-clean, 지급 원장 1건·100코인, Unity Player 또는 Native-only 증거를 구분하여 허용된 요약만 생성한다.
- harness/test_export_mock_e2e_evidence.py에 dirty/stale/NOT_RUN/원본 누락·Mock-as-Unity를 거부하는 단위 테스트를 추가하고 .github/workflows/verify.yml의 Linux lane에 Python 문법/해당 테스트를 추가했다. 원격 CI는 아직 실행하지 않았다.
- 실제 새로운 PASS 증거는 존재하지 않는다. docs/evidence/px-t03-android-mock-bridge.md의 기존 실험은 원래 소스/미커밋 상태 그대로 기록하며 새 HEAD의 재현성 PASS로 바꾸지 않는다.
- 최신 공개 증거는 Unity Player 시험 및 Kotlin-only 시험을 각각 다시 실제로 실행한 뒤에만 생성하고 PROGRESS/WORK_LOG/FINAL_REPORT에 반영한다.
- PX-T04 재개 (2026-11-12): origin/fix/unity-android-mock-e2e-evidence 기반 브랜치에서 Unity Android LOCAL_MOCK 전체 검증을 진행한다. 기존 미추적 Demo·캐시는 보존하고 자동 push는 하지 않는다. 현재 Player 결과는 NOT_RUN이다.
- PX-T04 환경 확인(2026-11-12): Unity 6000.5.8f1 활성 라이선스 확인, Android Build Support·SDK·NDK·OpenJDK 및 iOS Build Support 설치 확인. 모듈은 Editor 버전 디렉터리의 `PlaybackEngines`에 있으며, 기존 Android 빌드 스크립트가 `Unity.app/Contents` 아래만 검사하는 경로 오류를 발견해 수정한다. 아직 Player 결과는 NOT_RUN이다.
- PX-T04 빌드 preflight 경로 수정: Unity.app 내부와 Hub 버전 디렉터리 양쪽의 AndroidPlayer를 확인하도록 변경했다. 문법·실제 Player 빌드로 검증할 예정이다.
- PX-T04 preflight 셸 문법 검사 PASS; PX-T06 evidence exporter 단위 테스트 4건 PASS/skip 0. 실제 Unity 빌드는 아직 NOT_RUN. 최신 소스 기준 산출물 및 E2E에 앞서 경로 수정 사항을 로컬 커밋한다.
- P08/PX-T04 최신 소스 패키징 검증 시작: 별도 새 경로에서 Android Maven·iOS XCFramework·UPM staging을 생성하고 버전·무결성을 검사한다. 기존 산출물은 보존한다.
- P08 Android 최신 로컬 Maven·별도 R8 consumer build 종료 0. iOS XCFramework 새 경로 빌드를 시작한다.
- P08 iOS XCFramework device/simulator archive 종료 0. UPM staging·플랫폼 arch/symbol·checksum과 0.1.0-dev 버전 정합성을 확인한다.
- P08 最新 staging `artifacts/upm-v2-20261112-f1e12b6`: Android Maven・独立 R8 consumer、iOS XCFramework device/simulator arch・C ABI、UPM 110개 checksum 및 Maven/UPM 0.1.0-dev 버전 검사 PASS. Unity import/Player는 아직 NOT_RUN이다.
- P08 패키징 기록 커밋 준비: 생성물은 artifacts에 보존하며 Unity Player 실행 전이다.
- PX-T04 실제 Unity Android LOCAL_MOCK E2E 검증 시작: 새 전용 GameBridge_V2_ AVD와 f1e12b6 제품 소스의 검증된 staging을 사용한다. Unity 실행·서버 원장 결과는 아직 NOT_RUN이다.
- PX-T04 첫 전체 실행 FAIL (`artifacts/unity-android-e2e-9qhef6ni`): Unity Android APK 빌드 후 전용 에뮬레이터 설치 단계에서 실패해 Player 및 DB 지급은 미검증이다. 설치 오류 원인을 조사한다.
- PX-T04 설치 원인 확인: 같은 전용 AVD에서 최초 APK의 독립 adb install 재시도는 성공했다. 최초 실패의 상세 출력이 없어 원인은 미확정이며, 기존 설치 앱을 보존하고 다음 시도는 새 전용 AVD에서 수행한다.
- PX-T04 runner의 APK 설치 오류 출력 보존 및 성공 표시 검사 추가. Python 문법 확인 후 새 전용 AVD에서 검증한다.
- PX-T04 runner Python 문법 검사 PASS. 설치 출력 보강과 첫 실패를 기록해 커밋한다. Unity Player 전체 결과는 아직 미검증이다.
- PX-T04 두 번째 전체 검증 시작: 새 전용 AVD에서 수정 runner와 동일한 최신 제품 패키지로 재실행한다. Player 및 원장 결과는 아직 NOT_RUN이다.
- PX-T04 두 번째 전체 실행 FAIL (`artifacts/unity-android-e2e-usi585vl`): 새 전용 AVD에서도 Unity APK 설치 실패. 저장된 adb 설치 로그로 원인을 확인한다. Player 전체 경로는 NOT_RUN이다.
- PX-T04 두 번째 설치 실패 원인 확인: adb 설치 로그에 daemon 재시작 직후 `device emulator-5584 not found`; 이후 같은 AVD는 다시 online으로 확인됐다. 빌드 후 전용 AVD 재확인과 재검색 대기를 추가한다.
- PX-T04 ADB 재검색 대기 및 전용 AVD·기존 앱 재검사 추가. 오프라인→온라인과 잘못된 기기·기존 앱 차단을 단위 검증한다.
- PX-T04 ADB 재검색 단위 검증 2건 PASS/skip 0. 실제 수정 runner의 새 Player 전체 실행 전이며 로컬 커밋한다.
- PX-T04 세 번째 전체 검증 시작: ADB 재검색 수정본을 또 다른 새 전용 AVD와 최신 staging으로 실행한다. 통합 결과는 아직 NOT_RUN이다.
- PX-T04 세 번째 전체 실행 FAIL (`artifacts/unity-android-e2e-8t7go26x`): 새 Unity APK 설치는 진행됐으나 앱 launch 명령에서 실패해 전체 Player 흐름은 미검증이다. 실행 명령과 기기 상태를 조사한다.
- PX-T04 launch 실패 원인: 테스트용 AndroidManifest가 Unity 기본 launcher activity를 덮어써 APK에 MAIN/LAUNCHER가 없었다. 생성된 Unity 6000.5.8f1 GameActivity 템플릿과 대조해 격리 테스트 manifest를 수정한다.
- PX-T04 테스트 소비 프로젝트의 GameActivity launcher 및 Unity metadata를 복원했다. 생성 manifest의 구조 검증 후 새 AVD의 실제 APK·Player로 재검증한다.
- PX-T04 새 소비 프로젝트 manifest 구조 검사 PASS: GameActivity·exported MAIN/LAUNCHER·Unity metadata 존재. 실제 APK 및 Player 검증은 아직 미실행이다. 커밋 후 새 전용 AVD에서 다시 실행한다.
- PX-T04 launcher 수정 후 전체 검증 시작: 새 전용 AVD와 현재 제품 staging을 사용한다. Player 결과는 아직 NOT_RUN이다.
- PX-T04 launcher 수정 후 전체 실행도 launch 단계 FAIL (`artifacts/unity-android-e2e-o8r7vzj4`). APK 설치는 통과했으나 Player 흐름은 미검증이다. APK launcher 및 명령 문법을 확인한다.
- PX-T04 APK 검사 결과 launcher GameActivity 존재. 암시적 `am start`는 intent 해석 실패했으나 같은 전용 앱의 명시적 component 실행은 종료 0·Status ok. harness를 명시적 component 및 실패 로그 redaction으로 수정한다.
- PX-T04 runner를 테스트 APK의 명시적 GameActivity 실행 및 redacted launch 진단으로 수정했다. 문법 검사 후 새 전용 AVD에서 전체 경로를 재검증한다.
- PX-T04 runner 문법 및 ADB 안전 테스트 2건 PASS. 실제 전체 Player 재검증 전 수정 사항을 커밋한다.
- PX-T04 명시적 launcher 수정 후 전체 검증 시작: 별도 새 AVD에서 Unity Player→Kotlin→Backend→DB 경로를 다시 실행한다. 결과는 아직 NOT_RUN이다.
- PX-T04 앱 실행은 성공했으나 전용 에뮬레이터 최초 전체화면 안내가 Player를 일시 정지했다. 안내를 닫은 뒤 Player 자체 FAIL을 보고해 전체 검증은 실패(`artifacts/unity-android-e2e-sapxskap`); 오류 단계를 조사한다.
- PX-T04 Player가 configuration 단계에서 FAIL. 생성 Gradle의 settings·unityLibrary build 파일에 GameBridge Maven 연결이 없고 Editor hook은 `UNITY_ANDROID` 조건부다. Unity Editor 활성 build target이 Android로 지정되지 않아 hook이 누락된 가능성을 확인했다. 수정 후 실제 Player로 재검증한다.
- PX-T04 Unity batch에 `-buildTarget Android`를 명시하고 테스트 앱 실패 stage·오류 타입만 출력하도록 보강했다. credential 값과 예외 메시지는 출력하지 않는다. 실제 Gradle 의존성 및 Player 재검증 전이다.
- PX-T04 Android target 지정 스크립트 문법 및 테스트 앱 managed compile PASS(경고 0·오류 0). Unity Editor hook과 Player 실동작은 재검증 전이다. 수정 사항 커밋 준비.
- PX-T04 Android active target 수정 후 전체 검증 시작: 새 전용 AVD에서 Gradle SDK 의존성과 Unity Player→Backend→DB 경로를 확인한다. 결과는 아직 NOT_RUN이다.
- PX-T04 실제 Unity Android Player LOCAL_MOCK 전체 검증 PASS (`artifacts/unity-android-e2e-zbdkbnnl/result.json`, source c58b4a6, tracked clean): initialize/login/products/purchase/wallet/logout, Native 진단, Backend HTTP trace와 DB 원장 1건·100코인 확인. 전용 AVD의 Android 전체화면 안내는 수동으로 닫았다. Google 로그인·실제 스토어 및 Unity iOS는 NOT_RUN. 공개 요약: `docs/evidence/px-t04-unity-android-local-mock.md`.
- PX-T04 README·USER_SETUP·FINAL_REPORT 및 기능 매트릭스의 현재 상태를 Unity Android LOCAL_MOCK PASS로 정리했다. 과거 실패 기록은 이력으로 보존하고 Unity iOS·실제 제공자는 NOT_RUN 유지한다.
- PX-T04 공개 evidence에 실제 실행 명령 형태·종료 코드·도구 버전·staging hash 및 최초 전체화면 안내 수동 처리를 명시했다. 전체 strict suite 및 Unity iOS는 별도로 미실행이다.
- PX-T04 기능별 매트릭스에 Unity Android LOCAL_MOCK 및 신규 UPM import·IL2CPP PASS를 반영했다. Unity Editor test suite, push·복구, iOS 및 외부 플랫폼 결과는 승격하지 않았다.
- PX-T04 USER_SETUP의 과거 라이선스 부재 기록을 당시 상태로 명시하고, 현재 6000.5.8f1 활성 라이선스·Android/iOS 모듈 설치 사실을 추가했다.
- PX-T04 PASS evidence·문서 커밋 준비: 검증된 Unity Android LOCAL_MOCK 범위만 기록하고 원본 로그·APK·DB 및 미추적 사용자 파일은 포함하지 않는다. 자동 push하지 않는다.
- PX-T04 최종 원장 검사 PASS 및 ADB 재검색 안전 테스트 2건 PASS/skip 0. Unity Player PASS 증거는 별도 source c58b4a6 결과이며 자동 push하지 않는다.
- PX-T07 Unity iOS LOCAL_MOCK 통합 개발 시작: source `2a116c2`, 추적 파일 clean, 기존 미추적 Demo·캐시 보존. Unity 6000.5.8f1 라이선스 활성·iOS 모듈 설치, Xcode 26.6/Swift 6.3.3 및 iOS 18.6·26.5 simulator runtime을 확인했다. Unity iOS Player는 NOT_RUN이다.
- PX-T07 기존 UPM staging 110개 checksum 및 XCFramework device/simulator arch·C ABI 4종 검사 PASS. Unity iOS Simulator 소비 프로젝트·실행 하네스 구현을 시작한다. 실제 Unity iOS 실행은 NOT_RUN이다.
- PX-T07 iOS 전용 소비 시나리오·Simulator export 스크립트 작성. 개발키는 Simulator 프로세스 환경에서만 읽고 127.0.0.1 테스트 앱 ATS 예외만 적용한다. 코드·Player 검증은 아직 미실행이다.
- PX-T07 소비 프로젝트 생성 및 staging checksum PASS (`artifacts/unity-ios-mock.8xjMY7`), 스크립트 문법 PASS. Unity iOS Simulator Xcode 프로젝트 생성을 시작한다.
- PX-T07 Unity 6000.5.8f1 iOS Simulator Xcode 프로젝트 export PASS (`artifacts/unity-ios-mock.8xjMY7/xcode`). Simulator용 Xcode 링크·빌드와 ATS 범위를 확인한다. Player 실행은 NOT_RUN이다.
- PX-T07 Unity iOS Simulator arm64 Xcode build/link PASS (`artifacts/unity-ios-mock.8xjMY7/Derived`, code signing 비활성). XCFramework 프로젝트 포함 확인. 실제 Simulator Player·Backend 통합은 아직 NOT_RUN이다.
- PX-T07 UnityFramework 실제 Simulator binary에서 C ABI 심볼 4종 확인, 테스트 Info.plist의 loopback 127.0.0.1 예외만 확인했다. 격리 Simulator·DB 전체 E2E runner를 구현한다.
- PX-T07 Simulator 전용 E2E runner 초안과 Python 문법 검사를 작성했다. 실제 Unity Player·Swift callback·DB 지급은 아직 NOT_RUN이며 실행으로 검증한다.
- PX-T07 iOS consumer·runner 1차 구현 커밋 준비: Unity Simulator export와 Xcode build·ABI 검증까지만 PASS, 전체 Player 실행은 NOT_RUN이다.
- PX-T07 Unity iOS LOCAL_MOCK 전체 E2E 검증 시작: 신규 Simulator·전용 DB와 checksum 검증된 staging을 사용한다. 결과는 아직 NOT_RUN이다.
- PX-T07 전용 iOS Simulator 앱 실행 중 예상하지 않은 알림 권한 창이 표시돼 Player 진행이 막혔다. Unity notifications 설정 또는 Host 동작을 조사하며 아직 E2E 결과는 미확정이다.
- PX-T07 첫 전체 실행 FAIL (`artifacts/unity-ios-e2e-sbwq4jn5`, exit 1 `UNITY_PLAYER_REPORTED_FAILURE`). 실제 Xcode build·Simulator 앱 launch는 진행됐지만 Player가 실패를 보고했다. 알림 권한 창은 전용 Simulator에서 거부했으며 정확한 실패 단계와 예상치 못한 권한 요청을 조사한다.
- PX-T07 원인 조사: Unity Notifications 기본 plist에 시작 시 알림 요청이 true이며 첫 local-mock 인증은 Backend HTTP 200까지 도달했다. 전체 실패 stage는 runner가 기록하지 않아 미확정; 테스트 앱에서 자동 알림 요청을 끄고 실패 시 안전한 단계 마커를 저장한다.
- PX-T07 테스트 전용 앱의 자동 알림 요청 비활성화와 실패 단계 마커 보존을 추가했다. 실제 결과는 재검증 전이다.
- PX-T07 알림 설정 및 실패 마커 runner 문법 검사 PASS. 실제 전체 흐름은 미검증이며 수정 사항을 로컬 커밋 후 전용 새 Simulator에서 재검증한다.
- PX-T07 수정 후 전체 E2E 재검증 시작: 새 전용 Simulator·DB를 사용하며 최신 source 기준 Player 결과는 아직 NOT_RUN이다.
- PX-T07 두 번째 전체 E2E FAIL (`artifacts/unity-ios-e2e-rfz6jnz2`, `UNITY_PLAYER_REPORTED_FAILURE`). 저장된 Unity 단계 마커와 Backend trace를 대조해 원인을 확인한다.
- PX-T07 失敗段階: Unity initialize PASS、Backend mock-auth HTTP 200 後 login INTERNAL_ERROR。テスト用 unsigned Simulator app の Keychain/コード署名を切り分ける。外部 Apple 認証は使用しない。
- PX-T07 대조용 Simulator ad-hoc Xcode 빌드 PASS: 무료 로컬 서명으로 bundle identifier가 보존됐으며 Apple 계정·인증서는 사용하지 않았다. Keychain 원인 여부는 실제 Player 재검증 전 미확정이다.
- PX-T07 runner에 명시적 Simulator local ad-hoc 대조 옵션을 추가한다. 기존 무서명 경로와 구분해 실제 전체 흐름을 재검증한다.
- PX-T07 ad-hoc 대조 runner 문법 검사 PASS. 커밋 후 새 Simulator에서 실제 로그인·구매·원장을 재검증한다.
- PX-T07 local ad-hoc Simulator 전체 E2E 대조 실행 시작. 새 전용 Simulator·DB를 사용하며 현재 결과는 NOT_RUN이다.
- PX-T07 local ad-hoc 대조 E2E PASS (`artifacts/unity-ios-e2e-f5r4zwvp`, source e2a7138, tracked clean): Unity initialize/login/products/purchase/wallet/logout, Swift Native 진단, Backend HTTP 및 DB 원장 1건·100코인. Apple 계정·실제 스토어 미사용. Main Thread 확인을 명시적으로 강화한 뒤 재검증한다.
- PX-T07 검증 강화: Unity API 각 단계와 Native diagnostics 복귀가 시작 시 Unity 메인 스레드와 같은지 명시적으로 검사하고 runner가 marker를 필수로 요구한다. 새 코드의 실제 Player 결과는 아직 NOT_RUN이다.
- PX-T07 메인 스레드 검증 강화 runner 문법 PASS. 테스트 코드 변경 후 실제 Player·callback 검증은 재실행 전이며 커밋 준비한다.
- PX-T07 메인 스레드 assertion 포함 전체 E2E 재검증 시작: 별도 Simulator·DB에서 현재 source로 실행한다. 결과는 NOT_RUN이다.
- PX-T07 최신 테스트 코드의 Unity iOS LOCAL_MOCK 전체 E2E PASS (`artifacts/unity-ios-e2e-29s8tvel`, exit 0): Unity 메인 스레드 확인, Swift C ABI diagnostics, Backend HTTP 및 DB 원장 1건·100코인. 로컬 ad-hoc Simulator signing 사용, 실제 Apple 계정·스토어는 NOT_RUN이다. 공개 evidence 작성에 앞서 결과와 해시를 대조한다.
- PX-T07 실제 PASS 결과에서 검증된 source·Unity/Xcode/runtime·UPM/iOS binary hash·실행 명령·local ad-hoc 및 실패/수동 조작 한계를 공개 evidence에 기록했다. 원본 로그와 비밀은 포함하지 않았다.

### 추가 Task PX-T07 — Unity iOS Simulator LOCAL_MOCK E2E

구현 IMPLEMENTED / iOS 18.6 ARM64 Simulator LOCAL_MOCK E2E PASS / 실제 Apple 로그인·App Store 결제·APNs NOT_RUN. [검증 evidence](evidence/px-t07-unity-ios-local-mock.md). 로컬 ad-hoc Simulator signing을 사용했으며 최초 무서명 시도는 로그인 INTERNAL_ERROR로 실패했다. Android 기존 PASS는 그대로 유지한다.
- PX-T07 README·FEATURE_MATRIX·USER_SETUP·FINAL_REPORT와 기능별 매트릭스에 iOS Simulator LOCAL_MOCK PASS를 반영했다. 실제 Apple 로그인·스토어·APNs·Unity push/lifecycle 및 실제 기기는 NOT_RUN 유지한다.
- PX-T07 주의: 최초 테스트 소비 프로젝트의 Unity Notifications 기본 설정이 알림 권한 창을 표시했다. 최종 테스트 앱에서 자동 요청을 껐으며 실제 host의 push/권한 수명주기는 별도 미검증이다.
- PX-T07 최종 원장 검사·iOS runner 문법 및 기존 Android ADB 기기 안전 단위 테스트 2건 PASS. 실제 Android Player 전체 회귀는 이번에 재실행하지 않았고 기존 PX-T04 PASS를 유지한다. 커밋 준비.
- PX-T08 Unity Android LOCAL_MOCK Push/Lifecycle 검증 시작: 기존 인증·구매 PASS를 보존하며 실제 Player→Kotlin→Backend/DB의 등록·수신·해제와 이벤트 전달을 먼저 구현·검증한다. 아직 Push/Lifecycle Player 결과는 NOT_RUN이다.
- PX-T08 Android 전용 Player 시나리오 작성: Mock 등록·동일 ID 중복 억제·Unity 메인 스레드·등록 해제/로그아웃 후 이벤트 대기를 분리해 검사한다. 실제 Player 검증은 NOT_RUN이다.
- PX-T08 Android Push 시나리오 Unity managed reference 컴파일 PASS(경고·오류 0). 실제 Player 푸시 수신은 미검증이며 Backend 발송·원장 확인을 위한 격리 runner를 작성한다.
- PX-T08 Android Push Player runner 작성 및 Python 문법 검사 PASS. 연결된 경우만 전달·등록 해제 후 서버 거부·DB token 삭제를 검사하도록 했으며 실제 E2E는 아직 NOT_RUN이다. 테스트 실행 전 로컬 커밋한다.
- PX-T08 Android LOCAL_MOCK Push Player E2E 시작: 새 전용 AVD·DB와 검증된 staging을 사용한다. 결과는 아직 NOT_RUN이다.
- PX-T08 Android Unity Player LOCAL_MOCK Push 부분 PASS (`artifacts/unity-android-push-z1lufhpv`, exit 0): 등록·동일 ID 3회 발송 중복 억제·Unity main-thread 수신·등록 해제/로그아웃 후 이벤트 미전달·token 삭제 확인. 최초 전체화면 안내는 전용 AVD에서 수동으로 닫았다. background/network/restart 및 iOS는 NOT_RUN이다.
- PX-T08 Android Push 부분 PASS만 `docs/evidence/px-t08-unity-android-mock-push.md`에 기록했다. Lifecycle·네트워크·프로세스 재시작과 iOS는 NOT_RUN이며 전체 완료가 아니다. 커밋 후 별도 검증을 계속한다.
- PX-T09 Android lifecycle·네트워크 복구 검증 시작: 앱 background/foreground와 전용 에뮬레이터의 네트워크 단절·복구를 실제로 조작해 이벤트·재연결을 확인한다. 프로세스 강제 종료는 별도다.
- PX-T09 Player 시나리오에 실제 pause/resume과 오프라인 메시지 미관측·재연결 후 새 메시지 수신 검사를 추가했다. 실제 Player 실행은 아직 NOT_RUN이다.
- PX-T09 Android managed compile PASS(경고·오류 0). runner에 실제 HOME→foreground, 전용 AVD의 Wi-Fi/data 차단·복구 및 offline/online 발송을 추가했다. 실제 실행은 아직 NOT_RUN이다.
- PX-T09 runner 문법 검사 PASS. 수정 시나리오와 진행 기록을 커밋한 뒤 새 AVD의 실제 Player에서 검증한다.
- PX-T09 Android lifecycle/network Player 검증 시작: 새 전용 AVD·DB로 실제 background/foreground 및 네트워크 단절·복구를 실행한다. 아직 결과는 NOT_RUN이다.
- PX-T09 Android Unity Player background/foreground 및 전용 AVD Wi-Fi/data 차단·복구 LOCAL_MOCK Push E2E PASS (`artifacts/unity-android-push-a82dcn48`, exit 0). 오프라인 발송은 복구 뒤 미수신, 연결 복구 후 새 메시지 수신·main thread 확인. 프로세스 강제 종료·pending 및 iOS는 NOT_RUN이다.
- PX-T09 Android lifecycle/network PASS 증거를 기존 Android Push evidence에 추가했다. 프로세스 강제 종료·pending·iOS는 NOT_RUN으로 유지하며 커밋한다.
- PX-T10 Android process 강제 종료·재시작 및 pending 구매 검증 시작: 서버 지급 후 응답만 합성 503으로 대체해 pending을 남긴 뒤 별도 프로세스에서 동일 계정 복구와 중복 지급 방지를 확인한다. background 전환과 별도다.
- PX-T10 Android Player 테스트 소스에 서버 지급 후 합성 실패 대기, 프로세스 재시작 후 세션 복원·pending sync 1회·재sync 0회·잔액 100 검사를 추가했다. 실제 강제 종료 검증은 NOT_RUN이다.
- PX-T10 Android process 테스트 consumer managed compile PASS(경고·오류 0). 서버 commit 후 응답 오류를 주입하는 격리 proxy 및 실제 프로세스 재시작 runner를 구현한다.
- PX-T10 Android restart runner·local fault proxy Python 문법 PASS. 실제 Unity 프로세스 강제 종료 및 pending 복구는 아직 NOT_RUN이며 실행 전 커밋한다.
- PX-T10 Android Unity force-stop/pending 복구 실검증 시작: 새 전용 AVD·DB와 test-only fault proxy 사용. 결과는 NOT_RUN이다.
- PX-T10 Android Unity Player process 강제 종료·재시작 LOCAL_MOCK pending 복구 PASS (`artifacts/unity-android-restart-r3p6hl0d`, exit 0): 첫 서버 commit 뒤 응답만 실패시킨 상태에서 별도 PID로 세션 복원·pending 1회 복구·재sync 0회·원장 1건/100 확인. 첫 전체화면 안내 수동 처리. 실제 Play Billing은 NOT_RUN.
- PX-T10 실제 Android Unity process 강제 종료·pending 복구 증거를 Android Push/Lifecycle evidence에 추가했다. 세션 변경·늦은 callback 및 iOS는 별도다. 커밋 준비.
- PX-T11 Android 세션 전환·늦은 이벤트 검증 시작: 기존 사용자 A 로그아웃 후 B로 재초기화·동일 설치 등록 시 이전 사용자 발송 차단과 새 사용자 이벤트를 실제 Player에서 확인한다.
- PX-T11 Android test에 A 로그아웃 후 B 재등록, A 발송 403·B 단일 수신과 기존 이벤트 재유입 차단을 추가했다. 실제 Player 재검증 전이다.
- PX-T11 확장 테스트 Android managed compile 및 runner 문법 PASS. A→B 세션 전환·이전 소유권 차단의 실제 Unity Player 결과는 아직 NOT_RUN이다. 커밋 후 검증한다.
- PX-T11 Android Push 세션 전환·lifecycle 재검증 시작: 새 전용 AVD 및 DB를 사용한다. 결과는 NOT_RUN이다.
- PX-T11 Android Unity LOCAL_MOCK 세션 A→B 전환 E2E PASS (`artifacts/unity-android-push-h9oyrtjy`, exit 0): A 소유권 발송 403, B 단일 이벤트 및 이전 메시지 미관측, 메인 스레드, 기존 lifecycle/network도 재통과. 전용 AVD의 최초 전체화면 안내 수동 처리. 재연결 실패 주입/임의 지연 Native callback 주입은 별도다.
- PX-T11 Android 실제 Player session 전환 PASS와 별도 미검증 범위를 evidence에 기록했다. 커밋 후 iOS Simulator의 동등 경로 개발을 이어간다.
- PX-T12 Unity iOS Simulator LOCAL_MOCK Push/Lifecycle 검증 시작: Android에서 확인한 등록·수신·중복·세션 전환과 별도로 iOS Swift C ABI·Player 경로를 검증한다. 실제 APNs는 NOT_RUN이다.
- PX-T12 iOS Simulator 전용 Unity Push 시나리오 초안 작성: Simulator 환경 변수로 합성 key·설치 ID를 받고 Android 동일 이벤트·메인 스레드·세션 전환을 검사한다. iOS Player 실행은 NOT_RUN이다.
- PX-T12 iOS Push 시나리오 Unity managed reference 컴파일 PASS(경고·오류 0). 전용 Simulator에서 Swift bridge·백그라운드·연결 중단/복구를 검증할 runner를 구현한다. 실제 iOS Player는 아직 NOT_RUN이다.
- PX-T12 iOS Simulator Push runner 작성 및 Python 문법 PASS. 격리 loopback TCP fault로 SDK 연결만 끊어 offline drop/복구를 검사하며 OS 전체 네트워크 차단으로 주장하지 않는다. 실제 Player 결과는 NOT_RUN이다.
- PX-T12 iOS Simulator LOCAL_MOCK Push/Lifecycle 첫 실제 E2E 시작: 신규 전용 Simulator·DB, local ad-hoc 및 테스트 전용 TCP fault 사용. 결과는 NOT_RUN이다.
