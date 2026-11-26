# GameBridge SDK — Verification Evidence

[README](../README.md) · [TECHNICAL_OVERVIEW](TECHNICAL_OVERVIEW.md) · [COMPATIBILITY](COMPATIBILITY.md)

**주장 → 구현 소스 → 테스트/실행 근거를 연결하는 공개 검토용 인덱스**입니다. 2026-11-27 기준 공개 저장소의 [main `d37e8a1`](https://github.com/CodingBot000/GameBridge_SDK/commit/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4), GitHub PR/Actions, [v0.1.2-dev Pre-release](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)를 조회하여 구성했습니다. 제품 검증의 새 실행이나 완료 상태 변경은 아닙니다.

| 증거 구분 | 확인 가능한 내용 |
| --- | --- |
| GitHub 실행 메타데이터 | 실행 커밋·Job·Step 결과. 로그 접근 및 보존은 GitHub 정책에 따릅니다. |
| 공개 소스 / 정제 JSON | 구현·테스트·기존 실행 요약과 기록된 식별자. 소스 존재만으로 실행 성공을 의미하지 않습니다. |
| 공개 문서 / PR 기록 | 로컬에서 관측한 결과의 공개 요약. 비공개 원본 로그·DB를 직접 읽은 것과 다릅니다. |
| Release 자산 | 실제 다운로드 가능한 개발자용 패키지 및 checksum/manifest. 이번 확인은 GitHub 등록 digest 비교이며 다운로드 재해시는 아닙니다. |

실제 개발 당시 정책의 결정 기록과 구현·테스트 연결은 [TECHNICAL_OVERVIEW — 개발 당시 기록된 기술 결정](TECHNICAL_OVERVIEW.md#개발-당시-기록된-기술-결정)을 참조하세요. 아래 고정 커밋의 소스·assertion 링크는 현재 구현과 시험 조건을 확인하는 경로이며, 과거 실행 커밋을 대체하지 않습니다.

## 구매 데이터 정합성과 업데이트 복구

**관측 범위:** Unity 6000.5.8f1 · Android API 34 AVD · iOS 18.6 Simulator · LOCAL_MOCK. 지급 commit 후 응답 유실, 기존 앱/DB 데이터 유지 및 `0.1.1-dev → 0.1.2-dev` 덮어 설치, 기존 세션·미완료 구매 복구, 두 번째 동기화 회수 0건, 플랫폼별 원장 1건·100코인.

| 확인 대상 | 공개 근거 |
| --- | --- |
| **LOCAL_MOCK 시험의 실제 지급 구현** | [멱등키·body hash](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/main/kotlin/com/gamebridge/purchase/MockPurchaseController.kt#L45-L47) · [거래 UNIQUE·소유권](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/main/kotlin/com/gamebridge/purchase/MockPurchaseController.kt#L49-L52) · [신규 거래 지급·완료 처리](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/main/kotlin/com/gamebridge/purchase/MockPurchaseController.kt#L53-L69) · [DB UNIQUE](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/main/resources/db/migration/V1__initial_schema.sql#L30-L39) |
| 별도 실 Provider 지급 구현 | [GoogleGrantService](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/main/kotlin/com/gamebridge/purchase/GoogleGrantService.kt#L20-L58) — 실제 Play 스토어 거래 성공 근거가 아님 |
| **복구 시험 assertion** | [Android: 최초·재동기화](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/tests/UnityAndroidRestartConsumer/MockPlayerScenario.cs#L25-L40) · [iOS: 최초·재동기화](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/tests/UnityIosRestartConsumer/MockIosPlayerScenario.cs#L23-L38) — 최초 examined/recovered 1, deferred/failure 0, 잔액 100; 재동기화 examined 0, 잔액 100. 현재 fixture의 기대값이며 실제 관측은 다음 기록을 따름 |
| 실제 복구 실행 진입점 | [Android runner](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/harness/run-unity-android-mock-restart-e2e.py) · [iOS runner](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/harness/run-unity-ios-mock-restart-e2e.py) |
| 0.1.2-dev 관측 결과 | [버전 교체 결과](evidence/bridge-client-refactor-verification.md#이전-공개-버전에서-업데이트) · [PR #18](https://github.com/CodingBot000/GameBridge_SDK/pull/18) — 로컬 실행 공개 요약 |
| 과거 기준 실행 | [Android 정제 JSON](evidence/p10-batch34-unity-android.json) · [iOS 정제 JSON](evidence/p10-batch34-unity-ios.json) · [0.1.1-dev Batch A](evidence/batch-a47-dev-compatibility.md) · [Batch B](evidence/batch-b48-compatibility.md) — 각각 당시 버전의 별도 기록 |
| 원장 제약의 결함 탐지 | [격리 schema·중복 INSERT assertion](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/backend/src/test/kotlin/com/gamebridge/purchase/LedgerInvariantDatabaseTest.kt#L29-L39) · [예상 실패와 정상 대조 판정](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/harness/check-ledger-mutation.py#L45-L65) · [실행 기록](evidence/p09-ledger-mutation-20261113.md) · [Hosted Backend Job — PR #21](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077417070) |

과거 원장 Mutation 기록은 정상 1 test/실패 0과 UNIQUE 제거 1 test/예상 실패 1을 구분합니다. PR #21 Hosted Backend Job은 `Owned Testcontainers purchase invariants and mutation` Step 성공을 별도로 기록합니다. 이 결과는 실제 Google Play/App Store 거래 검증이 아닙니다.

## 비동기 요청과 세션 격리

- 구현: [응답 상관관계](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs#L107-L126) · [원자적 pending 제거·Task 완료](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs#L183-L205) · [GameBridgeClient](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/unity/Packages/com.gamebridge.sdk/Runtime/GameBridgeClient.cs) · [AndroidTransport](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/unity/Packages/com.gamebridge.sdk/Runtime/Platforms/AndroidTransport.cs) · [IosTransport](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/unity/Packages/com.gamebridge.sdk/Runtime/Platforms/IosTransport.cs)
- 테스트: [지연 응답·stale session·Dispose assertion](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/tests/UnityLateCallback/Program.cs#L23-L36) · [중복 응답 Mutation 판정](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/harness/check-bridge-mutation.py#L37-L58) · [Wire schema](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/contracts/bridge.schema.json)
- 결과: [과거 Bridge Mutation 기록](evidence/p09-bridge-mutation-20261111.md) · [과거 회귀 정제 JSON](evidence/p10-batch34-regression.json) · [0.1.2-dev 후속 종료/복원 시험](evidence/bridge-client-refactor-verification.md#2026-11-26-후속-실제-player-검증)

기존 관리 코드 418 assertion과 플랫폼별 시험·marker 수는 별도 집계입니다. 0.1.2-dev 후속 시험에서 양 플랫폼 로그아웃 후 복원 차단·종료와 대기 요청 0개를 기록했습니다. 원본 로그가 Git에 없는 후속 결과는 공개 요약입니다.

## Unity iOS Export 및 Native 연동 문제 해결

| 문제 | 확인할 소스 / 실행 기록 |
| --- | --- |
| 일부 파일 기록 후 Export 실패 및 동일 폴더 재시도 충돌 | [PR #11 설명 및 변경](https://github.com/CodingBot000/GameBridge_SDK/pull/11) · [Recovery Journal 기록 및 복구](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/unity/Packages/com.gamebridge.sdk/Editor/IosExportFiles.cs#L75-L118) · [Export Hook](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/unity/Packages/com.gamebridge.sdk/Editor/IosXcodeBuildHook.cs) · [4개 쓰기 지점 장애 주입·Host 보존 assertion](https://github.com/CodingBot000/GameBridge_SDK/blob/d37e8a105d3f47d25a24ccb2e44c7ef97f1cc3b4/tests/UnityIosHook/Program.cs#L178-L203) |
| Meta Framework 누락 및 로딩 실패 | [원인 분석](IOS_META_EMBED_FIX.md) · [정제 JSON](evidence/ios-meta-embed-fix.json) — 실패 앱 검출, Framework 4개 포함, 서명 및 LOCAL_MOCK Player 확인 |
| Google OAuth URL 전달 경로 | [PR #8](https://github.com/CodingBot000/GameBridge_SDK/pull/8) · [검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md) · [정제 JSON의 lifecycle20261123](evidence/ios-google-oauth-verification.json) |

PR #11의 157개 PBX/콜백 검사는 독립 test case 157개라는 뜻이 아닙니다. cold/warm 합성 URL 처리와 실제 OAuth ABI 진입, 실제 cold Scene 직접 주입은 서로 다른 범위입니다.

## SDK 배포와 선정 API/ABI 검증

[PR #18](https://github.com/CodingBot000/GameBridge_SDK/pull/18) · [리팩토링 결과](evidence/bridge-client-refactor-verification.md#변경과-호환성) · [선정 C# 호환성 검사](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/scripts/check-csharp-compat.sh) · [패키징 소스](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/scripts/package-sdk.sh) · [전이 계약](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/contracts/bridge-client-refactor-transition.json)

기록된 0.1.2-dev 비교 결과: C# 공개 reflection 383줄 동일, 선정 JVM 클래스 5개의 공개 descriptor 및 BridgeFacade/BridgeCallback JNI, iOS C ABI 5개 GB 심볼 및 header 비교. 전체 Kotlin metadata/ABI 또는 모든 OS 조합을 검증한 것은 아닙니다.

| 공개 패키지 | GitHub 등록 SHA-256 digest와 기존 검증 문서 대조 |
| --- | --- |
| [Unity UPM TGZ](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/com.gamebridge.sdk-0.1.2-dev.tgz) | 일치 (`4e1bf57f…`) |
| [Android Maven ZIP](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/GameBridge-Maven-0.1.2-dev.zip) | 일치 (`ed6c50c9…`) |
| [iOS XCFramework ZIP](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/GameBridgeNative-0.1.2-dev.xcframework.zip) | 일치 (`2c8b5cf6…`) |

[전체 SHA256SUMS](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/SHA256SUMS) · [SOURCE_MANIFEST.json](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/SOURCE_MANIFEST.json) · [RELEASE_NOTES.md](https://github.com/CodingBot000/GameBridge_SDK/releases/download/v0.1.2-dev/RELEASE_NOTES.md). 공개 Pre-release에 패키지 3종과 검증 관련 파일 3종이 등록된 것을 확인했습니다. GitHub API의 각 패키지 전체 digest는 [기존 로컬 SHA-256 기록](evidence/bridge-client-refactor-verification.md#변경과-호환성)과 일치합니다. 이번 문서 점검에서는 다운로드 파일의 바이트를 다시 해시하지 않았습니다.

## GitHub Hosted CI

| 실행 | 검증 결과 |
| --- | --- |
| [PR #22 — HEAD d3b7aa2](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875) | 최초 Android 의존성 다운로드 HTTP 429 FAIL → 2차 기본 5개 SUCCESS, Unity E2E·Release Readiness SKIPPED |
| [PR #21 — HEAD c84b0bf](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182) | 기본 5개 SUCCESS, Unity E2E·Release Readiness SKIPPED |
| [main — 536ab987](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45863332014) | 기본 5개 SUCCESS, Unity E2E·Release Readiness SKIPPED |
| [배포 기준 PR #18 — HEAD 46988f8](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45812418546) | 기본 5개 SUCCESS, Unity E2E·Release Readiness SKIPPED |

PR #22의 최초 실패 [Android Job](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875/job/140092120780)과 2차 성공 [Android Job](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875/job/140100260083) · [Basic CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875/job/140102064658)를 각각 확인했습니다. 실패는 Maven Central HTTP 429 의존성 다운로드 단계이며 테스트 assertion 실패로 확인된 것이 아닙니다. 같은 HEAD의 재실행으로 성공했고 제품 코드·workflow 수정은 없었습니다.

PR #21의 Job별 접근 경로:

| Job | 상태 및 주요 범위 |
| --- | --- |
| [inventory-contracts](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077417117) | SUCCESS · inventory / contract |
| [backend-postgres](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077417070) | SUCCESS · 격리 PostgreSQL, 세션 수명주기, Testcontainers 불변조건·Mutation |
| [android-native](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077417029) | SUCCESS · Native / 독립 Maven R8 소비 |
| [swift-ios-simulator](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077416970) | SUCCESS · Swift / 합성 iOS Simulator Host |
| [basic-ci](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140083258676) | SUCCESS · 기본 gate |
| [unity-e2e](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140077419647) | SKIPPED |
| [release-readiness](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182/job/140083305151) | SKIPPED |

[Workflow 정의](https://github.com/CodingBot000/GameBridge_SDK/blob/99b157546c7a7f76d65f7678b7a3dca4f19b7efd/.github/workflows/verify.yml) · [CI 범위](CI.md). PR #21에서 별도 다운로드용 Actions artifact가 등록되지 않았습니다. PR/Job 메타데이터는 조회했지만 로그의 비로그인 접근 또는 장기 보존까지 보장하지 않습니다.

## 실계정·Player 검증의 구분

| 실행 | 공개 기록과 경계 |
| --- | --- |
| 이전 Android Google 실계정 | [2026-11-25 AVD 기록](evidence/android-google-live-20261125.md). 0.1.1-dev Native/Unity 로그인·취소 후 재시도·재시작 복원·로그아웃 |
| 이전 iOS Google 실계정 | [2026-11-23 검증 기록](IOS_GOOGLE_OAUTH_VERIFICATION.md#session-lifecycle-and-automatic-callback-2026-11-23-kst) · [정제 JSON](evidence/ios-google-oauth-verification.json). 18.6 Simulator Native/Unity 실계정 로그인·복원·취소·로그아웃. Native 취소 후 재로그인 성공 미확인 |
| 0.1.2-dev 후속 Player | [2026-11-26 요약과 원본 식별자](evidence/bridge-client-refactor-verification.md#2026-11-26-후속-실제-player-검증) · [PR #18](https://github.com/CodingBot000/GameBridge_SDK/pull/18). Android/iOS 합성 PII·로그아웃 후 복원 차단/종료, iOS LOCAL_MOCK Push |

**비공개 로컬 원본:** 최신 Player의 일부 result.json, marker 및 DB 원본은 Git에 포함되지 않습니다. 공개 요약의 SHA-256은 원본 식별 정보이며, 해시만으로 실행 결과를 재구성하거나 독립 검증할 수 없습니다. 과거 정제 JSON을 0.1.2-dev 원본으로 대체하지 않습니다. 계정·raw token·개인 로그·로컬 DB는 이 인덱스에 복제하지 않습니다.

0.1.2-dev Google 실계정 재검증, 실제 Google refresh/replay, Apple/Facebook 실계정, 실제 스토어 거래, 원격 FCM/APNs, 실기기, 전체 Strict는 미완료입니다. 기존 StoreKit 26.5 FAIL 및 weak client 원인 미확정을 유지합니다. [기능별 상태](FEATURE_MATRIX.md) · [호환성](COMPATIBILITY.md) · [최종 판정](FINAL_REPORT.md).
