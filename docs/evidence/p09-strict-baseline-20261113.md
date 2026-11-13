# P09-T06 현재 소스 Strict 기준선

2026-11-13, source HEAD `d6bbe7ce921b4b21d0ea97dae1b2d10d06cceef5`에서 `harness/run-strict-local-isolated.py --run-local`을 한 차례 실행했다. 시작 시 tracked 변경은 없었으나 보존한 기존 미추적 파일 때문에 보고서 `sourceDirty=true`다. 새 local/sandbox DB `gamebridge_ci_74cd3b0f0d_local`·`gamebridge_ci_74cd3b0f0d_sandbox` 및 role과 새 Simulator를 사용했다. 원본 결과 `artifacts/verify-all-u2vuk3u_/result.json`, orchestration `artifacts/strict-isolated-myjcd44z`는 로컬에만 보존한다.

**전체 FAIL / exit 1**: 49 required lane 중 PASS 46, FAIL 1, DEFERRED_ENV 2. 외부 Provider 13개는 별도 WAITING_USER다. 정적 매핑 checker PASS 1개는 46개에 포함되지만 시나리오 실행 성공이 아니다.

## 각 lane

`실행 수`는 집계 원본의 tests 값이다. `*`는 스크립트 marker·checker 호출을 1로 센 값으로 제품 테스트 건수가 아니다. `—`는 해당 항목을 원본 집계에서 수집하지 않았다는 뜻이며 0으로 가정하지 않는다. status가 DEFERRED_ENV인 항목은 미실행이다. 모든 경로는 로컬 evidence이며 원본 로그는 커밋하지 않는다.

| Lane | 결과 | 실행 수 | failure | skip | 종료 | 증거 |
|---|---|---:|---:|---:|---:|---|
| harness-self | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/harness-self.log` |
| progress | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/progress.log` |
| manifest | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/manifest.log` |
| api-baseline | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/api-baseline.log` |
| api-baseline-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/api-baseline-negative.log` |
| csharp-compat | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/csharp-compat.log` |
| aggregation-self | PASS | 14 | — | 0 | 0 | `artifacts/verify-all-u2vuk3u_/aggregation-self.log` |
| progress-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/progress-negative.log` |
| manifest-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/manifest-negative.log` |
| contract-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/contract-negative.log` |
| contracts/kotlin | PASS | 10 | 0 | 0 | 0 | `artifacts/contracts-lx5r2jal/result.json` |
| contracts/swift | PASS | 12 | 0 | 0 | 0 | `artifacts/contracts-lx5r2jal/result.json` |
| contracts/csharp | PASS | 1 | 0 | 0 | 0 | `artifacts/contracts-lx5r2jal/result.json` |
| bridge-mutation | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/bridge-mutation.log` |
| lifecycle-stress | PASS | 100 | — | 0 | 0 | `artifacts/verify-all-u2vuk3u_/lifecycle-stress.log` |
| r50-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/r50-negative.log` |
| purchase-verifier | PASS | 7 | — | 0 | 0 | `artifacts/verify-all-u2vuk3u_/purchase-verifier.log` |
| session-replay | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/session-replay.log` |
| push-router-scenarios | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/push-router-scenarios.log` |
| push-ownership | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/push-ownership.log` |
| android-dependency-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/android-dependency-negative.log` |
| ios-xcframework-negative | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/ios-xcframework-negative.log` |
| auth/backend-jwt-fake | PASS | 6 | 0 | 0 | 0 | `artifacts/auth-regression-4k5du9z2/result.json` |
| auth/backend-sandbox-test-key-db | PASS | 3 | 0 | 0 | 0 | `artifacts/auth-regression-4k5du9z2/result.json` |
| auth/android-native-fake | PASS | 17 | 0 | 0 | 0 | `artifacts/auth-regression-4k5du9z2/result.json` |
| auth/swift-native-fake | PASS | 22 | 0 | 0 | 0 | `artifacts/auth-regression-4k5du9z2/result.json` |
| purchase/local-postgres-fixtures | PASS | 7 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/sandbox-http-fixtures | PASS | 2 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/android-native-fake | PASS | 18 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/swift-native-fake | PASS | 16 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/android-local-response-loss | PASS | 3 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/swift-local-response-loss | PASS | 3 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/xcode-storekit-local-db-recovery | PASS | 1 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| purchase/xcode-storekit-process-recovery | PASS | 1 | 0 | 0 | 0 | `artifacts/purchase-regression-aq1lgyl0/result.json` |
| ledger-mutation | PASS | 1* | — | — | 0 | `artifacts/verify-all-u2vuk3u_/ledger-mutation.log` |
| push/backend-push-fake | PASS | 10 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/sandbox-push-http-fake | PASS | 1 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/android-push-fake | PASS | 5 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/swift-push-fake | PASS | 9 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/ios-host-simulator-synthetic | PASS | 1 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/mock-permission-denied | PASS | 1 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/upm-staging-integrity | PASS | 1 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/package-negative-fixtures | PASS | 1 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/local-push-native-db-e2e | PASS | 2 | 0 | 0 | 0 | `artifacts/push-regression-bjers501/result.json` |
| push/unity-player-notifications | DEFERRED_ENV | 0 | 0 | — | 2 | `artifacts/push-regression-bjers501/result.json` |
| unity-pii-e2e | DEFERRED_ENV | 0 | — | — | 2 | `docs/PROGRESS.md` |
| scenario-coverage | PASS | 0 (매핑 50) | — | — | 0 | `artifacts/verify-all-u2vuk3u_/manifest.log` |
| unity-editor-runtime | PASS | 2 | — | 0 | 0 | `artifacts/verify-all-u2vuk3u_/unity-editor-runtime.log` |
| recorded-unresolved-failures | FAIL | 0 | — | — | 1 | `docs/PROGRESS.md` |

## 원인과 경계

- **P05-T03 / P09-T04·T06 — 기존 내부 실패:** iOS 26.5에서 StoreKit 테스트 세션 초기화 실패가 원장에 남아 있어 `recorded-unresolved-failures`가 FAIL을 반환했다. 이 lane 자체에서 26.5를 재실행한 것은 아니다. 이번 iOS 18.6 로컬 StoreKit/프로세스 복구 PASS와 구분한다.
- **P09-T05 — 환경 대기:** Unity Player 푸시 lane은 이번 실행에 별도의 격리 AVD/Player opt-in을 제공하지 않아 DEFERRED_ENV다. 실제 원격 푸시 실패를 뜻하지 않는다.
- **P09-T03/T05 — 환경 대기:** 현재 실행의 양 플랫폼 PII Player evidence/nonce를 제공하지 않아 DEFERRED_ENV다. 과거 Player 증거를 이번 실행으로 대체하지 않았다.
- 위 결과에서 식별된 내부 FAIL은 한 항목이다. 대기 두 건이나 외부 Provider 미설정을 추가 내부 버그로 세지 않는다.
- `scenario-coverage`: manifest checker 실제 실행 exit 0, 정적 매핑 50, checks 1, tests 0, executionStatus NOT_RUN. 개별 50개 시나리오가 이번에 모두 실행됐다는 뜻이 아니다.
- `harness-self`의 집계 값 1은 checker marker 호출 수다. 하위 실제 9개 lane과 각 테스트·예상 실패는 `artifacts/harness-self-trxrwsxw/result.json`에서 확인한다. 다른 `*` lane도 실제 상세 테스트 수가 원본 집계에 없는 한 미수집이다.
- Unity Editor consumer는 실제 2건 PASS다. 외부 인증·실제 스토어·FCM/APNs 및 실기기 검증은 이번 범위가 아니다. 이번 실행에서 켠 전용 Process Simulator는 삭제 없이 shutdown했다.

다음 우선 작업: P09-T05에서 사용자 AVD를 건드리지 않는 전용 환경으로 Unity Player 푸시와 PII 현재 실행 evidence를 각각 확보하고, 기존 iOS 26.5 StoreKit 내부 실패는 별도 원인 조사로 유지한다.
