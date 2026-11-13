# P00–P08 부분 기능 기준점 — 2026-11-11

상태: **INCOMPLETE / PARTIAL**. 이 기준점은 공개 release나 기능 완료 선언이 아니다. source 기준 commit: `66c5206b55357390ad6fd2a9e05d59635ad7a1c1`. `contracts/baseline/manifest.json`의 파일은 해당 시점의 API/protocol snapshot이다.

최신 Android Maven의 독립 R8 consumer, iOS static XCFramework의 slice·symbol·Swift consumer link, UPM staging 체크섬 110개 및 독립 hook 시험은 확인했다. Unity Editor import/export/IL2CPP는 ENV-002로 실행하지 못했다. Mock DB 응답 유실·보안 저장소 인스턴스 재생성은 시험했으나 실제 기기 프로세스 재시작과 Unity player는 미검증이다.

남은 내부 작업: LOCAL_MOCK 개발 push의 Backend→client simulated delivery E2E, XCODE_STOREKIT 전체 검증/지급 경로, Native 진단의 Unity 통합, 실제 Unity demo scene/host 통합 및 전체 회귀 검증. iOS 26.5 StoreKit local 시험은 ENV-STOREKIT-26 실패 이력이 있고 실제 Google/Apple/FCM/APNs는 사용자 설정 대기다. 당시 `scripts/smoke-local.sh`는 미구현 push E2E 때문에 실패했다. 이후 변경 사항과 현재 실행 상태는 진행 원장을 따른다.

다음 표는 snapshot 시점 원장 전체이며 미완료 행을 숨기지 않는다.

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
