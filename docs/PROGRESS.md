# GameBridge SDK 진행 원장

> 각 Task 시작·검증·블로커·커밋 전에 갱신한다.

## 현재 체크포인트

- 전체 상태: IN_PROGRESS / 전체 SDK BLOCKED_INTERNAL. P05-T03 FAIL·StoreKit26 OPEN·실 Provider13 WAITING_USER 유지.
- 현재 Phase / Task: 포트폴리오 최종화 종료 / 사용자 문서36. SDK제품화 원장과 별도의 종료 판정이다.
- 마지막 갱신: 2026-11-18 (Asia/Seoul).
- 현재 source: 기능 변경은 누락 필수 HTTP header를400으로 분류하는 수정. Native/UPM shipping source는 배치33 build source a83561a와 동일.
- 현재 검증: 마지막 code648bb80의 Python263·Native/Core·managed·변이/원장/소비·Hosted SUCCESS 근거를 유지. 최종화는 문서 검토·동일패키지 checksum 확인이며 새 제품/하네스 실행이 아니다.
- 최신 staging: artifacts/batch33/upm, 147파일. 새 배치34 양Unity 소비에서 실제 사용했으며 새 Native 재빌드로 표현하지 않는다.
- 작업 트리: handoff/p09-resume-20261113; 기존 미추적 Demo·Python 캐시 보존.
- 현재 모드: LOCAL_MOCK·synthetic Sandbox, 실제 Provider 호출 없음.
- 미완료: Android JNI heap/시간, iOS Task·continuation, Unity weak client1 잔존 원인·CPU blocking, Strict E2 자원생성/전체 소유권 전파, SSE·동적Map 세부 HTTP 계약. P10-T03/T04·P11 PARTIAL, BUG-017 OPEN.
- 다음 행동: 없음(포트폴리오 개발 종료). 명시적 새 요청이 있는 경우에만 선택적 제품화 backlog를 검토한다.

## 집계

- 계획 Task 총수: 64
- 구현: NOT_STARTED 0 / IN_PROGRESS 39 / IMPLEMENTED 25 / BLOCKED 0
- 로컬 검증: NOT_RUN 0 / PASS 23 / FAIL 1 / PARTIAL 40 / DEFERRED_ENV 0 / REVIEW_ONLY 0
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
| P00-T02 | 도구·라이선스·버전 조합 확정 | IMPLEMENTED | PASS | N/A | docs/TOOLCHAIN.md, WORK_LOG P00-T02 | ENV-001 |
| P00-T03 | 빌드 가능한 최소 프로젝트 구성 | IMPLEMENTED | PASS | N/A | docs/evidence/p10-batch33-package.json; docs/evidence/p10-batch32-post-native-android.json; docs/evidence/p10-batch32-post-native-ios.json; WORK_LOG P00-T03 | - |
| P00-T04 | 진행 문서 검사·기본 명령 진입점 | IMPLEMENTED | PASS | N/A | docs/evidence/p00-entrypoints.md | - |
| P00-T05 | 모드·비밀정보·설정 격리 | IMPLEMENTED | PASS | N/A | docs/evidence/p00-mode-config-isolation.md | - |
| P01-T01 | 공통 모델·오류·상태 schema | IMPLEMENTED | PASS | N/A | WORK_LOG P01-T01; artifacts/contracts-72sh1hus | - |
| P01-T02 | Bridge wire protocol·공용 fixture | IMPLEMENTED | PASS | N/A | WORK_LOG P01-T02; artifacts/contracts-gmjhtcvv | - |
| P01-T03 | SDK 상태기계·Provider interface | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T03 | - |
| P01-T04 | 결정적인 Fake Provider | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T04 | - |
| P01-T05 | Native HTTP·저장소·세션 소유권 기반 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P01-T05 | - |
| P02-T01 | Backend·PostgreSQL·migration 기동 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T01 | - |
| P02-T02 | Mock 사용자·opaque 세션·갱신 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T02 | - |
| P02-T03 | 상품·재화·구매 원장 서비스 | IMPLEMENTED | PASS | N/A | docs/evidence/p02-mock-ledger.md | - |
| P02-T04 | purchase 재시도·finalization queue | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T04 | - |
| P02-T05 | device token·config·개발 푸시 API | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P02-T05 | - |
| P02-T06 | 로컬 Backend 통합 smoke 명령 | IMPLEMENTED | PASS | N/A | docs/evidence/p02-backend-smoke.md | - |
| P03-T01 | Kotlin SDK의 LOCAL_MOCK 수직 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T01 | - |
| P03-T02 | Swift SDK의 LOCAL_MOCK 수직 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T02 | - |
| P03-T03 | Android JNI 왕복 transport | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T03 | sdk.status/UTF8 조건별 증거 연결 잔여; 새 Android 소비 PASS |
| P03-T04 | Swift C ABI 왕복 transport | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T04 | Unicode 조건별 증거 연결 잔여; 새 iOS/C ABI 소비 PASS |
| P03-T05 | Unity facade·dispatcher·request registry | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P03-T05 | Scene/Domain Reload 조합별 검증 잔여 |
| P03-T06 | Unity 최소 Demo·Native 경로 분기 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T02 | 샘플 UI 직접 클릭/렌더링 검증 잔여 |
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
| P06-T03 | Unity iOS Push Host Adapter | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T03 | USER-PUSH-APPLE, Host/원격 조건별 검증 잔여 |
| P06-T04 | Backend FCM·APNs 실제 sender | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T04 | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P06-T05 | 수명주기·콜드스타트·클릭 라우팅 | IN_PROGRESS | PARTIAL | WAITING_USER | WORK_LOG P06-T05 | USER-PUSH-GOOGLE, USER-PUSH-APPLE |
| P07-T01 | 진단·redaction·점검 설정 완성 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T01 | - |
| P07-T02 | 세 샘플 전체 사용자 흐름 연결 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T02 | 샘플 UI/순서별 직접 시연 검증 잔여 |
| P07-T03 | 연동 문서·오류·소유권 가이드 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P07-T03 | - |
| P07-T04 | 구현 누락 1차 점검 | IN_PROGRESS | PARTIAL | N/A | docs/FEATURE_MATRIX.md, WORK_LOG P07-T04 | - |
| P08-T01 | Android Maven 산출물·소비 build | IMPLEMENTED | PASS | N/A | docs/evidence/p08-android-maven-consumer.md | - |
| P08-T02 | Swift Package·static XCFramework 산출물 | IMPLEMENTED | PASS | N/A | docs/evidence/p08-ios-xcframework-consumer.md | - |
| P08-T03 | UPM staging·멱등 build hook | IMPLEMENTED | PASS | N/A | docs/evidence/p08-upm-staging.md | - |
| P08-T04 | 신규 Unity 프로젝트 재설치 검증 | IMPLEMENTED | PASS | N/A | docs/evidence/consumer-install.md | - |
| P08-T05 | 기능 개발 기준점 고정 | IMPLEMENTED | PASS | N/A | docs/evidence/feature-baseline-current-20261113.md | - |
| P09-T01 | 후반 하네스 manifest·공통 contract test | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch25-integrated.md, WORK_LOG P09-T01 | - |
| P09-T02 | Core·Bridge 회귀·실패 주입 | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch26-integrated.md; docs/evidence/p09-batch26-assertions.json, WORK_LOG P09-T02 | 측정 밖 assertion은 UNMEASURED; 현재 JNI Player 대기 |
| P09-T03 | 인증·세션·개발모드 차단 회귀 | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch25-integrated.md, WORK_LOG P09-T03 | - |
| P09-T04 | 구매·DB 동시성·복구 회귀 | IMPLEMENTED | PARTIAL | N/A | docs/evidence/p09-batch26-integrated.md, WORK_LOG P09-T04 | DEP-P09-SK18 |
| P09-T05 | Push·Lifecycle·패키징 회귀 | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch25-integrated.md, WORK_LOG P09-T05 | - |
| P09-T06 | 검증 집계·진행 원장 강제 검사 | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch25-integrated.md, WORK_LOG P09-T06 | - |
| P09-T07 | CI 설정·플랫폼 lane 분리 | IMPLEMENTED | PARTIAL | N/A | docs/evidence/p09-batch26-integrated.md; docs/evidence/p09-ci-modes.md, WORK_LOG P09-T07 | ENV-P09-RUNNER |
| P09-T08 | Fail-closed 하네스 자체 시험 | IMPLEMENTED | PASS | N/A | docs/evidence/p09-batch25-integrated.md, WORK_LOG P09-T08 | - |
| P10-T01 | 검증 기준 유지하며 Core·Bridge 리팩토링 | IMPLEMENTED | PASS | N/A | docs/evidence/p10-batch32-t01-decision.md; docs/evidence/p10-batch32-core.json, WORK_LOG P10-T01 | 추가 전체Strict/Release는 ENV-UNITY-LICENSE-IPC/ENV-P09-RUNNER로 별도 유지 |
| P10-T02 | 인증·결제·푸시 책임과 보안 정리 | IMPLEMENTED | PASS | N/A | docs/evidence/p10-batch32-native-refactor.md; docs/evidence/p10-batch32-post-native-android.json; docs/evidence/p10-batch32-post-native-ios.json | 실제Provider/전체SDK·Release별도; fullStrict는DEP-STRICT-OWNED-ENV |
| P10-T03 | 측정 기반 수명주기·메모리·응답 확인 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T03 | 추가 profiling NOT_RUN·weak1 원인 미확정 |
| P10-T04 | 리팩토링 후 재패키징·호환성 재검증 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P10-T04 | 선행 P10-T03 PARTIAL; 선정 ABI·새 양 소비 PASS |
| P11-T01 | 전체 Task·TODO·계약 누락 최종 감사 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T01 | - |
| P11-T02 | 사용자 설정·실연동 재개 runbook 완성 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T02 | - |
| P11-T03 | 최종 문서·release candidate 로컬 패키지 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T03 | - |
| P11-T04 | 마지막 검증·커밋·인계 | IN_PROGRESS | PARTIAL | N/A | WORK_LOG P11-T04 | - |

## 블로커 원장

| ID | 유형 | 영향 Task | 실제 증상/실행 명령 | 코드 개발 지속 방법 | 해소 조건 | 상태 |
|---|---|---|---|---|---|---|
| USER-PUSH-CONCURRENCY | USER | P06-T04 | 기본 동시 1건 사용자 선택 | scheduler 설정·검증 진행 | 실제 원격 발송은 별도 | RESOLVED |
| USER-CONFIG-TTL | USER | P07-T01 | 기본 유효기간 5분 사용자 선택 | 서버 설정·local-mock 통합 진행 | 실제 플랫폼 검증은 별도 | RESOLVED |
| BUG-017 | BUG | P11-T01·P11-T03 | 최초 OpenAPI 부재는해소; 현재24operation/DTO23/응답구조검증존재, SSE/동적Map의세부기계검사잔여 | API.md에중요SSE/Map사용계약보강, portfolio Known Limitation으로유지 | 기존Source/DTO/HTTP검증보존; 상세SSE/Map자동검사확대는선택적제품화범위 | OPEN |
| BUG-016 | BUG | P04-T04, P09-T03 | Native 실제 Provider의 profile 확인 이후 요청 401에서 refresh 누락 | Android/iOS 단일 refresh·1회 재시도 및 proof idempotency 유지 구현 | fake 동시 요청·계정 변경·반복 401·증빙 멱등키 검증 | RESOLVED |
| BUG-015 | BUG | P07-T01, P10-T02 | Native 진단 ring의 Unity 공개 조회: Android 및 iOS Simulator LOCAL_MOCK Player 확인 | Native typed snapshot과 C# 제한 검사 유지 | 다른 모드·실제 기기 redaction 별도 | OPEN |
| BUG-014 | BUG | P02-T06, P06-T05 | LOCAL_MOCK Unity Android emulator·iOS Simulator 전달 및 lifecycle 확인 | 인증·소유권·heartbeat 회귀 유지 | 실제 기기·FCM/APNs 및 iOS OS 전체 네트워크 차단 별도 | OPEN |
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
| DEP-P09-SK18 | DEP | P09-T04 | 배치24 18.6 timeout 원인 미확정, 배치25 동일 제한의 두 경로 PASS | 최초/후속 증거 및 checkpoint 분리 유지 | 정지 구간·기기 상태/부하 관측으로 간헐 원인 분류 | OPEN |
| DEP-P10-T01 | DEP | P10-T02 | 배치27 실제 Editor 미복구로 current Player·Strict 완료 증거 없음 | 제품 변경 없이 책임 감사/후보2/회귀설계만 완료 | P10-T01 current Player·Strict 및 로컬 완료 조건 확인 후 후보별 진입 | OPEN |
| ENV-UNITY-ADB-STARTUP | ENV | P10-T01·전용 기기 시험 | 배치28 Hub GUI Editor 상태바에서 다른 SDK ADB server 인스턴스 종료 경고 관측, 대상/영향 미확정 | 에이전트 ADB명령 없음, 추가 기기/서버 조작 보류 | 후속 기기 시험 전 SDK·ADB process 및 전용 serial/PID/양port 소유 확인 | OPEN |
| DEP-P10-ANDROID-E2E | DEP | P10-T01 구매·PII 범위 | 배치29 timeout FAIL 원본/미수집 UI 원인 미확정 보존; 배치30 새 APK/AVD에서 명시1회 교육안내 ACK 후 동일 PID managed/Backend/원장1·100 PASS | 현재 동일 제품/source 범위 성공과 과거FAIL 분리 | 구매PII 재검증 충족; Push/JNI/무인CI는 별도 DEP-P10-PLAYER-IMPACT | RESOLVED |
| ENV-UNITY-LICENSE-IPC | ENV | P10-T01 자동batch/Strict | 배치28자동IPC실패保全; 배치32새Hub4에서direct/cli nonce batch메서드PASS 및新CLI APK/실제Player PASS | 라이선스파일/활성화변경없이현재원래자동Builder검증 | 자동Editor기본경로는회복; 전체Strict専用통합환경별도 | RESOLVED |
| ENV-MAC-LOCKED | ENV | 선택적 post-package GUI 시각검증 | CUA가 Mac 잠금/자동해제불가/사용자수동해제를반환 | 필수 후속제품검증은명시CLI/실제Player로완료,headless개발계속 | GUI시각조작필요시사용자수동unlock | OPEN |
| ENV-HUB-NEW-TERMS | ENV | P10-T01 GUI Push/JNI | Hub 재시작 후4.0.1의 새 Software License Terms 화면; 명시 동의 미수신/동의0·실제GUI APK0 | 독립harness/Core/API/ABI/CI 및두소유project등록 | 사용자 직접 새약관처리 또는행동시점 명시허용 뒤6000.5.8f1 실제GUI빌드 | RESOLVED |
| DEP-P10-PLAYER-IMPACT | DEP | P10-T01·T02 | 새 Android Push/JNI 실제Player 미실행; 과거iOSUnityPush 이후RequestRegistry 변경1개로current 영향 미검증 | 명시GUI 입력/음성 fixture와기존제품source 유지 | 양플랫폼별필수Player 영향증거와Strict환경제한을분리확인후T01판정 | RESOLVED |
| DEP-STRICT-OWNED-ENV | DEP | P09-T06·P10-T04 전체Strict | 原fullStrict의全wrapper에현재SDK build/runtime ADB분리·PID/server binding과全必須OS/StoreKit컨텍스트가전파/완비됐는지未驗證 | 原required suite/recorded P05FAIL를유지하고개별원래CLI/실제Player검증 | 안전한全lane격리preflight/일관된device-server수명설정완비後최대1회原Strict | OPEN |
| ENV-P09-RUNNER | ENV | P09-T07 | 전용 self-hosted 격리·실제 Unity CI/Release 미검증 | Hosted-only 및 local CI 경로 유지 | 전용 runner 준비와 별도 명시 검증 | OPEN |
| ENV-P09-AVD | ENV | P09-T05 | 배치24 serial/PID/실제 port 불일치 | 배치25 새 AVD의 PID·이름·console/ADB 양 port 소유를 확인한 current Push PASS | 재실행마다 소유 검증·새 앱 상태 유지; 무인 CI 별도 | RESOLVED |
| ENV-STOREKIT-26 | ENV | P05-T03 | iOS 26.5 simulator SKTestSession 설정 저장 Code 3 및 상품 조회 실패; 별도 iOS 18.6 전용 simulator 상품 조회 1건 통과 | 다른 독립 구현 진행; 실패 시험 보존 | 호환 환경에서 StoreKit local 재시험 | OPEN |
| ENV-008 | ENV | P04-T04 | 전용 PostgreSQL container 정상 종료 상태에서 opt-in DB 시험 실패 | 기존 volume 보존 후 재기동 | DB healthy 및 실패 시험 재실행 | RESOLVED |
| ENV-005 | ENV | P03-T02 | Simulator UI snapshot 대상 0개, 수동 대체 입력으로도 흐름 미확인 | XCTest 기반 독립 UI 검증 시도 | iOS local-mock UI smoke 실행 확인 | RESOLVED |
| ENV-004 | ENV | P03-T01 | 전용 emulator 복원 시험에서 화면 준비 전 입력 실패 | UI 준비 후 재시도 | Keystore 복원 확인 | RESOLVED |
| ENV-003 | ENV | P00-T03 | XcodeGen 최초 부재 | 로컬 도구 2.46.0 확보 후 프로젝트 생성·빌드 확인 | 실제 스토어 및 Unity 검증 별도 | RESOLVED |
| ENV-002 | ENV | P00-T03 및 Unity 검증 | 과거 Unity 라이선스 비활성 및 Android 모듈 부재 | Unity 6000.5.8f1 라이선스·Android 모듈 준비 확인, Unity Android local-mock Player 실행 | Unity iOS 및 나머지 테스트 별도 | RESOLVED |
| ENV-001 | ENV | P00-T02 | Unity 6.3 LTS 미설치·미검증; 설치된 6000.5.8f1 라이선스/Android·iOS 모듈 및 로컬 Player 확인 | 설치된 Editor에서 계속 검증 | 6.3 LTS 호환성 별도 확인 | OPEN |

유형: USER=사용자 계정·서명·콘솔, ENV=설치/실행환경, BUG=내부 버그, DEP=선행 구현 미해결. 같은 사건은 중복 ID를 만들지 않고 영향 Task를 추가한다. 사용자 인증 필요성은 USER_SETUP에 이미 계획되어 있지만 실제 구현 준비 여부는 개발 중 갱신한다.

## 기능별 검증 매트릭스

| 기능 | Android 코드/빌드 | iOS 코드/빌드 | Unity Editor | Unity Android | Unity iOS | 실제 외부 서비스 |
|---|---|---|---|---|---|---|
| Core·Bridge | BUILD:PASS / LOCAL_MOCK:PARTIAL | BUILD:PASS / LOCAL_MOCK:PARTIAL | IMPORT:PASS / TEST:NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | N/A |
| 인증 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | WAITING_USER |
| 결제 | BUILD:PASS / MOCK:PARTIAL | BUILD:PASS / MOCK:PARTIAL / STOREKIT_LOCAL:FAIL | NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | WAITING_USER |
| 푸시 | BUILD:PASS / FAKE:PARTIAL | BUILD:PASS / FAKE:PARTIAL | NOT_RUN | LOCAL_MOCK:PASS | SIM_LOCAL_MOCK:PASS | WAITING_USER |
| 세션·복구 | EMULATOR:PARTIAL | SIMULATOR:PARTIAL | NOT_RUN | LOCAL_MOCK_RESTART:PASS | SIM_LOCAL_MOCK_RESTART:PASS | WAITING_USER |
| 배포·신규 소비 | MAVEN_CONSUMER:PASS | XCFRAMEWORK_CONSUMER:PASS | UPM_IMPORT:PASS | IL2CPP:PASS | SIM_IL2CPP:PASS | N/A |

각 칸은 가능한 경우 `BUILD:PASS / RUN:WAITING_USER`처럼 분리한다. “Android 완료” 한마디로 Native standalone과 Unity Android를 합치지 않는다.

## 완료/미완료 요약

- 일부 계약·빌드·가짜 Provider·로컬 DB 회귀 및 독립 패키지 소비 검증 통과. 개별 범위와 명령은 WORK_LOG 참조.
- Unity Android 및 iOS Simulator LOCAL_MOCK 인증·구매·푸시/lifecycle 및 별도 프로세스 재시작 복구는 통과했으나 실제 플랫폼·실기기·원격 푸시·복구 전체 검증은 미완료. 외부 인증·서명·콘솔 설정은 USER_SETUP 참조.
- 내부 미완료: Xcode StoreKit 실제 기기 및 Unity 복구 검증, 실제 기기의 Unity push/lifecycle 검증, LOCAL_MOCK 외 Native 진단의 Unity 검증. BUG-009 실제 기기 재시작 검증도 미완료.
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

- 구현: NOT_STARTED 0 / IN_PROGRESS 43 / IMPLEMENTED 21 / BLOCKED 0
- harness/run-unity-android-mock-e2e.py를 추가했다. 기존 전용 AVD를 확인하고, 새 격리 Unity 소비 프로젝트를 생성하여 UPM staging을 검사한 후 APK를 빌드한다.
- 빌드 이후 별도의 랜덤 local-mock DB 및 Backend를 기동하고 Player를 실행한다. Unity 로그의 initialize/login/products/purchase/wallet/logout PASS, Native 진단 초기화·인증·구매 이벤트, Backend HTTP trace와 DB wallet_ledger 1건·100코인을 **모두** 확인해야 PASS다.
- Unity 6000.5.8f1 import·Android IL2CPP APK 및 전용 Android 36 에뮬레이터에서 LOCAL_MOCK 전체 경로를 검증했다. 첫 전체화면 안내는 수동으로 닫았다. 실제 Provider/스토어와 Unity iOS는 NOT_RUN 유지.
- 원본 로그와 생성 APK는 로컬 artifacts에만 남기며, 전용 AVD·DB를 삭제하지 않는다.

### 추가 Task PX-T05 — Native-only Runner 환경 가변화

- 구현: NOT_STARTED 0 / IN_PROGRESS 43 / IMPLEMENTED 21 / BLOCKED 0
- 기존 harness/run-android-mock-bridge-e2e.py의 emulator-5598, 사용자 홈 Android SDK 경로, Docker 컨테이너·포트 가정을 CLI/환경변수로 대체했다.
- adb로 현재 연결된 emulator와 GameBridge_V2_ 전용 AVD 이름을 확인하며 기존 com.gamebridge.sample 설치 앱을 보존한다. 재검증 전에는 이전 PX-T03 PASS 증거만 유효하며, 변경 후 재현성은 미검증이다.

### 추가 Task PX-T06 — 공개용 증거 요약과 CI 정적/오프라인 검사

- 구현: NOT_STARTED 0 / IN_PROGRESS 43 / IMPLEMENTED 21 / BLOCKED 0
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
- PX-T12 iOS Unity import 환경 블로커: 격리 프로젝트의 UPM resolve가 `packages.unity.com` ETIMEDOUT을 보고했다. 현재 실행 결과는 아직 미확정이며 이전에 확인한 패키지 캐시의 안전한 재사용 가능성을 조사한다.
- PX-T12 첫 iOS Push runner는 UPM registry timeout이 반복돼 작업 소유 프로세스를 중단했다(exit 130). Unity Player는 NOT_RUN이다. runner의 interrupted 상태 분류 및 검증된 동일 버전 캐시를 새 테스트 프로젝트에만 복사하는 경로를 보강한다.
- PX-T12 iOS runner에 exact package version 확인 후 새 테스트 프로젝트에만 embedded 복사하는 선택 경로와 INTERRUPTED 구분을 추가했다. Unity package resolver·실제 Player 검증은 재실행 전이다.
- PX-T12 격리 package cache 경로의 정확한 버전 복사 및 누락 시 fail-closed 단위 검증 시작. 실제 Unity import/Player는 미실행이다.
- PX-T12 exact-version cache 복사·누락 차단 단위 테스트 2건 PASS/skip 0. 실제 iOS Player는 NOT_RUN이며 수정 runner를 커밋한 뒤 새 Simulator로 재실행한다.
- PX-T12 검증된 동일 버전 로컬 패키지 cache를 새 소비 프로젝트에 복사해 iOS Player E2E 재검증 시작. 현재 Player 결과는 NOT_RUN이다.
- PX-T12 cache 사용 재시도 FAIL (`artifacts/unity-ios-push-flh6xhkq`, `UNITY_EXPORT_FAILED`): embedded Notifications의 패키지 자체 테스트가 소비 프로젝트에서 컴파일돼 NUnit 참조가 없어 실패했다. Unity Player는 NOT_RUN이며 테스트 전용 복사본의 불필요한 package tests만 제외해 재검증한다.
- PX-T12 cache 복사에서 test-only `Tests` 디렉터리만 제외하도록 변경했다. 원본 cache와 운영 package는 변경하지 않으며 단위 검사·실제 Unity export로 검증한다.
- PX-T12 test-only package 제외·원본 보존 unit 2건 PASS/skip 0. Unity export/Player는 다시 검증해야 한다. 커밋 준비.
- PX-T12 iOS Push 재검증 시작: Unity test-only package 제외본으로 새 Simulator·DB에서 Player 경로를 실행한다. 결과는 NOT_RUN이다.
- PX-T12 iOS Push 전체 재시도 FAIL (`artifacts/unity-ios-push-cggylkb4`, `BACKGROUND_FAILED`, exit 1). Unity export·Simulator build/실행은 진행됐지만 background 전환 명령에서 실패했으며 전체 통과가 아니다. 실제 수신 단계와 원인을 조사한다.
- PX-T12 iOS 첫 실행에서 Unity 초기화·로그인·Mock 푸시 등록, 단일 수신·중복 억제·main-thread 마커를 확인했다. `about:blank`는 Simulator에서 열 수 없었고 로컬 127.0.0.1 URL 열기는 성공했다. background 이후 흐름은 아직 NOT_RUN이다.
- PX-T12 Simulator background 전환을 로컬 Backend health URL로 변경했다. iOS 실제 lifecycle·연결 복구 결과는 재실행 전 NOT_RUN이다.
- PX-T12 background 전환 runner 문법 검사 PASS. 수정 사항 커밋 후 전용 새 Simulator에서 재검증한다.
- PX-T12 지원되는 loopback background 전환으로 iOS Push/Lifecycle 전체 재검증 시작. 새 Simulator·DB 사용, 결과는 NOT_RUN이다.
- PX-T12 Unity iOS Simulator LOCAL_MOCK Push/Lifecycle E2E PASS (`artifacts/unity-ios-push-248n_2n2`, exit 0): 등록·중복·main-thread·background/foreground·test TCP 연결 차단/복구·A→B 소유권·등록 해제/로그아웃 및 DB token 삭제 확인. OS 전체 네트워크 차단·process restart·실제 APNs는 미검증이다.
- PX-T12 실제 iOS Simulator 부분 PASS를 `docs/evidence/px-t12-unity-ios-mock-push.md`에 기록했다. iOS process restart/pending 및 실제 APNs는 NOT_RUN이며 커밋 후 이어서 검증한다.
- PX-T13 iOS Simulator process 강제 종료·재시작 및 pending 복구 검증 시작: 서버 commit 후 응답만 합성 503으로 바꾸고 새 프로세스에서 세션·pending·원장 불변을 확인한다. 아직 NOT_RUN이다.
- PX-T13 iOS Simulator 전용 Unity pending 복구 시나리오 작성: 서로 다른 프로세스 PID, 저장 세션, pending sync 1회·재sync 0회·잔액 100을 검사한다. 실제 실행은 NOT_RUN이다.
- PX-T13 iOS process restart runner 문법 검사 PASS. 로컬 ad-hoc Simulator와 test-only 응답 손실 proxy를 사용하며 실제 Player 검증은 아직 NOT_RUN이다. 커밋 후 전용 환경에서 실행한다.
- PX-T13 iOS Simulator process 종료·pending 복구 전체 검증 시작: 새 전용 Simulator·DB 및 exact-version test cache 사용. 결과는 NOT_RUN이다.
- PX-T13 Unity iOS Simulator LOCAL_MOCK 실제 앱 terminate/relaunch 및 pending 복구 PASS (`artifacts/unity-ios-restart-vidqoa21`, exit 0): 서로 다른 PID, session restore·pending 1회 복구·재sync 0, DB 원장 1건/100·main-thread 확인. local ad-hoc이며 실제 StoreKit은 NOT_RUN이다.
- PX-T13 실제 iOS Simulator process/pending PASS를 iOS Push evidence에 추가했다. 재연결 실패·임의 지연 callback 주입 및 실제 제공자·기기는 NOT_RUN이다. 커밋 준비.
- PX-T14 재연결 실패 명시 검증 시작: 기존 단절·복구 PASS는 재시도 실패 횟수를 직접 증명하지 않는다. 테스트 전용 loopback proxy로 Android/iOS SDK의 재연결 시도를 거부한 뒤 회복 여부를 별도 검증한다.
- PX-T14 iOS test proxy가 차단 중 실제 재연결 시도 거부 횟수를 세고 1회 이상을 요구하도록 수정했다. 새 코드의 실제 Player 검증은 NOT_RUN이다.
- PX-T14 Android runner에도 test 전용 TCP proxy를 추가해 OS 네트워크 복구 후 일시적 재연결 거부와 실제 시도 횟수를 검사한다. 실제 Android/iOS Player 재검증은 아직 NOT_RUN이다.
- PX-T14 양 runner Python 문법 및 package cache 안전 단위 2건 PASS. 실제 재연결 실패/복구 Player E2E는 재실행 전이며 커밋 준비한다.
- PX-T14 Android 재연결 실패·복구 실제 Player E2E 시작: 새 전용 AVD/DB와 test-only proxy를 사용한다. 새 결과는 NOT_RUN이다.
- PX-T14 Android Unity Player 재연결 실패 주입·복구 PASS (`artifacts/unity-android-push-n3lvsnkx`, exit 0): OS 네트워크 차단·복원 외 test proxy 재연결 거부 관측 후 새 push 수신. 상세 횟수 및 같은 실행의 lifecycle/session을 확인한다.
- PX-T14 Android 재연결 거부 2회 및 복구 Player PASS를 evidence에 기록했다. iOS의 동일 주입은 아직 NOT_RUN이며 커밋 후 이어서 실행한다.
- PX-T14 iOS 재연결 실패·복구 Player E2E 시작: 새 전용 Simulator·DB와 test-only TCP proxy 사용. 결과는 NOT_RUN이다.
- PX-T14 iOS Unity Simulator test-only TCP 재연결 실패 주입 및 복구 PASS (`artifacts/unity-ios-push-gcmp59n7`, exit 0). OS 전체 Wi-Fi 차단과 실제 APNs는 별도다. 결과 횟수·범위를 확인한다.
- PX-T14 iOS test-only TCP proxy 재연결 거부 6회·복구 Player PASS를 공개 evidence에 기록했다. OS 네트워크 전체 차단 및 실제 APNs는 별도다. 커밋 준비.
- PX-T15 기존 Android/iOS Unity 인증·구매 LOCAL_MOCK 전체 E2E 회귀 검증 시작: 새 Player 및 전용 기기·DB에서 다시 실행한다. 패키지 registry timeout 환경에서 기존 exact-version cache를 test 프로젝트에만 복사하는 옵션을 추가한다.
- PX-T15 기존 Android/iOS 인증·구매 Runner에 격리 consumer용 exact-version package cache 선택 기능을 추가했다. 실제 회귀는 아직 NOT_RUN이다.
- PX-T15 두 Runner 문법·cache 안전·ADB 안전 단위 각 2건 PASS. cache 누락 오류를 기존 runner 오류 분류로 전달한다. 실제 Android/iOS Player 회귀는 아직 NOT_RUN이다. 커밋 준비.
- PX-T15 기존 Android Unity 인증·구매 LOCAL_MOCK 전체 회귀 시작: 새 전용 AVD·DB 및 exact-version cache를 사용한다. 결과는 NOT_RUN이다.
- PX-T15 Android Unity 인증·구매 LOCAL_MOCK 전체 Player 회귀 PASS (`artifacts/unity-android-e2e-7001epc_`, exit 0). 전용 AVD 최초 전체화면 안내는 수동으로 닫았다. 실제 Google/Play는 NOT_RUN. iOS 동일 회귀를 시작한다.
- PX-T15 iOS Unity Simulator 인증·구매 LOCAL_MOCK 전체 회귀 시작: 새 Simulator·DB, 로컬 ad-hoc 및 exact-version cache. 결과는 NOT_RUN이다.
- PX-T15 기존 iOS Unity Simulator 인증·구매 LOCAL_MOCK 전체 회귀 PASS (`artifacts/unity-ios-e2e-zizcrlvt`, exit 0). local ad-hoc 서명·exact-version embedded cache 사용. 실제 Apple 로그인/StoreKit은 NOT_RUN이다.
- PX-T15 Android/iOS 인증·구매 LOCAL_MOCK 전체 Player 회귀 PASS를 각 플랫폼 evidence에 별도 source와 함께 기록했다. 실제 외부 제공자 및 스토어는 미검증이다. 커밋 준비.
- PX-T16 늦은 콜백·세션 격리 별도 검증 시작: 실제 Player의 세션 전환 결과와 구분해 Unity wire registry에 timeout 후 응답 및 이전 세션 이벤트를 합성 주입한다. Native 지연 callback 실제 Player 주입은 아직 NOT_RUN이다.
- PX-T16 Unity wire registry 지연 응답·이전 세션·dispose 이후 event 합성 단위 테스트 작성. 실제 Player Native callback 주입은 NOT_RUN이다. 단위 검증을 시작한다.
- PX-T16 managed 단위 첫 실행 FAIL: custom output 경로와 `dotnet run`의 기본 실행 경로가 달라 프로세스를 찾지 못했다. 테스트 assertion은 아직 미실행이며 빌드한 DLL을 직접 실행해 재검증한다.
- PX-T16 managed 단위 DLL 직접 실행 재검증 시작.
- PX-T16 실제 Unity Player 지연 callback 합성 주입 검증 시작: 이전 A session 이벤트를 B 활성 후 transport callback 경로에 주입해 폐기 여부와 버퍼 복사를 확인한다. 합성 주입과 실제 원격 푸시를 분리한다.
- PX-T16 이전 session 이벤트를 플랫폼 transport callback 큐에 test-only로 합성 주입하는 Player probe를 추가했다. iOS는 입력 버퍼를 즉시 해제해 복사 경계도 검사한다. 실제 테스트는 NOT_RUN이며 실제 APNs/FCM callback으로 주장하지 않는다.
- PX-T16 managed wire 합성 단위 테스트 PASS(초기 `dotnet run` 경로 오류는 명시 DLL 실행으로 해결). Android/iOS Player 지연 callback probe managed compile은 각각 경고·오류 0이다. 실제 Player 주입 결과는 NOT_RUN이며 커밋 후 재검증한다.
- PX-T16 Android Unity Player 합성 지연 callback·session 검증 시작: 새 전용 AVD/DB에서 실행하며 실제 FCM 지연 전달과 구분한다. 결과는 NOT_RUN이다.
- PX-T16 Android Unity Player 합성 지연 callback 폐기 PASS (`artifacts/unity-android-push-3n9bo6qw`, exit 0): B 활성 후 A session 메시지를 Android callback 큐 경로에 합성 주입해 무시됨을 확인했다. 실제 FCM/JNI 지연 전달로 주장하지 않는다. iOS 동일 검증은 NOT_RUN이다.
- PX-T16 Android Player 합성 이전-session callback 시험 범위와 JNI/FCM 비해당 한계를 공개 evidence에 기록했다. iOS 같은 검증은 NOT_RUN이며 커밋 후 실행한다.
- PX-T16 iOS Unity Simulator 합성 지연 callback·session 검증 시작: 새 Simulator/DB와 local ad-hoc, exact-version cache 사용. 실제 결과는 NOT_RUN이다.
- PX-T16 iOS Unity Simulator 합성 지연 callback 폐기 PASS (`artifacts/unity-ios-push-213zsmr5`, exit 0): 이전 session C# callback 입력 버퍼를 즉시 해제한 뒤 Unity 큐가 폐기했다. 실제 APNs의 지연 전송은 아니다. 같은 실행의 기존 Push/Lifecycle도 통과했다.
- PX-T16 iOS 실제 Player의 합성 이전-session callback 주입 결과와 Swift/APNs 비해당 한계를 공개 evidence에 기록했다. Android/iOS 공통 product 소스는 변경하지 않았다. 커밋 준비.
- PX-T17 최종 범위·문서 감사 시작: Android/iOS Player의 각 Push/Lifecycle·강제 종료·재연결·합성 늦은 callback 및 인증/구매 회귀 결과를 별도 source와 함께 정리한다. 실제 원격 푸시·실기기와 혼동하지 않는다.

### 추가 Task PX-T08~PX-T17 — Unity LOCAL_MOCK Push/Lifecycle

Android 전용 emulator와 iOS Simulator에서 등록·중복·main-thread·background/foreground·연결 복구·session 전환·해제/로그아웃 및 별도 process 종료/pending 복구가 PASS했다. 지연 이벤트는 test-only 합성 callback 주입으로만 검증했다. iOS 연결 차단은 test-only TCP proxy이며 OS 전체 네트워크 차단이 아니다. 실제 FCM/APNs, 실기기 및 실제 원격 지연 callback은 NOT_RUN. [Android evidence](evidence/px-t08-unity-android-mock-push.md), [iOS evidence](evidence/px-t12-unity-ios-mock-push.md).
- PX-T17 README·FEATURE_MATRIX·FINAL_REPORT와 플랫폼 매트릭스에 Android/iOS Unity LOCAL_MOCK Push/Lifecycle 및 별도 restart/pending 시험을 반영했다. 합성 지연 callback·iOS TCP fault와 실제 원격/실기기 미검증을 명시한다.
- PX-T17 BUG-014/015의 오래된 Unity 전체 미검증 문구를 실제 local-mock Player 통과 범위와 실기기/외부 미검증으로 갱신했다. 두 항목의 전체 범위는 OPEN 유지한다.
- PX-T17 플랫폼 evidence의 과거 NOT_RUN 표현을 해당 시험 시점의 범위로 명확히 바꾸고 후속 실제 결과를 가리키도록 정리했다. 각 source 결과는 변경하지 않았다.
- PX-T17 기능 matrix 세부 Push·복구 행과 USER_SETUP의 과거 Unity Push 미검증 표현을 현재 LOCAL_MOCK Player 증거로 정정했다. 실제 알림 클릭·원격 전송·실기기는 미검증이다.
- PX-T17 최종 문서·원장 검사 PASS. 플랫폼별 실제 Player PASS, 합성 지연 callback 및 iOS test-only TCP fault 한계, 실기기·실제 원격 제공자 NOT_RUN을 유지하며 커밋 준비한다. 자동 push하지 않는다.
- PX-T18 P09 6개 PARTIAL 및 CI 고도화 시작: 기준 HEAD 058742d, 기존 Android/iOS LOCAL_MOCK Player 결과는 보존한다. 실제 검증이 없는 항목은 PARTIAL 유지하고 사용자 미추적 파일을 건드리지 않는다.
- P09-T07 CI 작업 시작: Backend·Android·Swift 기본 gate, 명시적인 self-hosted Unity 실제 실행 및 별도 fail-closed Release readiness로 분리한다. Unity 미실행을 PASS로 처리하지 않는다.
- P09-T07 CI 구조를 독립 inventory/backend/Android/Swift 기본 gate와 명시적 self-hosted Unity Editor+Android/iOS Player·strict gate, 별도 Release readiness로 분리했다. 실제 Actions 실행은 아직 NOT_RUN이다.
- P09-T07 YAML 검증 첫 시도는 로컬 Python PyYAML 부재로 미실행(exit 2). 내장 Ruby YAML 파서로 구문을 다시 확인한다.
- P09-T07 Ruby 내장 parser의 workflow YAML 구문 PASS. 필수 시나리오 검사에서 6개 PARTIAL로 exit 1이 확인되어 Release 준비가 아님을 유지한다. CI gate의 미실행/실패 거부를 단위 검증한다.
- P09-T07 Unity 필수 환경 누락, 미실행 Unity gate 및 PARTIAL 시나리오의 Release 차단 테스트 시작.
- P09-T07 CI gate 음성 테스트가 현재 PARTIAL 상태에 영구 의존하지 않도록 격리 fixture로 보완했다. 재검증한다.
- P09-T07 Unity gate에 실제 Editor 실행 전 활성 라이선스 확인을 추가하고 CI 음성 테스트를 기본 inventory gate에 연결했다. 원격 Actions는 NOT_RUN이다.
- P09-T07 CI gate 로컬 음성 테스트 3건 및 YAML 구조·셸 문법 PASS. strict의 Unity push 집계는 아직 DEFERRED_ENV로 명시되며 우회하지 않는다. Actions 원격 job 결과는 NOT_RUN이다.
- P09-T07 CI 구조·음성 테스트 및 현재 한계 문서 커밋 준비. 원격 검증 미실행을 PASS로 기록하지 않는다.
- P09-T01/R49 근거 대조 시작: 기존 Android·iOS Unity LOCAL_MOCK Player 실행이 각각 새 소비 프로젝트·embedded UPM·독립 빌드인지, 제품 소스와 staging이 일치하는지 확인한다. 실행 가능한 현재-source 시나리오 runner도 연결한다.
- R49 기존 Android/iOS Player 실행은 서로 같은 UPM staging hash, Demo 소스 비참조 격리 consumer, 제품 소스 무차이를 확인했다. 현재-source 양 플랫폼 실제 실행만 통과시키는 새 runner의 fail-closed 단위 검사를 시작한다.
- R49 기존 두 플랫폼의 새 Unity consumer import·Player 실행 및 동일 staged 제품 source 증거를 확인해 IMPLEMENTED로 매핑했다. 새 통합 wrapper 자체의 실제 재실행은 별도 NOT_RUN이며 real stores/devices는 미검증이다. manifest·음성 테스트를 시작한다.
- R49 manifest·누락 음성 검사와 새 wrapper fail-closed 단위 2건 PASS. 기존 두 실제 Player 증거와 새 wrapper 자체의 전체 재실행 미실행을 구분해 커밋한다.
- P09-T02/R11 Unity Editor 실제 검증 시작: 라이선스 활성 환경에서 새 격리 consumer의 scene 전환·domain reload enabled/disabled·dispatcher 정리를 확인한다. 기존 test source만으로 PASS 처리하지 않는다.
- R11 격리 Unity Editor test runner에 기존 exact-version cache와 설치 Editor 내장 Test Framework/NUnit 사용 옵션을 추가했다. 전역 환경·기존 프로젝트는 수정하지 않으며 실제 Editor test는 아직 NOT_RUN이다.
- R11 실제 Unity Editor test 2건 PASS/skip 0 (`artifacts/unity-consumer.j4aGtO/results.xml`): scene 전환·domain reload 두 설정과 dispatcher 정리를 실행했다. 다만 기존 test는 객체 재생성·callback 누수 assertion이 없어 R11은 PARTIAL 유지하고 테스트를 강화한다.
- R11 Unity Editor test에 scene 전환 후 SDK 재생성, 이전 session 합성 이벤트 차단, 단일 callback 및 dispose 후 미전달·dispatcher 0개 assertion을 추가했다. 새 테스트는 아직 미실행이다.
- R11 강화된 Unity Editor test FAIL (`artifacts/unity-consumer.upNR5n`, exit 1). 실패 원인을 확인하기 전 R11은 PARTIAL 유지한다.
- R11 실패 원인: 테스트가 dispose 후 이미 해제된 registry에서 이전 session ID를 읽으려 했다. ID를 dispose 전에 캡처하고 실패 시 SDK 객체도 정리하도록 수정해 재검증한다.
- R11 강화 Editor test 두 번째 실행도 FAIL (`artifacts/unity-consumer.d0MHsU`, exit 1). 구체적 실패 원인을 다시 확인한다.
- R11 두 번째 시험 결과: reload-disabled 1건 PASS, reload-enabled는 도메인 리로드를 넘는 테스트 람다 캡처 상태의 NullReference로 FAIL. 테스트 callback을 static 메서드로 바꾸어 세 번째 검증한다.
- R11 강화된 Unity Editor test 실제 2건 PASS/skip 0 (`artifacts/unity-consumer.U1ob4f`), reload-enabled/disabled 각각 완료 marker 확인. 결과 parser가 marker 누락도 거부하도록 보강하고 음성 검증한다.
- R11 Unity XML 결과 판정이 각 domain reload 시험의 완료 marker를 요구하도록 변경했다. 실제 결과와 누락/skip 음성 검증을 시작한다.
- R11 실제 Unity XML의 두 완료 marker 검사 PASS, 누락·skip·중복 음성 검사 PASS. 테스트 코드 및 exact-version 격리 실행기 변경을 커밋한 뒤 clean source에서 재실행한다. R11은 재검증 전 PARTIAL 유지.
- R11 커밋된 테스트 소스로 Unity Editor reload-enabled/disabled 및 scene·callback 재검증 시작. 결과는 아직 NOT_RUN이다.
- R11 커밋된 source a0ba7a5에서 실제 Unity Editor reload-enabled/disabled 2건 PASS/skip 0 (`artifacts/unity-consumer.EfzZEr/results.xml`), 완료 marker 모두 확인. scene·dispose/재생성·이전 session callback 차단 및 dispatcher 1→0 검사 범위로 evidence를 정리한다.
- R11 실제 Unity Editor의 두 reload 경로와 scene·객체·합성 callback 검증을 바탕으로 IMPLEMENTED로 매핑했다. 원격 push·실기기와 구분하고 manifest·원장 검사를 수행한다.
- R11 manifest·누락 음성·원장 검사 PASS. 실제 Editor 2건 및 합성 callback 범위를 evidence와 함께 커밋한다.
- P09-T02/R09 Android JNI·iOS C ABI UTF-8 실제 경계 검증 시작: 한국어·emoji payload가 비동기 callback 이후 동일하게 남는지 확인한다. 실제 검증 전 R09은 PARTIAL이다.
- R09 iOS C ABI test에 한국어·emoji 원시 UTF-8 입력, dispatch 반환 직후 입력 버퍼 덮어쓰기 및 비동기 callback 복사 결과 동일성 assertion을 추가했다. Swift test를 실행한다.
- R09 iOS C ABI 원시 UTF-8·입력 buffer 덮어쓰기·비동기 callback 동일성 Swift test 1건 PASS/skip 0(로컬 macOS host). Android JNI Player 테스트 소스 컴파일을 시작한다.
- R09 Android JNI probe managed compile PASS(경고·오류 0), 실제 Unity AndroidJavaProxy/JNI 실행은 아직 NOT_RUN. 수정 테스트와 runner를 커밋 후 새 전용 AVD에서 확인한다.
- R09 Android JNI UTF-8 실제 Player 검증 시작: 새로운 전용 AVD·DB, 원시 한국어/emoji 및 callback 큐 경계를 확인한다.
- R09 iOS C ABI UTF-8 시험을 macOS host에 그치지 않고 실제 iOS Simulator XCTest에서도 실행하도록 전용 Xcode test target을 추가한다. 검증 전이다.
- R09 iOS Simulator CBridge XCTest target 추가 후 전용 새 Simulator 실행 시작. 기존 macOS host 결과와 구분한다.
- R09 전용 iOS 18.6 Simulator C ABI UTF-8 및 dispatch 입력 buffer 즉시 덮어쓰기·callback 복사 test PASS (`artifacts/r09-ios-20261112203456.xcresult`): 1건, 실패·skip 0. Android JNI Player는 진행 중이다.
- R09 Android Unity Player 실제 JNI 한국어·emoji 왕복 및 callback 지연 처리 PASS (`artifacts/unity-android-e2e-c26jgz32`, exit 0). 전용 AVD 최초 전체화면 안내는 수동으로 닫았다. iOS Simulator C ABI 시험과 함께 근거를 정리한다.
- R09 Android JNI Player 및 iOS Simulator C ABI 실측 모두 PASS. iOS Simulator test target 추가 당시 test-only project 설정이 미커밋이었으므로 명확히 기록하고 해당 target을 커밋한다. 재현 runner·manifest 연결은 별도다.
- R09 Android 실제 Unity JNI 및 iOS Simulator C ABI의 UTF-8 복사·수명 실측을 evidence에 정리하고 IMPLEMENTED로 매핑했다. wrapper의 전체 재실행은 별도이며 실기기/원격 제공자는 미검증이다. manifest를 검증한다.
- R09 manifest·누락 음성·원장 검사 및 wrapper 문법 PASS. 실제 Android JNI Player/iOS Simulator C ABI와 wrapper 미실행을区分해 커밋한다.
- P09-T05/R43 iOS host delegate·Unity 전달 검증 시작: 기존 Simulator host delegate/completion 합성 시험과 Unity iOSHostAdapter→Swift bridge→Unity 이벤트를 별도로 대조한다. 실제 APNs 원격 수신은 제외한다.
- R43 iOS Unity Player test-only host callback probe 및 runner 옵션 작성. 정상 Player 이벤트·중복 억제·main-thread 확인 전에는 PARTIAL 유지한다.
- R43 host callback probe runner 문법 검사 PASS. Unity iOS Simulator Player 및 기존 host XCTest는 새 실행으로 검증한다. 수정 사항 커밋 준비.
- R43 Unity iOS Simulator synthetic host callback 실제 Player 검증 시작. 신규 Simulator·DB·local ad-hoc 및 격리 package cache 사용.
- R43 iOS host callback Player 첫 실행 FAIL (`artifacts/unity-ios-e2e-429_2_xw`, UNITY_EXPORT_FAILED). Unity 프로젝트 compile 오류를 확인한다. 실제 APNs 및 Unity host 전달은 아직 미검증이다.
- R43 원인: Editor compile에서 iOS 전용 `GameBridge.iOSHost` 네임스페이스를 무조건 참조해 CS0234가 발생했다. 테스트 consumer의 iOS 전용 using을 platform 조건으로 감싸 재빌드한다.
- R43 테스트 전용 조건부 using 수정 커밋 준비. 실제 iOS Player 성공은 재검증 후에만 기록한다.
- R43 조건부 using 수정 후 실제 iOS Simulator Player host callback 재검증 시작. 새 Simulator·DB 사용.
- R43 Swift host delegate·completion synthetic XCTest 최신 source 재검증 시작: 새 iOS 18.6 Simulator 사용. Unity host Player와 결과를 분리한다.
- R43 전용 iOS 18.6 Simulator의 Swift host delegate 보존·completion 합성 XCTest 1건 PASS/skip 0 (`artifacts/r43-ios-20261112204204.xcresult`). Unity host callback Player 검증은 별도 진행 중이다.
- R43 Unity iOS Simulator 실제 Player의 synthetic host callback→Swift bridge→Unity 이벤트·중복 억제·main-thread PASS (`artifacts/unity-ios-e2e-f7bwumjl`, exit 0). Swift delegate/completion XCTest와 별도 근거를 대조한다. 실제 APNs 원격 수신은 NOT_RUN이다.
- R43 Swift host delegate/completion Simulator XCTest와 Unity iOS Player synthetic host→Swift→Unity 전달을 각각 실제 PASS해 IMPLEMENTED로 매핑했다. 실제 APNs 원격/실기기는 NOT_RUN이며 새 wrapper 전체 재실행은 별도다.
- R43 재현 runner 문법·manifest·누락 음성·원장 검사 PASS. 두 실제 synthetic 시험의 source와 범위를 구분해 커밋한다.
- P09-T05/R40 실제 OS 권한 거부 검증 시작: 새 Android Player에서 명시적 알림 권한 거부·재요청·등록 차단을 확인한다. iOS 및 Mock 경로는 별도이며 아직 PARTIAL이다.
- R40 Android OS test-only Player 소스 작성: 권한 거부 → 등록 차단 → 재요청 거부 순서를 검사한다. 실제 OS 동작은 미실행이다.
- R40 Android OS permission test managed compile PASS(경고·오류 0). 새 전용 Unity test project를 생성해 Android 권한 선언 후 실제 Player 빌드를 시작한다.
- P09 manifest 현재 48개 IMPLEMENTED, 2개 PARTIAL(R22/R40). CI·최종 보고서의 과거 44/6 표기를 현재 근거로 정정했다. R40 실제 OS 검증은 진행 중이다.
- R40 Android 실제 OS 권한 test APK 빌드 PASS. 새 전용 AVD에서 알림 거부·등록 차단·재요청을 검증한다. 아직 OS 실행은 NOT_RUN이다.
- R40 Android 실제 OS 첫 알림 권한 거부는 DENIED로 반환됐지만 이어진 등록 차단 test가 기대한 PERMISSION_DENIED와 일치하지 않아 FAIL. 정확한 허용된 오류 코드를 식별한다. iOS/Mock 거부는 미실행이다.
- R40 test-only Player에 등록 오류 코드만 출력하는 진단을 추가했다. credential·provider 결과 본문은 출력하지 않으며 실제 재검증 전이다.
- R40 등록 오류 코드 진단을 추가한 두 번째 테스트 APK 빌드 PASS. 이전 AVD/app은 보존하고 새 AVD에서 실제 권한 거부를 재검증한다.
- R40 실제 Android 재시험: OS 권한은 DENIED였으나 등록 API가 Firebase host 미설정 `CONFIG_REQUIRED`를 우선 반환했다. 등록 자체는 차단됐지만 권한 거부에 의한 차단을 증명하지 못해 PARTIAL 유지한다. 테스트 전용 Firebase SDK 의존성만 제공해 재검증한다.
- R40 test-only Firebase SDK dependency 추가 후 실제 Android OS 거부·등록 차단을 세 번째 검증한다. Firebase 앱 설정 및 원격 발송은 하지 않는다.
- R40 test-only Firebase SDK dependency가 포함된 세 번째 Android Player build PASS. Firebase 설정/계정 없이 새 전용 AVD의 OS 거부·등록 차단을 검증한다.
- R40 세 번째 Android OS 검증 부분 PASS (`artifacts/r40-android-os-denial-20261112/markers.log`): 실제 Android 36 알림 권한 두 차례 거부, SDK 등록 `PERMISSION_DENIED` 차단, 재요청 후 DENIED 확인. test-only Firebase SDK dependency만 제공했으며 실 Firebase 연결은 없음. iOS OS 권한 및 Mock 거부 주입은 미실행이므로 R40 전체 PARTIAL 유지.

### P09 작업 일시 중단 체크포인트 (사용자 요청)

- 완료: R09/R11/R43/R49 실제 증거 및 manifest 매핑, 기본 CI/Unity/Release gate 분리와 로컬 음성 검사. 전체 50개 중 IMPLEMENTED 48, PARTIAL 2(R22/R40), NOT_IMPLEMENTED 0.
- R40은 Android 실제 OS 거부/재요청·등록 PERMISSION_DENIED만 부분 PASS, iOS OS/Mock 거부는 NOT_RUN. R22는 PARTIAL. 기존 iOS 26.5 StoreKit local 실패는 별도다.
- `scripts/verify-all.sh --strict-local`은 이번 변경 후 **NOT_RUN**. 원격 GitHub Actions도 NOT_RUN. `harness/run-push-regression.py`의 Unity push 집계는 여전히 DEFERRED_ENV이므로 Release readiness가 PASS될 수 없다. 이 gate를 지우거나 기존 Player 증거를 현재 실행으로 속이지 말고 actual run 검증을 연결할 것.
- 재개: 이 브랜치와 `git status` 확인 후 AGENTS·현재 파일을 읽고 R40 iOS/Mock 및 R22를 계속한다. staging `artifacts/upm-v2-20261112-f1e12b6`, package cache `artifacts/unity-ios-mock.8xjMY7/project/Library/PackageCache`. 기존 Demo·cache·AVD·DB 보존, 자동 push 없음.
- 사용자 요청 중단 전 최종 원장·manifest 검사 PASS. Android 권한 부분 증거, 미완료 CI/strict 및 재개 지점을 로컬 커밋한다. push는 하지 않는다.
- P09-T06 Unity Push 실제 실행 집계 연결 시작: 현재 run에서 Android/iOS Player runner를 각각 새로 실행하고 source·clean 상태·필수 marker를 검증해야만 해당 lane을 PASS로 집계한다. 기존 DEFERRED_ENV를 무조건 성공으로 바꾸지 않는다.
- P09-T06 Unity push lane opt-in 실행기를 추가했다. 같은 실행에서 Android/iOS Player를 새로 실행하고 현재 HEAD·tracked-clean·7개 marker·재연결 거부 및 token 삭제를 확인한다. 실제 새 Player 실행은 아직 NOT_RUN이다.
- P09-T06 Unity push 결과의 stale·dirty·미실행·marker 누락·잘못된 플랫폼 및 잘못된 token 삭제 값 거부를 단위 검증한다.
- P09-T06 결과 검증: 현재 실행 증거의 음성 단위 시험 1건과 CI gate 음성 시험 3건 PASS. 실제 새 Player 실행은 NOT_RUN이며 CI의 기존 600초 제한과 깨끗한 checkout 테스트 조건을 보완한다.
- P09-T06 재검증: Push 증거 단위 1건, CI gate 3건, 집계 13건 PASS; Python·shell 문법과 workflow YAML 구문 PASS. 합성 시험이며 실제 Player 및 GitHub Actions 재실행은 NOT_RUN. 커밋 준비.
- P09-T03/R22 민감정보 노출 검증 재개: 기존 diagnostics 및 Unity 공개 결과 경로와 기존 시험 범위를 조사한다. 전체 경로의 증거가 갖춰지기 전까지 PARTIAL을 유지한다.
- R22 조사: Kotlin/Swift typed diagnostics와 bridge 오류의 기존 synthetic redaction 시험은 있으나 Unity 실제 Player 공개 결과·Backend 오류 로그의 포괄 증거는 없다. 우선 기존 양 플랫폼 bridge 회귀를 재실행하며 PARTIAL을 유지한다.
- R22 Android 재검증 첫 호출은 wrapper 경로 오타로 exit 127, 테스트 미실행. 올바른 android/gradlew로 재실행한다. Swift 시험은 진행 중이다.
- R22 부분 재검증: Android BridgeDispatcher/Diagnostics 및 Swift CBridge/Diagnostics 5건 PASS. synthetic Native 시험이며 Unity Player 전체 및 Backend 오류 로그는 미검증, R22 PARTIAL 유지.
- R22 Backend 오류 로그 검증 시작: 합성 credential을 예외 메시지와 요청에 넣고 HTTP 응답 및 실제 캡처된 logger가 이를 내보내지 않는지 확인한다.
- R22 Backend MockMvc 예외 응답·ApiErrors logger의 synthetic secret 비노출 시험 PASS. 전체 로그·Unity Player 검사는 미완료이므로 R22 PARTIAL. 관련 회귀와 결과 커밋 준비.
- P09-T05/R40 iOS 권한 거부 검증 재개: 기존 test-only Player 및 host adapter의 실제 OS 권한 요청 경로와 전용 Simulator 실행 조건을 확인한다. Android 부분 PASS와 별도로 기록한다.
- R40 iOS 전용 test-only Player 시나리오 작성: 실제 SDK host adapter로 첫 권한 거부·등록 차단·재요청 거부를 검사한다. Simulator 및 OS 실행은 NOT_RUN.
- R40 iOS 검증 준비: 기존 staged SDK와 정확한 패키지 캐시를 새 격리 소비 프로젝트에 복사해 Unity Simulator export를 실행한다. 실제 권한 결과는 아직 NOT_RUN.
- R40 iOS 전용 소비자 Unity Simulator Xcode export PASS (`artifacts/unity-ios-mock.PLDU8j`), 실제 Xcode 빌드 및 OS 권한 실행은 NOT_RUN.
- R40 iOS Xcode Simulator 빌드 시작: 새 derived data와 ad-hoc 서명만 사용하며 Apple 개발 인증은 사용하지 않는다.
- R40 iOS Simulator arm64 Xcode 빌드 PASS; 새 전용 Simulator에서 실제 권한 팝업·등록 차단 검증을 시작한다.
- R40 iOS 새 Simulator 부팅 PASS이나 첫 설치는 잘못 추정한 앱 경로로 실패(파일 없음); Player/권한은 NOT_RUN. 실제 빌드 산출물 경로를 확인해 재시도한다.
- R40 iOS 18.6 실제 Simulator Unity Player 부분 PASS (`artifacts/unity-ios-mock.PLDU8j/player-console.log`): OS 알림 거부, SDK 등록 PERMISSION_DENIED, 재요청 DENIED. Mock 거부 주입은 NOT_RUN이므로 R40 PARTIAL 유지. 실제 APNs 전송은 미검증.
- R40 iOS 부분 검증의 안전한 marker·환경과 최초 설치 실패를 증거 문서에 기록했다. test-only 소비자와 결과 기록 커밋 준비; Mock 거부 미검증 유지.
- P09-T05/R40 Mock 거부 주입 검증 시작: EditorOffline 실제 push.register 거부 분기를 사용하고 permission 응답만 test transport에서 거부로 주입해 Unity 공개 API의 오류 전달을 확인한다.
- R40 managed Mock 거부 주입 PASS: permission DENIED 두 번, 실제 EditorOffline 등록 로직의 PERMISSION_DENIED 확인. Unity Editor/Player 시험은 아니며 OS 수동시험 자동 재현·시나리오 집계가 남아 PARTIAL 유지. 커밋 준비.
- P09-T06 격리 strict-local 전체 검증 시작: 새 테스트 DB·서버·Simulator를 사용한다. 이번 호출에서 Unity Editor 및 두 Push Player opt-in을 제공하지 않으므로 해당 lane은 NOT_RUN/DEFERRED_ENV로 남는다.
- 사용자 요청으로 이전 GameBridge 테스트 전용 Simulator만 종료 시작. 현재 strict 시험용은 유지하며 기기·데이터는 삭제하지 않는다. 앞으로 상태 격리가 불필요하면 테스트 전용 Simulator 재사용.
- Simulator 종료 도중 현재 실행이 새로 만든 기기까지 포함될 가능성을 발견해 일괄 명령을 중단했다(exit 130). 시작 전에 확인한 기존 기기 ID만 지정해 계속하며 현재 시험 기기는 보존한다.
- 기존에 확인한 GameBridge 테스트용 Simulator를 shutdown 완료(삭제·초기화 없음). 현재 strict 관련 기기는 유지; 사용자가 이후 재사용할 수 있다.
- P09-T06 격리 strict-local 종료 1 / 전체 FAIL (`artifacts/verify-all-n8ajxtoz/summary.md`); 외부 13개 WAITING_USER. 세부 실패·미실행을 확인하며 Unity 미실행을 PASS로 기록하지 않는다.
- strict Xcode local StoreKit 실패 상세: 1건이 signal TERM으로 종료(exit 65), 원인은 미확정. 기존 Simulator 종료와 시간대가 겹쳐 영향 가능성을 배제할 수 없어 단독 전용 환경 재검증을 시도한다. Process-recovery는 별도 PASS.
- Xcode local StoreKit + DB 복구 단독 재시험 PASS (`artifacts/xcode-storekit-e2e-he6ows9_`, 1건). 앞선 strict 실행의 signal TERM FAIL은 그대로 보존하며 원인은 확정하지 않는다. strict 전체는 여전히 FAIL.
- strict 실행 결과·Simulator 종료·단독 재시험 기록 커밋 준비. 미완료 R22/R40, Unity Player 새 집계와 외부 검증은 그대로 남는다.
- P09-T03/R22 Unity 공개 결과 합성 비밀값 시험 시작: profile·purchase·push 응답의 미허용 credential 필드가 typed 결과로 유출되지 않는지 기존 managed registry smoke에 추가한다. 실제 Player 검사는 별도 유지.
- R22 managed smoke 첫 실행 컴파일 FAIL: JsonConvert namespace 누락(CS0103), 테스트 미실행. 정규화된 이름으로 수정해 재검증한다.
- R22 managed registry 재시험 PASS: 합성 access/refresh token, purchase proof/receipt, push token이 typed 공개 결과로 나오지 않음을 확인. Player·전체 로그는 미검증이므로 R22 PARTIAL 유지. 커밋 준비.
- P09-T06 현재 HEAD Unity Push 양 플랫폼 집계 실측 시작: 기존 앱 데이터를 보존해야 하므로 미사용 전용 Android AVD가 필요하다. 새 격리 기기와 iOS Simulator에서 같은 run의 실제 LOCAL_MOCK Player 결과를 확인한다. 외부 FCM/APNs는 미실행이다.
- P09-T06 동일 실행 Unity Push 집계 PASS(2 Player): source f40f8d5, Android `artifacts/unity-android-push-0b67f62g`, iOS `artifacts/unity-ios-push-ejpifgez`, 양쪽 tracked-clean·필수 marker 확인. Android 최초 전체화면 안내 수동 처리; hosted CI/실제 FCM·APNs는 미검증.
- 양 플랫폼 결과 파일 재확인 첫 호출은 작업 디렉터리 오타로 실행되지 않았다. 올바른 저장소 경로에서 재확인한다.
- 양 result JSON 재확인: 두 Player PASS·동일 source f40f8d5·tracked-clean·token 0, iOS network는 LOCAL_TRANSPORT_FAULT로 구분. 사용한 테스트 기기 shutdown 완료, 삭제 없음. 증거·CI 문서 커밋 준비.
- P09-T05/R40 Mock 거부 회귀 집계 연결 시작: 독립 managed 시험을 strict Push 필수 lane으로 추가한다. 환경 누락·실패·marker 없음은 PASS로 처리하지 않으며 OS 수동시험은 별도 PARTIAL 유지.
- R40 managed Mock 거부 단독 시험과 집계 단위 13건 PASS, Python 문법 PASS. Push runner 전체에 새 lane이 실제 나타나는지 확인한다.
- Push 독립 집계 exit 2 (`artifacts/push-regression-0qh7drmi`): 새 mock-permission-denied 1건 PASS, 환경 미제공 lane은 DEFERRED_ENV. 전체 통과가 아니다. R40 OS 자동 재현은 PARTIAL 유지. 커밋 준비.
- P09-T07 Unity self-hosted preflight 보완 시작: 새 필수 Mock 권한 시험과 기존 managed 검증에 필요한 UNITY_EDITOR_PATH를 조기에 확인하고 환경 요구를 문서화한다.
- CI preflight shell 문법과 기존 음성 3건 PASS. 존재하지 않는 Editor 경로도 실제 실행 전 DEFERRED_ENV로 거부하는 별도 음성 시험을 추가한다.
- CI preflight 음성 시험 4건 및 shell 문법 PASS; GitHub Actions 실행은 NOT_RUN. 변경 커밋 준비.
- P11 진행 증거 정합성 점검 시작: R40 기존 Android/iOS 부분 증거와 현재 Mock 실행 상태, CI·최종 보고서의 과거 미검증 표현을 대조한다.
- 문서 정합성 1차 수정 및 원장 검사 PASS: 최신 iOS/Android OS 권한, Mock 거부, strict 실패 및 단독 재시험을 반영했다. 나머지 기능 matrix의 이전 Unity 미실행 표현도 증거와 대조한다.
- P11 문서 정합성 검사: 원장·50개 manifest 구문 검사와 diff 공백 검사 PASS. 과거 산출물 결과는 당시 상태로 명시하고 최신 LOCAL_MOCK·실제 플랫폼 범위를 구분했다. 커밋 준비.
- P09-T06 strict 격리 orchestration timeout 점검 시작: 실제 Unity 양 플랫폼 opt-in 시 내부 실행 제한과 외부 900초 제한 충돌 가능성을 검토한다.
- P09-T06 제한 충돌 확인: opt-in Push에 내부 3600초를 허용하면서 격리 전체는 900초에서 중단한다. opt-in 때만 외부 여유를 늘리고 환경별 단위 검증을 추가한다.
- strict timeout 환경별 단위 1건·집계 13건 PASS, Python 문법 PASS. 실제 긴 전체 실행은 NOT_RUN; CI 기본 검사에 새 단위를 포함하고 커밋 준비.
- P09-T03/R22 Unity Player 공개 결과 점검 확장 시작: test-only consumer에서 합성 개발키가 인증·구매·진단 공개 결과에 포함되지 않는지 확인한다. 실제 access/refresh token 및 전체 로그 검사는 별도로 유지한다.
- R22 test-only 양 플랫폼 consumer에 합성 개발키 결과 비노출 검사와 필수 marker를 추가했다. 컴파일 및 Player 실행은 아직 NOT_RUN.
- R22 Android consumer managed compile PASS(경고·오류 0), Python runner 문법 PASS. iOS 조건부 managed compile을 확인한다. 실제 Player는 미실행.
- R22 양 플랫폼 test-only consumer managed compile PASS(각 경고·오류 0). 실제 Unity Player 재실행은 NOT_RUN이며 clean-source 실행을 위해 테스트 코드를 먼저 커밋한다.
- R22 양 플랫폼 실제 LOCAL_MOCK Player 재검증 시작: source cc3cc60과 빈 Android 전용 AVD·격리 iOS Simulator를 사용한다. 합성 개발키 검사이며 실 provider token 검증은 별도다.
- R22 Android Player 재검증 FAIL (`artifacts/unity-android-e2e-419abzrk`): `UNITY_RESULT_REDACTION_MISSING`. 검사 자체 실패와 로그 필터 누락 중 원인을 조사한다. iOS는 아직 NOT_RUN.
- R22 Android 실패 원인: runner가 완료 marker 전 새 marker를 검사하고 logcat 필터도 이를 제외했다. Player 결과는 미확정이다. 필터·검사 순서를 수정하고 미완료/누락 음성 시험을 추가한다.
- Android runner marker 필터·대기 순서 수정 후 단위 2건/Python 문법 PASS. 실제 Player는 재실행 전이며 새 빈 AVD가 필요하다. 커밋 준비.
- R22 Android/iOS Player 재검증 재시작: 수정된 polling을 적용한 source ffb7842 기준으로 빈 Android AVD와 별도 iOS Simulator를 사용한다. 앞선 실패는 보존한다.
- R22 Android LOCAL_MOCK Unity Player 재검증 PASS (`artifacts/unity-android-e2e-m62mfexg`): source 7156dac tracked-clean, 인증·구매·진단 결과의 합성 개발키 부재 및 marker 확인. 최초 전체화면 안내 수동 처리. 실제 token·iOS는 별도.
- R22 iOS LOCAL_MOCK Player 실제 재검증 시작: source ccec48d, 격리 Simulator에서 합성 개발키 결과 비노출과 기존 인증·구매 흐름을 함께 확인한다.
- R22 iOS LOCAL_MOCK Unity Simulator Player PASS (`artifacts/unity-ios-e2e-nz5fz8r5`): 인증·구매·진단 결과의 합성 개발키 부재. 실제 provider token 및 전체 로그 누락 여부는 별도이며 R22 PARTIAL 유지.
- R22 두 Player 실행의 source/clean 결과를 재확인하고 사용한 전용 Simulator·AVD를 shutdown했다(삭제 없음). 부분 증거와 기록 커밋 준비.
- R22 기존 R09/R43 회귀 호환성 조사 시작: 공유 runner의 새 필수 marker가 별도 UTF-8/host consumer에도 적용되는지 확인한다.
- 공유 consumer 호환성 문제 확인: R09 Android UTF-8 및 R43 iOS host 전용 consumer에 새 필수 marker가 없어 현재 runner가 최종 성공을 거부한다. 두 consumer에도 실제 결과 검사를 적용한다.
- R09/R43 전용 consumer에도동일한 합성 개발키 검사와 marker를 추가했다. marker 단위 2건 PASS; 두 조건부 managed compile 및 실제 Player는 아직 미확인이다.
- R09 UTF-8·R43 host consumer 조건부 managed compile 양쪽 PASS(각 경고·오류 0). 변경 후 실제 Player 재실행은 NOT_RUN. 공유 consumer marker 누락을 막는 inventory 검사를 추가한다.
- 네 consumer marker inventory 포함 단위 3건과 원장 검사 PASS. R09/R43 변경 후 실제 Player 재실행은 NOT_RUN이며 기존 증거는 보존한다. 커밋 준비.
- P09-T02/R43 host callback 전용 consumer 실제 Player 재검증 시작: 새 redaction 검사와 기존 합성 host callback·중복·main-thread 흐름을 함께 확인한다.
- R43 수정 iOS host callback Unity Player 재실행 PASS (`artifacts/unity-ios-e2e-fj2ddrvp`): 합성 callback·중복·main-thread와 합성 개발키 결과 비노출 확인. 실제 APNs는 미검증.
- R43 test Simulator shutdown 완료(데이터 보존), tracked-clean 재확인. 결과 기록 커밋 준비.
- P09-T02/R09 UTF-8 전용 Android consumer 실제 Player 재검증 시작: 빈 전용 AVD에서 JNI 문자열·개발키 결과 비노출과 기존 흐름을 확인한다.
- R09 수정 UTF-8 Unity Android Player 재실행 PASS (`artifacts/unity-android-e2e-jtraqi0j`): JNI 한글/emoji 및 합성 개발키 결과 비노출; 최초 전체화면 안내 수동 처리. 실제 기기·제공자는 별도.
- R09 전용 AVD를 데이터 삭제 없이 shutdown했다. tracked-clean 및 검증 결과 기록 커밋 준비.
- P09-T03/R22 Native LOCAL_MOCK 세션 토큰 결과 검사 확장 시작: 테스트 전용 메모리 저장소에서 해당 실행의 synthetic access/refresh token을 읽어 실제 bridge 응답·결과에 포함되지 않는지 확인한다. 토큰 값은 출력하지 않는다.
- R22 Native 테스트 컴파일 PASS; Swift 대상은 로컬 Backend opt-in이 없어 1건 SKIP이며 검증 PASS가 아니다. 격리 테스트 DB/서버에서 양 플랫폼 대상 시험을 실제 실행한다.
- R22 Native LOCAL_MOCK 합성 access/refresh token 값 자체의 bridge 결과 비노출 검증: Android 1건·Swift 1건 PASS (`artifacts/r22-native-9f0p4b_t`), skip 0. 실제 provider credential과 전체 로그는 미검증, R22 PARTIAL 유지.
- R22 토큰 비교 시험을 기존 local purchase regression의 Android/iOS 실행 대상에 연결해 재실행 가능하게 한다. 별도 synthetic 결과와 실제 제공자 검증을 혼동하지 않는다.
- R22 회귀 filter 연결 후 Python/원장 검사 PASS. 한 개만 실행되고도 세 시험 묶음이 PASS되는 것을 막기 위해 각 언어의 필수 3건 수를 확인하도록 보강한다.
- P09-T06 새 Native token 회귀 포함 격리 strict 재검증 시작: Android/Swift 각 3건 필수 집계를 확인한다. Unity Player opt-in은 제공하지 않아 해당 lane은 DEFERRED_ENV로 남는다.
- strict 진행 중 local integration 중간 결과: Android JUnit 3건·Swift 3건, 실패/skip 0 (`artifacts/purchase-regression-n4qmg2ka`). 전체 집계는 아직 진행 중이다.
- strict 구매 하위 집계 전 항목 PASS: Android/Swift local integration 각 3건, Xcode local DB 및 process recovery 각 1건. 전체 strict와 별개이며 아직 진행 중.
- 최신 strict 전체 FAIL/exit 1 (`artifacts/verify-all-r1ely80_/summary.md`), 외부 13 WAITING_USER. 구매 하위는 모두 PASS이나 전체 실패·미실행 원인을 확인한다.
- 최신 strict 세부: 구매 전체와 mock-permission PASS, Unity Push DEFERRED_ENV, Editor NOT_RUN, R22/R40 PARTIAL 및 기존 P05-T03 FAIL. 사용한 테스트 Simulator shutdown(데이터 보존).
- Native token assertion과 regression 3건 필수 집계, 최신 strict 결과·최종 보고서 반영 및 원장/Python/diff 검사 PASS. 커밋 준비. 실제 제공자·전체 로그는 미검증.
- P09-T01 시나리오 manifest 증거 연결 시작: R22의 새 Native token 및 Unity 결과 부분 증거와 R40 OS/Mock 부분 증거를 후보 suite에 연결하되 PARTIAL 유지.
- R22/R40 부분 증거 연결 후 manifest·음성·원장/diff 검사 PASS. 제품 시험 재실행이 아니며 두 시나리오 PARTIAL 유지. 커밋 준비.
- R22 Android 세션 token 음성 시험의 사전조건 보강 시작: 토큰 저장소가 비어 있을 때 비교가 조용히 생략되는 경우를 방지한다.
- R22 Android token 존재 사전조건 테스트 컴파일 PASS. 격리 Native token 회귀 재현 runner를 추가해 실제 실행과 skip/0건 거부를 확인한다.
- R22 격리 재현 runner 실행 PASS: Android/Swift 합성 세션 token 비교 각 1건, skip 0 (`artifacts/r22-native-vdwala6w`). 실제 provider는 별도. opt-in 누락 음성 검사를 확인한다.
- R22 전용 runner opt-in 누락 exit 2·Python/원장/diff 검사 PASS. 부분 manifest와 증거에 재현 명령을 연결하고 커밋 준비한다.
- P09-T03/R22 합성 세션 token의 Backend 로그 노출 검증 시작: 전용 격리 runner에서만 테스트가 서버 로그와 access/refresh token을 메모리로 비교하고 결과 marker를 요구한다.
- R22 전용 격리 실행 PASS (`artifacts/r22-native-37ca4aes`): Android/Swift 각 합성 access/refresh token·개발키의 bridge 결과 및 Backend 로그 비노출 marker 확인. 실제 제공자·전체 로그 범위는 별도다.
- R22 로그 marker 누락·잘못된 값 거부 단위 1건과 Python/원장 검사 PASS. helper 보완 후 격리 실행을 다시 확인한다.
- R22 marker helper 적용 후 격리 양 Native 재실행 PASS (`artifacts/r22-native-bpyoimew`), 각 1건/skip0 및 synthetic token·개발키 서버 로그 비노출 marker 확인. R22 전체 PARTIAL 유지, 커밋 준비.
- P09 전체 coverage 재확인: `check-required-coverage.py` exit 1, PARTIAL 2·NOT_IMPLEMENTED 0. 예상된 미완료이며 통과가 아니다. 미추적 Demo와 Python cache만 남아 있다.
- 부분 coverage 검사 및 미추적 파일 보존 결과 기록 커밋 준비.
- P09-T03/R22 synthetic 구매 증빙의 HTTP 응답·Backend 로그 검증 시작: 실제 구매 없이 fake verifier와 전용 sandbox DB에서 실패 및 성공 응답을 검사한다.
- R22 구매 증빙 테스트 Kotlin 컴파일 PASS. 전용 sandbox DB에서 실제 fake HTTP 시험 1건과 로그 수집을 실행한다.
- R22 synthetic Google 구매 증빙 HTTP/로그 1건 PASS/skip0 (`artifacts/r22-proof-0bcej9x1`): 성공·거부 응답 및 캡처된 Backend 로그에 증빙·세션 token 비노출 확인. 실제 Play는 미검증.
- R22 구매 증빙 검사 서식을 정리하고 재컴파일한다. 실제 HTTP 시험 PASS는 서식 정리 전 소스에서 확인했다.
- 구매 증빙 시험 서식 정리 후 Kotlin 재컴파일·diff 검사 PASS. 전체 로그/실제 provider 미검증으로 R22 PARTIAL 유지; 커밋 준비.
- P11-T01 작업 원장 정합성 점검 시작: 이미 RESOLVED인 ENV-002를 사유로 P08-T04가 DEFERRED_ENV인 행을 현재 Player 증거와 완료 기준에 맞춰 재평가한다.
- P08-T04는 독립 staged consumer Android/iOS 실제 Player 증거가 있어 ENV 대기가 아닌 PARTIAL로 정정했다. bootstrap 문서 그대로의 재설치 등 완료 기준은 별도이며 PASS가 아니다.
- P08-T04 상태·집계 정정 후 원장 및 음성 검사 PASS. 제품 시험이 아니며 커밋 준비.
- P09-T08 R22 runner fail-closed 상태 점검 시작: 전용 DB 부재를 제품 FAIL로 잘못 분류하지 않고 DEFERRED_ENV로 보존하는지 확인한다.
- R22 runner 환경 대기·marker 음성 단위 2건 및 Python 문법 PASS. 실제 포트 점유 시 exit 2를 확인하고 정상 격리 재실행한다.
- R22 runner 포트 점유 시 DEFERRED_ENV/exit 2, 정상 격리 실행 Android·Swift PASS (`artifacts/r22-native-b5e3facc`). 환경 대기와 제품 실패를 구분했다. 커밋 준비.
- P08-T04 샘플 설치 절차 점검 시작: Unity CLI status는 Pipeline 연결 Editor 0건(exit 6); 해당 명령을 원장 기록보다 먼저 실행한 순서 누락을 기록한다. 격리 프로젝트에서 sample과 의존성을 확인한다.
- P08-T04 Offline Demo 격리 Editor 검증 시작: staged UPM sample·uGUI를 새 소비 프로젝트에 복사하고 EventSystem·빈 GameObject를 구성해 Editor Play의 초기화·모의 구매를 확인한다. Package Manager UI import/렌더링은 별도다.
- P08-T04 staged Offline Demo Editor test 및 격리 runner 초안 작성, shell 구문 PASS. 실제 Unity Editor 실행은 아직 NOT_RUN이다.
- P08-T04 staged Offline Demo Unity Editor Play fake 흐름 1건 PASS (`artifacts/offline-sample.wpOk2c/results.xml`): 초기화·모의 로그인·상품 목록·100코인 구매 callback. package-manager UI import 및 실제 화면 렌더링 검사는 아님.
- P08-T04 sample 실행 보고서 1건 PASS·skip0 및 완료 marker 재확인. 빈 결과·skip·실패·marker 누락을 거부하는 runner 판정 검사를 보강한다.
- sample 보고서 판정 음성 단위 1건 PASS, 실제 기존 NUnit 결과 재검사 PASS, shell 구문 PASS. 강화 runner로 새 격리 Editor 실행을 재확인한다.
- 강화된 Offline Demo 격리 Unity Editor Play 재실행 1건 PASS/skip0 (`artifacts/offline-sample.JGRMHJ/results.xml`); 화면 렌더링·Package Manager UI는 미검증. 샘플/기능 문서의 과거 라이선스 표현을 수정한다.
- P08-T03 sample README 변경을 포함한 새 UPM staging 생성 시작: 기존 검증된 Native 산출물을 사용하고 기존 staging은 보존한다. 새 staging의 Editor 실행은 별도다.
- 새 UPM staging `artifacts/upm-offline-sample-20261112`의 XCFramework arch/C ABI·110개 파일 checksum PASS. 기존 Native 산출물 재사용이며 새 staging Editor 실행은 아직 NOT_RUN.
- 새 staging Offline Demo 격리 Unity Editor Play 1건 PASS/skip0 (`artifacts/offline-sample.0FsGva/results.xml`). 실제 화면 렌더링·Package Manager UI·실제 결제는 범위 밖이다.
- 새 staged SDK와 현재 checkout 제품 소스 일치, sample 결과 음성 단위 1건·workflow YAML·diff 검사 PASS. 실제 화면/패키지 관리자 UI는 계속 미검증이다.
- Offline Demo Editor 부분 증거·새 staging hash·제한 범위를 문서화했다. P08-T04는 Package Manager UI 및 Native Demo 재현이 남아 PARTIAL. 커밋 준비.
- P08-T03 staging 블로커: `upm-offline-sample-20261112` Native 산출물은 직전 f1e12b6 staging과 81개 중 41개가 달라 최신 Native와 동등하다고 볼 수 없다. 기존 검증본의 Native 산출물로 새 staging을 다시 만든다. 해당 후보는 최신 패키지로 사용하지 않는다.
- f1e12b6 검증본의 Native payload를 사용한 새 staging `artifacts/upm-offline-sample-current-20261112` 생성·110개 checksum PASS. Native 동일성 및 새 Editor 실행은 아직 미확인.
- 새 staging Native payload 81개 byte 동일·checkout 소스 일치 PASS. 이 staging의 Offline Demo Editor test를 재실행한다.
- 올바른 Native payload staging에서 Offline Demo Unity Editor 재검증 1건 PASS/skip0 (`artifacts/offline-sample.Tg04iK/results.xml`). 이전 오래된 Native 후보와 구분해 증거·재개 경로를 수정한다.
- 재패키징 증거·CI staging 경로 정정 후 원장·manifest·diff 검사 PASS. 이전 후보 오류를 보존하고 관련 기록만 커밋 준비한다.
- P08-T04 sample runner의 staging 소스 일치 강제 시작: checksum만 맞는 오래된 패키지가 현재 checkout 테스트로 오인되지 않게 한다.
- sample runner에 이전 stage 투입 음성 시험 exit 1: checksum이 정상이어도 checkout source 불일치를 거부했다. 의도된 음성 결과이며 새 stage 양성 시험을 실행한다.
- 현재 source 일치 stage의 sample runner 양성 재실행 1건 PASS/skip0 (`artifacts/offline-sample.k1uWmY/results.xml`). 과거 stage 거부와 분리해 기록, 커밋 준비.
- P08-T04 Native Demo Editor 안전 경계 시험 시작: staged sample을 격리 프로젝트에 추가해 Editor에서 Native 동작이 차단되고 안내·버튼 상태가 명확한지 확인한다. Native Player 실제 흐름은 별도다.
- Native Demo Editor guard test 초안·두 marker fail-closed 음성 단위 1건·Python/shell 구문 PASS. 실제 Editor 실행은 아직 NOT_RUN이다.
- Native Demo Editor guard와 Offline fake flow를 함께 Unity Editor에서 1건 PASS/skip0 (`artifacts/offline-sample.TwukI1/results.xml`): Native 사용 안내·버튼 비활성 확인. Native Player 흐름 및 실제 렌더링은 미검증.
- 양 sample 결과 음성 단위·실제 XML 재검사·원장 PASS이나 diff 공백 검사 1건 FAIL(후행 공백). 공백만 제거하고 재검사한다.
- 공백 수정 후 sample 음성·실제 XML·원장/diff 검사 PASS. Native Demo Player·실제 화면은 계속 미검증, 커밋 준비.
- P08-T04 Native Demo Android LOCAL_MOCK Player 시험 시작: staged sample을 빈 소비 프로젝트에 가져와 runtime 입력·버튼 callback·mock Backend/DB 흐름을 검증한다. 실제 화면 터치·결제는 별도다.
- P08-T04 Native Demo Android test-only probe와 격리 runner option 작성, Python 문법 PASS. 실제 Unity 컴파일·Player는 미실행이며 managed compile을 확인한다.
- Native Demo Android test-only probe managed compile PASS(경고·오류 0). marker 필터 및 혼합 probe 거부를 확인한 뒤 clean-source Player를 실행한다.
- Native Demo marker/filter 포함 단위 4건 PASS, UTF-8/Native probe 동시 선택 exit 2 확인. 실제 Android Player는 NOT_RUN; clean-source 시험 전 코드 커밋 준비.
- P08-T04 Native Demo Android Player 실제 검증 시작: source 337d4ec 제품/테스트 코드와 최신 staged SDK, 빈 전용 AVD·격리 DB를 사용한다. 시작 기록을 커밋한 뒤 실행한다.
- P08-T04 Native Demo Android Unity LOCAL_MOCK Player PASS (`artifacts/unity-android-e2e-j7ir0wt8`): staged sample 설정·초기화·로그인·상품·모의 구매·로그아웃 callback 및 DB 원장 1건/100, 개발키 입력 삭제 확인. 최초 전체화면 안내는 수동 처리; 화면 터치·실제 Play 미검증.
- Native Demo test AVD는 데이터 삭제 없이 shutdown했다. Android 부분 증거·기능 matrix 및 최종 보고 반영, iOS Player/시각 QA는 미검증으로 커밋 준비.
- P08-T04 Native Demo iOS Simulator LOCAL_MOCK Player 검증 시작: Android와 같은 staged sample·UI callback·격리 Backend/DB 경로를 별도로 구현한다. 실제 Apple/APNs는 범위 밖이다.
- Native Demo iOS test-only probe·runner option 초안 작성, Python 문법 및 전문 probe 동시 선택 거부 PASS. 조건부 컴파일과 실제 Player는 미실행이다.
- Native Demo iOS probe managed compile PASS(경고·오류 0). 실제 Simulator Player는 NOT_RUN; clean-source 실행 전 코드 커밋 준비.
- P08-T04 Native Demo iOS Simulator Player 실제 검증 시작: source bf1c526 제품/테스트 코드와 최신 staged SDK·격리 DB를 사용한다.
- Native Demo iOS 첫 검증 FAIL (`artifacts/unity-ios-e2e-kd8mlvys`): UNITY_EXPORT_FAILED, Player 미실행. 격리 Unity 빌드 오류를 확인한다.
- Native Demo iOS export 원인 확인: `GameBridge.NativeDemo.iOS` asmdef가 `GameBridge.Runtime` 직접 참조를 누락해 `GameBridgeClient` CS0246. test-only가 아닌 실제 sample 패키지 버그로 수정한다.
- Native Demo iOS asmdef에 Runtime 직접 참조 추가 및 assembly contract 음성 방지 검사 작성. Unity 실제 export는 재실행 전이다.
- iOS sample asmdef 직접 참조 단위 1건·workflow YAML·diff 검사 PASS. 수정 제품 소스를 포함한 새 staged UPM을 생성한다.
- 수정 asmdef 포함 새 UPM staging `artifacts/upm-native-sample-fix-20261112` 생성, XCFramework 검증·110개 checksum PASS. 실제 iOS Player 전 수정 코드 커밋 준비.
- P08-T04 Native Demo iOS Simulator 재검증 시작: Runtime asmdef 수정 source a761007 및 새 stage를 사용한다. 첫 export FAIL은 보존한다.
- P08-T04 수정 Native Demo iOS Unity Simulator LOCAL_MOCK Player PASS (`artifacts/unity-ios-e2e-56e5wx05`): 설정·초기화·로그인·상품·모의 구매·로그아웃 callback, main thread, 개발키 삭제 및 DB 1건/100. 실제 터치·Apple 거래·APNs 미검증.
- 수정 iOS Native Demo 결과 source aa9c155 tracked-clean, 테스트 Simulator shutdown(데이터 보존). 새 stage Native payload는 이전 검증본과 81개 byte 동일; 동일 stage에서 Editor sample 회귀 재확인한다.
- Native Demo 수정 최신 stage에서 Offline fake/Native Editor guard 회귀 1건 PASS (`artifacts/offline-sample.GHbI58/results.xml`). iOS 부분 증거·stage 경로와 기존 실패 이력을 반영한다.
- Native Demo iOS 증거·sample Editor 결과·현재 stage 경로 정리 후 원장/manifest/diff PASS. 원격 provider·시각 QA는 미검증, 커밋 준비.
- P09-T07 Unity self-hosted gate에 staged Offline/Native Editor sample 회귀 연결 시작: 정확한 패키지 cache를 명시적으로 요구하며 sample skip을 성공으로 처리하지 않는다.
- CI sample gate 연결 후 shell 문법 및 기존 preflight 음성 4건 PASS. package cache 경로 누락의 직접 음성 검사를 추가한다.
- CI preflight 음성 5건·shell/원장/diff PASS. self-hosted 전체 및 GitHub Actions 실행은 NOT_RUN이며 커밋 준비.
- P11-T03 최신 staging·strict 소스 기준 정합성 확인 시작: 이후 재개 시 과거 staging을 최신 제품으로 사용하지 않도록 체크포인트를 갱신한다.
- 현재 stage/cache와 strict 실행 source 명시 후 원장/diff 검사 PASS. 새 source의 strict 미실행은 별도로 유지하며 커밋 준비.
- P09-T07 self-hosted strict 격리 실행 연결 점검 시작: CI gate가 필수 DB·local server fixture를 스스로 준비하는지 확인한다.
- P09-T07 확인: Unity gate의 direct strict 호출은 test DB·server opt-in을 준비하지 않는다. 기존 격리 orchestration을 연결하고 전체 gate 시간 여유를 반영한다. 실제 self-hosted 실행 전이다.
- CI 격리 strict 연결 후 preflight 5건·timeout 단위 1건·shell/YAML PASS. mock fixture로 실제 gate가 orchestration 실패를 전파하는지 확인한다.
- CI 격리 fixture 첫 실행 FAIL: mock unity shell 문자열 따옴표 오류로 Python test import 불가. 실제 CI/Unity는 미실행이며 fixture 문법을 수정한다.
- CI 격리 fixture 수정 후 6건 PASS/skip0: orchestration 호출 및 실패 전파 확인. 실제 self-hosted/GitHub Actions는 NOT_RUN, 커밋 준비.
- P09-T07 격리 CI의 Editor·Native artifact 경로 일치 점검 시작: 선택한 Editor와 현재 staging이 strict의 내부 경로에서도 유지되는지 확인한다.
- CI 경로 결함 확인: helper가 지정 Editor를 무시하고 독립된 오래된 Native artifact 기본값을 사용한다. 선택 Editor와 staging 내부 산출물을 사용하도록 수정한다.
- 지정 Editor/Newtonsoft 경로 단위 2건, CI fixture 6건 및 Python/shell 구문 PASS. staged Native 경로가 실제 strict 호출에 전달되는지도 fixture로 확인한다.
- CI 경로 전달 fixture 6건·Editor/timeout 2건 및 원장/diff PASS. 실제 self-hosted 전체는 NOT_RUN, 커밋 준비.
- P09-T07 전체 Unity CI gate 로컬 실행 시작: 최신 stage·Editor 및 별도 빈 Android AVD 2개·격리 DB/Simulator를 사용한다. 기존 R22/R40 PARTIAL과 P05-T03 FAIL이 있어 전체 성공을 미리 주장하지 않는다.
- P09-T07 첫 전체 Unity CI gate exit 2: Editor 2건·sample 1건 PASS 후 Android baseline `TARGET_NOT_AN_ONLINE_EMULATOR` DEFERRED_ENV (`artifacts/unity-android-e2e-ds3m3hkh`). Unity의 ADB 재시작 후 기기 재검색을 확인한다. 후속 Player/strict는 NOT_RUN.
- Android baseline의 최초 기기 조회는 재시작 직후 바로 실패하고 후반 설치 전 조회만 재시도한다. Push runner도 동일 패턴이어서 두 최초 조회에 기존 안전한 재검색을 적용한다.
- ADB 재검색 단위 3건 PASS: offline 복구, 시간 초과 환경 대기, 다른 기기/기존 앱 즉시 거부. Python/원장/diff PASS; clean-source 전체 gate 재시도 전 커밋 준비.
- P09-T07 전체 Unity gate 재실행 시작: 최초 실패에서 앱이 설치되지 않은 동일 전용 AVD 두 개를 재사용한다. 이전 DEFERRED_ENV는 보존한다.
- P09-T07 전체 Unity CI gate 로컬 재실행 종료 1/전체 FAIL (`artifacts/verify-all-4r3l36i6/summary.md`). 기본 Android/iOS Player와 Push 양 플랫폼 실행 뒤 strict 결과를 확인한다. 두 Android 최초 안내 수동 처리, GitHub Actions/실제 provider 아님.
- 최신 전체 gate 세부: Unity Editor 2건·양 플랫폼 기본/Push Player PASS, strict는 R22/R40 PARTIAL 및 기존 P05-T03 FAIL로 전체 FAIL; 외부 13 WAITING_USER. Player 4개 source e703f43 tracked-clean, strict dirty는 기존 미추적 파일 포함 기준. 테스트 AVD 2·Simulator 3 shutdown, 데이터 보존.
- P09-T07 로컬 gate 증거 정리 중: isolated helper가 Editor opt-in 상태와 무관하게 Editor 분리 문구를 출력한 점을 실제 선택 상태로 정정한다. 기존 검증 판정에는 영향 없다.
- helper 안내 문구 수정 후 Python/timeout 단위 2건·원장/diff PASS. 전체 gate는 수정 전 source e703f43에서 FAIL이며 새 source 전체 재실행은 NOT_RUN. 정제 증거 커밋 준비.
- R22 최신 로컬 gate Backend 로그 4개를 합성 `mock:<UUID>` token/증빙 패턴으로 재검사해 노출 없음. 실제 credential·다른 형식·Player 전체 로그는 범위 밖이다. 사전 검증 기록을 누락해 즉시 보완한다.
- R22 전용 격리 runner에 LOCAL_MOCK push token/구매 proof 형태의 서버 로그 검사를 추가한다. 다른 형식과 실제 provider 검증을 대신하지 않는다.
- 합성 token/proof 패턴 탐지·marker·환경 대기 단위 3건 PASS, Python 문법 PASS. 격리 Native/Backend 실제 검증을 재실행한다.
- R22 전용 격리 재실행 PASS (`artifacts/r22-native-7r45s8ui`): Android·Swift 합성 session token, 개발키 및 mock push/proof 형태 서버 로그 검사. 실제 provider·다른 형식·전체 Player 로그는 별도, PARTIAL 유지.
- R22 synthetic mock credential 검사·결과 JSON·원장/diff PASS. 커밋 준비; 전체 로그·실제 provider 상태는 미완료로 둔다.
- P09-T03/R22 Unity LOCAL_MOCK runner 로그 검사 보강 시작: Android/iOS 기본·Push의 원시 Unity/server 로그에서 synthetic mock token/proof 형태를 검사한다. 실제 provider 및 다른 형식은 별도다.
- Unity 네 runner의 synthetic mock credential 검사 추가 후 Python 문법·기존 marker 4건 PASS. 유출된 가상 token이 필터되기 전에 실패하는 음성 시험을 추가한다.
- Unity raw log mock credential 주입 거부 포함 단위 5건·Push 증거 단위 1건 PASS. 중복 정규식을 공통 helper로 통일하고 재검증한다.
- 공통 synthetic credential 패턴의 R22 단위 3건 및 격리 Native 재실행 PASS (`artifacts/r22-native-7__7z_m1`). Unity runner 추가 검사는 아직 실제 Player 재실행 전, 커밋 준비.
- P09-T03/R22 강화 로그 검사 iOS 기본 LOCAL_MOCK Player 재검증 시작: source 4e10efc runner와 최신 stage를 사용한다. synthetic mock 패턴에 한정한다.
- R22 강화 synthetic mock 로그 검사의 iOS 기본 LOCAL_MOCK Player PASS (`artifacts/unity-ios-e2e-o2mypwsg`), tracked-clean. Android 및 양 Push 수정 후 실제 실행은 별도 NOT_RUN.
- 사용한 iOS Simulator shutdown, 데이터 보존. iOS 부분 결과를 기록하고 Android/Push 검증은 별도로 유지하며 커밋 준비.
- P09-T03/R22 강화 로그 검사 Android 기본 LOCAL_MOCK Player 재검증 시작: 최신 stage와 앱 미설치 전용 AVD를 사용한다.
- R22 강화 synthetic mock 로그 검사의 Android 기본 LOCAL_MOCK Player PASS (`artifacts/unity-android-e2e-j9tb9ven`), 최초 전체화면 안내 수동 처리. 양 Push runner 변경 후 실제 실행은 별도다.
- 테스트 AVD shutdown·데이터 보존. Android 부분 결과 커밋 준비, 양 Push 재검증은 아직 NOT_RUN.
- P09-T03/R22 강화 mock credential 로그 검사의 Android/iOS Push Player 동일 실행 시작: 최신 stage와 빈 전용 AVD를 사용한다. 기존 E2E 결과는 대체하지 않는다.
- R22 강화 synthetic mock 로그 검사의 Android/iOS Push 동일 실행 2건 PASS (`artifacts/unity-android-push-918elqj3`, `artifacts/unity-ios-push-anrcrvlm`). Android 최초 안내 수동 처리; 실제 provider·다른 비밀 형식은 미검증.
- Push 시험 Simulator·AVD shutdown(데이터 보존), 강화 로그 부분 증거 정리·커밋 준비. R22 전체는 다른 credential 형식·나머지 로그 범위가 남아 PARTIAL.
- P08-T04 staged sample의 Unity Package Manager import API 검증 시작: 수동 파일 복사를 실제 sample metadata import로 대체해 격리 Editor flow를 재확인한다. GUI 클릭·시각 QA는 별도다.
- sample import API 전용 Editor setup 및 격리 runner 변경 초안 작성, shell 구문 PASS. 실제 Unity import·Player test는 아직 NOT_RUN이다.
- P08-T04 Unity Package Manager Sample API로 Offline/Native 두 sample import 및 격리 Editor fake flow/Native guard 1건 PASS (`artifacts/offline-sample.wdb0LN`). GUI import 클릭·실제 렌더링은 미검증이다.
- sample import 성공 marker는 이어지는 Unity test가 Editor.log를 덮어써 사후 증거로 남지 않는 문제를 발견했다. import 직후 두 marker만 별도 저장하도록 보완한다.
- P08-T04 Package Manager Sample API 두 sample import marker 보존 및 새 Editor fake flow/Native guard PASS (`artifacts/offline-sample.FAkiaR`). GUI 클릭·시각/포인터와 실제 provider는 미검증.
- sample import marker 보존 후 결과 음성·원장/shell/diff PASS. 두 marker가 정확히 한 번씩 존재해야 통과하도록 판정을 강화한다.
- marker 정확성 강화 후 Sample API import 양쪽 및 Editor Play 1건 PASS/skip0 (`artifacts/offline-sample.Afsqij`). GUI 클릭·실제 렌더링은 미검증, 커밋 준비.
- P08-T04 Native Demo 양 플랫폼 probe의 Sample API import 연결 시작: 직접 sample 복사 대신 격리 Package Manager import 후 Player 빌드·LOCAL_MOCK 실행을 확인한다.
- Native Player runner의 Sample API import 연결·Python/shell 및 marker 단위 5건 PASS. 격리 경로 보호를 추가한 뒤 실제 Player에서 검증한다.
- Sample import helper가 artifacts 외부 프로젝트를 거부하는 음성 시험과 shell 문법 PASS. 실제 양 플랫폼 Player는 NOT_RUN; clean-source 실행 전 커밋 준비.
- P08-T04 Sample API import→Native Demo iOS Simulator Player 실제 검증 시작: 최신 stage·격리 DB·ad-hoc Simulator 서명 사용.
- P08-T04 동일 신규 프로젝트 Sample API import→Native Demo iOS Simulator LOCAL_MOCK Player PASS (`artifacts/unity-ios-e2e-7ryle35b`), 원장 1건/100. GUI 클릭·실제 Apple 거래는 별도다.
- iOS test Simulator shutdown·데이터 보존. iOS 결과 커밋 준비, Android Sample API→Player는 미실행이다.
- P08-T04 Sample API import→Native Demo Android Player 실제 검증 시작: 앱 미설치 전용 AVD·최신 stage·격리 DB를 사용한다.
- P08-T04 동일 신규 프로젝트 Sample API import→Native Demo Android LOCAL_MOCK Player PASS (`artifacts/unity-android-e2e-8hjon046`), 원장 1건/100. 최초 전체화면 안내 수동 처리, GUI 클릭·실제 Play 거래는 별도다.
- Android test AVD shutdown·데이터 보존. 양 플랫폼 import→Native Demo Player의 source/범위를 증거·기능표·보고서에 반영한다. GUI/시각·실제 provider 미검증은 유지한다.
- P08-T04 두 Player 결과의 staging manifest hash 동일, 두 source 사이 SDK/Native 제품 경로 diff 없음. Sample API 설치·Editor sample·각 플랫폼 export/build/Player 증거를 계획 산출물로 정리한다.
- P08-T04 완료 기준의 격리 staged UPM·Sample API import·Editor mock flow·Android/iOS export/build/LOCAL_MOCK Player를 확인해 IMPLEMENTED/로컬 PASS로 갱신했다. GUI 포인터·시각 및 실제 provider 검증을 뜻하지 않는다.
- P08-T04 상태·집계 변경 후 원장/음성/diff 검사 PASS. 실provider·시각 QA 구분과 부분 Task 범위를 명시해 커밋 준비.
- P08-T03 Unity metadata 블로커 발견: SDK package 원본 `.meta` 0개, 새 consumer import 시 project별 GUID가 생성된다. 안정적 metadata 누락을 수정하고 기존 consumer·Demo는 보존한다.
- Unity가 격리 package 및 Sample API import에서 생성한 metadata 37개가 원본 asset/폴더와 모두 대응됨을 확인했다. 이 Unity 생성 metadata를 원본에 고정하고 GUID 중복·누락 검사를 추가한다.
- Unity 생성 metadata 37개를 원본에 고정했다. GUID 37개 유일성을 확인했으며 누락·중복·orphan 자동 검사 및 신규 프로젝트 간 안정성 검증은 아직 진행 전이다.
- package metadata completeness/GUID checker PASS; 누락·중복·orphan·폴더 오류 음성 2건 PASS. 실제 신규 Unity import 간 GUID 안정성은 아직 NOT_RUN.
- metadata 반영 staged UPM `artifacts/upm-stable-meta-20261113` 생성·147개 checksum/XCFramework 검증 PASS. 첫 신규 Unity import 및 sample 시험을 실행한다.
- metadata stage 첫 독립 Unity Sample import·Editor flow 1건 PASS (`artifacts/offline-sample.S2hxOa`). 두 번째 새 프로젝트에서 다시 실행한다.
- metadata stage 두 번째 신규 Unity Sample import·Editor flow 1건 PASS (`artifacts/offline-sample.McH39f`). 두 프로젝트의 실제 GUID를 원본과 대조한다.
- 신규 Unity 두 프로젝트 GUID 비교 FAIL: 74개 중 4개 불일치가 Sample API가 새로 만드는 Offline/Native sample 최상위 폴더 GUID에 집중됐다. 내부 asset 70개 결과는 별도 검증하며 최상위 폴더 안정성은 미완료다.
- package/sample 내부 asset GUID 70회 비교 불일치 0, Sample API 생성 최상위 폴더 GUID 4회 불일치 유지. metadata stage checksum 147개·Native payload 81개 동일성 PASS; 전체 metadata 안정성은 PARTIAL.
- metadata 정적·음성·YAML·원장/diff 검사 PASS. Sample 최상위 폴더 GUID 불일치와 최신 Player 미실행을 PARTIAL로 보존하며 커밋 준비.
- P08-T03 metadata stage iOS Native Demo Sample API→Simulator Player 재검증 시작: source e33a2bd와 147파일 stage, 격리 DB를 사용한다. 최상위 sample 폴더 GUID 불일치는 별도 유지.
- metadata stage iOS Sample API→Native Demo Simulator LOCAL_MOCK Player PASS (`artifacts/unity-ios-e2e-q9ua_s4_`), tracked-clean·원장 1건/100. Android 재실행 및 sample 최상위 폴더 GUID는 별도.
- iOS test Simulator shutdown(데이터 보존), 결과 커밋 준비. Android metadata stage Player는 NOT_RUN.
- P08-T03 metadata stage Android Native Demo Sample API→Player 재검증 시작: 앱 미설치 전용 AVD·격리 DB 사용.
- metadata stage Android Sample API→Native Demo LOCAL_MOCK Player PASS (`artifacts/unity-android-e2e-2trvul1k`), tracked-clean·원장 1건/100. 최초 전체화면 안내 수동 처리. Sample 최상위 폴더 GUID 차이는 미해결.
- metadata stage Android/iOS Native Demo Player 양쪽 재검증 PASS. 테스트 AVD shutdown·데이터 보존. Sample 최상위 폴더 GUID 불일치로 P08-T03 PARTIAL 유지, 최신 staging/증거 갱신.
- 최신 metadata stage·양 Player 결과 문서 정합성/manifest/diff PASS. 최상위 폴더 GUID·실제 provider는 미완료로 커밋 준비.
- P08-T03 실제 Unity iOS export hook 멱등성 검증 시작: 격리 export 후 hook을 두 번 추가 실행해 PBX·복사된 XCFramework가 중복/변경되지 않는지 확인한다.
- 실제 iOS hook 반복 시험용 Editor probe 초안 작성·Python 구문 PASS. Unity export 및 hook 재호출은 아직 NOT_RUN이다.
- P08-T03 실제 Unity iOS export hook 반복 PASS (`artifacts/unity-ios-mock.mWBnyZ`): 자동 hook 후 2회 재호출 시 PBX·XCFramework 전체 hash 동일. 서명·Player 시험은 아님.
- iOS hook 반복 재현 runner 실제 실행 PASS (`artifacts/unity-ios-mock.yLBxjk`), Unity export 후 2회 동일성 확인. stale staging을 거부하도록 runner 사전검사를 보강한다.
- iOS hook runner에 이전 stage 투입 음성 시험 exit 1: checksum 정상이나 source 불일치를 거부했다. 의도된 음성이며 현재 metadata stage로 재실행한다.
- P08-T03 iOS hook runner stale stage 음성 거부 및 현재 stage 실제 export 반복 PASS (`artifacts/unity-ios-mock.ztGwKd`). 이어서 Android 실제 Gradle export hook 반복을 검증한다.
- P08-T03 Android 실제 Gradle export hook 반복 probe·격리 runner 작성, 실행은 아직 NOT_RUN이다.
- P08-T03 실제 Unity Android Gradle export hook 반복 PASS (`artifacts/unity-android-mock.mri8OM`): 자동 hook 뒤 2회 재호출 시 Gradle 설정·복사된 Maven 파일 hash 동일. APK/Player는 별도다.
- P08-T03 실제 Android/iOS export hook 반복 검증 결과를 CI·패키징 문서에 연결한다. Git source와 Native binary 포함 staging을 명확히 구분하며 GUI/실 provider 상태는 그대로 둔다.
- 실제 Unity export hook Android/iOS 각 2회 반복 PASS 증거 작성, CI gate 연결. CI 음성 6건·shell/원장/diff PASS; 변경된 전체 gate 및 GitHub Actions는 NOT_RUN. 커밋 준비.
- P09-T08 Unity CI mock gate가 sample 및 양 export hook 실행을 빠뜨리지 않는지 음성 방지 시험을 보강한다.
- CI mock gate의 sample·Android/iOS hook 호출 및 strict 실패 전파 포함 단위 6건 PASS, 원장/diff PASS. 실제 새 gate 전체는 NOT_RUN, 커밋 준비.
- P09-T03/R22 개인정보 형태 입력의 Backend 오류/trace 및 Native diagnostics 비노출 검증 시작: 합성 email·전화번호만 사용한다.
- 합성 개인정보 입력 assertion을 Backend 오류/trace 및 Android/Swift diagnostics 시험에 추가했다. 실제 검증은 아직 NOT_RUN이다.
- R22 합성 email/전화번호 비노출: Backend 오류/trace 4건, Android bridge 3건, Swift C bridge 4건 PASS/skip0. 실제 개인정보·Unity raw log 개인정보 주입은 별도 미검증.
- R22 개인정보 fixture 실제 주입 위치와 assertion 재확인, 원장/diff PASS. 전체 Unity 로그 개인정보·실제 provider 범위는 미검증으로 커밋 준비.
- P09-T03/R22 Unity Player synthetic 개인정보 callback 주입 검증 시작: 허용 목록 밖 email/전화번호가 Unity 공개 Push 결과·원시 로그에 나오지 않는지 Android/iOS에서 별도로 확인한다.
- R22 test-only synthetic 개인정보 callback probe 작성. Native callback에 허용되지 않은 합성 필드를 주입하며 실제 빌드·실행은 아직 NOT_RUN이다.
- synthetic 개인정보 전용 Android/iOS runner 연결과 Python 문법 PASS. 두 조건부 managed compile 및 raw 로그 누출 음성 시험을 실행한다.
- synthetic 개인정보 probe Android/iOS managed compile 각 경고·오류 0, raw 로그 주입 거부 포함 단위 6건 PASS. 실제 Player는 NOT_RUN이며 clean-source 실행 전 커밋 준비.
- R22 synthetic 개인정보 callback iOS LOCAL_MOCK Simulator Player 실제 검증 시작: source 48388c7 probe, 최신 stage·격리 DB 사용.
- R22 iOS Simulator Unity Player synthetic 개인정보 callback PASS (`artifacts/unity-ios-e2e-ehxq_12y`): 허용되지 않은 email/전화번호가 공개 Push 결과 및 raw console에 없음. 실제 개인정보·APNs는 미검증.
- iOS PII test Simulator shutdown·데이터 보존. iOS 부분 결과 커밋 준비, Android는 NOT_RUN이다.
- R22 synthetic 개인정보 callback Android LOCAL_MOCK Player 실제 검증 시작: 앱 미설치 전용 AVD·최신 stage·격리 DB 사용.
- R22 Android Unity Player synthetic 개인정보 callback PASS (`artifacts/unity-android-e2e-rtm39zwn`): 허용되지 않은 email/전화번호가 공개 Push 결과 및 raw logcat에 없음. 최초 안내 수동 처리, 실제 개인정보/원격 push 미검증.
- Android PII test AVD shutdown·데이터 보존. 양 Player synthetic PII 결과 증거를 기록하되 자동 strict lane·다른 개인정보 형식/실 provider는 별도 미완료다.
- synthetic PII Player 정제 증거·원장/diff 검사 PASS. 원격 provider·자동 strict lane은 미완료로 커밋 준비.
- P09-T07 Unity CI 기본 Android/iOS Player에 이미 검증된 synthetic PII probe 연결 시작: 별도 AVD 추가 없이 기존 기본 flow와 함께 실행한다. strict의 독립 PII lane은 여전히 미구현이다.
- CI baseline 양 플랫폼 PII probe 인자 전달 fixture 포함 6건 PASS, shell/원장/diff PASS. 변경된 실제 전체 gate·standalone strict PII lane은 NOT_RUN/미구현, 커밋 준비.
- P09-T06/R22 동일 실행 PII Player 증거 집계 시작: Android/iOS 현재 HEAD·tracked-clean·필수 marker·원장 및 실행별 nonce를 검증하고 누락/과거 결과를 strict PASS로 사용하지 않는다.
- 동일 실행 PII wrapper/검사기 초안 작성, Python 구문 PASS. stale/dirty/marker 누락·nonce 불일치 음성 시험 및 실제 Player는 아직 NOT_RUN이다.
- 동일 실행 PII 증거의 stale·dirty·nonce·marker·원장 누락 음성 단위 1건 PASS, Python 구문 PASS. CI baseline과 strict 필수 lane을 연결한다.
- CI/strict PII lane 연결 후 mock CI 6건·증거 음성 1건 및 Python/shell 구문 PASS. strict로 동일 nonce와 evidence 경로가 전달되는지 추가 검증한다.
- PII 증거/nonce의 CI→strict 전달 fixture 6건, stale 증거 1건, 집계 13건 PASS. 실제 wrapper 및 변경된 전체 gate는 NOT_RUN, clean-source Player 검증 전 커밋 준비.
- P09-T06/R22 동일 실행 PII wrapper 실제 검증 시작: source b2a000d runner, 최신 stage·실행별 nonce·빈 전용 AVD 및 격리 iOS Simulator 사용.
- P09-T06/R22 동일 실행 Unity PII wrapper PASS 2건 (`artifacts/unity-pii-current-ml8muq1n`): source 222a2f3, 양 Player tracked-clean·nonce·marker·DB 원장 확인. Android 최초 안내 수동 처리, 실제 개인정보/제공자는 미검증.
- 동일 PII evidence/nonce의 strict checker 직접 PASS 2건 확인, 시험 AVD·Simulator shutdown(데이터 보존). 같은 논리 실행 증거를 격리 strict에 전달해 필수 lane 집계를 실제 검증한다.
- PII evidence 전달 격리 strict 종료 1/전체 FAIL (`artifacts/verify-all-p09mpzq9`), 외부 13 WAITING_USER. PII lane과 나머지 실패·미실행을 확인한다.
- PII evidence 전달 strict에서 `unity-pii-e2e` 2건 PASS; 구매 하위 PASS, Unity Push DEFERRED_ENV·Editor NOT_RUN·R22/R40 PARTIAL·P05-T03 FAIL로 전체 FAIL. test Simulator shutdown·데이터 보존.
- P09-T01/R22 시나리오 재현 연결 시작: 동일 실행 PII wrapper를 명시적 opt-in suite로 연결하고 느린 양 플랫폼 시험의 timeout·미설정 대기를 검증한다.
- R22 PII opt-in wrapper 음성/인자 전달 단위 2건·Python 문법 PASS. manifest timeout 경계의 음성 검사와 실제 evidence 매핑을 확인한다.
- R22의 합성 키/token/proof/PII 요구를 Backend·Native·양 Unity Player 실제 결과와 strict PII lane에 매핑해 local/fake IMPLEMENTED로 갱신했다. 실 provider·모든 가능 입력에 대한 보장은 별도다. 명시적 opt-in 진입 wrapper의 실제 호출은 아직 NOT_RUN이다.
- R22 assertion mapping·manifest/음성 검사 PASS. 필수 coverage 검사는 예상대로 exit 1: R40 1개 PARTIAL, NOT_IMPLEMENTED 0. 실제 provider 검증은 여전히 별도다.
- R22 opt-in 내부 timeout을 scenario 상위 3300초보다 짧게 두어 자체 timeout 분류를 반환할 여유를 확보한다. 단위·구문 및 manifest를 재검증한다.
- R22 opt-in/증거 단위 및 manifest 음성 검사 PASS. 플랫폼 누락 음성 fixture가 다른 실패 조건과 겹치지 않도록 독립성을 보강한다.
- R22 로컬/합성 시나리오 assertion·재현 suite·독립 음성 fixture 검증 PASS. opt-in 진입 wrapper 실제 호출과 실 provider는 NOT_RUN, R40 PARTIAL로 전체 coverage 미완료. 커밋 준비.
- R40 기존 실제 OS 증거의 현재 소스 유효성 점검 시작: 현재와 비교 시 Unity Runtime 변경은 새 .meta만 보인다. 플랫폼 코드 차이는 경로별로 재확인한다.
- R40 기존 Android/iOS OS 권한 증거 source와 현재 플랫폼/Unity Runtime의 비-metadata 제품 코드 차이 0, 각 실행에 사용한 test consumer 파일도 현재와 동일함을 확인했다. OS/Mock은 별도이며 재현 runner는 추가한다.
- P09-T05/R40 Android OS 권한 거부 재현 runner 구현 시작: 빈 전용 AVD·실제 OS dialog·test-only Firebase dependency를 사용하고 mock 권한 시험과 분리한다.
- Android OS 재现 runner 초안 작성,Python 구문 PASS. 전용 dialog 식별·누락 marker·중단/환경 대기 구분을 음성 검증한다.
- Android OS permission runner dialog 오선택/중복·marker 누락 음성 단위 2건 및 Python 구문 PASS. 실제 OS 재실행은 NOT_RUN이며 clean-source 실행 전 커밋 준비.
- R40 Android OS permission 재현 runner 실제 실행 시작: source 3279dc2 코드, 최신 stage·권한 이력 없는 전용 AVD. Firebase test dependency만 사용.
- R40 Android runner 첫 실제 실행 INTERRUPTED/exit 130 (`artifacts/unity-android-permission-ikutzs0w`): OS 거부 버튼 실제 ID는 `permission_deny_and_dont_ask_again_button`으로 기존 허용 목록에 없어 안전하게 중단했다. 권한 시험 PASS/FAIL은 미판정이다.
- 실제 관찰된 두 명시적 거부 ID에 대한 selector 음성/양성 단위 2건·Python/원장/diff PASS. 수정 runner의 실제 OS 재시험은 NOT_RUN, 커밋 준비.
- R40 Android OS runner 수정 후 재시험 시작: 중단된 AVD는 데이터 보존 종료하고 권한 이력 없는 별도 전용 AVD를 사용한다.
- R40 Android OS permission runner 자동 재실행 PASS (`artifacts/unity-android-permission-j_5q_9e9`): 실제 OS 거부·등록 PERMISSION_DENIED·재요청 DENIED, tracked-clean. 실제 FCM은 아님.
- Android permission test AVD shutdown·데이터 보존. 실제 자동 재시험 및 초기 중단 이력 커밋 준비. iOS 별도 runner는 미구현이다.
- P09-T05/R40 iOS OS 권한 거부 재현 runner 구현 시작: 새 전용 Simulator·실제 권한 dialog를 사용한다. GUI 거부가 처리되지 않으면 DEFERRED_ENV이며 자동 성공하지 않는다.
- iOS OS 재현 runner 초안 Python 구문 PASS. Simulator 생성 환경 대기 인자와 필수 marker·미설정 거부를 단위 확인한다. 실제 실행은 아직 NOT_RUN.
- iOS OS marker·명시적 opt-in 음성 2건, Python/원장/diff PASS. GUI 거부 미처리 시 환경 대기이며 실제 수정 runner 실행은 NOT_RUN; 커밋 준비.
- R40 iOS OS permission 재현 runner 실제 검증 시작: source 73638cb 코드, 최신 stage·권한 이력 없는 신규 Simulator 사용. OS 거부 입력을 실제 처리한다.
- R40 iOS OS permission 재현 runner PASS (`artifacts/unity-ios-permission-d3b5a0lc`): 실제 OS 거부·등록 PERMISSION_DENIED·재요청 DENIED, tracked-clean. Simulator GUI 거부는 도구로 수동 처리했으며 APNs 아님.
- OS runner 결과에 dialog 처리 방식 표시 보강 시작: Android가 실제로 자동 선택한 횟수와 iOS 외부 GUI 거부 필요를 구분한다.
- R40 OS dialog 처리 방식 분류 단위 Android 3건/iOS 2건 PASS, Python 구문 PASS. 양 OS와 Mock을 분리 실행하는 명시적 opt-in scenario entry를 추가한다.
- R40 통합 opt-in entry의 누락 시 대기·세 경로 순차 실행·중간 대기 전파 단위 2건 PASS. 실제 통합 wrapper 및 변경된 interaction metadata는 NOT_RUN, clean-source 실행 전 커밋 준비.
- P09-T05/R40 OS Android·iOS 및 managed Mock 통합 opt-in 실제 검증 시작: source dc8d9f9 코드, 최신 stage와 권한 이력 없는 전용 기기 사용. iOS GUI 거부는 도구로 처리한다.
- R40 통합 opt-in 실제 실행 PASS: Android OS 자동 denial (`artifacts/unity-android-permission-ube13ah7`), iOS OS GUI 거부 (`artifacts/unity-ios-permission-hk912uou`), managed Mock 각각 실행. 동일 source ef9405b tracked-clean; 실제 FCM/APNs 아님. 첫 결과 정리 호출은 작업 경로 오타로 실행되지 않아 재실행했다.
- R40 통합 실제 결과 재확인: Android OS 자동 denial 2회, iOS OS 외부 GUI denial, managed Mock 별도 PASS. 두 test 기기 shutdown·데이터 보존. 시나리오 범위에 맞춰 재현 suite와 증거 매핑을 검증한다.
- R40 Android OS·iOS OS·Mock 실제 통합 결과와 재현 suite를 assertion별로 매핑했다. 50개 시나리오 local/fake coverage 기록 완료, 단 iOS GUI 수동 처리 및 현재 CI 미실행·실 provider 미검증은 유지한다.
- R40 완료 매핑 후 시나리오 50/50 local/fake coverage 기록. 전체 CI/strict·실 provider의 현재 실행 성공은 별도이며 최종 음성/원장 검증을 수행한다.
- R40 OS/Mock 통합 opt-in 실제 PASS 후 marker/환경/CI 음성 13건, manifest/coverage/원장 검사 PASS. local/fake 시나리오 50/50 evidence 기록; 전체 strict·실 provider는 별도 미완료. 커밋 준비.
- P09-T07 50/50 local/fake coverage·최신 metadata/sample/hook/PII gate 반영 후 전체 Unity CI gate 로컬 재검증 시작. 기존 P05-T03 FAIL 및 실 provider 13 WAITING_USER는 그대로 둔다.
- 최신 전체 Unity CI gate 로컬 실행 종료 1/전체 FAIL (`artifacts/verify-all-n3u_5w60/summary.md`), 외부 13 WAITING_USER. 세부 lane과 기존 실패를 확인하며 실제 GitHub Actions로 간주하지 않는다.
- 최신 strict 세부: source 562c75f, coverage 50건·Unity PII 2건·Push 2건·Editor 2건 및 실행 suite PASS; 유일한 비PASS는 이전 P05-T03 FAIL, 전체 FAIL. OS R40 iOS GUI 보조는 별도 선행 증거. 테스트 AVD 2·Simulator 3 shutdown, 데이터 보존.
- 최신 gate source/lane·수동 조작·P05-T03 FAIL·외부 대기를 정제 증거와 문서에 반영, 원장/manifest/diff PASS. 커밋 준비.
- P05-T03 iOS 26.5 StoreKit 실패 원인 조사 시작: Apple 공식 문서와 설치된 runtime을 확인한다. 이전 실패와 외부 보고가 같다고 단정하지 않는다.
- Apple 공식 문서는 SKTestSession의 named/URL 초기화 경로를 제공하며, iOS 26.5 관련 별도 문제는 공개 포럼에서도 보고됐다. 로컬 원인과 동일하다고 단정하지 않고 test-only URL 초기화 대조를 추가한다.
- StoreKit test-only URL 초기화 선택 경로 초안 및 Python 문법 PASS. 잘못된 선택이 DB 생성 전에 거부되는지 보강·확인한다.
- 잘못된 StoreKit initializer는 DB 생성 전 exit 2, Python/diff PASS. iOS 18.6 전용 Simulator에서 URL initializer 양성 대조를 먼저 실행한다.
- iOS 18.6 test-only URL initializer·local process recovery 양성 대조 PASS (`artifacts/xcode-process-recovery-xbadp2tm`). 26.5 및 기존 named 실패는 별도다.
- P05-T03 iOS 26.5 test-only URL initializer 대조 시작: 18.6 양성 대조 후 별도 Simulator/DB에서 실행, 기존 named 실패는 보존한다.
- P05-T03 iOS 26.5 URL initializer 대조 FAIL (`artifacts/xcode-process-recovery-97a0wg1_`): prepare `storekit-session` timeout. 18.6 URL 양성 대조는 PASS. 기존 named 실패와 동일 원인 여부는 미확정이며 P05-T03 FAIL 유지.

### 2026-11-13 사용자 요청 중단 체크포인트

- 브랜치 `fix/unity-android-mock-e2e-evidence`; 자동 push·main 병합·Release 없음. 기존 미추적 `unity/Demo`, `harness/__pycache__`, `scripts/__pycache__`와 테스트 DB/AVD/Simulator 데이터는 보존했다. 실행 중인 테스트 기기는 종료했다.
- P09 시나리오 local/fake coverage 50/50 기록, 실제 제공자 13개 WAITING_USER. R40 Android OS 자동·iOS OS GUI 보조·Mock을 별도로 확인했다. 최신 전체 Unity gate `artifacts/verify-all-n3u_5w60/summary.md`는 해당 실행 suite/50개 coverage PASS이나 기록된 P05-T03 FAIL 때문에 전체 FAIL이다. 두 Android 최초 안내는 수동 처리했고 GitHub Actions는 NOT_RUN이다.
- P05-T03: iOS 18.6 URL initializer의 local process recovery PASS `artifacts/xcode-process-recovery-xbadp2tm`; iOS 26.5 URL initializer는 `storekit-session` timeout FAIL `artifacts/xcode-process-recovery-97a0wg1_`. 기존 named timeout/Code 3과 동일 원인은 미확정; `ENV-STOREKIT-26` OPEN 및 P05-T03 FAIL 유지. 두 결과는 이 커밋의 당시 미커밋 test-only 진단 변경에서 실행했다.
- 최신 로컬 staging `artifacts/upm-stable-meta-20261113`, cache `artifacts/unity-ios-mock.8xjMY7/project/Library/PackageCache`. 내부 asset GUID 70회 비교 일치, Sample API가 생성하는 최상위 폴더 GUID 4회 불일치로 P08-T03 PARTIAL 유지.
- 재개 시 AGENTS.md·START_HERE.md·이 원장·WORK_LOG 및 Git 상태를 읽고 P05-T03 원인과 named/URL 차이를 계속 조사한다. test-only `GAMEBRIDGE_PROCESS_STOREKIT_INIT`의 기본은 `named`, `url`은 명시 선택이다. 최신 source 전체 gate는 마지막 문서/진단 커밋 이후 재실행하지 않았고, 실제 계정·스토어·원격 push는 USER_SETUP에 남는다.
- P05-T03 재개: 기존 `storekit-session` checkpoint는 생성과 disableDialogs 설정을 함께 포함한다. test-only 단계 분리 및 main/background 대조로 실제 정지 지점을 확인한다.
- P05-T03 test-only 생성/설정 checkpoint 분리 및 background 선택 경로 작성, Python/diff 검사 PASS. 아직 Swift 빌드·실행은 NOT_RUN이다.
- P05-T03 잘못된 executor는 DB 생성 전 exit 2. iOS 18.6에서 background initializer 양성 대조를 실행한다.
- P05-T03 iOS 18.6 background URL initializer·local process recovery PASS (`artifacts/xcode-process-recovery-dhe_8lqh`), Swift test-only 변경은 당시 미커밋. 26.5와 별도다.
- P05-T03 18.6 background 양성 확인 후 26.5 background URL 대조 시작. 기존 main/named/URL 실패는 보존한다.
- P05-T03 iOS 26.5 background URL 대조 FAIL (`artifacts/xcode-process-recovery-na8yq85t`): 세분화된 `storekit-session-create` timeout. 같은 test-only 경로 iOS 18.6은 PASS. Apple 내부 원인은 미확정, 기존 FAIL 유지.
- P05-T03 named/URL 및 background 대조에도 26.5 session 단계 미해결. 동일 오류의 추가 반복 대신 이력·환경 blocker 유지하고, 변경된 test-only 기본 18.6 named 경로 회귀만 확인한 뒤 독립 작업으로 이동한다.
- P05-T03 변경 후 기본 main/named iOS 18.6 회귀 PASS (`artifacts/xcode-process-recovery-7v4ybj7y`). 26.5 실패와는 별도이며 실 Apple sandbox는 NOT_RUN.
- P05-T03 대조 결과·blocker·보고서 정리, 세 전용 Simulator shutdown/데이터 보존. test-only 진단과 이력 커밋 준비.
- P08-T03 Sample API 최상위 폴더 GUID 재가져오기 진단 시작: 프로젝트별 GUID 차이와 같은 프로젝트 내 override import 안정성을 구분해 검증한다.
- P08-T03 신규 격리 consumer sample import·Editor test 1건 PASS (`artifacts/offline-sample.KSrzqt`). 이 작업에서 생성한 프로젝트에만 override 재import 진단을 실행한다.
- P08-T03 같은 격리 프로젝트의 Sample API override 재import 결과: Offline/Native 대상 최상위 폴더와 내부 asset GUID가 각각 유지됐다 (`artifacts/offline-sample.KSrzqt`). 서로 다른 프로젝트의 생성 폴더 GUID 차이는 별도 사실이다. 자동 검증에 연결한다.
- Sample 재import 안정성 fail-closed checker/음성 단위 1건 PASS, shell/Python 문법 PASS. 강화된 신규 consumer 전체 실행을 검증한다.
- P08-T03 강화 runner에서 새 격리 consumer Sample API import·Editor 1건·동일 프로젝트 override 재import의 두 sample root/internal GUID 안정성 PASS (`artifacts/offline-sample.PbKuS1`). 다른 프로젝트의 생성 root GUID는 다르며 package 내부 asset GUID와 구분한다.
- P08-T03 계획 범위의 staging checksum·실제 양 export hook 반복·package asset GUID 및 동일 프로젝트 sample 재import 안정성·소비 빌드·README 구분을 확인해 IMPLEMENTED/로컬 PASS로 갱신했다. 프로젝트별 새 sample 대상 root GUID 차이와 실 provider/GUI 시각 미검증은 별도 명시했다.
- P08-T03 상태/집계 갱신 후 원장·음성·metadata·manifest/diff PASS. 프로젝트별 생성 root GUID 차이, 실 provider/GUI 미검증은 유지하며 커밋 준비.
- P08-T01/T02 최신 Native 산출물 독립 소비 검증 시작: 새 Maven과 iOS XCFramework 경로를 사용해 clean consumer R8 및 source/slice/symbol/link를 확인한다. 실기기·서명·실 provider는 별도다.
- P08-T02 `swift build --package-path ios` exit 0: Swift package 자체 빌드 PASS. 별도 소비자 링크·XCFramework archive는 아직 진행 중이다.
- P08-T02 독립 SwiftPM source consumer 초안 추가: Core/Apple 제품을 package dependency로 가져와 host 실행을 확인한다. 실행은 아직 NOT_RUN이다.
- P08-T01 최신 Android Maven publish·독립 consumer R8 release build exit 0 (`artifacts/maven-p08-reverify-20261113`). P08-T02 무서명 device/simulator XCFramework archive exit 0 (`artifacts/ios-p08-reverify-20261113`), 독립 SwiftPM source consumer host 실행 PASS (`artifacts/ios-source-consumer.UIxcpt`). 실제 기기/스토어는 아님. 세부 산출물 검증은 진행 중.
- P08-T02 새 XCFramework device/simulator arch 및 C ABI symbol 검사 PASS. P08-T01 consumer는 source project 참조 없이 Maven 좌표·R8 release 설정, POM 전이 의존성 선언 확인; APK 실행은 아님.
- P08-T02 독립 Swift consumer의 arm64 iOS Simulator 링크 PASS 및 Mach-O IOSSIMULATOR 확인. P08-T01 merged manifest의 BILLING/INTERNET 확인, SDK XML 버전 경고 있음. clean consumer 재현을 별도 디렉터리에서 진행한다.
- P08-T01 신규 격리 Maven consumer의 unsigned R8 release APK·mapping 및 merged manifest BILLING/INTERNET/consumer activity PASS (`artifacts/android-maven-consumer.cNk7BG`). 기기 실행은 아니다.
- P08-T01 fresh isolated Maven R8 consumer 및 merged manifest, P08-T02 SwiftPM source host consumer·unsigned XCFramework arch/symbol·독립 iOS Simulator link를 확인했다. 제출된 APK/기기 실행·실 provider는 별도다. 증거를 정리한다.
- P08-T01/T02 계획의 publication·clean Maven R8 소비 및 SwiftPM source/XCFramework arch·symbol·독립 simulator link를 실제 확인해 해당 Task 로컬 IMPLEMENTED/PASS로 갱신했다. unsigned APK·archive의 실기기 실행/실 provider는 별도다.
- P08-T01/T02 원장/집계·음성·shell/metadata/diff 검사 PASS. Maven repository 미설정 시 실제 실행 없이 DEFERRED_ENV가 되는지 확인한다.
- Maven repository 미설정 음성 exit 2/DEFERRED_ENV 및 CI YAML PASS. P08-T01/T02 관련 source consumer·증거·상태 커밋 준비; 원격/실기기 별도.
- P08-T05 현재 기능·패키징 기준점 재검증 시작: 기존 API/protocol snapshot을 보존하고 P00~P08 원장 행과 미완료/실연동 상태를 다시 대조한다. 기능 전체 완료를 뜻하지 않는다.
- P08-T05 기존 API baseline 정상·mutation 음성 PASS, 계획 P00~P08 48개 ID와 원장 48개 일치. 당시 로컬 PASS 6/PARTIAL 41/FAIL 1이며 현재 부분 기준점을 별도로 보존한다.
- P08-T05 기준점 기록 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. 기준점의 P00~P08 snapshot 자체는 FAIL 1·PARTIAL 41이므로 기능 전체 완료나 실 provider PASS가 아니다. 이전 API snapshot과 실패 이력은 보존한다.
- P08-T05 상태 갱신 후 원장 검사 FAIL: 선언 집계가 실제 행과 불일치. 다른 검사 성공은 이를 상쇄하지 않으며 행/집계를 정정한다.
- 원인: P08-T05 기존 행의 증거 표기가 예상보다 길어 문자열 교체가 적용되지 않았다. 실제 행과 증거 링크를 갱신하고 집계를 재검증한다.
- P08-T05 행·집계 정정 후 원장 단독 검사 PASS. snapshot의 과거 P05 FAIL/PARTIAL은 보존하며 기준점 문서 Task만 완료로 기록한다.
- P08-T05 정정 후 원장·음성·API mutation·manifest/diff PASS. INCOMPLETE 기준점 snapshot과 Task 기록 커밋 준비.
- P00-T02 환경·도구 기준 재감사 시작: 기존 2026-11-10 TOOLCHAIN/ENVIRONMENT와 현재 설치·라이선스·실행 증거를 대조한다. 최신 공식 지원 문서 확인을 시작 기록보다 먼저 수행한 순서 누락을 보완한다.
- P00-T02 현재 도구 조회: Unity installed 6000.5.8f1(Android/iOS 모듈)·6000.4.0f1(Web/Windows), 라이선스 active, Xcode 26.6/Swift 6.3.3/JDK 21.0.10/PostgreSQL 17.6 컨테이너 running. Unity 6.3 LTS는 미설치다. 실제 provider/기기는 별도다.
- P00-T02 TOOLCHAIN/ENVIRONMENT/USER_SETUP의 현재 설치·실행 범위를 갱신했다. 6000.3 LTS 미설치, 26.5 StoreKit FAIL, 실provider·실기기 대기는 유지한다.
- P00-T02의 현 설치 버전·라이선스·로컬 검증/미검증 환경 기록 기준을 충족해 문서화 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. Unity 6.3 LTS 미설치 ENV-001 및 26.5/실 provider 실패·대기는 해소한 것이 아니다.
- P00-T02 행/집계 갱신 후 원장 검사 PASS. ENV-001 OPEN·실 provider/26.5 실패는 그대로이며 음성 검사 후 커밋 준비.
- P00-T04 문서 검증·명령 종료 코드 재감사 시작: Task 행 누락·증거 없는 PASS·잘못된 상태 음성 및 도구 부재/실행 실패 구분을 격리 사본에서 확인한다.
- P00-T04 원장 사본의 행 누락·증거 없는 PASS·잘못된 상태 및 기존 음성 사례, 도구 부재 exit 2와 실행 실패 exit 7 분리 2건 PASS. 실제 doctor/Makefile 진입점도 확인한다.
- `bash scripts/doctor.sh` exit 0: 로컬 명령·Docker·SDK 경로 가용성 확인. 라이선스·기기·실 provider 검증은 이 명령 범위 밖이다. Makefile 라우팅을 확인한다.
- P00-T04 `make doctor`, `make verify-progress`, 원장 음성 및 종료 코드 격리 단위 2건 PASS. 실제 제품 검증은 아니며 계획 evidence를 정리한다.
- P00-T04 계획의 정상·행 누락·빈 PASS evidence·잘못된 상태 및 도구 부재/명령 실패 구분을 확인해 해당 문서/진입점 Task만 IMPLEMENTED/로컬 PASS로 갱신했다. 실제 제품 동작/실 provider PASS가 아니다.
- P00-T04 격리 도구 부재 fixture가 시스템 HOME을 바꾸지 않도록 조정하고 종료 코드 단위를 재검증한다.
- 격리 fixture 조정 후 종료 코드 2건·원장/diff PASS. P00-T04 진입점 Task 증거와 로컬 상태 커밋 준비.
- P00-T05 설정/비밀정보 격리 재감사 시작: 추적 파일명과 ignore 규칙만 확인하며 실제 비밀값은 읽지 않는다. `.env` 및 Unity 라이선스·독립 빌드 산출물의 ignore 누락을 보강한다.
- P00-T05 합성 파일명 ignore 2건 PASS. Android sandbox에서 client ID 누락 시 CONFIG_REQUIRED는 나오지만 Native 오류와 Unity capability에 정확한 설정 key가 충분히 표시되는지 확인한다.
- P00-T05 Android Google 설정 진단 누락 발견: client ID 부재 시 CONFIG_REQUIRED는 반환하나 Native 오류에 누락 key 이름이 없다. capability reason도 실제 누락 key를 구분하지 못한다. 값 노출 없이 수정한다.
- Android Google client ID 미설정의 Native CONFIG_REQUIRED에 key 이름을 추가하고 Unity capability의 auth/store/push별 실제 누락 key만 표시하도록 작성했다. 값·Mock fallback은 출력하지 않는다. 실행 검증 전이다.
- Android 설정 진단 첫 시험은 ANDROID_HOME 미지정으로 SDK 경로 탐색 실패(exit 1), 테스트 NOT_RUN. 설치된 SDK 경로를 명시해 재실행한다.
- P00-T05 Android Google fake/provider 15건·bridge 5건 PASS/skip0(설정 key 진단 포함), SDK XML 경고 있음. Unity 공개 capability 전달과 backend 호출 전 차단을 더 확인한다.
- Android Google fake/provider 15건·bridge 5건 재실행 PASS/skip0: client ID key 진단·challenge 전 차단·capability 누락 key 조합 확인. 실제 Google 인증은 미검증이다.
- P00-T05 설정 회귀: Backend EnvironmentPolicy·Android/Swift Configuration 각 2건, C# capability/fake smoke, 합성 파일명 ignore 2건 PASS. 실제 provider 인증 및 기기 경로는 별도다.
- P00-T05 Android 제품 진단 변경으로 이전 P08-T01/T03/T04 산출물·Player 증거는 현재 코드 검증이 아니다. 재빌드·재패키징·재실행 전 세 Task를 IN_PROGRESS/PARTIAL로 전환하고 이전 결과는 보존한다.
- P00-T05/P08-T01 설정값 미제공 mock build 및 변경된 Android Maven 재빌드 시작. 실제 key를 읽거나 저장하지 않고 새 output만 사용한다.
- P00-T05 주요 개발키·Google credential 환경변수를 제거한 Backend bootJar 빌드 PASS. 서버 기동/실연동은 이 결과에 포함되지 않는다.
- P00-T05/P08-T01 개발키·Google credential 환경변수 제거 후 변경 Android Maven publication·독립 R8 소비 build PASS. 새 isolated consumer와 staging은 별도 확인한다.
- P00-T05 iOS sandbox capability도 store/push 누락 설정을 일반 문구만 표시하는 동일한 진단 누락을 확인했다. 실제 설정 key 이름만 표시하며 Apple 인증/entitlement 준비 완료로 취급하지 않는다.
- iOS Apple bridge 제품 진단 문구 변경 후 fake XCTest 3건 PASS/skip0. 기존 XCFramework는 이전 소스이므로 P08-T02도 IN_PROGRESS/PARTIAL로 전환하고 새 archive/link·양 플랫폼 staging을 검증한다.
- 변경된 Android fresh Maven의 별도 clean R8 consumer PASS (`artifacts/android-maven-consumer.IjHXTq`). iOS product 변경을 포함한 무서명 XCFramework를 새 경로에 재빌드한다.
- 변경 iOS 제품의 무서명 device/simulator XCFramework archive PASS (`artifacts/ios-config-diagnostic-20261113`), symbol·독립 link는 아직 확인 전이다.
- 변경 iOS XCFramework device/simulator arch·C ABI, 독립 arm64 Simulator link 및 SwiftPM host consumer PASS. 새 Android/iOS 산출물로 UPM staging을 생성한다. 실제 기기/실 provider는 아님.
- 새 stage Unity 검증 명령 첫 호출은 작업 디렉터리 오타로 프로세스가 시작되지 않았다. checksum PASS와 별개이며 올바른 경로에서 실행한다.
- 새 UPM stage Editor sample/API import·동일 프로젝트 재import PASS (`artifacts/offline-sample.X4RqNd`), Android Gradle export hook 반복 PASS (`artifacts/unity-android-mock.RMw4BW`). iOS hook은 진행 중이다.
- 새 UPM stage iOS Xcode export hook 반복 PASS (`artifacts/unity-ios-mock.v5pYhN`), 서명/Player는 별도다. 현재 변경 product의 Android/iOS Player 재실행을 준비한다.
- P00-T05 Android/iOS 설정 진단 변경과 ignore 규칙은 fake 단위·키 없는 빌드·새 stage Editor/양 hook PASS. 실제 Unity sandbox 누락 경계 및 변경 Player 검증 전이며 P00-T05/P08 재검증 상태는 PARTIAL 유지, clean-source 실행 위해 커밋 준비.
- P00-T05 실제 Unity sandbox 설정 누락 경계 검증 시작: Android Google client ID와 iOS store/installation 설정이 없는 경우 capability의 key 이름 및 CONFIG_REQUIRED를 확인한다. 실제 계정 UI·서버 호출은 수행하지 않는다.
- test-only Android/iOS sandbox 누락 설정 consumer를 작성했다. 실제 account UI/서버 호출 없이 capability key 및 CONFIG_REQUIRED를 확인하며 아직 컴파일/Player 미실행이다.
- Unity sandbox config 전용 runner 초안과 platform marker/opt-in 음성 단위 2건 PASS. 양 조건부 managed compile 및 실제 Player는 아직 NOT_RUN이다.
- sandbox config consumer Android/iOS 조건부 managed compile 각각 경고·오류 0, marker/opt-in 음성 2건 PASS. 실제 Player는 NOT_RUN이며 clean-source 실행 전 커밋 준비.
- P00-T05 iOS sandbox 누락 설정 Unity Simulator Player 실제 검증 시작: 최신 stage, example.invalid 및 test-only consumer 사용. Apple 계정 UI/원격 호출은 의도하지 않는다.
- iOS Unity sandbox 설정 누락 경계 PASS (`artifacts/unity-sandbox-config-ios-c9m2245o`): store/installation key reason 및 products CONFIG_REQUIRED, tracked-clean. 실제 Apple 계정·서버·스토어 호출은 아님.
- iOS sandbox config test Simulator shutdown·데이터 보존. iOS 결과 커밋 준비, Android Player는 미실행이다.
- P00-T05 Android sandbox 누락 client ID Unity Player 실제 검증 시작: 앱 미설치 전용 AVD, example.invalid. Google 계정 UI/원격 호출은 수행하지 않는다.
- Android Unity sandbox 설정 누락 경계 PASS (`artifacts/unity-sandbox-config-android-yklqwymu`): client/store/installation key reason 및 sign-in CONFIG_REQUIRED, tracked-clean. 최초 전체화면 안내 수동 처리; 실제 Google 인증은 아님.
- P00-T05 계획의 explicit mode·설정 누락 key/no-fallback·no-key build·비밀 파일 ignore를 local/fake 및 Unity sandbox 설정 경계에서 확인해 해당 Task IMPLEMENTED/로컬 PASS로 갱신했다. 실제 provider/entitlement/실기기는 별도 WAITING_USER다.
- P00-T05 상태·집계/원장 음성·ignore 단위 2건/diff PASS. 설정 격리 로컬 증거만 커밋 준비; P08 변경 artifact/Player 재검증은 계속 PARTIAL이다.
- 새 stage Editor sample·재import 및 실제 Android/iOS export hook 반복 PASS. Native product source는 설정 진단 commit fb48371 이후 변하지 않았다. 변경 Native의 독립 소비/staging 증거를 갱신한다.
- P08-T01/T02/T03은 변경 Native 재빌드·독립 소비·새 staging/Editor/양 hook 실제 재검증으로 로컬 PASS를 복원했다. P08-T04 변경 Native의 양 Player 재실행은 아직 PARTIAL이며 실 provider는 별도다.
- 변경 후 P08-T01/T02/T03 로컬 상태 복원 뒤 원장·음성·metadata/diff PASS. P08-T04 양 Player 재검증 전 정제 evidence 커밋 준비.
- P08-T04 변경 Native 포함 최신 UPM의 Sample API→Native Demo iOS LOCAL_MOCK Player 재검증 시작. 실제 Apple provider/시각 QA는 별도다.
- 변경 Native 최신 stage의 Sample API→iOS Native Demo LOCAL_MOCK Player PASS (`artifacts/unity-ios-e2e-kobckvqn`), tracked-clean·원장 1건/100. Android 재검증·실 provider는 별도다.
- iOS test Simulator shutdown·데이터 보존. iOS 부분 결과 커밋 준비, Android는 최신 stage 재실행 전이다.
- P08-T04 변경 Native 포함 최신 UPM의 Sample API→Native Demo Android LOCAL_MOCK Player 재검증 시작. 앱 미설치 전용 AVD·격리 DB 사용, 실 Google/Play는 별도다.
- 변경 Native 최신 stage의 Sample API→Android Native Demo LOCAL_MOCK Player PASS (`artifacts/unity-android-e2e-xhb_xrnk`), tracked-clean·원장 1건/100, 최초 안내 수동 처리. 실제 Google/Play는 별도다.
- 최신 양 Native Demo Player는동일 staging hash·각 tracked-clean이며 두 source 간 Unity/Native 제품 diff 0. AVD shutdown·데이터 보존, P08-T04 증거를 갱신한다.
- P08-T04 변경 product의 최신 stage에서 Sample API→Android/iOS Native Demo LOCAL_MOCK Player를 각각 재검증해 해당 로컬 PASS를 복원했다. 실제 provider·실기기·시각 QA는 아니다.
- P08-T04 상태 복원 후 원장·음성·manifest/diff PASS. 최신 양 Player·stage evidence 커밋 준비; 실제 provider/시각 QA는 별도다.
- P01-T01 공통 model fixture 재감사 시작: Kotlin/Swift는 네 DTO round-trip을 검사하지만 C# smoke는 profile/product 값과 일부 purchase만 확인한다. 동일 fixture 네 DTO의 round-trip·필수 null 필드 검증을 보강한다.
- P01-T01 C# standalone smoke PASS: 네 DTO의 공유 fixture round-trip 및 nullable 오류 확인. 전체 Kotlin/Swift/C# 계약 runner는 새로 실행한다.

- P01-T01 진행: 공통 contract runner Kotlin 10·Swift 11·C# 1 PASS/skip 0 (`artifacts/contracts-72sh1hus`, d238169 + 미커밋 테스트). fixture 변조 음성 검증 및 완료 기준 대조 예정.

- P01-T01 `check-contract-negative.py` PASS: 별도 복사본의 protocolVersion 변조를 Kotlin/Swift가 거부했으며 원본 fixture는 보존됐다. C# nullable 누락은 별도 managed 테스트에서 확인했다.

- P01-T01 완료 기준: 공통 fixture 네 모델의 Kotlin/Swift/C# encode/decode, Unicode·null·큰 정수 문자열과 필수 필드 누락 검증 PASS. standalone 계약 시험이며 Unity IL2CPP 및 실제 플랫폼 검증은 범위 밖이다.

- P01-T01 커밋 전 원장 검사에서 `harness/verify-progress.py` 경로 오류로 실행되지 않았다. 실제 스크립트 위치를 확인해 재실행한다.

- P01-T01 원장 검사는 Task 상태 변경 후 상단 합계 미갱신을 발견해 실패했다. 합계를 원장에 맞춘 뒤 재검증한다.

- P01-T01 원장 합계 수정 후 `scripts/verify-progress.py`, `harness/check-progress-negative.py`, `git diff --check` PASS. 커밋 전: C# contract smoke와 진행 문서만 포함하며 미추적 Demo·캐시는 보존한다.

- P01-T02 시작: bridge schema·정상/오류/구버전 fixture와 각 언어 parser의 requestId 불일치·error 누락 거부 및 실제 schema validation을 대조한다. P01-T01은 1b310fb 로컬 커밋이다.

- P01-T02 스키마 검증기 조사: 현재 Python 환경에 `jsonschema`가 없어 해당 검사는 미실행이다. 의존성 고정 및 CI 설치 경로를 확인한다. 조사 명령 하나는 zsh 미일치 glob으로 실행되지 않았다.

- P01-T02 확인: 기존 Kotlin/Swift parser는 잘못된 version/operation, 실패 error 누락, 다른 requestId, oversized payload를 검사하지만 JSON Schema 자체를 평가하는 CI 단계가 없다. 고정된 검증 의존성과 양성·음성 schema 시험을 추가한다.

- P01-T02 격리 venv에서 Draft 2020-12 schema 자체 검사 및 기존 양성·음성 fixture, event/response 필수 필드·UUID 변조 검사 2건 PASS/skip 0. GitHub Actions 설정은 변경했으나 원격 실행은 NOT_RUN이다. 명시적 성공·일반 실패·event 공유 fixture를 추가한다.

- P01-T02 성공·일반 실패·event fixture 추가 후 schema 2건, `run-contracts.py` Kotlin 10·Swift 11·C# 1 PASS/skip 0 (`artifacts/contracts-wmods2k9`, HEAD 1b310fb + 미커밋 변경). Kotlin/Swift가 공유 양성 fixture를 parse했다. C# registry 음성 검사 및 schema 범위를 별도 확인한다.

- P01-T02 `check-bridge-mutation.py` PASS: 별도 복사본의 중복 응답 guard 제거를 C# standalone 테스트가 감지, 원본 소스 유지. requestId 대조·payload 한도는 Kotlin/Swift parser 및 registry smoke에서 별도 검사했다.

- P01-T02 계획 대조에서 oversize는 각 언어가 독립 생성해 시험하지만 공통 크기 fixture가 없음을 발견했다. 큰 바이너리를 저장하지 않고 byte count를 공유하는 descriptor fixture로 보강한다.

- P01-T02 공통 oversized descriptor 적용 후 `run-contracts.py` Kotlin 10·Swift 11·C# 1 PASS/skip 0 (`artifacts/contracts-gmjhtcvv`, HEAD 1b310fb + 미커밋 변경). Swift와 Kotlin이 동일 262145 byte 경계 fixture를 사용한다.

- P01-T02 최신 schema 양성·음성 2건 및 복사 fixture protocolVersion 변조 검사 PASS. C# registry가 다른 requestId를 격리하는지 명시적 회귀 단언을 추가한다.

- P01-T02 C# standalone smoke에서 불일치 requestId 격리 PASS. Draft schema 양성·음성 및 각 언어 parser/크기 경계 검증을 근거로 IMPLEMENTED/로컬 PASS; 원격 CI·실기기 검증은 미실행이다.

- P01-T02 커밋 전 원장 일관성·원장 음성 검사·`git diff --check` PASS. schema 시험·fixture·CI 설정·진행 문서만 로컬 커밋하며 기존 미추적 파일은 보존한다.

- P01-T03 시작: Kotlin/Swift coordinator 및 C# facade의 초기화·중복·shutdown·재시작과 동시성, provider interface 및 capability 분리를 기존 증거와 소스에서 대조한다. P01-T02는 65b460f 로컬 커밋이다.

- P01-T03 감사: Kotlin·C#은 shutdown 후 재초기화를 실행하지만 Swift 테스트에 명시 assertion이 없다. Swift 재초기화를 보강한다. Auth/Store/Push/Clock별 공통 interface는 검색상 확인되지 않아 구현 범위를 추가 대조하며 전체 Task 완료로 기록하지 않는다.

- P01-T03 Swift host `SdkCoordinatorTests` 3건 PASS/skip 0: shutdown 중단·중복 init·다른 설정 거부·중복 shutdown·재초기화 추가 확인. 별도 Swift Testing의 0건 출력은 해당 XCTest 3건과 구분한다. Swift 상호 배제 실행을 보강한다.

- P01-T03 Swift host `SdkCoordinatorTests` 4건 PASS/skip 0: 추가된 상호 배제 BUSY 및 재초기화가 통과했다. actor 기반 순서 제어 시험이며 전체 data race 부재를 증명하지 않는다. 공통 provider interface 전체 범위는 미완료/PARTIAL로 유지한다.

- P01-T03 커밋 전 원장 및 diff 검사 PASS. Swift host 테스트와 문서만 커밋하고 P01-T03은 IN_PROGRESS/PARTIAL로 유지한다.

- P01-T03 추가 대조: 각 기능별 공통 Auth/Store/Push/Clock 계약이 계획처럼 Core에 노출되지는 않는다. 단순 미사용 interface 추가를 완료로 오인하지 않고 해당 항목을 미완료로 기록한다. P01-T04 fake 시나리오를 독립적으로 점검한다.
- P01-T04 시작: Android·iOS·Editor Fake의 결정적 시나리오와 중복 지급 방지의 실제 구현·검증 범위를 대조한다.

- P01-T04 발견: 독립 Native test Fake의 푸시 중복 ID는 무제한 보관되고 shutdown 후 남는다. 승인된 최근 200개·앱 세션 기준과 다르며 Swift는 공백 ID도 허용한다. 두 Fake만 일치시키고 순서·세션 경계를 검증한다. 실제 FCM/APNs 결과는 아니다.

- P01-T04 독립 test Fake 개선 후 Android `OfflineFakeTest` 1건 및 Swift host `OfflineFakeTests` XCTest 1건 PASS/skip 0: 200개 FIFO, 재초기화 세션, 공백 ID, 기존 구매 중복·푸시 흐름 확인. Swift Testing 별도 0건은 XCTest와 구분한다. 실제 provider·Unity Player 시험은 아니다.

- P01-T04 JUnit 결과 1건·원장·diff 검사 PASS. 커밋 전: 별도 테스트용 Native Fake와 그 테스트·진행 문서만 포함한다. 늦은 callback 등 남은 fake 범위가 있어 Task는 IN_PROGRESS/PARTIAL을 유지한다.

- P01-T04 후속 감사: 방금 검증한 Android `sdk-testing`과 Swift `OfflineFakeTests`가 CI 필터에 포함되지 않는다. 해당 테스트를 필수 lane에 넣고 로컬에서 실행 수/skip을 재확인한다. 원격 CI는 미실행으로 유지한다.

- P01-T04 CI Swift 필터와 동일한 host 실행은 필수 6개 class, XCTest 16건 PASS/skip 0 (`artifacts/p01-fake-swift-ci.log`); Android Fake는 직전 JUnit 1건 PASS. GitHub Actions/macOS CI 자체는 NOT_RUN이며 원본 로그는 커밋하지 않는다.

- P01-T04 CI YAML 파싱·원장·diff 검사 PASS. 커밋 전: 테스트 필터 및 기록만 포함하며 원격 CI와 실제 플랫폼을 완료로 표시하지 않는다.

- P01-T05 시작: Native BackendClient의 mock HTTP 200/401/timeout/invalid JSON, token 저장·redaction 및 개발 HTTP 제한에 대한 현행 코드와 테스트를 대조한다. 실제 provider·실기기 보안 저장소는 구분한다.

- P01-T05 양 Native `BackendClientTest(s)`에 200/401/timeout/invalid JSON·오류 redaction 검사가 있으나 현재 원격 workflow 필수 필터에서 빠져 있다. 분리된 CI 명령 및 비어 있는 테스트 방지 검사를 연결하고 로컬 실행한다.

- P01-T05 Android local loopback `BackendClientTest` JUnit 1건과 Swift URLProtocol stub `BackendClientTests` XCTest 1건 PASS/skip 0: HTTP 상태/timeout/invalid JSON 및 합성 오류 redaction. Kotlin 별도 파일 deprecated URL 경고 1건; 실제 원격 서버·TLS·실기기 저장소 검증이 아니다. CI remote NOT_RUN.

- P01-T05 커밋 전 CI YAML 파싱·원장·diff PASS. 필수 테스트 CI 연결과 로컬 실행 증거만 포함하고 Task 및 실플랫폼 검증은 PARTIAL로 유지한다.

- P02-T06 시작: 기존 local smoke의 실제 DB 격리·핵심 시나리오·음성 검증 및 현재 증거를 점검한다. 기존 사용자 DB를 변경·삭제하지 않는다.

- P02-T06 블로커 발견: `smoke-local.sh`는 세 검사 성공 여부와 무관하게 Unity push 미실행을 이유로 무조건 exit 1이며, 하위 스크립트는 고정 서버·Docker DB와 A/B 계정을 사용한다. 현재 환경에서 기존 데이터에 쓰지 않고 독립 서버/DB로 실행할 수 있는 재사용 경로를 확인한다. 기존 DB에는 실행하지 않았다.

- P02-T06은 Backend 전용 smoke가 완료 기준인데 현재 Unity 미실행을 강제 실패 원인으로 삼는다. 고정 DB에 실수로 쓰지 않도록 명시적 격리 환경 opt-in을 요구하고, 하위 검사 실패는 유지하면서 세 검사가 실제 성공할 때만 Backend 범위 성공을 반환하도록 고친다. 격리 테스트를 별도로 추가하며 Unity 통과로 기록하지 않는다.

- P02-T06 격리 stub 단위 시험 2건 PASS/skip 0: opt-in 누락 exit 2, 하위 실패 exit 1, 세 stub 성공 시 Backend 범위 exit 0 및 Unity NOT_RUN 표시. 이 결과는 실제 서버·DB smoke 성공이 아니다.

- P02-T06 CI YAML·shell 구문·원장·diff 검사 PASS. 커밋 전: aggregate 종료 판정, stub 단위 시험, CI와 현재 문서만 포함한다. 고정 DB에 실행하지 않았고 실제 Backend smoke·틀린 잔액 음성 테스트는 NOT_RUN이므로 Task PARTIAL 유지한다.

- P02-T06 전용 PostgreSQL 컨테이너와 loopback DB가 실행 중임을 확인했다. 기존 DB는 사용하지 않고 새 무작위 테스트 DB·role과 새 loopback port를 사용하는 격리 실행 경로를 추가한다. 생성한 테스트 DB는 기존 정책대로 보존한다.

- P02-T06 새 loopback 서버·고유 DB `gamebridge_ci_7805cd13e7`에서 `run-backend-smoke-isolated.py --run-local` exit 0 (`artifacts/backend-smoke-isolated-t07g1q3l`): auth 16·purchase 13·device/config 19 assertions, Backend LOCAL_MOCK만 PASS. Unity/실 provider/원격 push NOT_RUN, DB·role 보존. 잘못된 잔액 기대 음성 시험은 아직 미실행이다.

- P02-T06 재실행 `artifacts/backend-smoke-isolated-he08vjff` exit 0: 새 DB `gamebridge_ci_a6026477d3`에서 auth 16·purchase 13·device/config 19 assertions 및 틀린 잔액 기대 복사본의 예상 실패 확인. local mock Backend 전용이며 Unity/실 provider/원격 push는 NOT_RUN. 임의로 DB·role을 지우지 않았다.

- P02-T06 전용 새 DB에서 실제 HTTP/DB smoke 및 틀린 기대값 음성을 충족해 IMPLEMENTED/로컬 PASS. 실제 외부 provider와 Unity 결과로 확장 해석하지 않는다.

- P02-T06 커밋 전 aggregate stub 2건·원장 및 원장 음성·diff PASS. 격리 runner/loopback 선택·정제된 증거·문서만 포함하고 생성된 DB·role·로그·키는 커밋하지 않는다.

- P02-T03 시작: 동일 transaction·교차 사용자·premium 중복의 현재 DB 강제 조건과 격리 smoke/DB 회귀 증거를 대조한다. P02-T06은 6e1e95e 로컬 커밋이다.

- P02-T03 격리 smoke에 거래 중복·교차 사용자·premium 재요청은 포함되지만 catalog 응답 확인은 빠져 있다. 두 상품을 명시 검사하고 단위 지급이 클라이언트 금액 필드에 좌우되지 않는지 격리 DB에서 확인한다.

- P02-T03 전용 새 DB `gamebridge_ci_6a1f22d6f1`에서 catalog와 위조 amount/userId/price가 포함된 구매를 더한 smoke exit 0 (`artifacts/backend-smoke-isolated-hbw5kx_k`): auth 16·purchase 14·device 19 assertions 및 잘못된 기대 잔액 음성 PASS. local mock만 검증했으며 실제 스토어는 별도다.

- P02-T03 계획된 mock catalog·중복·타 사용자 거부·premium 재요청을 격리 DB로 확인하고 IMPLEMENTED/로컬 PASS로 갱신했다. 실제 스토어 검증은 포함하지 않는다.

- P02-T03 커밋 전 원장 일관성·원장 음성·diff PASS. 구매 smoke assertion과 정제된 증거 및 진행 문서만 포함한다. 테스트 DB·로그·키는 제외한다.

- 현재 재개 기준: 로컬 HEAD는 직전 커밋 `3d84945` 이후의 체크포인트 커밋이며, 새 Backend 격리 DB·role은 보존한다. P05-T03 iOS 26.5 StoreKit은 FAIL, 실제 provider 13건은 WAITING_USER다.

- 체크포인트 원장·diff 검사 PASS. 커밋 전: 현재 다음 작업과 검증 상태만 기록하고 미추적 Demo·캐시 및 보존 DB를 건드리지 않는다.

- P09-T08 재개: manifest suite 실행 경로의 저장소 이탈·절대 경로·심볼릭 링크를 disposable fixture로 확인하고 fail-closed 검사 한 단위를 보강한다. 시작 HEAD 8cb4003; 기존 미추적 Demo·캐시는 보존한다.

- P09-T08 기존 manifest 정상 검사 및 기존 음성 검사 PASS. suite 명령 경로 이탈을 별도 변조본으로 재현한다.

- P09-T08 블로커 재현: contracts suite를 `python3 /usr/bin/true`로 바꾼 복사 manifest를 기존 `check-manifest.py`가 exit 0으로 승인했다 (`artifacts/p09-manifest-path-0lu14th1`). 제품 테스트를 실행하지 않았고 원본 manifest는 보존했다. 저장소 내부 정규 경로만 허용하도록 고친다.

- P09-T08 수정 후 원본 manifest PASS, 변조 음성 검사 PASS(절대·상대 이탈·외부 symlink·bash·실행파일 5종 포함), 최초 변조본은 예상대로 exit 1. 이 검사는 inventory 경로 검사이며 시나리오 제품 실행 자체는 아니다.

- P09-T08 Push 전 검사 준비: gitleaks 실행 시 지정 모듈 경로와 실제 go.mod 경로가 달라 실행되지 않았다. 정확한 모듈 경로로 재시도하며, 아직 비밀정보 검사 통과로 기록하지 않는다.

- P09 인계 Push 전 이력 검사: gitleaks 8.24.2가 origin 이후 138개 커밋을 검사해 1건을 탐지하고 exit 1을 반환했다. 값은 출력하지 않으며 위치와 허위 탐지 여부를 확인하기 전 Push하지 않는다.

- 이력 비밀정보 검사 1건은 `scripts/registry-smoke.cs`의 공개 redaction 테스트 전용 합성 고정 문자열로 확인했다(커밋 2f0c32e, generic-api-key). 실제 credential이라는 증거는 없으며 스캐너 원본 결과는 제외한다. 다른 파일 형식·개인정보와 최종 diff를 추가 검사한다.

- P09-T08 검증: aggregation 13건, CI gate 6건, manifest 정상 및 음성, 진행 원장, diff 검사 PASS/skip 0. 변경 범위는 manifest 경로 fail-closed 한 단위이며 전체 P09-T08은 PARTIAL이다. Git 이력에서 private key/AWS/GitHub token 패턴과 민감 확장자·캐시 경로는 발견되지 않았고 email 패턴은 합성 example.invalid 1종이다.

- P09-T08 커밋 전: manifest 경로 검사·복사본 음성 시험·P09 재개 감사 및 진행 문서만 개별 stage한다. 전체 P09는 PARTIAL, 실제 provider 및 현재 source strict 미검증을 유지한다.

- P09 인계 최종 이력 확인: 139개 커밋 gitleaks 결과는 이전에 확인한 합성 redaction fixture 1건뿐이다. 전체 범위 `git diff --check`는 기존 Unity 생성 .meta의 빈 필드 후행 공백으로 exit 2였다. 이번 P09 커밋 자체 diff는 통과했으며 해당 Unity 파일은 재작성하지 않는다. 최종 원격 브랜치 유무와 이력을 별도로 확인한다.

- P09-T08 인계 기록 커밋 전: origin 이후 diff는 Unity `.meta` 제외 PASS, 원격 기존 브랜치와의 분기 없음(로컬 139개 앞섬), 신규 handoff 브랜치 최초·재확인 시 없음. 정제 감사와 원장만 stage한다.

- P09-T08 시작: manifest suite 명령의 인터프리터·인자 검증과 scenario 실행 전 fail-closed 검사를 보강한다. 시작 HEAD 및 handoff 원격은 c862f723 일치, 미추적 파일 보존. DB mutation은 이번 범위에서 제외한다.

- P09-T08 현행 suite 30개 명령을 명시 allowlist로 대조하고 scenario 실행 전 동일하게 로드한 manifest 전체를 검증하도록 구현했다. 기존 manifest 정상 및 기존 음성 검사 PASS; 명령 실행 차단·마커 및 정상 scenario 실행은 아직 미검증이다.

- P09-T08 `test_manifest_execution_guard.py` 2건 PASS/skip 0: 격리 manifest 8종(절대·상위·외부 symlink·sh/bash/python 옵션·임의 추가 인자·Gradle 옵션) exit 1 및 마커 미생성, 다른 suite 오염 시 R50 미실행; 정상 R50 exit 0. 이는 하네스 단위이며 제품 전체 검증은 아니다.

- P09-T08 정상 manifest·기존 음성·원장·CI YAML 파싱·diff PASS. marker 검사를 CI에 연결했으나 GitHub Actions 원격 실행은 NOT_RUN. malformed manifest와 suite 실행 차단도 추가 확인한다.

- P09-T08 실행 guard 3건 PASS/skip 0: 8개 변조 명령·다른 suite 오염·잘못된 JSON/자료형/필수값은 실행 전에 거부했고 정상 R50은 실행됐다. 추가로 정상 R01 Kotlin/Swift/C# contract 경로를 실제 실행한다.

- P09-T08 정상 `run-scenario.py R01` exit 0: Kotlin 10·Swift 12·C# 1 PASS/skip 0 (`artifacts/contracts-y_9ccyrf`, 시작 HEAD c862f723 + 미커밋 변경). Unity Player·실 provider는 이 테스트 범위 밖이다.

- P09-T08 재검토 중 JSON `null`은 checker 기본 인자와 혼동될 수 있음을 발견했다. 실행 전에 manifest가 객체인지 명시 검증하고 음성 사례를 추가한다.

- P09-T08 `null` 포함 잘못된 manifest 4종과 변조 명령 8종을 차단하고 정상 R50 실행을 확인한 guard 3건 PASS/skip 0. 전체 Task는 PARTIAL, 원격 CI는 NOT_RUN이다.

- P09-T08 재검증 aggregation 13건·CI gate 6건·manifest 음성·diff PASS/skip 0. 커밋 전 실행 guard·명령 allowlist·독립 테스트·CI 연결 및 정제 문서만 개별 stage한다. 원격 CI·실 provider 미실행, P09 전체 PARTIAL 유지.

- P09-T08 stage 검사: gitleaks 8.24.2 staged diff exit 0, 탐지 0건. 커밋 전 검사 결과 기록만 다시 stage하고 diff를 확인한다.

- P09-T08 DB mutation 시작: 로컬·handoff 원격 HEAD 37061d9 일치. 기존 Docker PostgreSQL은 127.0.0.1:54329에서 실행 중이며 새 DB/role·서로 다른 test schema만 사용한다.

- P09-T08 하네스 보강: mutation/정상 JUnit XML을 각각 보존하고 실행 시각·Gradle exit·tests/failures/errors/skipped·예상 assertion을 검사한다. 문법·diff 검사 PASS; DB 실제 실행은 다음 단계다.

- P09-T08 새 전용 DB `gamebridge_ci_4e486cab7f`에서 `check-ledger-mutation.py` exit 0 (`artifacts/ledger-mutation-il0fvfi4`): mutation Gradle exit 1, JUnit 1건 중 예상 실패 1·errors/skip 0; 별도 신규 스키마 정상 Gradle exit 0, 1건 PASS·errors/skip 0. XML 두 파일을 각각 보존했다. 스키마·제약 실상태를 추가 대조한다.

- P09-T08 보존 XML 대조: mutation은 정확히 `DataIntegrityViolationException`이 발생하지 않았다는 assertion 실패, 정상은 동일 testcase PASS. 전용 DB에는 서로 다른 신규 schema 2개가 있고 각각 purchase_id UNIQUE 제약 0개/1개로 확인됐다. 제약 이름·예상 실패 유형을 하네스에서 더 엄격히 판별한다.

- P09-T08 XML 판정 단위 1건 PASS/skip 0: stale report, 무관 실패, skip/error, 다른 testcase를 거부하고 정확한 실패·정상 결과만 허용한다. 이 수정 후 새 DB에서 mutation/정상을 다시 실행한다.

- P09-T08 보강 후 새 DB `gamebridge_ci_54affdf462`에서 하네스 exit 0 (`artifacts/ledger-mutation-1mys19ze`): mutation Gradle exit 1, 정확한 제약 assertion 실패 1/1, errors·skip 0; 정상 Gradle exit 0, 1/1 PASS·errors/skip 0. 두 JUnit XML은 각 별도 파일로 보존됐다. DB별 제약을 재확인한다.

- P09-T08 수정 후 DB 제약 직접 대조 PASS: mutation schema `gb_ledger_invariant_93b32ebcf60f49ed9ad8438b93b46cf8` UNIQUE 0, 정상 schema `gb_ledger_invariant_b0a86827754944719fbca5606f012e75` UNIQUE 1. XML testcase·실행/실패/error/skip 수 일치. DB/role/schema는 보존했다.

- P09-T08 DB mutation·정상 대조 한 단위 PASS: [정제 evidence](evidence/p09-ledger-mutation-20261113.md). P09-T08 전체 IN_PROGRESS/PARTIAL, iOS 26.5 FAIL과 실제 provider WAITING_USER 유지.

- P09-T08 보고서 판정 단위 1건·진행 원장·CI YAML·diff PASS. 커밋 전: 하네스 freshness/정확한 실패 확인, 단위시험, 정제 evidence 및 진행 문서만 개별 stage한다. P09 전체 PARTIAL과 실 provider 미검증 유지.

- P09-T08 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 이 기록만 다시 stage하고 관련 파일만 커밋한다.

- P09-T08 통합 자체시험 시작: 시작 및 handoff 원격 HEAD c9f9dfb 일치. 기존 manifest guard·원장 mutation 구현은 재작성하지 않는다.

- P09-T08 자체시험 보강: sandbox에서 별도 challenge 뒤 합성 mock identity에 401을 요구하는 독립 JUnit을 추가하고 해당 testcase만 실제 실행·식별하도록 연결했다. marker 실행은 테스트 건수가 아닌 checker 1회로 기록하고 정상 contract JSON의 Kotlin/Swift 건수를 집계한다. 아직 통합 실행 전이다.

- P09-T08 통합 실행: 전용 DB `gamebridge_ci_575ffbea78_local`·`gamebridge_ci_575ffbea78_sandbox` 및 새 role 생성 후 각 프로필 bootstrap/health 통과. 9개 lane 실제 실행 중이며 전체 결과는 아직 미확정, DB와 role은 보존한다.

- P09-T08 통합 자체시험 첫 실행 exit 0 (`artifacts/harness-self-1wlemrje`): 9/9 lane PASS, checker 6 lane 각 1회·failed/zero 3회, sandbox 독립 JUnit 1건, Kotlin/Swift 22건 및 C# smoke 1회. 위 수치는 7개 checker 실행을 제품 test case로 세지 않는다. 결과 보존·집계 실패 경계 검사를 보강한 뒤 전체를 다시 실행한다.

- P09-T08 보고서 guard 단위 2건 PASS/skip 0: sandbox 지정 testcase·fresh JUnit·실패/skip 및 누락·0건·exit 실패를 거부한다. sandbox JUnit은 실행 증거 디렉터리에 복사하며 최종 수정본의 9개 lane을 새 전용 DB에서 재실행한다.

- P09-T08 최종 수정본 자체시험 exit 0 (`artifacts/harness-self-0wr81lum`), 새 local/sandbox DB `gamebridge_ci_8c603a61f1_*`: 9/9 lane PASS/skip 0. checker 6 lane 각 1회·failed/zero 3회, sandbox 독립 JUnit 1건, Kotlin/Swift 22건 및 C# smoke 1회. 실행별 XML과 음성 실패 원인을 대조한다.

- P09-T08 최종 실행 증거 대조: sandbox 독립 testcase 1건·정상 contract Kotlin/Swift 22건, ledger 내부 mutation 예상 실패 1건 및 정상 1건 확인. 계약 변조 내부 Kotlin/Swift 실행·예상 실패 수도 별도 집계하기 위해 실제 하위 JSON 경로를 연결한다.

- P09-T08 집계 보강: 계약 변조의 Kotlin/Swift 실제 실행·예상 실패 2건과 C# smoke 정상, 원장 mutation·정상 JUnit 각 1건을 하위 결과에서 읽어 기록한다. 예상 실패를 별도 표시하고 무관한 C# 실패·누락은 거부한다. 수정 후 전체 9 lane을 다시 실행한다.

- P09-T08 최종 통합 자체시험 `artifacts/harness-self-_hrkwuit` exit 0, 새 local/sandbox DB `gamebridge_ci_d9834a1423_*`: 9/9 PASS, 무관 실패·errors·skip 0. 계약 변조 Kotlin/Swift 22건(예상 실패 2), 원장 변조/정상 2건(예상 실패 1), sandbox 401 1건, 정상 계약 22건과 별도 checker 수가 보고됐다.

- P09-T08 실행 증거 대조: sandbox 독립 XML testcase 1건·failure/error/skip 0, 정상 contract Kotlin 10·Swift 12·C# smoke 1, ledger JUnit mutation/정상 각 1건과 예상 Gradle exit 1/0을 확인했다. 실제 Provider 인증과 전체 strict 검증은 실행하지 않았다.

- P09-T08 통합 자체시험 9/9 PASS·exit 0: [정제 evidence](evidence/p09-self-check-20261113.md). 테스트·checker 호출과 예상 mutation 실패를 구분한다. 전체 strict 미실행, P09 전체 PARTIAL 유지.

- P09-T08 보고서 guard 2건·원장 및 manifest 검사·CI YAML·diff PASS/skip 0. 커밋 전: 독립 sandbox 401 test, 9 lane 정확한 집계·자체 단위시험·CI 및 정제 evidence/진행 문서만 개별 stage한다. 원본 로그·키·DB는 제외한다.

- P09-T08 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 해당 기록을 stage해 관련 변경만 로컬 커밋한다.

- P09-T06 시작: HEAD/원격 f09d1ed 일치. 기존 scenario-coverage는 정적 mapping 50건을 실행 테스트 50건으로 기록하므로 checker 증거와 실제 실행 수를 분리한다. 새 DB 및 독립 simulator만 사용한다.

- P09-T06 집계 수정 검증: aggregation 단위 14건 PASS/skip 0. 정적 매핑은 tests=0, checks=1, mappedScenarios=50, executionStatus=NOT_RUN이며 실제 manifest checker 로그가 없거나 실행 건수를 50으로 기록하면 실패한다. 현재 source strict 실행 전 변경을 로컬 커밋한다.

- P09-T06 커밋 전 원장·manifest·diff PASS. 수정된 집계 코드·단위시험과 진행 문서만 stage하며 전체 strict 및 외부 provider는 아직 미실행이다.

- P09-T06 strict 시작 준비: 새 local/sandbox DB·role과 새 synthetic iOS simulator를 만드는 기존 runner를 사용한다. 기존 staging 및 package cache는 읽어 새 consumer에 복사하며 Unity Editor lane을 opt-in한다. 사용자 AVD·기존 simulator는 사용하지 않고 PII/Unity push Player lane은 별도 환경 대기다.
- P09-T06 커밋 전: strict 시작 checkpoint만 기록해 tracked-clean 소스에서 한 차례 실행한다. 기존 26.5 실패는 보존한다.

- P09-T06 현재 소스 strict 한 차례 실행 종료: 전체 FAIL / exit 1, 외부 WAITING_USER 13 (`artifacts/verify-all-u2vuk3u_`, orchestration `artifacts/strict-isolated-myjcd44z`, 소스 d6bbe7c). 실패·환경 대기 원인과 lane별 실행 결과를 확인하며 이전 26.5 실패를 유지한다.

- P09-T06 strict 결과 대조: 총 49 lane 중 PASS 46(정적 mapping 검사 1 포함), FAIL 1(이전 P05-T03 기록), DEFERRED_ENV 2(Unity Player 푸시·PII), 외부 13 WAITING_USER. 이번 실행의 iOS 18.6 StoreKit 복구 PASS는 기존 iOS 26.5 실패를 해결하지 않는다. 실행 중 새로 기동된 전용 Process Simulator는 삭제 없이 shutdown했다.

- P09-T06 현재 source strict: PASS 46(정적 매핑 검사 포함) / FAIL 1(기존 P05-T03) / DEFERRED_ENV 2, 전체 exit 1. 시나리오 매핑 50은 실행 0과 구분한다. [기준선 evidence](evidence/p09-strict-baseline-20261113.md).

- P09-T06 기준선 정리 후 aggregation 14건·self-check report 2건 PASS/skip 0, 진행 원장·diff PASS. 커밋 전: lane별 정제 evidence와 과거 정적 mapping 표현 정정 및 진행 문서만 포함한다. P09 전체 PARTIAL 유지.

- P09-T06 커밋 전 staged gitleaks exit 0, 탐지 0건. 정제 기준선 기록을 커밋한다.

- P09-T05 시작: HEAD/원격 c4269e9 일치, tracked clean. Unity 6000.5.8f1 라이선스 활성·Android/iOS 모듈 확인, 최신 staging 147개 checksum PASS 및 fb48371 이후 배포 product 경로 diff 없음. PII/Push Player는 아직 NOT_RUN이다.

- P09-T05 새 전용 Android AVD 2개 생성: `GameBridge_V2_P09_PII_20261113_210717`, `GameBridge_V2_P09_PUSH_20261113_210717`. 기존 AVD는 변경하지 않았다. 아직 부팅·Player 실행은 NOT_RUN이다.

- P09-T05 두 전용 AVD는 부팅 초기 adb offline 상태로 아직 사용할 수 없다. 부팅 완료 및 지정 AVD 이름을 확인한 뒤 진행하며 이 시점 Player 결과는 NOT_RUN이다.

- P09-T05 전용 AVD 부팅 확인: emulator-5580=P09_PII, emulator-5582=P09_PUSH, 각 이름·boot_completed 확인. 다음 `ci-unity-e2e.sh`는 PII·Push·strict를 같은 tracked-clean HEAD에서 수행한다. 커밋 전 시작 기록만 포함한다.

- P09-T05 `ci-unity-e2e.sh` 실행: PII 양 Player gate PASS (`artifacts/unity-pii-current-gh5ksqc3`), strict 전체 FAIL / exit 1 (`artifacts/verify-all-e2d8gd77`, `artifacts/strict-isolated-veycx1cq`). source 5d716bd, 두 Android AVD 최초 전체화면 안내 수동 확인. Push lane 및 기존 실패의 상세를 대조한다.

- P09-T05 strict에서 Push·PII 각 2건 PASS, 나머지 P05-T03 기존 실패로 전체 FAIL(exit 1), 49 lane 중 PASS 48·FAIL 1, 외부 WAITING_USER 13. PII Player 각각 원장 1건/100·동일 HEAD·tracked-clean을 확인했다. 상세 marker 대조 명령은 파일명 착오로 미실행되어 정확한 경로를 확인한다.

- P09-T05 Push 양 Player marker 대조 PASS: receive/dedupe/main thread, background/foreground, network recovery, unregister/logout, synthetic late callback, session switch. Android 실제 AVD 네트워크 전환·iOS 로컬 transport fault injection을 구분한다. 사용한 전용 PII·Push AVD와 Simulator는 삭제 없이 종료했다.

- P09-T05 PII·Push 양 플랫폼 현재 소스 각 2건 PASS, strict 48 PASS/기존 FAIL 1, 전체 exit 1. [Player evidence](evidence/p09-current-unity-player-20261113.md). 실 Provider·실기기 미검증.

- P09-T05 종료 검증: 전용 AVD 프로세스·부팅 Simulator 없음. strict `sourceDirty=true`는 보존한 미추적 Demo/캐시를 포함하며 Player 각 `sourceTrackedDirty=false`와 구분한다. 원장·diff 검사 후 정제 문서만 커밋한다.

- P09-T05 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 정제 evidence·진행 문서만 커밋하고 원본 로그·APK·DB·합성 키는 제외한다.

- P05-T03 독립 원인 분리 시작: HEAD/원격 6c87900 일치. 기존 통합 named/URL·스레드 반복은 하지 않는다. Xcode 26.6, iOS 18.6/26.5 runtime 확인; 제품 SDK와 Backend 없이 test-only 비교를 준비한다.

- P05-T03 독립 UIKit host·XCTest와 1상품 최소 StoreKit 설정을 작성했다. 기존 설정은 실행 시 복사하고 SDK·Unity·Backend·DB 의존성은 없다. 새 runtime별 Simulator에서 각 설정을 1회씩, testcase timeout 60초로 실행할 예정이다. 아직 실제 빌드·실행은 NOT_RUN이다.

- P05-T03 독립 runner 문법·원장·diff PASS. 18.6/26.5 전용 신규 simulator 각 하나에서 최소/현재 설정 2종을 각각 1회씩 실행한다. 각 테스트 60초·명령 150초 상한, 결과는 성공/실패/환경 대기를 구분한다.

- P05-T03 독립 XCTest iOS 18.6 최소 1상품 구성: exit 0, 1건 PASS/skip 0. 기존 구성과 26.5 비교는 진행 중이며 전체 원인은 아직 미확정이다.

- P05-T03 독립 XCTest iOS 18.6 기존 구성: exit 0, 1건 PASS/skip 0. 26.5 전용 신규 Simulator를 만들었으며 비교는 진행 중이다.

- P05-T03 독립 XCTest iOS 26.5 최소·기존 구성 각각 exit 0, 각 1건 PASS/skip 0. SDK 없는 독립 테스트에서는 기존 timeout이 재현되지 않았다. XCTest host와 기존 SwiftUI 실행 앱의 환경 차이를 조사하며 P05-T03 FAIL은 유지한다.

- P05-T03 네 독립 실행 전부 exit 0, 4건 PASS/skip 0 (`artifacts/storekit-isolation-04skqp6v`). 기존 .storekit 복사본 SHA-256이 원본과 일치한다. 26.5 기존 app의 `storekit-session-create` timeout과 달리 XCTest host에서는 재현되지 않았다. Xcode SDK StoreKitTest header의 deprecated 경고는 관찰됐으나 원인 연결 근거는 없다.

- P05-T03 독립 XCTest 18.6/26.5 각 최소·기존 설정 4/4 PASS. 기존 통합 앱 26.5 timeout은 해결로 간주하지 않으며 FAIL/ENV-STOREKIT-26 OPEN 유지. [독립 비교 evidence](evidence/p05-storekit-26-isolation.md).

- P05-T03 커밋 전 원장·diff PASS, 신규 Simulator 2대 shutdown 확인. 독립 test fixture/runner 및 정제 evidence·진행 문서만 stage한다. 제품 StoreKit Provider·원본 xcresult·로그·사용자 미추적 파일은 제외한다.

- P05-T03 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 독립 재현 코드와 정제 문서만 커밋한다.

- P05-T03 독립 앱 비교 시작: HEAD/원격 b4b4c37 일치, 이전 XCTest 양 runtime PASS. SDK·Backend 없이 기존 설정의 app bundle URL과 simctl launch를 비교한다.

- P05-T03 독립 앱 경로 작성: 명시 opt-in일 때만 app bundle `Current.storekit` URL을 사용하며 started·생성 전·생성 후·예외를 각각 별도 파일로 기록한다. 테스트 build·runtime 실행 전이다.

- P05-T03 독립 앱 runner 문법·원장·diff PASS. 동일 app을 build한 뒤 18.6/26.5 새 simulator에서 각각 한 번 launch하고 각 75초 checkpoint를 대기한다. 빌드·framework 실패는 session 실패와 분리한다.

- P05-T03 독립 UIKit app build exit 0, app bundle 설정 파일 존재 확인. iOS 18.6 전용 Simulator를 새로 생성했고 앱 실행 결과는 아직 미확정이다.

- P05-T03 iOS 18.6 독립 앱 simctl launch exit 0, 시작·세션 생성 전·생성 후 checkpoint 확인 PASS, timeout 없음. XCTest 없는 standalone이며 실제 스토어는 아니다.

- P05-T03 독립 앱 iOS 26.5 `simctl launch` exit 0, started·session-create-before checkpoint 뒤 75초 동안 생성 후/예외 미기록으로 FAIL timeout (`artifacts/storekit-standalone-zu6etuhp`). 18.6은 생성 후 checkpoint PASS. timeout과 앱 조기 종료를 분리하기 위해 보존된 launch/terminate 및 결과를 대조한다. 기존 P05-T03 FAIL을 유지한다.

- P05-T03 블로커: 26.5 종료 확인 로그는 대상 프로세스가 이미 없다고 보고하고, 해당 PID의 Simulator 진단 보고서는 SIGABRT를 기록했다. 따라서 최초 runner의 `session-create-timeout` 표기는 부정확하며 앱이 checkpoint 이후 종료된 사실과 종료 원인을 별도로 분석한다. 기존 P05-T03 FAIL 유지.

- P05-T03 원인 분리: 신규 26.5 독립 앱 PID 87401의 crash report는 SIGABRT이며 StoreKitTest `XCTestLibrary` → `__getXCTestConfigurationClass_block_invoke` → `SKTestSession` stack이다. 기존 통합 앱의 17:00:37 crash report도 같은 함수 경로를 보여주지만 정확한 실행 매칭을 추가 확인한다. XCTest 프레임워크를 주입하거나 우회하지 않는다.

- P05-T03 기존 crash report의 simulator UUID `481932FB-...`가 `artifacts/xcode-process-recovery-na8yq85t/result.json`과 일치한다. 기존 통합 앱도 해당 시도에 SIGABRT 및 동일 StoreKitTest XCTestLibrary 호출 경로를 보였다. 당시 runner는 앱 종료를 감지하지 못해 75초 checkpoint timeout으로 보고했다. 새 독립 앱도 같은 유형이지만 Apple 내부 원인이나 수정법은 미확정이다.

- P05-T03 기존 통합 앱 crash UUID는 이전 timeout 결과의 simulator UUID와 일치하며 SIGABRT stack의 StoreKitTest `XCTestLibrary` 경로가 신규 독립 앱과 동일하다. 새 진단 runner에 앱 조기 종료와 timeout 구분을 추가했고 단위 1건 PASS/skip 0. 분류 보강을 확인하기 위해 26.5 신규 Simulator에서 제한적 진단 1회를 추가한다.

- P05-T03 진단 보강 후 26.5 신규 Simulator 1회: launch exit 0, 생성 전 checkpoint 이후 프로세스 종료를 `app-exited-during-session-create` FAIL로 감지 (`artifacts/storekit-standalone-6ieup1xl`, 전체 exit 1). 초기 결과의 timeout 오분류는 그대로 보존하고 crash 근거로 정정한다.

- P05-T03 독립 앱: 18.6 PASS, 26.5 세션 생성 중 SIGABRT FAIL(재대조 1회 동일). XCTest 양 runtime PASS와 구분하며 기존 FAIL/ENV-STOREKIT-26 OPEN을 유지한다. [비교 evidence](evidence/p05-storekit-26-isolation.md).

- P05-T03 커밋 전: standalone 분류 단위 1건 PASS, 원장·diff PASS, 전용 Simulator 3대 shutdown 확인. 실제 실행 앱·runner·정제 evidence만 stage하며 기존 통합 앱, 제품 Provider, 원본 crash report·사용자 파일은 제외한다.

- P05-T03 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 재현 코드와 정제 문서만 커밋한다.

- P05-T03 XCTest 검증 시작: 시작 HEAD/원격 824fa4d 일치. 기존 GameBridgeStoreKit scheme과 구매·Ask-to-Buy 테스트를 재사용하며 새 26.5 Simulator에서 순차 실행한다. 이전 독립 앱 crash는 재실행하지 않는다.

- P05-T03 기존 두 XCTest에 세션·store 시작·상품·구매/가짜 지급·완료/pending checkpoint를 추가했고, 성공 구매의 unfinished 0을 명시 assertion으로 확인하도록 보강했다. 검증 실행 전이며 결과는 NOT_RUN이다.

- P05-T03 기존 StoreKit scheme 순차 실행 runner의 문법·원장·diff 검사 PASS. 테스트별 90초, 명령별 240초 상한과 fresh Simulator 종료를 적용한다. 26.5가 미통과일 때만 18.6 대조를 실행한다. 아직 XCTest 결과는 없다.

- P05-T03 iOS 26.5 구매 XCTest exit 65 / FAIL, 마지막 checkpoint `products-before`; 세션 생성과 store.start는 통과했지만 상품 조회 이후는 미확인이다. 실패가 assertion·예외·환경 중 무엇인지 xcresult를 대조한다. pending 테스트는 순차 실행 중이다.

- P05-T03 iOS 26.5 pending XCTest도 exit 65 / FAIL, 마지막 checkpoint `products-before`. 두 시험 모두 상품 이후 구매·pending·지급 검증은 미실행이며 새 18.6 Simulator 양성 대조를 시작한다.

- P05-T03 18.6 양성 대조 구매 XCTest exit 0, 1건 PASS/skip 0, complete checkpoint 확인. 세션·상품 조회·가짜 지급·finish assertion이 통과했다. 18.6 pending은 이어 실행 중이다.

- P05-T03 18.6 pending 대조 exit 0, 1건 PASS/skip 0, 가짜 grant 미호출 및 complete 확인. 전체 비교 runner exit 1 (`artifacts/storekit-xctest-comparison-l5tx8137`)은 26.5 두 상품 조회 실패 때문이다.

- P05-T03 검토: 추가 계측의 `store.products()`는 기존 구매 테스트보다 범위가 넓어 두 상품 모두를 요구한다. 첫 26.5 실패는 이 추가 사전 조회에서 발생했으므로 기존 coins 구매 경로 자체의 결과와 분리한다. 직접 조회에서 반환된 ID만 기록하고 assertion 범위를 늘리지 않는 계측으로 수정해 제한적으로 재대조한다.

- P05-T03 계측 수정: 공용 store의 두 상품 강제 조회를 제거하고 원래 구매 경로의 동작을 유지하면서 StoreKit 직접 조회의 반환 ID만 기록한다. 26.5 실패 및 18.6 최초 대조는 보존하고 동일 계측으로 26.5 두 테스트와 필요 시 18.6을 다시 비교한다.

- P05-T03 수정 계측 26.5 구매 XCTest exit 65 FAIL: 직접 상품 조회 결과 빈 목록, 원래 coins 구매 호출 이전 checkpoint에 도달했고 구매 호출에서 실패했다. xcresult 오류 종류와 pending 대조를 확인한다.

- P05-T03 수정 계측 26.5 pending XCTest도 exit 65 FAIL, `purchase-before`에 도달 후 상품 미조회 경로를 대조한다. 18.6 동일 계측 양성 대조 시작.

- P05-T03 수정 계측 동일 18.6 대조: 구매·pending 각각 exit 0, 각 XCTest 1건 PASS/skip 0. 26.5 두 테스트는 각각 exit 65·PRODUCT_NOT_FOUND (`artifacts/storekit-xctest-comparison-jryw7wv_`, 전체 exit 1). 기존 P05-T03 FAIL·ENV OPEN 유지.

- P05-T03 4개 `.xcresult` 재대조: 26.5 각 1건 실패·skip 0, 18.6 각 1건 PASS·skip 0. 이전 standalone 분류 단위 1건·runner 문법·원장·diff PASS. 커밋 전 test-only 계측·runner와 정제 문서만 stage하며 원본 로그·Simulator 데이터는 제외한다.

- P05-T03 커밋 전 staged gitleaks exit 0, 탐지 0건. test-only 코드와 정제 문서만 커밋한다.

- P05-T03 상품 조회 원인 분리 시작: 시작 HEAD/원격 49a2546 일치, Apple TN3185 및 현재 설정·scheme을 대조한다. 기존 구매·pending과 독립 앱 SIGABRT는 재실행하지 않는다.

- P05-T03 scheme 대조: 생성된 `GameBridgeStoreKit.xcscheme`의 LaunchAction은 원본 .storekit를 참조하고 TestAction은 GameBridgeSample host와 GameBridgeStoreKitTests target을 지정하나 별도 StoreKit 참조는 없다. 이 사실만으로 결함이라 판단하지 않는다. 이전 test bundle 복사본은 원본과 동일하다. 독립 XCTest 상품 조회를 추가한다.

- P05-T03 독립 XCTest 상품 조회 runner 작성·문법·원장·diff PASS. 세션 생성과 상품 조회를 별도 checkpoint로 기록하고 product ID 두 개가 정확히 일치할 때만 PASS한다. 26.5/18.6 신규 Simulator 각 1회, 결제·pending은 실행하지 않는다.

- P05-T03 SDK 없는 독립 XCTest iOS 26.5: SKTestSession 생성 PASS, 상품 조회는 빈 ID 배열로 FAIL, xcodebuild exit 65. 18.6 양성 대조를 진행하며 원인은 확정하지 않는다.

- P05-T03 독립 XCTest iOS 18.6: 세션 PASS, 정확히 coins_100·premium_unlock 조회 PASS, exit 0. 26.5 세션 PASS이나 빈 목록 FAIL/exit 65, runner 전체 exit 1 (`artifacts/storekit-isolation-products-dwknj5y4`). 새 Simulator 2대 종료·보존, 기존 P05 FAIL 유지.

- P05-T03 18.6 `.xcresult` 1 PASS/skip 0 재확인, 26.5 1 FAIL/skip 0의 직접 반환은 빈 배열이었다. 기존 bundle·원본 config hash와 요청 ID 일치. 설정 JSON에 Load Products 오류 주입 필드는 없지만 실제 활성 config·네트워크 경로는 계측하지 않아 단정하지 않는다.

- P05-T03 독립 XCTest: 26.5 세션 PASS·상품 빈 목록 FAIL, 18.6 세션 및 두 상품 PASS. 기존 FAIL/OPEN·sandbox WAITING_USER 유지. [비교 evidence](evidence/p05-storekit-26-isolation.md).

- P05-T03 커밋 전: 26.5/18.6 xcresult 각 1건·실패/skip 및 config hash, 원장·diff 검사 확인. 독립 XCTest·runner·정제 evidence와 진행 문서만 stage하며 제품 Provider·원본 로그·xcresult는 제외한다.

- P05-T03 커밋 전 staged gitleaks 8.24.2 exit 0, 탐지 0건. 관련 테스트·정제 문서만 커밋한다.

- P05-T03 scheme A/B 시작: 시작 HEAD/원격 b2937ba 일치. 기존 26.5 독립 XCTest 상품 미조회 결과는 유지하며 두 복사본에서 run.storeKitConfiguration 변수만 비교한다.

- P05-T03 A/B runner 문법·원장·diff PASS. 복사본의 앱·test·설정 바이트 및 StoreKit 참조 제거 후 scheme XML 동일성을 검증한 뒤에만 새 26.5 Simulator 각 1회씩 상품 조회한다. 실제 활성 config는 별도 NOT_CONFIRMED다.

- P05-T03 A/B 초기 준비는 scheme 정규화 비교에서 차이를 감지해 exit 1 (`artifacts/storekit-scheme-ab-2ytgnfm0`), Simulator·XCTest는 아직 실행하지 않았다. StoreKit 참조 외 생성 차이의 원인을 확인한다.

- P05-T03 초기 scheme 차이는 XcodeGen이 B의 run stanza에 빈 `CommandLineArguments`를 추가한 것이었다. A 원본은 그대로 두고 B의 빈 요소만 제거해 실제 scheme의 의미 및 요소가 StoreKit 참조 하나만 다르도록 정규화한다. 비지원 설정·우회는 추가하지 않는다.

- P05-T03 A/B 재생성: A 원본 scheme 유지, B의 XcodeGen 빈 인자 요소 제거 후 StoreKit 참조 외 XML 구조 동일 PASS; test/app/config 바이트도 동일. 새 26.5 Simulator A 실행 중이다.

- P05-T03 A(기존 scheme) iOS 26.5: 세션 생성 PASS, 상품 빈 배열 FAIL, XCTest exit 65. B 전용 신규 Simulator 대조 진행 중이다.

- P05-T03 A/B 26.5 결과: A·B 모두 SKTestSession PASS, 상품 조회 빈 배열 FAIL, 각 XCTest 1건 실패/skip 0·exit 65, runner exit 1 (`artifacts/storekit-scheme-ab-izz719r6`). RunAction 참조만으로 문제는 해소되지 않았으며 실제 TestAction 활성 설정은 NOT_CONFIRMED다. 반복 우회 실험은 중단한다.

- P05-T03 A/B 두 xcresult 대조: 각 1건 실패·skip 0, 빈 배열과 두 ID의 XCTAssert 불일치. 앱·test·두 설정 복사본 해시 일치, 실제 scheme diff는 LaunchAction StoreKit 참조뿐이다. 새 Simulator 둘은 shutdown·보존했다.

- P05-T03 scheme A/B: 26.5 세션 각 PASS, 상품 두 시험 모두 빈 배열 FAIL. TestAction 활성 설정 NOT_CONFIRMED, 기존 FAIL/OPEN 유지. [A/B evidence](evidence/p05-storekit-26-isolation.md), [미제출 Feedback 초안](evidence/p05-storekit-26-feedback-draft.md).

- P05-T03 커밋 전: A/B xcresult·원장·diff 확인. A/B test-only runner와 정제 evidence·미제출 Feedback 초안·진행 문서만 stage한다. 원본 로그·xcresult·사용자 파일은 제외한다.

- P05-T03 커밋 전 staged gitleaks 8.24.2 exit 0·탐지 0건. 비교 코드와 정제 문서만 커밋한다.

- P09-T07 시작: 로컬·handoff 원격 HEAD c977b24 일치. GitHub CLI 인증됨, default workflow 등록 active, repository Actions 변수 목록 0개. self-hosted 실행 가능성 및 조직·환경 설정을 추가 대조한다.

- P09-T07 확인: owner는 개인 User, repo Actions variable 목록 0개·해당 이름 조회 404, job에 environment 없음. 따라서 현재 `vars.GAMEBRIDGE_UNITY_E2E_ENABLED == true`는 충족되지 않는다. 정적 actionlint v1.7.7은 `macos-26` 및 custom self-hosted label을 구버전 label 목록에서 거부했다. 공식 runner 문서로 macos-26 존재 확인 후 최신 검사기를 검토한다. 원격 dispatch는 아직 NOT_RUN이다.

- P09-T07 static 검증: actionlint 1.7.7은 구버전 label 목록에서 macos-26/custom label을 거부(실제 실패 기록). 1.7.12는 공식 macos-26을 인식하며 격리 설정에 명시한 custom self-hosted label을 포함해 exit 0. owner는 개인 User, repository 변수 0개·해당 변수 404·job environment 없음으로 현재 Unity opt-in 조건 false. default branch workflow_dispatch 등록 active 및 handoff ref c977b24 확인. 이제 원격 hosted run 1회를 시작한다.

- P09-T07 `workflow_dispatch` 1회 요청 성공: run `43481632527`, ref `handoff/p09-resume-20261113`, 예상 SHA c977b24. Hosted/Unity/release job 결과는 아직 미확정이다.

- P09-T07 run 43481632527 확인: 실제 source SHA c977b24, Unity self-hosted job SKIPPED; 네 hosted job 실행 중. skip은 원격 Unity PASS가 아니다.

- P09-T07 원격 inventory-contracts job FAIL, 나머지 hosted jobs 진행 중. 실패한 step과 원인을 원본 로그에서 확인하며 실제 환경/코드 문제를 분리한다.

- P09-T07 원격 inventory 실패 원인 확인: `test_manifest_execution_guard.py`가 fresh checkout에 존재하지 않는 `artifacts/` 아래 임시 디렉터리를 만들려다 FileNotFoundError, 3건 중 error 1. 제품 테스트 실패가 아닌 CI 테스트 환경 초기화 결함이다. 이 경로만 보강한다. 첫 `gh run view --log`는 전체 run 진행 중이라 미제공이었고 job logs API로 해당 job을 확인했다.

- P09-T07 테스트가 artifacts 상위 폴더를 안전하게 생성하도록 한 줄 보강한 뒤 새 `git archive` 격리 checkout(artifacts 없음)에서 manifest guard 3건 PASS/skip 0. 원본 사용자 artifacts는 변경·삭제하지 않았다. 나머지 hosted 결과를 기다린다.

- P09-T07 hosted backend-postgres job 성공. Android는 독립 Maven/R8 소비자, macOS는 synthetic iOS Simulator host 시험 진행 중이다. inventory 결함의 clean checkout 수정은 로컬 3건 PASS이며 원격 재검증은 아직 미실행이다.

- P09-T07 첫 원격 run: Android Native job SUCCESS(계약·fake·clean R8 consumer), Backend SUCCESS, inventory FAIL, Unity SKIPPED. macOS synthetic Simulator host test는 아직 진행 중이다.

- P09-T07 macOS Swift package step은 SUCCESS, synthetic iOS host step 진행 중이다. 원격 inventory 수정 검증을 보강하기 위해 실제 git clone의 빈 artifacts 상태에서 전체 inventory step을 별도 실행한다.

- P09-T07 수정한 clean git clone에서 workflow inventory step 전체 exit 0, Python unittest 24개 suite 68건 PASS. 정적 문서·manifest·metadata 검사도 통과했으며 원격 재실행은 별도다.

- P09-T07 macOS job 진행 중 개별 logs API는 HTTP 404로 아직 제공되지 않았다. job 완료 후 로그를 확인하며 현재 실패로 판정하지 않는다.

- P09-T07 커밋 전: 확인된 fresh checkout artifacts 초기화 결함 1줄과 진행 문서만 포함한다. clean clone 전체 inventory step 24 suite/68건 PASS; 첫 원격 run의 macOS는 계속 진행 중이며 완료 결과는 별도 기록한다.

- P09-T07 커밋 전 staged gitleaks exit 0, 탐지 0건. 수정 1줄과 진행 기록만 로컬 커밋한다.

- P09-T07 첫 원격 run 43481632527 완료 FAIL: Backend·Android·macOS SUCCESS, inventory FAIL(빈 artifacts), basic-ci FAIL(의존 job 실패), Unity SKIPPED, release FAIL. 후속 gate 로그의 실제 실패 사유를 확인하고, 수정 commit 기반 재검증을 준비한다.

- P09-T07 첫 run gate 원인 대조: basic-ci는 inventory=failure를 정확히 전파했고 release-readiness는 basic failure에서 먼저 종료했다. Unity SKIPPED는 성공이 아니다. 수정 commit을 검사·push 후 같은 조건에서 재검증한다.

- P09-T07 재검증 전 커밋: 첫 원격 run 상태와 gate 원인만 기록한다. 91228d8 및 이 기록을 비밀정보·원격 이력 검사한 후 push한다.

- P09-T07 수정 및 첫 run 기록 commit `2af863b`를 handoff에 fast-forward push했다. 전체 2개 commit gitleaks exit 0. repository 변수 재확인 후 수정된 hosted 검증을 재실행한다.

- P09-T07 수정 검증용 두 번째 workflow_dispatch 요청: run 43483388390, 예상 SHA 2af863b. Unity 조건은 재확인 시 여전히 비활성이다. hosted 실제 결과는 대기 중이다.

- P09-T07 수정 SHA 2af863b의 원격 재검증 run 43483388390: inventory-contracts SUCCESS, Unity SKIPPED. Backend·Android·macOS와 두 gate는 아직 진행 중이다. 최초 inventory 실패 이력은 보존한다.

- P09-T07 수정 run inventory 원격 job 로그: unittest 요약 25 suite 합계 70건(설정 schema 2 포함), FAILED/skip 표시 없음, SUCCESS. 이는 정적·하네스 검사이며 원격 Unity Player 검증이 아니다.

- P09-T07 재검증 run: inventory SUCCESS(원격 70건), Backend PostgreSQL SUCCESS, Unity SKIPPED. Android 추가 unit 및 macOS synthetic host 단계 진행 중.

- P09-T07 재검증 run 43483388390 완료: inventory·Backend·Android·macOS·basic-ci SUCCESS, unity-e2e SKIPPED, release-readiness FAILURE, 전체 FAILURE. release gate 로그와 hosted 실제 검사 수를 대조한다.

- P09-T07 재검증 최종 로그: Backend JUnit 13, Android JUnit 45+1+1, Swift XCTest 17 모두 실패/skip 0; synthetic iOS host는 검사상 1건 이상 통과(정확한 수 미출력). release gate는 BASIC=success, UNITY=skipped로 `DEFERRED_ENV` exit 2라 GitHub job FAILURE. 전체 workflow failure는 release 미준비를 반영하며 hosted job 실패가 아니다.

- P09-T07 hosted 재검증: 4개 hosted job·basic-ci SUCCESS, Unity SKIPPED, release gate DEFERRED_ENV(exit 2) / GitHub FAILURE, 전체 failure. P09-T07 전체 PARTIAL, 실제 provider 대기 유지. [결과 evidence](evidence/p09-hosted-ci.md).

- P09-T07 커밋 전 원장·diff PASS. 두 hosted run의 정제된 결과와 CI 문서·진행 기록만 stage하며 원본 job 로그·사용자 미추적 파일은 제외한다.

- P09-T07 커밋 전 staged gitleaks exit 0·탐지 0건. 정제된 결과 문서만 커밋한다.

- P09-T07 self-hosted 사전 점검 시작: 시작 HEAD/원격 2a771c6 일치. 원격 runner 목록 0개, repository 변수 목록 0개. runner 등록·변수 변경·workflow 실행은 이번 범위에 없다.

- P09-T07 읽기 전용 점검: 현재 개발 계정은 admin 그룹의 macOS ARM64이며 전용 runner 계정·개인 파일 접근 차단 증거 없음. 로컬 Unity 활성, Android/iOS 모듈, staging 147 checksum 및 배포 제품 diff 0, exact PackageCache 두 종 각 1개를 확인했다. 전용 AVD 두 개는 과거 시험 데이터가 있는 보존 기기이고 연결 기기/booted simulator는 없다. PostgreSQL은 기존 개발 컨테이너로 원격 runner 격리를 증명하지 않는다. self-hosted는 DEFERRED_ENV다.

- P09-T07 로컬 gate 단위 7건 PASS/skip 0: Unity 미실행·실패/skip, basic 실패, 부분/누락 coverage 거부, 결합 script의 strict 실패 전파, 정상 fixture의 gate 성공을 확인했다. 정상 fixture 성공은 제품/원격 release PASS가 아니다. runtime gate 분리 구현은 이번에 적용하지 않고 판정표·최소 변경안으로만 기록했다.

- P09-T07 readiness DEFERRED_ENV: 전용 runner/label·계정/접근 격리 미준비. 등록·활성화·원격 실행 없음. [사전 점검 evidence](evidence/p09-self-hosted-readiness.md). 기존 P05 FAIL/OPEN 및 Provider 대기 유지.

- P09-T07 커밋 전 원장·diff PASS. 현행 gate 단위 보강과 CI 문서·사전 점검 evidence만 stage한다. runtime workflow/script, runner 등록·변수·원격 실행 상태는 변경하지 않았다.

- P09-T07 커밋 전 staged gitleaks exit 0·탐지 0건. 검토 문서·현행 gate 단위 보강만 커밋한다.

- P09-T07 CI 모드 분리 시작: PR/기본 dispatch는 hosted 결과만, 명시 release 요청에만 Unity·release gate를 조건부 실행한다. 기존 Strict 결합·실패 전파와 coverage 검사는 유지한다.

- P09-T07 로컬 검증: 기존 gate 7건 및 workflow 모드 정적 단위 2건 PASS/skip 0, 원장·diff PASS. GitHub 원격 조회와 actionlint가 응답하지 않아 중단했으며 원격 안전 조건·실행은 아직 확인되지 않았다.

- P09-T07 ロ컬 actionlint 1.7.12(기존 바이너리·custom label 설정) exit 0. GitHub 조회 2종은 각각 12초 timeout으로 원격 SHA·Unity 변수 재확인 불가; 원격 push/dispatch는 미실행으로 유지한다.

- P09-T07 커밋 전: CI 모드·관련 테스트와 정제 문서만 stage한다. GitHub 연결 timeout으로 원격 push/dispatch는 미실행이며 재개 조건을 기록했다.

- P09-T07 Hosted-only 검증 시작: 로컬·원격 f8d644e 전체 SHA 일치, repository 변수 API 성공·총 0개로 Unity 변수 미설정 확인. 기존 Push는 완료됐으며 release_validation=false로 dispatch 1회만 요청한다.

- P09-T07 false 입력 dispatch 1회 수락: run 43840984922, 실제 실행 SHA f8d644e83dd8219578c19c4d1330e9846e35a35b 확인. 완료 job 결과는 아직 대기 중이며 자동 재실행하지 않는다.

- P09-T07 hosted-only run 43840984922: inventory-contracts SUCCESS, Unity SKIPPED. Backend·Android·macOS 실행 중이며 Release 최종 상태는 아직 확인 전이다.

- P09-T07 hosted-only run: Backend PostgreSQL·inventory SUCCESS, Android Maven/R8 consumer와 macOS synthetic iOS host 단계는 진행 중이다.

- P09-T07 hosted-only run: Android Native도 SUCCESS. macOS synthetic host test와 basic-ci·release 최종 상태를 기다린다.

- P09-T07 Hosted-only run 43840984922 완료 SUCCESS: inventory·Backend·Android·macOS·basic-ci SUCCESS, unity-e2e·release-readiness SKIPPED. release_validation=false로 단 1회 실행했고 재실행하지 않았다. 기존 P05-T03 FAIL·Provider 대기·P09 PARTIAL 유지.

- P09-T07 커밋 전 원장·diff PASS. Hosted-only 단일 실행의 정제 evidence와 진행 문서 3개만 stage한다. code/workflow·기존 미추적 파일은 변경하지 않았다.

- P09-T07 커밋 전 staged gitleaks exit 0·탐지 0건. 결과 문서만 커밋한다.

- P09 완료 조건 감사 시작: 기준 HEAD/원격 129b1bb 일치. Task 상태 변경 없이 계획·소스·보존 결과 JSON/evidence를 대조한다. 전체 suite나 원격 workflow는 재실행하지 않는다.

- P09 감사 완료: T01/T03/T08 local 충족 근거는 상태 변경 제안만 기록, 전체 원장 PARTIAL 유지. T06 errors 독립 필드 수집/판정 공백, T04 Testcontainers 계획 차이, T07 격리 runner 대기를 확인했다. 다음 한 Task는 T06 errors 보강이며 이번 구현은 하지 않았다. [감사 evidence](evidence/p09-completion-gap-audit.md).

- P09 감사 커밋 전: 감사 문서와 진행 문서 3개만 개별 stage한다. 원장·manifest·링크·diff 정적 검사 통과, Task 상태·코드·workflow 변경 없음.

- P09 감사 커밋 전 staged gitleaks exit 0·탐지 0건. 정제 문서만 커밋한다.

- P09-T06 errors 계약 보강 시작: HEAD/원격 c1c121a. JUnit은 독립 errors를 수집하고 Swift/xcresult 합산 실패 및 marker 검사에는 명시 errorModel을 부여한다. 오류 미측정은 null로 표현하며 근거 없는 누락·잘못된 타입은 PASS를 거부한다.

- P09-T06 오류 계약 단위 9건, 기존 aggregation 14건, self report 2건 PASS/skip 0. 정상/오류·부정 타입/누락·합산 호환·nested JSON/Markdown 및 producer main을 stub 명령으로 확인했으며 실제 제품 suite/Strict/DB/Player/Actions는 실행하지 않았다.

- P09-T06 errors 보강: 관련 단위 25건 PASS, 정상/오류 fixture process exit 0/1, 정적 원장·manifest·actionlint PASS. 전체 Strict·제품 suite·원격 Actions는 미실행, 기존 PARTIAL/FAIL/WAITING_USER 유지. [errors evidence](evidence/p09-errors-contract.md).

- P09-T06 최종 검토에서 nested 합산 실패 필드의 누락도 0으로 메우지 않도록 유지하고 summary의 MISSING/UNMEASURED를 구분했다. 오류 계약 9건 재검증 PASS, 원장·manifest·diff PASS. 커밋 전 관련 집계/producer/단위시험·CI 연결·정제 문서만 stage한다.

- P09-T06 커밋 전 staged gitleaks exit 0·탐지 0건. errors 계약 범위의 변경만 커밋한다.

- P09-T06 측정 계약 시작: 기준 HEAD/원격 6c8af7b 일치. simple 기본 marker를 tests 0/checks 1, stress는 samples, PII 검증은 players로 분리하고 checker의 실제 로그·marker·exit·hash 근거를 요구한다. 이번은 fixture 검사만 수행한다.

- P09-T06 측정 fixture 10건 PASS, 내부 실제 aggregation unittest 14건 실행·건수 확인, 기존 errors 계약 9건 PASS/skip 0. checker marker·exit·로그 누락/변조와 required 누락·skip·errors를 차단했다. Player/스트레스는 fixture뿐이며 실제 제품 실행이 아니다.

- P09-T06 측정 단위: 관련 최상위 단위 35건 PASS/skip 0. checker tests 0/checks 1과 samples·players 분리, static mapping 및 오류 차단 유지. 전체 Strict·실 제품 실행 없음. [측정 evidence](evidence/p09-measurement-contract.md).

- P09-T06 커밋 전 원장·manifest·diff PASS. simple 측정/근거 계약·관련 단위와 CI 연결·정제 문서만 개별 stage하며 과거 보고서나 제품 코드는 수정하지 않는다.

- P09-T06 커밋 전 staged gitleaks exit 0·탐지 0건. 측정 계약 범위의 코드·정제 문서만 커밋한다.

- P09-T06 배치24 작업 A 시작: HEAD 8eec64a 기준 nested producer 단위 보존과 자체시험 checker 계약을 구현한다. 작업 B에서 실행 근거 연결·fail-closed를 보강하고 C/D 실제 통합·원격 검증까지 연속 수행한다. 기존 P05-T03 FAIL/ENV-STOREKIT-26 OPEN/Provider WAITING_USER, 사용자 미추적 자료를 보존한다.

- 배치24 A 검증 1: 계약·측정 단위 19건 중 기존 stub fixture 3건 FAIL(exit 1). 실행 로그를 만들지 않던 fixture가 새 근거 필수 조건에 걸렸다. fixture에 관측 명령·로그를 명시하고 자체시험 fixture도 checker 계약으로 갱신한다. 실제 제품 검증 실패는 아니다.

- 배치24 A 검증/커밋 전: 계약·측정 19건, nested 단위 4건, self-report 2건 PASS(skip 0), 원장·manifest·diff exit 0. 최초 stub 3건 실패는 실제 로그를 생성하는 fixture로 수정했다. C#·패키징·marker는 tests 0/checks, Unity push는 players 2, 상위 nested는 모든 측정 필드와 누락을 보존한다. 자체시험의 checks→tests 치환을 제거했다. 통합 제품 실행은 C에서 수행한다.

- 배치24 작업 B 시작: A commit 2af4d7a. 같은 SHA의 과거 로그 재사용, 임의 경로/부모·자식 종료 불일치/누락·중복·부정 타입을 차단하기 위해 실행 ID·실제 관측 시간·소스 내용 digest와 부모 호출에 묶인 receipt를 적용한다.

- 배치24 B 검증 1: 기존 계약·측정 19건 중 3건 FAIL. 오류 기본 fixture와 집계 unittest가 측정 필드 없는 과거 형식을 사용했다. 누락 허용으로 되돌리지 않고, 정상 fixture만 현재 실행 receipt·명시 단위를 갖추도록 수정한다. zero/누락 fixture는 계속 거부한다.

- 배치24 B 전체 단위 1차: 112건 실행 중 failure 1(이전 Markdown errorModel 기대값), error 1(시스템 Python에 jsonschema 미설치), exit 1. 기대값을 실제 separate 표시에 맞추고 기존 schema venv로 전체 단위를 재실행한다. 새 collector 경계 11건은 PASS이며 종료 0/1/2 subprocess를 확인했다.

- 배치24 B 검증/커밋 전: schema venv 전체 113건 PASS(exit 0/skip 0); 추가 양수 count 변조 방어를 포함한 collector 12건 재검증 PASS. sourceHead+tracked diff digest, 관측 registry/명령/실행 ID/시간/로그 hash와 부모의 실제 stdout→새 report→자식 receipt를 연결했다. 단위 누락·0건·부정 타입·오류·중복·skip 승격·부모 종료 불일치·동일 SHA 과거 report 재사용을 거부한다. classifier를 실제 subprocess에서 실행하여 exit 0/1/2 확인. 원장·manifest·actionlint·diff PASS. 새 unit 2종을 Hosted inventory에 연결했다.

- 배치24 작업 C 시작: B source commit 확정 후 전체 Python·정적 검증→격리 PostgreSQL 자체시험 9 lane→ci-unity-e2e.sh 경로의 현재 Player/Strict 1회를 실행한다. Unity license active, staging 147 checksum PASS, exact PackageCache 존재. 사용자 연결 AVD 4개·기존 booted iOS 기기는 보존하며 별도 GameBridge 전용 AVD 2개만 사용한다.

- 배치24 C 1차 검증/Strict 전 커밋: 전체 Python 114건 PASS(exit 0/skip 0), 원장·manifest·Unity meta·API baseline·actionlint·diff exit 0. 격리 self-check source 94dad65 + 진행 문서 변경에서 9/9 PASS, 실제 tests 47(정상 44/예상 실패 3), checks 9, samples/players 0. sandbox 지정 testcase JUnit 1건 401 거부 확인. artifacts/harness-self-cvmhknn5 및 strict-isolated-pf5d4dpu. DB·role·Simulator 보존. 이어서 이 기록을 커밋해 tracked-clean source에서 ci-unity-e2e.sh 전체 Player/Strict 1회를 실행한다.

- 배치24 C 환경 블로커: ci-unity-e2e.sh exit 2. source a6a14da tracked-clean에서 Editor 2건·sample 1건/reimport·Android/iOS hook PASS 후 기존 PII AVD의 TEST_APP_ALREADY_INSTALLED_PRESERVE_EXISTING으로 설치 차단. artifacts/unity-android-e2e-jefckpl8 및 unity-pii-current-ocq0awkp. Player/Strict NOT_RUN, 과거 증거 재사용 없음. 기존 앱·AVD를 보존하고 새 전용 AVD 2개로 환경을 준비한다. 전체 Strict 실행은 아직 0회다.

- 배치24 C 환경 기록 커밋 전: 차단된 AVD·앱은 보존하며 원본 로그나 빌드는 stage하지 않는다. 다음 실행 source를 문서 커밋으로 확정한다.

- 배치24 C Strict 완료: source 0b6fb7250e6f9edb2c93ba477ac06a5060b1769a, ci-unity-e2e.sh/Strict exit 1. artifacts/verify-all-5ffhc5v8: 57 lane 중 52 PASS, 4 FAIL, 1 DEFERRED_ENV. 기존 P05 기록 FAIL 외 새 StoreKit DB timeout(124), process prepare/store-history timeout, Android Unity Push READY timeout(따라서 iOS Push 미실행), Editor runtime 환경 대기. 자체시험 9/9·PII 양 Player·합성 회귀는 통과. 검증 완료 전 source 고정을 위해 runtime checkpoint에 즉시 보존했던 실패를 이제 정식 원장에 반영한다. 새 실패를 알려진 P05만의 실패로 기록하지 않는다. 원본 실패 유지 후 영향 lane만 조사/재실행한다.

- 배치24 C 원인 관측: Android Push 실패 AVD UIAutomator에서 systemui Viewing full screen/Got it 안내를 확인했다(READY 이전 차단). 기존 APK·AVD 보존 후 새 전용 AVD에서 안내를 관측·닫고 해당 Player gate만 재실행한다. Editor CLI 원본은 300초 process timeout/CLI exit 6이며 test verdict 없음. StoreKit DB xcresult는 Info.plist 미완결, process recovery는 Transaction history 진입 후 timeout이다. 원인 확정 없이 runtime FAIL을 환경 PASS로 바꾸지 않는다. 현재 실행 완료로 source 고정 해제, 관련 진단 로그 보강과 영향 lane만 재검증한다.

- 배치24 C 결과 커밋 전: 실제 실패·대기와 52 보고 PASS를 정제 문서에 기록했다. 전체 Strict 재실행은 하지 않고 원본 실패를 보존한 채 관련 진단/재검증으로 이동한다.

- 배치24 B/C 영향 보강 시작: 전체 실행의 source를 보존한 뒤 timeout 부분 로그 폐기·history 단계 미분리 진단 공백을 보강한다. 추가 검토에서 미정 errorModel 및 호출 후 command 리스트 변경에 대한 방어도 음성 fixture로 확인하고 같은 배치에서 수정한다. StoreKit/Editor/Push 원본 실패는 유지하며 전체 Strict는 반복하지 않는다.

- 배치24 후속 음성 재현: 실제 collector 단위 3건 모두 기대와 달리 FAIL(exit 1)—unknown errorModel 수락, 호출 후 mutable command 리스트 변경 수락, 실제 subprocess timeout의 부분 stdout 폐기를 확인했다. 세 공백을 수정한 뒤 재검증하며 제품 테스트 통과로 기록하지 않는다.

- 배치24 후속 검증/커밋 전: 정상 오류 모델 3종만 허용, 관측 command snapshot deep copy, timeout 부분 stdout 보존(부분 PASS marker로 승격 불가), Markdown 누락/실패/exit/단위 표시를 보강했다. RecoveryHarness history all/unfinished checkpoint만 분리(제품 SDK 의미 변경 없음). 전체 Python 117건 PASS/skip 0, timeout 실제 프로세스 1건 재확인 PASS. 원장·manifest·actionlint·diff exit 0. 현재 실패 lane만 확정 source에서 재실행한다.

- 배치24 C 영향 재검증 1: source 4508b9a에서 단독 bash scripts/build-unity.sh --editor-smoke exit 0, 실제 Editor tests 2 PASS(artifacts/unity-consumer.nsFJLu). 최초 Strict의 CLI 300초 timeout/DEFERRED는 그대로 보존하며 현재 재검증 성공을 별도 기록한다. StoreKit retry는 timeout 로그·고정 stage marker를 보강하고 새 격리 DB/Simulator에서 각 1회만 실행한다.

- 배치24 진단 커밋 전: source4508 Editor 재검증 PASS를 기록하고 test-only stage 로그를 추가했다. Swift parse 확인 후 커밋하며 StoreKit 실제 재검증은 아직 NOT_RUN이다.

- 배치24 C 영향 재검증 2: source 4b23529의 StoreKit DB wrapper 단독 retry exit 0, 실제 XCTest 1 PASS/skip 0/testExitCode 0/timedOut false(artifacts/xcode-storekit-e2e-zk9hcbqp). SDK 동작·timeout 변경 없이 통과했지만 최초 180초 실패 원인은 미확정/간헐 관측으로 남긴다. 최초 Strict 결과는 수정하지 않는다. 완료된 이번 전용 Simulator를 shutdown 후 process recovery만 재실행한다.

- 배치24 C 영향 재검증 3: source 4b23529 + 진행 문서 변경(코드 동일)에서 process recovery exit 0(artifacts/xcode-process-recovery-r2r9s3db). prepare/recover balance 100, 서로 다른 PID로 실제 프로세스 종료·재실행 복구 확인. StoreKit 두 lane 및 Editor는 단독 재검증 PASS지만 최초 Strict 실패·간헐 원인 미확정을 보존한다. 현재 문서 commit 후 fresh Push AVD5570에서 UI 안내를 관측·닫는 보조와 함께 양 Player gate만 재실행한다.

- 배치24 StoreKit 재검증 기록 커밋 전: 두 영향 검증 PASS와 최초 FAIL/원인 미확정을 함께 기록했다. 다음 Push Player는 이 문서 커밋의 tracked-clean source에서 새로 실행한다.

- 배치24 C Push 재개 환경 차단: 예정 serial5570 조회가 Pomodoro_QA_33을 반환해 보조 실행이 Wrong dedicated AVD/exit 1로 즉시 중단됐다. UI/설치/네트워크 명령은 수행하지 않았다. GameBridge retry AVD는 현재 online 목록에 없어 원인 미확정으로 기록한다. serial 소유를 가정하지 않고 각 기기 명령 직전 identity 재확인과 cleanup 보호를 보강한 뒤 비어 있는 전용 포트에서 실행한다.

- 배치24 기기 소유 보호 검증/커밋 전: 전체 Python 119건 PASS/skip 0. serial 재배정·비전용 이름·serial 없는 명령을 검사해 기기 조작 전 차단한다. network cleanup도 다른 AVD에는 보내지 않으며 기존 FAIL을 DEFERRED로 덮지 않는다. retry AVD PID는 살아 있었으나 예상 ADB serial과 연결되지 않았고 같은 serial은 타 AVD를 반환했다. 원인은 미확정; 검증한 자기 PID만 종료·디스크 보존. Android Push 재검증은 ENV-P09-AVD/DEFERRED_ENV로 남기고 독립 iOS Push를 실행한다. 다른 기기·ADB server를 종료/재설정하지 않는다.

- 배치24 C 완료(부분)/D 시작: source 5eaf31f59f0d187a24bffb5007543744359ca076에서 전체 Python 119 PASS/skip 0, self-check 9/9 PASS/exit 0(whqw6w9q, tests47/예상실패3/checks9), 독립 iOS Unity Push PASS/exit 0(5wsdfn1e, tracked-clean/rejectedReconnect6/deviceTokens0). Android Push 재검증 ENV-P09-AVD 대기, 원래 Strict 52PASS/4FAIL/1대기/exit1 및 P05 FAIL 보존. D는 Hosted unit 연결/false·Unity비활성 조건을 유지하고 관련 commit scan→handoff FF push→Hosted-only dispatch 1회→최종 감사 기록을 수행한다.

- 배치24 C/D 준비 커밋 전: source별 실제 결과와 T01/T03/T06/T08 local 변경 근거를 감사에 기록했다. 원장 일괄 PASS 변경 없음. 다음은 code 변경 없이 scan/FF push/Hosted-only 1회다.

- 배치24 D push 전/커밋 전: 원격 CodingBot000/GameBridge_SDK(public), local fix/unity-android-mock-e2e-evidence/upstream origin/fix 확인. handoff 원격 8eec64a→local6313963 10 commit 조상/FF 확인. gitleaks 전 범위 exit0/탐지0, 31경로에 금지 파일·raw log·서명/실키·cache·binary 없음. 이 기록은 별도 docs commit으로 추가·staged scan 후 HEAD:handoff 정상 push한다. Unity 변수 총0, false 입력 dispatch 1회만 허용된 범위다. 자동 재실행·main·force·Release 없음.

- 배치24 D push 성공: 로컬/원격 handoff HEAD 8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18 일치. FF push만 수행했다. repository 변수 재조회 총0(활성 Unity 변수 없음). 지금 해당 SHA의 release_validation=false Hosted-only dispatch 1회 요청하며 완료 전 PASS로 기록하지 않는다.

- 배치24 D dispatch 1회 수락: run 43862394352, 실제 source 8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18, release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43862394352 . 실행 완료 전이며 자동 재실행하지 않는다.

- 배치24 D 원격 중간 결과: run43862394352 source8c8fc62에서 inventory-contracts SUCCESS, backend-postgres SUCCESS, unity-e2e SKIPPED. Android/macOS는 진행 중, basic/release는 아직 최종 미확인이다. 원격 전체 PASS로 기록하지 않는다.

- 배치24 D 원격 검증: inventory 실제 unittest 32 suite/113건 PASS(FAILED 요약0), Backend·Android job SUCCESS, Unity SKIPPED. 로컬119와 원격113은 scope가 다르며 기존 CI 미연결4파일6건은 로컬에서만 실행했다. 이번 변경 단위는 모두 Hosted에 연결됐다. macOS synthetic host와 basic/release 최종 결과를 기다린다.

- 배치24 D 완료: run43862394352 source8c8fc627858c098b68c7cedcd0f2dacbcf4b8c18 workflow_dispatch(false) 전체 SUCCESS. inventory/Backend/Android/macOS/basic-ci 5 SUCCESS, Unity/Release 2 SKIPPED. 원격 unit32suite113 PASS, BackendJUnit13, Android45+1+1, SwiftXCTest17, synthetic host는 >0·실패/skip0 검사 통과(정확건수 미출력). 자동 재실행 없음. 로컬119/self9/iOSPush와 구분한다. Android Push ENV-P09-AVD, 최초Strict FAIL, P05 FAIL/ENV26 OPEN/Provider WAITING_USER/self-hosted 미검증 유지. 최종 docs scan·commit·FF push·HEAD 대조만 남았다.

- 배치24 최종 커밋 전: Hosted7개job 최종 상태와 source별 검증·남은 환경/내부 항목을 정제 evidence에 기록했다. 추가 코드 변경·원격 재실행 없음. 최종 문서만 stage/scan/FF push하고 local/remote HEAD 및 기존 미추적3개 디렉터리를 확인한다.

- 배치25 A 시작: 기준 f6915e35f28e06a0d88e053a66883505bc7bc881 및 기존 미추적3개 디렉터리 확인. ENV-P09-AVD의 serial/이름/PID/실제 listen port를 읽기 전용 대조하며 타 AVD·앱·기기/ADB server kill·restart·초기화는 하지 않는다. 첫 adb devices 조회에서 daemon 부재로 CLI가 자동 시작을 출력했고 이후 명시적 server 조작은 하지 않는다. A 독립 PASS/환경 준비 없이는 C 전체 Strict를 실행하지 않는다. B/C/D를 순차 수행하고 최종 통합 보고한다.

- 배치25 A 검증: PID/console·ADB port 양쪽 소유, 요청 이름·port 불일치/PID 재사용/반쪽 연결/다중 owner 거부, 기존 기기 guard 및 CI gate 15건 PASS(exit0/skip0). 현재 타 AVD의 요청5560과 실제5560/5561 owner PID89772 일치를 읽기 전용 확인했다. 배치24는 요청5570·자기 PID가 있어도 실제 console/ADB listen이 없고 serial이 타 AVD에 연결됐던 관측이다. 포트 소유 불일치는 확인됐지만 최초 경쟁/실패 시점은 보존 증거가 없어 확정하지 않는다. 새 guard는 예상 PID와 실제 두 port 소유를 매 명령 전 요구한다.

- 배치25 A 실행 준비 커밋 전: 관련 단위16건 PASS/skip0, progress/manifest/diff exit0. 예상 PID 및 실제 console·ADB 소유 증거 요구를 추가했다. 새 전용 AVD 생성/실제 Push는 아직 NOT_RUN이며 tracked-clean commit 후 준비한다. 기존 실제 사용자 AVD·앱·ADB server는 변경하지 않는다.

- 배치25 A 검증/커밋 전: source b55ffe722cfd9bd2663cd3e193343cebb0b4c202 tracked-clean의 Android Unity LOCAL_MOCK Push exit0/PASS(artifacts/unity-android-push-l_yu9kmb). PID22235가5582/5583 양 port 소유, serial·AVD명 일치. 필수7 marker·수신/중복/main-thread/background/실제 emulator망 차단·재연결/session/token삭제0 확인. 초기 systemui 전체화면 안내를 관측해 Got it1회 클릭(UI 보조, 무인CI 아님). 새 자기 emulator만 종료·디스크 보존, 기존 AVD/ADB server조작 없음. ENV-P09-AVD는 이 local 검증에서 RESOLVED. B로 이동하며 C Strict는 새 전용전체환경 준비 후 최대1회다.

- 배치25 B 시작: 배치24 StoreKit18.6 최초 실패/단독 retry 성공의 source·checkpoint·XCTest/Simulator/Backend/timeout를 대조한다. 원인 미확정 위험을 유지하고 26.5 재실행·timeout 증가는 하지 않는다. Testcontainers 요구와 현재 별도PostgreSQL 격리의 차이를 코드·실행 증거로 판단해 처리 방향을 정한다.

- 배치25 B 검증/방향 결정: StoreKit 최초 두 실패와 단독성공은 SDK runtime diff없음, 동일180초(DB)·75초(phase) 제한. 실패 DB 둘 모두 sessions1/purchases0/ledger0, 성공 둘은 purchases1/ledger1/delta100. DB recovery 최초부분stdout폐기·xcresult미완결 및 당시bootstate미보존으로 정확정지위치미확정, process는history진입후timeout. 두원인을합치거나후속PASS로간헐위험을해소처리하지 않는다. 현재 Docker PostgreSQL은 기능·fresh schema 불변식은 증명하나 Testcontainers 수명관리 literal요구는 충족하지 않는다. 기존fixture/보호를 유지한 Testcontainers2.0.5 별도opt-in 실행경로를 최소 보강해 실제 검증한다. 신규container만 시작/정리하고 기존개발DB는 변경하지 않는다.

- 배치25 B Testcontainers 최초 검증 exit1/0 tests: Gradle init script의 nullable labels map 접근이 Kotlin compile에서 거부됐다. container 시작 전 실패라 기존DB/기기 영향 없음. safe nullable lookup으로 수정 후 같은 경로를 재검증한다. 미구현/미실행을 PASS로 기록하지 않는다.

- 배치25 B Testcontainers 2차: 새 loopback container 실제 시작/owned cleanup 확인, 기존 local7건 중5 PASS/2 FAIL(exit1). 두 Finalization 시험은 기존public schema의 users/products를 사용하므로 marker만 초기화한 TC bootstrap이 불충분했다. 원장조건을 바꾸지 않고 프로젝트와 동일 Flyway migration+mock catalog 전체를 새container에 적용해 보강한다. 기존DB/시험assertion 변경 없음.

- 배치25 B 3차: Testcontainers local7건은 실제모두PASS/Gradle0, 전체Flyway bootstrap도성공했다. wrapper는 cleanup확인실패로전체FAIL1을 반환했다. 실제 Docker inspect1 stderr가 소문자 no such object였고 새container삭제는확인됐다. 알려진not-found만대소문자정규화로판정하고 permission/daemon오류는거부하는단위검사후전체4case검증한다. 원본FAIL보고서는수정하지않는다.

- 배치25 B 검증/커밋 전: Testcontainers2.0.5/PG17.6 신규loopback container4개에서 기존fixture11건 실행(정상10+의도된원장변이failure1), case Gradle exit0/1/0/0, wrapper exit0. 네container 실제시작·label·loopback owner·stop/삭제확인. 변이는기존named invariant assertion과일치하고정상복원1건도검사했다. bootstrap/cleanup파서초기실패원본보존. 새계약단위5건PASS, JDBC42.7.11/Flyway11.7.2는프로젝트기존해결버전고정. 기존devDB·assertion·timeout변경없음. source9c94234+구현중harness로실행했으며C에서commit된현재소스로다시검증한다. StoreKit18.6 간헐위험원인미확정유지.

- 배치25 C 시작: 기존CI미연결4파일6건과새binding/TC계약단위를Hosted에연결하고측정/오류/집계회귀·새격리self9를검증한다. TC11건은예상실패1과검사4를보존해별도Strict lane에연결한다. A currentAndroid PushPASS 확보, C용새PII/Push전용AVD와실제PIDport소유를준비한경우에만commit후ci-unity-e2e.sh 전체Strict최대1회실행한다.

- 배치25 C 검증/실행준비 커밋 전: 전체 Python131건PASS/skip0(38파일),기존미연결4파일6건은순수fixture/XML/파일복사검사로Linux Hosted적합하여모두연결. 신규binding/TC단위도연결하고backend Hosted에실제TC4case경로추가. actionlint/progress/manifest/diff exit0. TC는별도required Strict lane(tests11/expectedFailures1/outerchecks1/childChecks4)으로분리한다. self-only는사용하지않는iOSproject/Simulator생성을생략한다. currentcommit에서새전용DB self9 및TC 경로부터확인후C전체AVD준비조건을판단한다.

- 배치25 C 실제검증/Strict전 커밋: source43d255a39f9efd28e630fad40889cec9d255365d에서 self9/9 PASS(exit0, tests47/예상failure3/checks9; harness-self-rl7_n0r_) 및TC4case11test/예상failure1 PASS(exit0; purchase-testcontainers-86d9mge4). self-only 불필요Simulator 생성없음. Unity active/staging147 PASS. C새PIO5578/PID36894 및Push5580/PID36901 각각이console+ADB양port소유·AVD이름·boot완료일치. A독립PASS와C전용환경이확인돼 이문서commit후tracked-clean source에서ci-unity-e2e.sh 전체경로1회만 실행한다. 기존P05FAIL은유지한다.

- 배치25 C 검증/커밋 전: source e46cb6520272334d9816d951274b91bd39133b9b tracked-clean의ci-unity-e2e.sh/전체Strict1회실행완료. verify-all-q_sj2gpu:58lane/57PASS/기존P05기록FAIL1/신규FAIL0/대기0,exit1. tests226(예상negative4포함),checks57(고유56,TC내부4별도),samples100,Players4. self9·TC11·StoreKit18.6두복구·Android/iOS현재Push·PII·Editor통과. AndroidPush PID36901/양port소유확인,reconnect2; iOS reconnect6/LOCAL_TRANSPORT_FAULT,각deviceTokens0. PII양원장1/delta100. C UI안내각1회관측클릭,무인CI검증은별도. 모든생성기기/DB/로그보존,완료된이번전용process만종료. 최초배치24간헐위험/P05FAIL/Provider13대기는제거하지않는다.

- 배치25 D 시작: A~C 현재증거로P09-T01~T08의명시완료조건을개별판단한다. P05 FAIL/26OPEN/실Provider13WAIT/self-hosted·Release미검증은분리유지. 근거있는로컬상태만변경하고table에서집계를재계산·원장/음성검사통과후scan/FF push/false Hosted-only1회를수행한다.

- 배치25 D 원장 편집1차는 blocker ID가 Task셀에참조된것을중복행으로오인한assert에서exit1,파일쓰기전에중단됐다. 원장상태/집계는갱신되지않았음을확인했고행시작조건으로수정해다시검증한다. 제품/하네스검증실패가아니다.

- 배치25 D 개별 상태 반영: T01/T03/T05/T06/T08 local 완료 조건을 실제 증거로 충족해 IMPLEMENTED/PASS. T02 assert총수 미측정으로 IN_PROGRESS/PARTIAL, T04 TC구현 완료·18.6 간헐 원인 미확정으로 IMPLEMENTED/PARTIAL, T07 Hosted/설정 구현 완료·self-hosted/Release 미검증으로 IMPLEMENTED/PARTIAL. 집계는64개 원장행에서 재계산했고 외부13 WAITING_USER·P05 FAIL은 유지했다.

- 배치25 D 감사 커밋 전: 계획과source별실제증거를대조해5개localPASS·3개PARTIAL을반영했고원장/음성/manifest/diff통과. TCgap/미연결unit/현재AVD대기는해소,간헐원인/actual assert/self-hosted는남김. 원래StrictFAIL및26.5/실Provider대기보존. 다음은범위·비밀정보검사후handoff FF push/false Hosted1회다.

- 배치25 D push 전/커밋 전: CodingBot000/GameBridge_SDK public 확인, handoff 원격 f6915e3이local2b2b6b7의조상으로FF가능. 신규7commit/21text path의gitleaks exit0·탐지0,금지키/서명/원본로그/cache/빌드/binary delta없음. 이기록만추가scan·commit후명시handoff FF push한다. repo변수0/runner0,변경된Hosted를false입력1회실행하고self-hosted/Release는비활성으로유지한다.

- 배치25 D FF push 성공: local/remote handoff HEAD59b98349689171cc8a75d9652f248708645a85c2 일치. repo변수재조회0,code/Hosted연결변경이있어 release_validation=false dispatch1회만지금요청한다. 진행중결과를PASS로기록하지않는다. self-hosted/Release는비활성유지한다.

- 배치25 D dispatch1회수락: run43889958441,source59b98349689171cc8a75d9652f248708645a85c2,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43889958441 . 현재in_progress이며job최종확인전PASS로기록하지않는다. 원격재실행은하지않는다.

- 배치25 D 원격중간검증: source59b9834 run43889958441 inventory38suite/131건PASS/FAILED요약0,Backend(TC포함)·Android jobSUCCESS,UnitySKIPPED. 기존미연결6건도원격실행범위에포함됐다. macOS synthetic host및basic/Release 최종상태는아직대기하며전체SUCCESS로기록하지않는다.

- 배치25 D 최종검증: run43889958441 source59b98349689171cc8a75d9652f248708645a85c2 전체SUCCESS. inventory/Backend/Android/macOS/basic-ci 5SUCCESS,Unity/Release 2SKIPPED. 원격38suite/131unit PASS,backend기존JUnit13+TC11(예상failure1,정확변이/정상복원),Swift17및synthetic Host검사통과. false dispatch1회만수행·재실행없음. 이후최종문서만commit/scan/FF push하고Head일치를확인한다.

- 배치25 최종 커밋 전: 원격7job 최종결과와local5PASS/3PARTIAL·source별actual counts·잔여작업을확정했다. 최종문서만scan/commit/FF push하고HEAD와미추적3개디렉터리보존을대조한다. 추가코드/원격재실행없음.

- 배치26 A 시작: 기준6d200b064b5cd8ea5ebca76bf3b58c1bd0086e6d/추적변경없음/기존미추적Demo·cache보존. 명시작업브랜치 handoff/p09-resume-20261113을같은HEAD에서생성해전환했다(main/fix이력변경없음). R01~R12의실행test/actualassertion/static선언을구분하는test-only계측과mutation복원기준을확보한다. 이후B18.6제한진단/C실질CoreBridge분리/D통합·Hosted1회까지진행한다. P05FAIL/26OPEN/Provider13WAIT/self-hosted미검증유지.

- 배치26 A 초기검증: Kotlin선택10 test PASS/실행helper50,Swift12 PASS/helper122,C#managed smoke0 tests/check1/helper391 확인. 기본framework건수와assertions실행을구분했다. Xcode spec경로첫참조오류는실제ios/Framework/project.yml로정정해test-only helper를CBridge target에도포함했다. 분기없는valid parse testcase의helper0은0 tests라는뜻이아니며implicit throw/check는별도UNMEASURED다. shipping API/runtime변경은아직없다.

- 배치26 A 계측초기통합 exit0: Kotlin10/50,Swift12/122,managedcheck1/391,stress100sample의helper316(warmup15/sample300/final1),정상복원391 확인. Mutation partial helper1에서unknown request-ID guard가duplicate보다먼저실패했음을trace로발견했다. 기존감지의민감도는유효하지만duplicate 전용 probe로정상0/변이nonzero를확인하도록범위를정확히보강한다. 정적호출수/manifest항목수는실행수로대체하지않는다.

- 배치26 A 계측 준비 커밋 전: 실제Kotlin10/50·Swift12/122·managed391·stress316·Unity2/32 확인,전체Python136 PASS/skip0,APIbaseline/progress/manifest/diff통과. 동적helper호출/정상·예상오류/partial변이/정적선언·미측정범위구분. duplicate-only 정상0/변이nonzero와원본hash복원 검증을보강했다. 현재shipping runtime은6d와동일. commit후동일cohort/조건분기control로A최종baseline을확정한다.

- 배치26 A 검증/커밋 전: commit b6fd5379c8ec31b110904754e744325bd39d61c9 tracked-clean baseline core-assertions-2u0cmwrq PASS/exit0. Kotlin10test/helper50,Swift12/122,managedcheck1/391,원본복원391,분기control OFF0/ON1로392,stress316(15/300/1),Unity2/32. duplicate-only정상probe0/helper2,변이nonzero/partialhelper1·NullReference의정확한duplicate단계감지·원본hash동일확인. R01~R12 shared-test/label attribution과JNI Player/implicit signals/전체assertoutcomes UNMEASURED를명시했다. 정적manifest목록은숫자실행으로합산하지않는다. 최종P09T02판정은D의실제영향검증과함께검토한다. B제한진단으로이동.

- 배치26 B 시작: 배치24최초18.6실패/24retry/25통합성공을source/configuration/Xcode/boot/health/순서/checkpoint와대조한다. 필요한test-only관측만추가하고SDK구매·지급·finish/recovery는변경하지않는다. 구분가능한controlled가설각1회범위,기존timeout유지·26.5재조사없음. 미재현이면미확정위험으로종료하고C실질리팩토링을계속한다.

- 배치26 B 진단 준비 검증/커밋 전: read-only toolchain Xcode26.6/17F113 확인,0b6fb72·4b23529·e46cb65의GameBridge.storekit SHA동일. 최초failures의버전/boot/부분로그누락한계유지. test-only monotonic API전후trace/XCTest attachment/config SHA/health·boot·test단계관측추가,Python진단단위3 PASS/Swiftparse0. --diagnose는새owned18.6를따로boot관측하고nonparallel·전용DerivedData로각영향경로1회만검증한다. test180/phase75제한및SDK구매·지급·finish/recovery동작은변경하지않는다.

- 배치26 B controlled DB 경로1회: source5bca33f의새owned18.6/nonparallel/별도DerivedData,실제XCTest1PASS/skip0/exit0(artifacts/xcode-storekit-e2e-s3e8c47b). Xcode26.6/17F113,source configurationSHA확인. 첫built-app경로검색은0개로built일치는아직미검증이며아래추가확인으로정정한다. backend-ready8.75s,boot-ready30.92s,teststart32.22s/return67.96s를단조시계로관측했다. 기존180초제한그대로며최초간헐원인은재현되지않아미확정유지. 다음process경로도fresh환경1회만관측한다.

- 배치26 B 제한진단종료/커밋 전: source5bca33f(후속진행문서변경외코드동일) controlled18.6 DB1회XCTest1PASS/exit0,process1회재시작PASS/exit0. 실제built config는.app/PlugIns/시험bundle에있어첫root-app검색0개를정정했고확인SHA4ead4675...로기존과동일. XCTest15단계attachment수집(최초start약5.94s/purchase1.39s/recover1.09s),processTransaction.all prepare3.93s/recover0.92s,unfinished0.18s/0.005s 관측. 최초timeout재현없음·원인미확정위험유지,추가반복종료. 새owned기기process만종료/디스크DB보존. P09T04 PARTIAL/26.5미조사/P05FAIL유지. C반드시계속한다.

- 배치26 C/P10-T01 시작: P09T08 localPASS에의존조건충족;self-hosted대기는중단사유아님. shippingKotlin/SwiftCoordinator는플랫폼고유동시성으로유지하고C#RequestRegistry의3중event공통header검증과Finish/finally의동일소유removal중복을선정했다. publicAPI·Native소스/CABI/wire기준을기록하고,변경전동일cohort+추가eventheader negative matrix를실행한뒤책임경계별작게refactor/검증/commit한다.

- 배치26 C baseline: shipping 변경 전 3종 event×7 invalid header 및 정상 callback matrix를 추가해 managed418 helper/exit0 확인. API snapshot 첫 시도는 기존에 없는 contracts/openapi.yaml 참조로exit1/쓰기없음, 실제 존재하는 wire·public-api와Native shipping hash/C ABI exports/C#선언을기록했다. OpenAPI 부재는UNMEASURED로표시하며전체binary ABI검증으로주장하지않는다. 변경전baseline검사PASS.

- 배치26 C1 검증/커밋 전: RequestRegistry의3중event session/id/time/payload header검증을private TryReadEventEnvelope로집중하고kind별body/disposed/callback전달은유지했다. 변경전/후같은managed matrix+race cohort actualhelper418=198normal+220expected,process0동일. 기존API baseline및새79파일Native/C#선언/C-export/wire scope baselinePASS. 공개/internal호출표면변경없음;단순공통추상화가아닌동일검증3곳→1곳. public/wire/source/export변경음성단위3PASS. Kotlin/Swift coordinator는각각Mutex/actor·generation고유상태소유로이영역형식통일이득낮아이번수정제외했다.

- 배치26 C2 검증/커밋 전: RequestRegistry Finish/finally의동일pending-entry reference확인+remove를private RemoveOwned로모았다. lookup/remove 및필요한ignored계수는같은gate안,Completion通知는기존대로밖. finally중복정리는ignored를추가하지않고Dispose clear/abandon순서및cancellation/timeouterror선택은유지. 같은matrix+100racecohort418=198normal+220expected/exit0,duplicate-only정상0/변이nonzero감지,API/source/wire검사PASS. 공개/Internal/C ABI변경없음. 실제새빌드/플랫폼·최종회귀는D에서검증한다.

- 배치26 D 시작: 현재변경의전체Python·Kotlin/SwiftCoreBridge·managed/stress/mutation·API/ABI/contract·self9·원장검사를통합하고현재source에서Native패키지/UPMstaging을새로생성한다. old변경전staging을현재C#runtime증거로쓰지않는다. 소유입증전용기기에서실제Native/Unity LOCAL_MOCK와조건부Strict최대1회,모두commit후falseHosted1회를검증한다. P09T04/P09T07PARTIAL/P05FAIL/Provider대기유지.

- 배치26 D 준비검증/커밋 전: 전체Python143건PASS/skip0(신규assert계약/진단/surface/staging단위),API/source/wire·progress·actionlint/diff통과. build-unity consumer에도current checkout source검사를추가해old147-checksum-valid staging을실제exit1로거부(현재runtime를old로검증하지않음). 새단위4파일을Hosted연결했다. 현재codecommit뒤Native/Maven/XCFramework/UPM을새경로로재생성하고currentSource/hash/ABI를검증한다.

- 배치26 D 실제검증/플랫폼준비: commitdc45a2f tracked-clean에서새Maven+Android/R8 build0,Xcodedevice/simulatorarchive+XCFramework0,새UPM147checksum0. Native javap3종class publicsurface와GB_*4개export(2slice)모두변경전동일. shipping79파일/currentstage hash 기록. current post-refactor ledger core-assertions-zn69jotl exit0: Kotlin10/50,Swift12/122,managed418=198+220,restore418,branch419(OFF0/ON1),stress316,Unity2/32,duplicate정상0/변이nonzero/원본hash동일. 변화전cohort391에header matrix27을추가한418이며전후동일matrix418비교. 추가Native/actualJNI·self9·조건부Strict를이어서검증한다.

- 배치26 D 실행소스확정 커밋 전: Native추가sdk-unity-bridge JUnit1/실패skip0도current code에서통과. 새Maven/XCFramework/UPM checksum·javap/nm ABI표면·postassert ledger·old-stage 거부증거를보존했다. 다음source에서freshDB self9,전용R09 JNI/C ABI및현재Unity실행/조건부Strict1회만수행한다. oldstaging은사용하지않는다.


- 배치26 D 환경 블로커/검증: source d86ccc23ceb14dc6a81d93c2317de0c78f5d708e의 fresh self9는 tests47(예상negative3)/checks9/exit0, harness-self-5b5bz9vm PASS. 현재 R09 Android Player 빌드는 CLI license status active/exit0인데 Editor LicensingClient IPC channel 부재·60초 reconnect 실패를 8분 이상 반복했고 APK 생성/Player 실행 전이었다. 소유 project+PID9961을 재확인해 해당 Editor만 종료했으며 raw runner exit1/RESULT FAIL UNITY_IMPORT_OR_ANDROID_BUILD_FAILED는 보존했다(artifacts/unity-android-e2e-0tikbq7v). 제품 assertion 실패로 단정하지 않으며 실제 Android JNI/현재 Player는 DEFERRED_ENV/NOT_RUN이다. 계정·라이선스 재활성화/우회/반복빌드는 하지 않았다.
- 배치26 D Strict 환경 판단: 전용 AVD 두 개의 PID/양 port/serial/이름/boot는 준비됐으나 실제 Unity 실행환경은 미준비. full request 및 c-full.log 없이 실행횟수0, 전체 Strict DEFERRED_ENV. 준비 controller만 SIGINT해 finally에서 소유 emulator들을 종료했고 디스크/DB/원본 로그·기존 사용자 기기를 보존했다. 기존 배치25 Strict 결과는 역사 증거로 유지하며 이번 source 실행으로 재사용하지 않는다. 독립 iOS C ABI 시험은 현재 source/new18.6 Simulator에서 별도로 수행 중이다.


- [P09-T02] 배치26 완료 조건 판정: Kotlin10 tests/50 helpers(37normal+13expected),Swift12/122(112+10),managed0tests/check1/418(198+220),UnityEditor2/32,stress0tests/100samples/316 helpers를 실제 scope로 분리했다. R01~R12 구조화 결과·공유 native testcase 중복배분 금지·분기 OFF0/ON1·duplicate-only mutation 정상0/변이nonzero/원본hash일치/정상전체418 복원을 확인했다. 전체 assertion outcomes/래퍼밖 implicit signal/JNI assertion은 UNMEASURED이며 현재 Android JNI Player는 환경 대기다. 배치26 A의 명시 완료 조건을 충족해 IMPLEMENTED/PASS로 전환한다. 모든 플랫폼의 현재 Player PASS나 assertion 전체 측정 완료 선언은 아니다.
- [P10-T01] 배치26 D 독립 iOS 실제 검증: source d86ccc2, 새 owned18.6 Simulator의 CBridge testHostPushEventRoutingAndDedup XCTest1 PASS/skip0/exit0(35.92초). xcresult deviceId 일치, 시험 후 정확한 기기 Shutdown 상태 확인; shutdown149는 이미 Shutdown인 기기에 대한 응답이며 실패한 시험으로 계산하지 않는다. Android 새 APK/Player는 ENV-UNITY-LICENSE-IPC로 미실행이며 full Strict 실행0/DEFERRED_ENV. 관련 raw FAIL은 보존한다. 두 private refactor와 unit/Editor/API·선정 ABI 확인 범위는 완료했으나 현재 Unity Player 회귀를 끝내지 못해 Task 전체 IN_PROGRESS/PARTIAL 유지.
- 배치26 D 원격 준비/커밋 전: 새 assertion 계측·진단·staging 검사 unit143 PASS/skip0, 새 self9 PASS. 원장64행 재집계 및 T02 local PASS 근거·T04/T07 PARTIAL·P05 FAIL/ENV26 OPEN/Provider13 WAIT를 분리한다. 원장 편집 첫 시도는 64행 선택 assertion에서 쓰기 전 exit1이었다. 행 시작 정규식으로 대상을 한정해 수정했으며 제품 검증 실패와 구분한다. Native shipping byte/hash와 wire/public API 보존 검사도 Hosted inventory에 연결한다. 다음은 staged 명시 파일·원장/manifest/meta/actionlint/diff 검사 및 전체 push 범위 secret/생성물/PII 점검이다.

- 배치26 D 문서 검사 exit1은 blocker행 삽입 anchor가 Task셀의 동일 ID 참조를 먼저 선택한 편집 오류였다. 변경 전 행을 복원하고 행 시작 anchor로 실제 blocker 원장에만 추가했다. historical 집계 문구도 보존했으며 원장 검사를 재실행한다. 제품/하네스 테스트 실패를 숨긴 것이 아니다.

- 배치26 D 검증/커밋 직전: 원장64행·manifest50·Unity metadata·Core79파일 source/API/wire·actionlint·diff 검사 exit0, CI gate7+workflow mode2 PASS. repo CodingBot000/GameBridge_SDK public 재확인, Actions variables0/runners0(등록/변경 없음). 코드·계측·현재 실행 증거를 명시 파일로만 stage하고 staged 및 기준6d200b0 이후 전체 range의 비밀정보/금지 생성물/PII를 검사한 뒤 handoff FF push한다. false Hosted dispatch는 아직0회다.

- 배치26 D push 점검/커밋 전: 전체8개 기존 commit와 staged 범위를 gitleaks v8.24.2 redact=100으로 검사해 exit0/탐지0. 변경39개 text path에 금지 key·서명·Unity license·원본log·cache·APK/Xcode 산출물·binary 없음. 별도 PII 패턴의3개 후보는 기준source에 이미 있던 synthetic-person@example.invalid 고정 시험 fixture임을 line별 대조했다. 실제 개인정보/실키가 아니며 제품코드 유일 변경은 RequestRegistry.cs다. 원격 handoff는 local의 조상(0 behind/8 ahead),변수0/runner0. 이 기록 및 검증 증거만 명시 stage·scan·commit 후 FF push하고 false Hosted1회를 요청한다.

- 배치26 D FF push 검증/원격 Task 시작: local/remote handoff HEAD c34b419e3a2c719e5d615362f179b38f59b1a241 일치,6d200b0→c34b419 FF 성공. 보존된 미추적3경로 외 tracked clean. repo변수0 재확인. 모든 제품/계측/하네스 소스 commit 후 release_validation=false Hosted-only dispatch1회를 요청한다. Unity self-hosted/Release SKIPPED가 최종 확인되기 전 원격PASS로 기록하지 않는다.

- 배치26 D Hosted-only dispatch1회 수락: run43934095574,source c34b419e3a2c719e5d615362f179b38f59b1a241,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/43934095574 . 현재 in_progress이며 최종 job 결과 대기. 재실행·Release 활성화는 하지 않는다.

- 배치26 D 원격 중간 검증: run43934095574 source c34b419,inventory SUCCESS/Unity SKIPPED,나머지 job 진행 중. 완료 job 로그 조회는 workflow 미완료 상태에서 exit1/빈 반환이라 test0건 또는 계측PASS로 단정하지 않았다. 현재 소유 테스트 Editor/AVD PID6개 모두 종료 및 독립 C ABI 기기 Shutdown을 read-only로 확인했다. full 요청/로그 부재도 재확인(호출0), raw runtime FAIL과 환경 대기 기록을 유지한다.

- 배치26 D 원격 검증: 공식 completed-job API 로그에서 inventory42파일/143 Python건·FAILED요약0·Core source/API/wire gatePASS 확인. Backend jobSUCCESS,Android Maven/R8까지SUCCESS,Swift synthetic Simulator host는아직진행중이다. 앞선 commentary의Android완료선기록은 즉시진행중으로정정한뒤최종SUCCESS를확인했으며 최종보고는공식job상태만사용한다. run43934095574 단일실행/UnitySKIPPED이며basic/Release최종상태는대기다.


- [P09-T07] 배치26 D 최종 원격 검증/커밋 전: run43934095574/sourcec34b419,단1회false입력의전체SUCCESS. Hosted4+basic SUCCESS,Unity/Release SKIPPED를공식job상태로확인했다. inventory42파일/143건·Core source gatePASS,Backend TC11/negative1·복원,Swift17/failure0및syntheticSimhost stepSUCCESS. P09T07 PARTIAL(전용runner/remoteUnity/Release미검증),T04 PARTIAL(18.6간헐미확정),T02localPASS·T01첫범위PARTIAL은유지한다. 최종문서에는모든source·rawFAIL/DEFERRED/UNMEASURED·Strict호출0·기존대기를분리하고작업별9commit이력을남긴다. 다음최종문서commit만scan후handoffFFpush/localremote일치및미추적3경로보존을확인한다. 원격재실행은하지않는다.

- 배치26 최종 검증/커밋 직전: 최종8개 staged경로는공개용Markdown문서뿐이며원본log/key/서명/cache/binary/산출물없음,stagedgitleaks exit0/탐지0. 원장64행·manifest50·meta·Core79파일 API/source/wire·구조화R12개JSON·diff exit0. c34b419 이후 shipping/test/harness/workflow 변경0이고원격단일SUCCESS소스와코드동일. main=e4b677e/fix=6d200b0 그대로보존. 이문서commit을handoff에FFpush후실제local/remoteHEAD와미추적3경로상태를최종보고한다.

- [P10-T01] 배치27 A 시작: 요청문서와 AGENTS/START_HERE·현재원장·마지막로그를 대조했다. branch handoff 및 시작HEADcf276b7 일치,tracked clean/기존미추적3경로보존. 공식log read-only 대조→새전용project CLI/direct 실제Editor smoke 각1회,근거있는 수정최대2회로IPC복구를판정한다. A 실제PASS 전 Player강행없음. C Strict최대1회,완료시에만T02제품변경;차단되면독립감사/회귀설계·E검증/CI/FF인계를끝까지수행한다.

- 배치27 A 관측: batch26 공식Client로그에서 CLI1.0.0-beta.13/LocalIPC1.19.0-rc.3에대한기존HubClient505 Unsupported protocol response와EditorClient1.18.1의globalmutex획득실패를확인했다. PID/시각상관관측이며단일rootcause확정은아니다. 현재CLI상태active/exit0. 공식direct smoke새project를시작했으나marker미생성/Clientmutex실패를관측중이며최종verdict대기. 라이선스/Hub/사용자프로세스조작없음. 비교대기중독립D책임경계read-only검토에착수한다(제품T02수정은C완료전금지).

- 배치27 A direct검증: 새project/공식Editor -batchmode -quit -projectPath -executeMethod -logFile 1회,210초timeout/실제wrapper124/검증exit2(DEFERRED_ENV),smoke JSON/marker없음,compiler CS오류0. Clientmutex획득실패·IPC재연결관측이최종까지지속됐다. own process group만기한종료했고기존Hub/Client/타Editor변경없음. 다음CLI동일smoke새project1회를비교한다.

- 배치27 A/E 관측 도구 보강 시작: raw로그를공개하지않고IPC오류범주·실제Editor메서드receipt/marker/exit를대조하는명시실행형smoke진단하네스를추가한다. active또는부분로그만으로PASS하지않고timeout/nonzero/다른runreceipt/compile실패를구분한다. 이미수행중인CLI/direct비교는각1회로끝내며새하네스추가때문에실제Editor재실행하지않는다. 제품API/라이선스확인/실행gate변경없음.

- 배치27 A 최종검증/블로커: CLI새project비교1회는timeout180초/actualCLIexit6/181.47초,validator exit2,receipt/marker없음,CS compile오류0/IPC부재5회. direct1회는timeout210초/124/210.05초였다. 실제Editor smokePASS가없어A DEFERRED_ENV,복구미완료다. 확인된관측층은protocol505/Clientglobalmutex거부와Editorchannel부재이며누가mutex를유지하는지까지확정하지않는다. 공식명령옵션에서안전한수정근거가없어추가수정시도0/최대2,Hub/라이선스/계정/전체프로세스조작없이대기로전환한다. B현재Player NOT_RUN,C전체Strict호출0/DEFERRED_ENV,T01PARTIAL유지. D는제품변경없이경계감사·최대2후보·회귀설계를수행하고E독립검증/CI/FF인계를계속한다.

- 배치27 A/E 검증: 새순수진단계약6단위PASS/skip0(licenseactive만으로PASS거부,timeout부분결과/비영/foreign·duplicate receipt/compile실패/원본payload비공개). raw실행2건을새판정함수로read-only재분석해둘다DEFERRED_ENV확인했으며Editor재실행은없다. staging147/currentSDKsource일치·PackageCache Notifications2.5.0/Newtonsoft3.2.2 확인. B준비검사는유효하나Player실행은A미충족으로NOT_RUN. 현재소스/API/wire검사·전체Python및별도Native/managed 회귀를E에서진행한다.

- [P10-T02] 배치27 D 감사/설계 완료(REVIEW_ONLY): Native인증/UI/세션저장·구매계정/증빙/완료·Push host/등록/router·전송redaction경계를파일/함수/기존테스트로대조했다. 후보는Android bound-session codec/검증과Swift grant 응답decoder 두개뿐,추가회귀설계는NOT_RUN. Android두refresh flow의저장/profile순서차이와Swiftgeneration/MainActor·동일attempt retry/finish순서를보존하도록기록했다. Push는분리근거가충분해새후보추가없음. A차단/C미충족이므로제품변경0,T02완료승격없음. E전체회귀/새하네스CI연결/인계로이동한다.

- 배치27 E 검증/커밋 전: Python전체149건PASS/skip0,새진단6건은Hosted inventory에연결했다. 원장64행·manifest50·meta·Core source/API/wire·actionlint·diff PASS,staging147/currentSDKsource·exactCache일치. A실제direct/CLI는각1회DEFERRED_ENV(124/6),다시실행없음. 공개정제IPC JSON·T02감사/설계를추가했고shipping제품/baseline파일변경0. 원본log/개인정보/라이선스파일은추적하지않는다. 진단도구는미래재개용이며이번실제비교는보존된artifact wrapper명령으로수행했음을분리한다. commit후고정source에서Core·Native·managed/mutation/self9를검증한다.

- 배치27 A/E 커밋 직전: 두실제Editor비교DEFERRED_ENV·추가수정0·B/C미실행과raw보존/정제IPC JSON을기록했다. 신규진단하네스는6unit/전체Python149PASS·actionlint/API/progress검사PASS이며현재실패log재분석만추가(Editor추가실행0). 이진단/CI연결과A증거를독립commit하고D감사문서를다음별도commit으로남긴뒤고정source의E실행을수행한다. 공개에는원본Client/Hub/CLI로그·라이선스·개인정보를올리지않는다.

- [P10-T02] 배치27 D 검증/독립 커밋 전: 책임감사문서의호출경로·후보2·기존testcase·미실행설계·선행차단근거를확인했다. T02원장은IN_PROGRESS/PARTIAL유지,감사활동만REVIEW_ONLY이며DEP-P10-T01을명시했다. 제품source/API/baseline파일변경0. A진단commit39a3076 이후이문서와진행기록만별도commit하고고정sourceE검증으로계속한다.

- 배치27 E Core/API 실제검증: sourceffed5c2 tracked-clean의core-assertions-_jnkfd1a exit0/PASS. Kotlin10test/50helper,Swift12/122,managed0test/check1/418(198normal+220expected),duplicate정상2/0→변이부분1/nonzero→원본hash동일/정상복원418,분기419/추가OFF0ON1,stress100samples/316. Editor는include하지않아NOT_RUN. 보존batch26artifact의shipping79hash·UPMmanifest/checksum147·javap3class·Cexport4개양slice현재재대조PASS(새build아님). E뒤이은Native회귀는같은shipping code이며현재미커밋변경은이결과문서뿐이다.

- 배치27 E Native 검증/커밋 전: ffed5c2와같은shipping79hash(전후실측동일)에서Android선택Core/session·auth·purchase·push fake JUnit42건/실패error skip0·Gradle0,Swift선택Native/session/store/push XCTest38건/실패skip0·exit0. 현재미커밋은결과문서뿐이며실제OS/Provider/Player실행은아니다. lifecycle100samples/liveClient·Transport0·helper316 및API/선정ABI대조도기록한다. 이독립회귀증거commit후새격리DB/role의self9만수행하고전체Strict/Editor/Player는A미충족으로재실행하지않는다.

- [P09-T08] 배치27 E self검증/커밋 전: sourceb540e7b tracked-clean의새DB/role에서self-only9/9PASS/exit0(harness-self-natvatov,strict-isolated-sj48fr5f),tests47/의도negative3/checks9/예상외failure0/skip0. checkererrors null은미측정으로보존,fullStrict호출0·Simulator/Player생성없음. Core/Native/ABI·자가시험정제JSON을추가했다. repository CodingBot000/GameBridge_SDK public,변수0/runner0 정상API응답확인;remotehandoff CF276b7이local조상(0behind/3ahead). 모든소스commit후증거/문서를scan하고FFpush/falseHosted1회를요청한다.

- 배치27 E push검사/커밋 전: cf276b7이후4commit gitleaks exit0/탐지0,13개text경로에제품/baseline변경·key/서명/Unitylicense/원본log/cache/binary/산출물없음. PII후보3개는기존원장/로그의변경없는synthetic설명2개와새sanitizer시험용invalid-domain값1개뿐이다. 첫전파일패턴검사는기존기록후보를신규후보로보아assertionexit1이었으며line별기준source대조로확인했다. 전체Python43module/149건확인,Actions변수정상응답0/runner0. 현재commit후handoffFFpush/falseHosted단1회만실행한다.

- 배치27 E FFpush 검증/Hosted Task 시작: local/remote handoff HEAD50cd34c2f3c97eca36708d4a2ed377da392247d7 일치,cf276b7→50cd34c FF성공. 코드/테스트/CI변경모두commit됐고기존미추적3경로외tracked clean. repo변수정상응답0재확인. release_validation=false Hosted-only1회를지금요청하며Unity/Release최종SKIPPED확인전전체원격PASS로기록하지않는다.

- 배치27 E Hosted dispatch1회수락: run44057317769/source50cd34c2f3c97eca36708d4a2ed377da392247d7,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44057317769 . 현재in_progress,최종결과대기이며추가dispatch/재실행/runner등록/Release활성화없음. 직전push검사문구의경로개수오기를실제audit13개로정정했다(관측실패삭제없음).

- 배치27 E 원격중간검증: run44057317769/source50cd34c,inventorySUCCESS·공식joblog43파일/149건PASS/FAILED요약0·신규진단6건연결·Core source/API/wire gatePASS. UnitySKIPPED. 나머지Android/Backend/Swift 및basic/Release최종상태는대기하며전체PASS로선기록하지않는다. 원격재실행없음.

- 배치27 E 원격중간검증2: Android/Maven·R8와Backend최종SUCCESS,공식Backend로그에Testcontainers11건/의도mutationfailure1·정상복원receipt확인. Swift package fake stepSUCCESS이나syntheticSimulatorhost는아직진행중,전체job/Basic·Release최종상태대기. 단일dispatch유지. 별도조회에서오입력job ID의404는현재workflow실패가아니며공식run metadata의실제Swift job ID로상태를다시대조했다.


- [P09-T07] 배치27 E 최종검증/문서커밋 전: 단일run44057317769/source50cd34c2f3c97eca36708d4a2ed377da392247d7,release_validation=false전체SUCCESS. Hosted4+basic SUCCESS,Unity/Release SKIPPED,inventory43파일/149건·진단6건·CoregatePASS를공식job/로그로확인했다. A/B/C환경대기·T01/T02PARTIAL·P05FAIL/ENV26OPEN/18.6간헐위험/Provider13WAIT/self-hosted미검증유지. 최종문서에모든commit/source/미실행·UNMEASURED를구분하고앞선경로개수오기13으로정정했다. 제품/test/harness/workflow는CI소스이후변경0,이문서만scan·commit·handoffFFpush후local/remoteHEAD및미추적3경로보존을확인한다. 추가원격실행없음.

- 배치27 E 최종문서검증/커밋 직전: 원장/manifest/meta·두API/source baseline·정제JSON·diff검사PASS,CI이후제품/harness/test/workflow변경0. IPC JSON의124는direct실제Editor반환값이아닌outer timeout wrapper코드이고CLI6은실제CLI반환값임을명시했다. 두경로Editor child 종료값은미수집/UNMEASURED로분리했다. 최종문서와정제증거만명시stage·secret/생성물검사후commit/FFpush하고실제HEAD일치및Git상태를보고한다. 새실행/승격/재dispatch없음.

- 배치27 최종커밋 직전: staged8개는Markdown/정제JSON문서뿐,secret검사exit0/탐지0·binary/원본로그/서명/license/build산출물없음. CI이후소스변경0,원장/두APIbaseline/diffPASS. 마지막문서commit후전체batchrange scan·handoff FFpush와remoteHEAD일치를검증하고,기존미추적Demo/cache만보존된Git상태를최종보고한다.

- [P10-T01] 배치28 A 시작: 지시문·AGENTS/START_HERE·마지막원장/로그·branch/HEAD3955e4e/기존미추적3경로를확인했다. 문서의사용자Editor정상실행확인에대해사용자가“네가 정상실행 확인해줄수있나?”로확인을위임했다. 새전용project direct실제smoke1회로receipt/marker/exit를판정한다. 단순CLIactive는PASS아님. 실패시Player강행/반복없음;T01완료시에만C1/C2순차변경. 버전조회/실행/결과기록후독립검증과명시FF인계까지진행한다.

- 배치28 A 관측/독립D 시작: Hub3.22.6/CLI1.0.0-beta.13/Editor6000.5.8f1,HubClient1.18.3+d7ffd15를read-only확인했다. EditorClient bundle표시1.2.0과실제실행Client product version1.18.1+9fbee8e는서로다른metadata로분리한다. 새direct smoke1회진행중IPCtimeout/receipt부재관측,최종결과대기. 이대기동안실제Editor·라이선스·사용자기기를조작하지않는D전체Python/API/staging검사를독립수행한다. B/C제품진입조건은아직미충족이다.

- 배치28 D 독립검증: Python전체149건PASS/skip0(15.830초). 원장64행·manifest50·meta·두API/source/wire baseline·staging147·actionlint·diff exit0. 실제Editor는IPCtimeout/receipt미생성상태로아직verdict대기이며unitPASS를EditorPASS로바꾸지않는다. 제품/하네스/테스트/workflow변경0,미커밋은배치시작/검증문서뿐이다.

- 배치28 A 최종검증/블로커: 위임된direct smoke1회는210초timeout/진단wrapper124·검증exit2(DEFERRED_ENV),receiptCorrelated=false/marker0/compile오류0. 실제Editor child종료반환값은미수집UNMEASURED로구분한다. 이번실행이시작한Client PID로그만read-only대조해mutex획득실패를확인했고productversion1.18.1+9fbee8e이다. 원본artifacts/unity-editor-smoke-w2bupii_와정제JSON보존,라이선스/계정/기존프로세스조작없음. B현재Player/R09플랫폼영향NOT_RUN·fullStrict0/DEFERRED_ENV,T01PARTIAL유지. C1/C2제품진입은선행미충족으로미실행이다. D독립Core/Native/자가시험·E문서/FF인계를계속하며동일Editor재실행없음.

- 배치28 위임된Hub일반실행확인: CUA로Hub3.22.6의새전용artifact project만Add project from disk→해당project(6000.5.8f1)열기를1회수행했다. 실제Unity6000.5.8f1창/Scene·Hierarchy(Main Camera/Directional Light)·Project·Inspector정상UI를확인(PASS_UI_SCOPE)했고CUA결과확정후completion기록했다. 기존사용자project/계정/Cloud연결/라이선스설정변경없음;검증용GUIEditor는열린상태로보존한다. 앞선direct batchtimeout은삭제하지않고A자동receipt조건미충족으로B/Strict/C진입보류유지,추가자동smoke0회.
- 배치28 실제관측부작용: 새GUIEditor상태바에Multiple ADB server instances 및다른SDK인스턴스종료경고가표시됐다. 에이전트가ADB kill/restart/설치·네트워크명령을호출하지않았으나Unity시작의자동동작관측이므로ADB상태완전불변이라고주장하지않는다. 대상SDK/프로세스/기기영향은미확정이며확인없이추가ADB조작하지않는다. 사용자에게commentary로알렸고정제JSON에분리기록했다.

- 배치28 A/D 커밋 직전: 실제direct1회실패와HubGUI1회정상UI를서로다른scope로공개정제기록했다. 자동receipt/B/Strict/C조건미충족·실제ADB시작경고미확정도유지한다. Python149·문서/두API/staging/actionlint/diff통과,제품코드변경0. 이관측/설정인계를별도commit후고정source독립Core·Native·자가시험을검증한다. 원본화면/개인project목록/원시log/라이선스는commit하지않는다.

- 배치28 D Core 검증: commit4d58d13 tracked-clean의core-assertions-7b_9fhgq exit0/PASS. Kotlin10/50helper,Swift12/122,managed418(198normal+220expected),복원418/branch419,stress100samples/helper316 및정확duplicate-only변이감지/원본hash복원확인. Editorinclude없음/JNI실제Player assertion UNMEASURED. 보존artifact의현재79source/checksum·javap3class/Cexport4x2재대조PASS(새build아님). Nativeauth/purchase/push회귀와self9는동일shippingcode에서계속한다.

- 배치28 D Native 검증/커밋 전: source4d58d13과동일shipping79hash전후실측에서Android선택session/auth/purchase/push JUnit42건/failure0/error0/skip0/exit0,Swift38건/failure0/skip0/exit0. 미커밋은결과문서뿐이며실기기/스토어/푸시서비스통과가아니다. 현재5037 listener PID68316을lsof/ps로만읽었고사전owner/종료대상은UNMEASURED;ADB실행/서버조작없음. 이결과문서commit후새격리DB/role self9만수행하며fullStrict/Player/추가Editor실행없음.

- [P09-T08] 배치28 D/E 검증: self source2737429c873e272b1576b519e709582670cf75ac tracked-clean에서새격리DB/role self-only9/9PASS/exit0(artifacts/harness-self-ewkzqy1d,strict-isolated-9y2p_lsi). tests47/의도negative3/checks9/예상외failure0/skip0,checkererrors미측정유지. self-only로Simulator/Player/전체Strict없음. 이번제품/harness/test/workflow/baseline변경0이라E조건의Hosted추가dispatch0/NOT_RUN,기존배치27CI는역사증거로만유지한다. 현재local/remotehandoff는FF가능(0behind/2ahead),repo public CodingBot000/GameBridge_SDK확인. 정제회귀JSON·상태/다음행동·최종보고를갱신하고scan/commit/FF인계를마친다.

- 배치28 E 최종검증/커밋 직전: 공개문서/정제JSON만변경,제품/harness/test/scripts/workflow/baseline diff0. 정제JSON두개parse·원장64행·API/source/wire·metadata/manifest/diff검사PASS,Python149·Native42/38·Core/managed418·self9의scope를분리했다. 일반GUI정상과자동batch실패·ADB경고미확정·미실행B/Strict/C1C2·추가CI0을정확히기록했다. 원본log/화면·사용자project목록·라이선스/서명/빌드산출물을제외하고명시stage/scan/commit/FFpush후localremoteHEAD와Git상태를검증한다.

- 배치28 E staged검증/커밋 직전: 명시stage8개는문서/정제JSON뿐이며gitleaks exit0/탐지0,binary/원본log/서명/license/생성물없음. baseline이후전체변경도문서10경로뿐이다. 마지막인계commit후전체범위scan→handoff동일branch FFpush→실제local/remoteSHA와tracked clean·기존미추적3경로보존을조회한다. GUI검증project는열린상태로남기며ADB추가명령/새Editor/Player/CI실행없음.

- [P10-T01] 배치29 A 시작: 지시문·AGENTS/START_HERE·마지막원장/로그와branch/HEAD7fe7c4a/기존미추적3경로확인. GUI가열린전용artifact project만대상으로test-only메뉴를구성해실제C#컴파일·nonce/버전/소유경로·Unity객체생성/정리·메서드도달receipt를검증한다. batch전용Application.isBatchMode조건과GUI를구분하고새장시간batch는실행하지않는다. 이후현재소비projectGUI Player빌드,ADBread-only/전용기기소유증명조건부E2E,미충족시T02독립정상음성test까지연속수행한다.

- 배치29 A 구현/검증·커밋 전: test-only GUI메뉴는실제UnityEngine객체생성/Transform조회/DestroyImmediate7조건과nonce·버전·projectpath·scriptSHA·Editor assembly/PID·시간receipt를검사한다. parser는GUI범위만PASS하며batch/Player로승격하지않는다. 누락runtime증거·stale source/nonce/script·다른project/version/batch·부분실패receipt음성5단위PASS/skip0,CI연결완료. 전용artifact project만준비하는명시도구를추가했다. 소스commit후기존열린project에복사·컴파일하여GUI에서메뉴를실제로실행한다. 제품SDK/라이선스/장시간batch수정없음.

- 배치29 A 실제GUI컴파일 최초FAIL: test-only GameBridgeGuiVerification.cs의GetInstanceID가Unity6000.5.8f1에서CS0619(Use GetEntityId instead)로거부됐다. 신규메뉴미노출/메서드NOT_RUN,SDK제품회귀FAIL로분류하지않는다. 로그조회는실제GUIlog경로와default로그를구분한다. UnityEngine객체이름·active/Transform·DestroyImmediate검증으로호환수정하며조건7개/nonce/proof를약화하지않는다. 수정시도1회,원본실패보존.

- 배치29 A 실제GUI 검증PASS: source dcc0b4c,nonce7bbe2cf1b06d4612be219d88ac488fb2,Editor6000.5.8f1/PID68110/Assembly-CSharp-Editor의RunProbe가실제메뉴로컴파일·실행됐다. 소유project/메서드/scriptSHA/nonce/time/receipt·freshlog1회검증,실제UnityGameObject이름/active/Transform·DestroyImmediate7조건통과. tests0/check1/enginechecks7,GUI범위PASS이며batch/PlayerNOT_RUN이다. 최초test-onlyCS0619실패/수정1회는보존했다. BcurrentSDK새소비project GUIbuild로계속한다.

- [P10-T01] 배치29 B/C 입력계약 설계·구현 시작: A GUI실제메서드PASS에따라현재staging147/source/API·Maven/XCFramework/cache를확인한새소비project를준비한다. test-only메뉴가project내비밀아닌출력설정을검증하고기존BuildMockPlayer.Build를변경없이호출한다(환경값은그Editor프로세스에서만일시전달/복원). GUI APK를실제E2E에쓸경우명시receipt입력으로만허용하고nonce/source·147manifest·builder/scenario/log·APK SHA/size를엄격검사하며기존CLI실패→성공fallback은없다. B/C 실제빌드/실행은아직NOT_RUN이다.

- 배치29 B/C 계약 검증/커밋 전: GUI Android메뉴는147패키지파일·builder/scenario/adapter SHA를실제검사후기존BuildMockPlayer를그대로호출하고실제APK size/SHA·원본빌드return·로그nonce를기록한다. GUI용명시입력은APK hash/크기/신선도/소유path/symlink/sourceancestor및보호SDK·scenario diff0/currentstage147·정확cache·원본빌드marker를검사하며,실패입력은ADB/DB전즉시차단하는음성단위추가. 기존CLI기본경로와Backend/원장/marker/PII검사본문은유지했다. unit통과후commit된source로새소비project준비·GUI빌드를진행한다. 실제B빌드/C실행은아직NOT_RUN이다.

- 배치29 B 실제GUI Android빌드PASS: source7263444/nonce85e0d5036b344ac7b90ef95da9cb035f,새GameBridgeGuiAndroidB29 project에서Androidtarget전환후기존BuildMockPlayer.Build를실제호출했다. originalBuilderReturned=true,packageFilesVerified147,APK27072192bytes/실제SHA·원본GB_MOCK_BUILD PASS·freshnonce시작/완료로그·project/source/staging/cache·builder/scenario/adapter SHA입력계약모두재검증PASS. tests0/check1/players0,CLI/batchPASS아님. 이전probe전용Editor만정상Quit했고새소비project는Hub로열었다. C는5037owner/동일ADB실행경로·전용AVD/PID양port소유입증후에만진행한다.

- 배치29 C 안전경계 구현/검증·커밋 전: GUI APK소비경로는명시emulator PID/이름/serial/양port와기존5037 serverPID·동일SDK adb실행파일을모든ADB호출직전에재검증한다. 다른기기/SDKclient·server kill/start명령·owner변경은실행전차단하며실패입력의ADB/DB도달0을확인했다. 신규GUI계약15건및기존emulator binding5건PASS/skip0,CI연결했다. 기존CLI모드/Player결제원장·PII·callback검사본문은유지한다. 실제C조건부실행은새전용AVD소유입증후1회수행하며기존서버를기동/종료하지않는다.

- 배치29 C 실제Android E2E FAIL/exit1: GUI APK입력검증·새AVD부팅(PID80979/serial5590/이름/5590·5591양port소유)·기존Unity SDK ADBserver79436同경로가드·설치Success·Activity Status:ok까지통과했으나180초내Player완료marker가없어UNITY_PLAYER_RESULT_TIMEOUT(artifacts/unity-android-e2e-eb3lua0b). batch빌드실패와다른실제실행FAIL로보존한다. CUA가Qt Emulator를제어가능앱으로노출하지않아UI확인/조작은불가했고UI원인으로단정하지않는다. 원본DB/AVD/로그보존,controller는자기emulator만종료,이후serialbinding없어추가ADB조회안함. DBread-only확인첫시도는prefix검사에서실행전중단됐고실제producer의gamebridge_ci_10hex규약대조후해당신규DB만조회했다. 근거없는동일실행반복없음. D제품변경은보류하고독립후보정상/음성test를진행하며iOS는별도GUIexport가능성을확인한다.

- [P10-T02] 배치29 D 독립test 구현 시작: Android실행timeout으로T01완료조건미충족/PARTIAL이므로codec/decoder제품변경은하지않는다. 기존Nativeauth/HTTPSink 경로에저장binding/잘못된session/저장실패순서,GRANTED·ALREADY_GRANTED/잘못된grant/다른account/로그아웃후늦은HTTPgrant를정상음성case로구현한다. fakegateway/URLProtocol만사용하고실Provider·finalization정책변경없음. 전체Native149/self9를관성적으로반복하지않고변경된AuthProvider testclass와GUI하네스영향을검증한다.

- 배치29 D test 검증: Swift AppleAuthProviderTests20건/실패skip0/exit0(신규grant정상·잘못된응답/다른account·logout후늦은HTTPgrant거부포함). Kotlin첫호출은ANDROID_HOME미지정으로task의존성계산단계exit1/테스트0건이었다. 소스/assertion수정없이기존설치SDK경로를해당subprocess환경에명시해재검증한다. 최초환경실패원본보존,성공으로위장하지않는다.

- 배치29 B/C iOS 독립검증 시작: Android timeout을iOS결과로확대하지않고새전용iOS소비project에서기존BuildMockIosPlayer를GUI메뉴로호출하는export경로를구성한다. 출력설정은project-local/비밀아님,현재147패키지·builder/scenario·exporttree/PBX hash/nonce로그를검사한다. 원본Builder/SDK/finish정책변경없음. export가실제성공하고입력계약을검증한경우에만새ownedSimulator/DB로기존iOSE2E의원장·callback/PII검사를그대로진행한다. 아직iOSexport/Player NOT_RUN.

- [P10-T02] 배치29 D 실제독립회귀/커밋 전: Android GoogleAuthProviderTest18건(신규3)/failure0/error0/skip0/Gradle0,Swift AppleAuthProviderTests20건(신규2)/failure0/skip0/exit0. stored binding/잘못된credentials의network전거부·profile후save실패순서,정상grant2status/잘못된grant·account및logout후늦은HTTPgrant CANCELED를실제주입경로로검증했다. SDK제품/refactor/finish순서변경0이며T02전체완료아님. 기존동시refresh/tombstone/같은idempotency retry회귀도같은class에서유지됐다. Swift20class를Hosted필터/required suite 검사에연결했다. Kotlin최초SDK설정실패는보존.

- 사용자 요청 안전중단/커밋 직전: 현재빌드/Player/시험Backend·Gradle/Swift testcase진행없음,ownedemulator80979/controller종료·AVD/DB/로그보존,Android소비GUI79170은idle로남긴다. 미완료iOS helper/준비·export입력계약·음성4건은Python syntax/GUI단위19PASS를확인한코드상태로localcommit하되실제iOS컴파일/export/PlayerNOT_RUN이다. 신규unit을Hosted연결했지만아직CI미실행. docs/evidence/p10-batch29-resume.md에모든source/nonce/artifact·실패/미실행·재개명령·금지조건을기록했다. 이번push0/dispatch0,네트워크작업시작없이pause한다. T01/T02PARTIAL/기존FAIL·외부대기유지.

- 중단기록검증: 문서작성의첫호출은마지막PROGRESS머리말갱신전에import re 누락NameError로멈췄다. 이미기록된체크포인트/실패·unit결과는보존하고머리말/USER_SETUP만정정완료했다. 원장검사·Python문법·새iOS4음성/정상unit은exit0. 실제iOSGUI실행/전체회귀는미실행으로명시한다. offline secret검사후로컬중단commit만남기고정지한다.

- 중단전offline secret검토: version명시go-run은deprecation metadata lookup차단으로실행불가였다. 캐시source 직접실행으로6commit전체scan은exit1/finding2. 모두b1e3c73 candidate-tests.json18/19의testSourceHashes값이며실제Kotlin/Swift test파일SHA256과독립계산일치→credential아닌metadata오탐확인. publicJSON은path/sha256배열로정리했고기존이력/실패를삭제·amend/ignore하지않았다. rawexit1과정확재검토근거를resume문서에기록했다. 네트워크/push/CI없음.

- 사용자요청중단확정/최종localcommit전: 마지막staged문서offline gitleaks exit0/탐지0,원장/diff검사PASS. 이전6commit scan의2개sourcehash metadata오탐은별도근거/exit1그대로보존했다. 현재활성시험/빌드/Player없음,새네트워크/push/CI없음. 사용자재개지시전작업을진행하지않으며resume문서의정확한다음명령에서시작한다.

- 사용자 재개 지시 수신: HEAD953a5a5/동일handoff/기존미추적3경로보존·중단문서/AGENTS/START_HERE/원장/로그대조완료. 사용자요청pause는해제됐다. 기존Androidtimeout·GUI APK/후보test PASS는보존하고새근거없는재실행없음. 현재Editor·5037owner는read-only로새로조회했으며과거PID/AX index재사용하지않는다. 다음미실행iOS GUI소비project준비→실제컴파일/export입력검증→가능시별도Simulator E2E·E검증/명시FF/Hosted1회로이어간다.

- 배치29 재개 iOS 실제GUI export PASS: source953a5a5/nonceb0626c0dfa914789b0fe2eee01d2a3af,새GameBridgeGuiIosB29를Hub로열고실제iOS target전환·기존BuildMockIosPlayer.Build를GUI에서호출했다. 원본Builder return/147SDKfiles·script/adapter/scenario·PBX/exporttreeSHA·nonce로그·현재source보호경로diff0입력계약검증PASS. tests0/check1/Player0,GUIexportPASS는batch나Simulator실행PASS가아니다. 이전Android전용GUI만정상종료했으며사용자project/라이선스/기존기기를조작하지않았다. 이제해당검증된export로새Simulator/DB의기존E2E를독립1회수행한다.

- 배치29 iOS GUI입력 의존성검사 보강/커밋 전: 실제export PASS후E2E소비계약을점검해iOS에도정확embedded Notifications2.5.0/Newtonsoft3.2.2검사를명시하고summary에보존했다(기존Android같은검사공유). 잘못된version음성unit포함GUI20단위PASS/skip0. C#Builder/SDK/export바이트변경없음,receipt빌드source953a5a5는보호경로diff0인현재harness/doc후속commit의ancestor로기록한다. 실제Simulator실행은아직미실행이며commit후시작한다.

- 배치29 iOS 실제Simulator E2E PASS/exit0: sourced543556 tracked-clean,GUIexport buildsource953a5a5와보호SDK/scenario바이트동일성검증후Xcode ad-hoc Simulator build·C ABI4symbols·새Simulator/DB·initialize/login/products/purchase/wallet/logout 및PII24marker·Backendtrace·원장1/delta100통과(artifacts/unity-ios-e2e-c4qqwuvs). 실Apple/스토어/APNs아님. receipt의UUID8D737ECF-CD32-4069-A64D-30D3D5176210와새DB suffix로deviceName소유를대조한뒤해당기기만shutdown/데이터보존,다른Simulator조작없음. AndroidFAIL과합치지않는다.
- 배치29 E 영향하네스최종회귀: 코드변경이있어전체Python을최종1회수행,169건PASS/skip0(18.793초). 이번에전체Native·self9/Strict를관성재실행하지않았고이전증거와구분한다. 원장/manifest/meta/API-source-wire/actionlint/diffPASS. T01은AndroidFAIL/나머지미실행조건때문에PARTIAL이며T02제품refactor진입없음,독립신규tests만PASS다.

- 배치29 E 입력경계검토·검증: GUI용ADBguard dispatch가configured client의basename만검사하면renamed실행파일로빠질수있는경로를발견해configured실제path도검사하도록보강했다. subprocess전거부unit추가. PII주scenario뿐아니라보조PiiProbe/link.xml의현재checkout일치도양GUI입력에서검사하고변이음성추가. 실제두소비project보조소스일치확인,GUI22단위PASS/skip0. 실제실행은원래동일SDK의adb·원래보조소스였으므로이두보강으로플랫폼E2E를반복하지않는다. SDK제품/기존검사약화없음. 변경된harness최종전체Python을다시검증한다(이전169PASS도보존).

- 배치29 E 현재결과/커밋 전: A GUI컴파일메서드·AndroidAPK·iOSexport와실제iOSPlayer는PASS,AndroidPlayer는timeoutFAIL로보존,StrictNOT_RUN·T01/T02PARTIAL. 후보제품변경0/신규test3+2는18/20class에서PASS,GUI22/전체Python171 PASS와이전169PASS를분리했다. API/source/wire·manifest/meta/actionlint/diffPASS. source별정제JSON/인계문서를갱신했다. 원격repo public/변수0/runner0/behind0 ahead9 확인,전체이력scan실제exit1의2finding은정확한b1e3c73 test-sourceSHA metadata와재계산일치(신규finding0)로review,원래이력삭제/ignore없음. 문서commit후명시handoffFFpush/falseHosted1회만수행한다.

- 배치29 E push전검사/커밋 전: 전체변경경로는text의하네스/test/CI·정제문서뿐이며SDK제품/contract·binary·금지키/서명/license/원본로그/캐시/APK/Xcode산출물delta0. PII gate첫검사는기존harness합성identity설명을새후보로보아중단됐고기준source같은line/invalid-domain값대조로검토했다. 모든후보는변경없는합성fixture/설명이다. gitleaks는정확히b1e3c73 sourceSHA metadata2건오탐만재확인(실제exit1보존),새finding없음. repo public/변수0/runner0·FF이력확인. 이문서commit후handoffFFpush,새소스와test를포함한falseHosted단1회로검증한다.

- 배치29 E FFpush 검증/Hosted 시작: local/remote handoff HEAD3fd95f459355d5abdab98ff9c622a7bd5675d0d1일치,7fe7c4a→3fd95f4 FF성공. 코드/test/CI변경모두commit됐고기존미추적3경로외tracked clean. 변수정상API응답0을재확인했다. release_validation=false Hosted-only단1회를지금요청하며최종job결과대기전원격PASS로기록하지않는다. runner등록/main/force/Release실행없음.

- 배치29 E Hosted dispatch1회수락: run44096116650/source3fd95f459355d5abdab98ff9c622a7bd5675d0d1,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44096116650 . 현재진행중이며최종결과대기,추가dispatch/재실행/runner등록/Unity활성변수변경/Release없음.

- 배치29 E 원격중간검증: run44096116650/source3fd95f4 inventorySUCCESS,공식job로그47파일/171건PASS/FAILED요약0와GUI4모듈연결확인. UnitySKIPPED,나머지Hosted/basic/Release최종상태대기이며전체PASS선기록없음. 단일dispatch유지.

- 배치29 E 추가정적관측: 보존APK의arm64 libgame/libmain/libunity/libil2cpp·manifest UnityPlayerGameActivity/native lib=game을read-only대조했다. 현재자료에서해당누락/mismatch가관측되지않았다는범위이며timeout원인/정상실행증명아님,추가device실행없음. 원격Android/Backend SUCCESS,Swift package단계SUCCESS·host시험대기,코드변경/추가dispatch없음.


- [P09-T07] 배치29 E 최종원격검증/문서커밋 전: run44096116650/source3fd95f459355d5abdab98ff9c622a7bd5675d0d1,false입력1회전체SUCCESS. Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED. 공식Python47모듈171/Swift37(후보20포함)/TC11·의도변이1및정상복원확인. 신규code/test모두검증source에포함됐고이후문서변경뿐이다. AndroidFAIL/Strict미실행·T01/T02PARTIAL·P05FAIL/ENV26OPEN/18.6위험/Provider13WAIT/self-hosted미검증보존. 단계별source·모든commit·남은작업을최종문서에기록후stage scan/localcommit/handoffFFpush와localremoteHEAD/미추적보존을검증한다. 추가dispatch없음.

- 배치29 E 최종stage검증/커밋 직전: 명시11개파일은Markdown/정제JSON문서뿐,staged gitleaks 실제exit0/탐지0·diff0오류. 전체이력의b1e3c73 sourcehash2건오탐(actualexit1)은별도재계산근거로유지했다. 원장64행집계22구현/42진행·local20PASS/1FAIL/43PARTIAL일치. CI이후code/test/harness/workflow delta0. 마지막문서commit후handoff동일branch FFpush/localremoteHEAD·tracked clean/기존미추적3경로보존을확인한다. 추가CI/실기기/Provider/Release실행없음.

- [P10-T01] 배치30 A 시작: 지시문·AGENTS/START_HERE/원장/마지막로그·branch/HEAD2c8e7a7/기존미추적3경로대조완료. B29 원본/소비scenario/builder/harness와B25PASS를읽고설치/Activity·process/runtime/Scene/Awake/Start/intent/SDK객체/init/callback/HTTP를분리한다. 첫marker가init완료뒤라는코드상한계를확인했으며Start미도달로단정하지않는다. 원본을보존하고필요한진단만추가→새GUI APK·새전용AVD1회,원인별수정후최대1추가실행조건을지킨다. SDK제품/timeout/성공조건/서버/타기기변경없음.

- 배치30 A 대조결과: B25/B29 모두Unity6000.5.8f1 serializedversion/arm64IL2CPP·같은선택PlayerSettings와동일Pii scenario SHA,Scene에올바른script GUID참조확인. libmain/libc++동일이지만libunity/libgame/libil2cpp/swappy바이트는달라전체Native동일로주장하지않는다. debugger대기/nativeWait0 등선택boot옵션동일,build GUID/network주소는공개제외. B29설치/Activity응답확인외실제PID생존·Scene/Awake/Start/intent/SDK/init는UNMEASURED,emulator VkInstance관측은graphics호출부분증거뿐이다. initialize는HTTP없고첫dev-auth는SignInAPI뒤이므로DB0을Start미도달로단정하지않는다. B의조기단계/다중로그관측이필요하다.

- 배치30 B 구현 시작: Android전용표준/PII/UTF8소비scenario에실제Awake/sceneIndex·Start/focus/pause·intent존재/유효성(bool만)·SDK생성·init호출/반환/예외·첫auth API직전marker를추가한다. 제품SDK/await순서/완료시점/기존성공·실패marker는바꾸지않는다. 하네스는동일소유guard하의PID생존·resumed/focus·모든logcatbuffer/AndroidRuntime/ANR/native-load·UI hierarchy·Backendhealth/첫trace관측을ignored raw와정제범주로분리한다. 로그수집불가를정상으로판정하지않는다.

- 배치30 B 진단계약검증/커밋 전: startup진단8건/GUI입력7건PASS/skip0(무marker는UNMEASURED,init호출과반환구분,package crash/ANR·knownSystemUI증거,raw비공개/secretredaction·PID종료관측·log수집불가거부·HTTP첫관측시간미위조). 원래180초deadline은Activity응답직후로유지해진단수집으로대기창을늘리지않는다. defaultCLI옵션은유지하고 --startup-diagnostics를명시한다. 새marker는고정point/유효성bool/engineelapsed뿐이며기존성공/실패조건·SDK/await순서변경0. CI연결및별도GUI projectlabel검증추가. commit된source에서새B30A소비project/APK를준비한다.

- 배치30 B/C 전검증·커밋 전: 새계측GUI APK가실제원본Builder로생성됐고147package·source/scenarioSHA·nonce로그·APK크기/hash·현재입력계약재검증PASS. package crash판정은FATAL/해당Process 또는해당Native tombstone을요구하도록구체화했고optional UI idle timeout은UNMEASURED/124로표시하되소유권실패는전파하는음성추가(진단9건PASS). mandatorylog/PID수집실패는여전히E2E성공불가다. SDK제품/await/원래성공/timeout조건변경0. commit후새전용AVD1회진단실행을시작한다.

- 배치30 C 첫진단재현 관측/블로커: 앱PID4639생존·Activityresumed·Unity Initialize engine version/PlayerInitEngineGraphics OK가실제allbuffer로그에있으나Awake/Start marker없음·Backendtrace0. NativeFocus lost이후UIhierarchy의framework package android에Viewing full screen/To exit swipe/Got it 안내가실제존재했다. 초기detector의SystemUI전용조건이이를False로놓친문제(진단하네스)를android도허용하도록수정/음성검증했고focusfield부재는UNMEASURED로정정했다(원본보존). 이것은OS안내관측이며닫은뒤실제회복검증전SDK원인완전확정/PASS로표시하지않는다. Qt CUA표면한계로필요한정상UIack은사용자직접조작가능여부/이전용기기ADB UI입력명시요청을async문의했고답변전그조작을강행하지않는다. SDK제품변경0.

- 배치30 C 최초진단실행 종료FAIL/exit1(UNITY_PLAYER_RESULT_TIMEOUT,artifacts/unity-android-e2e-pe_0tdqo). 원래180초marker판정뒤failure후속관측까지194.418초이며수락deadline은늘리지않았다. 전체로그/프로세스/Activity/UI가수집됐고마지막PID4639생존·UnityNative그래픽초기화·Activityresumed확인,Awake/Start/intent/SDK/init/HTTP는미도달관측. 실제Viewingfullscreen/Gotit의android소유UI와NativeFocusLost는새증거다. corrected detector true는원본을덮지않은별도재분석. OSguide정상ack뒤회복검증전원인완전확정/SDKPASS로기록하지않는다. controller는자기AVD PID94221만종료했고이후기기명령없음. UI조작응답대기중제품변경/동일재실행강행없음.

- 배치30 독립호환성검증: 기존iOS actualPASS sourced543556와현재HEAD의UnitySDK·iOSSource/CABI·iOS공급scenario·공통PiiProbe/link소스gitdiff0확인. 이증거의동일제품범위는유효하나이번새iOS실행으로표시하지않고무조건재실행하지않는다. AndroidUI응답대기동안새SDK제품변경/Push/JNI/전체Native/self9/Strict를선행조건없이강행하지않는다.

- 배치30 C/E 독립입력계약검증: framework android/SystemUI의고정Viewingfullscreen·정확히1개enabled Gotit·유효bounds만선택하는순수함수와음성4건PASS를추가했다. 다른app·권한prompt·중복/disabled/badgeometry는거부한다. 이코드는좌표식별만하며실제UI입력0,사용자응답전ACK를하지않는다. 변경하네스관련전체Python을검증하되조건미충족Push/JNI/CoreNative全/self9/Strict/제품refactor는아직미실행으로유지한다.

- 배치30 E 독립최종회귀: 변경harness관련전체Python185건/49모듈PASS/skip0(16.813초),startup10·정상안내선택4음성/정상unit포함. API/source/wire·staging147·manifest/meta·progress/actionlint/diffPASS. 현재UIACK방식응답대기로추가E2E/Push/JNI/CoreNative/Strict는NOT_RUN·T01/T02PARTIAL유지. C첫실패는마지막확인Nativeengine/graphics+PID/Activity와최초미확인Scene/Awake/Start로분리했고UI안내ACK/인과회복검증은미실행이다. 독립순수selector는좌표만식별해실제입력0이며CI에연결했다.

- 배치30 UI입력대기 체크포인트: 독립Python185·compile-only/API/staging검증은완료했으나정상OS안내ACK방식사용자응답전실제UI입력/추가C실행을하지않는다. 과거첫진단AVD는종료/원본보존,현재B30A GUI는idle. docs/evidence/p10-batch30-ui-handoff.md에사실/마지막확인단계/미측정/응답후최대1추가재검증과D/E순서를기록했다. 향후조건부코드변경이남아전체code/test최종commit후1회원격CI/push는아직시작하지않았다. 배치완료선언/사용자요청pause로오표기하지않는다.

- 사용자 명시요청 수신(2026-11-18 Asia/Seoul): “이 전용 AVD에 한해 ADB UI 입력으로 안내를 닫아줘”. CUA대체기술범위가이전용재검증AVD의정확한비구속Viewingfullscreen/Gotit ACK에한해허용됐다. 다른app/권한/설정/서버조작허용아님. 새source/APK/새전용AVD·기존동일SDKserver/양port를재검증하고허용된추가E2E최대1회만진행한다. before/after UI·tap1/foreground/조기marker·Backend/원장을실측하고원본첫FAIL은보존한다.

- 배치30 C 명시ACK구현/검증·커밋 전: --ack-known-fullscreen-notice는GUIreceipt/진단/소유바인딩이모두있는경로의명시옵션일때만작동한다. 실제freshXML의정상교육header·단일enabled Gotit/bounds만식별하고같은run guard를통해1회tap,전후XML/시간/exit·unattendedCI=false를기록한다. default입력0/권한·타app prompt입력0/단일정확serial좌표음성검증PASS. 실제UI입력은아직0이며허용된추가C검증을위해새B30B project/APK를생성한다. 기존첫FAIL·AVD·DB/로그보존,SDK제품/await/성공/timeout조건변경0.

- 배치30 C 추가재검증 시작: 사용자명시전용ADB UI ACK요청범위에서새GUI B30B APK(현재source/147/nonce/hash검증)·새AVD B30_START_B_20261118_ACK·5594/5595·현재동일UnitySDK server98843을확인했다. 기존A/B29AVD·설치app/DB보존. 아래controller에서소유PID/양port/이름/serial을실측한뒤명시ACK옵션의E2E를1회만수행한다. 정상교육안내이외tap/권한/설정/서버변경없으며원래180초/기존auth-purchase-PII-원장조건유지. 허용추가1회를이실행에서사용하며더반복하지않는다.

- 배치30 C 재검증 PASS/exit0: source6f813a79ffe2b8b932a7b562f326613950c7d7fc·GUI buildsource c07a264/APK f8f402fd. 새전용AVD에서정확한Viewing full screen 안내를사용자허용범위로1회tap(exit0,14.528s). 동일PID4479에서focus회복·안내소멸·Awake/Start/intent/SDK/init반환/auth진입관측,첫HTTP22.937s·완료27.976s·PII포함marker34·Backendauth/catalog/entitlements/verify/logout·원장1/delta100 PASS. 일반OS안내가이재현의managed진입을막았음은전후실측으로확인됐으나B29원본UI미수집때문에과거원인을소급확정하지않는다. 무인CI PASS아님/실Provider미검증. controller는자기PID99860만종료·AVD/DB/원본보존,첫진단FAIL도유지. 정제증거p10-batch30-android-e2e-b.json. D Core/duplicate·API/ABI/source대조를시작하고Push/JNI/Strict자동경로의미충족조건은별도평가한다.

- 배치30 D Core 검증 PASS/exit0(artifacts/core-assertions-vkyulm0x,source6f813a7): Kotlin10건/helper50,Swift12건/helper122,managed checker1/helper418(정상198/예상오류220),stress100samples/helper316. duplicate-only 변이 process134 1회감지·정상probe0·원본SHA복원·복원418/분기419확인. 새Editor/Player/실Provider회귀와구분한다. Push는현재GUIreceipt 미지원의자동batch빌드전용,JNI는새UTF8 APK/설치없는전용기기·정상안내조작조건이남아 NOT_RUN/DEFERRED_ENV. 이미확인된batch실패를반복하거나설치보존gate/사용자ACK범위를넓혀우회하지않는다. Strict의자동batch정상선행조건미충족으로실행0/DEFERRED_ENV,T01/T02PARTIAL유지. C결과commit전원장명령첫호출은잘못된scripts/check-progress.py 경로라exit2였고실제scripts/verify-progress.py로정정검증한다(실패숨김없음). API/ABI/최종Python 검증을계속한다.

- 배치30 E 검증 환경 정정: 최초 full Python은기본python3에jsonschema가없어module import1error/exit1(186loader항목)였다. 제품test실패가아니며원본final-python.log보존,이미준비된p01-schema-venv Python으로정확히같은suite를재실행한다. actionlint첫호출은PATH없음127,캐시binary 직접호출은기존custom self-hosted label 미등록오류1이므로기존허용label을명시한검증설정으로재검사한다(원본로그보존/워크플로우약화없음). 원장·API·manifest·meta·staging147검사는각exit0이다.

- 배치30 D/E 결과/커밋 직전: 정확한venv의전체Python187건/49모듈PASS/skip0(16.309초),원장·API/source/wire·manifest·metadata·staging147·명시custom runner label actionlint 각exit0. 최초기본Python import실패와actionlint PATH/label실패는원본보존. 79shipping SHA·3Java class선정javap·양iOSslice Cexport4개가배치26보존artifact와일치,현재GUI APK source/receipt/147/hash 재검증PASS(새Native빌드아님). 현재iOS보호소스는d543556 실제PASS와diff0(새iOS실행아님). Core/duplicate 결과와환경상미실행Push/JNI/Strict를정확히분리했으며T01/T02PARTIAL·제품refactor0유지. 최종정제문서/보안점검/FF인계·falseHosted1회를이어간다.

- 배치30 E 정제문서/커밋 전: 통합보고10항목·PROGRESS/WORK_LOG/USER_SETUP/FINAL_REPORT·source별JSON을현재결과로정리했다. 초기UI입력대기는사용자명시요청과실제1회ACK/PASS로해소됐으나과거이력보존. Push/JNI/Strict미완료·T01/T02PARTIAL/Provider13WAIT를명시하고재개조건을기록했다. 전체push범위scanner0/탐지0,이전범위1/기존SHA오탐2를독립재계산했고전체commit text/산출물제외·FFancestor·repo public/vars0/runners0확인. 명시stage/scan/commit뒤handoff FFpush·falseHosted1회수행한다.

- 배치30 E 최종stage검증/커밋 직전: 명시stage6개는정제Markdown/JSON뿐이며실제staged blob복사scan exit0/탐지0,원장/diff검사PASS. origin handoff와0behind/9ahead·FF가능확인. 원본로그/키/서명/license/생성물/미추적Demo·cache는stage하지않았다. 모든code/test는이미commit됐으며이문서commit후전체push범위재scan→handoff동일branch FFpush→변수정상응답재확인후Hosted false1회만수행한다.

- 배치30 E FFpush 확인/Hosted 시작: local/remote handoff HEAD a1cc004139193d175f6964cf11be7051f6e5b5f7 일치,origin2c8e7a7에서FFpush성공/exit0. 전체push범위secret실제exit0·탐지0,tracked clean·기존미추적3경로보존. 변수정상API exit0/vars0을다시확인했고모든code/test가원격source에포함됐다. release_validation=false Hosted-only 단1회를이source에서요청하며최종상태전PASS기록없음. 추가Unity/runner/Release활성화·main/force없음.

- 배치30 E Hosted dispatch1회수락: run44115202057/sourcea1cc004139193d175f6964cf11be7051f6e5b5f7,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44115202057 . 현재 in_progress 이며결과대기,추가dispatch/재실행/runner등록/Unity변수/Release없음.

- 배치30 E 원격관측: watch에서inventory-contracts SUCCESS/UnitySKIPPED를확인했으나전체run진행중job log조회gh exit1로아직공식Python합계재추출은미완료다. 원격결과를로컬187건으로대신채우지않고전체완료후로그를다시확인한다. 새dispatch/코드변경없음.

- 배치30 E 상태해석 보강: 전체SDK의기존BLOCKED_INTERNAL판정을최신보고에도명시했다. Push자동batch환경미충족과GUIreceipt확장미구현(내부후속작업)을구분하며후자를사용자인증대기로넘기지않는다. 이번범위의Android회복PASS로T01/T02나전체SDK를완료표기하지않는다. 원격은단일run최종결과대기이며추가실행없음.

- 배치30 E 원격로그 확인: 공식GitHub jobs/{id}/logs 직접조회exit0에서49module run/187Python건·FAILED요약0을재추출했다. 앞선gh run view 진행중archive조회exit1과구분한다. inventory/Backend SUCCESS,UnitySKIPPED,Android/Swift최종대기. 추가dispatch없음.

- 배치30 E 원격중간결과: Android-native·inventory-contracts·Backend-postgres 세job SUCCESS,UnitySKIPPED. Backend공식로그는TC local7/의도변이1(예상exit1)/정상복원1/sandbox2로총11executed tests·예상mutation failure1을확인했다. Swift synthetic Simulator host가진행중이며전체run/basic/Release판정은아직대기다. 원격Unity/전체Strict/실Provider로확대하지않는다.

- [P09-T07] 배치30 E 최종원격검증/문서커밋 전: run44115202057/sourcea1cc004139193d175f6964cf11be7051f6e5b5f7,false 단1회 SUCCESS. Hosted4/basic SUCCESS,Unity/ReleaseSKIPPED,공식Python49모듈187·Swift37(auth20포함)·TC11/의도변이1·정상복원확인. synthetic iOS host step/xcresultgatePASS이지만quietlog의정확test수UNMEASURED·Unity실행아님. 이후code/test변화0,최종정제보고/USER_SETUP/원장/로그만변경. T01/T02PARTIAL·전체BLOCKED_INTERNAL/P05FAIL/Provider13WAIT와미완료Push/JNI/Strict조건을유지한다. 최종stage scan/원장·diff확인→문서commit/동일handoff FFpush/HEAD일치와기존미추적3경로보존을검증한다. 추가dispatch없음.

- 배치30 E 최종stage검증/커밋 직전: 명시7개문서blob text/JSONparse·원장64행·diff검사PASS,staged offline gitleaks 실제exit0/탐지0. Hosted 이후harness/test/SDK/workflow/baseline변화0,실제완료run과미실행scope·내부후속구현을분리했다. 최종문서commit뒤전체이번push범위scan·handoff FF가능성/remoteHEAD·tracked clean·초기미추적3경로보존을실제조회한다. 추가CI/Player/Provider/Release실행없음.

- [P10-T01] 배치31 A/B/C 시작: 지시문·AGENTS/START_HERE·계획0~4와배치30결과/현재handoff HEAD089f1a8/기존미추적3경로확인. 구매PII Player PASS와원본FAIL·단일AVD ACK범위를고정한다. Push는자동batch전용이며GUIreceipt미지원,UTF8개별E2E는GUI지원하지만R09 wrapper가전달하지않고Android실패시iOS판정도없다는공백확인. 원본Builder·현재147/staging/cache·source/nonce/receipt/hash·매ADB소유가드를재사용해명시GUI입력을추가하고defaultbatch/fallback·기존DB/Proxy/Player판정은유지한다. 새AVD안내ACK는기존허가를확대하지않으며실제새안내가관측되면해당UI입력만보류한다. 아직새실제빌드/Player/Strict/제품refactor/원격작업NOT_RUN.

- 배치31 B/C 입력계약 구현/검증·커밋 전: GUI preparer에push variant/LateCallbackProbe/link를추가하고shared loader가주/보조scenario·147package/cache·receipt/APK/source/nonce를동일검사한다. Push명시GUI 경로는batch를호출하지않고기존Backend/Proxy/DB/Player전체본문을실행하며동일SDKserver/AVDPID·양port가드를매ADB전유지한다. wrapper기본both/CLI는그대로이고platform명시별실행·R09 GUI전달/필수UTF8 marker/probe·현재clean원장검사·Android/iOS독립결과와소유Simulator만shutdown을추가했다. 새GUI 계약fixtures/기존GUI36건PASS/skip0(exit0),누락aux/변조APK·다른scenario/오래된receipt/source·invalidGUI의ADB/Backend전거부/별도platform실행을검증했고CI에연결했다. 아직실제새GUI컴파일/APK/Player는NOT_RUN,ACK자동확대0·SDK제품변경0. commit후각새GUI project에서원본Builder를실제로실행한다.

- 배치31 B/D 신규환경블로커: CUA에서Hub3.22.6 파일선택창이GoTo경로를수락하지않고초기화해다른근거(정확한path/자동완성/AX메뉴)로확인후정상Quit했다. 재시작에서설치된Hub가4.0.1로바뀌었고Unity Hub Software License Terms 화면(Disagree/Agree disabled)이새로표시됐다. 에이전트가update/install/약관동의/계정/라이선스설정변경을요청한것아니며기존환경의재시작후새화면관측이다. 새법적약관동의는CUA정책상행동시점명시확인필수라진행하지않았다. 새GUI Push/UTF8 project는준비됐지만컴파일/APK/Player아직NOT_RUN. 해당GUI입력만사용자확인대기로두고음성fixture/구조적검사·Core/source/ABI 등독립작업계속. 약관차단을CLI/저장설정조작으로우회하지않는다.

- 배치31 B/C/F 독립검증 시작: 새GUI 양variant의엄격입력fixture36PASS뒤실제Push명시GUI분기가기존Backend build에도달하며batch fallback0임을검증하는경계case를추가했다(현재GUI37PASS/skip0). R09 malformed/非object·bool원장거부와iOS timeout의소유기기shutdown을확인했다. 새Hub약관확인은pending이며동의/우회/새기기UI조작없음. 제품코드는변경0,Core/duplicate·현재source/선정ABI와변경완료후전체Python 단1회를지금수행한다. 새APKs/실제Push/JNI Player/Strict는NOT_RUN이다.

- 배치31 F 독립결과/커밋 전: full Python202건/51모듈PASS/skip0(16.704초,최종code변경뒤1회),GUI37경계unitPASS. Core artifacts/core-assertions-pq_thtsw exit0:Kotlin10/helper50,Swift12/helper122,managed418(198정상/220예상오류),stress100/helper316,duplicate-only process134감지1·정상probe0·원본hash복원/418·분기419. 실행시harness/test/doc미커밋변경이있었고SDK79shipping SHA는전후동일임을분리기록. API/manifest/meta/staging147/actionlint/progress각0·선정javap3class/Cexport양slice4개동일. iOS구매PII d543556·독립CABI d86ccc2와보호source diff0인반면,과거iOSUnityPush e46cb65와는RequestRegistry.cs변경1개가남아current Push검증을승계하지않는다. 따라서새Android뿐아니라current iOSPush/Strict도미완료로T01/T02PARTIAL·제품개선보류. 새HubEULA입력은pending/GUI APK0/Player0이며해당경계외검증완료. 보완code/정제JSON·문서만별도commit한다.

- 배치31 F 블로커/수정前: R09의실패·누락계약최종검토에서iOS xcresult JSON이object아닌배열일때AttributeError로result.json판정저장이중단되는내부하네스결함을신규fixture로재현했다(9unit중error1/exit1, r09-malformed-before.log). 실제iOS test실행실패나약관동의가아니며소유Simulator shutdown은finally에서수행됐다. 잘못된summary형식을명시FAIL/정확code로기록하도록최소보강하고음성복구검증후,코드변경이있으므로전체Python을최종source에서재검증한다. 이전202PASS는그실행당시의결과로보존하며약관UI대기는계속pending이다.

- 배치31 F R09 오류수정 검증/커밋 전: xcresult summary는JSONobject 및passed/failed/skipped integer를명시검증하며잘못된형식을IOS_RESULT_UNAVAILABLE/FAIL로저장하고소유기기shutdown을유지한다. 기존재현error1을보존했고GUI38unit PASS/skip0,전체Python203건/51모듈PASS/skip0(17.370초,code수정후재검증)로복구확인. 이전202건성공은수정전별도증거다. Core/Native shipping/ABI는변화없어반복하지않는다. Hub4.0.1새약관화면은읽기전용재확인에서도남아있고사용자직접동의/명시허용은아직없다. GUI컴파일/APK/각새AVD실행은보류하고독립검증·인계만진행,새terms회피/이전ACK확대/실Provider/Strict실행0. 전체code/test를이commit으로확정하고통합문서·scan/FF인계와Hosted false1회를수행한다.

- 배치31 F 통합문서/커밋 전: A~F/최종보고11항목·source별JSON·이전배치30연결·USER_SETUP/FINAL_REPORT를갱신했다. GUI입력구현/fixture검증과실제미실행·새Hub약관동의대기를명확히분리했다. 공식CLI project등록2개각0/launch0,현재5037read-only listener0/ADB명령0도기록. 최종Python203/GUI38·Core/API/ABI/stagingPASS,새미형식summary오류재현/복구와과거iOSPush current-gap유지. 모든code/test commit완료,새range scan0/탐지0·기존history1/정확sourcehash오탐2보존. 명시stage scan·원장검사뒤handoff FFpush/vars정상0재확인/falseHosted1회만수행한다. 약관승인pending의존GUI단계는강행하지않는다.

- 배치31 F stage검증/커밋 직전: 명시7개정제문서text/JSONparse·원장/diff PASS,실제staged blob scan0/탐지0. origin handoff0behind/3ahead·FFancestor확인. 키/서명/license/rawlog/DB/APK/Library/Temp/Xcode생성물·미추적Demo/cache는stage하지않았다. 이문서commit뒤전체이번range재scan/FFpush→코드source원격일치/vars0정상응답확인→release_validation=false Hosted단1회. 새Hub약관/실제GUI·Player pending을CI통과로대체하지않는다.

- 배치31 F FFpush 확인/Hosted 시작: local/remote handoff HEAD5af3aff08686d330d107bee2bb6482c7e6ed1383 일치,origin089f1a8→5af3aff FFpush exit0. 모든code/test포함·전체이번range scan0/탐지0·생성물0·tracked clean/초기미추적3경로보존. vars정상API exit0/total0재확인. release_validation=false Hosted-only 단1회를이source에서요청하며결과전PASS표기없음. 새약관입력pending·실제GUI/Player/Strict는미실행으로유지하고추가실행/약관동의/runner등록/Release없음.

- 배치31 F Hosted dispatch1회수락: run44126492891/source5af3aff08686d330d107bee2bb6482c7e6ed1383,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44126492891 . 현재진행상태최종대기이며새동의/Player/추가dispatch/재실행/Unity활성변수/runner/Release없음.

- 배치31 F 원장정합성: 과거Android구매PII timeout의존성은배치30같은scope신규PASS로RESOLVED 처리하되원본FAIL/과거원인미확정은보존했다. 새환경ENV-HUB-NEW-TERMS와현Player영향DEP-P10-PLAYER-IMPACT를원장에등록하고T01은여전히PARTIAL. 기존자동IPC블로커를자동batch/Strict범위로명시해GUI제품성공과혼동하지않는다. 64Task의구현/검증집계변화없음. Hosted run44126492891/source5af3aff 진행결과대기,추가dispatch없음.

- 배치31 F 문서검사 정정: 새블로커행삽입의첫문자열치환이P09-T07 Task행마지막셀을먼저매치해원장parser가expected six fields를검출했다(문서오류,제품test아님). 정확한blocker table행앵커로복구했고기존64Task행/집계는그대로다. 다시원장검사하며코드/test/CI source변화없음.

- 배치31 F 원격중간검증: run44126492891 inventory-contracts SUCCESS/UnitySKIPPED. 공식jobs/logs API exit0에서Python51모듈203건·FAILED요약0·신규GUI/R09모듈연결을재추출했다. Backend/Android진행·macOS Swift queued로전체결과는대기,추가dispatch/runner활성화없음. 원장문서앵커수정후검사PASS/64행집계보존·이후코드변경0.

- 배치31 F CI진행중추가결함 재현: 새iOS독립runner가생성UUID를canonical소문자로만들지만simctl list의대문자UUID와직접비교해already-Shutdown exit149를cleanup실패로오판하는경계결함을10unit중failure1/exit1로재현(r09-uppercase-before.log). 다른기기조작이나실제XCTest실패가아니다. UUID비교만대소문자무관하게고치고회귀를추가한다. 이추가code/test는이미요청한단일Hosted source5af3aff에포함되지않으므로원격203건결과와최종로컬검증을구분하며,1회제약을지켜추가dispatch/재실행은하지않는다. 마지막후속수정의Hosted검증미완료를최종보고에명시한다.

- 배치31 F UUID수정 결과/커밋 전: 실제형식의대문자simctl UUID fixture로재현한cleanup오판을비교1곳casefold로수정했고GUI39unit/최종Python204건·51모듈PASS/skip0(17.796초)확인. 이후Hosted source5af3aff(203건)와추가수정의범위를명시하고추가dispatch0유지. 사용자응답은“직접 약관 확인·동의 후 알려줄게”로,동의완료나에이전트동의허용이아니라직접처리예정임을기록한다. 해당GUI는계속보류하며사용자조작에간섭하지않는다. 독립적으로변경된R09 iOS runner를새소유18.6Simulator에서1회실행해C ABI/XCTest/cleanup을실측한다(새UnityPlayer아님). codecommit후실행하며기존Simulator/DB는보존한다.

- 배치31 C 독립iOS 실제시도1 FAIL: source7e07c70,artifacts/r09-utf8-5lb0vxs3,wrapper1/childxcodebuild70. 생성UUID를소문자로정규화해전달한destination id를Xcode가매치하지못했고available목록에는같은소유UUID대문자형이실제존재했다. XCTest실행전destination선택실패로tests0/NOT_RUN이며SDKtestcase실패로치환하지않는다. 자기Simulator만shutdown149후조회Shutdown확인/디스크보존,타기기조작0. 원본available목록은private로그에만보존한다. simctl이반환한정확한UUID표기를명령에유지하고비교시에만casefold하는최소수정+destination인자음성검증뒤새소유기기로근거있는재검증1회를진행한다. 이후수정은원격CI source밖임을계속명시한다.

- 배치31 C destination수정 검증/커밋 직전: UUID유효성만검사하고simctl원문UUID를Xcode/기기명령에그대로전달하며조회비교만양쪽소문자로수행하도록수정했다. 대문자destination인자보존·alreadyShutdown149확인포함GUI39unit PASS/skip0. 최초실제70/시험0을보존했고SDK/승인/timeout변경없음. commit된새source에서신규Simulator1회재검증후최종Python을현재source로검증한다. 사용자약관직접처리완료메시지는아직대기중이며Hub에입력하지않는다.

- 배치31 C 실제독립iOS 재검증 PASS: sourcea812cddc0215dcaf3e340dfc0308f89d2830dac1 tracked-clean,artifacts/r09-utf8-70ipi4ww,wrapper/child exit0. 새전용18.6Simulator CAAD6B11-E8E7-4E5F-A3F2-8CC0A2413CB4와xcresult실제deviceId일치·CBridge testHostPushEventRoutingAndDedup1건(한글/emoji UTF8 bytes·callback/event·중복route)PASS/failure0/skip0. 자기기기shutdown149뒤list의Shutdown을casefold비교로확인했고두시도디스크/기존Simulator보존. 첫source7e07의destination70/시험0FAIL은정제증거와원본으로보존. AndroidJNI/UnityiOSPlayer 실행아님. 실제runner수정이완료됐으므로current source에서fullPython을최종재검증하며이후Hosted source5af와의변경2파일/추가검증미완료를명시한다. 약관직접처리완료메시지는아직대기.

- [P09-T07/P10-T01] 배치31 F 최종결과/문서커밋 전: run44126492891/source5af3aff08686d330d107bee2bb6482c7e6ed1383,false 단1회SUCCESS(Hosted4/basicSUCCESS,Unity/ReleaseSKIPPED),공식Python203/Swift37/TC11·변이1확인. CI요청뒤UUID후속2commit은포함되지않아최종code전체원격검증이라고기록하지않는다. sourcea812cdd최종localPython204/GUI39·새iOSCABI1실제PASS/ownedcleanup확인,최초destination70/시험0FAIL보존. 사용자직접약관처리완료통지는대기·GUI/APK/Android Player/Strict0/T01T02PARTIAL유지. code후속diff2파일과정제모든scope·원장복구/64집계를문서로정리했고stage scan/commit/동일handoffFFpush/HEAD일치·초기미추적3경로보존을확인한다. 추가CI/약관동의/main/force/Release없음.

- 배치31 F 최종stage검증/커밋 직전: 명시9개문서는text/JSONparse·원장64행·diff PASS,staged scanner실제exit0/탐지0. 최종sourcea812cdd local204/실제CABI1과Hosted source5af3aff203건SUCCESS의범위를구분했고후속2파일의원격미검증을명시했다. 두실제시도/실패0tests·성공1test/ownedcleanup·사용자직접약관완료대기·현재GUI미실행/Strict0/T01T02PARTIAL을보존한다. 문서commit후전체이번range scan·freshfetch/FF확인/동일handoffpush·localremoteHEAD/초기미추적3경로보존을조회한다. 추가dispatch/약관동의/사용자조작간섭없음.

- [P10-T01/P10-T02] 배치32 A 시작: 지시문A~J·AGENTS/START_HERE·계획계약/마지막원장·배치31/책임감사27·현재HEAD3639a1d/동일handoff/초기미추적3경로확인. 사용자는일반권장설정과추가실행권한을위임했다. 새법적약관은기존직접처리완료미통지상태라동의/우회하지않고현재UI를확인한다. GUI의존단계대기시에도Task32명시범위에따라격리local branch D1/D2제품후보baseline/실제구현/회귀·E사전계측·F분리패키징·G/P11사전감사·H검증을진행한다. 후보제품은T01PARTIAL이면handoff에통합/push하지않는다. 원격CI는배치31 UUID후속수정을포함한모든최종handoff code/test정리뒤1회만수행한다. 기존P05FAIL/Provider13WAIT/Strict·self-hosted미검증/사용자기기·DB·license보존.

- 배치32 A/B 환경확인: CUA에서Hub4.0.1은새약관화면대신정상Projects와등록된두소유project를실제로보여준다. 에이전트약관동의0/우회0이며현재동의버튼조작이필요없음을확인해GUI개발을이어간다. Stage147/source/Builder/scenario/LateCallback/link/cache·source8aadancestor/보호경로diff0/출력미존재를재검증PASS. Hub의두project Editor선택이비어있어설치된6000.5.8f1을명시한뒤새GUI빌드부터실행한다. 이미승인된기술적설정과일반권한은재질문하지않는다.

- [P10-T02] 배치32 D 격리후보 시작: T01은현재PARTIAL이므로Task32명시허용에따라candidate/p10-t02-batch32-20261118 worktree(기준3639a1d)를생성했다. handoff의Native제품파일은변경하지않고후보별기존Kotlin18/Swift20 baseline→내부codec/grantdecode분리→동일회귀/음성/API검사→각localcommit으로보존한다. T01PASS전handoff통합/push없음. A/B GUI Push빌드는소유project에서기존Builder실행중이며후보baseline은독립적으로진행한다.

- 배치32 B1 검증/후보D baseline: PushGUI기존 Builder실제PASS,nonceac3018583bfa47cca483c96521536726/source8aadcf4/147files/APK27074492bytes/SHA97a2e42a76f71c72aae68769c4574787562f18ef263fab77e46d72ab333bc648. strictreceipt/current-source/cache/주·보조scenario·hash검사PASS(tests0/check1/Player0). 격리candidate baseline은KotlinGoogleAuthProvider18/SwiftAppleAuthProvider20·실패skip0/각exit0,보고서/hash/원본XML보존. 실제개선은각후보branch에서만진행하고handoff제품변경0유지. 다음UTF8GUI와B3iOSPush GUI입력구현/음성검증을계속한다.

- 배치32 B3 구현 시작: 기존iOSPush는batch export만지원하고cleanup에서소유Simulator종료가없어,새GUI push variant/보조소스·strict export receipt를명시입력으로추가한다. 기존원본Builder/실제Xcodead-hoc Simulator build·Backend/Proxy·모든marker·token0판정은유지한다. GUI실패→CLI fallback0,잘못된receipt는Xcode/DB/기기전거부,새로생성한자기Simulator만종료/상태확인한다. helper C# Builder/SDK제품은수정하지않고기존공급scene를재사용한다. UTF8 GUI는별도소유project로전환/컴파일중이다.

- 배치32 B3 입력시험 최초결과: GUI43unit중새iOS positive fixture1건이macOS /var→/private/var canonical path 비교불일치로실패(exit1). 실제validator는소유export를정규화해올바르게반환했고fixture의기대path만.resolve가빠졌다. validator/판정조건은변경하지않고기대경로를정규화해재확인한다. 기존42건은PASS이며원본로그보존. UTF8실제GUI APK는별도로PASS/27073808bytes/SHA0a4a8b1b5e2319eccf21a4eadfd2a26a15279110e6e826900fc759d478aa23ac,147/receipt/source관계통과·JNI실행은아직NOT_RUN이다.

- 배치32 A/B3 검증/커밋 전: 두Android실제GUI APK(Push/UTF8)·147/cache/source/receipt검증PASS·Player미실행과iOSPush새명시export입력/보조소스/트리hash/기기cleanup fixture43PASS를분리했다. 최초fixture경로1실패는기대값정규화로복구/validator변경0. 잘못된export의Xcode/DB/Simulator/batch전 거부와자기UUID/이름/Shutdown확인검증추가,CI연결했다. Hub는정상Projects/Editor실행상태로약관버튼조작없이진행했다. 후보D1제품은격리local e6e1de7(기존18+추가2/API PASS)로handoff미통합. handoff제품/원장/지급·finish정책변경0,이harnesscommit뒤새iOSPush GUI project를준비한다.

- 배치32 B4 새전용기기 준비/정상안내 범위: 사용자최신“추가권한전부승인/권장안자율진행”을이번배치의새소유GameBridge 테스트AVD에한정해적용한다. 정확한android/SystemUI Viewingfull screen/Gotit교육안내만기존strict selector·매호출PID/양port/동일SDKserver가드의명시옵션으로각최대1회닫는다. 배치30의과거허가를재사용한것아니며계정/permission/법적약관/보안설정/타기기조작은포함하지않는다. Push도기존동일Collector의명시GUI+진단옵션에서만이ACK를지원하고기본입력0을유지한다. 해당보완의범위음성unit후commit된source로각새AVD검증을시작한다.

- 배치32 B4 검증/실행 직전: 정상안내ACK입력범위8unit PASS/skip0. 현재5037은Unity6000.5.8f1 SDK adb PID31840 하나임을read-only확인했고local Docker unix context/Postgres gamebridge-sdk-local-postgres-1 healthy. 기존server기동/종료명령0·타기기조작0. 소유UTF8Editor는idle로유지해server변경을피한다. 새GameBridge_V2_B32_PUSH_A_20261118/5596·5597,UTF8_A/5598·5599를각따로생성하고매명령소유가드를입증한경우에만검증한다. 원래marker/DB/Proxy/timeout판정을유지하며새명시교육안내option만전달한다. 이commit후tracked-clean에서Push부터실행한다.

- 배치32 B1 최초기기준비/진입FAIL: 새AVD A의소유PID34033/5596·5597/이름guard·boot통과후상위Push wrapper가새ACK옵션을미전달/미인식해argparse exit2로중단했다. Player/Backend/설치/ACK까지도달0이며SDKtest실패아님(내부CLI연결누락). 자기emulator만finally종료·AVD보존. 상위wrapper에도명시옵션검증/전달과CLI연결음성을추가하고새source commit후새B AVD에서첫실제Player시험을진행한다. 동일실패무조건재시도/기존AVD재사용없음.

- 배치32 B1 CLI연결수정 검증/커밋 전: 상위Push wrapper가명시ACK옵션을파싱하고GUI/owned binding이있을때만Android자식에전달하도록보강,default입력0/다른platform승계0 유지. 관련GUI45unit PASS/skip0. 원본A는argparse2/Player0으로보존했고새B controller는별도로그/AVD명으로준비했다. 동일현재server31840과원본APK/receipt를검증한tracked-clean source에서첫실제Push를수행한다. 진행중에는primary source를동결하고격리candidate만독립작업한다.

- 배치32 B1 실제Push B FAIL/exit1(source48dc7de,artifacts/unity-android-push-ihs2a2a8): initialize/login/register·수신1/중복main-thread·BG/FG markerPASS뒤network InvalidOperationException. WAIT_OFFLINE→FAIL90.023초·reconnected marker0이기존90초RECONNECT_TIMEOUT분기와일치하나메시지는로그에없어추론으로명시한다. reconnect거절2관측,logout/session/최종token0은미실행. 정상교육안내는child동일가드로1회ACK(exit0,41.497초). raw controller uiInputs0은controller직접입력0이었고childACK1/HOME와구분표기하도록후속controller수정,원본은보존. 종료뒤추가read-onlyADB진단은소유가드가EMULATOR_BINDING_UNAVAILABLE로subprocess전 거부했고실제추가ADB0. 모든AVD/DB/log보존. GUIguard와legacyidentity가같은명령에서중복증명을여러번해임계창을소모할수있음을발견했다. GUI는매실제명령직전동일강도GuiAdbGuard만사용하고legacy경로를유지하며,고정18초fault대기를기존요구조건거절>=1관측시반환(상한18유지)으로바꾼다. 성공assertion/앱90초/대기상한증가없음. 안전/시간trace 음성검증뒤다른신규기기에서검증한다.

- 배치32 B1 timing/guard 검증·커밋 전: 새5unit은GUI모드에서도매명령GuiAdbGuard가server변경을subprocess전 거부하고legacy명령은종전PID/identity증명을유지함을확인했다. 거절관측대기는첫failure관측시즉시반환/미관측시종전18초상한/기존거절시추가sleep0을검증했다. 앱90초·host22초reconnect·성공marker/DB조건은변경없음. command category/소요시간만secret없는trace로저장하고실패시marker도보존,실제launch상태필드를정확히갱신한다. 기존B failure는유지하고먼저독립UTF8 JNI를새AVD에서검증한다. sourcecommit후tracked-clean 시작,기존소유UTF8Editor/server유지.

- 배치32 B2 첫준비경로도상위R09 wrapper의ACK옵션미인식argparse2로Player/Backend/설치전 중단됐다(UTF8_A PID42438/5598·5599소유/boot는확인,실제JNI0·controller종료/데이터보존). B1과동일계열의입력연결누락이별도wrapper에남았음을확인했다. R09에도조건부명시전달을연결하고두상위wrapper parser를노출해privatecontroller가AVD생성전 정확한인자계약을검사하도록보강한다. source/조건검증unit후새기기첫실제JNI를실행,timeout증가/기존성공AVD재사용없음.

- 배치32 B2 CLI계약修復/커밋 전: R09상위parser/명령생성에명시ACK+GUI+진단필수조건을연결했고,Push/R09모두argument_parser를통해기기없이정확한인자검증이가능해졌다. GUI46unit PASS/skip0. 새controller는AVD생성전 실제wrapper parser와명령구성을검사한뒤에만기동한다. A준비실패는원본/설치0/실JNI0으로유지,새B에서첫실제JNI를진행한다. Native후보넓은회귀47Android/43Swift도모두PASS이며미통합상태보존.

- 배치32 B2 실제JNI PASS/exit0(sourceb6bd767): 새UTF8_B PID44685/serial5598/5598·5599 및sameSDKserver31840가드·정상교육안내1회ACK/원본GUIAPK0a4a8b1b...·필수GB_UTF8_JNI_ROUNDTRIP와전체mock callback/Backend/SQL원장1/delta100통과(artifacts/unity-android-e2e-oqkoqd_3,R09wrapperajz6mwxj). tracked-clean 시작·child실제PASS/Android만실행/새 iOS실행아님. controller는자기AVD만종료·disk/DB/log보존. 최초UTF8_A argv2/Player0은유지. 다음새Push_C에동일원본APK/새harness source/명령timing추적·重複proof제거/거절조건동기를적용해근거있는재검증한다. iOSPush GUI project는준비/등록돼있으며Android서버변경을피해그실행후Editor전환한다.

- [P10-T03] 배치32 E 사전계측 구현 시작: 현재Push 자식은GUI입력을읽은단계(초기HEAD/clean메타데이터수집뒤)이며이후primary변경은관련없은새계측파일/문서뿐이다. 기존Core/Player성공판정은변경하지않는다. 독립.NET Release fake transport/실제RequestRegistry와새격리LOCAL_MOCK HTTP/DB의warmup20·measurement100·p50/p95/max/잔존수·멱등충돌계측을구현한다. 실제실행은빌드/Player부하종료후로분리하고T02정식완료전 사전계측으로표시한다. Native memory/UI jank/Unity startup은NOT_RUN이며기존100samples/316helper를성능시간으로대체하지않는다.

- 배치32 B1 실제재검증C PASS/exit0(source1ec45b9,artifacts/unity-android-push-bwjh5gqj): 새PUSH_C PID46481/5596·5597/sameSDKserver31840·원본GUIAPK97a2e42a...의같은SDK/90초조건에서전체6필수Push marker·dedup/mainthread/BG-FG/network/reconnect실패/session/latecallback·최종DBtoken0통과. 정상교육안내child1회ACK/코드source초기clean,실행중추가는새계측파일/문서뿐이었고관련소스동결. 소유controller종료·모든기기/DB/로그보존. B의network90초FAIL/부분PASS와A/UTF8_A의argv2/Player0은삭제하지않는다. 중복legacyproof제거+거절관측동기화조합으로회복했으며어느한항목만단독원인이라고단정하지않는다. 두Android검증종료후소유UTF8Editor만정상Quit해신규iOSPush GUI export로전환한다.

- 배치32 B3 실제GUI export PASS/실행 직전: sourcebf10f53/nonce9312d8c3e3f442f38d468eefc18323e1,원본Builder/147SDK/cache·3076exportfiles/트리SHA240382641e18305287cdf61ffb7d3ff6e7480436b5acb9fb7ca88e5431496eb0/PBX·주/보조source strict입력통과. tests0/check1/Player0와분리해이commit뒤명시GUI입력으로Xcode ad-hoc build·새owned18.6Simulator/새DB의원래Push/Proxy/6marker/token0검사를1회수행한다. UI약관조작0/기존기기재사용0·독립NativeCABI만으로UnityPush통과처리없음.

- 배치32 B3 실제현재iOSPush PASS/exit0(source01892c8,artifacts/unity-ios-push-rb4s3i0g): strictGUIexport/현재C#Registry·Xcodead-hoc build·새18.6Simulator/DB에서전체 6필수marker(dedup/mainthread/BG-FG/localtransport network-recovery/reconnect실패/session/latecallback)·token0통과. 자기Simulator shutdown/state/name/UUID확인및원본disk/DB/log보존. 원격APNs/실기기/OS전체network단절로기록하지않는다. AndroidJNI/Push새 PASS와같은제품source 관계를확보했으므로계획T01명시완료(API/기존동작/관련회귀·전후증거)와추가통합/Strict/Release조건을분리재평가한다. 当전 Core/API/원장확인뒤에만T01상태변경/후보formal통합을검토한다. Strict는자동batch/전용환경미확인으로0/DEFERRED_ENV이며SDK전체BLOCKED_INTERNAL/P05FAIL등은유지.

- 배치32 E 계측도구검증/커밋 전: 새독립.NET Release probe가warmup20와100측정을분리하고실제Stopwatch값으로create/init·callback제품조회·shutdown/dispose·8inflight/duplicate/cancel/late응답·pending/weakref잔존을계측한다. 별도localHTTP/PG probe는catalog/동일멱등키반복/409충돌100개씩과원장1·100을검사한다. rawsample없는숫자/316helper선언/위조p95·나쁜clock/build/남은pending을거부하는4unit PASS. source/time/build/OS를보존하고realStore/Unity성능주장없음. 모든agent Nativebuild/Player가끝나고소유Editoridle인현재commit된source로최초실측하며사용자프로세스는중단하지않는다. 후보packaging/Native47·43은완료/보존,측정은T03사전증거다.

- 배치32 E 최초실측 aggregateFAIL(source4793bc4,performance-local-0t0528ka): managed는Release/Stopwatch/warmup20+100각측정·pending/live0으로실제PASS. Backend는catalog120/200과초회verify1/200까지도달했으나기존WalletSnapshot.coinBalance가JSON문자열인데driver가숫자100으로비교해ValueError로중단했다. 제품/원장장애아닌계측harness계약오독으로Backend전체PASS가아니다. 원본보존·정확한문자열100비교/음성fixture추가. 이미유효한managed실측은별도artifact로보존·반복하지않고명시backend-only 새측정/새DB로재확인한다. source/시간/범위혼동없음.

- 배치32 E backend계약수정 검증/커밋 전: WalletSnapshot의정확한문자열100/같은purchaseID와숫자·bool·잘못된문자열거부5unit PASS. Driver는측정scope별PARTIAL/실패code를보존하고backend-only를명시해이전managed실측을새실행으로재표시하지않는다. 제품API/샘플수/warmup/원장조건변경0. 기존managed p50/p95/max는원본4793source에서유효하고이번반복은수정된Backend부분만새DB에서실행한다.

- 배치32 E 검증/P09의존 self9 시작: 원본4793의managed실측은warmup20+100각Release/Stopwatch로PASS·pending/live0,수정eff5의Backend-only 새측정도catalog/동일멱등키/409충돌 각100(+warmup20)·원장1/delta100 PASS/exit0(performance-local-jn_wziif). JSON문자열수량오독의첫aggregateFAIL은보존,이미유효한managed는반복0/별도source로분리했다. Core-current10/12/helpers50·122/managed418/복원·변이134·stress100/316도PASS. T01명시조건최종판정에앞서현재하네스의P09-T08 self-only 필수9개를새격리DB/role로검증한다. 전체Strict/새Simulator/Player를호출하지않으며사용자DB보존.

- 배치32 C 판정/커밋 전: DEVELOPMENT_PLAN 명시Core완료(API baseline·관련회귀·취소/late semantics·전후소스/결과)와Task32가구분한추가전체Strict/Release를대조해T01 IMPLEMENTED/로컬PASS로판정. 기존79file기존 Coreguard·P08API·現Core10/12/418/변이복원·신규AndroidJNI/Push·현재iOSPush·유효기존구매PII/CABI·現self9전체 PASS 근거를decision문서에연결했다. 64Task그대로구현23/진행41·localPASS21/FAIL1/PARTIAL42; P05FAIL/Strict0·ENV/Provider13WAIT/SDK BLOCKED_INTERNAL유지. 의존을우회하지않고이closing commit을고정한뒤검증된Native후보를정식T02로통합한다. 기존Core baseline변경0/후속phase정확4파일전이검사를추가해검증약화없이CI를유지한다.

- [P10-T02] 배치32 D1 정식통합 시작: T01 closing4485b2f로명시제품조건PASS판정후격리후보e6e1de7의정확한Kotlin2제품파일/추가test2를handoff에반영했다. 전후bytehash를p10-feature-batch32 전이기준으로고정하며원본Core기준은변경하지않는다. 기존18baseline동일소스+후보20/넓은47증거와별개로현재handoff에서18+2를동일명령재실행한다. 저장순서/refresh·cancel·tombstone/공개API/정책변경없음. Swift후보는다음별도정식commit이며로컬branch21b5f71은보존한다.

- [P10-T02] 배치32 D2 정식통합 준비: T01PASS조건에따라후보fc3da2f의Swift순수decoder/기존sink위임·추가3test를정확한동일bytes로handoff에반영했다. 기존 attemptId/auth closure/account검사·retry/late result/acceptGrant/finish/journal위치는변경없다. 현재handoff의기존20+신규3를동일명령검증하며D1과D2는별도commit으로보존한다. 모든변경뒤새Core종결＋Native exact4파일전이검사(기존 baseline hash고정/나머지Core·wire불변)와fresh패키징/영향E2E를수행한다.

- 배치32 D1 정식검증/커밋 전: handoff의기존GoogleAuthProvider18+codec2=20건·failure/error/skip0/Gradle0. candidatee6e1de7와제품bytes동일·기존storage/profile/save/operation401/refresh/cancel/logout/tombstone/사전거부의미보존. 전후baseline183639근거와현재20을구분한다. 이commit은Kotlin제품3파일만정식통합하며Swift와전이검사/CI연결은다음별도commit이다. 기존Corebaseline덮어쓰기없음,T01closing4485고정·전체SDK/ReleasePASS아님.

- 배치32 D2/전이검사 검증·커밋 전: handoff AppleAuthProvider20+GrantDecoder3=23 PASS/failure/skip0/Swift0,후보fc3da2f와제품bytes동일. attempt/auth/account/idempotency/late grant/finish/journal·공개API변경0. 원본Coreguard는closed4485 Git tree에서그대로PASS하고현재tree는정확승인Native4파일hash/추가2개파일집합·나머지Core/Native/wire byte불변·Cexports불변을확인했다. 전이checker8unit이Coreprivate/Wire/승인Native의추가drift·잘못된preimage/경로·元baselinehash변경·존재하지않는closedref를거부한다. 元baseline파일변경0/기존Core검사unit유지,CIinventory fullhistory와새phase체인·신규Native2/3 test필수연결. E1/E2각formalcommit후현재SDKfresh패키지/소비·회귀/모의구매PII를검증한다.

- [P10-T04] 배치32 F handoff신규빌드 시작: 정식D1/D2 Native sourceff2d0d5를기준으로이제handoff자체에서새Maven3모듈/AAR/sample/별도R8와새XCFramework device/sim을artifacts/batch32/handoff/...에생성한다. candidate산출물은사전검증으로보존할뿐새handoff빌드성공근거로대체하지않는다. 원본version/API·C ABI 유지·checksum/Swift module/소비자검증뒤그새staging으로post-T02 구매PII신규GUI소비를수행한다. T03사전계측/Native profiling·전체Release미완료로T04전체PARTIAL유지.

- 배치32 신규환경블로커: 완료된소유iOS Editor를GUI로전환하려는CUA조회가“The Mac is locked and automatic unlock could not unlock it; unlock manually”를반환했다. 잠금해제/비밀번호입력/우회는진행하지않고사용자수동해제만요청한다. GUI후속새package소비2건은보류,이미검증한T01/Native후보/정식단위/신규handoff Nativebuild·소비/147staging은분리유지. 문서감사/CLI계약/일반headless검증/scan 등독립작업은계속한다. T02와T04최종플랫폼검증은미실행으로정확히남기며Stage모두PASS로변경하지않는다.

- 배치32 H 변경후현재handoff 검증 시작: 정식Native두후보와동일한현재handoff source를freshbuild했으며현재auth/purchase/push/session을Native보고서실수로재확인한다(candidate결과재표시아님). 새Maven/R8·XCFramework/Swift source/binary import/147staging을같은handoff기준확인뒤새staging으로self9/Testcontainers검증을수행한다. Mac잠금은GUI후속만중단하고headless검증계속한다.

- [P11-T01] 배치32 G 사전읽기완료/문서수정 시작: 64Task·각증거경로를대조해누락path0/제품TODO-FIXME-NotImplemented표식0을확인했으나기능완성근거로쓰지않는다. FEATURE_MATRIX의110checksum/COMPATIBILITY의Unity미검증·이전 ENV-002/START_HERE계획전용소개가현재실측과불일치해정정한다. contracts/openapi.yaml은기존계획에있지만부재(기존Core baseline에서도미존재명시)로P11기계계약문서gap을등록,實행Controller/docsAPI/Bridge schemas와구분한다. P11전체완료/실Provider13·P05실패·self-hosted/Strict제약은유지한다.

- 배치32 F/H 현재handoff검증 결과: ff2d0d5제품 source의freshAndroid/Maven/AAR/R8·device+sim XCFramework·SwiftPM sourceconsumer·SimulatorSDK binarymodule typecheck·UPM147체크섬·선정3Java class/Cexports4양slice 모두PASS. GoogleAuthProvider는compiler synthetic private accessors를제외한공개bytecode surface도전과동일(전체ABI주장아님). 현재Native폭넓은회귀Android47/Swift43 failures/skip0,P08sourceAPI/닫힌Core＋정확Native전이검사PASS. Testcontainers11실행(의도변이1 exit1·정상복원0포함)PASS. 후보기능제품bytes는candidatee6/fc와동일하며정식handoff에별도5ef87e5/ff2d0d5로통합; candidate21b5f71은로컬이력보존/원격push0. T02코드구현은완료하되Mac잠금으로새package post-change GUI소비필수검증이남아로컬PARTIAL,SDK/Release완료아님.

- 배치32 H 최종현재코드검증: 전체 Python229/55모듈PASS/skip0(18.532초),현재Native47Android/43Swift·새handoff source/binary Swift소비·Maven/R8/XCFramework/147checksum·P08API/원본Core종결+Native exact전이guard PASS. 새Native source/새package로self9 재검증9/9PASS(이전T01판정用self9와Source/staging이변경돼재실행필요),TC11(정상10/의도변이1과정상복원)PASS. test/check/sample/expected failure/Player수는분리한다. 기존 P05FAIL·실Provider13/Native profile/GUIpost형검증은미완료. 새 Hub4에서정상GUI/실제Builder環境이확인된변경근거로 기존tiny direct batch diagnostic을소유새project/nonce/session/210초상한에서단1회수행한다. 라이선스활성화/파일수정/사용자process종료없고실패시동일재시도없음. 이진단이전체Strict는아니다.

- 배치32 자동Editor direct진단PASS: ff2d0d5,새소유project/nonce862871954f4d43b3a0879b56a0a20bf1·실제batch C# method/receipt·정확6000.5.8f1·marker1/exit0/7.26초,missingChannel/IPC/compileerror0(tests0/check1/Player0). Mac잠금은CUA UI조작제약이며이자동실행을GUI검증이라고재표시하지않는다. 기존 빌드script는unity run CLI를사용하므로이제동일한tiny--mode cli를새소유project/210초상한에서한번확인한다. 직접실행PASS로CLI/전체Strict/Player까지PASS로추론하지않는다. 라이선스파일/활성화/타process조작0. 전체Strict는전용환경까지완비될때만최대1 유지.

- 배치32 자동Editor CLI tiny진단도PASS/exit0(실제batch method·nonce receipt·marker1/compileerror0,unity-editor-smoke-fxlcmqqv). 기존build script의unity run 경로정상도별도확인했으므로Mac잠금중후속새package소비를GUI대신원래CLI batch 경로로실행가능하다. GUI검증으로재표시하지않는다. CLI에서도같은명시PID/AVD/양port/동일SDKserver Guard를사용하도록분리하고known教育안내는명시diagnostics+전부binding일때만허용한다. GUIreceipt요구를CLI에가짜로충족시키지않고실제원본batchBuilder/APK와최종DB/PII판정을유지한다. Default ACK0/불완전binding/타SDK기기거부는강화unit뒤실제실행한다. 전체 Strict는별도완전한전용환경확인전 0이며tiny PASS로대체하지않는다.

- 배치32 H CLI대체후속경로 검증/커밋 전: batch direct와cli실제nonce method완료PASS에근거해원래CLI consumer경로로현재Native변경후E2E를수행한다. GUI실행이라고claim하지않고실제원본batchBuilder/APK·동일staging/source검사·PII/SQL/marker/시간제한을유지한다. 새 3unit은CLI/GUI동일GuiAdbGuard 생성·부분binding거부/legacyACK없는경로유지·completebinding없는notice입력거부와유효CLI입력처리를검증했다. 매명령PID/AVD/양port/server/exe는동일강도,GUIreceipt를위조하거나OS잠금을우회하지않는다. Code완료후새기기PostPII/새iOSCLI 소비를실측하고새fullPython은그후최종source에서재검증한다.

- 배치32 CLI후속단계 사전조건: 현재5037listener0으로기존server31840을재사용하지않는다. 새AVD전 한정SDK server를loopback에직접foreground server nodaemon으로생성해OS bind가경쟁時실패하도록하고기존daemon을kill/restart하지않는다(공식ADB -L/foreground문법확인). 생성된자기PID/실행파일만실측·기록하고기기명령은같은guard를통과시킨다. 실효환경의server socket/host/port override는사전거부해검증한5037과다른endpoint로명령이가지않도록보강한다. Mac잠금중새GUI조작아닌명시CLI batch 소비로분리/기존성공기기보존/시간상한유지. 첫파일수정호출은작업디렉터리오타로process생성전 거부돼변경0이었고정확한저장소로정정했다.

- 배치32 후속CLI 명시binding 검증/커밋 전: CLI/GUI동일Guard3기본검사와실효env endpoint변경거부/legacybinding검사총9건PASS/skip0. 사용자Mac잠금을해제하거나GUI조작을대체하는스크립트가아니라이미정상확인한원래자동batch builder를명시선택한다. 실제SDK코드/가격/retention/시간제한/marker·PII·SQL조건변경0. 다음새own foreground SDK서버/새PostNativePII AVD와현재147staging을사용하고자기서버·기기만종료해기존daemon/process는건드리지않는다. 현코드commit뒤초기tracked-clean을확인한실제플랫폼검증을수행한다.

- 배치32 CLI후속서버최초준비FAIL/기기0: foreground -L tcp:127.0.0.1:5037을설치된adb36이“specified hostname unsupported”로bind전 거부했다. 기존5037listener0/daemon교체0/AVD생성0/Player0으로원본보존. 같은foreground OS bind방식에서지원되는tcp:5037(기본localhost, -a없음)으로정정하고실제listen주소가loopback임을추가확인한다. UI/SDK/시간제한변경아닌테스트서비스시작인자수정이며다른server를kill/restart하지않는다.

- 배치32 post-Native CLI A는새 SDK/package의APK9823d4fc4ca24706018d9d8f99f8f6b7710c5ada4732003b46afab26589fb541생성/Backendready까지통과했으나설치전 GUI_DEVICE_OR_ADB_BINDING_CHANGED/DEFERRED_ENV2로중단됐다. ownADB로그에“adb server killed by remote request”가있어batch종료시server수명변화를확인했다. 원본은BUILT_NOT_RUN·실제Player0/새DB/AVD보존,기준을무시해성공시키지않는다. ADB공식commandline source의server socket/ANDROID_ADB_SERVER_PORT precedence를확인했으며원래Builder를runtime5037과분리된5038의build전용환경에서한번검증한다. 두port기존listener0확인·같은SDK/ownedforeground runtime·-a없음/loopback·기존server교체0. APK검증이지PlayerPASS아님을분리하고실험이성공한경우만공개harness에명시옵션을추가한다.

- 배치32 batch/runtime ADB분리 실험PASS: 동일기존 Builder가5038 build전용env에서APK생성0,동시에5037 runtime foregroundPID66577은전후동일하게살아있음/빌드port종료0관측(AVD/Player0). 이검증된분리를명시--build-adb-port옵션으로추가,GUI/불완전runtimebinding/5037 재사용/이미소유된buildport는거부한다. helper는OS에직접bind한같은 SDK foregroundPID만소유/정리하고다른daemon을교체/kill-server하지않는다. 기존 build/PII/DB판정은동일. 새 4unit이busy/invalid포트·실행파일변조·child환경분리·자기process만정리·builder가종료한경우를검증PASS. runtimeguard/시간제한완화없음. 새post PII B에서현재Native/package첫실제Player를재검증한다.

- 배치32 post-Native 실제Android B FAIL/exit1(3seglcb1,source0d6df8f): 分離build/runtime endpoint로같은ownedruntimePID67934가유지돼APK설치/Activity/Native engine·Awake까지확인했다. 그러나Start/SDK/HTTP전appEXIT_SELF status0로종료해기존 180초timeout; crash/ANR관측0·안내1회ACK·beforeGUI와selectedsettings/boot옵션차이없음(buildGUID 등identity제외). NativeSDK진입0으로새 Authhelper원인확정불가,실패/AVD/DB/log보존. Mac잠금중창표면영향을분리하는근거로새headless(-no-window)AVD만바꿔한번대조한다. 동일SDK/API/newNativepackage/성공조건/CPU2/RAM2GB/timeout/JSONCLI구조는유지한다. 이것도같은실패면근거없는추가반복없이Root미확정/부분으로유지한다.

- 배치32 post-T02 Android새source/새package 실제PASS(source5bc3cd0,zr28pnb1): CLI기존 builder/freshNative81 source/package d11a2.../별도buildport5038·runtime5037/새headless같은 image·2CPU/2GB에서전단계/Nativecallback/PII24marker·Backend/원장1/delta100/exit0,초기tracked-clean. 최초window형실행Awake후 EXIT_SELF0/timeout과원장未실행을별도보존,hostWindow영향대조회복으로기록하며특정Nativehelper근본원인확정은아님. 기존SDK/시간제한/성공조건변경0. 自己emulator/runtimeforeground만종료·AVD/DB/log보존,기존daemon kill/restart0. 이후sourceCode변경없이전체 Python237/57모듈PASS/skip0(25.101초). 다음iOS도새Native/package의명시CLI batch·새 sim/DB·기존 PII/SQL판정으로1회검증하며GUI와구분한다.

- 배치32 post-T02 iOS 실제PASS/exit0(sourcedaf3cd9,artifacts/unity-ios-e2e-mmev5ejd): 새Native/package d11a2...의원래CLI batch export·Xcodead-hoc·새 18.6Simulator·DB에서24필수PII/Native/mainthread marker·Backend各trace·원장1/delta100/초기tracked-clean확인. 실제생성UUID473D3E40-A8E9-43FF-91DA-04F8E76E2FFA와db-suffix deviceName을read-only대조한뒤그기기만shutdown/후속Shutdown확인·disk/DB/log보존. Android새현재source실제Pii와Native20/23·넓은47/43·API/전이/선정ABI·freshpackage/소비검증이모두충족돼P10T02명시로컬완료조건PASS로판정. RootSDK전체완료/실Provider/Strict/Release/Native메모리Profiling성공은아니며P05FAIL/Provider13WAIT 등유지.

- 배치32 I/J 최종scan/커밋 전: 전체코드최종237/57모듈연결·Native47/43·현재source/패키지/양플랫폼post E2E와정확한Source/실패한계·AJ/15항목·후보→정식커밋맵을통합문서에정리했다. 신규range scanner0/탐지0,역사range scanner1/기존hash오탐2는현재test SHA독립재계산일치로검토/보존. 全commit text/금지생성물0,원장64/구현24·진행40/localPASS22·FAIL1·PARTIAL41정합,57module全CI연결확인. repo public/vars0/runners0·handoffFF이력확인. 명시stage/scan/문서commit後allcode포함sourceFFpush·정상vars0再확인·falseHosted1회만수행한다. Macunlock필수대기는CLI회복/실제검증완료로해소했지만GUI잠금자체를해제했다고claim하지않는다.

- 배치32 I/J stage검증/커밋 직전: 명시16개README/정제문서·JSON의파싱/text·원장/누락경로·diff 검사PASS,실제staged blob scanner exit0/탐지0. 코드/테스트는현재최종Source에서237검증됐고이후변경은결과문서뿐이다. 모든개발키/로그/DB/라이선스/빌드출력·기존Demo/cache는stage하지않았다. 마지막문서commit후전체이번범위재scan·freshfetch/FF확인·동일handoffpush·localremote 일치확인→vars정상응답0뒤singlefalseHosted로배치31UUID후속/전체현재Native·harness/test를함께검증한다.

- 배치32 I FFpush확인/단일Hosted시작: local/remote handoff HEAD2017771d355cb56865f44ef1ddf9e4faad78442d 일치,3639a1d→2017771 FFpush exit0. 모든현재code/test/배치31UUID후속·정식Native변경과새전이guard가해당source에포함됐고trackedclean/초기미추적3경로보존. 마지막전체range scan0/탐지0·정상vars API0/total0 재확인. release_validation=false Hosted-only 단1회를이source에서요청하며최종결과前PASS기록없음. 추가실Provider/OS잠금조작/main/force/runner/Release없음.

- 배치32 I Hosted dispatch1회수락: run44165459795/source2017771d355cb56865f44ef1ddf9e4faad78442d,release_validation=false. https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44165459795 . 현재최종결과대기이며추가dispatch/retry/Unity활성변수/runner/Release없음. 소스동결후코드변경0,최종결과와local/remoteHEAD만기록한다.

- 배치32 I 원격중간검증: run44165459795 inventory-contracts SUCCESS/UnitySKIPPED. 공식job logs API exit0에서Python57모듈237건 및닫힌原Core기준+정확Native전이guard PASS를확인했다. 新KotlinCodec/SwiftDecoder 포함native job과Backend/기본집계최종결과는대기이며추가dispatch/소스변경없음. 원격수와로컬237일치,배치31UUID후속을포함한최종source2017771검증이다.

- 배치32 I 원격추가관측: Android-native/Backend-postgres SUCCESS. 공식logs에서필수StoredGoogleSessionCodecTest/JUnit gate와TC11/의도변이1/정상복원을확인했다. Swift package단계도SUCCESS후syntheticSimulatorhost최종대기이며전체PASS를앞서기록하지않는다. 추가dispatch0/현재code tree2017771불변,검토한local문서링크누락0.

- 배치32 I/J 최종원격결과/문서커밋 전: run44165459795/source2017771d355cb56865f44ef1ddf9e4faad78442d,false 단1회SUCCESS. Hosted4/basic SUCCESS,Unity/ReleaseSKIPPED. 공식Python57모듈237·原Core＋Native전이guard·신규KotlinCodec/JUnit·Swift40/Decoder3·TC11/의도변이1/정상복원·synthetic iOShost job확인. quiet host정확test수UNMEASURED/Unity실행아님. 배치31UUID후속과전체현재code/test포함,이후코드변경0. AJ/15항목·후보→정식커밋맵·64Task24/40/local22/1/41 및모든실패/미완료scope를문서로정리했고최종문서stage scan/commit/동일handoffFFpush/localremoteHEAD·원래미추적3경로보존을검증한다. 추가CI/실Provider/main/force/Release없음.

- 배치32 J 최종stage검증/커밋 직전: 명시7개결과문서text/JSONparse·64Task원장·diff PASS,실제staged scanner exit0/탐지0. 검증source2017771뒤SDK/harness/tests/workflow/baseline코드변경0이다. 마지막문서commit後freshfetch·전체이번range scan·handoffFF가능성·push·최종remoteHEAD/추적파일clean·초기미추적3경로와candidate로컬branch보존을실제조회한다. 추가dispatch/원격branch/candidatepush/실Provider/main/force/Release없음.

- 배치33 재개: 전체 Strict 소유권 preflight가 미완성인 현재 구현은 자원 생성 전에 `DEFERRED_ENV`/exit 2로 중단하도록 보호했다. 이는 완성된 preflight가 아니며 전체 Strict는 미실행이다. P10-T03/T04 및 P11 상태는 변경하지 않는다. `docs/API.md`의 LOCAL_MOCK Player 관련 오래된 설명을 배치32 증거에 맞게 정정했다.
- 배치33 연속 작업 A 시작: 실제 Controller/DTO/Security/오류 필터를 조사하고 HTTP OpenAPI 및 소스 대응 검사를 구현한다. 기존 a83561a와 미추적 파일을 보존한다.
- 배치33 A: OpenAPI 24 operation과 정적 source/profile/security/header/error guard 및 정상1/음성6 PASS. OpenAPI 문법 PASS. DTO 및 endpoint별 실제 HTTP 오류 응답 대응 보강이 남아 BUG-017 OPEN 유지. 전체 API PASS로 승격하지 않는다.
- 배치33 B: 64 Task별 완료 기준과 현 원장 필드를 연결한 감사 JSON 작성. 24 IMPLEMENTED/40 IN_PROGRESS, 로컬 PASS22/FAIL1/PARTIAL41 유지. 기준별 증거 내용의 수동 전수 판정은 미완료이며 자동 승격 없음. 설정 checker의 productIds/certificate 배열·scalar 자료형 검사 강화 및 2시험 PASS. 외부 7항목은 모두 미준비/exit2.
- 배치33 C: 새 전용 iOS18.6 Simulator에서 Swift coordinator fake-provider warmup20/100회 실제 계측, weak 잔존0. C ABI/Task continuation·세션 전환·Android JNI/heap·Unity scene/frame 측정은 NOT_RUN. T03 PARTIAL 유지.
- 배치33 D: 새 Maven/AAR/sample/R8, 새 device/simulator XCFramework, 독립 Android R8/Swift source/binary compile 및 UPM147 checksum PASS. 빌드 시작 source a83561a의 shipping source는 현재까지 동일하다. 신규 Unity 소비·선정 Kotlin binary API 비교는 미실행, T03 의존과 T04 PARTIAL 유지.
- 배치33 E/F: 읽기 전용 preflight inventory 추가, 새 staging checksum/설치도구/Docker daemon 확인. E1의 license/module/source/required lane와 자원 소유 계약 미완료 → exit2 DEFERRED_ENV. E2·제품 lane·전체 Strict는 NOT_RUN/0회. 기존 조기 차단 유지. 완성된 preflight나 E3 음성 전체로 표시하지 않는다.
- 배치33 G/H: artifacts/batch33/DEV_RC에 새 UPM/Maven/XCFramework·설치/API/호환성/설정 문서와 manifest를 조합했다. 정식 Release 아님. Python247(venv)/managed418/lifecycle100 확인. TC 변이·self9·Android/Unity 새 E2E 등 요청 전체 회귀는 미실행. 미완료 목록은 통합증거에 명시한다.
- 배치33 H 후속: Hosted inventory는 OpenAPI source binding 열거 순서 차이로 실패했다. 비교를 source 기준 정렬하도록 수정하고 순서반전 정상 fixture를 추가해8시험 PASS, 전체Python248 PASS. 이 수정은 단1회 Hosted source 이후여서 원격 미검증이다. 자체시험9 lane 표시는 모두 PASS였지만 실행 중 문서 diff 변경으로 provenance 집계 exit1을 유지했다. 소스를 고정해 자체시험만 재확인한다(전체Strict 아님). TC11/의도변이1/정상복원 exit0.
- 배치33 H 소스고정 재확인: 84e1026에서 self9/47test/check9/예상실패3, 전체집계 PASS exit0. 최초 provenance FAIL 원본 유지. Testcontainers11/예상변이1+정상복원 PASS. 최종Python248 PASS. 전체Strict는 계속0회이며 Hosted 후속코드 미검증 표시를 유지한다.
- 배치33 최종 원격: run44269328731/source deb9074 FAILURE. Backend·Android·Swift/iOS Simulator SUCCESS, inventory/basic FAIL, Unity/Release SKIPPED. 후속84e1026은 FF push/로컬248+frozen self9 PASS, 원격 미검증. 미완료 task 상태·BUG-017/P05/StoreKit/Provider 대기는 그대로 유지한다.
- 배치34 A 시작: 3313c84에서 재개, 기존 실패·미추적 경로 보존. binding을 source/profile/header 의미로 정규화하고 누락·중복을 fail-closed 검사한다. HTTP 실제 응답 수집과 schema 대조를 추가한다.
- 배치34 A: 의미기반 binding 누락/중복·중첩순서와 Kotlin DTO field/type/nullable/required 검사 추가. 실제 LOCAL_MOCK HTTP24 operation 대응표와 성공/오류 schema 대조 완료. 누락 Idempotency-Key가 INTERNAL_ERROR500이던 내부 오류를 INVALID_ARGUMENT400으로 수정/회귀 확인. 합성Sandbox의 성공·오류 전수는 남아 BUG-017 OPEN 유지.
- 배치34 B: 64 Task를 각 완료기준/실제근거/남은조건별로 검토한 개별감사 JSON 작성. P00-T03의 최소프로젝트 build조건은 기존Native·Backend/Unity실행으로충족되어 IMPLEMENTED/PASS로개별정정, RESOLVED ENV-002/003을현재 blocker에서 제거. 나머지65가아닌64행을유지하며 blanket승격0. 현재25 IMPLEMENTED/39 IN_PROGRESS, localPASS23/FAIL1/PARTIAL40. P11-T01은 남은기준별근거공백/내부FAIL로PARTIAL.
- 배치34 C: 새전용 iOS18.6/실제패키지 C ABI init/status/shutdown 각warmup20+측정100,120session/360callback·harness outstanding0. Nativeprivatepending/Taskcancel/continuation·Androidheap·Unityscene/frame은미측정. T03 PARTIAL유지.
- 배치34 D: 선정JVM public4class가배치32/33Maven에서동일. 새전용Unity iOS UPMimport→CLIexport→Xcode ad-hoc→실제18.6Player 24marker/원장1·100 PASS. 새Android는5037/5038또는선택기기port기존소유로생성전중단(원본보존). T03의존/Android미실행으로T04 PARTIAL.
- 배치34 E/F: required lane을실제verify-all AST에서추출하고20종 E1필수조건을판정하는순수계약/실관측을추가. 정상합성fixture PASS와필수조건누락/소유identity변조6시험 PASS. E2identity대조는구현됐지만자원생성/실관측배선미완료,license·소유계획등불충족으로실제E1 DEFERRED_ENV/2. 전체Strict0회.
- 배치34 D 후속: source고정후실제free port를다시검사한새owned Androidcontroller c가exit0. 신규UPMimport/CLIAndroidbuild·PII Player PASS,자기AVD/ADB종료확인. 첫port충돌·미커밋guard실패원본은보존. Android와iOS새소비는각PASS이며T03의존으로T04 PARTIAL유지.
- 배치34 A2 후속: 기존합성HTTP6class에opt-in 구조수집기를연결해문자열증빙/토큰을지우고실제직렬화type을검증했다. profile별별도DB에서Sandbox5/Local5시험PASS,132응답shape·requestId대조PASS. 최초LOCAL관측과합쳐24operation모두200근거. SSE전체payload·동적Map의세부계약보강은남아BUG-017 OPEN유지.
- 배치34 H 최종로컬: 최신고정6b8d884 self9/47test·9check PASS/0. Python262,OpenAPI16·문법,HTTPcapture+오류MockMvc4,합성HTTP10/132구조,선정API/Core/managed/변이복원·TC11 및신규양Player 모두확인했다. 실제Strict는미실행,기존P05/StoreKit/Provider대기는유지. 최종코드/검토후단1회Hosted를실행한다.
- 배치34 C3 추가: 원격네트워크대기동안새전용 iOSUnityPlayer에서warmup20+100회 init/Native진단왕복/shutdown/Scene생성·해제를실측했다. frame1000개·runtimeProfiler메모리관측·pending0, forcedGC후weakclient1이관측됐다. 이를누수라고단정하거나0으로정정하지않는다. first-app-init/CPU blocking·Androidheap/Taskcontinuation은未측정, T03 PARTIAL.
- 배치34 최종Hosted44287600414/source648bb807baeab4e83b037856a9ae04f84e8a2154 SUCCESS. inventory/Backend/Android/Swift-iOS/basic PASS,Unity/Release SKIPPED. Ubuntu263와OpenAPI 정상/순서반전·음성 확인. 같은source 로컬Core/self9/TC11 PASS,CI후code/test/workflow변경0. 최종결과문서만FF인계한다. T03/T04/P11부분·BUG017/P05/StoreKit/Provider대기는그대로다.

## 포트폴리오 최종화 — 문서36 사용자 종료 기준

- 포트폴리오 상태: PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS / DEVELOPMENT_CLOSED. 기존 SDK의 BLOCKED_INTERNAL 및64 Task 상태/집계와 별도로 판정한다.
- 범위: 제공 공고 W/G와 실제 코드·검증의 대응, Quick Start/책임·호환성/문제해결 문서, weak client 제한 조사, 최종 DEV_RC와 개발 종료 인계. 신규 기능/실Provider/추가 성능프로젝트는 포함하지 않는다.
- 기존 제품·하네스·계약 source648bb80 및 배치34 결과를 보존하며, 날짜만 갱신하는 재검증은 하지 않는다. 남은 개선점을 자동 필수 배치로 전환하지 않는다.
- 포트폴리오 문서 검토: README 공고대응/진입점, Quick Start/실제Host·API·SSE/Map/오류·버전·호환성·보안·선택적USER_SETUP을현재사실로정리했다. 과거generic Unity미검증/계획변수·NOT_STARTED 소개는현재문서에서제거하고원본Git/WORK_LOG/evidence는보존. local문서링크150/SDK호출명11/Python예제문법검사PASS(예제실행·새Player아님). portfolio판정은최종RC/일관성검토뒤확정한다.
- 포트폴리오 최종판정 확정: PORTFOLIO_READY_WITH_KNOWN_LIMITATIONS / DEVELOPMENT_CLOSED.9개종료기준을기존실행/source·현재가이드·제한공개와대조했다. 기존64 Task상태·집계/FAIL/WAITING_USER는변경하지않고이미RESOLVED인ENV-002를잔여사유로쓰던행의설명만실제남은조건으로정정했다. BUG-017은현재파일존재/24op검증및SSE/Map잔여로설명정정하되OPEN유지.
- 포트폴리오 원격 인계: beba1ff→e45188b73b70f3e54061f9ed5298ec9207903d62를동일handoff로FFpush0,local/remote일치·tracked-clean·기존미추적3경로보존확인. 마지막인계기록만별도commit하며새제품/하네스/계약code와CI실행은0이다. 포트폴리오개발종료상태를유지한다.

## 사용자 문서37 — 별도 소셜 로그인 확장

- 범위: A iOS Google → B Android/iOS Facebook → C Android Apple 웹 OAuth. 기존 포트폴리오 종료와64 Task 원장은 유지하고 이 확장만 별도로 기록한다.
- 시작dc3ed4224d1c676e33ee92e8aa7aa6ceaa3c7855, branch feature/social-login-20261119. 기존 Demo/cache 보존. 각 배치 로컬 commit만, push/PR/main/Release/실Provider 없음.
- A IN_PROGRESS: GoogleSignIn9.2.0 공식 nonce 시그니처·iOS 최소버전 호환 검토. Host URL callback은 명시적 forwarding, 새 Provider session은 별도 저장과 기존 Backend 세션/원장 권위를 사용한다.
- 소셜 A 결과: iOS Google Native session/GoogleSDKnonce·공통Native store/push account 접근·C ABI router/HostURLforward/UI sample 구현. Swift29(신규Social5/기존Apple20/CBridge4)PASS,기존JWT/Audience unit PASS. device/simulator新XCFramework·Google resource 포함source consumer·고립binary consumer build·Unity PBX hookcompile·staging147 PASS. 실제Google/새UnityPlayer는미실행,계정설정WAITING_USER. B로진행하며최종FB의존성추가후패키지는별도판정한다.
- 소셜 B 시작: Facebook Classic access token/limited OIDC JWT를명시proofType으로구분한다. Classic은nonceclaim을가정하지않고매번Meta debug검증+proofType에결속된challenge원자소비를사용한다. 유효bearer를새challenge에서다시쓰는OAuth특성은제한으로명시한다. 동일FBAppID의여러app scope중복설정은거부,SDKsession갱신은기존세션을사용. Meta App Secret은Backend에만설정한다.

- 소셜 B IMPLEMENTED: Android Classic/iOS Limited·Classic, 증명분리·server app/subject 결속·Native session/store/push 재사용. Backend unit3/합성HTTP3·Android unit·Swift30·C# routing PASS. Meta remote download 지연은 공식SHA/codesign 확인 cache로 local archive 검증, 원격 DEFERRED_ENV. 실Facebook WAITING_USER. C로 진행한다.

- B 최종 소스 재검사: Facebook HTTP3 exit0/owned DB gamebridge_ci_abaf17e7c9, build-android.sh --mock Maven+R8 consumer exit0, 최신 Simulator archive exit0. 실제 Provider·새UnityPlayer未실행.
- 소셜 C IN_PROGRESS: HTTPS form_post callback, state/nonce/code 재생 방어, verifier-bound 60초 handle 및 Android Custom Tabs/App Link Native 경로를 구현한다. 실제 Apple 계정/Services ID/키·도메인 구성은 WAITING_USER.
- 소셜 C/확장 종료: Android Apple웹 OAuth·BackendHTTPS form_post/code교환/ES256·verifier-bound1회handle·기존session/원장연결 IMPLEMENTED. 최종Backend20+별도기존Auth/Mock/원장5 PASS,Android47+Bridge9 PASS,Swift31 PASS,C#PASS,OpenAPI27/변이18 PASS. device/sim XCF·binary소비/Meta포함AndroidR8·Maven/UPM147 PASS. proofType생략legacyHTTP호환을실제검증후수정. 실제4경로WAITING_USER·Meta기본remoteSPM DEFERRED_ENV·새UnityPlayer/실기기UI未실행. 선정내부시험미해결FAIL없음. 세배치를로컬commit으로종료,기존64행/개발종료·Strict0상태유지. 세부명령/제한/설정은SOCIAL_AUTH_HANDOFF.md와evidence/social-login/c-android-apple.json.

## 사용자 문서38 — GitHub 소셜 확장 인계

- 시작23536d2/feature/social-login-20261119, tracked-clean·기존미추적3경로보존. 사용자명시로push/PR금지만해제,main병합/Release/실Provider/새Player는허용하지않음.
- fetch후origin/main5ed09e5 확인. merge-base e4b677e에서main5commit·기존handoff+소셜359commit 분기,예상PR516파일/소셜3배치77파일. 지정브랜치와기존commitSHA를유지하며main의README/API/INTEGRATION보강을feature에merge하여보존한다. main자체는변경하지않음. PR에서기존누적baseline과소셜범위를명확히구분한다.
- 문서38: feature push e8823e0와PR#4 생성,GitHub516파일=로컬diff집합동일. 이전PR#2 CI44339264161은unity-runtime-required 미구현exit2/local-gate연쇄실패,Native/Linux PASS. 새PR CI44499239447 inventory는승인된social변경을기존P08/P10 bytefreeze가거부한별도신규실패로판정. 기존baseline/guard를수정하지않고closed dc3에원래검사를수행한뒤승인23536d2의26경로·enumappend·CABI추가만현재소스와대조하는명시적전환검사를추가한다. 새guard/음성5검증PASS,동일inventory step로컬재검사중.
- 문서38 CI수정1 로컬검증: GitHub와동일inventory step전체268 test/60 suite exit0,원본P08/P10 guard의historical실행과current source전환·5음성 포함. 최초Hosted run의Backend/Android는SUCCESS,Swift진행중,Unity는SKIPPED. 수정한코드는guard/새전환record/CI호출뿐이며Native/Backend/Unity제품을바꾸지않았다.

## 사용자 문서42 — Unity iOS Meta 동적 의존성 Embed 수정

- main36ca836에서별도fix/ios-meta-embed-20261119 worktree시작. 원본41실패·DB/기기/UPM·원본feature와미추적경로보존. Android의41PASS는유지하고재실행하지않는다.
- 원본앱/otool/PBX/서명을대조: UnityFramework는FBAEMKit/FBSDKCoreKit_Basics/FBSDKCoreKit/FBSDKLoginKit4개를strong참조하지만.app에는UnityFramework/UnityRuntime만존재. 정상ad-hoc서명과기존@executable_path/Frameworks runpath확인. FacebookLogin SPM제품이UnityFramework에만연결되고HostApp의package제품소유/Embed가없음이원인. Meta18.1.1/Google9.2/staticNative링크를유지하여영속ExportHook을수정하고독립PBX회귀→새iOSPlayer로검증한다.
- 수정안: FacebookLogin의UnityFramework strong링크를유지하며같은SPM제품을HostApp에도소유/strong링크시켜Xcode가4개동적의존성을자동Embed·서명하게한다. packageGUID/버전·target별제품/강링크를검증해중복추가와잘못된의존성을거부한다. 실제UnityAssembly+Apple plutil oracle의독립40검사PASS. iOS실행기에최종앱의4개framework및서명사전검사추가,원본실패앱은실제로명시거부PASS. 새staging/새소비자E2E대기.
- 문서42 최종로컬결과: 새iOS18.6/Unity6000.5.8f1 소비프로젝트/E2E attempt1 exit0/Player PASS,23marker·6단계/redaction 및Backend필수trace·원장1건/+100·logout후활성session0. HostAppFacebookLogin제품연결로Meta4개모두.app/Frameworks에포함,strict서명0·강LC_LOAD_DYLIB유지·런타임dyld오류0확인. 새UPM147/SHA256SUMS997fd8de… PASS. Android41PASS유지/이번실행0,실OAuth·실결제·원격push·Release NOT_RUN. 독립40회귀/원본앱누락거부와별도docs/IOS_META_EMBED_FIX.md/evidence기록;최소범위commit/push/PR만진행.
