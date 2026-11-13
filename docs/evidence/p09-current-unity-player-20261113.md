# P09-T05 현재 소스 Unity Player 검증

2026-11-13 시작 기준 `c4269e9`에서 실행 checkpoint `5d716bd96cd8b8d3bcbc58b90f0cbf83ef7ad968`를 커밋한 뒤, tracked 소스 변경 없이 `scripts/ci-unity-e2e.sh`를 실행했다. Unity 6000.5.8f1, 활성 라이선스, Android/iOS 모듈, 147개 파일 staging checksum과 현재 배포 제품 소스 일치를 확인했다. 양 플랫폼 Player 결과의 `sourceHead`는 `5d716bd` 전체 SHA이고 `sourceTrackedDirty=false`다. Strict 보고서의 `sourceDirty=true`는 보존한 기존 미추적 Demo·캐시를 포함한 Git 상태이며, Player 결과는 tracked-clean을 별도로 확인했다. 이후 인계 커밋은 문서 변경이다.

전용 Android AVD `GameBridge_V2_P09_PII_20261113_210717`과 `GameBridge_V2_P09_PUSH_20261113_210717` 및 새 iOS 18.6 Simulator를 사용했다. 기존 사용자 AVD·Simulator는 변경하지 않았다. 두 Android AVD의 최초 전체화면 안내는 수동으로 확인했다. PII AVD 종료 후 adb가 일시 재연결됐으나 Push AVD가 정상으로 돌아온 뒤 시험을 진행했다. 이번 실행에서 사용한 전용 AVD와 Simulator는 삭제하지 않고 종료했다. 새 DB·role과 기존 artifacts도 보존한다.

## `unity-pii-e2e`: PASS

- Gate `artifacts/unity-pii-current-gh5ksqc3/result.json`: 고유 nonce 및 같은 source/head 검증 PASS.
- Android `artifacts/unity-android-e2e-ue2nmla6/result.json`, iOS `artifacts/unity-ios-e2e-9s1c5bq1/result.json`: 실제 Unity LOCAL_MOCK Player 각각 PASS, tracked-clean, 각 격리 Backend 원장 1건·100코인. 합성 개인정보·token redaction과 결과 marker 확인.
- Strict `artifacts/verify-all-e2d8gd77/unity-pii-e2e.log` 및 result에서 2건 PASS / exit 0. 개인정보는 합성 입력이며 실제 계정·실기기 검증은 아니다.

## `push/unity-player-notifications`: PASS

- Android `artifacts/unity-android-push-2c2omial/result.json`, iOS `artifacts/unity-ios-push-i3yvouey/result.json`: 각각 PASS, 동일 source 및 tracked-clean. 수신·중복 제거·main thread, background/foreground, 재연결, unregister/logout, 합성 늦은 callback 거부, 세션 전환 marker를 모두 확인했고 등록 token 0개로 종료했다.
- Android는 전용 AVD의 네트워크 차단/복원 및 재연결 거부 2회, iOS는 로컬 transport fault injection 및 재연결 거부 6회를 확인했다. iOS 시험은 실제 OS 네트워크 단절을 뜻하지 않는다.
- Strict `artifacts/push-regression-yffa1ett/result.json`에서 2건 PASS / exit 0. 외부 FCM/APNs나 실제 단말 전송은 아니다.

## Strict 집계

`artifacts/verify-all-e2d8gd77/result.json`: PASS 48, FAIL 1, 전체 **FAIL / exit 1**. 두 이전 DEFERRED_ENV lane은 이번 Player 실행으로 PASS가 됐다. 남은 FAIL은 기존 `P05-T03` iOS 26.5 StoreKit 실패를 기록한 lane이며 이번에 26.5를 재검증하거나 해결한 것은 아니다. Provider 13개는 WAITING_USER다. `scenario-coverage`는 정적 매핑 50개, tests 0이고 50개 시나리오의 개별 현재 실행을 주장하지 않는다. 원본 로그·APK·DB·임시 키는 저장소에 포함하지 않는다.
