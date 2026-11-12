# 기능 호출 경로 1차 조사 — 개발 중

2026-11-12 소스 및 WORK_LOG 기준. Unity Android LOCAL_MOCK 전체 흐름은 전용 에뮬레이터에서 PASS했다 ([증거](evidence/px-t04-unity-android-local-mock.md)); Unity iOS Simulator LOCAL_MOCK 전체 흐름도 PASS했다 ([증거](evidence/px-t07-unity-ios-local-mock.md)). 양 플랫폼의 LOCAL_MOCK Push/Lifecycle도 별도 Player에서 검증했다 ([Android](evidence/px-t08-unity-android-mock-push.md), [iOS](evidence/px-t12-unity-ios-mock-push.md)); 실제 제공자와 실기기는 별도다. `PARTIAL`은 일부 경로만 구현하거나 완료 검증이 남았다는 뜻이다. Fake·LOCAL_MOCK·실제 플랫폼 결과는 서로 대체하지 않는다. 이 문서는 최종 P11 감사가 아니다.

| 기능/Unity 공개 표면 | Editor offline | Android/iOS Native bridge | 확인한 범위와 잔여 작업 |
|---|---|---|---|
| 초기화·상태·종료 | in-memory fake | LOCAL_MOCK과 PLATFORM_SANDBOX 경로, session/종료 경계 구현 | 독립 .NET 및 Native fake/C ABI, Unity Editor 및 Android/iOS LOCAL_MOCK Player 경계 확인. 실기기·다른 모드는 별도 |
| 로그인·복원·로그아웃 | fake | LOCAL_MOCK 서버, Android Google, iOS Apple Native facade 연결 | 양 Native Mock local DB·fake provider 및 Android/iOS Unity LOCAL_MOCK Player 로그인 확인. 실제 Google/Apple 계정은 미검증 |
| 상품·구매·잔액 | fake 두 상품 | LOCAL_MOCK 서버, Play Billing 및 StoreKit sandbox facade 연결; 검증 전 대기와 검증 후 이벤트 구분 | Mock local DB·fake 및 Android/iOS Unity LOCAL_MOCK Player 구매 확인. 실제 Play/Apple 거래는 미검증; iOS 26.5 local StoreKit 시험은 ENV-STOREKIT-26 FAIL |
| 구매 복구 | fake | 양 Native Mock의 암호화 pending 단서·sync, Play/StoreKit recovery 및 동일 계정 single-flight | Unity Android emulator/iOS Simulator에서 서버 응답 유실 후 별도 프로세스 재시작·세션/pending 복구 및 원장 불변 확인. 실기기·실제 스토어 복구 미실행 (BUG-009 OPEN) |
| push 권한·등록·해제 | fake | LOCAL_MOCK simulated 등록, Android FCM 및 iOS host-managed APNs sandbox 등록 코드 | Unity Android emulator/iOS Simulator LOCAL_MOCK 등록·해제·logout 후 DB token 삭제 확인. Android emulator·iOS Simulator OS 권한 dialog 거부, 등록 차단 및 재요청 확인; 독립 managed Mock 거부 PASS. OS 시험 자동 재현·원격 FCM/APNs·실기기는 미검증 |
| push 수신·열기 | fake UI 경로 일부 | Android host forwarding/메모리 cold-start queue, iOS Unity Notifications host adapter 및 C ABI route 연결 | Unity Android emulator/iOS Simulator LOCAL_MOCK 수신·중복·main-thread·session 전환 확인. 실제 알림 클릭 및 remote FCM/APNs·실기기는 미검증 |
| 점검 설정 | fake default | LOCAL_MOCK 및 sandbox 서버 조회·유효 cache와 구매 gate 연결 | server/fake 및 local HTTP→Unity decoder 확인. sandbox 공개 조회와 구매 gate는 같은 Native cache를 사용하며 실제 sandbox/Unity player는 미검증 |
| 진단 | C# registry snapshot | Native typed ring과 Unity 비동기 snapshot 연결 | Native·독립 managed fake 및 Android/iOS LOCAL_MOCK Unity Player에서 Native 진단 조회 확인. 실기기·다른 모드는 미검증 |
| 샘플 | Editor Offline UGUI 소스 | Android/iOS Native sample과 별도 UPM Native Demo 소스 | Native Mock sample의 과거 simulator/emulator UI 일부, Offline Demo는 격리 Unity Editor에서 모의 로그인·상품·구매 callback 확인. Native Demo의 Editor 사용 차단·안내 및 Android/iOS LOCAL_MOCK Player 설정/모의 구매 callback 확인. Package Manager UI import와 실제 화면 렌더링·포인터는 미검증 |
| 패키지 | UPM staging·export hooks | Android Maven/AAR, iOS static XCFramework script | 최신 Android Maven 독립 R8 consumer와 iOS device/simulator XCFramework·Swift consumer link 확인. 최신 UPM staging 110개 체크섬 확인. 별도 staged SDK의 Unity Android/iOS LOCAL_MOCK Player import/export 확인; 새 산출물마다 재검증 필요 |

Backend의 Apple/Google synthetic verifier→인증 HTTP→DB grant 및 Google durable finalizer fake 시험은 실제 스토어 검증이 아니다. LOCAL_MOCK 개발 send에서 Android·Swift Native 수신까지 전용 local DB로 확인했다. `SIMULATED`는 FCM/APNs 원격 전달이 아니다. `scripts/smoke-local.sh`의 판정은 자체 필수 조건을 따르며 별도 Player 증거만으로 해당 명령을 통과 처리하지 않는다.

`XCODE_STOREKIT`의 iOS 18.6 local 거래·fake DB 응답 유실 복구는 확인했으나 Unity player·실제 프로세스 종료는 미검증이다. 실제 플랫폼 자격증명 설정과 검증은 별도로 남았다. 외부 설정·재실행 절차는 `docs/USER_SETUP.md`, 남은 내부 문제와 환경 대기는 `docs/PROGRESS.md` 및 `docs/WORK_LOG.md`를 따른다.
