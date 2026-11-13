# P08-T04 신규 Unity 소비 프로젝트 설치 검증

- staged SDK `artifacts/upm-native-sample-fix-20261112`; `SHA256SUMS`의 SHA-256 `6f966d4be29bfb9907d769a1d3da430d0b55aa53cf3043dce9568b83b62f0f1e`. 110개 파일 checksum, iOS XCFramework arch/C ABI 검사를 확인했다. Native payload 81개 파일은 이전 `f1e12b6` 검증 staging과 byte 동일하다.
- `scripts/smoke-unity-offline-sample.sh`는 기존 Demo를 참조하지 않는 신규 프로젝트에 staged UPM을 설치하고 Unity Package Manager Sample API로 Offline/Native sample을 import한다. Unity 6000.5.8f1 Editor Play에서 EventSystem을 구성해 Offline fake 로그인·상품·100코인 구매와 Native sample의 Editor guard를 확인했다 (`artifacts/offline-sample.Afsqij`, 1건 PASS/skip0).
- 별도의 신규 Android 프로젝트에서 동일 staged UPM과 Sample API import 후 Native Demo의 runtime 설정·LOCAL_MOCK 로그인·상품·구매·로그아웃을 Unity Android Player로 실행했다. source `64cb90b`, tracked-clean, `artifacts/unity-android-e2e-8hjon046`, Backend 원장 1건·100코인 PASS. 최초 전체화면 안내는 수동으로 닫았다.
- 별도의 신규 iOS 프로젝트에서 동일 Sample API import 후 Native Demo의 동일 흐름을 Unity iOS 18.6 Simulator Player로 실행했다. source `083100f`, tracked-clean, `artifacts/unity-ios-e2e-7ryle35b`, Backend 원장 1건·100코인 PASS. Simulator 서명은 로컬 ad-hoc이다. 두 source 사이 Unity SDK·Android SDK·iOS 제품 경로는 동일하다.
- 재현에는 명시적인 테스트 장비·격리 PostgreSQL 및 로컬 staging/cache가 필요하다. 상세 명령과 제한은 [Android 증거](p08-native-demo-android.md), [iOS 증거](p08-native-demo-ios.md), [Editor 증거](p08-offline-sample-editor.md)를 참조한다.
- Package Manager GUI 클릭, 화면 포인터·시각 QA, 실기기, 실제 Google/Apple 로그인·스토어·FCM/APNs는 이 검증 범위가 아니다. 원본 로그·키·DB·APK는 Git에 포함하지 않는다.

metadata 추가 후 `artifacts/upm-stable-meta-20261113`에서 동일 Android/iOS Sample API import→Native Demo Player를 재실행했다 ([metadata 부분 증거](p08-unity-metadata-partial.md)). Unity가 프로젝트별로 생성하는 샘플 최상위 폴더 GUID 차이와 동일 프로젝트 재import 결과는 별도로 기록한다.
