# P08-T03 UPM staging 및 Unity export hook 검증

- `artifacts/upm-stable-meta-20261113`의 147개 파일 checksum과 iOS XCFramework device/simulator arch·C ABI 검사를 통과했다. `SHA256SUMS` SHA-256은 `fe45dc0622451409d062d70ceb20e75e2ccfdb5735228bdfaeb25ea5f690680b`이며, Native payload 81개 파일은 기존 f1e12b6 검증 staging과 byte 동일하다.
- Unity 6000.5.8f1 신규 소비 프로젝트에서 Sample API import와 Editor fake/guard 시험, Android/iOS Native Demo LOCAL_MOCK Player 빌드·실행을 확인했다 ([소비자 증거](consumer-install.md)). iOS sample의 누락된 직접 asmdef 참조는 실제 export 실패 후 수정했다.
- 실제 Unity Android Gradle export와 iOS Xcode export에서 각각 hook을 두 번 추가 실행해 설정 파일과 Native payload hash가 변하지 않음을 확인했다 ([hook 증거](p08-export-hooks.md)).
- package 원본의 37개 asset/folder metadata를 고정했고 누락·중복·orphan 검사를 통과했다. 두 프로젝트에서 package 및 imported sample 내부 asset GUID 70회 비교는 일치했고, 같은 프로젝트에서 sample 재import 시 생성 대상 root 및 내부 GUID도 유지됐다 (`artifacts/offline-sample.PbKuS1/reimport-markers.log`). 서로 다른 프로젝트에서 Unity가 새로 만드는 sample 대상 root 폴더 GUID는 다르므로 package가 배포하는 내부 asset GUID와 구분한다 ([metadata 이력](p08-unity-metadata-partial.md)).
- README에서 Native 바이너리가 없는 Git source package와 바이너리를 포함한 staging을 구분한다. 이 결과는 Unity 로컬 패키징 범위의 PASS이며 실제 인증·스토어·원격 push·실기기 또는 Package Manager GUI 시각 검증은 아니다.

## 2026-11-13 설정 진단 변경 후 재검증

- 현재 product 변경을 포함한 staging `artifacts/upm-config-diagnostic-20261113`의 147개 checksum PASS, `SHA256SUMS` SHA-256 `358be20096ead408552438708504447faa727f2fd78b57d02e602aceacc596a8`. Android/iOS Native binary는 위 두 최신 packaging evidence의 새 산출물을 사용했다.
- 이 stage에서 Unity Sample API import·Editor fake/guard 및 동일 프로젝트 재import GUID 안정성 PASS (`artifacts/offline-sample.X4RqNd`); 실제 Android Gradle 및 iOS Xcode export hook 반복 PASS (`artifacts/unity-android-mock.RMw4BW`, `artifacts/unity-ios-mock.v5pYhN`). 실제 Player·실제 provider는 별도다.
