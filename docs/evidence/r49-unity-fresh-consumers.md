# R49 새 Unity 소비 프로젝트의 독립 설치·실행

- Android: source `8afe5d07551d639d6510af7b736f60dec0b475cc`, tracked-clean. 격리 프로젝트에 staged UPM을 복사하고 Unity 6000.5.8f1 Android IL2CPP APK를 만들어 전용 Android 36 emulator에서 실제 LOCAL_MOCK 흐름 실행 PASS (`artifacts/unity-android-e2e-7001epc_/result.json`, exit 0). 전용 AVD의 최초 전체화면 안내는 수동으로 닫았다.
- iOS: source `90311242becb02c649eea29844237875d3a0b8cd`, tracked-clean. 별도 격리 프로젝트에 같은 staged UPM을 복사하고 Unity iOS Simulator Xcode project와 arm64 Player를 생성·실행 PASS (`artifacts/unity-ios-e2e-zizcrlvt/result.json`, exit 0). Simulator local ad-hoc signing을 사용했다.
- 두 실행의 UPM staging SHA-256은 `d0f88d08e435d2de9b11028f15db9fbbcc526d894aeedeb110cb23c309dfec7e`로 일치한다. 두 source의 Unity SDK·Android Native SDK·iOS Native SDK 제품 디렉터리는 `git diff`상 동일했다. 각 생성기는 독립 test consumer 소스를 사용하고 `unity/Demo`를 참조하지 않는다. 이 결과는 Unity package 설치·두 Player의 local-mock 실행 범위다.
- 새 `harness/run-unity-consumer-e2e.py`는 같은 현재 HEAD와 tracked-clean, Android 및 iOS 새 Player 실행과 DB grant를 모두 요구한다. 이 wrapper 자체의 실제 전체 재실행은 별도이며 실패·미실행·기존 다른 SHA는 통과시키지 않는다.
- 실제 Google/Apple 인증, Play/App Store 결제, 실기기 실행은 NOT_RUN이다. 원본 로그·APK·키·DB는 Git에 포함하지 않는다.
