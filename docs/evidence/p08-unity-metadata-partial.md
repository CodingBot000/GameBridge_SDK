# P08 Unity package metadata 부분 검증

- 원본 package의 37개 파일·폴더에 Unity가 격리 프로젝트에서 생성한 `.meta`를 고정했다. 정적 검사는 누락·GUID 중복·orphan 및 폴더 표식 오류를 거부한다.
- 새 staging `artifacts/upm-stable-meta-20261113`: 147개 파일 checksum, `SHA256SUMS` SHA-256 `fe45dc0622451409d062d70ceb20e75e2ccfdb5735228bdfaeb25ea5f690680b`. Native payload 81개 파일은 f1e12b6 검증 staging과 byte 동일하다.
- Unity 6000.5.8f1의 두 신규 소비 프로젝트 `artifacts/offline-sample.S2hxOa`와 `artifacts/offline-sample.McH39f`에서 Sample API import 및 Editor test 각각 1건 PASS/skip0. package 및 sample **내부** asset/folder의 원본 대비 GUID 70회 비교는 불일치 0이었다.
- Sample API가 새로 만드는 Offline/Native sample **최상위 대상 폴더** GUID는 두 프로젝트에서 원본의 package 폴더 GUID와 달랐다(전체 74회 중 4회 불일치). 최상위 폴더 GUID의 프로젝트 간 안정성은 확인되지 않았으며 P08-T03은 PARTIAL이다. 개별 파일·내부 폴더의 GUID 결과와 혼동하지 않는다.
- 신규 metadata staging에서 Native Demo Sample API import→LOCAL_MOCK Player 재실행: Android `artifacts/unity-android-e2e-2trvul1k` source `a80d552`, iOS `artifacts/unity-ios-e2e-q9ua_s4_` source `094333b`, 모두 tracked-clean·원장 1건/100 PASS. Android 최초 전체화면 안내는 수동 처리했다. 실제 provider/실기기는 미검증이다. 기존 프로젝트 및 사용자 Demo는 수정하지 않았다.
- 추가 대조 `artifacts/offline-sample.PbKuS1/reimport-markers.log`: 동일 프로젝트에서 각 sample을 `OverridePreviousImports`로 재가져온 뒤 생성 대상 root와 내부 asset GUID가 모두 유지됐다. 서로 다른 프로젝트에서 Unity가 새로 만드는 대상 root GUID는 서로 다르며 package가 배포하는 내부 asset GUID의 교차 프로젝트 안정성과 구분한다.

이 문서의 PARTIAL 표기는 당시 상태다. 이후 동일 프로젝트 재import 안정성·실제 export hook 반복까지 확인한 로컬 패키징 Task 판정은 [P08-T03 증거](p08-upm-staging.md)에 정리했다. 프로젝트별 새 대상 root GUID가 다르다는 관찰은 변하지 않는다.
