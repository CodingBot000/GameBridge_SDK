# CI 검증 범위

> **0.1.2-dev 배포 기준** PR #18 HEAD `46988f8` (main 병합 `5c899be`)에서 `inventory-contracts`, `backend-postgres`, `android-native`, `swift-ios-simulator`, `basic-ci` **SUCCESS**. `unity-e2e`와 `release-readiness`는 **SKIPPED**입니다. [Hosted CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45812418546)

**PR #22 재실행 및 병합:** HEAD `d3b7aa2`의 [최초 Android Job](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875/job/140092120780)은 Maven Central HTTP 429(Too Many Requests)로 Gradle 의존성 다운로드에 실패했고 `basic-ci`도 실패했습니다. 테스트 assertion 실패는 확인되지 않았습니다. 같은 HEAD의 [2차 Android Job](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875/job/140100260083)에서 contract/provider fake, Backend transport, standalone fake, Maven/R8 단계가 성공했고 [기본 5개 Job](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45872763875) 모두 SUCCESS, Unity E2E·Release Readiness SKIPPED를 확인했습니다. 제품 코드나 workflow를 바꾸지 않고 재실행으로 해소했으며 PR #22는 main `d37e8a1`에 병합했습니다. 첫 실패를 삭제하거나 새 실Provider 검증으로 계산하지 않습니다.

**후속 문서 PR 확인:** PR #21 HEAD `c84b0bf`의 [CI 실행](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45868483182)에서 기본 5개 Job SUCCESS, Unity E2E·Release Readiness SKIPPED를 확인했습니다. Job별 접근 경로와 공개 증거의 범위는 [VERIFICATION_EVIDENCE](VERIFICATION_EVIDENCE.md)를 참고하세요. 이 실행을 신규 Player나 실계정 검증으로 간주하지 않습니다.

**후속 main 확인:** 검토 기준 main `536ab987`의 [수동 CI 실행](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45863332014)에서도 위 기본 5개 Job SUCCESS, `unity-e2e`와 `release-readiness` SKIPPED를 확인했습니다. 배포 기준 PR 실행과 구분하며 이후 문서 변경의 CI 결과로 소급하지 않습니다.

Android·iOS의 실제 Unity Player와 업데이트 결과는 로컬에서 확보했습니다. 공개 Pre-release는 검증된 패키지의 SHA-256과 매니페스트를 대조하여 배포했습니다. [로컬 검증](evidence/bridge-client-refactor-verification.md) · [v0.1.2-dev 배포](https://github.com/CodingBot000/GameBridge_SDK/releases/tag/v0.1.2-dev)

## 기존 게이트 설명 및 과거 실행 기록

`.github/workflows/verify.yml`은 PR과 수동 실행에서 다음 결과를 분리한다. hosted CI는 소스 `2af863b`에서 네 hosted job과 basic-ci가 원격 통과했다 ([증거](evidence/p09-hosted-ci.md)). Unity self-hosted는 SKIPPED이며 로컬 정적·음성 시험을 원격 Unity 성공으로 기록하지 않는다.

- `inventory-contracts`: 진행 원장·manifest·집계와 fail-closed gate 단위 검사 및 `harness/requirements-schema.txt`의 검증 라이브러리로 bridge Draft 2020-12 schema/fixture 검사. 로컬에서는 가상환경 설치 후 `python -m unittest discover -s harness -p test_bridge_schema.py -v`를 실행한다. 리팩토링 전 고정 Git tree에서 기존 전이 가드를 실행하고 현재 소스에는 정확한 승인 경로 및 preimage/postimage 검사와 음성 시험을 적용한다. [현재 전이 기록](../contracts/bridge-client-refactor-transition.json)
- `backend-postgres`: GitHub 호스팅 Linux의 전용 PostgreSQL과 Backend fixture. Google 세션 수명과 challenge 재사용 거부 HTTP 시험은 별도 sandbox DB에서 실행하고 두 테스트의 실행 및 skip 0을 확인한다. 테스트 전용 자격값이며 외부 서비스 계정이 아니다.
- `android-native`: GitHub 호스팅 Linux의 Android 단위/fake 검사와 별도 Maven/R8 consumer 빌드.
- `swift-ios-simulator`: GitHub 호스팅 macOS의 Swift 단위/fake(Provider 선택 및 소셜 인증 수명 포함), 독립 SwiftPM source consumer 및 합성 iOS host callback 시험. 실제 Provider 계정 로그인·APNs 전송은 아니다.
- `basic-ci`: 위 네 job이 모두 실제 성공해야만 성공한다. 이 결과는 SDK Release 준비 완료가 아니다.
- `unity-e2e`: `workflow_dispatch`에서 repository 변수 `GAMEBRIDGE_UNITY_E2E_ENABLED=true`인 경우에만 전용 `self-hosted, macOS, ARM64, gamebridge-unity-e2e` runner에서 실행한다. PR의 신뢰되지 않은 코드를 self-hosted에서 자동 실행하지 않는다. 활성 Unity 라이선스, 격리 새 AVD, 테스트 DB, 최신 staged SDK, 설치된 Editor 실행 파일 `UNITY_EDITOR_PATH`와 `GAMEBRIDGE_UPM_STAGING`, `GAMEBRIDGE_ANDROID_SERIAL`, `GAMEBRIDGE_TEST_AVD_NAME`, 별도 Push 전용 `GAMEBRIDGE_PUSH_ANDROID_SERIAL`, `GAMEBRIDGE_PUSH_TEST_AVD_NAME`이 필요하다. 두 AVD 이름은 `GameBridge_V2_`로 시작하고 서로 다른 기기여야 한다. `GAMEBRIDGE_UNITY_PACKAGE_CACHE`는 정확한 버전의 격리 테스트용 package cache 경로로 필수다. Editor smoke, Offline/Native sample Editor 검사, Android/iOS 실제 export hook 반복 검사, synthetic PII callback 검사를 포함한 Android/iOS 실제 LOCAL_MOCK Player와 동일 실행 nonce·HEAD·marker·원장 증거를 확인하는 strict-local suite 중 하나라도 실패·미실행이면 성공하지 않는다. strict 실행은 지정한 `UNITY_EDITOR_PATH`와 같은 staging 안의 Maven/XCFramework를 사용한다. strict orchestration은 `gamebridge-sdk-local-postgres-1` 컨테이너에 새 전용 DB/role을 만들고 테스트 서버를 실행한 뒤 보존하므로 전용 로컬 PostgreSQL과 Docker가 필요하다.
- `release-readiness`: basic-ci와 실제 unity-e2e가 모두 성공하고 모든 필수 회귀 시나리오가 완료되어야 성공한다. Unity job이 skipped이면 `DEFERRED_ENV` 메시지와 비영 종료를 남긴다. GitHub UI의 failed job은 환경 대기와 제품 테스트 실패를 자동으로 구분하지 않으므로 로그를 확인해야 한다.

현재 50개 시나리오의 local/fake coverage 증거는 모두 기록됐고 `harness/check-required-coverage.py`가 통과한다. 이는 현재 CI 실행에서 50개가 모두 재실행됐거나 실제 제공자 검증이 끝났다는 뜻이 아니다. R40 iOS OS 거부는 외부 GUI 도구로 처리한 실제 Simulator 증거이며 무인 CI 검증은 아니다. strict-local의 Unity push lane은 명시적인 `GAMEBRIDGE_RUN_UNITY_PUSH_E2E=true`와 전용 환경이 있을 때 두 Player를 새로 실행하고 현재 HEAD·clean 상태·필수 marker를 확인한다. opt-in이나 환경이 없으면 DEFERRED_ENV다. 당시 로컬 전체 gate에서 소스 `562c75f`의 Android/iOS PII 및 Push LOCAL_MOCK Player, Unity Editor와 50개 시나리오 coverage 기록이 각각 PASS했으나 기존 P05-T03 실패로 전체 gate는 FAIL이다 ([증거](evidence/p09-unity-ci-local.md)). Android 최초 전체화면 안내는 수동으로 닫았으며 당시 GitHub Actions는 NOT_RUN이었다. 이후 hosted CI 원격 실행 결과는 [P09 hosted CI evidence](evidence/p09-hosted-ci.md)에 기록했으며 Unity self-hosted는 SKIPPED, 실제 원격 푸시는 미검증이다. 기존 검증을 삭제하거나 과거 증거로 현재 실행을 대체하지 않는다. 실제 계정, 원격 FCM/APNs, 상용 서명이나 외부 인증키는 사용하지 않는다.

2026-11-13 당시 로컬 UPM staging은 `artifacts/upm-config-diagnostic-20261113`이었다. 변경 Android/iOS Native 산출물과 147개 checksum, Editor sample 및 양 export hook을 검증했다. 해당 stage의 양 Native Demo LOCAL_MOCK Player를 별도로 재검증했다 ([소비자 증거](evidence/consumer-install.md)). `upm-native-sample-fix-20261112`에는 안정적 asset metadata 추가가 없다. 이전 `upm-offline-sample-current-20261112`에는 iOS Native Demo asmdef 수정이 없다. 이전 `upm-offline-sample-20261112` 후보는 Native payload가 달라 최신 staging으로 사용하지 않는다. 로컬 산출물은 원격 checkout에 자동으로 존재하지 않는다.

standalone strict에서 현재 실행의 `GAMEBRIDGE_UNITY_PII_EVIDENCE`와 `GAMEBRIDGE_UNITY_PII_NONCE`가 없으면 PII Player lane은 `DEFERRED_ENV`다. CI는 양 Player를 새로 실행해 nonce와 증거를 전달하며 기존 결과를 재사용하지 않는다. 이 연결을 포함한 로컬 전체 gate는 실행했지만, 두 Android 최초 안내를 수동 처리했으므로 무인 CI 검증은 아니다.


## Self-hosted 실행 전 점검

2026-11-14 사전 점검은 **DEFERRED_ENV**다. 등록 runner와 전용 label이 없고 Unity 활성화 repository 변수도 없다. 현재 로컬 개발 계정에서 도구가 동작하더라도 전용 실행 계정·VM과 개인 credential/업무 파일/기존 개발 리소스 접근 차단은 확인되지 않았다. 보존된 AVD와 개발 PostgreSQL을 원격 CI 격리 환경으로 간주하지 않는다. 이번에는 등록·변수 변경·원격 실행을 하지 않았다.

현재 Unity job은 전체 Strict도 포함하므로 Player가 통과해도 P05-T03 FAIL이 job 실패로 전파된다. 두 상태를 독립적으로 보여주려면 strict 호출·nonzero 차단을 유지하면서 같은 실행의 Player 증거와 strict 결과를 각각 기록하고 Release가 둘 다 검증하도록 바꿔야 한다. 이는 적용 전 제안이며 판정표·준비 조건과 단위시험 범위는 [self-hosted 사전 점검](evidence/p09-self-hosted-readiness.md)을 따른다.


## Hosted와 Release 실행 모드

PR과 기본 `workflow_dispatch`는 hosted 네 job 및 basic-ci만 결과를 판단하며 Unity·release-readiness는 skipped다. `workflow_dispatch`의 `release_validation`을 명시적으로 true로 지정하고 repository의 기존 Unity opt-in 변수도 true일 때만 self-hosted Unity job이 실행된다. Release 요청 시 Unity가 skipped/failed이면 기존 release gate가 비영 종료한다. Unity와 전체 strict는 아직 단일 job으로 결합돼 있으며 독립 결과 인터페이스는 후속 작업이다. 이번 변경의 원격 Actions 실행 여부는 [모드 분리 evidence](evidence/p09-ci-modes.md)를 따른다.

## Batch A와 Batch B 검증 범위

Batch A 후보 `026716f`의 [수동 Hosted 검증](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45574448608)과 [PR #13 필수 CI](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/45577041949)가 통과했다. Batch A는 main `35cddc1`로 병합했다. Batch B의 버전 교체 및 Unity Player는 별도 로컬 시험으로 기록한다. [로컬 증거](evidence/batch-b48-compatibility.md).

PR #14의 기본 5개 Job 성공을 확인했다. 이후 Android 실계정 시험은 제품 코드 변경 없는 로컬 실행이며 별도 CI를 실행하지 않았다. 최종 문서 정리는 새 runtime 검증 결과가 아니다.
