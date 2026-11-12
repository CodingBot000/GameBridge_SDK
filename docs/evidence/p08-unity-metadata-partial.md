# P08 Unity package metadata 부분 검증

- 원본 package의 37개 파일·폴더에 Unity가 격리 프로젝트에서 생성한 `.meta`를 고정했다. 정적 검사는 누락·GUID 중복·orphan 및 폴더 표식 오류를 거부한다.
- 새 staging `artifacts/upm-stable-meta-20261113`: 147개 파일 checksum, `SHA256SUMS` SHA-256 `fe45dc0622451409d062d70ceb20e75e2ccfdb5735228bdfaeb25ea5f690680b`. Native payload 81개 파일은 f1e12b6 검증 staging과 byte 동일하다.
- Unity 6000.5.8f1의 두 신규 소비 프로젝트 `artifacts/offline-sample.S2hxOa`와 `artifacts/offline-sample.McH39f`에서 Sample API import 및 Editor test 각각 1건 PASS/skip0. package 및 sample **내부** asset/folder의 원본 대비 GUID 70회 비교는 불일치 0이었다.
- Sample API가 새로 만드는 Offline/Native sample **최상위 대상 폴더** GUID는 두 프로젝트에서 원본의 package 폴더 GUID와 달랐다(전체 74회 중 4회 불일치). 최상위 폴더 GUID의 프로젝트 간 안정성은 확인되지 않았으며 P08-T03은 PARTIAL이다. 개별 파일·내부 폴더의 GUID 결과와 혼동하지 않는다.
- 신규 metadata staging의 Android/iOS Player 재실행은 별도로 기록해야 한다. 기존 프로젝트 및 사용자 Demo는 수정하지 않았다.
