# P08 Offline Demo 격리 Editor 검증

- 소스: `a761007`의 Offline Demo README, 수정 iOS sample asmdef 및 SDK 소스. Native SDK 바이너리는 `f1e12b6` staged 산출물과 byte 동일한 81개 파일을 재사용했다.
- 새 staging: `artifacts/upm-native-sample-fix-20261112`, `SHA256SUMS` SHA-256 `6f966d4be29bfb9907d769a1d3da430d0b55aa53cf3043dce9568b83b62f0f1e`; 파일 110개 checksum 및 XCFramework arch/C ABI 검사가 통과했고 runner가 staged SDK 소스와 checkout의 일치를 확인했다. 과거 stage는 source 불일치 음성 시험에서 거부됐다.
- `scripts/smoke-unity-offline-sample.sh`는 새 테스트 프로젝트에 staged UPM을 복사하고 Unity Package Manager Sample API로 Offline/Native sample을 import하며 정확한 Unity 패키지 버전·EventSystem을 구성한다. Unity 6000.5.8f1 Editor Play에서 fake 초기화, 모의 로그인, 상품 목록과 100코인 구매 UI callback을 실행했다.
- `artifacts/offline-sample.Afsqij/results.xml`: 1건 PASS, skip 0, 완료 marker 확인. 누락·실패·skip·marker 누락을 거부하는 결과 판정의 독립 음성 시험도 통과했다.
- 같은 Editor 시험은 Native Demo가 Editor에서 플랫폼 안내를 표시하고 Native 동작 버튼을 비활성화하는지도 확인했다.
- 프로그램으로 button callback을 호출한 결과다. Sample API import marker는 `artifacts/offline-sample.Afsqij/import-markers.log`에 보존했다. Package Manager UI의 Import 버튼 클릭, 실제 포인터 조작이나 화면 렌더링은 시험하지 않았다. Native Demo의 Player 흐름, 실제 기기·결제·원격 서비스 검증도 아니다.
- 첫 후보 `artifacts/upm-offline-sample-20261112`는 오래된 Native 산출물을 포함해 최신 패키지로 사용하지 않는다. 그 후보에서의 이전 Editor sample test는 제품 Native 동등성 증거가 아니다.
