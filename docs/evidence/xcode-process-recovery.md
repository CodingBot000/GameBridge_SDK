# P09-T04 R34 Xcode 로컬 프로세스 복구

- 제품 소스: `2bc9d77` + 당시 미커밋 XcodeStoreKitSession 수정; 수정은 이후 로컬 커밋에서 확인한다.
- 명령: `python3 harness/run-xcode-process-recovery.py --run-local`.
- 환경: 전용 iOS 18.6 simulator, Xcode StoreKit 로컬 설정, 별도 local-mock PostgreSQL DB 및 합성 인증.
- 결과: `artifacts/xcode-process-recovery-f_w2fsya/result.json`, exit 0, 두 개 서로 다른 프로세스. 첫 프로세스는 서버 commit 뒤 응답 유실·pending 기록, 종료 후 새 프로세스는 잔액 100·unfinished 0·journal 삭제 및 관찰 중 재생성 0회를 확인했다.
- 선행 실패: `artifacts/xcode-process-recovery-oz3ycsw7`에서 finish 뒤 journal 재생성. 미완료 거래 재확인으로 해당 중복을 차단한 후 재시험했다.
- 한계: Xcode local fake 거래이며 Apple sandbox·실기기·Unity player는 검증하지 않았다. 실제 결제 환경의 거래 ID 및 검증과 분리한다.
