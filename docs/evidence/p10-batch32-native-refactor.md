# P10-T02 Native 책임 분리 — 배치32

[변경 전후 source·커밋·검증](p10-batch32-native-refactor.json). T01이 대기 중일 때 후보를 별도 로컬 브랜치에서 개발했고, [T01 제품 조건 판정](p10-batch32-t01-decision.md) 후 같은 제품 bytes를 handoff에 후보별 두 커밋으로 정식 반영했다. 후보 브랜치는 로컬 이력으로 남기며 원격에 push하지 않았다.

| 영역 | 실제 변경 | 보존한 경계 | 검증 |
| --- | --- | --- | --- |
| Android 인증 | StoredGoogleSession DTO·JSON encode/decode·config binding/session 검증을 내부 StoredGoogleSessionCodec로 추출 | profile/save 순서, signIn/restore/operation401 차이, ui/session lock, refresh single-flight·tombstone·cancel·offline logout, 오류 코드와 사전 network 거부 | 변경 전18 → 기존18+추가2=20, 넓은 현재 Native47/실패0 |
| Swift 구매 | AppleHttpProofSink의 JSON grant decode/허용status/ServerGrant 생성을 내부 순수 decoder로 추출 | auth closure 밖 attempt ID1회·같은 멱등키/계정 소유·잘못된 응답·logout 후 늦은 grant 차단·downstream binding·grant 뒤 finish·StoreKit/journal 정책 | 변경 전20 → 기존20+추가3=23, 넓은 현재 Native43/실패0 |

새 public API, 공통 base class, DI framework, 실제 Provider의 Fake 교체, 가격·재시도·동시성·보존 정책 변경은 없다. 새 테스트는 저장 bytes/unknown field·binding 오류 우선순위, 두 grant status/잘못된 UUID·누락/status 및 decoder가 downstream 정책을 가로채지 않는 경계를 확인한다. Native 회귀는 주입된 gateway/HTTP/스토어 Fake 범위이며 실제 Google/Apple·스토어·FCM/APNs 성공이 아니다.

원본 `p10-core-batch26.json`은 수정하지 않았다. CI의 전이 검사는 닫힌 Core4485b2f Git tree에 원본 엄격 검사를 적용한 뒤, 승인된 Native4파일의 정확한 전후hash/추가파일집합만 허용한다. 나머지 Core/Native/wire는 byte 불변이며 C ABI export를 유지한다. 승인 파일이라는 이유로 임의 내용 변경을 허용하지 않는다. 다른 Core/private body·wire·export·경로·hash·과거기준 변조를 거부하는8개 단위시험을 추가했다. CI는 고정된 과거 Git tree 검증을 위해 full history를 읽는다.

후보와 현재 handoff 각각 새 Maven/AAR·R8·XCFramework 양 slice·Swift source/binary import·UPM147 checksum을 검증했다. 선정 Core/Bridge Java3class 및 C ABI4개를 비교했고, GoogleAuthProvider의 공개 bytecode 표면은 compiler-generated private accessor를 제외해 동일했다. 전체 binary ABI 보증은 아니다.

변경 후 새 패키지 Android 구매·PII는 명시적 CLI batch/headless 새 AVD에서 PASS했다. ADB build/runtime 분리와 host 창 조건은 별도 하네스 증거로 기록했다. 이전 준비 오류/시작 실패를 삭제하지 않았다. [변경 후 iOS 구매·PII](p10-batch32-post-native-ios.json)도 새 source/패키지/전용Simulator·DB에서 CLI batch로24marker·Backend trace·원장1/100과 소유기기종료를PASS했다. 최종source/한계는배치32통합보고를따른다. 각 source의 현재 여부를 전체 SDK 완료나 Release 준비로 확대하지 않는다.
